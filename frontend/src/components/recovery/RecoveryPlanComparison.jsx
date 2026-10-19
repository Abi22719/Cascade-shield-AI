import React from 'react';
import { GitCompare, Award, CheckCircle2 } from 'lucide-react';

export default function RecoveryPlanComparison({
  comparisonResult,
  onSelectPlan
}) {
  if (!comparisonResult || !comparisonResult.compared_plans || comparisonResult.compared_plans.length === 0) {
    return (
      <div style={{ textAlign: 'center', color: '#64748b', padding: '2rem 1rem', fontSize: '0.85rem' }}>
        No comparison data available. Generate candidate plans to enable side-by-side trade-off analysis.
      </div>
    );
  }

  const { compared_plans, recommended_plan_id } = comparisonResult;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <div className="sim-table-container">
        <table className="sim-table">
          <thead>
            <tr>
              <th>Recovery Strategy</th>
              <th>Strategy Type</th>
              <th>Risk Score</th>
              <th>Recovery Time</th>
              <th>Resource Cost</th>
              <th>Reversibility</th>
              <th>Data Loss</th>
              <th>Outcome</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {compared_plans.map((p) => {
              const isRec = p.plan_id === recommended_plan_id;

              return (
                <tr
                  key={p.plan_id}
                  style={{
                    backgroundColor: isRec ? 'rgba(16, 185, 129, 0.1)' : undefined
                  }}
                >
                  <td>
                    <div style={{ fontWeight: 700, color: isRec ? '#6ee7b7' : '#f8fafc', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                      {isRec && <Award size={14} color="#10b981" />}
                      <span>{p.plan_name}</span>
                    </div>
                  </td>
                  <td>
                    <span className={`strategy-badge ${p.strategy_type}`}>
                      {p.strategy_type.replace('_', ' ')}
                    </span>
                  </td>
                  <td>
                    <span style={{ fontWeight: 700, color: p.risk_score > 50 ? '#f87171' : '#34d399' }}>
                      {p.risk_score.toFixed(1)}
                    </span>
                    <span style={{ fontSize: '0.7rem', color: '#94a3b8', marginLeft: '0.2rem' }}>
                      ({p.risk_level})
                    </span>
                  </td>
                  <td>{p.estimated_recovery_time} steps</td>
                  <td>{p.estimated_cost.toFixed(1)} units</td>
                  <td>
                    <span className={`reversibility-badge ${p.reversibility}`}>
                      {p.reversibility.replace('_', ' ')}
                    </span>
                  </td>
                  <td>
                    <span style={{
                      color: p.data_loss_exposure === 'High' ? '#f87171' : (p.data_loss_exposure === 'Moderate' ? '#fbbf24' : '#6ee7b7'),
                      fontWeight: 600,
                      fontSize: '0.75rem'
                    }}>
                      {p.data_loss_exposure}
                    </span>
                  </td>
                  <td>
                    <span style={{ fontSize: '0.75rem', color: p.simulated_outcome ? '#6ee7b7' : '#94a3b8' }}>
                      {p.simulated_outcome ? p.simulated_outcome.replace('_', ' ') : 'Pending'}
                    </span>
                  </td>
                  <td>
                    <button
                      className="btn-rec-secondary"
                      onClick={() => onSelectPlan && onSelectPlan(p.plan_id)}
                      style={{ fontSize: '0.75rem', padding: '0.25rem 0.55rem' }}
                    >
                      Inspect
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
