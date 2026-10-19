import React from 'react';

export default function BenchmarkOverview({ summary, latestExperiment, onLaunchClick }) {
  const avgScore = summary?.average_resilience_score ?? 0;
  const scoreBreakdown = latestExperiment?.summary?.score_breakdown || {};
  const overallScore = latestExperiment?.overall_resilience_score ?? null;

  const getScoreClass = (score) => {
    if (score >= 85) return 'bm-score-high';
    if (score >= 65) return 'bm-score-medium';
    return 'bm-score-low';
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Stat Cards */}
      <div className="bm-stats-grid">
        <div className="bm-stat-card">
          <div className="bm-stat-icon">🛡️</div>
          <div className="bm-stat-content">
            <h4>Avg Resilience Score</h4>
            <div className={`bm-stat-number ${avgScore >= 80 ? 'text-emerald-400' : 'text-amber-400'}`}>
              {avgScore.toFixed(1)} <span style={{ fontSize: '0.85rem', color: '#94a3b8' }}>/ 100</span>
            </div>
            <div className="bm-stat-sub">Across historical benchmark runs</div>
          </div>
        </div>

        <div className="bm-stat-card">
          <div className="bm-stat-icon">🧪</div>
          <div className="bm-stat-content">
            <h4>Total Experiments</h4>
            <div className="bm-stat-number">{summary?.total_experiments ?? 0}</div>
            <div className="bm-stat-sub">{summary?.completed_experiments ?? 0} completed successfully</div>
          </div>
        </div>

        <div className="bm-stat-card">
          <div className="bm-stat-icon">📑</div>
          <div className="bm-stat-content">
            <h4>Evaluated Modules</h4>
            <div className="bm-stat-number">{summary?.evaluated_modules_count ?? 7}</div>
            <div className="bm-stat-sub">Modules 2 through 8 + End-to-End</div>
          </div>
        </div>

        <div className="bm-stat-card">
          <div className="bm-stat-icon">📁</div>
          <div className="bm-stat-content">
            <h4>Benchmark Datasets</h4>
            <div className="bm-stat-number">{summary?.available_datasets ?? 1}</div>
            <div className="bm-stat-sub">10 Standard Failure Archetypes</div>
          </div>
        </div>
      </div>

      {/* Latest Run Highlights */}
      <div className="bm-card">
        <div className="bm-card-header">
          <h3>
            <span>🏆</span> Latest Benchmark Evaluation:{' '}
            <span style={{ color: '#a5b4fc', fontWeight: 600 }}>
              {latestExperiment?.name || 'No experiment run yet'}
            </span>
          </h3>
          {overallScore !== null && (
            <div className={`bm-score-badge ${getScoreClass(overallScore)}`}>
              Resilience Score: {overallScore.toFixed(1)} / 100.0
            </div>
          )}
        </div>

        {latestExperiment ? (
          <div>
            <p style={{ fontSize: '0.85rem', color: '#94a3b8', margin: '0 0 1rem 0' }}>
              Execution completed at {latestExperiment.completed_at ? new Date(latestExperiment.completed_at).toLocaleString() : 'N/A'}. 
              Evaluated across 10 reproducible failure scenarios in an isolated simulated sandbox.
            </p>

            <h4 style={{ fontSize: '0.9rem', color: '#f1f5f9', margin: '0 0 0.5rem 0' }}>
              Resilience Pillar Score Breakdown:
            </h4>
            <div className="bm-table-wrapper">
              <table className="bm-table">
                <thead>
                  <tr>
                    <th>Resilience Pillar</th>
                    <th>Module</th>
                    <th>Pillar Weight</th>
                    <th>Raw Performance</th>
                    <th>Weighted Score</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(scoreBreakdown).map(([pillar, info]) => (
                    <tr key={pillar}>
                      <td style={{ fontWeight: 600, color: '#f8fafc', textTransform: 'capitalize' }}>
                        {pillar}
                      </td>
                      <td>
                        {pillar === 'detection' && 'Module 2: Anomaly Detection'}
                        {pillar === 'prediction' && 'Module 3: Cascading Failure'}
                        {pillar === 'rca' && 'Module 4: Root Cause Analysis'}
                        {pillar === 'diagnostic' && 'Module 5: Diagnostic Agent'}
                        {pillar === 'simulation' && 'Module 6: What-If Simulation'}
                        {pillar === 'recovery' && 'Module 7: Recovery Planning'}
                        {pillar === 'validation' && 'Module 8: Recovery Validation'}
                      </td>
                      <td>{(info.weight * 100).toFixed(0)}%</td>
                      <td>
                        <span style={{ fontWeight: 600, color: info.raw_score >= 80 ? '#4ade80' : '#fbbf24' }}>
                          {info.raw_score.toFixed(1)}%
                        </span>
                      </td>
                      <td style={{ fontWeight: 600, color: '#a5b4fc' }}>
                        {info.weighted_score.toFixed(2)} pts
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '2rem 1rem' }}>
            <p style={{ color: '#94a3b8', marginBottom: '1rem' }}>
              No resilience benchmark experiments have been executed yet.
            </p>
            <button className="btn-bm-primary" onClick={onLaunchClick} style={{ margin: '0 auto' }}>
              🚀 Launch Standard 10-Scenario Resilience Benchmark
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
