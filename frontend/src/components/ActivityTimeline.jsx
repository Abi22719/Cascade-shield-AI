import React from 'react';
import { Clock, Activity, RefreshCw } from 'lucide-react';

export default function ActivityTimeline({ activities = [], loading, onRefresh }) {
  const formatTime = (ts) => {
    if (!ts) return 'Just now';
    try {
      const d = new Date(ts);
      return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    } catch {
      return 'Recent';
    }
  };

  return (
    <div className="db-panel">
      <div className="db-panel-header">
        <div className="db-panel-title">
          <Activity size={18} color="#38bdf8" />
          <span>Cross-Module Activity Stream</span>
        </div>
        {onRefresh && (
          <button 
            className="btn btn-secondary" 
            style={{ padding: '0.3rem 0.6rem', fontSize: '0.75rem' }} 
            onClick={onRefresh}
            title="Refresh stream"
          >
            <RefreshCw size={12} className={loading ? "animate-spin" : ""} />
            <span>Sync</span>
          </button>
        )}
      </div>

      {activities.length === 0 ? (
        <p style={{ color: '#94a3b8', fontSize: '0.84rem' }}>
          No system events recorded yet. Perform actions across modules to see real-time milestone events.
        </p>
      ) : (
        <div className="activity-stream">
          {activities.map((act) => (
            <div key={act.id} className="activity-item">
              <div className="activity-icon-col">
                <div className="activity-dot" />
                <div className="activity-line" />
              </div>
              <div className="activity-content">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span className="activity-event-type">{act.event_type.replace(/_/g, ' ')}</span>
                  <span className="activity-time">{formatTime(act.created_at)}</span>
                </div>
                <div className="activity-desc">{act.description}</div>
                <span style={{ fontSize: '0.68rem', color: '#64748b' }}>
                  Source: {act.source_module}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
