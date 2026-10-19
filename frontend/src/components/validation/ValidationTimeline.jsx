import React from 'react';
import { Clock, CheckCircle2, AlertTriangle, XCircle, Info } from 'lucide-react';

export default function ValidationTimeline({ timeline }) {
  if (!timeline || timeline.length === 0) {
    return (
      <div className="val-card">
        <div className="val-card-header">
          <h3>Validation Event Timeline</h3>
        </div>
        <p style={{ fontSize: '0.82rem', color: '#94a3b8' }}>
          No timeline records available for this run.
        </p>
      </div>
    );
  }

  const getItemClass = (status) => {
    if (status === 'PASS') return 'item-pass';
    if (status === 'FAIL') return 'item-fail';
    return '';
  };

  return (
    <div className="val-card">
      <div className="val-card-header">
        <h3>
          <Clock size={16} color="#0ea5e9" /> Validation Timeline ({timeline.length} Events)
        </h3>
      </div>

      <div className="timeline-list">
        {timeline.map((item, idx) => (
          <div key={idx} className={`timeline-item ${getItemClass(item.status)}`}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontWeight: 600, color: '#f8fafc' }}>
                {item.title}
              </span>
              <span style={{ fontSize: '0.7rem', color: '#64748b' }}>
                Step +{item.step}
              </span>
            </div>
            <p style={{ margin: 0, color: '#cbd5e1', fontSize: '0.74rem' }}>
              {item.description}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
