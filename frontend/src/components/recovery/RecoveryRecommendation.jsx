import React from 'react';
import { Award, CheckCircle2, ShieldAlert, ArrowRight, HelpCircle } from 'lucide-react';

export default function RecoveryRecommendation({
  comparisonResult,
  recommendedPlan
}) {
  if (!comparisonResult || !recommendedPlan) {
    return (
      <div style={{ textAlign: 'center', color: '#64748b', padding: '1.5rem', fontSize: '0.85rem' }}>
        No recommendation generated. Run plan comparison to synthesize trade-off analysis.
      </div>
    );
  }

  const {
    tradeoff_analysis,
    recommendation_reason,
    alternative_plans_rejection_reasons = {}
  } = comparisonResult;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.9rem' }}>
      {/* Recommendation Highlight Card */}
      <div style={{
        background: 'rgba(16, 185, 129, 0.1)',
        border: '1px solid rgba(16, 185, 129, 0.3)',
        borderRadius: '8px',
        padding: '1.1rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '0.5rem'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem', color: '#6ee7b7', fontWeight: 700, fontSize: '0.95rem' }}>
            <Award size={18} />
            <span>Recommended Plan: {recommendedPlan.plan_name}</span>
          </div>
          <span className={`strategy-badge ${recommendedPlan.strategy_type}`}>
            {recommendedPlan.strategy_type.replace('_', ' ')}
          </span>
        </div>

        <div style={{ fontSize: '0.82rem', color: '#e2e8f0', lineHeight: 1.45 }}>
          {recommendation_reason}
        </div>

        <div style={{ display: 'flex', gap: '1rem', fontSize: '0.75rem', color: '#cbd5e1', borderTop: '1px solid rgba(255, 255, 255, 0.08)', paddingTop: '0.5rem', marginTop: '0.3rem' }}>
          <span>Risk Score: <b style={{ color: '#6ee7b7' }}>{recommendedPlan.risk_score.toFixed(1)}/100</b></span>
          <span>•</span>
          <span>Recovery Window: <b style={{ color: '#f8fafc' }}>{recommendedPlan.estimated_recovery_time} steps</b></span>
          <span>•</span>
          <span>Resource Cost: <b style={{ color: '#f8fafc' }}>{recommendedPlan.estimated_cost.toFixed(1)} units</b></span>
        </div>
      </div>

      {/* Trade-Off Analysis Summary */}
      <div style={{
        background: 'rgba(30, 41, 59, 0.5)',
        border: '1px solid rgba(255, 255, 255, 0.08)',
        borderRadius: '6px',
        padding: '0.85rem 1rem',
        fontSize: '0.82rem',
        color: '#cbd5e1',
        lineHeight: 1.4
      }}>
        <div style={{ fontWeight: 600, color: '#f8fafc', marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
          <ShieldAlert size={14} color="#f59e0b" />
          <span>Resilience Trade-Off Analysis</span>
        </div>
        {tradeoff_analysis}
      </div>

      {/* Alternative Plans Rejection Justifications */}
      {Object.keys(alternative_plans_rejection_reasons).length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.45rem' }}>
          <div style={{ fontSize: '0.78rem', fontWeight: 600, color: '#94a3b8' }}>
            Why Alternative Strategies Were Rejected:
          </div>
          {Object.entries(alternative_plans_rejection_reasons).map(([name, reason], idx) => (
            <div
              key={idx}
              style={{
                background: 'rgba(15, 23, 42, 0.4)',
                borderLeft: '2px solid #64748b',
                padding: '0.4rem 0.65rem',
                fontSize: '0.75rem',
                color: '#cbd5e1'
              }}
            >
              <b style={{ color: '#f8fafc' }}>{name}:</b> {reason}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
