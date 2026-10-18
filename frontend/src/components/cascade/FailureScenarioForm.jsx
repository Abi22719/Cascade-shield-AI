import React, { useState } from 'react';
import { Play, PlayCircle, Save, Sliders, Zap, ShieldAlert } from 'lucide-react';

const FAILURE_TYPES = [
  { id: 'service_unavailable', label: 'Service Unavailable (Crash/Outage)' },
  { id: 'latency_spike', label: 'Latency Spike (Upstream Bottleneck)' },
  { id: 'error_rate_surge', label: 'Error Rate Surge (5xx Fault Storm)' },
  { id: 'cpu_exhaustion', label: 'CPU Exhaustion (Compute Starvation)' },
  { id: 'memory_leak', label: 'Memory Leak (OOM Hazard)' },
];

export default function FailureScenarioForm({
  services,
  selectedServiceId,
  setSelectedServiceId,
  failureType,
  setFailureType,
  severity,
  setSeverity,
  steps,
  setSteps,
  attenuation,
  setAttenuation,
  onPredict,
  onSimulate,
  onSaveScenario,
  loading,
  hasPrediction
}) {
  const [scenarioName, setScenarioName] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [showSaveInput, setShowSaveInput] = useState(false);

  const handleSave = async () => {
    if (!scenarioName.trim()) {
      alert('Please enter a scenario name.');
      return;
    }
    setIsSaving(true);
    try {
      await onSaveScenario(scenarioName.trim());
      setScenarioName('');
      setShowSaveInput(false);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="scenario-form-card">
      <h3>
        <Sliders size={18} color="#3b82f6" />
        Failure Scenario Configuration
      </h3>

      {/* Target Service Selection */}
      <div className="form-group">
        <label>Root Failing / Degraded Service</label>
        <select
          className="form-select"
          value={selectedServiceId}
          onChange={(e) => setSelectedServiceId(e.target.value)}
          disabled={loading}
        >
          {services.map((s) => (
            <option key={s.id} value={s.id}>
              {s.name} ({s.id}) · {s.service_type} · {s.health_status}
            </option>
          ))}
        </select>
      </div>

      {/* Failure Mechanism */}
      <div className="form-group">
        <label>Failure Propagation Type</label>
        <select
          className="form-select"
          value={failureType}
          onChange={(e) => setFailureType(e.target.value)}
          disabled={loading}
        >
          {FAILURE_TYPES.map((t) => (
            <option key={t.id} value={t.id}>
              {t.label}
            </option>
          ))}
        </select>
      </div>

      {/* Severity Pill Toggle */}
      <div className="form-group">
        <label>Failure Severity Level</label>
        <div className="severity-pill-group">
          {['mild', 'moderate', 'severe'].map((lvl) => (
            <button
              key={lvl}
              type="button"
              className={`severity-pill ${lvl} ${severity === lvl ? `active ${lvl}` : ''}`}
              onClick={() => setSeverity(lvl)}
              disabled={loading}
            >
              {lvl.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Propagation Steps Slider */}
      <div className="form-group">
        <div className="range-header">
          <label>Max Propagation Hops</label>
          <span style={{ fontWeight: 600, color: '#3b82f6' }}>{steps} hops</span>
        </div>
        <input
          type="range"
          className="form-range"
          min="1"
          max="8"
          step="1"
          value={steps}
          onChange={(e) => setSteps(parseInt(e.target.value, 10))}
          disabled={loading}
        >
        </input>
      </div>

      {/* Attenuation Factor Slider */}
      <div className="form-group">
        <div className="range-header">
          <label>Hop Attenuation Decay Factor</label>
          <span style={{ fontWeight: 600, color: '#10b981' }}>{attenuation.toFixed(2)}</span>
        </div>
        <input
          type="range"
          className="form-range"
          min="0.1"
          max="1.0"
          step="0.05"
          value={attenuation}
          onChange={(e) => setAttenuation(parseFloat(e.target.value))}
          disabled={loading}
        >
        </input>
        <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
          Lower decay limits blast radius; higher decay lets failure ripple further.
        </span>
      </div>

      {/* Primary Action Triggers */}
      <div className="scenario-actions-row">
        <button
          className="btn-predict"
          onClick={onPredict}
          disabled={loading}
        >
          <Zap size={16} />
          {loading ? 'Evaluating...' : 'Predict Blast Radius'}
        </button>

        <button
          className="btn-simulate"
          onClick={onSimulate}
          disabled={loading}
          title="Run Step-by-Step Simulation Timeline"
        >
          <PlayCircle size={16} />
          Simulate
        </button>
      </div>

      {/* Save Scenario Accordion */}
      {hasPrediction && (
        <div style={{ marginTop: '4px' }}>
          {!showSaveInput ? (
            <button
              type="button"
              className="timeline-btn"
              style={{ width: '100%', justifyContent: 'center' }}
              onClick={() => setShowSaveInput(true)}
            >
              <Save size={14} />
              Save Scenario & Outcome
            </button>
          ) : (
            <div style={{ display: 'flex', gap: '6px', marginTop: '6px' }}>
              <input
                type="text"
                className="form-input"
                style={{ flex: 1 }}
                placeholder="Scenario name (e.g. Black Friday DB Spike)"
                value={scenarioName}
                onChange={(e) => setScenarioName(e.target.value)}
                maxLength={64}
              />
              <button
                type="button"
                className="btn-predict"
                style={{ padding: '8px 12px' }}
                onClick={handleSave}
                disabled={isSaving}
              >
                {isSaving ? 'Saving...' : 'Save'}
              </button>
              <button
                type="button"
                className="timeline-btn"
                style={{ padding: '8px' }}
                onClick={() => setShowSaveInput(false)}
              >
                Cancel
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
