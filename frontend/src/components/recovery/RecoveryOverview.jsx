import React from 'react';
import { ShieldCheck, PlayCircle, CheckCircle2, AlertTriangle, LifeBuoy } from 'lucide-react';

export default function RecoveryOverview({
  plans = [],
  activeIncidentsCount = 0
}) {
  const totalPlans = plans.length;
  const simulatedPlans = plans.filter(p => p.status === 'SIMULATED' || (p.runs_count || 0) > 0).length;
  const successfulRecoveries = plans.filter(p => p.runs_count > 0 && p.status !== 'REJECTED').length;
  const highRiskPlans = plans.filter(p => p.risk_level === 'High' || p.risk_level === 'Critical').length;

  return (
    <div className="rec-kpi-grid">
      <div className="rec-kpi-card">
        <div className="rec-kpi-title">
          <span>Total Recovery Plans</span>
          <LifeBuoy size={16} color="#10b981" />
        </div>
        <div className="rec-kpi-value">{totalPlans}</div>
        <div className="rec-kpi-sub">Across active incident archetypes</div>
      </div>

      <div className="rec-kpi-card info">
        <div className="rec-kpi-title">
          <span>Plans Simulated</span>
          <PlayCircle size={16} color="#0ea5e9" />
        </div>
        <div className="rec-kpi-value">{simulatedPlans}</div>
        <div className="rec-kpi-sub">Tested in virtual simulation sandbox</div>
      </div>

      <div className="rec-kpi-card success">
        <div className="rec-kpi-title">
          <span>Successful Recoveries</span>
          <CheckCircle2 size={16} color="#10b981" />
        </div>
        <div className="rec-kpi-value">{successfulRecoveries}</div>
        <div className="rec-kpi-sub">Simulated full health restoration</div>
      </div>

      <div className="rec-kpi-card warning">
        <div className="rec-kpi-title">
          <span>High-Risk Plans</span>
          <AlertTriangle size={16} color="#f59e0b" />
        </div>
        <div className="rec-kpi-value">{highRiskPlans}</div>
        <div className="rec-kpi-sub">Require stakeholder sign-off</div>
      </div>

      <div className="rec-kpi-card purple">
        <div className="rec-kpi-title">
          <span>Active Incidents</span>
          <ShieldCheck size={16} color="#8b5cf6" />
        </div>
        <div className="rec-kpi-value">{activeIncidentsCount}</div>
        <div className="rec-kpi-sub">Correlated from Modules 2 & 4</div>
      </div>
    </div>
  );
}
