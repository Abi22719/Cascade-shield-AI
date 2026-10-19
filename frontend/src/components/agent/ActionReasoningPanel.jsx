import React from 'react';
import { HelpCircle, BrainCircuit, CheckCircle2, AlertOctagon, TrendingUp } from 'lucide-react';

export default function ActionReasoningPanel({ 
  session, 
  unresolvedQuestions = [], 
  latestAction, 
  config 
}) {
  const stoppingReason = session?.stopping_reason;
  const isStopped = session?.status === 'COMPLETED' || session?.status === 'STOPPED';

  return (
    <div className="agent-panel">
      <div className="panel-title">
        <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <BrainCircuit size={16} color="#a855f7" />
          <span>Explainable Reasoning & Unresolved Questions</span>
        </span>
        {isStopped && (
          <span className="badge badge-success" style={{ fontSize: '0.7rem' }}>Session Concluded</span>
        )}
      </div>

      {/* Stopping Rationale Banner */}
      {isStopped && (
        <div style={{ background: 'rgba(16, 185, 129, 0.1)', border: '1px solid #10b981', borderRadius: '8px', padding: '0.8rem', display: 'flex', gap: '8px' }}>
          <CheckCircle2 size={18} color="#10b981" style={{ flexShrink: 0, marginTop: '2px' }} />
          <div>
            <div style={{ fontWeight: 600, fontSize: '0.82rem', color: '#6ee7b7' }}>Stopping Condition Met</div>
            <div style={{ fontSize: '0.78rem', color: '#cbd5e1', marginTop: '2px' }}>{stoppingReason}</div>
          </div>
        </div>
      )}

      {/* Latest Step Reasoning */}
      {latestAction && (
        <div style={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '8px', padding: '0.85rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
            <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#38bdf8' }}>
              Step {latestAction.step_number} Decision Rationale
            </span>
            <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
              Utility: <strong style={{ color: '#38bdf8' }}>{latestAction.selection_score?.toFixed(3)}</strong>
            </span>
          </div>
          <p style={{ fontSize: '0.78rem', color: '#cbd5e1', margin: 0, lineHeight: 1.45 }}>
            {latestAction.selection_reason}
          </p>
        </div>
      )}

      {/* Unresolved Questions List */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.82rem', fontWeight: 600, color: '#f1f5f9', marginBottom: '0.5rem' }}>
          <HelpCircle size={14} color="#f59e0b" />
          <span>Current Unresolved Questions ({unresolvedQuestions.length})</span>
        </div>
        {unresolvedQuestions.length === 0 ? (
          <div style={{ fontSize: '0.78rem', color: '#10b981', background: 'rgba(16, 185, 129, 0.08)', padding: '0.6rem', borderRadius: '6px' }}>
            ✓ All primary investigation questions have been evaluated by executed diagnostic checks.
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
            {unresolvedQuestions.map((q, idx) => (
              <div key={idx} className="question-item">
                <span style={{ fontWeight: 700, opacity: 0.8 }}>Q{idx + 1}:</span>
                <span>{q}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Policy Weight Reference */}
      <div style={{ borderTop: '1px solid rgba(255, 255, 255, 0.05)', paddingTop: '0.6rem', fontSize: '0.72rem', color: '#64748b' }}>
        Scoring Policy: <strong>w_info={config?.weight_information_gain || 0.35}</strong>, <strong>w_rel={config?.weight_relevance || 0.30}</strong>, <strong>w_disc={config?.weight_hypothesis_discrimination || 0.20}</strong>, <strong>w_cost={config?.weight_cost || 0.10}</strong>, <strong>RepeatPenalty={config?.repeated_action_penalty || 0.70}</strong>.
      </div>
    </div>
  );
}
