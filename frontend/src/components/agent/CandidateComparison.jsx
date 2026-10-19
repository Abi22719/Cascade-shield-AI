import React from 'react';
import { Target, ShieldAlert, Award, AlertCircle } from 'lucide-react';

export default function CandidateComparison({ candidates = [] }) {
  const getConfidenceBadge = (label) => {
    switch (label) {
      case 'Strong supporting evidence':
        return <span className="badge badge-critical" style={{ fontSize: '0.68rem' }}>Strong Confidence</span>;
      case 'Moderate supporting evidence':
        return <span className="badge badge-warning" style={{ fontSize: '0.68rem' }}>Moderate</span>;
      case 'Weak supporting evidence':
        return <span className="badge" style={{ background: '#334155', color: '#94a3b8', fontSize: '0.68rem' }}>Weak</span>;
      default:
        return <span className="badge" style={{ background: '#1e293b', border: '1px dashed #475569', color: '#64748b', fontSize: '0.68rem' }}>Insufficient</span>;
    }
  };

  return (
    <div className="agent-panel">
      <div className="panel-title">
        <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Target size={16} color="#ef4444" />
          <span>Root Cause Candidate Dynamic Ranking</span>
        </span>
        <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
          {candidates.length} candidate{candidates.length === 1 ? '' : 's'} tracked
        </span>
      </div>

      {candidates.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '1.5rem', color: '#64748b', fontSize: '0.85rem' }}>
          No root cause candidates registered in session context.
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
          {candidates.map((c, idx) => {
            const score = c.score || 0;
            const isTop = idx === 0;

            return (
              <div 
                key={c.service_id}
                style={{ 
                  background: isTop ? 'rgba(14, 165, 233, 0.08)' : '#0f172a',
                  border: `1px solid ${isTop ? '#0284c7' : '#334155'}`,
                  borderRadius: '8px',
                  padding: '0.8rem 0.9rem',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.4rem'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span 
                      style={{ 
                        background: isTop ? '#0284c7' : '#334155', 
                        color: '#ffffff', 
                        fontSize: '0.72rem', 
                        fontWeight: 700, 
                        width: '20px', 
                        height: '20px', 
                        borderRadius: '50%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                      }}
                    >
                      {idx + 1}
                    </span>
                    <span style={{ fontWeight: 600, fontSize: '0.85rem', color: '#f8fafc' }}>
                      {c.service_name || c.service_id}
                    </span>
                    <code style={{ fontSize: '0.7rem', color: '#38bdf8' }}>{c.service_id}</code>
                  </div>
                  <div>
                    {getConfidenceBadge(c.confidence_label)}
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem', marginTop: '0.2rem' }}>
                  <div style={{ flex: 1, background: '#1e293b', height: '6px', borderRadius: '3px', overflow: 'hidden' }}>
                    <div 
                      style={{ 
                        background: isTop ? 'linear-gradient(90deg, #0ea5e9, #38bdf8)' : '#64748b',
                        height: '100%',
                        width: `${Math.min(100, Math.max(0, score))}%`,
                        transition: 'width 0.4s ease'
                      }}
                    />
                  </div>
                  <span style={{ fontSize: '0.85rem', fontWeight: 700, color: isTop ? '#38bdf8' : '#cbd5e1', minWidth: '40px', textAlign: 'right' }}>
                    {score.toFixed(1)}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
