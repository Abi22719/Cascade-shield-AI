import React from 'react';
import { Bot, CheckCircle2, AlertTriangle, Clock, ShieldAlert, Sparkles, Layers } from 'lucide-react';

export default function AgentStatusCard({ session, targetService, config }) {
  const status = session?.status || 'IDLE';
  const totalSteps = session?.total_steps || 0;
  const maxActions = config?.max_actions || 5;
  const budgetRemaining = Math.max(0, maxActions - totalSteps);
  const completeness = session?.evidence_completeness !== undefined 
    ? Math.round(session.evidence_completeness * 100) 
    : 0;

  const getStatusBadge = () => {
    switch (status) {
      case 'RUNNING':
        return <span className="badge badge-info" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}><span className="pulse-dot"></span> Active Loop</span>;
      case 'COMPLETED':
        return <span className="badge badge-success" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}><CheckCircle2 size={13} /> Completed</span>;
      case 'STOPPED':
        return <span className="badge badge-warning" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}><Clock size={13} /> Stopped</span>;
      case 'FAILED':
        return <span className="badge badge-critical" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}><AlertTriangle size={13} /> Failed</span>;
      default:
        return <span className="badge" style={{ background: '#334155', color: '#94a3b8' }}>Ready / Idle</span>;
    }
  };

  return (
    <div className="agent-kpi-grid">
      <div className={`agent-kpi-card status-${status.toLowerCase()}`}>
        <div className="kpi-label">
          <span>Agent Lifecycle State</span>
          <Bot size={15} color="#38bdf8" />
        </div>
        <div className="kpi-value" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {getStatusBadge()}
        </div>
        <div className="kpi-meta">
          Policy v{session?.policy_version || '1.0.0'} &bull; Session ID: {session?.id ? session.id.substring(0, 8) + '...' : 'None'}
        </div>
      </div>

      <div className="agent-kpi-card">
        <div className="kpi-label">
          <span>Target Cloud Service</span>
          <ShieldAlert size={15} color="#f59e0b" />
        </div>
        <div className="kpi-value" style={{ color: '#f8fafc', fontSize: '1.25rem' }}>
          {targetService || session?.target_service_id || 'Auto-Detected'}
        </div>
        <div className="kpi-meta">
          Suspected root cause focus area
        </div>
      </div>

      <div className="agent-kpi-card">
        <div className="kpi-label">
          <span>Action Steps Progress</span>
          <Layers size={15} color="#a855f7" />
        </div>
        <div className="kpi-value">
          {totalSteps} <span style={{ fontSize: '0.9rem', color: '#64748b', fontWeight: 400 }}>/ {maxActions} budget</span>
        </div>
        <div style={{ background: '#0f172a', height: '6px', borderRadius: '3px', overflow: 'hidden', marginTop: '4px' }}>
          <div 
            style={{ 
              background: 'linear-gradient(90deg, #0ea5e9, #10b981)', 
              height: '100%', 
              width: `${Math.min(100, (totalSteps / maxActions) * 100)}%`,
              transition: 'width 0.3s ease'
            }} 
          />
        </div>
      </div>

      <div className="agent-kpi-card">
        <div className="kpi-label">
          <span>Evidence Completeness</span>
          <Sparkles size={15} color="#10b981" />
        </div>
        <div className="kpi-value" style={{ color: completeness >= 75 ? '#34d399' : (completeness >= 40 ? '#fbbf24' : '#94a3b8') }}>
          {completeness}%
        </div>
        <div className="kpi-meta">
          {budgetRemaining > 0 ? `${budgetRemaining} actions remaining in budget` : 'Budget exhausted'}
        </div>
      </div>
    </div>
  );
}
