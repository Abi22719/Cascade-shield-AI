import React from 'react';
import { X, GitCommit, ArrowRight, ShieldAlert, Info } from 'lucide-react';

export default function FailurePathsModal({
  service,
  onClose
}) {
  if (!service) return null;

  const paths = service.failure_paths || [];
  const evidence = service.contributing_evidence || [];

  return (
    <div className="cascade-modal-overlay" onClick={onClose}>
      <div className="cascade-modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <h3>Failure Propagation Paths & Evidence</h3>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Service: <b>{service.service_name}</b> ({service.service_id}) · Impact: <b>{service.impact_type}</b>
            </span>
          </div>
          <button className="modal-close-btn" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <div className="modal-body">
          {/* Key Metrics Overview */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '12px' }}>
            <div style={{ background: 'var(--bg-hover)', padding: '10px 14px', borderRadius: 'var(--radius-sm)' }}>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>HOP DISTANCE</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 700 }}>{service.hop_distance} hops</div>
            </div>
            <div style={{ background: 'var(--bg-hover)', padding: '10px 14px', borderRadius: 'var(--radius-sm)' }}>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>ESTIMATED RISK</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 700, color: service.estimated_risk_score >= 75 ? '#ef4444' : '#f97316' }}>
                {service.estimated_risk_score} pts ({service.risk_level})
              </div>
            </div>
            <div style={{ background: 'var(--bg-hover)', padding: '10px 14px', borderRadius: 'var(--radius-sm)' }}>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>PROPAGATION PROBABILITY</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 700 }}>
                {(service.propagation_probability_estimate * 100).toFixed(0)}%
              </div>
            </div>
          </div>

          {/* Contributing Evidence */}
          <div>
            <h4 style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
              <Info size={14} color="#3b82f6" /> Contributing Heuristic Evidence
            </h4>
            <ul style={{ paddingLeft: '18px', fontSize: '0.8rem', color: 'var(--text-muted)', display: 'flex', flexDirection: 'column', gap: '4px' }}>
              {evidence.length > 0 ? (
                evidence.map((ev, idx) => <li key={idx}>{ev}</li>)
              ) : (
                <li>Baseline propagation analysis across directed dependencies.</li>
              )}
            </ul>
          </div>

          {/* Propagation Paths List */}
          <div>
            <h4 style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
              <GitCommit size={14} color="#f97316" /> Distinct Upstream Propagation Paths ({paths.length})
            </h4>

            {paths.length === 0 ? (
              <div style={{ padding: '16px', background: 'var(--bg-hover)', borderRadius: 'var(--radius-sm)', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                {service.hop_distance === 0
                  ? 'This service is the Ground-Zero Root Failure origin.'
                  : 'Direct single-hop dependency linkage.'}
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {paths.map((p, idx) => (
                  <div key={idx} className="path-chain-card">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#f97316' }}>
                        Path #{idx + 1} ({p.hop_count} hop{p.hop_count > 1 ? 's' : ''})
                      </span>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        Contribution: <b>{p.risk_contribution} pts</b>
                      </span>
                    </div>

                    <div className="path-chain-sequence">
                      {p.path_names?.map((name, nIdx) => (
                        <React.Fragment key={nIdx}>
                          <span
                            className="path-node-pill"
                            style={{
                              borderColor: nIdx === 0 ? '#ef4444' : (nIdx === p.path_names.length - 1 ? '#f97316' : '#475569'),
                              color: nIdx === 0 ? '#fca5a5' : undefined
                            }}
                          >
                            {name}
                          </span>
                          {nIdx < p.path_names.length - 1 && (
                            <span style={{ display: 'flex', alignItems: 'center', gap: '2px', fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                              <ArrowRight size={12} color="#f97316" />
                              <span style={{ fontSize: '0.65rem', background: 'var(--bg-hover)', padding: '1px 4px', borderRadius: '4px' }}>
                                {p.dependency_types?.[nIdx] || 'sync'}
                              </span>
                            </span>
                          )}
                        </React.Fragment>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
