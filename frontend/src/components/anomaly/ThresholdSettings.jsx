import React, { useState, useEffect } from 'react';
import { X, Sliders, CheckCircle2, AlertTriangle, Save } from 'lucide-react';

export default function ThresholdSettings({
  isOpen,
  onClose,
  initialThresholds,
  onSave
}) {
  const [cpuWarning, setCpuWarning] = useState(75.0);
  const [cpuCritical, setCpuCritical] = useState(90.0);
  const [memWarning, setMemWarning] = useState(80.0);
  const [memCritical, setMemCritical] = useState(95.0);
  const [latWarning, setLatWarning] = useState(500.0);
  const [latCritical, setLatCritical] = useState(1000.0);
  const [errWarning, setErrWarning] = useState(5.0);
  const [errCritical, setErrCritical] = useState(10.0);
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    if (initialThresholds) {
      setCpuWarning(initialThresholds.cpu_warning ?? 75.0);
      setCpuCritical(initialThresholds.cpu_critical ?? 90.0);
      setMemWarning(initialThresholds.memory_warning ?? 80.0);
      setMemCritical(initialThresholds.memory_critical ?? 95.0);
      setLatWarning(initialThresholds.latency_warning ?? 500.0);
      setLatCritical(initialThresholds.latency_critical ?? 1000.0);
      setErrWarning(initialThresholds.error_rate_warning ?? 5.0);
      setErrCritical(initialThresholds.error_rate_critical ?? 10.0);
    }
  }, [initialThresholds]);

  if (!isOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    setErrorMsg('');

    // Validation
    if (cpuWarning > cpuCritical) {
      setErrorMsg('CPU Warning threshold cannot exceed Critical threshold.');
      return;
    }
    if (memWarning > memCritical) {
      setErrorMsg('Memory Warning threshold cannot exceed Critical threshold.');
      return;
    }
    if (latWarning > latCritical) {
      setErrorMsg('Latency Warning threshold cannot exceed Critical threshold.');
      return;
    }
    if (errWarning > errCritical) {
      setErrorMsg('Error Rate Warning threshold cannot exceed Critical threshold.');
      return;
    }

    const payload = {
      cpu_warning: parseFloat(cpuWarning),
      cpu_critical: parseFloat(cpuCritical),
      memory_warning: parseFloat(memWarning),
      memory_critical: parseFloat(memCritical),
      latency_warning: parseFloat(latWarning),
      latency_critical: parseFloat(latCritical),
      error_rate_warning: parseFloat(errWarning),
      error_rate_critical: parseFloat(errCritical)
    };

    onSave(payload);
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-dialog" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '540px' }}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Sliders size={18} color="#0ea5e9" />
            <h3>Configurable Anomaly Thresholds</h3>
          </div>
          <button className="btn-icon" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Configure operational thresholds for rule-based detection. Threshold breaches generate Warning or Critical incident alerts.
            </p>

            {errorMsg && (
              <div style={{ 
                background: 'rgba(239, 68, 68, 0.12)', 
                border: '1px solid #ef4444', 
                padding: '8px 12px', 
                borderRadius: '6px', 
                color: '#f87171', 
                fontSize: '0.8rem' 
              }}>
                {errorMsg}
              </div>
            )}

            {/* CPU Thresholds */}
            <div style={{ background: 'var(--bg-card)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
              <div style={{ fontWeight: 600, fontSize: '0.82rem', marginBottom: '8px', color: '#f8fafc' }}>
                CPU Utilization (%)
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div className="form-group">
                  <label className="form-label" style={{ color: '#f59e0b' }}>Warning Limit (%)</label>
                  <input
                    type="number"
                    min="1"
                    max="100"
                    step="0.5"
                    className="form-input"
                    value={cpuWarning}
                    onChange={(e) => setCpuWarning(e.target.value)}
                    required
                  />
                </div>
                <div className="form-group">
                  <label className="form-label" style={{ color: '#ef4444' }}>Critical Limit (%)</label>
                  <input
                    type="number"
                    min="1"
                    max="100"
                    step="0.5"
                    className="form-input"
                    value={cpuCritical}
                    onChange={(e) => setCpuCritical(e.target.value)}
                    required
                  />
                </div>
              </div>
            </div>

            {/* Memory Thresholds */}
            <div style={{ background: 'var(--bg-card)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
              <div style={{ fontWeight: 600, fontSize: '0.82rem', marginBottom: '8px', color: '#f8fafc' }}>
                Memory Utilization (%)
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div className="form-group">
                  <label className="form-label" style={{ color: '#f59e0b' }}>Warning Limit (%)</label>
                  <input
                    type="number"
                    min="1"
                    max="100"
                    step="0.5"
                    className="form-input"
                    value={memWarning}
                    onChange={(e) => setMemWarning(e.target.value)}
                    required
                  />
                </div>
                <div className="form-group">
                  <label className="form-label" style={{ color: '#ef4444' }}>Critical Limit (%)</label>
                  <input
                    type="number"
                    min="1"
                    max="100"
                    step="0.5"
                    className="form-input"
                    value={memCritical}
                    onChange={(e) => setMemCritical(e.target.value)}
                    required
                  />
                </div>
              </div>
            </div>

            {/* Latency Thresholds */}
            <div style={{ background: 'var(--bg-card)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
              <div style={{ fontWeight: 600, fontSize: '0.82rem', marginBottom: '8px', color: '#f8fafc' }}>
                Response Latency (ms)
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div className="form-group">
                  <label className="form-label" style={{ color: '#f59e0b' }}>Warning Limit (ms)</label>
                  <input
                    type="number"
                    min="10"
                    step="10"
                    className="form-input"
                    value={latWarning}
                    onChange={(e) => setLatWarning(e.target.value)}
                    required
                  />
                </div>
                <div className="form-group">
                  <label className="form-label" style={{ color: '#ef4444' }}>Critical Limit (ms)</label>
                  <input
                    type="number"
                    min="10"
                    step="10"
                    className="form-input"
                    value={latCritical}
                    onChange={(e) => setLatCritical(e.target.value)}
                    required
                  />
                </div>
              </div>
            </div>

            {/* Error Rate Thresholds */}
            <div style={{ background: 'var(--bg-card)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
              <div style={{ fontWeight: 600, fontSize: '0.82rem', marginBottom: '8px', color: '#f8fafc' }}>
                Error Rate (%)
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div className="form-group">
                  <label className="form-label" style={{ color: '#f59e0b' }}>Warning Limit (%)</label>
                  <input
                    type="number"
                    min="0.1"
                    max="100"
                    step="0.1"
                    className="form-input"
                    value={errWarning}
                    onChange={(e) => setErrWarning(e.target.value)}
                    required
                  />
                </div>
                <div className="form-group">
                  <label className="form-label" style={{ color: '#ef4444' }}>Critical Limit (%)</label>
                  <input
                    type="number"
                    min="0.1"
                    max="100"
                    step="0.1"
                    className="form-input"
                    value={errCritical}
                    onChange={(e) => setErrCritical(e.target.value)}
                    required
                  />
                </div>
              </div>
            </div>
          </div>

          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary">
              <Save size={15} />
              <span>Save Thresholds</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
