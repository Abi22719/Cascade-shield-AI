import React, { useState, useEffect, useCallback } from 'react';
import { 
  Route, 
  CheckCircle2, 
  Clock, 
  AlertCircle, 
  ArrowRight, 
  RefreshCw, 
  ShieldCheck,
  ExternalLink,
  ChevronRight
} from 'lucide-react';
import { dashboardApi } from '../services/dashboardApi';

export default function IncidentWorkflowPage({ onNavigateModule }) {
  const [workflow, setWorkflow] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadWorkflow = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await dashboardApi.getIncidentWorkflow();
      setWorkflow(data);
    } catch (err) {
      setError(err.message || "Failed to load incident investigation workflow");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadWorkflow();
  }, [loadWorkflow]);

  const mapStepToModule = (stepNumber) => {
    switch(stepNumber) {
      case 1: return 'anomaly-detection';
      case 2: return 'root-cause-analysis';
      case 3: return 'cascade-prediction';
      case 4: return 'root-cause-analysis';
      case 5: return 'diagnostic-agent';
      case 6: return 'what-if-simulation';
      case 7: return 'recovery-planning';
      case 8: return 'recovery-planning';
      case 9: return 'recovery-validation';
      case 10: return 'reports-center';
      default: return 'digital-twin';
    }
  };

  const steps = workflow?.steps || [];
  const completedCount = steps.filter(s => s.status === 'COMPLETED').length;
  const progressPct = steps.length > 0 ? Math.round((completedCount / steps.length) * 100) : 0;

  return (
    <div className="workflow-page">
      {/* Header */}
      <div className="workflow-header">
        <div className="db-title-group">
          <h2>
            <Route size={24} color="#38bdf8" />
            <span>End-to-End Incident Investigation Workflow</span>
          </h2>
          <p>
            Guided 10-step lifecycle connecting telemetry detection, causal diagnosis, simulation, recovery planning, and verification.
          </p>
        </div>

        <div className="db-header-actions">
          <button 
            className="btn btn-secondary" 
            onClick={loadWorkflow} 
            disabled={loading}
          >
            <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {error && (
        <div style={{ background: 'rgba(239, 68, 68, 0.15)', border: '1px solid rgba(239, 68, 68, 0.4)', borderRadius: '8px', padding: '0.75rem 1rem', color: '#fca5a5' }}>
          <strong>Error loading workflow: </strong> {error}
        </div>
      )}

      {/* Progress Bar */}
      <div className="workflow-progress-bar-container">
        <div className="progress-header">
          <span>Lifecycle Progress: {completedCount} of {steps.length} Steps Completed</span>
          <span style={{ color: '#38bdf8' }}>{progressPct}% Verified</span>
        </div>
        <div className="progress-track">
          <div className="progress-fill" style={{ width: `${progressPct}%` }} />
        </div>
        <div style={{ fontSize: '0.78rem', color: '#94a3b8', display: 'flex', justifyContent: 'space-between' }}>
          <span>Incident: {workflow?.incident_id || 'Active Cloud Degraded Event'}</span>
          <span>Target Service: <strong>{workflow?.service_id || 'srv-payment'}</strong></span>
        </div>
      </div>

      {/* 10-Step Timeline */}
      <div className="steps-list">
        {steps.map((step) => {
          const isCompleted = step.status === 'COMPLETED';
          const isInProgress = step.status === 'IN_PROGRESS';
          const targetModule = mapStepToModule(step.step_number);

          return (
            <div 
              key={step.step_number} 
              className={`step-card ${isCompleted ? 'completed' : isInProgress ? 'in-progress' : 'pending'}`}
            >
              <div className="step-number-badge">
                {isCompleted ? <CheckCircle2 size={22} color="#10b981" /> : step.step_number}
              </div>

              <div className="step-info">
                <div className="step-title-row">
                  <span className="step-name">{step.step_name}</span>
                  <span className="step-module-label">{step.module}</span>
                  <span className={`risk-pill`} style={{ 
                    background: isCompleted ? 'rgba(16, 185, 129, 0.15)' : isInProgress ? 'rgba(245, 158, 11, 0.15)' : 'rgba(255, 255, 255, 0.05)',
                    color: isCompleted ? '#6ee7b7' : isInProgress ? '#fcd34d' : '#94a3b8',
                    border: 'none'
                  }}>
                    {step.status}
                  </span>
                </div>
                <div className="step-summary">{step.summary}</div>
                {step.record_id && (
                  <span style={{ fontSize: '0.72rem', color: '#64748b' }}>
                    Linked Evidence Record: <code>{step.record_id}</code>
                  </span>
                )}
              </div>

              <div className="step-actions">
                <button 
                  className="btn-db-secondary"
                  onClick={() => onNavigateModule && onNavigateModule(targetModule)}
                  title={`Open ${step.module}`}
                >
                  <span>Open Module</span>
                  <ExternalLink size={13} />
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* AI Recommendations Bar */}
      {workflow?.recommendations && workflow.recommendations.length > 0 && (
        <div className="db-panel">
          <div className="db-panel-header">
            <div className="db-panel-title">
              <ShieldCheck size={18} color="#10b981" />
              <span>Investigation Post-Mortem Recommendations</span>
            </div>
          </div>
          <ul style={{ margin: 0, paddingLeft: '1.25rem', color: '#cbd5e1', fontSize: '0.86rem', lineHeight: '1.6' }}>
            {workflow.recommendations.map((rec, i) => (
              <li key={i}>{rec}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
