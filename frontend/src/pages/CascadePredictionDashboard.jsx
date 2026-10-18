import React, { useState, useEffect, useCallback } from 'react';
import { 
  GitBranch, 
  Play, 
  Layers, 
  Award, 
  RotateCcw, 
  ShieldAlert, 
  Info,
  CheckCircle,
  AlertTriangle
} from 'lucide-react';

import { cascadeApi } from '../services/cascadeApi';
import { api } from '../services/api';
import CascadeSummaryCards from '../components/cascade/CascadeSummaryCards';
import FailureScenarioForm from '../components/cascade/FailureScenarioForm';
import CascadeGraphViewer from '../components/cascade/CascadeGraphViewer';
import PropagationTimeline from '../components/cascade/PropagationTimeline';
import ImpactedServicesTable from '../components/cascade/ImpactedServicesTable';
import FailurePathsModal from '../components/cascade/FailurePathsModal';
import CascadeEvaluationModal from '../components/cascade/CascadeEvaluationModal';
import ScenarioComparisonModal from '../components/cascade/ScenarioComparisonModal';

import '../styles/cascade-dashboard.css';

const PRESETS = [
  {
    name: 'Payment Service Outage',
    serviceId: 'srv-payment',
    failureType: 'service_unavailable',
    severity: 'severe',
    steps: 4,
    attenuation: 0.8
  },
  {
    name: 'Database Latency Backlog',
    serviceId: 'srv-database',
    failureType: 'latency_spike',
    severity: 'severe',
    steps: 4,
    attenuation: 0.75
  },
  {
    name: 'Auth Error Storm',
    serviceId: 'srv-auth',
    failureType: 'error_rate_surge',
    severity: 'moderate',
    steps: 3,
    attenuation: 0.7
  },
  {
    name: 'Product Memory Saturation',
    serviceId: 'srv-product',
    failureType: 'memory_leak',
    severity: 'moderate',
    steps: 3,
    attenuation: 0.65
  }
];

export default function CascadePredictionDashboard() {
  const [services, setServices] = useState([]);
  const [graphData, setGraphData] = useState(null);
  const [summary, setSummary] = useState(null);
  
  // Scenario configuration state
  const [selectedServiceId, setSelectedServiceId] = useState('srv-payment');
  const [failureType, setFailureType] = useState('service_unavailable');
  const [severity, setSeverity] = useState('severe');
  const [steps, setSteps] = useState(4);
  const [attenuation, setAttenuation] = useState(0.75);

  // Prediction output state
  const [prediction, setPrediction] = useState(null);
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [statusMessage, setStatusMessage] = useState(null);

  // Modals state
  const [inspectingService, setInspectingService] = useState(null);
  const [showEvaluationModal, setShowEvaluationModal] = useState(false);
  const [showComparisonModal, setShowComparisonModal] = useState(false);

  // 1. Initial Data Fetch
  const loadInitialData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const [servicesRes, graphRes, summaryRes] = await Promise.all([
        api.getServices(),
        api.getGraph(),
        cascadeApi.getSummary()
      ]);

      const svcList = servicesRes.items || servicesRes || [];
      setServices(svcList);
      setGraphData(graphRes);
      setSummary(summaryRes);

      if (svcList.length > 0 && !selectedServiceId) {
        setSelectedServiceId(svcList[0].id);
      }
    } catch (err) {
      console.error('Failed to load cascade digital twin data:', err);
      setError(err.message || 'Failed to load cloud infrastructure data.');
    } finally {
      setLoading(false);
    }
  }, [selectedServiceId]);

  useEffect(() => {
    loadInitialData();
  }, [loadInitialData]);

  // 2. Run Cascade Prediction
  const handlePredict = async () => {
    if (!selectedServiceId) return;
    try {
      setLoading(true);
      setError(null);
      setStatusMessage('Simulating failure propagation across digital twin graph...');

      const payload = {
        initial_service_id: selectedServiceId,
        failure_type: failureType,
        failure_severity: severity,
        propagation_steps: steps,
        attenuation_factor: attenuation
      };

      const result = await cascadeApi.predictCascade(payload);
      setPrediction(result);
      setActiveStep(result.simulation_timeline?.length ? result.simulation_timeline.length - 1 : 0);
      setStatusMessage(`Prediction complete: ${result.total_impacted_services} services impacted.`);
    } catch (err) {
      console.error('Prediction failed:', err);
      setError(err.message || 'Cascading failure prediction failed.');
    } finally {
      setLoading(false);
    }
  };

  // 3. Run Step-by-Step Simulation (starts at Step 0)
  const handleSimulate = async () => {
    if (!selectedServiceId) return;
    try {
      setLoading(true);
      setError(null);

      const payload = {
        initial_service_id: selectedServiceId,
        failure_type: failureType,
        failure_severity: severity,
        propagation_steps: steps,
        attenuation_factor: attenuation
      };

      const result = await cascadeApi.simulateCascade(payload);
      setPrediction(result);
      setActiveStep(0); // Inception wave
      setStatusMessage('Simulation initiated. Use timeline scrubber to step through failure waves.');
    } catch (err) {
      console.error('Simulation failed:', err);
      setError(err.message || 'Simulation execution failed.');
    } finally {
      setLoading(false);
    }
  };

  // 4. Save Scenario
  const handleSaveScenario = async (scenarioName) => {
    if (!prediction) return;
    try {
      const payload = {
        scenario_name: scenarioName,
        initial_service_id: prediction.initial_service_id,
        failure_type: prediction.failure_type,
        failure_severity: prediction.failure_severity,
        input_parameters: {
          propagation_steps: steps,
          attenuation_factor: attenuation
        },
        result_summary: {
          total_impacted_services: prediction.total_impacted_services,
          direct_impact_count: prediction.direct_impact_count,
          indirect_impact_count: prediction.indirect_impact_count,
          high_risk_count: prediction.high_risk_count,
          critical_risk_count: prediction.critical_risk_count,
          max_risk_score: prediction.max_risk_score
        }
      };

      await cascadeApi.saveScenario(payload);
      setStatusMessage(`Scenario "${scenarioName}" saved to SQLite database successfully.`);
      const updatedSummary = await cascadeApi.getSummary();
      setSummary(updatedSummary);
    } catch (err) {
      alert('Failed to save scenario: ' + err.message);
    }
  };

  // 5. Apply Quick Preset
  const handleApplyPreset = (preset) => {
    setSelectedServiceId(preset.serviceId);
    setFailureType(preset.failureType);
    setSeverity(preset.severity);
    setSteps(preset.steps);
    setAttenuation(preset.attenuation);
  };

  return (
    <div className="cascade-dashboard-container">
      {/* Page Header */}
      <div className="cascade-page-header">
        <div className="cascade-title-group">
          <h2>
            <GitBranch size={22} color="#3b82f6" />
            Cascading Failure Prediction Engine
          </h2>
          <p>
            AI-Powered Cloud Resilience Digital Twin & Intelligent Failure Prevention Agent · Module 3
          </p>
        </div>

        <div className="cascade-header-actions">
          <button
            type="button"
            className="timeline-btn"
            onClick={() => setShowEvaluationModal(true)}
          >
            <Award size={14} color="#3b82f6" />
            Benchmark Evaluation
          </button>

          <button
            type="button"
            className="timeline-btn"
            onClick={() => setShowComparisonModal(true)}
          >
            <Layers size={14} color="#8b5cf6" />
            Compare Scenarios
          </button>

          <button
            type="button"
            className="timeline-btn"
            onClick={() => {
              setPrediction(null);
              setActiveStep(0);
              setStatusMessage('Simulation cleared. Digital twin baseline restored.');
            }}
          >
            <RotateCcw size={14} />
            Reset
          </button>
        </div>
      </div>

      {/* Incident Simulation Presets Bar */}
      <div className="cascade-presets-bar">
        <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)' }}>
          Quick Scenario Presets:
        </span>
        {PRESETS.map((p, idx) => (
          <button
            key={idx}
            type="button"
            className="preset-chip"
            onClick={() => handleApplyPreset(p)}
          >
            {p.name}
          </button>
        ))}
      </div>

      {/* Notifications / Status */}
      {statusMessage && (
        <div style={{ background: 'rgba(59, 130, 246, 0.1)', border: '1px solid rgba(59, 130, 246, 0.3)', padding: '10px 14px', borderRadius: 'var(--radius-sm)', fontSize: '0.8rem', color: '#93c5fd', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span>{statusMessage}</span>
          <button style={{ background: 'transparent', border: 'none', color: '#93c5fd', cursor: 'pointer' }} onClick={() => setStatusMessage(null)}>×</button>
        </div>
      )}

      {error && (
        <div style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', padding: '10px 14px', borderRadius: 'var(--radius-sm)', fontSize: '0.8rem', color: '#fca5a5' }}>
          {error}
        </div>
      )}

      {/* Summary KPI Cards */}
      <CascadeSummaryCards prediction={prediction} summary={summary} />

      {/* Executive Recommendations Banner */}
      {prediction?.recommendations?.length > 0 && (
        <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderLeft: '4px solid #3b82f6', borderRadius: 'var(--radius-md)', padding: '14px 18px' }}>
          <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
            <ShieldAlert size={16} color="#3b82f6" />
            Decision-Support Failure Mitigation Recommendations:
          </div>
          <ul style={{ paddingLeft: '20px', fontSize: '0.8rem', color: 'var(--text-muted)', display: 'flex', flexDirection: 'column', gap: '4px' }}>
            {prediction.recommendations.map((rec, i) => (
              <li key={i}>{rec}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Workspace Grid: Scenario Builder (Left) + Graph Viewer (Right) */}
      <div className="cascade-workspace-grid">
        <FailureScenarioForm
          services={services}
          selectedServiceId={selectedServiceId}
          setSelectedServiceId={setSelectedServiceId}
          failureType={failureType}
          setFailureType={setFailureType}
          severity={severity}
          setSeverity={setSeverity}
          steps={steps}
          setSteps={setSteps}
          attenuation={attenuation}
          setAttenuation={setAttenuation}
          onPredict={handlePredict}
          onSimulate={handleSimulate}
          onSaveScenario={handleSaveScenario}
          loading={loading}
          hasPrediction={!!prediction}
        />

        <CascadeGraphViewer
          graphData={graphData}
          prediction={prediction}
          currentStep={activeStep}
          selectedServiceId={selectedServiceId}
          onSelectService={(id) => {
            setSelectedServiceId(id);
            const found = prediction?.impacted_services?.find(s => s.service_id === id);
            if (found) {
              setInspectingService(found);
            }
          }}
        />
      </div>

      {/* Simulation Timeline Player */}
      {prediction?.simulation_timeline?.length > 0 && (
        <PropagationTimeline
          timeline={prediction.simulation_timeline}
          activeStep={activeStep}
          setActiveStep={setActiveStep}
        />
      )}

      {/* Impacted Services Assessment Table */}
      <ImpactedServicesTable
        impactedServices={prediction?.impacted_services || []}
        selectedServiceId={selectedServiceId}
        onSelectService={(id) => setSelectedServiceId(id)}
        onViewPaths={(svc) => setInspectingService(svc)}
      />

      {/* Modal: Failure Paths & Evidence */}
      {inspectingService && (
        <FailurePathsModal
          service={inspectingService}
          onClose={() => setInspectingService(null)}
        />
      )}

      {/* Modal: Benchmark Ground-Truth Evaluation */}
      {showEvaluationModal && (
        <CascadeEvaluationModal
          onClose={() => setShowEvaluationModal(false)}
        />
      )}

      {/* Modal: Scenario Comparison */}
      {showComparisonModal && (
        <ScenarioComparisonModal
          onClose={() => setShowComparisonModal(false)}
        />
      )}
    </div>
  );
}
