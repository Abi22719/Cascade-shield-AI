import React from 'react';
import { Play, RefreshCw, Sliders, BarChart2, ShieldAlert } from 'lucide-react';

export default function DetectionMethodSelector({
  method,
  onMethodChange,
  onRunDetection,
  onRefresh,
  onOpenThresholds,
  onOpenEvaluation,
  loading
}) {
  return (
    <div className="detection-controls-card">
      <div className="controls-left-group">
        <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)' }}>
          Detection Mode:
        </span>
        <div className="method-btn-group">
          <button
            className={`method-btn ${method === 'combined' ? 'active' : ''}`}
            onClick={() => onMethodChange('combined')}
            title="Combines threshold violations and Isolation Forest multivariate anomalies"
          >
            Combined (Recommended)
          </button>
          <button
            className={`method-btn ${method === 'threshold' ? 'active' : ''}`}
            onClick={() => onMethodChange('threshold')}
            title="Evaluates metric thresholds (Warning & Critical limits)"
          >
            Threshold Rules Only
          </button>
          <button
            className={`method-btn ${method === 'isolation_forest' ? 'active' : ''}`}
            onClick={() => onMethodChange('isolation_forest')}
            title="Uses Scikit-learn Isolation Forest for multivariate anomaly detection"
          >
            Isolation Forest (ML)
          </button>
        </div>

        <button
          className="btn btn-primary"
          onClick={onRunDetection}
          disabled={loading}
          title="Run detection scan on active services"
        >
          <Play size={14} fill="currentColor" />
          <span>Run Detection Scan</span>
        </button>

        <button
          className="btn btn-secondary"
          onClick={onRefresh}
          disabled={loading}
          title="Fetch latest metrics and alerts"
        >
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
          <span>Refresh</span>
        </button>
      </div>

      <div className="controls-right-group">
        <button
          className="btn btn-secondary"
          onClick={onOpenThresholds}
          title="Configure warning and critical metric limits"
        >
          <Sliders size={14} />
          <span>Threshold Settings</span>
        </button>

        <button
          className="btn btn-secondary"
          onClick={onOpenEvaluation}
          title="View benchmark evaluation comparing detection algorithms on labeled data"
        >
          <BarChart2 size={14} color="#0ea5e9" />
          <span>Evaluation Benchmark</span>
        </button>
      </div>
    </div>
  );
}
