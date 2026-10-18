import React, { useState, useEffect } from 'react';
import { X, BarChart2, ShieldCheck, CheckCircle2, RefreshCw } from 'lucide-react';
import { anomalyApi } from '../../services/anomalyApi';

export default function EvaluationModal({ isOpen, onClose }) {
  const [evalData, setEvalData] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchEvaluation = () => {
    setLoading(true);
    anomalyApi.getEvaluation()
      .then(data => setEvalData(data))
      .catch(err => console.error('Failed to load evaluation:', err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    if (isOpen) {
      fetchEvaluation();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-dialog" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '820px' }}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <BarChart2 size={20} color="#0ea5e9" />
            <h3>AI Anomaly Detection Performance Evaluation</h3>
          </div>
          <button className="btn-icon" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <div className="modal-body">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Evaluation metrics calculated across a labeled benchmark dataset with ground-truth labels.
            </p>
            <button 
              className="btn btn-secondary" 
              style={{ fontSize: '0.72rem', padding: '4px 8px' }}
              onClick={fetchEvaluation}
              disabled={loading}
            >
              <RefreshCw size={12} className={loading ? 'animate-spin' : ''} />
              <span>Re-run Evaluation</span>
            </button>
          </div>

          {evalData ? (
            <>
              {/* Benchmark Summary Pill */}
              <div style={{ 
                background: 'rgba(14, 165, 233, 0.08)', 
                border: '1px solid rgba(14, 165, 233, 0.3)',
                padding: '10px 14px', 
                borderRadius: '8px', 
                fontSize: '0.8rem',
                color: '#e2e8f0',
                display: 'flex',
                justifyContent: 'space-between',
                flexWrap: 'wrap',
                gap: '10px'
              }}>
                <div><strong>Total Benchmark Samples:</strong> {evalData.dataset_size}</div>
                <div><strong>Anomalous Samples:</strong> {evalData.anomalous_samples_count}</div>
                <div><strong>Normal Samples:</strong> {evalData.normal_samples_count}</div>
              </div>

              {/* 3 Detectors Comparison Grid */}
              <div className="eval-card-grid" style={{ marginTop: '14px' }}>
                {/* 1. Threshold Detector */}
                <div className="eval-detector-card">
                  <div className="eval-detector-title">1. Threshold Rules</div>
                  
                  <div className="eval-stat-row">
                    <span className="eval-stat-label">Precision:</span>
                    <span className="eval-stat-val">{(evalData.threshold_detector.precision * 100).toFixed(1)}%</span>
                  </div>
                  <div className="eval-stat-row">
                    <span className="eval-stat-label">Recall:</span>
                    <span className="eval-stat-val">{(evalData.threshold_detector.recall * 100).toFixed(1)}%</span>
                  </div>
                  <div className="eval-stat-row">
                    <span className="eval-stat-label">F1-Score:</span>
                    <span className="eval-stat-val" style={{ color: '#38bdf8' }}>{evalData.threshold_detector.f1_score.toFixed(3)}</span>
                  </div>
                  <div className="eval-stat-row">
                    <span className="eval-stat-label">Accuracy:</span>
                    <span className="eval-stat-val">{(evalData.threshold_detector.accuracy * 100).toFixed(1)}%</span>
                  </div>
                  <div className="eval-stat-row">
                    <span className="eval-stat-label">False-Pos. Rate:</span>
                    <span className="eval-stat-val">{(evalData.threshold_detector.false_positive_rate * 100).toFixed(1)}%</span>
                  </div>

                  <div style={{ marginTop: '10px', paddingTop: '8px', borderTop: '1px solid var(--border-color)', fontSize: '0.72rem', color: 'var(--text-dim)' }}>
                    Confusion Matrix: TP={evalData.threshold_detector.true_positives}, FP={evalData.threshold_detector.false_positives}, TN={evalData.threshold_detector.true_negatives}, FN={evalData.threshold_detector.false_negatives}
                  </div>
                </div>

                {/* 2. Isolation Forest */}
                <div className="eval-detector-card">
                  <div className="eval-detector-title" style={{ color: '#c084fc' }}>2. Isolation Forest (ML)</div>
                  
                  <div className="eval-stat-row">
                    <span className="eval-stat-label">Precision:</span>
                    <span className="eval-stat-val">{(evalData.isolation_forest.precision * 100).toFixed(1)}%</span>
                  </div>
                  <div className="eval-stat-row">
                    <span className="eval-stat-label">Recall:</span>
                    <span className="eval-stat-val">{(evalData.isolation_forest.recall * 100).toFixed(1)}%</span>
                  </div>
                  <div className="eval-stat-row">
                    <span className="eval-stat-label">F1-Score:</span>
                    <span className="eval-stat-val" style={{ color: '#c084fc' }}>{evalData.isolation_forest.f1_score.toFixed(3)}</span>
                  </div>
                  <div className="eval-stat-row">
                    <span className="eval-stat-label">Accuracy:</span>
                    <span className="eval-stat-val">{(evalData.isolation_forest.accuracy * 100).toFixed(1)}%</span>
                  </div>
                  <div className="eval-stat-row">
                    <span className="eval-stat-label">False-Pos. Rate:</span>
                    <span className="eval-stat-val">{(evalData.isolation_forest.false_positive_rate * 100).toFixed(1)}%</span>
                  </div>

                  <div style={{ marginTop: '10px', paddingTop: '8px', borderTop: '1px solid var(--border-color)', fontSize: '0.72rem', color: 'var(--text-dim)' }}>
                    Confusion Matrix: TP={evalData.isolation_forest.true_positives}, FP={evalData.isolation_forest.false_positives}, TN={evalData.isolation_forest.true_negatives}, FN={evalData.isolation_forest.false_negatives}
                  </div>
                </div>

                {/* 3. Combined Approach */}
                <div className="eval-detector-card" style={{ borderColor: 'rgba(16, 185, 129, 0.4)', background: 'rgba(16, 185, 129, 0.05)' }}>
                  <div className="eval-detector-title" style={{ color: '#10b981' }}>3. Combined Detection</div>
                  
                  <div className="eval-stat-row">
                    <span className="eval-stat-label">Precision:</span>
                    <span className="eval-stat-val">{(evalData.combined_detector.precision * 100).toFixed(1)}%</span>
                  </div>
                  <div className="eval-stat-row">
                    <span className="eval-stat-label">Recall:</span>
                    <span className="eval-stat-val" style={{ color: '#10b981', fontWeight: 700 }}>{(evalData.combined_detector.recall * 100).toFixed(1)}%</span>
                  </div>
                  <div className="eval-stat-row">
                    <span className="eval-stat-label">F1-Score:</span>
                    <span className="eval-stat-val" style={{ color: '#10b981', fontWeight: 700 }}>{evalData.combined_detector.f1_score.toFixed(3)}</span>
                  </div>
                  <div className="eval-stat-row">
                    <span className="eval-stat-label">Accuracy:</span>
                    <span className="eval-stat-val">{(evalData.combined_detector.accuracy * 100).toFixed(1)}%</span>
                  </div>
                  <div className="eval-stat-row">
                    <span className="eval-stat-label">False-Pos. Rate:</span>
                    <span className="eval-stat-val">{(evalData.combined_detector.false_positive_rate * 100).toFixed(1)}%</span>
                  </div>

                  <div style={{ marginTop: '10px', paddingTop: '8px', borderTop: '1px solid var(--border-color)', fontSize: '0.72rem', color: 'var(--text-dim)' }}>
                    Confusion Matrix: TP={evalData.combined_detector.true_positives}, FP={evalData.combined_detector.false_positives}, TN={evalData.combined_detector.true_negatives}, FN={evalData.combined_detector.false_negatives}
                  </div>
                </div>
              </div>

              {/* Methodology note */}
              <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', background: 'var(--bg-card)', padding: '10px', borderRadius: '6px' }}>
                <strong>Key Takeaway:</strong> Threshold rules excel at capturing single-metric spikes (high latency/CPU) with low false positives. Isolation Forest detects subtle multidimensional outliers where individual values stay within standard limits. The combined approach maximizes Recall and overall resilience protection.
              </div>
            </>
          ) : (
            <div style={{ textAlign: 'center', padding: '30px', color: 'var(--text-dim)' }}>
              Loading benchmark evaluation metrics...
            </div>
          )}
        </div>

        <div className="modal-footer">
          <button type="button" className="btn btn-secondary" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
