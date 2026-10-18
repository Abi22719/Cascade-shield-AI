import React from 'react';
import { 
  Server, 
  CheckCircle2, 
  AlertTriangle, 
  AlertOctagon, 
  Clock, 
  Zap,
  Activity
} from 'lucide-react';

export default function MetricsSummaryBar({ summary }) {
  if (!summary) return null;

  const total = summary.total_services || 0;
  const healthy = summary.healthy_services || 0;
  const warning = summary.warning_services || 0;
  const critical = summary.critical_services || 0;

  const healthyPct = total > 0 ? (healthy / total) * 100 : 0;
  const warningPct = total > 0 ? (warning / total) * 100 : 0;
  const criticalPct = total > 0 ? (critical / total) * 100 : 0;

  return (
    <div className="metrics-summary-bar">
      {/* Total Services */}
      <div className="metric-card">
        <div className="metric-card-header">
          <span className="metric-title">Total Services</span>
          <div className="metric-icon-box" style={{ background: 'rgba(56, 189, 248, 0.1)', color: '#38bdf8' }}>
            <Server size={15} />
          </div>
        </div>
        <div className="metric-value-row">
          <span className="metric-value">{total}</span>
          <span className="metric-unit">nodes</span>
        </div>
        <div className="health-bar-wrapper">
          <div className="health-bar-segment" style={{ width: `${healthyPct}%`, backgroundColor: '#10b981' }} title={`Healthy: ${healthy}`}></div>
          <div className="health-bar-segment" style={{ width: `${warningPct}%`, backgroundColor: '#f59e0b' }} title={`Warning: ${warning}`}></div>
          <div className="health-bar-segment" style={{ width: `${criticalPct}%`, backgroundColor: '#ef4444' }} title={`Critical: ${critical}`}></div>
        </div>
        <div className="metric-footer">
          <span>Health Score: <strong>{summary.health_score_pct}%</strong></span>
        </div>
      </div>

      {/* Healthy Services */}
      <div className="metric-card metric-healthy">
        <div className="metric-card-header">
          <span className="metric-title">Healthy</span>
          <div className="metric-icon-box">
            <CheckCircle2 size={15} />
          </div>
        </div>
        <div className="metric-value-row">
          <span className="metric-value">{healthy}</span>
          <span className="metric-unit">services</span>
        </div>
        <div className="metric-footer">
          <span>Normal operating thresholds</span>
        </div>
      </div>

      {/* Warning Services */}
      <div className="metric-card metric-warning">
        <div className="metric-card-header">
          <span className="metric-title">Warning</span>
          <div className="metric-icon-box">
            <AlertTriangle size={15} />
          </div>
        </div>
        <div className="metric-value-row">
          <span className="metric-value">{warning}</span>
          <span className="metric-unit">services</span>
        </div>
        <div className="metric-footer">
          <span>Elevated latency or errors</span>
        </div>
      </div>

      {/* Critical Services */}
      <div className="metric-card metric-critical">
        <div className="metric-card-header">
          <span className="metric-title">Critical</span>
          <div className="metric-icon-box">
            <AlertOctagon size={15} />
          </div>
        </div>
        <div className="metric-value-row">
          <span className="metric-value">{critical}</span>
          <span className="metric-unit">services</span>
        </div>
        <div className="metric-footer">
          <span>Severe degradation risk</span>
        </div>
      </div>

      {/* Avg Response Latency */}
      <div className="metric-card">
        <div className="metric-card-header">
          <span className="metric-title">Avg Latency</span>
          <div className="metric-icon-box" style={{ background: 'rgba(168, 85, 247, 0.1)', color: '#c084fc' }}>
            <Clock size={15} />
          </div>
        </div>
        <div className="metric-value-row">
          <span className="metric-value">{summary.avg_latency_ms}</span>
          <span className="metric-unit">ms</span>
        </div>
        <div className="metric-footer">
          <span>Simulated roundtrip time</span>
        </div>
      </div>

      {/* Avg Error Rate */}
      <div className="metric-card">
        <div className="metric-card-header">
          <span className="metric-title">Avg Error Rate</span>
          <div className="metric-icon-box" style={{ background: 'rgba(239, 68, 68, 0.1)', color: '#f87171' }}>
            <Zap size={15} />
          </div>
        </div>
        <div className="metric-value-row">
          <span className="metric-value">{summary.avg_error_rate}</span>
          <span className="metric-unit">%</span>
        </div>
        <div className="metric-footer">
          <span>Traffic volume: {summary.total_request_volume?.toLocaleString()} req/s</span>
        </div>
      </div>
    </div>
  );
}
