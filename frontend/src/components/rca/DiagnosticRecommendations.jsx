import React, { useState } from 'react';
import { Stethoscope, CheckCircle, AlertTriangle, ArrowRight } from 'lucide-react';

export default function DiagnosticRecommendations({ recommendations = [] }) {
  const [reviewedMap, setReviewedMap] = useState({});

  const toggleReviewed = (id) => {
    setReviewedMap(prev => ({ ...prev, [id]: !prev[id] }));
  };

  const getPriorityClass = (pri) => {
    switch (pri?.toUpperCase()) {
      case 'P1_IMMEDIATE':
        return 'priority-badge p1';
      case 'P2_HIGH':
        return 'priority-badge p2';
      default:
        return 'priority-badge p3';
    }
  };

  if (!recommendations || recommendations.length === 0) return null;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <Stethoscope size={16} color="#3b82f6" />
        <h3 style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-main)', margin: 0 }}>
          Targeted Diagnostic Recommendations ({recommendations.length})
        </h3>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {recommendations.map((rec) => {
          const isDone = reviewedMap[rec.recommendation_id];

          return (
            <div
              key={rec.recommendation_id}
              className="recommendation-card"
              style={{
                opacity: isDone ? 0.6 : 1,
                borderLeft: isDone ? '4px solid #10b981' : undefined
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span className={getPriorityClass(rec.priority)}>
                    {rec.priority.replace('_', ' ')}
                  </span>
                  <span style={{ fontWeight: 600, color: 'var(--text-main)', fontSize: '0.82rem' }}>
                    {rec.action_description}
                  </span>
                </div>

                <button
                  type="button"
                  className="timeline-btn"
                  style={{
                    padding: '3px 8px',
                    fontSize: '0.7rem',
                    background: isDone ? 'rgba(16, 185, 129, 0.2)' : undefined,
                    color: isDone ? '#34d399' : undefined
                  }}
                  onClick={() => toggleReviewed(rec.recommendation_id)}
                >
                  <CheckCircle size={12} />
                  {isDone ? 'Reviewed' : 'Mark Reviewed'}
                </button>
              </div>

              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', lineHeight: 1.35 }}>
                <b>Rationale:</b> {rec.reason}
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: '#94a3b8', background: 'rgba(0,0,0,0.2)', padding: '6px 10px', borderRadius: '4px' }}>
                <span><b>Gap:</b> {rec.evidence_gap}</span>
                <span style={{ color: '#60a5fa' }}><b>Gain:</b> {rec.expected_information_gain}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
