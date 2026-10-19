import React, { useState, useEffect } from 'react';
import { X, GitCompare, Award, CheckCircle2, AlertTriangle, ShieldCheck } from 'lucide-react';
import { simulationApi } from '../../services/simulationApi';

export default function ScenarioComparisonModal({
  isOpen,
  onClose,
  currentRunId,
  availableRuns = []
}) {
  const [selectedRunIds, setSelectedRunIds] = useState([]);
  const [comparisonResult, setComparisonResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Initialize selected runs
  useEffect(() => {
    if (isOpen) {
      const ids = [];
      if (currentRunId) ids.push(currentRunId);
      const others = availableRuns.filter(r => r.id !== currentRunId).slice(0, 2);
      others.forEach(r => ids.push(r.id));
      setSelectedRunIds(ids);
    }
  }, [isOpen, currentRunId, availableRuns]);

  // Execute comparison
  useEffect(() => {
    if (!isOpen || selectedRunIds.length === 0) return;

    async function fetchComparison() {
      setLoading(true);
      setError(null);
      try {
        const res = await simulationApi.compareRuns({ run_ids: selectedRunIds });
        setComparisonResult(res);
      } catch (err) {
        setError(err.message || 'Failed to compare scenario runs');
      } finally {
        setLoading(false);
      }
    }

    fetchComparison();
  }, [isOpen, selectedRunIds]);

  if (!isOpen) return null;

  const handleToggleRun = (runId) => {
    if (selectedRunIds.includes(runId)) {
      if (selectedRunIds.length > 1) {
        setSelectedRunIds(selectedRunIds.filter(id => id !== runId));
      }
    } else {
      if (selectedRunIds.length < 4) {
        setSelectedRunIds([...selectedRunIds, runId]);
      }
    }
  };

  return (
    <div className="sim-modal-overlay">
      <div className="sim-modal-card" style={{ maxWidth: '1050px' }}>
        <div className="sim-modal-header">
          <h3>
            <GitCompare size={18} color="#8b5cf6" />
            <span>Scenario Run Comparison Matrix</span>
          </h3>
          <button className="btn-sim-secondary" style={{ padding: '0.25rem 0.5rem' }} onClick={onClose}>
            <X size={16} />
          </button>
        </div>

        <div className="sim-modal-body">
          {/* Run Selectors */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
            <span className="sim-form-label">Select Runs to Compare (up to 4):</span>
            <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap' }}>
              {availableRuns.map(r => {
                const isSelected = selectedRunIds.includes(r.id);
                return (
                  <button
                    key={r.id}
                    className="btn-sim-secondary"
                    onClick={() => handleToggleRun(r.id)}
                    style={{
                      fontSize: '0.75rem',
                      padding: '0.3rem 0.6rem',
                      borderColor: isSelected ? '#8b5cf6' : undefined,
                      backgroundColor: isSelected ? 'rgba(139, 92, 246, 0.25)' : undefined,
                      color: isSelected ? '#c4b5fd' : undefined
                    }}
                  >
                    {r.scenario_name || r.id.substring(0, 10)} ({r.total_steps} steps)
                  </button>
                );
              })}
            </div>
          </div>

          {loading && (
            <div style={{ textAlign: 'center', padding: '2rem', color: '#94a3b8' }}>
              Calculating comparative impact and resilience metrics...
            </div>
          )}

          {error && (
            <div style={{ color: '#f87171', padding: '1rem', background: 'rgba(239, 68, 68, 0.1)', borderRadius: '6px' }}>
              {error}
            </div>
          )}

          {comparisonResult && !loading && (
            <>
              {/* AI Insights Alert */}
              <div style={{
                background: 'rgba(139, 92, 246, 0.12)',
                border: '1px solid rgba(139, 92, 246, 0.3)',
                borderRadius: '6px',
                padding: '0.85rem 1rem',
                fontSize: '0.82rem',
                color: '#e2e8f0',
                lineHeight: 1.4
              }}>
                <div style={{ fontWeight: 600, color: '#c4b5fd', marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <Award size={15} />
                  <span>Comparative Resilience Assessment</span>
                </div>
                {comparisonResult.summary_insights}
              </div>

              {/* Side-by-Side Comparison Cards */}
              <div className="comparison-grid">
                {comparisonResult.comparisons.map((c) => {
                  const isRecommended = comparisonResult.recommended_scenario === c.scenario_name;

                  return (
                    <div key={c.run_id} className={`comparison-card ${isRecommended ? 'recommended' : ''}`}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontWeight: 700, fontSize: '0.95rem', color: '#f8fafc' }}>
                          {c.scenario_name}
                        </span>
                        {isRecommended && (
                          <span style={{
                            fontSize: '0.68rem',
                            padding: '0.2rem 0.5rem',
                            background: 'rgba(16, 185, 129, 0.2)',
                            color: '#34d399',
                            border: '1px solid rgba(16, 185, 129, 0.4)',
                            borderRadius: '4px',
                            fontWeight: 700
                          }}>
                            Lowest Impact
                          </span>
                        )}
                      </div>

                      <div style={{ fontSize: '0.72rem', color: '#94a3b8' }}>
                        Initial: {c.initial_failures?.join(', ') || 'None'}
                      </div>

                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', marginTop: '0.5rem' }}>
                        <div className="comparison-metric-row">
                          <span>Total Impacted Services</span>
                          <span>{c.total_impacted_services}</span>
                        </div>
                        <div className="comparison-metric-row">
                          <span>Peak Simultaneous Blast</span>
                          <span>{c.peak_simultaneous_impact}</span>
                        </div>
                        <div className="comparison-metric-row">
                          <span>First Downstream Step</span>
                          <span>{c.time_to_first_impact_step !== null ? `Step ${c.time_to_first_impact_step}` : 'N/A'}</span>
                        </div>
                        <div className="comparison-metric-row">
                          <span>Recovery Step</span>
                          <span>{c.time_to_recovery_step !== null ? `Step ${c.time_to_recovery_step}` : 'None'}</span>
                        </div>
                        <div className="comparison-metric-row">
                          <span>Avg Risk Score</span>
                          <span>{c.avg_risk_score.toFixed(1)} / 100</span>
                        </div>
                        <div className="comparison-metric-row" style={{ borderBottom: 'none', paddingTop: '0.25rem' }}>
                          <span style={{ fontWeight: 700, color: '#c4b5fd' }}>Resilience Penalty</span>
                          <span style={{ fontWeight: 700, color: c.aggregate_impact_score > 50 ? '#f87171' : '#34d399' }}>
                            {c.aggregate_impact_score.toFixed(1)} / 100
                          </span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </>
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
