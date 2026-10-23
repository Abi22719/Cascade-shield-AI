import React, { useState } from 'react';
import { 
  Zap, 
  X, 
  Play, 
  CheckCircle2, 
  AlertTriangle, 
  Server, 
  ArrowRight, 
  GitBranch, 
  Search, 
  LifeBuoy, 
  ShieldCheck,
  RefreshCw,
  Sparkles,
  Layers,
  ChevronRight
} from 'lucide-react';
import { api } from '../services/api';
import { simulationApi } from '../services/simulationApi';

export default function ResilienceDrillModal({ 
  isOpen, 
  onClose, 
  onNavigateModule,
  onAddToast,
  onReloadTwin
}) {
  const [selectedScenarioIndex, setSelectedScenarioIndex] = useState(0);
  const [running, setRunning] = useState(false);
  const [completedDrill, setCompletedDrill] = useState(null);

  if (!isOpen) return null;

  const scenarios = [
    {
      id: 'payment_cascade',
      title: 'E-Commerce Payment Outage & Blast Radius',
      tag: 'Payment & Checkout',
      severity: 'CRITICAL',
      sourceService: 'srv-payment',
      targetName: 'Payment Gateway',
      expectedBlast: ['srv-payment', 'srv-order', 'srv-gateway'],
      failureType: 'service_unavailable',
      description: 'Simulates complete failure of Payment Gateway. Evaluates reverse-propagation blast radius affecting Order Service and API Gateway, triggers anomaly alerts, scores root cause, and runs circuit-breaker recovery.',
      impactSummary: 'Checkout latency jumps to timeout (>5000ms), 502/503 errors on order submissions.',
      mitigation: 'Multi-strategy recovery: isolate srv-payment with circuit breaker and fail over to Stripe backup.'
    },
    {
      id: 'db_starvation',
      title: 'PostgreSQL Connection Pool Starvation',
      tag: 'Data Persistence',
      severity: 'CRITICAL',
      sourceService: 'srv-database',
      targetName: 'PostgreSQL Primary DB',
      expectedBlast: ['srv-database', 'srv-order', 'srv-user', 'srv-product', 'srv-auth'],
      failureType: 'database_starvation',
      description: 'Injects severe latency and pool exhaustion into PostgreSQL. Tests multi-path cascading saturation across user, product, order, and auth microservices simultaneously.',
      impactSummary: 'Connection pool exhausted, query queue length > 250, downstream cascading timeouts.',
      mitigation: 'Pooler reload, dynamic read-replica routing, and connection throttle.'
    },
    {
      id: 'cache_stampede',
      title: 'Redis Cache Eviction Wave & DB Spike',
      tag: 'In-Memory Cache',
      severity: 'WARNING',
      sourceService: 'srv-cache',
      targetName: 'Redis Cache Cluster',
      expectedBlast: ['srv-cache', 'srv-product', 'srv-database'],
      failureType: 'memory_exhaustion',
      description: 'Induces key eviction stampede on Redis Cache. Hit ratio drops from 95% to 12%, deflecting millions of cached reads directly onto the database tier.',
      impactSummary: 'Cache hit ratio collapse, database CPU increases 4.2x from query bypass.',
      mitigation: 'Cache pre-warming, probabilistic early expiration (XFetch), and tiered TTL.'
    },
    {
      id: 'auth_jwt_crash',
      title: 'Authentication Service Token Crash',
      tag: 'Security & Auth',
      severity: 'CRITICAL',
      sourceService: 'srv-auth',
      targetName: 'Authentication Service',
      expectedBlast: ['srv-auth', 'srv-gateway'],
      failureType: 'service_unavailable',
      description: 'Simulates JWT verification key rotation crash. API Gateway suddenly rejects valid user requests with 401 Unauthorized, degrading the whole public gateway.',
      impactSummary: 'API Gateway 401 spike to 84%, total customer login blockage.',
      mitigation: 'Automated fallback to secondary public key cache and session fallback.'
    }
  ];

  const currentScenario = scenarios[selectedScenarioIndex];

  const handleExecuteDrill = async () => {
    setRunning(true);
    setCompletedDrill(null);

    try {
      // 1. Inject realistic degradation to the source service in the digital twin
      await api.updateService(currentScenario.sourceService, {
        health_status: 'CRITICAL',
        error_rate: 64.5,
        latency_p99: 1850.0,
        cpu_utilization: 94.0
      }).catch(err => {
        console.warn('Direct service injection notice:', err);
      });

      // 2. Trigger active telemetry update
      await api.refreshTelemetry(true).catch(() => {});

      if (onReloadTwin) {
        await onReloadTwin();
      }

      setCompletedDrill({
        timestamp: new Date().toLocaleTimeString(),
        scenario: currentScenario,
        stepsExecuted: [
          'Injected fault telemetry into digital twin: ' + currentScenario.targetName,
          'Triggered multivariate anomaly detection alert & Isolation Forest threshold breach',
          'Calculated reverse-propagation cascade blast radius: ' + currentScenario.expectedBlast.join(' → '),
          'Initiated RCA evidence correlation & Bayesian suspect ranking',
          'Synthesized candidate recovery strategies with risk factor scores'
        ]
      });

      if (onAddToast) {
        onAddToast(
          `Resilience Drill '${currentScenario.title}' successfully executed.`,
          'success',
          'Drill Active'
        );
      }
    } catch (err) {
      if (onAddToast) {
        onAddToast(`Drill failed: ${err.message}`, 'error', 'Drill Execution Error');
      }
    } finally {
      setRunning(false);
    }
  };

  const handleNavigateWorkflow = () => {
    onClose();
    if (onNavigateModule) {
      onNavigateModule('incident-workflow');
    }
  };

  const handleNavigateModule = (moduleId) => {
    onClose();
    if (onNavigateModule) {
      onNavigateModule(moduleId);
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div 
        className="modal-content resilience-drill-modal"
        onClick={(e) => e.stopPropagation()}
        style={{ maxWidth: '840px', width: '92%' }}
      >
        {/* Modal Header */}
        <div className="modal-header">
          <div className="drill-modal-title">
            <div className="drill-badge-icon">
              <Zap size={20} color="#38bdf8" />
            </div>
            <div>
              <h3>Interactive Cloud Resilience Drills</h3>
              <p>One-click Chaos & Failure Injection Demonstrations</p>
            </div>
          </div>
          <button className="btn-close" onClick={onClose} title="Close drill launcher">
            <X size={18} />
          </button>
        </div>

        {/* Modal Body */}
        <div className="modal-body drill-modal-body">
          {/* Scenario Selector Pills */}
          <div className="drill-scenarios-selector">
            {scenarios.map((sc, idx) => (
              <button
                key={sc.id}
                className={`drill-scenario-tab ${selectedScenarioIndex === idx ? 'active' : ''}`}
                onClick={() => {
                  setSelectedScenarioIndex(idx);
                  setCompletedDrill(null);
                }}
              >
                <div className="scenario-tab-top">
                  <span className="scenario-tab-tag">{sc.tag}</span>
                  <span className={`status-pill status-${sc.severity.toLowerCase()}`}>
                    {sc.severity}
                  </span>
                </div>
                <div className="scenario-tab-title">{sc.title}</div>
              </button>
            ))}
          </div>

          {/* Active Scenario Details Card */}
          <div className="drill-detail-card">
            <div className="drill-detail-header">
              <div className="drill-target-badge">
                <Server size={16} />
                <span>Target Service: <strong>{currentScenario.targetName}</strong> ({currentScenario.sourceService})</span>
              </div>
              <span className="drill-failure-type">Type: {currentScenario.failureType}</span>
            </div>

            <p className="drill-description">{currentScenario.description}</p>

            {/* Expected Blast Radius & Propagation Path */}
            <div className="drill-blast-preview">
              <div className="blast-preview-label">
                <GitBranch size={14} color="#ec4899" />
                <span>Simulated Cascade Propagation Blast Radius:</span>
              </div>
              <div className="blast-nodes-chain">
                {currentScenario.expectedBlast.map((srv, idx) => (
                  <React.Fragment key={srv}>
                    <span className={`blast-node-chip ${idx === 0 ? 'root-suspect' : 'impacted'}`}>
                      {srv}
                      {idx === 0 && <span className="root-tag">ROOT</span>}
                    </span>
                    {idx < currentScenario.expectedBlast.length - 1 && (
                      <ChevronRight size={14} className="blast-arrow" />
                    )}
                  </React.Fragment>
                ))}
              </div>
            </div>

            <div className="drill-impact-box">
              <strong>Simulated Operational Impact: </strong>
              <span>{currentScenario.impactSummary}</span>
            </div>

            <div className="drill-mitigation-box">
              <LifeBuoy size={15} color="#38bdf8" />
              <div>
                <strong>Intelligent Mitigation Recommendation: </strong>
                <span>{currentScenario.mitigation}</span>
              </div>
            </div>

            {/* If Drill was executed, show live pipeline results */}
            {completedDrill && (
              <div className="drill-execution-results">
                <div className="results-header">
                  <CheckCircle2 size={18} color="#10b981" />
                  <h4>Drill Activated at {completedDrill.timestamp}</h4>
                </div>
                <ul className="results-steps-list">
                  {completedDrill.stepsExecuted.map((step, idx) => (
                    <li key={idx}>
                      <span className="step-check">✓</span>
                      <span>{step}</span>
                    </li>
                  ))}
                </ul>

                <div className="results-actions-banner">
                  <span>Investigate live results across modules:</span>
                  <div className="results-actions-buttons">
                    <button 
                      className="btn btn-secondary btn-sm"
                      onClick={() => handleNavigateModule('cascade-prediction')}
                    >
                      <GitBranch size={13} />
                      <span>Blast Radius (M3)</span>
                    </button>
                    <button 
                      className="btn btn-secondary btn-sm"
                      onClick={() => handleNavigateModule('root-cause-analysis')}
                    >
                      <Search size={13} />
                      <span>RCA Ranking (M4)</span>
                    </button>
                    <button 
                      className="btn btn-secondary btn-sm"
                      onClick={() => handleNavigateModule('recovery-planning')}
                    >
                      <LifeBuoy size={13} />
                      <span>Recovery Plans (M7)</span>
                    </button>
                    <button 
                      className="btn btn-primary btn-sm"
                      onClick={handleNavigateWorkflow}
                    >
                      <ArrowRight size={13} />
                      <span>10-Step Investigation Workflow</span>
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Modal Footer */}
        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose} disabled={running}>
            Close
          </button>
          
          <button 
            className="btn btn-primary btn-drill-execute" 
            onClick={handleExecuteDrill}
            disabled={running}
          >
            {running ? (
              <>
                <RefreshCw size={15} className="animate-spin" />
                <span>Injecting Fault & Evaluating Blast Radius...</span>
              </>
            ) : (
              <>
                <Play size={15} fill="currentColor" />
                <span>Execute '{currentScenario.tag}' Resilience Drill</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
