import React from 'react';
import { AlertCircle, ArrowRight, CheckCircle2, ShieldAlert, Zap } from 'lucide-react';

export default function SimulationTimeline({
  timelineSteps = [],
  currentStep,
  onSelectStep
}) {
  if (!timelineSteps || timelineSteps.length === 0) {
    return (
      <div style={{ textAlign: 'center', color: '#64748b', padding: '2rem 1rem', fontSize: '0.85rem' }}>
        No simulation timeline recorded. Run the scenario to generate step-by-step failure propagation and recovery events.
      </div>
    );
  }

  // Flatten all events with their step context
  const allEvents = [];
  timelineSteps.forEach(step => {
    (step.events || []).forEach(ev => {
      allEvents.push({
        ...ev,
        step_number: step.step_number
      });
    });
  });

  return (
    <div className="timeline-event-list">
      {allEvents.map((ev, idx) => {
        const isCurrent = ev.step_number === currentStep;
        const eventType = ev.event_type || 'EVENT';

        return (
          <div
            key={idx}
            className={`timeline-event-card ${eventType} ${isCurrent ? 'current-step' : ''}`}
            onClick={() => onSelectStep && onSelectStep(ev.step_number)}
            style={{ cursor: 'pointer' }}
          >
            <div className="event-header">
              <span className="event-type-badge">
                Step {ev.step_number} • {eventType.replace('_', ' ')}
              </span>
              <span style={{ color: '#94a3b8', fontSize: '0.72rem', fontWeight: 600 }}>
                {ev.service_id}
              </span>
            </div>

            <div className="event-desc">
              {ev.description || JSON.stringify(ev.data || {})}
            </div>

            {/* Event details if present */}
            {ev.data && (
              <div style={{ display: 'flex', gap: '0.6rem', flexWrap: 'wrap', fontSize: '0.72rem', color: '#94a3b8', marginTop: '0.2rem' }}>
                {ev.data.combined_risk !== undefined && (
                  <span>Risk: <b style={{ color: '#f8fafc' }}>{ev.data.combined_risk}%</b></span>
                )}
                {ev.data.new_health && (
                  <span>Health: <b style={{ color: '#f8fafc' }}>{ev.data.new_health}</b></span>
                )}
                {ev.data.upstream_services && ev.data.upstream_services.length > 0 && (
                  <span>Upstream: <b style={{ color: '#cbd5e1' }}>{ev.data.upstream_services.join(', ')}</b></span>
                )}
              </div>
            )}
          </div>
        );
      })}

      {allEvents.length === 0 && (
        <div style={{ textAlign: 'center', color: '#64748b', padding: '1.5rem', fontSize: '0.85rem' }}>
          Simulation completed with 0 failure propagation events. The blast radius was contained.
        </div>
      )}
    </div>
  );
}
