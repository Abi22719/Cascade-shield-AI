import React from 'react';
import { 
  Sparkles, 
  HelpCircle, 
  ArrowRight, 
  AlertCircle, 
  CheckCircle2, 
  Database,
  Layers
} from 'lucide-react';

export default function ExplainabilityPanel({ insights = [], loading, onNavigateModule }) {
  if (loading) {
    return (
      <div className="db-panel">
        <div className="db-panel-header">
          <div className="db-panel-title">
            <Sparkles size={18} color="#38bdf8" />
            <span>Explainable AI Insights</span>
          </div>
        </div>
        <p style={{ color: '#94a3b8', fontSize: '0.86rem' }}>Synthesizing cross-module evidence...</p>
      </div>
    );
  }

  return (
    <div className="db-panel">
      <div className="db-panel-header">
        <div className="db-panel-title">
          <Sparkles size={18} color="#38bdf8" />
          <span>Explainable AI Insights</span>
        </div>
        <div className="simulated-pill" style={{ fontSize: '0.72rem' }}>
          <Database size={12} />
          <span>Grounded in SQLite Records</span>
        </div>
      </div>

      {insights.length === 0 ? (
        <p style={{ color: '#94a3b8', fontSize: '0.86rem' }}>
          No anomalies or active incidents detected. All services operating at simulated baseline.
        </p>
      ) : (
        <div className="insights-list">
          {insights.map(ins => (
            <div key={ins.id} className="insight-card">
              <div className="insight-header">
                <div className="insight-title">
                  <AlertCircle size={16} color="#38bdf8" />
                  <span>{ins.title}</span>
                </div>
                <span className="insight-module-badge">{ins.source_module}</span>
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
                  <span style={{ color: '#38bdf8' }}>{ins.service_id || 'Global Topology'}</span>
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
                  <strong>⚠️ AI Uncertainty & Assumptions: </strong>
                  {ins.uncertainty_notes}
                </div>
              )}

              {/* Alternative Hypotheses */}
              {ins.alternative_explanations && ins.alternative_explanations.length > 0 && (
                <div style={{ fontSize: '0.78rem', color: '#94a3b8' }}>
                  <strong>Alternative Possibility: </strong>
                  {ins.alternative_explanations.join(' • ')}
                </div>
              )}

              {/* Recommended Next Step */}
              {ins.recommended_next_step && (
                <div className="insight-next-step">
                  <span>{ins.recommended_next_step}</span>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
