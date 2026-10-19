import React, { useState } from 'react';
import { X, Sparkles, Sliders, Layers, Plus, Trash2 } from 'lucide-react';

export default function RecoveryPlanBuilder({
  isOpen,
  onClose,
  onGeneratePlans,
  onCreateCustomPlan,
  services = [],
  options
}) {
  const [activeTab, setActiveTab] = useState('generate'); // 'generate' | 'custom'

  // Generator form
  const [selectedServiceId, setSelectedServiceId] = useState('srv-payment');
  const [optimizationGoal, setOptimizationGoal] = useState('balanced');

  // Custom form
  const [customName, setCustomName] = useState('');
  const [customDesc, setCustomDesc] = useState('');
  const [customStrategy, setCustomStrategy] = useState('balanced');
  const [customActions, setCustomActions] = useState([
    {
      action_type: 'restart_service',
      target_service_id: 'srv-payment',
      action_order: 1,
      estimated_duration: 1,
      reversibility: 'fully_reversible'
    }
  ]);

  if (!isOpen) return null;

  const handleAddAction = () => {
    setCustomActions([
      ...customActions,
      {
        action_type: 'scale_up',
        target_service_id: selectedServiceId,
        action_order: customActions.length + 1,
        estimated_duration: 1,
        reversibility: 'fully_reversible'
      }
    ]);
  };

  const handleRemoveAction = (idx) => {
    setCustomActions(customActions.filter((_, i) => i !== idx));
  };

  const handleActionChange = (idx, field, value) => {
    const updated = [...customActions];
    updated[idx][field] = value;
    setCustomActions(updated);
  };

  const handleGenerateSubmit = (e) => {
    e.preventDefault();
    onGeneratePlans({
      target_service_id: selectedServiceId,
      optimization_goal: optimizationGoal
    });
  };

  const handleCustomSubmit = (e) => {
    e.preventDefault();
    onCreateCustomPlan({
      plan_name: customName.trim() || 'Custom Recovery Plan',
      description: customDesc.trim() || 'Custom operator recovery sequence.',
      strategy_type: customStrategy,
      actions: customActions
    });
  };

  const actionTypes = options?.action_types || [
    { id: 'restart_service', name: 'Restart Service' },
    { id: 'rollback_deployment', name: 'Rollback Deployment' },
    { id: 'traffic_reroute', name: 'Traffic Reroute' },
    { id: 'scale_up', name: 'Scale Up' },
    { id: 'isolate_dependency', name: 'Circuit Breaker Isolation' },
    { id: 'restore_database', name: 'Database Restore' },
    { id: 'retry_request', name: 'Retry Requests' },
    { id: 'wait_auto_recovery', name: 'Wait Auto-Recovery' }
  ];

  return (
    <div className="sim-modal-overlay">
      <div className="sim-modal-card" style={{ maxWidth: '850px' }}>
        <div className="sim-modal-header">
          <h3>
            <Sparkles size={18} color="#10b981" />
            <span>Generate or Author Recovery Plans</span>
          </h3>
          <button className="btn-rec-secondary" style={{ padding: '0.25rem 0.5rem' }} onClick={onClose}>
            <X size={16} />
          </button>
        </div>

        {/* Tab switcher */}
        <div style={{ display: 'flex', borderBottom: '1px solid rgba(255, 255, 255, 0.08)', padding: '0 1.25rem' }}>
          <button
            className={`nav-tab-btn ${activeTab === 'generate' ? 'active' : ''}`}
            onClick={() => setActiveTab('generate')}
            style={{ padding: '0.75rem 1rem' }}
          >
            <Sparkles size={14} />
            <span>AI Multi-Strategy Generator</span>
          </button>
          <button
            className={`nav-tab-btn ${activeTab === 'custom' ? 'active' : ''}`}
            onClick={() => setActiveTab('custom')}
            style={{ padding: '0.75rem 1rem' }}
          >
            <Sliders size={14} />
            <span>Custom Action Sequencer</span>
          </button>
        </div>

        <div className="sim-modal-body">
          {activeTab === 'generate' ? (
            <form id="gen-form" onSubmit={handleGenerateSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.1rem' }}>
              <p style={{ fontSize: '0.82rem', color: '#94a3b8', margin: 0 }}>
                CascadeShield AI automatically generates 4 distinct candidate recovery strategies 
                (<b>Lowest-Risk</b>, <b>Fastest-Recovery</b>, <b>Lowest-Cost</b>, and <b>Balanced</b>) based on 
                service dependencies and anomaly evidence:
              </p>

              <div className="sim-form-row">
                <div className="sim-form-group">
                  <label className="sim-form-label">Target Degraded Service *</label>
                  <select
                    value={selectedServiceId}
                    onChange={(e) => setSelectedServiceId(e.target.value)}
                    className="sim-form-select"
                  >
                    {services.map(s => (
                      <option key={s.id} value={s.id}>
                        {s.name} ({s.id}) - {s.health_status}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="sim-form-group">
                  <label className="sim-form-label">Optimization Priority</label>
                  <select
                    value={optimizationGoal}
                    onChange={(e) => setOptimizationGoal(e.target.value)}
                    className="sim-form-select"
                  >
                    <option value="balanced">Risk-Aware Balanced (Recommended)</option>
                    <option value="lowest_risk">Lowest-Risk / Safe Circuit Breakers</option>
                    <option value="fastest_recovery">Fastest Recovery Time</option>
                    <option value="lowest_cost">Lowest Resource Cost</option>
                  </select>
                </div>
              </div>
            </form>
          ) : (
            <form id="custom-form" onSubmit={handleCustomSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div className="sim-form-row">
                <div className="sim-form-group">
                  <label className="sim-form-label">Plan Name *</label>
                  <input
                    type="text"
                    required
                    value={customName}
                    onChange={(e) => setCustomName(e.target.value)}
                    placeholder="e.g. Rolling Failover & Scaling"
                    className="sim-form-input"
                  />
                </div>
                <div className="sim-form-group">
                  <label className="sim-form-label">Strategy Category</label>
                  <select
                    value={customStrategy}
                    onChange={(e) => setCustomStrategy(e.target.value)}
                    className="sim-form-select"
                  >
                    <option value="balanced">Balanced</option>
                    <option value="lowest_risk">Lowest Risk</option>
                    <option value="fastest_recovery">Fastest Recovery</option>
                    <option value="lowest_cost">Lowest Cost</option>
                    <option value="custom">Custom</option>
                  </select>
                </div>
              </div>

              {/* Action Builder Sequence */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span className="sim-form-label">Action Sequence:</span>
                  <button type="button" className="btn-rec-secondary" onClick={handleAddAction} style={{ fontSize: '0.72rem', padding: '0.2rem 0.5rem' }}>
                    <Plus size={12} />
                    <span>Add Step</span>
                  </button>
                </div>

                {customActions.map((act, idx) => (
                  <div
                    key={idx}
                    style={{
                      display: 'grid',
                      gridTemplateColumns: '1.2fr 1fr 0.8fr 1fr auto',
                      gap: '0.5rem',
                      alignItems: 'center',
                      background: 'rgba(30, 41, 59, 0.4)',
                      padding: '0.5rem',
                      borderRadius: '5px'
                    }}
                  >
                    <select
                      value={act.action_type}
                      onChange={(e) => handleActionChange(idx, 'action_type', e.target.value)}
                      className="sim-form-select"
                    >
                      {actionTypes.map(at => (
                        <option key={at.id} value={at.id}>{at.name}</option>
                      ))}
                    </select>

                    <select
                      value={act.target_service_id || 'srv-payment'}
                      onChange={(e) => handleActionChange(idx, 'target_service_id', e.target.value)}
                      className="sim-form-select"
                    >
                      {services.map(s => (
                        <option key={s.id} value={s.id}>{s.name}</option>
                      ))}
                    </select>

                    <input
                      type="number"
                      min={1}
                      max={10}
                      value={act.estimated_duration}
                      onChange={(e) => handleActionChange(idx, 'estimated_duration', parseInt(e.target.value, 10))}
                      placeholder="Steps"
                      className="sim-form-input"
                    />

                    <select
                      value={act.reversibility}
                      onChange={(e) => handleActionChange(idx, 'reversibility', e.target.value)}
                      className="sim-form-select"
                    >
                      <option value="fully_reversible">Fully Reversible</option>
                      <option value="partially_reversible">Partially Reversible</option>
                      <option value="irreversible">Irreversible</option>
                    </select>

                    {customActions.length > 1 && (
                      <button
                        type="button"
                        onClick={() => handleRemoveAction(idx)}
                        style={{ background: 'none', border: 'none', color: '#f87171', cursor: 'pointer' }}
                      >
                        <Trash2 size={14} />
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </form>
          )}
        </div>

        <div className="sim-modal-footer">
          <button className="btn-rec-secondary" onClick={onClose}>
            Cancel
          </button>
          {activeTab === 'generate' ? (
            <button className="btn-rec-primary" type="submit" form="gen-form">
              Generate 4 Candidate Plans
            </button>
          ) : (
            <button className="btn-rec-primary" type="submit" form="custom-form">
              Validate & Save Custom Plan
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
