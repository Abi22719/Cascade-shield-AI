import React, { useState } from 'react';
import { Award, ChevronDown, ChevronUp, Check, X, GitFork, Crosshair } from 'lucide-react';

export default function RootCauseRanking({
  candidates = [],
  selectedCandidateId,
  onSelectCandidate,
  onViewPaths
}) {
  const [expandedId, setExpandedId] = useState(candidates.length > 0 ? candidates[0].service_id : null);

  const toggleExpand = (id) => {
    setExpandedId(prev => (prev === id ? null : id));
  };

  const getScoreColor = (score) => {
    if (score >= 75) return '#ef4444';
    if (score >= 50) return '#f59e0b';
    if (score >= 25) return '#3b82f6';
    return '#64748b';
  };

  const getConfidenceClass = (label) => {
    const l = label?.toLowerCase() || '';
    if (l.includes('strong')) return 'confidence-pill strong';
    if (l.includes('moderate')) return 'confidence-pill moderate';
    if (l.includes('weak')) return 'confidence-pill weak';
    return 'confidence-pill insufficient';
  };

  return (
    <div className="rca-candidates-panel">
      <div className="panel-header">
        <h3>
          <Award size={16} color="#8b5cf6" />
          Ranked Root Cause Candidates ({candidates.length})
        </h3>
        <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
          Multi-factor heuristic ranking
        </span>
      </div>

      <div className="candidates-list">
        {candidates.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '30px', color: 'var(--text-muted)' }}>
            No candidate root causes identified. Select affected services and run an investigation.
          </div>
        ) : (
          candidates.map((c) => {
            const isExpanded = expandedId === c.service_id;
            const isSelected = selectedCandidateId === c.service_id;

            return (
              <div
                key={c.service_id}
                className={`candidate-card ${c.rank === 1 ? 'top-rank' : ''}`}
                style={{
                  borderColor: isSelected ? '#8b5cf6' : undefined,
                  boxShadow: isSelected ? '0 0 10px rgba(139, 92, 246, 0.25)' : undefined
                }}
              >
                <div className="candidate-header">
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span className="candidate-rank-badge">#{c.rank}</span>
                    <div>
                      <div style={{ fontWeight: 600, color: 'var(--text-main)', fontSize: '0.9rem' }}>
                        {c.service_name}
                      </div>
                      <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                        {c.service_id}
                      </div>
                    </div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span className={getConfidenceClass(c.confidence_label)}>
                      {c.confidence_label}
                    </span>
                    <button
                      type="button"
                      className="timeline-btn"
                      style={{ padding: '4px' }}
                      onClick={() => toggleExpand(c.service_id)}
                      title="Toggle Details"
                    >
                      {isExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                    </button>
                  </div>
                </div>

                {/* Score Bar */}
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem' }}>
                    <span style={{ color: 'var(--text-muted)' }}>Ranking Score:</span>
                    <b style={{ color: getScoreColor(c.ranking_score) }}>{c.ranking_score} / 100</b>
                  </div>
                  <div className="candidate-score-bar-bg">
                    <div
                      className="candidate-score-bar-fill"
                      style={{
                        width: `${c.ranking_score}%`,
                        background: getScoreColor(c.ranking_score)
                      }}
                    />
                  </div>
                </div>

                {/* Quick Evidence Counters */}
                <div style={{ display: 'flex', gap: '8px', fontSize: '0.72rem' }}>
                  <span style={{ color: '#34d399', display: 'flex', alignItems: 'center', gap: '2px' }}>
                    <Check size={12} /> {c.evidence_for?.length || 0} Supporting
                  </span>
                  <span style={{ color: '#f87171', display: 'flex', alignItems: 'center', gap: '2px' }}>
                    <X size={12} /> {c.evidence_against?.length || 0} Contradictory
                  </span>
                  <button
                    type="button"
                    style={{ marginLeft: 'auto', background: 'transparent', border: 'none', color: '#c4b5fd', cursor: 'pointer', fontSize: '0.72rem', display: 'flex', alignItems: 'center', gap: '3px' }}
                    onClick={() => onSelectCandidate && onSelectCandidate(c.service_id)}
                  >
                    <Crosshair size={12} /> Focus Graph
                  </button>
                </div>

                {/* Expanded Accordion Details */}
                {isExpanded && (
                  <div style={{ marginTop: '8px', borderTop: '1px solid var(--border-color)', paddingTop: '10px', display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.75rem' }}>
                    <div style={{ color: 'var(--text-main)', lineHeight: 1.4 }}>
                      {c.explanation}
                    </div>

                    {c.evidence_for?.length > 0 && (
                      <div>
                        <b style={{ color: '#34d399' }}>Supporting Factors:</b>
                        <ul style={{ paddingLeft: '16px', margin: '4px 0', color: 'var(--text-muted)' }}>
                          {c.evidence_for.map((item, idx) => (
                            <li key={idx}>{item}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {c.evidence_against?.length > 0 && (
                      <div>
                        <b style={{ color: '#f87171' }}>Contradictory / Mitigating Factors:</b>
                        <ul style={{ paddingLeft: '16px', margin: '4px 0', color: 'var(--text-muted)' }}>
                          {c.evidence_against.map((item, idx) => (
                            <li key={idx}>{item}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {c.supporting_paths?.length > 0 && (
                      <div style={{ marginTop: '4px' }}>
                        <button
                          type="button"
                          className="timeline-btn"
                          style={{ width: '100%', justifyContent: 'center' }}
                          onClick={() => onViewPaths && onViewPaths(c)}
                        >
                          <GitFork size={13} />
                          Inspect Failure Paths ({c.supporting_paths.length})
                        </button>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
