import React from 'react';
import { Lightbulb, AlertCircle, ShieldAlert, ArrowRight } from 'lucide-react';

export default function ValidationRecommendations({ recommendations }) {
  if (!recommendations || recommendations.length === 0) {
    return (
      <div className="val-card">
        <div className="val-card-header">
          <h3>Actionable Recommendations</h3>
        </div>
        <p style={{ fontSize: '0.82rem', color: '#94a3b8' }}>
          No validation recommendations available.
        </p>
      </div>
    );
  }

  const getPriorityClass = (prio) => {
    switch (prio) {
      case 'CRITICAL': return 'prio-critical';
      case 'HIGH': return 'prio-high';
      case 'MEDIUM': return 'prio-medium';
      default: return 'prio-low';
    }
  };

  return (
    <div className="val-card">
      <div className="val-card-header">
        <h3>
          <Lightbulb size={16} color="#fbbf24" /> Actionable Next Steps ({recommendations.length})
        </h3>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
        {recommendations.map(r => (
          <div key={r.id} className="rec-item">
            <div className="rec-header-row">
              <span className={`rec-priority ${getPriorityClass(r.priority)}`}>
                {r.priority} PRIORITY
              </span>
              <span style={{ fontSize: '0.7rem', color: '#94a3b8', textTransform: 'capitalize' }}>
                {r.recommendation_type.replace('_', ' ')}
              </span>
            </div>
            <p style={{ margin: '0.2rem 0', color: '#f8fafc', fontSize: '0.8rem', fontWeight: 500 }}>
              {r.description}
            </p>
            {r.related_service_id && (
              <span style={{ fontSize: '0.7rem', color: '#0ea5e9' }}>
                Target Service: <strong>{r.related_service_id}</strong>
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
