import React, { useState } from 'react';
import { X, Sparkles, Layers, Sliders, ShieldAlert, Check } from 'lucide-react';

export default function ScenarioBuilderModal({
  isOpen,
  onClose,
  onSubmit,
  simulationOptions,
  services = []
}) {
  const [activeTab, setActiveTab] = useState('preset'); // 'preset' | 'custom'

  // Form State
  const [name, setName] = useState('');
  const [category, setCategory] = useState('failure_propagation');
  const [description, setDescription] = useState('');
  
  // Failure Injection
  const [targetServiceIds, setTargetServiceIds] = useState(['srv-payment']);
  const [failureType, setFailureType] = useState('service_unavailable');
  const [severity, setSeverity] = useState('severe');
  const [startStep, setStartStep] = useState(1);
  const [durationSteps, setDurationSteps] = useState(4);

  // Propagation
  const [maxSteps, setMaxSteps] = useState(6);
  const [attenuationFactor, setAttenuationFactor] = useState(0.75);
  const [propagationThreshold, setPropagationThreshold] = useState(25.0);

  // Recovery
  const [recoveryMode, setRecoveryMode] = useState('gradual');
  const [recoveryStep, setRecoveryStep] = useState(4);
  const [recoveryRate, setRecoveryRate] = useState(0.4);

  if (!isOpen) return null;

  const presets = simulationOptions?.presets || [];

  const handleSelectPreset = (preset) => {
    setName(preset.name);
    setCategory(preset.category || 'failure_propagation');
    setDescription(preset.description || '');
    setTargetServiceIds(preset.target_services || ['srv-payment']);
    setFailureType(preset.failure_type || 'service_unavailable');
    setSeverity(preset.severity || 'severe');
    setRecoveryMode(preset.recovery_mode || 'gradual');
    setRecoveryStep(preset.recovery_step || 5);
    setActiveTab('custom');
  };

  const handleToggleService = (sid) => {
    if (targetServiceIds.includes(sid)) {
      if (targetServiceIds.length > 1) {
        setTargetServiceIds(targetServiceIds.filter(id => id !== sid));
      }
    } else {
      setTargetServiceIds([...targetServiceIds, sid]);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const payload = {
      name: name.trim() || 'Custom What-If Scenario',
      category,
      description: description.trim() || 'Simulated what-if cloud failure scenario.',
      config: {
        failures: [
          {
            target_service_ids: targetServiceIds,
            failure_type: failureType,
            severity,
            start_step: startStep,
            duration_steps: durationSteps
          }
        ],
        propagation: {
          max_steps: maxSteps,
          attenuation_factor: attenuationFactor,
          propagation_threshold: propagationThreshold
        },
        recovery: {
          recovery_mode: recoveryMode,
          recovery_step: recoveryStep,
          recovery_rate: recoveryRate
        }
      },
      source_data_type: 'digital_twin'
    };

    onSubmit(payload);
  };

  return (
    <div className="sim-modal-overlay">
      <div className="sim-modal-card">
        <div className="sim-modal-header">
          <h3>
            <Sparkles size={18} color="#8b5cf6" />
            <span>Create What-If Scenario</span>
          </h3>
          <button className="btn-sim-secondary" style={{ padding: '0.25rem 0.5rem' }} onClick={onClose}>
            <X size={16} />
          </button>
        </div>

        {/* Tab Switcher */}
        <div style={{ display: 'flex', borderBottom: '1px solid rgba(255, 255, 255, 0.08)', padding: '0 1.25rem' }}>
          <button
            className={`nav-tab-btn ${activeTab === 'preset' ? 'active' : ''}`}
            onClick={() => setActiveTab('preset')}
            style={{ padding: '0.75rem 1rem' }}
          >
            <Layers size={14} />
            <span>Predefined Presets</span>
          </button>
          <button
            className={`nav-tab-btn ${activeTab === 'custom' ? 'active' : ''}`}
            onClick={() => setActiveTab('custom')}
            style={{ padding: '0.75rem 1rem' }}
          >
            <Sliders size={14} />
            <span>Configuration Builder</span>
          </button>
        </div>

        <div className="sim-modal-body">
          {activeTab === 'preset' ? (
            <div>
              <p style={{ fontSize: '0.82rem', color: '#94a3b8', margin: '0 0 1rem 0' }}>
                Select an engineering failure scenario template to instantly configure the simulation engine:
              </p>
              <div className="preset-grid">
                {presets.map((p, idx) => (
                  <div key={idx} className="preset-card" onClick={() => handleSelectPreset(p)}>
                    <div className="preset-card-title">{p.name}</div>
                    <div className="preset-card-desc">{p.description}</div>
                    <div style={{ display: 'flex', gap: '0.4rem', marginTop: '0.4rem', fontSize: '0.72rem', color: '#c4b5fd' }}>
                      <span>Target: {p.target_services?.join(', ')}</span>
                      <span>•</span>
                      <span>{p.severity}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <form id="scenario-form" onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {/* Metadata */}
              <div className="sim-form-row">
                <div className="sim-form-group">
                  <label className="sim-form-label">Scenario Name *</label>
                  <input
                    type="text"
                    required
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="e.g. Payment Gateway Failure"
                    className="sim-form-input"
                  />
                </div>
                <div className="sim-form-group">
                  <label className="sim-form-label">Category</label>
                  <select value={category} onChange={(e) => setCategory(e.target.value)} className="sim-form-select">
                    <option value="failure_propagation">Failure Propagation</option>
                    <option value="latency_storm">Latency Storm</option>
                    <option value="database_starvation">Database Starvation</option>
                    <option value="recovery_test">Recovery Test</option>
                  </select>
                </div>
              </div>

              {/* Target Service Selection */}
              <div className="sim-form-group">
                <label className="sim-form-label">Target Service(s) to Fail</label>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', maxHeight: '110px', overflowY: 'auto' }}>
                  {services.map(s => {
                    const sid = s.id || s.service_id;
                    const isSelected = targetServiceIds.includes(sid);
                    return (
                      <button
                        type="button"
                        key={sid}
                        className="btn-sim-secondary"
                        onClick={() => handleToggleService(sid)}
                        style={{
                          fontSize: '0.75rem',
                          padding: '0.25rem 0.55rem',
                          borderColor: isSelected ? '#8b5cf6' : undefined,
                          backgroundColor: isSelected ? 'rgba(139, 92, 246, 0.25)' : undefined,
                          color: isSelected ? '#c4b5fd' : undefined
                        }}
                      >
                        {isSelected && <Check size={12} />}
                        <span>{s.name || sid}</span>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Failure Parameters */}
              <div className="sim-form-row">
                <div className="sim-form-group">
                  <label className="sim-form-label">Failure Mode</label>
                  <select value={failureType} onChange={(e) => setFailureType(e.target.value)} className="sim-form-select">
                    <option value="service_unavailable">Service Unavailable (100% outage)</option>
                    <option value="high_latency">High Latency Storm</option>
                    <option value="error_rate_surge">Error Rate Surge (5xx)</option>
                    <option value="cpu_saturation">CPU Saturation</option>
                    <option value="memory_exhaustion">Memory Exhaustion (OOM)</option>
                    <option value="database_starvation">Database Pool Starvation</option>
                  </select>
                </div>
                <div className="sim-form-group">
                  <label className="sim-form-label">Severity Level</label>
                  <select value={severity} onChange={(e) => setSeverity(e.target.value)} className="sim-form-select">
                    <option value="severe">Severe (100% Maximum Blast)</option>
                    <option value="moderate">Moderate (80% Blast)</option>
                    <option value="mild">Mild (50% Blast)</option>
                  </select>
                </div>
                <div className="sim-form-group">
                  <label className="sim-form-label">Duration (Steps)</label>
                  <input
                    type="number"
                    min={1}
                    max={15}
                    value={durationSteps}
                    onChange={(e) => setDurationSteps(parseInt(e.target.value, 10))}
                    className="sim-form-input"
                  />
                </div>
              </div>

              {/* Propagation & Recovery Controls */}
              <div className="sim-form-row">
                <div className="sim-form-group">
                  <label className="sim-form-label">Total Steps (1-20)</label>
                  <input
                    type="number"
                    min={1}
                    max={20}
                    value={maxSteps}
                    onChange={(e) => setMaxSteps(parseInt(e.target.value, 10))}
                    className="sim-form-input"
                  />
                </div>
                <div className="sim-form-group">
                  <label className="sim-form-label">Attenuation Factor (0.1 - 1.0)</label>
                  <input
                    type="number"
                    step="0.05"
                    min={0.1}
                    max={1.0}
                    value={attenuationFactor}
                    onChange={(e) => setAttenuationFactor(parseFloat(e.target.value))}
                    className="sim-form-input"
                  />
                </div>
                <div className="sim-form-group">
                  <label className="sim-form-label">Recovery Mode</label>
                  <select value={recoveryMode} onChange={(e) => setRecoveryMode(e.target.value)} className="sim-form-select">
                    <option value="gradual">Gradual Metric Convergence</option>
                    <option value="immediate">Immediate Restoration</option>
                    <option value="none">No Recovery (Persistent)</option>
                  </select>
                </div>
                <div className="sim-form-group">
                  <label className="sim-form-label">Recovery Step</label>
                  <input
                    type="number"
                    min={1}
                    max={maxSteps}
                    value={recoveryStep}
                    onChange={(e) => setRecoveryStep(parseInt(e.target.value, 10))}
                    className="sim-form-input"
                    disabled={recoveryMode === 'none'}
                  />
                </div>
              </div>
            </form>
          )}
        </div>

        <div className="sim-modal-footer">
          <button className="btn-sim-secondary" onClick={onClose}>
            Cancel
          </button>
          {activeTab === 'custom' && (
            <button className="btn-sim-primary" type="submit" form="scenario-form">
              Save & Load Scenario
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
