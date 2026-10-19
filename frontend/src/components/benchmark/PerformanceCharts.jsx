import React from 'react';

export default function PerformanceCharts({ results }) {
  if (!results || results.length === 0) {
    return (
      <div className="bm-card">
        <div className="bm-card-header">
          <h3><span>📊</span> Module Performance Analytics</h3>
        </div>
        <p style={{ color: '#94a3b8', fontSize: '0.85rem' }}>
          No granular metric results available. Run an experiment to view performance distributions.
        </p>
      </div>
    );
  }

  // Group results by module
  const grouped = results.reduce((acc, r) => {
    if (!acc[r.module_name]) acc[r.module_name] = [];
    acc[r.module_name].push(r);
    return acc;
  }, {});

  const moduleTitles = {
    module_2: 'Module 2: Anomaly Detection (Precision, Recall, F1, FPR, Delay)',
    module_3: 'Module 3: Cascade Failure Prediction (Recall, Precision, Runtime)',
    module_4: 'Module 4: Root Cause Analysis (Top-1, Top-3 Accuracy, MRR)',
    module_5: 'Module 5: Diagnostic Agent (Utility Ratio, Efficiency, Budget)',
    module_6: 'Module 6: What-If Simulation (Reproducibility, Propagation Steps)',
    module_7: 'Module 7: Recovery Planning (Success Rate, Risk Score, Cost)',
    module_8: 'Module 8: Recovery Validation (5-Pillar Verification Accuracy)'
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {Object.entries(grouped).map(([mod, items]) => {
        // Distinct metrics for candidate method
        const candidateItems = items.filter((i) => !i.method_name.includes('baseline') && !i.method_name.includes('rules'));
        const displayItems = candidateItems.length > 0 ? candidateItems.slice(0, 8) : items.slice(0, 8);

        return (
          <div key={mod} className="bm-card">
            <div className="bm-card-header">
              <h3><span>📈</span> {moduleTitles[mod] || mod}</h3>
              <span className="badge-candidate">Candidate: {displayItems[0]?.method_name}</span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '0.85rem' }}>
              {displayItems.map((item, idx) => (
                <div
                  key={idx}
                  style={{
                    background: 'rgba(255, 255, 255, 0.03)',
                    border: '1px solid rgba(255, 255, 255, 0.06)',
                    borderRadius: '6px',
                    padding: '0.75rem',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '0.25rem'
                  }}
                >
                  <div style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'capitalize' }}>
                    {item.metric_name.replace(/_/g, ' ')}
                  </div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#f8fafc' }}>
                    {typeof item.metric_value === 'number'
                      ? item.metric_unit === 'ratio' && item.metric_value <= 1.0
                        ? `${(item.metric_value * 100).toFixed(1)}%`
                        : `${item.metric_value} ${item.metric_unit}`
                      : item.metric_value}
                  </div>
                </div>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}
