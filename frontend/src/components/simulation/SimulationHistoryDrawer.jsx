import React from 'react';
import { X, History, PlayCircle, Clock } from 'lucide-react';

export default function SimulationHistoryDrawer({
  isOpen,
  onClose,
  runs = [],
  currentRunId,
  onSelectRun
}) {
  if (!isOpen) return null;

  return (
    <div className="sim-modal-overlay">
      <div className="sim-modal-card" style={{ maxWidth: '750px' }}>
        <div className="sim-modal-header">
          <h3>
            <History size={18} color="#8b5cf6" />
            <span>Simulation Execution History</span>
          </h3>
          <button className="btn-sim-secondary" style={{ padding: '0.25rem 0.5rem' }} onClick={onClose}>
            <X size={16} />
          </button>
        </div>

        <div className="sim-modal-body">
          {runs.length === 0 ? (
            <div style={{ textAlign: 'center', color: '#64748b', padding: '2rem' }}>
              No historical simulation runs found. Run a scenario to record execution runs.
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
              {runs.map((r) => {
                const isCurrent = r.id === currentRunId;
                const dateStr = r.started_at ? new Date(r.started_at).toLocaleString() : 'N/A';

                return (
                  <div
                    key={r.id}
                    style={{
                      background: isCurrent ? 'rgba(139, 92, 246, 0.15)' : 'rgba(30, 41, 59, 0.5)',
                      border: isCurrent ? '1px solid #8b5cf6' : '1px solid rgba(255, 255, 255, 0.08)',
                      borderRadius: '6px',
                      padding: '0.75rem 1rem',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      gap: '1rem'
                    }}
                  >
                    <div>
                      <div style={{ fontWeight: 600, color: '#f8fafc', fontSize: '0.85rem' }}>
                        {r.scenario_name || r.id}
                      </div>
                      <div style={{ fontSize: '0.72rem', color: '#94a3b8', display: 'flex', gap: '0.6rem', marginTop: '0.2rem' }}>
                        <span>Steps: {r.total_steps}</span>
                        <span>•</span>
                        <span>{dateStr}</span>
                        {r.random_seed !== undefined && r.random_seed !== null && (
                          <>
                            <span>•</span>
                            <span>Seed: {r.random_seed}</span>
                          </>
                        )}
                      </div>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                      <span className={`execution-status-pill ${(r.status || 'completed').toLowerCase()}`}>
                        {r.status || 'COMPLETED'}
                      </span>
                      <button
                        className="btn-sim-secondary"
                        onClick={() => {
                          onSelectRun(r.id);
                          onClose();
                        }}
                        disabled={isCurrent}
                        style={{ fontSize: '0.75rem', padding: '0.3rem 0.6rem' }}
                      >
                        <PlayCircle size={13} />
                        <span>{isCurrent ? 'Active' : 'Load'}</span>
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        <div className="sim-modal-footer">
          <button className="btn-sim-secondary" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
