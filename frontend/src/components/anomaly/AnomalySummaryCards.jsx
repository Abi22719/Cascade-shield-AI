import React from 'react';
import { 
  Bell, 
  AlertOctagon, 
  AlertTriangle, 
  Cpu, 
  Server,
  CheckCircle2
} from 'lucide-react';

export default function AnomalySummaryCards({ summary }) {
  if (!summary) return null;

  return (
    <div className="anomaly-summary-grid">
      {/* Total Alerts */}
      <div className="anomaly-summary-card">
        <div className="card-top-row">
          <span className="card-title">Total Active Alerts</span>
          <div className="card-icon" style={{ background: 'rgba(14, 165, 233, 0.12)', color: '#38bdf8' }}>
            <Bell size={16} />
          </div>
        </div>
        <div className="card-value">{summary.total_alerts}</div>
        <div className="card-footer">
          <span>{summary.unacknowledged_alerts} pending acknowledgment</span>
        </div>
      </div>

      {/* Critical Alerts */}
      <div className="anomaly-summary-card" style={{ borderLeft: '3px solid #ef4444' }}>
        <div className="card-top-row">
          <span className="card-title">Critical Alerts</span>
          <div className="card-icon" style={{ background: 'rgba(239, 68, 68, 0.12)', color: '#ef4444' }}>
            <AlertOctagon size={16} />
          </div>
        </div>
        <div className="card-value" style={{ color: '#ef4444' }}>{summary.critical_alerts}</div>
        <div className="card-footer">
          <span>Severe threshold or cascade hazard</span>
        </div>
      </div>

      {/* Warning Alerts */}
      <div className="anomaly-summary-card" style={{ borderLeft: '3px solid #f59e0b' }}>
        <div className="card-top-row">
          <span className="card-title">Warning Alerts</span>
          <div className="card-icon" style={{ background: 'rgba(245, 158, 11, 0.12)', color: '#f59e0b' }}>
            <AlertTriangle size={16} />
          </div>
        </div>
        <div className="card-value" style={{ color: '#f59e0b' }}>{summary.warning_alerts}</div>
        <div className="card-footer">
          <span>Elevated latency, error, or ML deviation</span>
        </div>
      </div>

      {/* Anomalous Observations (ML) */}
      <div className="anomaly-summary-card" style={{ borderLeft: '3px solid #a855f7' }}>
        <div className="card-top-row">
          <span className="card-title">Anomalous Observations</span>
          <div className="card-icon" style={{ background: 'rgba(168, 85, 247, 0.12)', color: '#c084fc' }}>
            <Cpu size={16} />
          </div>
        </div>
        <div className="card-value" style={{ color: '#c084fc' }}>{summary.anomalous_observations}</div>
        <div className="card-footer">
          <span>Isolation Forest multivariate detections</span>
        </div>
      </div>

      {/* Affected Services */}
      <div className="anomaly-summary-card" style={{ borderLeft: '3px solid #0ea5e9' }}>
        <div className="card-top-row">
          <span className="card-title">Affected Services</span>
          <div className="card-icon" style={{ background: 'rgba(14, 165, 233, 0.12)', color: '#38bdf8' }}>
            <Server size={16} />
          </div>
        </div>
        <div className="card-value">{summary.affected_services}</div>
        <div className="card-footer">
          <span>Services with one or more alerts</span>
        </div>
      </div>
    </div>
  );
}
