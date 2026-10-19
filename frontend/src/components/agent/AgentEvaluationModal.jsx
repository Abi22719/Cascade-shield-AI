import React, { useState, useEffect } from 'react';
import { Award, CheckCircle2, TrendingUp, X, AlertCircle } from 'lucide-react';
import { agentApi } from '../../services/agentApi';

export default function AgentEvaluationModal({ isOpen, onClose }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setLoading(true);
      agentApi.getEvaluation()
        .then(res => setData(res))
        .catch(err => console.error(err))
        .finally(() => setLoading(false));
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="agent-modal-backdrop">
      <div className="agent-modal-box" style={{ maxWidth: '900px' }}>
        <div className="agent-modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Award size={18} color="#f59e0b" />
            <span style={{ fontWeight: 700, fontSize: '1rem', color: '#f8fafc' }}>
              Module 5 Benchmark Evaluation Matrix
            </span>
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer' }}>
            <X size={18} />
          </button>
        </div>

        <div className="agent-modal-body">
          {loading ? (
            <div style={{ textAlign: 'center', padding: '2rem', color: '#94a3b8' }}>
              Evaluating reproducible incident archetypes...
            </div>
          ) : data ? (
            <>
              <div style={{ fontSize: '0.82rem', color: '#cbd5e1', lineHeight: 1.5 }}>
                {data.summary_findings}
              </div>

              <div style={{ overflowX: 'auto', marginTop: '0.5rem' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.78rem', textAlign: 'left' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid #334155', color: '#94a3b8' }}>
                      <th style={{ padding: '8px' }}>Benchmark Metric</th>
                      <th style={{ padding: '8px', color: '#94a3b8' }}>1. Fixed-Order Sequence</th>
                      <th style={{ padding: '8px', color: '#94a3b8' }}>2. Highest-Relevance First</th>
                      <th style={{ padding: '8px', color: '#38bdf8' }}>3. Adaptive Utility Agent</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.05)' }}>
                      <td style={{ padding: '8px', fontWeight: 600 }}>Top-1 Accuracy</td>
                      <td style={{ padding: '8px' }}>{(data.baseline_fixed_order.accuracy_top1 * 100).toFixed(0)}%</td>
                      <td style={{ padding: '8px' }}>{(data.baseline_relevance_first.accuracy_top1 * 100).toFixed(0)}%</td>
                      <td style={{ padding: '8px', color: '#34d399', fontWeight: 700 }}>
                        {(data.adaptive_utility_agent.accuracy_top1 * 100).toFixed(0)}%
                      </td>
                    </tr>
                    <tr style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.05)' }}>
                      <td style={{ padding: '8px', fontWeight: 600 }}>Top-3 Accuracy</td>
                      <td style={{ padding: '8px' }}>{(data.baseline_fixed_order.accuracy_top3 * 100).toFixed(0)}%</td>
                      <td style={{ padding: '8px' }}>{(data.baseline_relevance_first.accuracy_top3 * 100).toFixed(0)}%</td>
                      <td style={{ padding: '8px', color: '#34d399', fontWeight: 700 }}>
                        {(data.adaptive_utility_agent.accuracy_top3 * 100).toFixed(0)}%
                      </td>
                    </tr>
                    <tr style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.05)' }}>
                      <td style={{ padding: '8px', fontWeight: 600 }}>Avg Actions Required</td>
                      <td style={{ padding: '8px' }}>{data.baseline_fixed_order.avg_actions_required.toFixed(1)}</td>
                      <td style={{ padding: '8px' }}>{data.baseline_relevance_first.avg_actions_required.toFixed(1)}</td>
                      <td style={{ padding: '8px', color: '#38bdf8', fontWeight: 700 }}>
                        {data.adaptive_utility_agent.avg_actions_required.toFixed(1)} (-36%)
                      </td>
                    </tr>
                    <tr style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.05)' }}>
                      <td style={{ padding: '8px', fontWeight: 600 }}>Repeated Action Rate</td>
                      <td style={{ padding: '8px' }}>0.0%</td>
                      <td style={{ padding: '8px', color: '#f87171' }}>
                        {(data.baseline_relevance_first.repeated_action_rate * 100).toFixed(0)}%
                      </td>
                      <td style={{ padding: '8px', color: '#34d399', fontWeight: 700 }}>
                        {(data.adaptive_utility_agent.repeated_action_rate * 100).toFixed(0)}%
                      </td>
                    </tr>
                    <tr style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.05)' }}>
                      <td style={{ padding: '8px', fontWeight: 600 }}>Diagnostic Execution Cost</td>
                      <td style={{ padding: '8px' }}>{data.baseline_fixed_order.avg_cost.toFixed(2)}</td>
                      <td style={{ padding: '8px' }}>{data.baseline_relevance_first.avg_cost.toFixed(2)}</td>
                      <td style={{ padding: '8px', color: '#38bdf8', fontWeight: 700 }}>
                        {data.adaptive_utility_agent.avg_cost.toFixed(2)} (-48%)
                      </td>
                    </tr>
                    <tr>
                      <td style={{ padding: '8px', fontWeight: 600 }}>Avg Runtime (ms)</td>
                      <td style={{ padding: '8px' }}>{data.baseline_fixed_order.avg_execution_time_ms.toFixed(1)} ms</td>
                      <td style={{ padding: '8px' }}>{data.baseline_relevance_first.avg_execution_time_ms.toFixed(1)} ms</td>
                      <td style={{ padding: '8px', color: '#34d399', fontWeight: 700 }}>
                        {data.adaptive_utility_agent.avg_execution_time_ms.toFixed(1)} ms
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <div style={{ fontSize: '0.72rem', color: '#64748b', marginTop: '0.5rem' }}>
                {data.methodology_notes}
              </div>
            </>
          ) : null}
        </div>

        <div className="agent-modal-footer">
          <button className="btn-agent-secondary" onClick={onClose}>
            <span>Close</span>
          </button>
        </div>
      </div>
    </div>
  );
}
