import React, { useState } from 'react';
import { Play, RotateCw, Filter, ShieldAlert } from 'lucide-react';

export default function RecoveryRunSelector({
  plans,
  selectedPlanId,
  onSelectPlan,
  verificationSteps,
  onChangeVerificationSteps,
  onRunValidation,
  loading
}) {
  const [forceRerun, setForceRerun] = useState(false);

  const selectedPlan = plans.find(p => p.id === selectedPlanId);

  return (
    <div className="val-selector-panel">
      <div className="val-selector-controls">
        <div className="val-input-group">
          <label>Target Recovery Plan (Module 7)</label>
          <select
            className="val-select"
            value={selectedPlanId || ''}
            onChange={(e) => onSelectPlan(e.target.value)}
            disabled={loading}
          >
            {plans.length === 0 ? (
              <option value="">No recovery plans found</option>
            ) : (
              plans.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.plan_name} ({p.strategy_type} | risk: {p.risk_score})
                </option>
              ))
            )}
          </select>
        </div>

        <div className="val-input-group">
          <label>Stability Window (Steps)</label>
          <input
            type="number"
            min="1"
            max="15"
            className="val-input"
            style={{ width: '100px' }}
            value={verificationSteps}
            onChange={(e) => onChangeVerificationSteps(parseInt(e.target.value) || 3)}
            disabled={loading}
          />
        </div>

        <div className="val-input-group" style={{ flexDirection: 'row', alignItems: 'center', height: '36px', gap: '0.5rem' }}>
          <input
            type="checkbox"
            id="forceRerunCheck"
            checked={forceRerun}
            onChange={(e) => setForceRerun(e.target.checked)}
            disabled={loading}
          />
          <label htmlFor="forceRerunCheck" style={{ cursor: 'pointer', margin: 0 }}>Force Rerun</label>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
        {selectedPlan && (
          <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
            Actions: <strong style={{ color: '#cbd5e1' }}>{selectedPlan.actions?.length || 0}</strong> | Risk: <strong style={{ color: selectedPlan.risk_score > 50 ? '#f87171' : '#34d399' }}>{selectedPlan.risk_score}</strong>
          </span>
        )}
        <button
          className="btn-val-primary"
          onClick={() => onRunValidation(forceRerun)}
          disabled={loading || !selectedPlanId}
        >
          {loading ? <RotateCw size={14} className="spin" /> : <Play size={14} />}
          {loading ? 'Validating Simulation...' : 'Run Recovery Validation'}
        </button>
      </div>
    </div>
  );
}
