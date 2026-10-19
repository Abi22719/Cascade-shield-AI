import React from 'react';
import { HelpCircle, Check, X, Search } from 'lucide-react';

export default function AlternativeHypotheses({ hypotheses = [] }) {
  if (!hypotheses || hypotheses.length === 0) return null;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <HelpCircle size={16} color="#8b5cf6" />
        <h3 style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-main)', margin: 0 }}>
          Competing Alternative Hypotheses ({hypotheses.length})
        </h3>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {hypotheses.map((hyp) => (
          <div key={hyp.hypothesis_id} className="hypothesis-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontWeight: 600, color: '#c4b5fd', fontSize: '0.85rem' }}>
                {hyp.hypothesis_title}
              </span>
              <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                {hyp.related_services?.length || 0} Related Services
              </span>
            </div>

            <div style={{ fontSize: '0.75rem', color: 'var(--text-main)', lineHeight: 1.4 }}>
              {hyp.plausibility_reason}
            </div>

            {hyp.supporting_evidence?.length > 0 && (
              <div style={{ fontSize: '0.72rem' }}>
                <span style={{ color: '#34d399', fontWeight: 600 }}>Supporting Signals:</span>
                <ul style={{ paddingLeft: '16px', margin: '2px 0', color: 'var(--text-muted)' }}>
                  {hyp.supporting_evidence.map((s, i) => (
                    <li key={i}>{s}</li>
                  ))}
                </ul>
              </div>
            )}

            {hyp.missing_information?.length > 0 && (
              <div style={{ fontSize: '0.72rem', background: 'rgba(0,0,0,0.2)', padding: '6px 10px', borderRadius: '4px' }}>
                <span style={{ color: '#60a5fa', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <Search size={11} /> Required Diagnostic Verification:
                </span>
                <span style={{ color: 'var(--text-muted)' }}>
                  {hyp.missing_information.join(' ')}
                </span>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
