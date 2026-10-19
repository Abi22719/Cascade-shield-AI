import React from 'react';
import { AlertTriangle, Flame, Clock, RefreshCw, Activity } from 'lucide-react';

export default function SimulationSummaryCards({ summary, currentStep, totalSteps }) {
  if (!summary) {
    return (
      <div className="sim-kpi-grid">
        <div className="sim-kpi-card info">
          <div className="sim-kpi-title">
            <span>Simulation Status</span>
            <Activity size={16} />
          </div>
          <div className="sim-kpi-value">Ready</div>
          <div className="sim-kpi-sub">Configure and run scenario</div>
        </div>
        <div className="sim-kpi-card">
          <div className="sim-kpi-title">
            <span>Total Steps</span>
            <Clock size={16} />
          </div>
          <div className="sim-kpi-value">{totalSteps || 0}</div>
          <div className="sim-kpi-sub">Discrete time steps</div>
        </div>
        <div className="sim-kpi-card">
          <div className="sim-kpi-title">
            <span>Current Step</span>
            <Activity size={16} />
          </div>
          <div className="sim-kpi-value">Step {currentStep || 0}</div>
          <div className="sim-kpi-sub">Timeline position</div>
        </div>
      </div>
    );
  }

  const {
    total_impacted_services = 0,
    peak_simultaneous_impact = 0,
    time_to_first_downstream_impact = null,
    time_to_recovery = null,
    aggregate_impact_score = 0,
    max_risk_score = 0,
    propagation_events_count = 0
  } = summary;

  return (
    <div className="sim-kpi-grid">
      <div className="sim-kpi-card danger">
        <div className="sim-kpi-title">
          <span>Total Impacted</span>
          <AlertTriangle size={16} color="#ef4444" />
        </div>
        <div className="sim-kpi-value">{total_impacted_services}</div>
        <div className="sim-kpi-sub">Services degraded or failing</div>
      </div>

      <div className="sim-kpi-card warning">
        <div className="sim-kpi-title">
          <span>Peak Blast Radius</span>
          <Flame size={16} color="#f59e0b" />
        </div>
        <div className="sim-kpi-value">{peak_simultaneous_impact}</div>
        <div className="sim-kpi-sub">Max simultaneous failures</div>
      </div>

      <div className="sim-kpi-card info">
        <div className="sim-kpi-title">
          <span>Propagation Velocity</span>
          <Clock size={16} color="#0ea5e9" />
        </div>
        <div className="sim-kpi-value">
          {time_to_first_downstream_impact !== null ? `Step ${time_to_first_downstream_impact}` : 'None'}
        </div>
        <div className="sim-kpi-sub">
          {time_to_first_downstream_impact !== null ? 'Time to 1st downstream impact' : 'No downstream cascade'}
        </div>
      </div>

      <div className="sim-kpi-card success">
        <div className="sim-kpi-title">
          <span>Recovery Window</span>
          <RefreshCw size={16} color="#10b981" />
        </div>
        <div className="sim-kpi-value">
          {time_to_recovery !== null ? `Step ${time_to_recovery}` : 'N/A'}
        </div>
        <div className="sim-kpi-sub">
          {time_to_recovery !== null ? 'First service recovery step' : 'No recovery modeled'}
        </div>
      </div>

      <div className="sim-kpi-card" style={{ borderTop: '3px solid #8b5cf6' }}>
        <div className="sim-kpi-title">
          <span>Resilience Penalty</span>
          <Activity size={16} color="#a78bfa" />
        </div>
        <div className="sim-kpi-value">{aggregate_impact_score} <span style={{ fontSize: '0.9rem', color: '#94a3b8' }}>/100</span></div>
        <div className="sim-kpi-sub">Peak risk: {max_risk_score} | {propagation_events_count} waves</div>
      </div>
    </div>
  );
}
