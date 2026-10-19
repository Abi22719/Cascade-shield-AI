import React from 'react';
import { ShieldCheck, CheckCircle2, AlertTriangle, XCircle, HelpCircle, Activity } from 'lucide-react';

export default function ValidationOverview({ summaryStats }) {
  const stats = summaryStats || {
    total: 0,
    verified_success: 0,
    partial_success: 0,
    failed: 0,
    inconclusive: 0,
  };

  const successRate = stats.total > 0
    ? Math.round((stats.verified_success / stats.total) * 100)
    : 0;

  return (
    <div className="val-kpi-grid">
      <div className="val-kpi-card">
        <span className="kpi-label">
          <Activity size={14} color="#0ea5e9" /> Total Validations
        </span>
        <span className="kpi-value">{stats.total}</span>
        <span className="kpi-sub">Simulated verification runs</span>
      </div>

      <div className="val-kpi-card">
        <span className="kpi-label">
          <CheckCircle2 size={14} color="#10b981" /> Verified Successes
        </span>
        <span className="kpi-value" style={{ color: '#34d399' }}>{stats.verified_success}</span>
        <span className="kpi-sub">{successRate}% verification success rate</span>
      </div>

      <div className="val-kpi-card">
        <span className="kpi-label">
          <AlertTriangle size={14} color="#f59e0b" /> Partial Successes
        </span>
        <span className="kpi-value" style={{ color: '#fbbf24' }}>{stats.partial_success}</span>
        <span className="kpi-sub">Recovered with metric/caller caveats</span>
      </div>

      <div className="val-kpi-card">
        <span className="kpi-label">
          <XCircle size={14} color="#ef4444" /> Failed Validations
        </span>
        <span className="kpi-value" style={{ color: '#f87171' }}>{stats.failed}</span>
        <span className="kpi-sub">Rollbacks or residual critical states</span>
      </div>

      <div className="val-kpi-card">
        <span className="kpi-label">
          <HelpCircle size={14} color="#a855f7" /> Inconclusive
        </span>
        <span className="kpi-value" style={{ color: '#c084fc' }}>{stats.inconclusive}</span>
        <span className="kpi-sub">Telemetry gaps / missing evidence</span>
      </div>
    </div>
  );
}
