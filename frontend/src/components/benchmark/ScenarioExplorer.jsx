import React, { useState } from 'react';

export default function ScenarioExplorer({ scenarios }) {
  const [selectedScenario, setSelectedScenario] = useState(scenarios[0] || null);

  if (!scenarios || scenarios.length === 0) {
    return (
      <div className="bm-card">
        <div className="bm-card-header">
          <h3><span>🧪</span> Benchmark Scenario Catalog</h3>
        </div>
        <p style={{ color: '#94a3b8', fontSize: '0.85rem' }}>
          No scenarios available. Scenarios will be auto-populated upon generating a dataset.
        </p>
      </div>
    );
  }

  const currentScn = selectedScenario || scenarios[0];
  const inputConfig = currentScn?.input_config || {};
  const groundTruth = currentScn?.ground_truth || {};

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'minmax(280px, 1fr) minmax(400px, 2fr)', gap: '1.25rem' }}>
      {/* Scenario List */}
      <div className="bm-card">
        <div className="bm-card-header">
          <h3><span>📋</span> Scenarios ({scenarios.length})</h3>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', maxHeight: '550px', overflowY: 'auto' }}>
          {scenarios.map((s) => {
            const isSelected = currentScn?.id === s.id;
            return (
              <div
                key={s.id}
                onClick={() => setSelectedScenario(s)}
                style={{
                  padding: '0.65rem 0.85rem',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  background: isSelected ? 'rgba(99, 102, 241, 0.15)' : 'rgba(255, 255, 255, 0.02)',
                  border: isSelected ? '1px solid rgba(99, 102, 241, 0.4)' : '1px solid rgba(255, 255, 255, 0.05)',
                  transition: 'all 0.2s'
                }}
              >
                <div style={{ fontWeight: 600, color: isSelected ? '#a5b4fc' : '#f8fafc', fontSize: '0.85rem' }}>
                  {s.name}
                </div>
                <div style={{ fontSize: '0.72rem', color: '#94a3b8', marginTop: '0.15rem' }}>
                  Type: <code>{s.scenario_type}</code>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Scenario Details & Isolated Ground Truth */}
      <div className="bm-card">
        <div className="bm-card-header">
          <h3><span>🔍</span> Scenario Specification & Ground Truth</h3>
          <span style={{ fontSize: '0.75rem', color: '#38bdf8', background: 'rgba(56, 189, 248, 0.1)', padding: '0.2rem 0.5rem', borderRadius: '4px' }}>
            ID: {currentScn?.id}
          </span>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div>
            <h4 style={{ margin: '0 0 0.4rem 0', fontSize: '0.82rem', color: '#94a3b8', textTransform: 'uppercase' }}>
              Fault Injection Parameters (Input)
            </h4>
            <div style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid rgba(255, 255, 255, 0.06)', borderRadius: '6px', padding: '0.75rem', fontSize: '0.82rem' }}>
              <div><strong>Target Service(s):</strong> {inputConfig.target_service_ids?.join(', ') || 'N/A'}</div>
              <div><strong>Failure Type:</strong> <code>{inputConfig.failure_type || 'N/A'}</code></div>
              <div><strong>Severity:</strong> {inputConfig.severity || 'N/A'}</div>
              <div><strong>Start Step:</strong> {inputConfig.start_step} | <strong>Duration Steps:</strong> {inputConfig.duration_steps}</div>
            </div>
          </div>

          <div>
            <h4 style={{ margin: '0 0 0.4rem 0', fontSize: '0.82rem', color: '#94a3b8', textTransform: 'uppercase' }}>
              🔒 Isolated Synthetic Ground Truth
            </h4>
            <div style={{ background: 'rgba(15, 23, 42, 0.8)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '6px', padding: '0.85rem', fontSize: '0.82rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <div>
                <strong style={{ color: '#cbd5e1' }}>Expected Anomalies:</strong>{' '}
                <span style={{ color: '#f87171' }}>{groundTruth.expected_anomalies?.join(', ') || 'None'}</span>
              </div>
              <div>
                <strong style={{ color: '#cbd5e1' }}>Expected Affected Services:</strong>{' '}
                <span style={{ color: '#fbbf24' }}>{groundTruth.expected_affected_services?.join(', ') || 'None'}</span>
              </div>
              <div>
                <strong style={{ color: '#cbd5e1' }}>True Root Cause:</strong>{' '}
                <span style={{ color: '#4ade80', fontWeight: 600 }}>{groundTruth.expected_root_cause || 'None'}</span>
              </div>
              <div>
                <strong style={{ color: '#cbd5e1' }}>Expected Diagnostic Actions:</strong>{' '}
                <span style={{ color: '#a5b4fc' }}>{groundTruth.expected_diagnostic_actions?.join(' ➔ ') || 'N/A'}</span>
              </div>
              <div>
                <strong style={{ color: '#cbd5e1' }}>Expected Validation Outcome:</strong>{' '}
                <span style={{ color: '#38bdf8', fontWeight: 600 }}>{groundTruth.expected_validation_outcome || 'N/A'}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
