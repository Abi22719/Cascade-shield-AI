import React, { useState, useEffect } from 'react';
import { X, Layers, ArrowRight, ShieldCheck, Flame } from 'lucide-react';
import { cascadeApi } from '../../services/cascadeApi';

export default function ScenarioComparisonModal({ onClose }) {
  const [scenarios, setScenarios] = useState([]);
  const [selectedIds, setSelectedIds] = useState([]);
  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isComparing, setIsComparing] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchScenarios() {
      try {
        setLoading(true);
        const res = await cascadeApi.getScenarios(1, 50);
        const list = res.items || [];
        setScenarios(list);
        if (list.length >= 2) {
          setSelectedIds([list[0].id, list[1].id]);
        } else if (list.length === 1) {
          setSelectedIds([list[0].id]);
        }
      } catch (err) {
        setError(err.message || 'Failed to load scenarios.');
      } finally {
        setLoading(false);
      }
    }
    fetchScenarios();
  }, []);

  const toggleSelect = (id) => {
    if (selectedIds.includes(id)) {
      setSelectedIds(selectedIds.filter(item => item !== id));
    } else {
      if (selectedIds.length >= 4) {
        alert('You can compare up to 4 scenarios simultaneously.');
        return;
      }
      setSelectedIds([...selectedIds, id]);
    }
  };

  const handleCompare = async () => {
    if (selectedIds.length === 0) {
      alert('Please select at least 1 scenario to compare.');
      return;
    }
    try {
      setIsComparing(true);
      const res = await cascadeApi.compareScenarios({ scenario_ids: selectedIds });
      setComparison(res);
    } catch (err) {
      alert('Error comparing scenarios: ' + err.message);
    } finally {
      setIsComparing(false);
    }
  };

  return (
    <div className="cascade-modal-overlay" onClick={onClose}>
      <div className="cascade-modal-content" style={{ maxWidth: '950px' }} onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Layers size={20} color="#8b5cf6" />
            <div>
              <h3>Scenario Comparative Blast Radius Matrix</h3>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Evaluate impact severity and blast radius divergence across saved cloud failure scenarios
              </span>
            </div>
          </div>
          <button className="modal-close-btn" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <div className="modal-body">
          {loading ? (
            <div style={{ padding: '30px', textAlign: 'center', color: 'var(--text-muted)' }}>
              Loading persisted simulation scenarios...
            </div>
          ) : scenarios.length === 0 ? (
            <div style={{ padding: '30px', textAlign: 'center', color: 'var(--text-muted)' }}>
              No saved scenarios found in the database. Run a simulation and click "Save Scenario & Outcome" first!
            </div>
          ) : (
            <>
              {/* Scenario Selector Chips */}
              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600, display: 'block', marginBottom: '6px' }}>
                  Select Scenarios to Compare (Up to 4):
                </label>
                <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                  {scenarios.map((scen) => {
                    const isChecked = selectedIds.includes(scen.id);
                    return (
                      <div
                        key={scen.id}
                        onClick={() => toggleSelect(scen.id)}
                        className={`preset-chip ${isChecked ? 'active' : ''}`}
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
                        {scen.scenario_name} ({scen.initial_service_id})
                      </div>
                    );
                  })}
                </div>

                <div style={{ marginTop: '10px' }}>
                  <button
                    type="button"
                    className="btn-predict"
                    style={{ background: '#7c3aed', padding: '8px 16px', display: 'inline-flex' }}
                    onClick={handleCompare}
                    disabled={isComparing || selectedIds.length === 0}
                  >
                    {isComparing ? 'Comparing...' : `Compare ${selectedIds.length} Selected Scenario${selectedIds.length > 1 ? 's' : ''}`}
                  </button>
                </div>
              </div>

              {/* Comparison Matrix Table */}
              {comparison && comparison.scenarios && (
                <div style={{ marginTop: '14px' }}>
                  {/* Analysis Notes */}
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
                          <th>Scenario Name</th>
                          <th>Root Service</th>
                          <th>Failure Type & Severity</th>
                          <th>Total Blast Radius</th>
                          <th>Direct / Indirect</th>
                          <th>High / Critical Risk</th>
                          <th>Max Risk Score</th>
                        </tr>
                      </thead>
                      <tbody>
                        {comparison.scenarios.map((scen, idx) => (
                          <tr key={idx}>
                            <td style={{ fontWeight: 600 }}>{scen.scenario_name}</td>
                            <td>{scen.initial_service_id}</td>
                            <td>
                              <span style={{ textTransform: 'capitalize' }}>
                                {scen.failure_type.replace(/_/g, ' ')}
                              </span>{' '}
                              <span style={{ fontSize: '0.72rem', color: scen.failure_severity === 'severe' ? '#ef4444' : '#f59e0b' }}>
                                ({scen.failure_severity})
                              </span>
                            </td>
                            <td style={{ fontWeight: 700, fontSize: '1rem', color: '#60a5fa' }}>
                              {scen.total_impacted} services
                            </td>
                            <td>{scen.direct_impact} / {scen.indirect_impact}</td>
                            <td>
                              <span style={{ color: '#f97316' }}>{scen.high_risk_count}</span> /{' '}
                              <span style={{ color: '#ef4444', fontWeight: 700 }}>{scen.critical_risk_count}</span>
                            </td>
                            <td style={{ fontWeight: 700, color: scen.max_risk_score >= 75 ? '#ef4444' : '#f97316' }}>
                              {scen.max_risk_score} pts
                            </td>
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
