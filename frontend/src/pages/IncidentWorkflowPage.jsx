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
  ChevronRight,
  Play,
  Zap,
  RotateCcw
} from 'lucide-react';
import { dashboardApi } from '../services/dashboardApi';
import SkeletonLoader from '../components/common/SkeletonLoader';
import EmptyState from '../components/common/EmptyState';

export default function IncidentWorkflowPage({ onNavigateModule }) {
  const [workflow, setWorkflow] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [simulatedStepIndex, setSimulatedStepIndex] = useState(null);
  const [filterMode, setFilterMode] = useState('all'); // 'all' | 'completed' | 'pending'

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

  const steps = (workflow?.steps || []).map((step, idx) => {
    if (simulatedStepIndex !== null) {
      if (idx < simulatedStepIndex) {
        return { ...step, status: 'COMPLETED' };
      }
      if (idx === simulatedStepIndex) {
        return { ...step, status: 'IN_PROGRESS' };
      }
      return { ...step, status: 'PENDING' };
    }
    return step;
  });

  const completedCount = steps.filter(s => s.status === 'COMPLETED').length;
  const progressPct = steps.length > 0 ? Math.round((completedCount / steps.length) * 100) : 0;

  const handleAdvanceStep = () => {
    setSimulatedStepIndex(prev => {
      if (prev === null) return 1;
      if (prev >= steps.length) return steps.length;
      return prev + 1;
    });
  };

  const handleResetWalkthrough = () => {
    setSimulatedStepIndex(null);
    loadWorkflow();
  };

  const filteredSteps = steps.filter(s => {
    if (filterMode === 'completed') return s.status === 'COMPLETED';
    if (filterMode === 'pending') return s.status !== 'COMPLETED';
    return true;
  });

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
          {/* Interactive Walkthrough Simulator */}
          <button 
            className="btn btn-drill-trigger"
            onClick={handleAdvanceStep}
            title="Step through investigation phases with simulated evidence"
          >
            <Play size={13} fill="currentColor" />
            <span>Advance Step ({simulatedStepIndex !== null ? Math.min(simulatedStepIndex + 1, 10) : completedCount + 1}/10)</span>
          </button>

          {simulatedStepIndex !== null && (
            <button
              className="btn btn-secondary"
              onClick={handleResetWalkthrough}
              title="Reset walkthrough simulation back to database records"
            >
              <RotateCcw size={13} />
              <span>Reset</span>
            </button>
          )}

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

      {loading && !workflow ? (
        <SkeletonLoader variant="table" count={5} />
      ) : (
        <>
          {/* Progress Bar & Status Pill */}
          <div className="workflow-progress-bar-container">
            <div className="progress-header">
              <span>Lifecycle Progress: {completedCount} of {steps.length} Steps Completed</span>
              <span style={{ color: '#38bdf8', fontWeight: 700 }}>{progressPct}% Verified</span>
            </div>
            <div className="progress-track">
              <div className="progress-fill" style={{ width: `${progressPct}%` }} />
            </div>
            <div style={{ fontSize: '0.78rem', color: '#94a3b8', display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: '8px' }}>
              <span>Incident ID: <strong>{workflow?.incident_id || 'inc-payment-cascade-01'}</strong></span>
              <span>Root Cause Target: <strong style={{ color: '#38bdf8' }}>{workflow?.service_id || 'srv-payment'}</strong></span>
              <span>Status: <strong style={{ color: progressPct === 100 ? '#10b981' : '#f59e0b' }}>{progressPct === 100 ? 'RESOLVED & VERIFIED' : 'ACTIVE INVESTIGATION'}</strong></span>
            </div>
          </div>

          {/* Filter Pills */}
          <div style={{ display: 'flex', gap: '8px', margin: '0.5rem 0' }}>
            <button 
              className={`filter-pill ${filterMode === 'all' ? 'active' : ''}`}
              onClick={() => setFilterMode('all')}
            >
              All 10 Steps
            </button>
            <button 
              className={`filter-pill ${filterMode === 'completed' ? 'active' : ''}`}
              onClick={() => setFilterMode('completed')}
            >
              Completed ({completedCount})
            </button>
            <button 
              className={`filter-pill ${filterMode === 'pending' ? 'active' : ''}`}
              onClick={() => setFilterMode('pending')}
            >
              Action Required ({steps.length - completedCount})
            </button>
          </div>

          {/* 10-Step Timeline */}
          <div className="steps-list">
            {filteredSteps.map((step) => {
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
                        border: 'none',
                        fontWeight: 600
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
                      title={`Jump to ${step.module} interface`}
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
            <div className="db-panel" style={{ marginTop: '1.5rem' }}>
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
        </>
      )}
    </div>
  );
}
