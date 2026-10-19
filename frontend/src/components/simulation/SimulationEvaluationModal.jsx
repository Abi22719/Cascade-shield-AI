import React, { useState, useEffect } from 'react';
import { X, BarChart3, CheckCircle, Info } from 'lucide-react';
import { simulationApi } from '../../services/simulationApi';

export default function SimulationEvaluationModal({ isOpen, onClose }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!isOpen) return;

    async function fetchEvaluation() {
      setLoading(true);
      setError(null);
      try {
        const res = await simulationApi.getEvaluation();
        setData(res);
      } catch (err) {
        setError(err.message || 'Failed to fetch benchmark evaluation');
      } finally {
        setLoading(false);
      }
    }

    fetchEvaluation();
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="sim-modal-overlay">
      <div className="sim-modal-card" style={{ maxWidth: '900px' }}>
        <div className="sim-modal-header">
          <h3>
            <BarChart3 size={18} color="#8b5cf6" />
            <span>Resilience Simulation Engine Benchmark Evaluation</span>
          </h3>
          <button className="btn-sim-secondary" style={{ padding: '0.25rem 0.5rem' }} onClick={onClose}>
            <X size={16} />
          </button>
        </div>

        <div className="sim-modal-body">
          {loading && (
            <div style={{ textAlign: 'center', padding: '2rem', color: '#94a3b8' }}>
              Computing empirical benchmark across standardized synthetic topologies...
            </div>
          )}

          {error && (
            <div style={{ color: '#f87171', padding: '1rem', background: 'rgba(239, 68, 68, 0.1)', borderRadius: '6px' }}>
              {error}
            </div>
          )}

          {data && !loading && (
            <>
              <p style={{ fontSize: '0.85rem', color: '#94a3b8', margin: 0 }}>
                Rigorous evaluation across <b>{data.benchmark_scenarios_count} standardized failure propagation scenarios</b> comparing
                static reachability, Module 3 cascade estimation, and the Module 6 multi-step discrete simulator:
              </p>

              {/* Benchmark Table */}
              <div className="sim-table-container">
                <table className="sim-table">
                  <thead>
                    <tr>
                      <th>Simulation Approach</th>
                      <th>Coverage Accuracy</th>
                      <th>State Transitions</th>
                      <th>Recovery Consistency</th>
                      <th>Reproducibility</th>
                      <th>Avg Latency</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td style={{ fontWeight: 600, color: '#f8fafc' }}>
                        {data.baseline_static_traversal.model_name}
                      </td>
                      <td>{(data.baseline_static_traversal.coverage_accuracy * 100).toFixed(1)}%</td>
                      <td>{(data.baseline_static_traversal.transition_consistency * 100).toFixed(1)}%</td>
                      <td>{(data.baseline_static_traversal.recovery_consistency * 100).toFixed(1)}%</td>
                      <td>{(data.baseline_static_traversal.reproducibility_rate * 100).toFixed(1)}%</td>
                      <td>{data.baseline_static_traversal.avg_runtime_ms.toFixed(2)} ms</td>
                    </tr>
                    <tr>
                      <td style={{ fontWeight: 600, color: '#f8fafc' }}>
                        {data.baseline_cascade_mod3.model_name}
                      </td>
                      <td>{(data.baseline_cascade_mod3.coverage_accuracy * 100).toFixed(1)}%</td>
                      <td>{(data.baseline_cascade_mod3.transition_consistency * 100).toFixed(1)}%</td>
                      <td>{(data.baseline_cascade_mod3.recovery_consistency * 100).toFixed(1)}%</td>
                      <td>{(data.baseline_cascade_mod3.reproducibility_rate * 100).toFixed(1)}%</td>
                      <td>{data.baseline_cascade_mod3.avg_runtime_ms.toFixed(2)} ms</td>
                    </tr>
                    <tr style={{ backgroundColor: 'rgba(139, 92, 246, 0.12)' }}>
                      <td style={{ fontWeight: 700, color: '#c4b5fd' }}>
                        {data.timestep_simulator_mod6.model_name}
                      </td>
                      <td style={{ fontWeight: 700, color: '#34d399' }}>
                        {(data.timestep_simulator_mod6.coverage_accuracy * 100).toFixed(1)}%
                      </td>
                      <td style={{ fontWeight: 700, color: '#34d399' }}>
                        {(data.timestep_simulator_mod6.transition_consistency * 100).toFixed(1)}%
                      </td>
                      <td style={{ fontWeight: 700, color: '#34d399' }}>
                        {(data.timestep_simulator_mod6.recovery_consistency * 100).toFixed(1)}%
                      </td>
                      <td style={{ fontWeight: 700, color: '#34d399' }}>
                        {(data.timestep_simulator_mod6.reproducibility_rate * 100).toFixed(1)}%
                      </td>
                      <td style={{ fontWeight: 700, color: '#f8fafc' }}>
                        {data.timestep_simulator_mod6.avg_runtime_ms.toFixed(2)} ms
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              {/* Summary Notes */}
              <div style={{
                background: 'rgba(30, 41, 59, 0.5)',
                border: '1px solid rgba(255, 255, 255, 0.08)',
                borderRadius: '6px',
                padding: '0.85rem 1rem',
                fontSize: '0.82rem',
                color: '#cbd5e1',
                lineHeight: 1.45
              }}>
                <div style={{ fontWeight: 600, color: '#f8fafc', marginBottom: '0.3rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <Info size={15} color="#0ea5e9" />
                  <span>Key Empirical Findings</span>
                </div>
                {data.summary_findings}
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
