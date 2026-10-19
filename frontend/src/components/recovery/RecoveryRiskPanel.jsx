import React from 'react';
import { AlertTriangle, ShieldCheck, Flame, Database, Clock, Info } from 'lucide-react';

export default function RecoveryRiskPanel({ plan }) {
  if (!plan) {
    return (
      <div style={{ textAlign: 'center', color: '#64748b', padding: '2rem 1rem', fontSize: '0.85rem' }}>
        Select a recovery plan to view its intelligent risk assessment breakdown.
      </div>
    );
  }

  const {
    risk_score = 0,
    risk_level = 'Low',
    estimated_recovery_time = 0,
    estimated_cost = 0,
    risk_breakdown = []
  } = plan;

  // Determine color for risk score
  let scoreColor = '#10b981';
  if (risk_score >= 75) scoreColor = '#ef4444';
  else if (risk_score >= 50) scoreColor = '#f97316';
  else if (risk_score >= 25) scoreColor = '#f59e0b';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Risk Score Header Card */}
      <div style={{
        background: 'rgba(30, 41, 59, 0.5)',
        border: '1px solid rgba(255, 255, 255, 0.08)',
        borderRadius: '8px',
        padding: '1rem',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div>
          <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#94a3b8', textTransform: 'uppercase' }}>
            Multi-Factor Risk Score
          </div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.5rem', marginTop: '0.2rem' }}>
            <span style={{ fontSize: '2.2rem', fontWeight: 800, color: scoreColor, fontFeatureSettings: 'tnum' }}>
              {risk_score.toFixed(1)}
            </span>
            <span style={{ fontSize: '0.9rem', color: '#64748b' }}>/ 100</span>
            <span style={{
              fontSize: '0.75rem',
              fontWeight: 700,
              padding: '0.2rem 0.5rem',
              borderRadius: '4px',
              backgroundColor: `${scoreColor}22`,
              color: scoreColor,
              border: `1px solid ${scoreColor}55`,
              marginLeft: '0.4rem'
            }}>
              {risk_level} Risk
            </span>
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.3rem', alignItems: 'flex-end', fontSize: '0.78rem' }}>
          <span style={{ color: '#94a3b8' }}>
            Duration: <b style={{ color: '#f8fafc' }}>{estimated_recovery_time} steps</b>
          </span>
          <span style={{ color: '#94a3b8' }}>
            Resource Cost: <b style={{ color: '#f8fafc' }}>{estimated_cost.toFixed(1)} units</b>
          </span>
        </div>
      </div>

      {/* Factor Breakdown List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
        <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <Info size={14} color="#0ea5e9" />
          <span>Risk Factor Contribution Breakdown</span>
        </div>

        {risk_breakdown.map((f, idx) => {
          const isIncreasing = f.impact_direction === 'increases_risk';
          const barColor = f.raw_score > 60 ? '#ef4444' : f.raw_score > 30 ? '#f59e0b' : '#10b981';

          return (
            <div key={idx} className="risk-factor-row">
              <div className="risk-factor-header">
                <span style={{ fontWeight: 600, color: '#e2e8f0' }}>{f.factor_name}</span>
                <span style={{ color: '#94a3b8', fontSize: '0.72rem' }}>
                  Raw: {f.raw_score.toFixed(1)} | Weighted: <b>{f.weighted_score.toFixed(1)}</b>
                </span>
              </div>

              <div className="risk-factor-bar-track">
                <div
                  className="risk-factor-bar-fill"
                  style={{
                    width: `${Math.min(100, f.raw_score)}%`,
                    backgroundColor: barColor
                  }}
                />
              </div>

              <div style={{ fontSize: '0.72rem', color: '#94a3b8', marginTop: '0.1rem' }}>
                {f.explanation}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
