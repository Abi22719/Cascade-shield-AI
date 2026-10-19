import React from 'react';
import { Play, Check, AlertCircle, Ban, Zap, Info, ShieldCheck } from 'lucide-react';

export default function DiagnosticActionList({ 
  recommendations = [], 
  selectedActionId, 
  onSelectAction, 
  onExecuteStep, 
  loading 
}) {
  const eligibleActions = recommendations.filter(r => r.eligible);
  const ineligibleActions = recommendations.filter(r => !r.eligible);

  return (
    <div className="agent-panel">
      <div className="panel-title">
        <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Zap size={16} color="#38bdf8" />
          <span>Eligible Diagnostic Actions Ranking</span>
        </span>
        <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
          {eligibleActions.length} eligible &bull; {ineligibleActions.length} ineligible
        </span>
      </div>

      <div className="action-ranking-list">
        {eligibleActions.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '1.5rem', color: '#64748b', fontSize: '0.85rem' }}>
            No eligible diagnostic actions remaining in current state.
          </div>
        ) : (
          eligibleActions.map((act, idx) => (
            <div 
              key={act.action_id}
              className={`action-item ${selectedActionId === act.action_id ? 'selected' : ''}`}
              onClick={() => onSelectAction && onSelectAction(act.action_id)}
              style={{ cursor: 'pointer' }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span 
                  style={{ 
                    width: '20px', 
                    height: '20px', 
                    borderRadius: '50%', 
                    background: idx === 0 ? '#0284c7' : '#1e293b', 
                    border: '1px solid #334155',
                    fontSize: '0.72rem', 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'center',
                    color: idx === 0 ? '#ffffff' : '#94a3b8',
                    fontWeight: 700 
                  }}
                >
                  {idx + 1}
                </span>
                <div className="action-info">
                  <div className="action-title" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span>{act.action_name}</span>
                    {idx === 0 && (
                      <span className="badge badge-info" style={{ fontSize: '0.65rem', padding: '1px 6px' }}>
                        Top Recommended
                      </span>
                    )}
                  </div>
                  <div className="action-desc">
                    Target: <code style={{ color: '#38bdf8' }}>{act.target_service_id || 'System'}</code> &bull; InfoGain: {(act.information_gain * 100).toFixed(0)}% &bull; Cost: {(act.cost * 100).toFixed(0)}%
                  </div>
                </div>
              </div>

              <div className="utility-badge">
                <span className="utility-score">{act.utility_score.toFixed(3)}</span>
                <span className="utility-label">Utility</span>
              </div>
            </div>
          ))
        )}

        {ineligibleActions.length > 0 && (
          <details style={{ marginTop: '0.5rem' }}>
            <summary style={{ fontSize: '0.78rem', color: '#64748b', cursor: 'pointer', outline: 'none' }}>
              View {ineligibleActions.length} Ineligible Actions
            </summary>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', marginTop: '0.4rem' }}>
              {ineligibleActions.map(act => (
                <div key={act.action_id} className="action-item ineligible">
                  <div className="action-info">
                    <div className="action-title" style={{ color: '#94a3b8' }}>{act.action_name}</div>
                    <div className="action-desc" style={{ color: '#f87171' }}>
                      Reason: {act.ineligibility_reason || 'Prerequisites unmet'}
                    </div>
                  </div>
                  <Ban size={15} color="#ef4444" />
                </div>
              ))}
            </div>
          </details>
        )}
      </div>
    </div>
  );
}
