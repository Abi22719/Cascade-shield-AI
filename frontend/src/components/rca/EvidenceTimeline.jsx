import React from 'react';
import { Clock, AlertCircle, AlertTriangle, Info, ShieldAlert } from 'lucide-react';

export default function EvidenceTimeline({ timelineEvents = [] }) {
  const getSeverityIcon = (sev) => {
    switch (sev?.toLowerCase()) {
      case 'critical':
        return <AlertTriangle size={15} color="#ef4444" />;
      case 'warning':
        return <AlertCircle size={15} color="#f59e0b" />;
      default:
        return <Info size={15} color="#3b82f6" />;
    }
  };

  return (
    <div className="rca-timeline-panel">
      <div className="panel-header" style={{ background: 'transparent', padding: '0 0 8px 0' }}>
        <h3>
          <Clock size={16} color="#3b82f6" />
          Chronological Evidence & Incident Progression Timeline ({timelineEvents.length})
        </h3>
        <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
          Earliest observed anomaly onset to downstream symptom emergence
        </span>
      </div>

      <div className="timeline-items-flow">
        {timelineEvents.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '24px', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
            No timestamped events recorded for this investigation window.
          </div>
        ) : (
          timelineEvents.map((evt, idx) => (
            <div key={idx} className={`timeline-item-row ${evt.severity}`}>
              <div style={{ marginTop: '2px' }}>
                {getSeverityIcon(evt.severity)}
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '3px', flex: 1 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontWeight: 600, color: 'var(--text-main)', fontSize: '0.82rem' }}>
                    {evt.service_name} ({evt.service_id})
                  </span>
                  <span style={{ fontSize: '0.7rem', color: '#60a5fa', fontFamily: 'monospace' }}>
                    {evt.timestamp_formatted}
                  </span>
                </div>

                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', lineHeight: 1.35 }}>
                  {evt.description}
                </div>

                <div style={{ display: 'flex', gap: '8px', fontSize: '0.68rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                  <span>Source: <b>{evt.source_module}</b></span>
                  <span>Type: <b>{evt.event_type}</b></span>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
