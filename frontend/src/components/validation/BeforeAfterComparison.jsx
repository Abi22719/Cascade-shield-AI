import React from 'react';
import { ArrowDownRight, ArrowUpRight, Minus, CheckCircle, AlertTriangle, XCircle } from 'lucide-react';

export default function BeforeAfterComparison({ comparison }) {
  if (!comparison) {
    return (
      <div className="val-card">
        <div className="val-card-header">
          <h3>Before-and-After Recovery Comparison</h3>
        </div>
        <p style={{ fontSize: '0.82rem', color: '#94a3b8' }}>
          No comparison summary available.
        </p>
      </div>
    );
  }

  const {
    healthy_count_before,
    healthy_count_after,
    degraded_count_before,
    degraded_count_after,
    unavailable_count_before,
    unavailable_count_after,
    affected_downstream_before,
    affected_downstream_after,
    metric_diffs,
    new_simulated_failures,
    is_stable_across_window,
    stability_window_steps
  } = comparison;

  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'IMPROVED':
        return <span className="trend-improved" style={{ display: 'flex', alignItems: 'center', gap: '0.2rem' }}><ArrowDownRight size={14} /> Improved</span>;
      case 'WORSENED':
        return <span className="trend-worsened" style={{ display: 'flex', alignItems: 'center', gap: '0.2rem' }}><ArrowUpRight size={14} /> Worsened</span>;
      default:
        return <span className="trend-unchanged" style={{ display: 'flex', alignItems: 'center', gap: '0.2rem' }}><Minus size={14} /> Unchanged</span>;
    }
  };

  return (
    <div className="val-card">
      <div className="val-card-header">
        <h3>Before-and-After Simulated Recovery Comparison</h3>
        <span style={{ fontSize: '0.75rem', color: is_stable_across_window ? '#34d399' : '#fbbf24' }}>
          {is_stable_across_window ? `Stable over ${stability_window_steps} steps` : 'Stability Warning'}
        </span>
      </div>

      <div className="comparison-grid">
        <div className="comp-state-box">
          <h4>Pre-Recovery State (Incident Active)</h4>
          <div className="comp-counts">
            <div>Healthy: <strong className="comp-badge" style={{ color: '#34d399' }}>{healthy_count_before}</strong></div>
            <div>Degraded: <strong className="comp-badge" style={{ color: '#fbbf24' }}>{degraded_count_before}</strong></div>
            <div>Critical: <strong className="comp-badge" style={{ color: '#f87171' }}>{unavailable_count_before}</strong></div>
          </div>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.4rem' }}>
            Affected Downstream Callers: <strong>{affected_downstream_before}</strong>
          </div>
        </div>

        <div className="comp-state-box">
          <h4>Post-Recovery State (Simulated)</h4>
          <div className="comp-counts">
            <div>Healthy: <strong className="comp-badge" style={{ color: '#34d399' }}>{healthy_count_after}</strong></div>
            <div>Degraded: <strong className="comp-badge" style={{ color: '#fbbf24' }}>{degraded_count_after}</strong></div>
            <div>Critical: <strong className="comp-badge" style={{ color: '#f87171' }}>{unavailable_count_after}</strong></div>
          </div>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.4rem' }}>
            Residual Unhealthy Callers: <strong style={{ color: affected_downstream_after > 0 ? '#f87171' : '#34d399' }}>{affected_downstream_after}</strong>
          </div>
        </div>
      </div>

      {new_simulated_failures?.length > 0 && (
        <div style={{ padding: '0.6rem 0.8rem', background: 'rgba(239, 68, 68, 0.15)', borderRadius: '6px', border: '1px solid rgba(239, 68, 68, 0.3)', marginBottom: '1rem', fontSize: '0.75rem', color: '#f87171' }}>
          <strong>Secondary Degradation Alert:</strong> Services {new_simulated_failures.join(', ')} suffered secondary failure post-recovery.
        </div>
      )}

      <h4 style={{ fontSize: '0.85rem', color: '#f8fafc', margin: '0 0 0.5rem 0' }}>Key Metric Differentials</h4>
      <div style={{ overflowX: 'auto', maxHeight: '250px' }}>
        <table className="val-check-table">
          <thead>
            <tr>
              <th>Service</th>
              <th>Metric</th>
              <th>Before</th>
              <th>After</th>
              <th>Delta</th>
              <th>% Change</th>
              <th>Trend</th>
              <th>SLA</th>
            </tr>
          </thead>
          <tbody>
            {(metric_diffs || []).slice(0, 10).map((m, idx) => (
              <tr key={idx}>
                <td><strong>{m.service_id}</strong></td>
                <td style={{ textTransform: 'capitalize' }}>{m.metric_name.replace('_', ' ')}</td>
                <td>{m.before_value !== null ? m.before_value : '-'}</td>
                <td style={{ fontWeight: 600 }}>{m.after_value !== null ? m.after_value : '-'}</td>
                <td>{m.delta !== null ? m.delta : '-'}</td>
                <td>{m.percent_change !== null ? `${m.percent_change}%` : '-'}</td>
                <td>{getTrendIcon(m.trend)}</td>
                <td>
                  <span className={`counter-pill ${m.status === 'PASS' ? 'pill-pass' : (m.status === 'FAIL' ? 'pill-fail' : 'pill-warn')}`}>
                    {m.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
