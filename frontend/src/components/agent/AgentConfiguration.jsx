import React, { useState } from 'react';
import { Sliders, RotateCcw, Check, X } from 'lucide-react';

export default function AgentConfiguration({ isOpen, onClose, currentConfig, onSaveConfig }) {
  const [form, setForm] = useState(currentConfig || {
    weight_information_gain: 0.35,
    weight_relevance: 0.30,
    weight_hypothesis_discrimination: 0.20,
    weight_cost: 0.10,
    weight_risk: 0.05,
    repeated_action_penalty: 0.70,
    max_actions: 5,
    max_execution_time_seconds: 30.0,
    min_utility_threshold: 0.12,
    sufficient_confidence_threshold: 0.75,
    confidence_margin_threshold: 20.0
  });

  if (!isOpen) return null;

  const handleChange = (key, val) => {
    setForm(prev => ({ ...prev, [key]: parseFloat(val) }));
  };

  const handleReset = () => {
    setForm({
      weight_information_gain: 0.35,
      weight_relevance: 0.30,
      weight_hypothesis_discrimination: 0.20,
      weight_cost: 0.10,
      weight_risk: 0.05,
      repeated_action_penalty: 0.70,
      max_actions: 5,
      max_execution_time_seconds: 30.0,
      min_utility_threshold: 0.12,
      sufficient_confidence_threshold: 0.75,
      confidence_margin_threshold: 20.0
    });
  };

  const handleSave = () => {
    onSaveConfig(form);
    onClose();
  };

  return (
    <div className="agent-modal-backdrop">
      <div className="agent-modal-box">
        <div className="agent-modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Sliders size={18} color="#38bdf8" />
            <span style={{ fontWeight: 700, fontSize: '1rem', color: '#f8fafc' }}>
              Adaptive Agent Policy Configuration
            </span>
          </div>
          <button 
            onClick={onClose}
            style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer' }}
          >
            <X size={18} />
          </button>
        </div>

        <div className="agent-modal-body">
          <div style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
            Configure utility scoring weights and stopping thresholds for the diagnostic control loop.
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div>
              <label style={{ fontSize: '0.75rem', fontWeight: 600, color: '#cbd5e1' }}>
                Weight: Information Gain ({form.weight_information_gain})
              </label>
              <input 
                type="range" min="0" max="1" step="0.05"
                value={form.weight_information_gain}
                onChange={(e) => handleChange('weight_information_gain', e.target.value)}
                style={{ width: '100%' }}
              />
            </div>

            <div>
              <label style={{ fontSize: '0.75rem', fontWeight: 600, color: '#cbd5e1' }}>
                Weight: Incident Relevance ({form.weight_relevance})
              </label>
              <input 
                type="range" min="0" max="1" step="0.05"
                value={form.weight_relevance}
                onChange={(e) => handleChange('weight_relevance', e.target.value)}
                style={{ width: '100%' }}
              />
            </div>

            <div>
              <label style={{ fontSize: '0.75rem', fontWeight: 600, color: '#cbd5e1' }}>
                Weight: Hypothesis Discrimination ({form.weight_hypothesis_discrimination})
              </label>
              <input 
                type="range" min="0" max="1" step="0.05"
                value={form.weight_hypothesis_discrimination}
                onChange={(e) => handleChange('weight_hypothesis_discrimination', e.target.value)}
                style={{ width: '100%' }}
              />
            </div>

            <div>
              <label style={{ fontSize: '0.75rem', fontWeight: 600, color: '#cbd5e1' }}>
                Weight: Execution Cost ({form.weight_cost})
              </label>
              <input 
                type="range" min="0" max="1" step="0.05"
                value={form.weight_cost}
                onChange={(e) => handleChange('weight_cost', e.target.value)}
                style={{ width: '100%' }}
              />
            </div>

            <div>
              <label style={{ fontSize: '0.75rem', fontWeight: 600, color: '#cbd5e1' }}>
                Repeated Action Penalty ({form.repeated_action_penalty})
              </label>
              <input 
                type="range" min="0" max="1" step="0.05"
                value={form.repeated_action_penalty}
                onChange={(e) => handleChange('repeated_action_penalty', e.target.value)}
                style={{ width: '100%' }}
              />
            </div>

            <div>
              <label style={{ fontSize: '0.75rem', fontWeight: 600, color: '#cbd5e1' }}>
                Max Diagnostic Action Budget ({form.max_actions} actions)
              </label>
              <input 
                type="number" min="1" max="20"
                value={form.max_actions}
                onChange={(e) => handleChange('max_actions', e.target.value)}
                style={{ width: '100%', background: '#0f172a', border: '1px solid #334155', borderRadius: '4px', padding: '4px 8px', color: '#f8fafc' }}
              />
            </div>
          </div>
        </div>

        <div className="agent-modal-footer">
          <button className="btn-agent-secondary" onClick={handleReset}>
            <RotateCcw size={14} />
            <span>Reset Defaults</span>
          </button>
          <button className="btn-agent-primary" onClick={handleSave}>
            <Check size={14} />
            <span>Apply Configuration</span>
          </button>
        </div>
      </div>
    </div>
  );
}
