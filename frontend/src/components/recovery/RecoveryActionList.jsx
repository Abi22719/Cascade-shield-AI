import React from 'react';
import { CheckCircle2, Clock, AlertCircle, RotateCcw, ShieldCheck, ChevronRight } from 'lucide-react';

export default function RecoveryActionList({ actions = [] }) {
  if (!actions || actions.length === 0) {
    return (
      <div style={{ textAlign: 'center', color: '#64748b', padding: '2rem 1rem', fontSize: '0.85rem' }}>
        No recovery actions configured in this plan.
      </div>
    );
  }

  const sortedActions = [...actions].sort((a, b) => a.action_order - b.action_order);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
      {sortedActions.map((act, idx) => {
        const preconditions = act.preconditions || [];
        const reversibilityClass = act.reversibility || 'fully_reversible';

        return (
          <div key={idx} className="action-card">
            <div className="action-card-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                <div className="action-order-badge">{act.action_order}</div>
                <div style={{ fontWeight: 700, color: '#f8fafc', fontSize: '0.9rem' }}>
                  {act.action_type.replace('_', ' ').toUpperCase()}
                </div>
                {act.target_service_id && (
                  <span style={{ fontSize: '0.75rem', color: '#6ee7b7', background: 'rgba(16, 185, 129, 0.1)', padding: '0.15rem 0.45rem', borderRadius: '4px' }}>
                    {act.target_service_id}
                  </span>
                )}
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span className={`reversibility-badge ${reversibilityClass}`}>
                  {reversibilityClass.replace('_', ' ')}
                </span>
                <span style={{ fontSize: '0.75rem', color: '#94a3b8', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                  <Clock size={12} />
                  <span>{act.estimated_duration} step{act.estimated_duration > 1 ? 's' : ''}</span>
                </span>
              </div>
            </div>

            {/* Expected Result */}
            {act.expected_result && (
              <div style={{ fontSize: '0.82rem', color: '#cbd5e1', lineHeight: 1.4 }}>
                {act.expected_result}
              </div>
            )}

            {/* Preconditions Checklist */}
            {preconditions.length > 0 && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.3rem', background: 'rgba(15, 23, 42, 0.4)', padding: '0.5rem 0.75rem', borderRadius: '5px' }}>
                <div style={{ fontSize: '0.72rem', fontWeight: 600, color: '#94a3b8', textTransform: 'uppercase' }}>
                  Execution Preconditions:
                </div>
                {preconditions.map((p, pIdx) => {
                  const isSatisfied = p.status === 'satisfied';
                  const isViolated = p.status === 'violated';

                  return (
                    <div key={pIdx} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.75rem' }}>
                      <span style={{ color: '#e2e8f0' }}>• {p.name}: {p.description}</span>
                      <span style={{
                        color: isSatisfied ? '#34d399' : (isViolated ? '#f87171' : '#fbbf24'),
                        fontWeight: 600,
                        fontSize: '0.7rem'
                      }}>
                        [{p.status || 'satisfied'}]
                      </span>
                    </div>
                  );
                })}
              </div>
            )}

            {/* Rollback Procedure */}
            {act.rollback_procedure && (
              <div style={{ fontSize: '0.75rem', color: '#94a3b8', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                <RotateCcw size={12} color="#f59e0b" />
                <span>Rollback Contingency: <i style={{ color: '#cbd5e1' }}>{act.rollback_procedure}</i></span>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
