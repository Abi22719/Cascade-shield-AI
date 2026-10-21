import React, { useState, useEffect, useCallback } from 'react';
import { 
  ShieldAlert, 
  Search, 
  Award, 
  Layers, 
  FileText, 
  RotateCcw, 
  Stethoscope, 
  Clock, 
  Zap,
  CheckCircle2,
  AlertTriangle
} from 'lucide-react';

import { rcaApi } from '../services/rcaApi';
import { api } from '../services/api';
import IncidentSummary from '../components/rca/IncidentSummary';
import RootCauseRanking from '../components/rca/RootCauseRanking';
import ConfidenceIndicator from '../components/rca/ConfidenceIndicator';
import EvidenceTimeline from '../components/rca/EvidenceTimeline';
import DependencyImpactGraph from '../components/rca/DependencyImpactGraph';
import AlternativeHypotheses from '../components/rca/AlternativeHypotheses';
import DiagnosticRecommendations from '../components/rca/DiagnosticRecommendations';
import EvidenceDetails from '../components/rca/EvidenceDetails';
import RCAReportPanel from '../components/rca/RCAReportPanel';
import RCAEvaluationModal from '../components/rca/RCAEvaluationModal';
import RCACompareModal from '../components/rca/RCACompareModal';

import '../styles/rca-dashboard.css';

const INCIDENT_PRESETS = [
  {
    name: 'Payment Latency Storm',
    targetService: 'srv-payment',
    affectedServices: ['srv-order', 'srv-gateway'],
    title: 'Payment Gateway Upstream Latency Storm',
    telemetry: {
      'srv-payment': { latency_ms: 1250.0, error_rate: 12.5, cpu_usage: 88.0 },
      'srv-database': { latency_ms: 35.0, error_rate: 0.1, cpu_usage: 28.0 },
      'srv-auth': { latency_ms: 32.0, error_rate: 0.1, cpu_usage: 30.0 }
    }
  },
  {
    name: 'Database Pool Exhaustion',
    targetService: 'srv-database',
    affectedServices: ['srv-order', 'srv-product', 'srv-gateway'],
    title: 'Relational Database Connection Starvation',
    telemetry: {
      'srv-database': { latency_ms: 1450.0, error_rate: 14.8, cpu_usage: 94.5 },
      'srv-payment': { latency_ms: 85.0, error_rate: 0.2, cpu_usage: 25.0 },
      'srv-auth': { latency_ms: 32.0, error_rate: 0.1, cpu_usage: 30.0 }
    }
  },
  {
    name: 'Auth Token Verification Outage',
    targetService: 'srv-auth',
    affectedServices: ['srv-user', 'srv-order', 'srv-gateway'],
    title: 'OAuth/JWT Auth Verifier Outage',
    telemetry: {
      'srv-auth': { latency_ms: 980.0, error_rate: 22.0, cpu_usage: 92.0 },
      'srv-database': { latency_ms: 35.0, error_rate: 0.1, cpu_usage: 28.0 },
      'srv-payment': { latency_ms: 85.0, error_rate: 0.2, cpu_usage: 25.0 }
    }
  },
  {
    name: 'Ambiguous / Insufficient Telemetry',
    targetService: 'srv-notify',
    affectedServices: [],
    title: 'Uncorroborated Mild Telemetry Fluctuation',
    telemetry: {
      'srv-notify': { latency_ms: 120.0, error_rate: 1.5, cpu_usage: 45.0 },
      'srv-database': { latency_ms: 35.0, error_rate: 0.1, cpu_usage: 28.0 },
      'srv-payment': { latency_ms: 85.0, error_rate: 0.2, cpu_usage: 25.0 },
      'srv-auth': { latency_ms: 32.0, error_rate: 0.1, cpu_usage: 30.0 }
    }
  }
];

export default function RCADashboard({ onAddToast }) {
  const [services, setServices] = useState([]);
  const [graphData, setGraphData] = useState(null);
  const [activePresetName, setActivePresetName] = useState('Payment Latency Storm');

  // Form inputs
  const [incidentTitle, setIncidentTitle] = useState('Payment Gateway Upstream Latency Storm');
  const [targetServiceId, setTargetServiceId] = useState('srv-payment');
  const [affectedServiceIds, setAffectedServiceIds] = useState(['srv-order', 'srv-gateway']);

  // Output report state
  const [report, setReport] = useState(null);
  const [selectedCandidateId, setSelectedCandidateId] = useState('srv-payment');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [statusMessage, setStatusMessage] = useState(null);

  // Modals state
  const [showEvaluationModal, setShowEvaluationModal] = useState(false);
  const [showCompareModal, setShowCompareModal] = useState(false);
  const [showEvidenceModal, setShowEvidenceModal] = useState(false);
  const [showReportModal, setShowReportModal] = useState(false);

  // 1. Initial Data Fetch
  const loadInitialData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const [servicesRes, graphRes] = await Promise.all([
        api.getServices(),
        api.getGraph()
      ]);

      const svcList = servicesRes.items || servicesRes || [];
      setServices(svcList);
      setGraphData(graphRes);

      // Auto-run baseline incident analysis on first load
      const initialPayload = {
        incident_title: 'Payment Gateway Upstream Latency Storm',
        target_service_id: 'srv-payment',
        affected_service_ids: ['srv-order', 'srv-gateway'],
        include_alternatives: true,
        include_recommendations: true
      };

      const res = await rcaApi.analyzeIncident(initialPayload);
      setReport(res);
      if (res.primary_root_cause) {
        setSelectedCandidateId(res.primary_root_cause.service_id);
      }
    } catch (err) {
      console.error('Failed to initialize RCA digital twin data:', err);
      setError(err.message || 'Failed to initialize RCA digital twin baseline.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadInitialData();
  }, [loadInitialData]);

  // 2. Run Root Cause Analysis
  const handleAnalyze = async () => {
    try {
      setLoading(true);
      setError(null);
      setStatusMessage('Correlating multi-source evidence, evaluating temporal precedence and dependency topology...');

      const payload = {
        incident_title: incidentTitle.trim() || undefined,
        target_service_id: targetServiceId || undefined,
        affected_service_ids: affectedServiceIds,
        include_alternatives: true,
        include_recommendations: true
      };

      const result = await rcaApi.analyzeIncident(payload);
      setReport(result);
      if (result.primary_root_cause) {
        setSelectedCandidateId(result.primary_root_cause.service_id);
      }
      setStatusMessage(`Analysis complete: Isolated "${result.primary_root_cause?.service_name || 'Inconclusive'}" with ${result.primary_root_cause?.confidence_label || 'Insufficient Evidence'}.`);
      if (onAddToast) {
        onAddToast(`RCA complete: ${result.primary_root_cause?.service_name || 'Inconclusive'}`, 'success', 'RCA Engine');
      }
    } catch (err) {
      console.error('RCA failed:', err);
      setError(err.message || 'Root cause investigation failed.');
      if (onAddToast) {
        onAddToast(err.message || 'Analysis failed', 'error', 'RCA Engine');
      }
    } finally {
      setLoading(false);
    }
  };

  // 3. Apply Quick Incident Preset
  const handleApplyPreset = async (preset) => {
    setActivePresetName(preset.name);
    setIncidentTitle(preset.title);
    setTargetServiceId(preset.targetService);
    setAffectedServiceIds(preset.affectedServices);

    try {
      setLoading(true);
      setError(null);
      setStatusMessage(`Applying incident preset "${preset.name}" and correlating telemetry...`);

      // Update simulated services in digital twin if telemetry is configured
      if (preset.telemetry) {
        await Promise.all(
          Object.entries(preset.telemetry).map(([svcId, patch]) =>
            api.updateService(svcId, patch).catch(e => console.warn('Could not patch service', svcId, e))
          )
        );
      }

      // Re-fetch services and graph so local state is fresh
      const [servicesRes, graphRes] = await Promise.all([
        api.getServices(),
        api.getGraph()
      ]);
      setServices(servicesRes.items || servicesRes || []);
      setGraphData(graphRes);

      // Run root cause investigation for this preset
      const payload = {
        incident_title: preset.title,
        target_service_id: preset.targetService,
        affected_service_ids: preset.affectedServices,
        include_alternatives: true,
        include_recommendations: true
      };

      const result = await rcaApi.analyzeIncident(payload);
      setReport(result);
      if (result.primary_root_cause) {
        setSelectedCandidateId(result.primary_root_cause.service_id);
      }
      setStatusMessage(`Analysis complete: Isolated "${result.primary_root_cause?.service_name || 'Inconclusive'}" with ${result.primary_root_cause?.confidence_label || 'Insufficient Evidence'}.`);
      if (onAddToast) {
        onAddToast(`RCA complete: ${result.primary_root_cause?.service_name || 'Inconclusive'}`, 'success', 'RCA Engine');
      }
    } catch (err) {
      console.error('RCA preset execution failed:', err);
      setError(err.message || 'Failed to analyze selected preset.');
    } finally {
      setLoading(false);
    }
  };

  // 4. Toggle Affected Service Checkbox
  const toggleAffectedService = (id) => {
    if (affectedServiceIds.includes(id)) {
      setAffectedServiceIds(affectedServiceIds.filter(item => item !== id));
    } else {
      setAffectedServiceIds([...affectedServiceIds, id]);
    }
  };

  const handleSelectCandidate = useCallback((id) => {
    setSelectedCandidateId(id);
  }, []);

  const primaryRootCauseId = report?.primary_root_cause?.service_id || null;
  const candidateIds = report?.ranked_candidates?.map(c => c.service_id) || [];

  return (
    <div className="rca-dashboard-container">
      {/* Page Header */}
      <div className="rca-page-header">
        <div className="rca-title-group">
          <h2>
            <ShieldAlert size={22} color="#8b5cf6" />
            Evidence-Grounded Root Cause Analysis (RCA) Engine
          </h2>
          <p>
            Multi-Source Evidence Correlation, Temporal Precedence & Diagnostic Recommendations · Module 4
          </p>
        </div>

        <div className="rca-header-actions">
          <button
            type="button"
            className="timeline-btn"
            onClick={() => setShowEvaluationModal(true)}
          >
            <Award size={14} color="#8b5cf6" />
            Benchmark Evaluation
          </button>

          <button
            type="button"
            className="timeline-btn"
            onClick={() => setShowCompareModal(true)}
          >
            <Layers size={14} color="#3b82f6" />
            Compare Investigations
          </button>

          <button
            type="button"
            className="timeline-btn"
            onClick={() => setShowEvidenceModal(true)}
            disabled={!report || report.evidence_items?.length === 0}
          >
            <Layers size={14} color="#10b981" />
            Evidence Registry ({report?.evidence_count || 0})
          </button>

          <button
            type="button"
            className="timeline-btn"
            onClick={() => setShowReportModal(true)}
            disabled={!report}
          >
            <FileText size={14} color="#f59e0b" />
            Audit Report
          </button>
        </div>
      </div>

      {/* Incident Presets Bar */}
      <div className="rca-presets-bar">
        <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)' }}>
          Incident Presets:
        </span>
        {INCIDENT_PRESETS.map((p, idx) => (
          <button
            key={idx}
            type="button"
            className={`rca-preset-btn ${activePresetName === p.name ? 'active' : ''}`}
            onClick={() => handleApplyPreset(p)}
          >
            {p.name}
          </button>
        ))}
      </div>

      {/* Status & Error Alerts */}
      {statusMessage && (
        <div style={{ background: 'rgba(139, 92, 246, 0.1)', border: '1px solid rgba(139, 92, 246, 0.3)', padding: '10px 14px', borderRadius: 'var(--radius-sm)', fontSize: '0.8rem', color: '#c4b5fd', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span>{statusMessage}</span>
          <button style={{ background: 'transparent', border: 'none', color: '#c4b5fd', cursor: 'pointer' }} onClick={() => setStatusMessage(null)}>×</button>
        </div>
      )}

      {error && (
        <div style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', padding: '10px 14px', borderRadius: 'var(--radius-sm)', fontSize: '0.8rem', color: '#fca5a5' }}>
          {error}
        </div>
      )}

      {/* Incident Summary KPI Cards */}
      <IncidentSummary report={report} />

      {/* Main 3-Column Workspace */}
      <div className="rca-workspace-grid">
        {/* Column 1: Incident Configuration Form */}
        <div className="rca-form-card">
          <h3>
            <Search size={16} color="#8b5cf6" />
            Incident Investigation Scope
          </h3>

          <div className="form-group">
            <label>Incident Investigation Title</label>
            <input
              type="text"
              className="form-input"
              value={incidentTitle}
              onChange={e => setIncidentTitle(e.target.value)}
              placeholder="e.g. Black Friday Checkout Drop"
            />
          </div>

          <div className="form-group">
            <label>Suspected / Target Service</label>
            <select
              className="form-select"
              value={targetServiceId}
              onChange={e => setTargetServiceId(e.target.value)}
              disabled={loading}
            >
              {services.map(s => (
                <option key={s.id} value={s.id}>
                  {s.name} ({s.id}) · {s.health_status}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Observed Affected Microservices ({affectedServiceIds.length}):</label>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', maxHeight: '180px', overflowY: 'auto', background: 'var(--bg-hover)', padding: '8px', borderRadius: '4px', border: '1px solid var(--border-color)' }}>
              {services.map(s => {
                const isChecked = affectedServiceIds.includes(s.id);
                return (
                  <label key={s.id} style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.75rem', color: 'var(--text-main)', cursor: 'pointer' }}>
                    <input
                      type="checkbox"
                      checked={isChecked}
                      onChange={() => toggleAffectedService(s.id)}
                    />
                    <span>{s.name}</span>
                    <span style={{ marginLeft: 'auto', fontSize: '0.68rem', color: s.health_status.toLowerCase() === 'critical' ? '#ef4444' : (s.health_status.toLowerCase() === 'warning' ? '#f59e0b' : '#10b981') }}>
                      {s.health_status}
                    </span>
                  </label>
                );
              })}
            </div>
          </div>

          <button
            type="button"
            className="btn-analyze"
            onClick={handleAnalyze}
            disabled={loading}
          >
            <Zap size={16} />
            {loading ? 'Correlating Evidence...' : 'Investigate Root Cause'}
          </button>
        </div>

        {/* Column 2: Ranked Candidates */}
        <RootCauseRanking
          candidates={report?.ranked_candidates || []}
          selectedCandidateId={selectedCandidateId}
          onSelectCandidate={handleSelectCandidate}
        />

        {/* Column 3: Dependency Impact Graph */}
        <DependencyImpactGraph
          graphData={graphData}
          primaryRootCauseId={primaryRootCauseId}
          candidateIds={candidateIds}
          affectedServiceIds={affectedServiceIds}
          selectedServiceId={selectedCandidateId}
          onSelectService={handleSelectCandidate}
        />
      </div>

      {/* Confidence Indicator & Uncertainty Rationale */}
      {report?.primary_root_cause && (
        <ConfidenceIndicator
          candidate={report.primary_root_cause}
          explanation={report.confidence_and_uncertainty_explanation}
        />
      )}

      {/* Chronological Evidence Timeline */}
      <EvidenceTimeline timelineEvents={report?.evidence_timeline || []} />

      {/* Bottom 2-Column Grid: Hypotheses + Recommendations */}
      <div className="rca-bottom-grid">
        <AlternativeHypotheses hypotheses={report?.alternative_hypotheses || []} />
        <DiagnosticRecommendations recommendations={report?.diagnostic_recommendations || []} />
      </div>

      {/* Modals */}
      {showEvidenceModal && (
        <EvidenceDetails
          evidenceItems={report?.evidence_items || []}
          onClose={() => setShowEvidenceModal(false)}
        />
      )}

      {showReportModal && (
        <RCAReportPanel
          report={report}
          onClose={() => setShowReportModal(false)}
        />
      )}

      {showEvaluationModal && (
        <RCAEvaluationModal
          onClose={() => setShowEvaluationModal(false)}
        />
      )}

      {showCompareModal && (
        <RCACompareModal
          onClose={() => setShowCompareModal(false)}
        />
      )}
    </div>
  );
}
