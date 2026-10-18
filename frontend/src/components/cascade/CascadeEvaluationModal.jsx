import React, { useState, useEffect } from 'react';
import { X, Award, BarChart2, CheckCircle2, AlertTriangle, ShieldCheck } from 'lucide-react';
import { cascadeApi } from '../../services/cascadeApi';

export default function CascadeEvaluationModal({ onClose }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadEvaluation() {
      try {
        setLoading(true);
        const res = await cascadeApi.getEvaluation();
        setData(res);
      } catch (err) {
        setError(err.message || 'Failed to execute benchmark evaluation.');
      } finally {
        setLoading(false);
      }
    }
    loadEvaluation();
  }, []);

  return (
    <div className="cascade-modal-overlay" onClick={onClose}>
      <div className="cascade-modal-content" style={{ maxWidth: '900px' }} onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Award size={20} color="#3b82f6" />
            <div>
              <h3>Cascade Engine Ground-Truth Benchmark Evaluation</h3>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Comparison of 3 algorithmic propagation techniques across 5 synthetic cloud architectures
              </span>
            </div>
          </div>
          <button className="modal-close-btn" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <div className="modal-body">
          {loading ? (
            <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>
              Executing multi-topology simulation benchmark across synthetic ground truth...
            </div>
          ) : error ? (
            <div style={{ padding: '20px', color: '#ef4444' }}>{error}</div>
          ) : data ? (
            <>
              {/* Methodology Header Callout */}
              <div style={{ background: 'rgba(59, 130, 246, 0.1)', border: '1px solid rgba(59, 130, 246, 0.3)', padding: '12px 16px', borderRadius: 'var(--radius-sm)', fontSize: '0.8rem', color: 'var(--text-main)', lineHeight: 1.4 }}>
                <div style={{ fontWeight: 600, color: '#60a5fa', marginBottom: '4px' }}>
                  Evaluation Methodology & Topology Archetypes:
                </div>
                {data.methodology_notes}
              </div>

              {/* Comparative Table */}
              <div style={{ overflowX: 'auto', marginTop: '10px' }}>
                <table className="cascade-table">
                  <thead>
                    <tr>
                      <th>Metric</th>
                      <th>Baseline Simple Traversal</th>
                      <th>Static Rule Scoring</th>
                      <th style={{ background: 'rgba(59, 130, 246, 0.25)', color: '#93c5fd' }}>
                        Evidence-Aware Cascade (Module 3)
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td style={{ fontWeight: 600 }}>Precision (P)</td>
                      <td>{(data.baseline_simple_traversal.precision * 100).toFixed(1)}%</td>
                      <td>{(data.static_rule_scoring.precision * 100).toFixed(1)}%</td>
                      <td style={{ fontWeight: 700, color: '#34d399', background: 'rgba(16, 185, 129, 0.08)' }}>
                        {(data.evidence_aware_cascade.precision * 100).toFixed(1)}%
                      </td>
                    </tr>
                    <tr>
                      <td style={{ fontWeight: 600 }}>Recall (R)</td>
                      <td>{(data.baseline_simple_traversal.recall * 100).toFixed(1)}%</td>
                      <td>{(data.static_rule_scoring.recall * 100).toFixed(1)}%</td>
                      <td style={{ fontWeight: 700, color: '#34d399', background: 'rgba(16, 185, 129, 0.08)' }}>
                        {(data.evidence_aware_cascade.recall * 100).toFixed(1)}%
                      </td>
                    </tr>
                    <tr>
                      <td style={{ fontWeight: 600 }}>F1-Score (Harmonic Mean)</td>
                      <td>{(data.baseline_simple_traversal.f1_score * 100).toFixed(1)}%</td>
                      <td>{(data.static_rule_scoring.f1_score * 100).toFixed(1)}%</td>
                      <td style={{ fontWeight: 700, color: '#60a5fa', background: 'rgba(59, 130, 246, 0.12)' }}>
                        {(data.evidence_aware_cascade.f1_score * 100).toFixed(1)}%
                      </td>
                    </tr>
                    <tr>
                      <td style={{ fontWeight: 600 }}>False Positive Rate (FPR)</td>
                      <td style={{ color: '#f87171' }}>{(data.baseline_simple_traversal.false_positive_rate * 100).toFixed(1)}%</td>
                      <td style={{ color: '#fb923c' }}>{(data.static_rule_scoring.false_positive_rate * 100).toFixed(1)}%</td>
                      <td style={{ fontWeight: 700, color: '#34d399', background: 'rgba(16, 185, 129, 0.08)' }}>
                        {(data.evidence_aware_cascade.false_positive_rate * 100).toFixed(1)}%
                      </td>
                    </tr>
                    <tr>
                      <td style={{ fontWeight: 600 }}>Detection Coverage %</td>
                      <td>{data.baseline_simple_traversal.impacted_detection_coverage_pct.toFixed(1)}%</td>
                      <td>{data.static_rule_scoring.impacted_detection_coverage_pct.toFixed(1)}%</td>
                      <td style={{ fontWeight: 700, color: '#34d399', background: 'rgba(16, 185, 129, 0.08)' }}>
                        {data.evidence_aware_cascade.impacted_detection_coverage_pct.toFixed(1)}%
                      </td>
                    </tr>
                    <tr>
                      <td style={{ fontWeight: 600 }}>Confusion Matrix (TP / FP / TN / FN)</td>
                      <td>{data.baseline_simple_traversal.true_positives} / {data.baseline_simple_traversal.false_positives} / {data.baseline_simple_traversal.true_negatives} / {data.baseline_simple_traversal.false_negatives}</td>
                      <td>{data.static_rule_scoring.true_positives} / {data.static_rule_scoring.false_positives} / {data.static_rule_scoring.true_negatives} / {data.static_rule_scoring.false_negatives}</td>
                      <td style={{ background: 'rgba(59, 130, 246, 0.08)' }}>
                        <b>{data.evidence_aware_cascade.true_positives}</b> / <b>{data.evidence_aware_cascade.false_positives}</b> / <b>{data.evidence_aware_cascade.true_negatives}</b> / <b>{data.evidence_aware_cascade.false_negatives}</b>
                      </td>
                    </tr>
                    <tr>
                      <td style={{ fontWeight: 600 }}>Avg Runtime (ms)</td>
                      <td>{data.baseline_simple_traversal.avg_runtime_ms} ms</td>
                      <td>{data.static_rule_scoring.avg_runtime_ms} ms</td>
                      <td style={{ background: 'rgba(59, 130, 246, 0.08)' }}>{data.evidence_aware_cascade.avg_runtime_ms} ms</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              {/* Takeaway Summary */}
              <div style={{ background: 'var(--bg-hover)', padding: '12px 16px', borderRadius: 'var(--radius-sm)', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>Key Finding: </span>
                {data.evaluation_criteria_summary}
              </div>
            </>
          ) : null}
        </div>
      </div>
    </div>
  );
}
