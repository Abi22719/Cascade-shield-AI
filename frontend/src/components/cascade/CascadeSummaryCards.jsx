import React from 'react';
import { AlertTriangle, ShieldAlert, GitBranch, ArrowRightCircle, Activity, Flame } from 'lucide-react';

export default function CascadeSummaryCards({ prediction, summary }) {
  const totalAnalyzed = prediction?.total_services_analyzed || summary?.total_services || 9;
  const totalImpacted = prediction?.total_impacted_services ?? (summary?.predicted_impacted_services || 0);
  const directCount = prediction?.direct_impact_count ?? 0;
  const indirectCount = prediction?.indirect_impact_count ?? 0;
  const highRiskCount = prediction?.high_risk_count ?? (summary?.high_risk_services || 0);
  const criticalRiskCount = prediction?.critical_risk_count ?? (summary?.critical_risk_services || 0);
  const maxRisk = prediction?.max_risk_score ?? 0;

  return (
    <div className="cascade-summary-grid">
      <div className="cascade-summary-card accent-blue">
        <div className="card-label">
          <span>Digital Twin Services</span>
          <Activity size={16} />
        </div>
        <div className="card-value">{totalAnalyzed}</div>
        <div className="card-subtext">Monitored cluster nodes</div>
      </div>

      <div className="cascade-summary-card accent-orange">
        <div className="card-label">
          <span>Total Blast Radius</span>
          <GitBranch size={16} />
        </div>
        <div className="card-value">{totalImpacted}</div>
        <div className="card-subtext">
          {totalImpacted > 0 ? `${directCount} Direct · ${indirectCount} Indirect` : 'No active incident simulation'}
        </div>
      </div>

      <div className="cascade-summary-card accent-red">
        <div className="card-label">
          <span>Critical Risk Services</span>
          <Flame size={16} />
        </div>
        <div className="card-value">{criticalRiskCount}</div>
        <div className="card-subtext">Immediate brownout hazard (score ≥ 75)</div>
      </div>

      <div className="cascade-summary-card accent-purple">
        <div className="card-label">
          <span>High Risk Services</span>
          <AlertTriangle size={16} />
        </div>
        <div className="card-value">{highRiskCount}</div>
        <div className="card-subtext">Vulnerable callers (score 50–74)</div>
      </div>

      <div className="cascade-summary-card accent-green">
        <div className="card-label">
          <span>Peak Risk Score</span>
          <ShieldAlert size={16} />
        </div>
        <div className="card-value">{maxRisk} <span style={{ fontSize: '1rem', fontWeight: 500 }}>/ 100</span></div>
        <div className="card-subtext">Maximum heuristic hazard level</div>
      </div>
    </div>
  );
}
