import React, { useState } from 'react';

export default function BenchmarkHistory({ experiments, onSelectExperiment, onCompare, activeExperimentId }) {
  const [selectedIds, setSelectedIds] = useState([]);

  const toggleSelect = (id) => {
    if (selectedIds.includes(id)) {
      setSelectedIds(selectedIds.filter((x) => x !== id));
    } else {
      setSelectedIds([...selectedIds, id]);
    }
  };

  const handleCompareClick = () => {
    if (selectedIds.length < 2) {
      alert('Please select at least 2 experiments to compare.');
      return;
    }
    onCompare(selectedIds);
  };

  if (!experiments || experiments.length === 0) {
    return (
      <div className="bm-card">
        <div className="bm-card-header">
          <h3><span>📜</span> Experiment History</h3>
        </div>
        <p style={{ color: '#94a3b8', fontSize: '0.85rem' }}>No historical experiments found.</p>
      </div>
    );
  }

  return (
    <div className="bm-card">
      <div className="bm-card-header">
        <h3><span>📜</span> Experiment Execution History</h3>
        {selectedIds.length >= 2 && (
          <button className="btn-bm-primary" onClick={handleCompareClick}>
            ⚔️ Compare Selected ({selectedIds.length})
          </button>
        )}
      </div>

      <div className="bm-table-wrapper">
        <table className="bm-table">
          <thead>
            <tr>
              <th style={{ width: '40px' }}>Select</th>
              <th>Experiment Name</th>
              <th>Status</th>
              <th>Resilience Score</th>
              <th>Modules Tested</th>
              <th>Executed At</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {experiments.map((exp) => {
              const isCurrent = exp.id === activeExperimentId;
              const isChecked = selectedIds.includes(exp.id);
              const score = exp.overall_resilience_score;

              return (
                <tr
                  key={exp.id}
                  style={{
                    background: isCurrent ? 'rgba(99, 102, 241, 0.08)' : 'transparent'
                  }}
                >
                  <td>
                    <input
                      type="checkbox"
                      checked={isChecked}
                      onChange={() => toggleSelect(exp.id)}
                    />
                  </td>
                  <td style={{ fontWeight: 600, color: '#f8fafc' }}>
                    {exp.name}
                    {isCurrent && (
                      <span style={{ marginLeft: '0.5rem', fontSize: '0.7rem', color: '#6366f1' }}>
                        (Active)
                      </span>
                    )}
                  </td>
                  <td>
                    <span
                      style={{
                        padding: '0.15rem 0.45rem',
                        borderRadius: '4px',
                        fontSize: '0.72rem',
                        fontWeight: 600,
                        background:
                          exp.status === 'COMPLETED'
                            ? 'rgba(34, 197, 94, 0.15)'
                            : exp.status === 'RUNNING'
                            ? 'rgba(99, 102, 241, 0.15)'
                            : 'rgba(239, 68, 68, 0.15)',
                        color:
                          exp.status === 'COMPLETED'
                            ? '#4ade80'
                            : exp.status === 'RUNNING'
                            ? '#a5b4fc'
                            : '#f87171'
                      }}
                    >
                      {exp.status}
                    </span>
                  </td>
                  <td>
                    {score !== null ? (
                      <span
                        style={{
                          fontWeight: 700,
                          color: score >= 80 ? '#4ade80' : score >= 60 ? '#fbbf24' : '#f87171'
                        }}
                      >
                        {score.toFixed(1)} / 100
                      </span>
                    ) : (
                      <span style={{ color: '#64748b' }}>N/A</span>
                    )}
                  </td>
                  <td>{exp.selected_modules?.length || 0} modules</td>
                  <td style={{ color: '#94a3b8', fontSize: '0.75rem' }}>
                    {new Date(exp.created_at).toLocaleString()}
                  </td>
                  <td>
                    <button
                      className="btn-bm-secondary"
                      style={{ padding: '0.2rem 0.6rem', fontSize: '0.75rem' }}
                      onClick={() => onSelectExperiment(exp.id)}
                    >
                      View Run
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
