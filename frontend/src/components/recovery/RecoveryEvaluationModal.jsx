import React, { useState, useEffect } from 'react';
import { X, BarChart3, Info, CheckCircle2 } from 'lucide-react';
import { recoveryApi } from '../../services/recoveryApi';

export default function RecoveryEvaluationModal({ isOpen, onClose }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!isOpen) return;

    async function fetchEvaluation() {
      setLoading(true);
      setError(null);
      try {
        const res = await recoveryApi.getEvaluation();
        setData(res);
      } catch (err) {
        setError(err.message || 'Failed to load recovery evaluation');
      } finally {
        setLoading(false);
      }
    }

    fetchEvaluation();
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="sim-modal-overlay">
      <div className="sim-modal-card" style={{ maxWidth: '950px' }}>
        <div className="sim-modal-header">
          <h3>
            <BarChart3 size={18} color="#10b981" />
            <span>Recovery Strategy Benchmark Evaluation</span>
          </h3>
          <button className="btn-rec-secondary" style={{ padding: '0.25rem 0.5rem' }} onClick={onClose}>
            <X size={16} />
          </button>
        </div>

        <div className="sim-modal-body">
          {loading && (
            <div style={{ textAlign: 'center', padding: '2rem', color: '#94a3b8' }}>
              Computing standardized empirical benchmarks across failure archetypes...
            </div>
          )}

          {error && (
            <div style={{ color: '#f87171', padding: '1rem', background: 'rgba(239, 68, 68, 0.1)', borderRadius: '6px' }}>
              {error}
            </div>
          )}

          {data && !loading && (
            <>
              <p style={{ fontSize: '0.82rem', color: '#94a3b8', margin: 0 }}>
                Rigorous empirical comparison across <b>{data.benchmark_scenarios_count} standardized cloud incident archetypes</b>:
              </p>

              <div className="sim-table-container">
                <table className="sim-table">
                  <thead>
                    <tr>
                      <th>Strategy</th>
                      <th>Success Rate</th>
                      <th>Mean Time</th>
                      <th>Max Risk</th>
                      <th>Avg Risk</th>
                      <th>Added Failures</th>
                      <th>Cost Units</th>
                      <th>Failed Steps</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.strategies.map((strat, idx) => {
                      const isBalanced = strat.strategy_name.includes('Balanced');

                      return (
                        <tr
                          key={idx}
                          style={{
                            backgroundColor: isBalanced ? 'rgba(16, 185, 129, 0.12)' : undefined
                          }}
                        >
                          <td style={{ fontWeight: isBalanced ? 700 : 500, color: isBalanced ? '#6ee7b7' : '#f8fafc' }}>
                            {strat.strategy_name}
                          </td>
                          <td style={{ fontWeight: isBalanced ? 700 : 500, color: strat.success_rate >= 90 ? '#34d399' : '#cbd5e1' }}>
                            {strat.success_rate.toFixed(1)}%
                          </td>
                          <td>{strat.mean_recovery_time.toFixed(1)} steps</td>
                          <td style={{ color: strat.max_risk > 60 ? '#f87171' : '#cbd5e1' }}>
                            {strat.max_risk.toFixed(1)}/100
                          </td>
                          <td>{strat.avg_risk.toFixed(1)}/100</td>
                          <td style={{ color: strat.additional_failures_count > 0 ? '#f87171' : '#34d399' }}>
                            {strat.additional_failures_count}
                          </td>
                          <td>{strat.avg_resource_cost.toFixed(1)}</td>
                          <td style={{ color: strat.failed_steps_count > 0 ? '#f87171' : '#34d399' }}>
                            {strat.failed_steps_count}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>

              {/* Methodology & Findings */}
              <div style={{
                background: 'rgba(30, 41, 59, 0.5)',
                border: '1px solid rgba(255, 255, 255, 0.08)',
                borderRadius: '6px',
                padding: '0.85rem 1rem',
                fontSize: '0.82rem',
                color: '#cbd5e1',
                lineHeight: 1.4
              }}>
                <div style={{ fontWeight: 600, color: '#f8fafc', marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                  <Info size={14} color="#0ea5e9" />
                  <span>Key Benchmark Findings</span>
                </div>
                {data.summary_findings}
              </div>
            </>
          )}
        </div>

        <div className="sim-modal-footer">
          <button className="btn-rec-secondary" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
