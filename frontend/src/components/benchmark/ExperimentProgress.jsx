import React from 'react';

export default function ExperimentProgress({ experiment, onCancel }) {
  if (!experiment) return null;

  const isRunning = experiment.status === 'RUNNING';
  const progress = experiment.progress || 0;

  return (
    <div className="bm-card" style={{ borderLeft: '4px solid #6366f1' }}>
      <div className="bm-card-header">
        <h3>
          <span>⚡</span> Experiment Execution: {experiment.name}
        </h3>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <span
            style={{
              padding: '0.25rem 0.65rem',
              borderRadius: '4px',
              fontSize: '0.78rem',
              fontWeight: 700,
              background:
                experiment.status === 'COMPLETED'
                  ? 'rgba(34, 197, 94, 0.2)'
                  : experiment.status === 'RUNNING'
                  ? 'rgba(99, 102, 241, 0.2)'
                  : 'rgba(239, 68, 68, 0.2)',
              color:
                experiment.status === 'COMPLETED'
                  ? '#4ade80'
                  : experiment.status === 'RUNNING'
                  ? '#a5b4fc'
                  : '#f87171'
            }}
          >
            {experiment.status}
          </span>
          {isRunning && (
            <button className="btn-bm-danger" onClick={onCancel}>
              🛑 Cancel Run
            </button>
          )}
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', color: '#94a3b8' }}>
          <span>Evaluation Progress</span>
          <span style={{ fontWeight: 600, color: '#f8fafc' }}>{progress.toFixed(1)}%</span>
        </div>
        <div className="bm-progress-container">
          <div className="bm-progress-fill" style={{ width: `${progress}%` }} />
        </div>
      </div>

      {experiment.overall_resilience_score !== null && (
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '0.5rem', background: 'rgba(255, 255, 255, 0.03)', padding: '0.75rem 1rem', borderRadiu: '6px' }}>
          <span style={{ fontSize: '0.85rem', color: '#94a3b8' }}>Overall Resilience Score:</span>
          <span style={{ fontSize: '1.2rem', fontWeight: 700, color: '#4ade80' }}>
            {experiment.overall_resilience_score.toFixed(1)} / 100.0
          </span>
        </div>
      )}
    </div>
  );
}
