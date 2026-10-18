import React, { useState, useEffect, useCallback } from 'react';
import AnomalySummaryCards from '../components/anomaly/AnomalySummaryCards';
import DetectionMethodSelector from '../components/anomaly/DetectionMethodSelector';
import AnomalyTrendChart from '../components/anomaly/AnomalyTrendChart';
import AnomalyTable from '../components/anomaly/AnomalyTable';
import ThresholdSettings from '../components/anomaly/ThresholdSettings';
import AlertDetailsPanel from '../components/anomaly/AlertDetailsPanel';
import EvaluationModal from '../components/anomaly/EvaluationModal';
import { anomalyApi } from '../services/anomalyApi';
import { api } from '../services/api';
import '../styles/anomaly-dashboard.css';

export default function AnomalyDashboard({ onAddToast }) {
  // State
  const [summary, setSummary] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [totalAlerts, setTotalAlerts] = useState(0);
  const [page, setPage] = useState(1);
  const [limit] = useState(12);

  const [services, setServices] = useState([]);
  const [selectedServiceId, setSelectedServiceId] = useState('srv-gateway');
  const [metricHistory, setMetricHistory] = useState([]);

  const [detectionMethod, setDetectionMethod] = useState('combined');
  const [thresholds, setThresholds] = useState(null);
  const [loading, setLoading] = useState(false);

  // Table filters
  const [filterService, setFilterService] = useState('');
  const [filterSeverity, setFilterSeverity] = useState('');
  const [filterMethod, setFilterMethod] = useState('');
  const [filterAcknowledged, setFilterAcknowledged] = useState('');

  // Modals
  const [isThresholdsOpen, setIsThresholdsOpen] = useState(false);
  const [isEvaluationOpen, setIsEvaluationOpen] = useState(false);
  const [selectedAlertForDetails, setSelectedAlertForDetails] = useState(null);

  // Load summary and thresholds
  const loadInitialData = useCallback(async () => {
    try {
      const [sum, thresh, svcs] = await Promise.all([
        anomalyApi.getSummary(),
        anomalyApi.getThresholds(),
        api.getServices()
      ]);
      setSummary(sum);
      setThresholds(thresh);
      setServices(svcs);
      if (svcs.length > 0 && !selectedServiceId) {
        setSelectedServiceId(svcs[0].id);
      }
    } catch (err) {
      console.error('Failed to load initial anomaly data:', err);
      if (onAddToast) onAddToast(err.message, 'error', 'Error Loading Data');
    }
  }, [selectedServiceId, onAddToast]);

  // Load alerts list
  const loadAlerts = useCallback(async () => {
    try {
      const res = await anomalyApi.getAnomalies({
        service_id: filterService || undefined,
        severity: filterSeverity || undefined,
        detection_method: filterMethod || undefined,
        acknowledged: filterAcknowledged !== '' ? (filterAcknowledged === 'true') : undefined,
        page,
        limit
      });
      setAlerts(res.alerts || []);
      setTotalAlerts(res.total || 0);
    } catch (err) {
      console.error('Failed to load alerts:', err);
    }
  }, [filterService, filterSeverity, filterMethod, filterAcknowledged, page, limit]);

  // Load metric history for selected service
  const loadServiceMetrics = useCallback(async (serviceId) => {
    if (!serviceId) return;
    try {
      const res = await anomalyApi.getServiceMetrics(serviceId, 35);
      setMetricHistory(res.metrics || []);
    } catch (err) {
      console.error('Failed to load metric history:', err);
    }
  }, []);

  useEffect(() => {
    loadInitialData();
  }, []);

  useEffect(() => {
    loadAlerts();
  }, [loadAlerts]);

  useEffect(() => {
    if (selectedServiceId) {
      loadServiceMetrics(selectedServiceId);
    }
  }, [selectedServiceId, loadServiceMetrics]);

  // Action: Run detection scan
  const handleRunDetection = async () => {
    setLoading(true);
    try {
      const res = await anomalyApi.runDetection({ method: detectionMethod });
      if (onAddToast) {
        if (res.anomalies_detected > 0) {
          onAddToast(
            `Detection Scan Complete: ${res.anomalies_detected} anomalies detected, ${res.new_alerts_generated} new alerts created.`,
            'warning',
            'Anomalies Detected'
          );
        } else {
          onAddToast(
            `Detection Scan Complete: All ${res.total_evaluated} services operating normally.`,
            'success',
            'Scan Complete'
          );
        }
      }
      // Refresh summary and alerts
      const newSummary = await anomalyApi.getSummary();
      setSummary(newSummary);
      loadAlerts();
    } catch (err) {
      if (onAddToast) onAddToast(err.message, 'error', 'Scan Failed');
    } finally {
      setLoading(false);
    }
  };

  // Action: Acknowledge alert
  const handleAcknowledgeAlert = async (alertId) => {
    try {
      await anomalyApi.acknowledgeAlert(alertId);
      if (onAddToast) onAddToast(`Alert ${alertId} acknowledged.`, 'success', 'Alert Acknowledged');
      loadAlerts();
      const newSummary = await anomalyApi.getSummary();
      setSummary(newSummary);
    } catch (err) {
      if (onAddToast) onAddToast(err.message, 'error', 'Acknowledgment Failed');
    }
  };

  // Action: Save updated thresholds
  const handleSaveThresholds = async (newConfig) => {
    try {
      const updated = await anomalyApi.updateThresholds(newConfig);
      setThresholds(updated);
      setIsThresholdsOpen(false);
      if (onAddToast) onAddToast('Operational thresholds updated successfully.', 'success', 'Thresholds Saved');
    } catch (err) {
      if (onAddToast) onAddToast(err.message, 'error', 'Failed to Save Thresholds');
    }
  };

  // Action: Refresh all
  const handleRefresh = async () => {
    setLoading(true);
    await Promise.all([
      loadInitialData(),
      loadAlerts(),
      loadServiceMetrics(selectedServiceId)
    ]);
    setLoading(false);
    if (onAddToast) onAddToast('Telemetry metrics and alerts refreshed.', 'info', 'Refreshed');
  };

  return (
    <div className="anomaly-dashboard-container">
      {/* Page Title & Context */}
      <div className="anomaly-page-header">
        <div className="anomaly-title-group">
          <h2>AI Anomaly Detection & Early Warning</h2>
          <p>
            Real-time metric telemetry monitoring, threshold rule evaluation, and Isolation Forest multivariate anomaly detection.
          </p>
        </div>
        <div className="simulated-pill">
          <span className="pulse-dot"></span>
          <span>Simulated Telemetry Stream</span>
        </div>
      </div>

      {/* 5 Summary Metric Cards */}
      <AnomalySummaryCards summary={summary} />

      {/* Detection Controls & Method Selector */}
      <DetectionMethodSelector
        method={detectionMethod}
        onMethodChange={setDetectionMethod}
        onRunDetection={handleRunDetection}
        onRefresh={handleRefresh}
        onOpenThresholds={() => setIsThresholdsOpen(true)}
        onOpenEvaluation={() => setIsEvaluationOpen(true)}
        loading={loading}
      />

      {/* Interactive Metric Trend Charts with Threshold Reference Lines */}
      <AnomalyTrendChart
        metricsData={metricHistory}
        services={services}
        selectedServiceId={selectedServiceId}
        onSelectService={setSelectedServiceId}
        thresholds={thresholds}
      />

      {/* Anomaly Alerts Table */}
      <AnomalyTable
        alerts={alerts}
        total={totalAlerts}
        page={page}
        limit={limit}
        onPageChange={setPage}
        services={services}
        filterService={filterService}
        onFilterServiceChange={setFilterService}
        filterSeverity={filterSeverity}
        onFilterSeverityChange={setFilterSeverity}
        filterMethod={filterMethod}
        onFilterMethodChange={setFilterMethod}
        filterAcknowledged={filterAcknowledged}
        onFilterAcknowledgedChange={setFilterAcknowledged}
        onAcknowledge={handleAcknowledgeAlert}
        onViewDetails={setSelectedAlertForDetails}
      />

      {/* Modals */}
      <ThresholdSettings
        isOpen={isThresholdsOpen}
        onClose={() => setIsThresholdsOpen(false)}
        initialThresholds={thresholds}
        onSave={handleSaveThresholds}
      />

      <AlertDetailsPanel
        alert={selectedAlertForDetails}
        onClose={() => setSelectedAlertForDetails(null)}
        onAcknowledge={handleAcknowledgeAlert}
      />

      <EvaluationModal
        isOpen={isEvaluationOpen}
        onClose={() => setIsEvaluationOpen(false)}
      />
    </div>
  );
}
