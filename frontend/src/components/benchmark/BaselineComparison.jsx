import React, { useState } from 'react';

export default function BaselineComparison({ comparisons }) {
  const [selectedCompIndex, setSelectedCompIndex] = useState(0);

  if (!comparisons || comparisons.length === 0) {
    return (
      <div className="bm-card">
        <div className="bm-card-header">
          <h3><span>⚖️</span> Baseline vs Candidate Method Comparisons</h3>
        </div>
        <p style={{ color: '#94a3b8', fontSize: '0.85rem' }}>
          No comparisons recorded. Run a benchmark experiment to evaluate candidate algorithms against standard baselines.
        </p>
      </div>
    );
  }

  const activeComp = comparisons[selectedCompIndex] || comparisons[0];
  const metrics = activeComp?.comparison_metrics || {};

  return (
    <div className="bm-card">
      <div className="bm-card-header">
        <h3><span>⚖️</span> Side-by-Side Method Evaluation</h3>
        <select
          className="bm-select"
          style={{ maxWidth: '380px' }}
          value={selectedCompIndex}
          onChange={(e) => setSelectedCompIndex(Number(e.target.value))}
        >
          {comparisons.map((c, idx) => (
            <option key={idx} value={idx}>
              {c.candidate_name} vs {c.baseline_name}
            </option>
          ))}
        </select>
      </div>

      {activeComp && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ background: 'rgba(99, 102, 241, 0.08)', border: '1px solid rgba(99, 102, 241, 0.2)', padding: '0.85rem 1rem', borderRadius: '6px' }}>
            <div style={{ fontSize: '0.78rem', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 600 }}>
              Comparative Interpretation
            </div>
            <div style={{ fontSize: '0.9rem', color: '#e2e8f0', marginTop: '0.25rem' }}>
              {activeComp.interpretation}
            </div>
          </div>

          <div className="bm-table-wrapper">
            <table className="bm-table">
              <thead>
                <tr>
                  <th>Evaluated Metric</th>
                  <th>Baseline ({activeComp.baseline_name})</th>
                  <th>Candidate ({activeComp.candidate_name})</th>
                  <th>Relative Improvement (%)</th>
                  <th>Verdict</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(metrics).map(([metricKey, data]) => {
                  const isImprovement = data.is_improvement;
                  const pct = data.percentage_diff ?? data.percent_change ?? 0;
                  const sign = pct > 0 ? '+' : '';

                  return (
                    <tr key={metricKey}>
                      <td style={{ fontWeight: 600, color: '#f8fafc' }}>{metricKey}</td>
                      <td>
                        <span className="badge-baseline">{data.baseline}</span>
                      </td>
                      <td>
                        <span className="badge-candidate">{data.candidate}</span>
                      </td>
                      <td>
                        <span style={{ fontWeight: 700, color: isImprovement ? '#4ade80' : '#f87171' }}>
                          {sign}{pct}%
                        </span>
                      </td>
                      <td>
                        {isImprovement ? (
                          <span className="badge-win">✅ Outperformed</span>
                        ) : (
                          <span className="badge-loss">➖ Equivalent</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
