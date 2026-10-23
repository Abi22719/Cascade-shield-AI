import React, { useState } from 'react';
import { 
  Sparkles, 
  HelpCircle, 
  ArrowRight, 
  AlertCircle, 
  CheckCircle2, 
  Database,
  Layers,
  ShieldAlert,
  GitBranch,
  Bot,
  LifeBuoy
} from 'lucide-react';
import SkeletonLoader from './common/SkeletonLoader';
import EmptyState from './common/EmptyState';

export default function ExplainabilityPanel({ insights = [], loading, onNavigateModule }) {
  const [filterType, setFilterType] = useState('all'); // 'all' | 'high_risk' | 'uncertainty'

  if (loading) {
    return (
      <div className="db-panel">
        <div className="db-panel-header">
          <div className="db-panel-title">
            <Sparkles size={18} color="#38bdf8" />
            <span>Explainable AI Insights</span>
          </div>
          <div className="simulated-pill" style={{ fontSize: '0.72rem' }}>
            <Database size={12} />
            <span>Grounded Reasoner</span>
          </div>
        </div>
        <SkeletonLoader variant="card" count={2} height="160px" />
      </div>
    );
  }

  const filteredInsights = insights.filter(ins => {
    if (filterType === 'high_risk') {
      return ins.risk_factors && ins.risk_factors.length > 0;
    }
    if (filterType === 'uncertainty') {
      return Boolean(ins.uncertainty_notes);
    }
    return true;
  });

  const getModuleTarget = (sourceModule) => {
    const s = String(sourceModule || '').toLowerCase();
    if (s.includes('anomaly') || s.includes('m2')) return 'anomaly-detection';
    if (s.includes('cascade') || s.includes('m3')) return 'cascade-prediction';
    if (s.includes('rca') || s.includes('m4') || s.includes('root')) return 'root-cause-analysis';
    if (s.includes('agent') || s.includes('m5')) return 'diagnostic-agent';
    if (s.includes('sim') || s.includes('m6')) return 'what-if-simulation';
    if (s.includes('recovery') || s.includes('m7')) return 'recovery-planning';
    if (s.includes('valid') || s.includes('m8')) return 'recovery-validation';
    if (s.includes('bench') || s.includes('m9')) return 'resilience-benchmark';
    return 'incident-workflow';
  };

  return (
    <div className="db-panel">
      <div className="db-panel-header">
        <div className="db-panel-title">
          <Sparkles size={18} color="#38bdf8" />
          <span>Explainable AI Insights</span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {/* Filter Pills */}
          <div className="insights-filter-pills">
            <button 
              className={`filter-pill ${filterType === 'all' ? 'active' : ''}`}
              onClick={() => setFilterType('all')}
            >
              All ({insights.length})
            </button>
            <button 
              className={`filter-pill ${filterType === 'high_risk' ? 'active' : ''}`}
              onClick={() => setFilterType('high_risk')}
            >
              Risk Factors
            </button>
            <button 
              className={`filter-pill ${filterType === 'uncertainty' ? 'active' : ''}`}
              onClick={() => setFilterType('uncertainty')}
            >
              Uncertainty
            </button>
          </div>

          <div className="simulated-pill" style={{ fontSize: '0.72rem' }}>
            <Database size={12} />
            <span>SQLite Grounded</span>
          </div>
        </div>
      </div>

      {filteredInsights.length === 0 ? (
        <EmptyState
          icon={CheckCircle2}
          title="All Telemetry Operating Normally"
          description="No anomalies or cascading disruptions detected in the digital twin baseline. All services verified stable."
          actionLabel="Run Resilience Drill"
          onAction={() => onNavigateModule && onNavigateModule('what-if-simulation')}
        />
      ) : (
        <div className="insights-list">
          {filteredInsights.map(ins => {
            const targetMod = getModuleTarget(ins.source_module);

            return (
              <div key={ins.id} className="insight-card">
                <div className="insight-header">
                  <div className="insight-title">
                    <AlertCircle size={16} color="#38bdf8" />
                    <span>{ins.title}</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span className="insight-module-badge">{ins.source_module}</span>
                    <button 
                      className="btn-insight-nav"
                      onClick={() => onNavigateModule && onNavigateModule(targetMod)}
                      title={`Open in ${targetMod}`}
                    >
                      <ArrowRight size={13} />
                    </button>
                  </div>
                </div>

                <div className="insight-summary">{ins.summary}</div>

                {/* Evidence & Metrics */}
                <div className="insight-evidence-grid">
                  <div>
                    <strong style={{ color: '#94a3b8' }}>Evidence Link: </strong>
                    <span style={{ color: '#f1f5f9' }}>
                      {ins.evidence_ids && ins.evidence_ids.length > 0 
                        ? ins.evidence_ids.map(id => id.length > 10 ? id.substring(0, 10) + '...' : id).join(', ')
                        : 'Statistical baseline match'}
                    </span>
                  </div>
                  <div>
                    <strong style={{ color: '#94a3b8' }}>Service / Target: </strong>
                    <span style={{ color: '#38bdf8', fontWeight: 600 }}>{ins.service_id || 'Global Topology'}</span>
                  </div>
                </div>

                {/* Risk Factors */}
                {ins.risk_factors && ins.risk_factors.length > 0 && (
                  <div className="insight-risk-factors">
                    {ins.risk_factors.map((rf, idx) => (
                      <span key={idx} className="risk-pill">{rf}</span>
                    ))}
                  </div>
                )}

                {/* Explicit Uncertainty Note */}
                {ins.uncertainty_notes && (
                  <div className="insight-uncertainty">
                    <strong>⚠️ Grounded Uncertainty & Causal Bounds: </strong>
                    {ins.uncertainty_notes}
                  </div>
                )}

                {/* Alternative Hypotheses */}
                {ins.alternative_explanations && ins.alternative_explanations.length > 0 && (
                  <div style={{ fontSize: '0.78rem', color: '#94a3b8' }}>
                    <strong>Alternative Hypothesis: </strong>
                    {ins.alternative_explanations.join(' • ')}
                  </div>
                )}

                {/* Recommended Next Step with direct action */}
                {ins.recommended_next_step && (
                  <div className="insight-next-step" onClick={() => onNavigateModule && onNavigateModule(targetMod)}>
                    <span>{ins.recommended_next_step}</span>
                    <ArrowRight size={13} style={{ marginLeft: 'auto' }} />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
