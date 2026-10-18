import React from 'react';
import { 
  X, 
  AlertTriangle, 
  AlertOctagon, 
  CheckCircle2, 
  Check, 
  Activity, 
  Clock, 
  Server,
  Cpu
} from 'lucide-react';

export default function AlertDetailsPanel({
  alert,
  onClose,
  onAcknowledge
}) {
  if (!alert) return null;

  const timeStr = new Date(alert.created_at).toLocaleString([], {
    dateStyle: 'medium',
    timeStyle: 'medium'
  });

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-dialog" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '580px' }}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            {alert.severity === 'Critical' && <AlertOctagon size={20} color="#ef4444" />}
            {alert.severity === 'Warning' && <AlertTriangle size={20} color="#f59e0b" />}
            {alert.severity === 'Normal' && <CheckCircle2 size={20} color="#10b981" />}
            <h3>Alert Evidence & Diagnostic Snapshot</h3>
          </div>
          <button className="btn-icon" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <div className="modal-body">
          {/* Header Tag Bar */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingBottom: '12px', borderBottom: '1px solid var(--border-color)' }}>
            <div>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
                {alert.id}
              </span>
              <h4 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#f8fafc', marginTop: '2px' }}>
                {alert.service_name}
              </h4>
            </div>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              <span className={`severity-pill ${alert.severity.toLowerCase()}`}>
                {alert.severity}
              </span>
              <span className="method-tag">
                {alert.detection_method}
              </span>
            </div>
          </div>

          {/* Metric Details Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <div className="telemetry-item">
              <div className="telemetry-label">Primary Metric</div>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.95rem', fontWeight: 600, color: '#38bdf8' }}>
                {alert.metric_name}
              </div>
            </div>

            <div className="telemetry-item">
              <div className="telemetry-label">Observed vs Threshold</div>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.95rem', fontWeight: 600 }}>
                {alert.observed_value !== null ? alert.observed_value.toFixed(1) : 'N/A'}
                {alert.threshold_value ? ` / ${alert.threshold_value.toFixed(1)}` : ''}
              </div>
            </div>

            <div className="telemetry-item">
              <div className="telemetry-label">Isolation Forest Score</div>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.95rem', fontWeight: 600, color: '#c084fc' }}>
                {alert.anomaly_score !== null ? alert.anomaly_score.toFixed(4) : 'N/A (Threshold only)'}
              </div>
            </div>

            <div className="telemetry-item">
              <div className="telemetry-label">Data Origin</div>
              <div style={{ fontSize: '0.9rem', color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span className="pulse-dot"></span>
                <span>{alert.data_source}</span>
              </div>
            </div>
          </div>

          {/* Evidence Summary Box */}
          <div style={{ background: 'var(--bg-card)', padding: '14px', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
            <div style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-dim)', marginBottom: '6px' }}>
              Detailed Anomaly Evidence
            </div>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-main)', lineHeight: '1.5' }}>
              {alert.evidence_summary}
            </p>
          </div>

          {/* Timestamp and Acknowledgment Status */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.78rem', color: 'var(--text-dim)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Clock size={14} />
              <span>Incident Detected: {timeStr}</span>
            </div>
            <div>
              {alert.acknowledged ? (
                <span style={{ color: '#10b981', display: 'flex', alignItems: 'center', gap: '4px', fontWeight: 600 }}>
                  <Check size={14} /> Acknowledged
                </span>
              ) : (
                <span style={{ color: '#f59e0b', fontWeight: 600 }}>
                  Awaiting Acknowledgment
                </span>
              )}
            </div>
          </div>
        </div>

        <div className="modal-footer">
          <button type="button" className="btn btn-secondary" onClick={onClose}>
            Close
          </button>
          {!alert.acknowledged && (
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => {
                onAcknowledge(alert.id);
                onClose();
              }}
            >
              <Check size={15} />
              <span>Acknowledge Alert</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
