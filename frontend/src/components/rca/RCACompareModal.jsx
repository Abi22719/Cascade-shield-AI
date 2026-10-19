import React, { useState, useEffect } from 'react';
import { X, Layers, ArrowRight, ShieldCheck, Flame } from 'lucide-react';
import { rcaApi } from '../../services/rcaApi';

export default function RCACompareModal({ onClose }) {
  const [incidents, setIncidents] = useState([]);
  const [selectedIds, setSelectedIds] = useState([]);
  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isComparing, setIsComparing] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchIncidents() {
      try {
        setLoading(true);
        const res = await rcaApi.getIncidents({ limit: 50 });
        const list = res.items || [];
        setIncidents(list);
        if (list.length >= 2) {
          setSelectedIds([list[0].id, list[1].id]);
        } else if (list.length === 1) {
          setSelectedIds([list[0].id]);
        }
      } catch (err) {
        setError(err.message || 'Failed to load investigations.');
      } finally {
        setLoading(false);
      }
    }
    fetchIncidents();
  }, []);

  const toggleSelect = (id) => {
    if (selectedIds.includes(id)) {
      setSelectedIds(selectedIds.filter(item => item !== id));
    } else {
      if (selectedIds.length >= 4) {
        alert('You can compare up to 4 investigations simultaneously.');
        return;
      }
      setSelectedIds([...selectedIds, id]);
    }
  };

  const handleCompare = async () => {
    if (selectedIds.length === 0) {
      alert('Please select at least 1 investigation to compare.');
      return;
    }
    try {
      setIsComparing(true);
      const res = await rcaApi.compareIncidents({ incident_ids: selectedIds });
      setComparison(res);
    } catch (err) {
      alert('Error comparing investigations: ' + err.message);
    } finally {
      setIsComparing(false);
    }
  };

  return (
    <div className="cascade-modal-overlay" onClick={onClose}>
      <div className="cascade-modal-content" style={{ maxWidth: '950px' }} onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Layers size={18} color="#8b5cf6" />
            <div>
              <h3>Investigation Comparative Analysis Matrix</h3>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Compare root cause attribution, ranking scores, and blast radius divergence across incidents
              </span>
            </div>
          </div>
          <button className="modal-close-btn" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <div className="modal-body">
          {loading ? (
            <div style={{ textAlign: 'center', padding: '30px', color: 'var(--text-muted)' }}>
              Loading persisted RCA investigations...
            </div>
          ) : incidents.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '30px', color: 'var(--text-muted)' }}>
              No saved RCA investigations found in the database. Run an investigation first!
            </div>
          ) : (
            <>
              {/* Incident Selector Chips */}
              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600, display: 'block', marginBottom: '6px' }}>
                  Select Investigations to Compare (Up to 4):
                </label>
                <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                  {incidents.map((inc) => {
                    const isChecked = selectedIds.includes(inc.id);
                    return (
                      <div
                        key={inc.id}
                        onClick={() => toggleSelect(inc.id)}
                        className={`rca-preset-btn ${isChecked ? 'active' : ''}`}
                        style={{
                          background: isChecked ? 'rgba(139, 92, 246, 0.2)' : undefined,
                          borderColor: isChecked ? '#8b5cf6' : undefined,
                          color: isChecked ? '#c4b5fd' : undefined
                        }}
                      >
                        <input
                          type="checkbox"
                          checked={isChecked}
                          onChange={() => {}}
                          style={{ marginRight: '6px' }}
                        />
                        {inc.title} ({inc.top_candidate || 'Inconclusive'})
                      </div>
                    );
                  })}
                </div>

                <div style={{ marginTop: '10px' }}>
                  <button
                    type="button"
                    className="btn-analyze"
                    style={{ padding: '8px 16px', display: 'inline-flex', width: 'auto' }}
                    onClick={handleCompare}
                    disabled={isComparing || selectedIds.length === 0}
                  >
                    {isComparing ? 'Comparing...' : `Compare ${selectedIds.length} Selected Investigation${selectedIds.length > 1 ? 's' : ''}`}
                  </button>
                </div>
              </div>

              {/* Comparison Matrix Table */}
              {comparison && comparison.comparisons && (
                <div style={{ marginTop: '14px' }}>
                  {comparison.comparative_analysis?.length > 0 && (
                    <div style={{ background: 'rgba(139, 92, 246, 0.1)', border: '1px solid rgba(139, 92, 246, 0.3)', padding: '10px 14px', borderRadius: 'var(--radius-sm)', fontSize: '0.8rem', color: '#c4b5fd', marginBottom: '12px' }}>
                      {comparison.comparative_analysis.map((note, i) => (
                        <div key={i}>• {note}</div>
                      ))}
                    </div>
                  )}

                  <div style={{ overflowX: 'auto' }}>
                    <table className="cascade-table">
                      <thead>
                        <tr>
                          <th>Investigation Title</th>
                          <th>Status</th>
                          <th>Affected Callers</th>
                          <th>Identified Primary Root Cause</th>
                          <th>Confidence Label</th>
                          <th>Ranking Score</th>
                          <th>Evidence Signals</th>
                        </tr>
                      </thead>
                      <tbody>
                        {comparison.comparisons.map((c, idx) => (
                          <tr key={idx}>
                            <td style={{ fontWeight: 600 }}>{c.title}</td>
                            <td>
                              <span className="confidence-pill" style={{ textTransform: 'uppercase' }}>
                                {c.status}
                              </span>
                            </td>
                            <td style={{ fontWeight: 700, color: '#60a5fa' }}>
                              {c.affected_services?.length || 0}
                            </td>
                            <td style={{ fontWeight: 700, color: '#f87171' }}>
                              {c.top_candidate}
                            </td>
                            <td>
                              <span className="confidence-pill moderate">
                                {c.confidence_label}
                              </span>
                            </td>
                            <td style={{ fontWeight: 700, color: c.ranking_score >= 75 ? '#ef4444' : '#f97316' }}>
                              {c.ranking_score} pts
                            </td>
                            <td>{c.evidence_count} items</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
