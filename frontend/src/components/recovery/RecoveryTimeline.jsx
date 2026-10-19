import React from 'react';
import { Clock, CheckCircle2, AlertTriangle, ShieldCheck, RotateCcw } from 'lucide-react';

export default function RecoveryTimeline({ events = [], outcome }) {
  if (!events || events.length === 0) {
    return (
      <div style={{ textAlign: 'center', color: '#64748b', padding: '2rem 1rem', fontSize: '0.85rem' }}>
        No simulation execution events recorded. Click "Simulate Recovery" to test this plan in the virtual sandbox.
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
      {outcome && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          padding: '0.65rem 0.9rem',
          borderRadius: '6px',
          background: outcome === 'SUCCESSFUL_RECOVERY' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)',
          border: outcome === 'SUCCESSFUL_RECOVERY' ? '1px solid rgba(16, 185, 129, 0.3)' : '1px solid rgba(239, 68, 68, 0.3)',
          color: outcome === 'SUCCESSFUL_RECOVERY' ? '#6ee7b7' : '#fca5a5',
          fontSize: '0.82rem',
          fontWeight: 700
        }}>
          <CheckCircle2 size={16} />
          <span>Simulation Outcome: {outcome.replace('_', ' ')}</span>
        </div>
      )}

      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.55rem' }}>
        {events.map((ev, idx) => {
          const evType = ev.event_type || 'EVENT';
          return (
            <div key={idx} className={`rec-event-card ${evType}`}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontWeight: 700, fontSize: '0.7rem', color: '#6ee7b7', textTransform: 'uppercase' }}>
                  Step {ev.step || ev.timestamp_or_step || 1} • {evType.replace('_', ' ')}
                </span>
                <span style={{ fontSize: '0.7rem', color: '#64748b' }}>Simulated</span>
              </div>
              <div style={{ color: '#e2e8f0', lineHeight: 1.35 }}>
                {ev.description}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
