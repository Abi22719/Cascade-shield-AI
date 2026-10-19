import React, { useState, useEffect } from 'react';
import { X, Award, CheckCircle2 } from 'lucide-react';
import { rcaApi } from '../../services/rcaApi';

export default function RCAEvaluationModal({ onClose }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchEval() {
      try {
        setLoading(true);
        const res = await rcaApi.getEvaluation();
        setData(res);
      } catch (err) {
        setError(err.message || 'Failed to load evaluation.');
      } finally {
        setLoading(false);
      }
    }
    fetchEval();
  }, []);

  return (
    <div className="cascade-modal-overlay" onClick={onClose}>
      <div className="cascade-modal-content" style={{ maxWidth: '900px' }} onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Award size={18} color="#8b5cf6" />
            <div>
              <h3>RCA Algorithm Ground-Truth Benchmark Evaluation</h3>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Comparison of 3 Root Cause Analysis algorithms across 5 synthetic incident archetypes
              </span>
            </div>
          </div>
          <button className="modal-close-btn" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <div className="modal-body">
          {loading ? (
            <div style={{ textAlign: 'center', padding: '30px', color: 'var(--text-muted)' }}>
              Executing multi-incident benchmark evaluation across synthetic ground truth...
            </div>
          ) : error ? (
            <div style={{ color: '#ef4444', padding: '20px' }}>{error}</div>
          ) : data ? (
            <>
              <div style={{ background: 'rgba(139, 92, 246, 0.1)', border: '1px solid rgba(139, 92, 246, 0.3)', padding: '12px 16px', borderRadius: 'var(--radius-sm)', fontSize: '0.8rem', color: 'var(--text-main)', lineHeight: 1.4 }}>
                <b style={{ color: '#c4b5fd' }}>Methodology & Ground-Truth Archetypes: </b>
                {data.methodology_notes}
              </div>

              <div style={{ overflowX: 'auto', marginTop: '10px' }}>
                <table className="cascade-table">
                  <thead>
                    <tr>
                      <th>Metric</th>
                      <th>Earliest-Anomaly Baseline</th>
                      <th>Dependency-Only Baseline</th>
                      <th style={{ background: 'rgba(139, 92, 246, 0.2)', color: '#c4b5fd' }}>
                        Evidence-Grounded RCA (Module 4)
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td style={{ fontWeight: 600 }}>Top-1 Accuracy</td>
                      <td>{(data.baseline_earliest_anomaly.top_1_accuracy * 100).toFixed(1)}%</td>
                      <td>{(data.baseline_dependency_only.top_1_accuracy * 100).toFixed(1)}%</td>
                      <td style={{ fontWeight: 700, color: '#34d399', background: 'rgba(16, 185, 129, 0.08)' }}>
                        {(data.evidence_grounded_rca.top_1_accuracy * 100).toFixed(1)}%
                      </td>
                    </tr>
                    <tr>
                      <td style={{ fontWeight: 600 }}>Top-3 Accuracy</td>
                      <td>{(data.baseline_earliest_anomaly.top_3_accuracy * 100).toFixed(1)}%</td>
                      <td>{(data.baseline_dependency_only.top_3_accuracy * 100).toFixed(1)}%</td>
                      <td style={{ fontWeight: 700, color: '#34d399', background: 'rgba(16, 185, 129, 0.08)' }}>
                        {(data.evidence_grounded_rca.top_3_accuracy * 100).toFixed(1)}%
                      </td>
                    </tr>
                    <tr>
                      <td style={{ fontWeight: 600 }}>Mean Reciprocal Rank (MRR)</td>
                      <td>{data.baseline_earliest_anomaly.mrr_score.toFixed(3)}</td>
                      <td>{data.baseline_dependency_only.mrr_score.toFixed(3)}</td>
                      <td style={{ fontWeight: 700, color: '#60a5fa', background: 'rgba(59, 130, 246, 0.1)' }}>
                        {data.evidence_grounded_rca.mrr_score.toFixed(3)}
                      </td>
                    </tr>
                    <tr>
                      <td style={{ fontWeight: 600 }}>Precision</td>
                      <td>{(data.baseline_earliest_anomaly.precision * 100).toFixed(1)}%</td>
                      <td>{(data.baseline_dependency_only.precision * 100).toFixed(1)}%</td>
                      <td style={{ fontWeight: 700, color: '#34d399', background: 'rgba(16, 185, 129, 0.08)' }}>
                        {(data.evidence_grounded_rca.precision * 100).toFixed(1)}%
                      </td>
                    </tr>
                    <tr>
                      <td style={{ fontWeight: 600 }}>Recall</td>
                      <td>{(data.baseline_earliest_anomaly.recall * 100).toFixed(1)}%</td>
                      <td>{(data.baseline_dependency_only.recall * 100).toFixed(1)}%</td>
                      <td style={{ fontWeight: 700, color: '#34d399', background: 'rgba(16, 185, 129, 0.08)' }}>
                        {(data.evidence_grounded_rca.recall * 100).toFixed(1)}%
                      </td>
                    </tr>
                    <tr>
                      <td style={{ fontWeight: 600 }}>Insufficient Evidence Handling</td>
                      <td style={{ color: '#f87171' }}>0.0% (Always Hallucinates)</td>
                      <td style={{ color: '#f87171' }}>0.0% (Always Hallucinates)</td>
                      <td style={{ fontWeight: 700, color: '#34d399', background: 'rgba(16, 185, 129, 0.08)' }}>
                        {(data.evidence_grounded_rca.insufficient_evidence_rate * 100).toFixed(1)}%
                      </td>
                    </tr>
                    <tr>
                      <td style={{ fontWeight: 600 }}>Avg Runtime (ms)</td>
                      <td>{data.baseline_earliest_anomaly.avg_runtime_ms} ms</td>
                      <td>{data.baseline_dependency_only.avg_runtime_ms} ms</td>
                      <td style={{ background: 'rgba(139, 92, 246, 0.08)' }}>{data.evidence_grounded_rca.avg_runtime_ms} ms</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <div style={{ background: 'var(--bg-hover)', padding: '12px 16px', borderRadius: 'var(--radius-sm)', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                <b style={{ color: 'var(--text-main)' }}>Key Finding: </b>
                {data.summary_findings}
              </div>
            </>
          ) : null}
        </div>
      </div>
    </div>
  );
}
