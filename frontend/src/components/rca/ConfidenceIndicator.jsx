import React from 'react';
import { HelpCircle, AlertCircle, CheckCircle } from 'lucide-react';

export default function ConfidenceIndicator({ candidate, explanation }) {
  if (!candidate) return null;

  const score = candidate.ranking_score;
  const confScore = candidate.confidence_score;
  const label = candidate.confidence_label;

  const getMeterColor = () => {
    if (score >= 75) return '#ef4444';
    if (score >= 50) return '#f59e0b';
    if (score >= 25) return '#3b82f6';
    return '#64748b';
  };

  return (
    <div style={{ background: 'var(--bg-hover)', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-sm)', padding: '14px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
        <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '6px' }}>
          <AlertCircle size={14} color="#8b5cf6" />
          Heuristic Confidence Assessment
        </span>
        <span style={{ fontSize: '0.8rem', fontWeight: 700, color: getMeterColor() }}>
          {label} ({(confScore * 100).toFixed(0)}%)
        </span>
      </div>

      <div className="candidate-score-bar-bg" style={{ height: '8px' }}>
        <div
          className="candidate-score-bar-fill"
          style={{ width: `${score}%`, background: getMeterColor() }}
        />
      </div>

      <div style={{ marginTop: '10px', fontSize: '0.75rem', color: 'var(--text-muted)', lineHeight: 1.4 }}>
        {explanation || candidate.explanation}
      </div>

      <div style={{ marginTop: '8px', fontSize: '0.7rem', color: '#94a3b8', fontStyle: 'italic', borderTop: '1px solid var(--border-color)', paddingTop: '6px' }}>
        * Note: Confidence is calibrated for decision support. Graph connectivity and temporal precedence are strong indicators, not absolute mathematical proof of causation.
      </div>
    </div>
  );
}
