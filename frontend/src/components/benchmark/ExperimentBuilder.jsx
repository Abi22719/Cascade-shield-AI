import React, { useState } from 'react';

export default function ExperimentBuilder({ datasets, baselines, onExperimentCreated, isRunning }) {
  const [name, setName] = useState('Standard Cloud Resilience Evaluation');
  const [description, setDescription] = useState('Comprehensive 7-module benchmark across 10 failure archetypes');
  const [datasetId, setDatasetId] = useState(datasets[0]?.id || '');
  const [selectedModules, setSelectedModules] = useState([
    'module_2', 'module_3', 'module_4', 'module_5', 'module_6', 'module_7', 'module_8'
  ]);
  const [seed, setSeed] = useState(42);
  const [repetitions, setRepetitions] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const toggleModule = (mod) => {
    if (selectedModules.includes(mod)) {
      setSelectedModules(selectedModules.filter((m) => m !== mod));
    } else {
      setSelectedModules([...selectedModules, mod]);
    }
  };

  const handleLaunch = async (e) => {
    e.preventDefault();
    if (selectedModules.length === 0) {
      setError('Please select at least one module to benchmark.');
      return;
    }
    setError(null);
    setLoading(true);

    try {
      const payload = {
        name,
        description,
        dataset_id: datasetId || null,
        selected_modules: selectedModules,
        random_seed: Number(seed),
        repetitions: Number(repetitions)
      };
      await onExperimentCreated(payload);
    } catch (err) {
      setError(err.message || 'Failed to start benchmark experiment.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bm-card">
      <div className="bm-card-header">
        <h3><span>🛠️</span> Configure & Launch Resilience Experiment</h3>
      </div>

      {error && (
        <div style={{ background: 'rgba(239, 68, 68, 0.15)', border: '1px solid rgba(239, 68, 68, 0.4)', borderRadius: '6px', padding: '0.65rem 1rem', color: '#f87171', fontSize: '0.85rem' }}>
          {error}
        </div>
      )}

      <form onSubmit={handleLaunch} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
          <div className="bm-form-group">
            <label>Experiment Name</label>
            <input
              type="text"
              className="bm-input"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>

          <div className="bm-form-group">
            <label>Target Failure Dataset</label>
            <select
              className="bm-select"
              value={datasetId}
              onChange={(e) => setDatasetId(e.target.value)}
            >
              {datasets.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name} ({d.scenario_count} scenarios)
                </option>
              ))}
              {datasets.length === 0 && <option value="">Auto-generate Canonical 10-Scenario Dataset</option>}
            </select>
          </div>
        </div>

        <div className="bm-form-group">
          <label>Description</label>
          <input
            type="text"
            className="bm-input"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </div>

        <div className="bm-form-group">
          <label>Select Modules & Methods to Evaluate</label>
          <div className="bm-checkbox-grid">
            {Object.entries(baselines || {}).map(([modKey, modInfo]) => {
              const isChecked = selectedModules.includes(modKey);
              return (
                <label key={modKey} className="bm-checkbox-item" style={{ cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    checked={isChecked}
                    onChange={() => toggleModule(modKey)}
                  />
                  <div>
                    <div style={{ fontWeight: 600, color: '#f8fafc' }}>{modInfo.name}</div>
                    <div style={{ fontSize: '0.72rem', color: '#94a3b8' }}>
                      <span className="badge-candidate">{modInfo.candidate}</span> vs {modInfo.baselines.length} baselines
                    </div>
                  </div>
                </label>
              );
            })}
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem' }}>
          <div className="bm-form-group">
            <label>Random Seed (Reproducibility)</label>
            <input
              type="number"
              className="bm-input"
              value={seed}
              onChange={(e) => setSeed(e.target.value)}
              min={1}
            />
          </div>

          <div className="bm-form-group">
            <label>Repetitions (Statistical Stability)</label>
            <input
              type="number"
              className="bm-input"
              value={repetitions}
              onChange={(e) => setRepetitions(e.target.value)}
              min={1}
              max={10}
            />
          </div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '0.5rem' }}>
          <button
            type="submit"
            className="btn-bm-primary"
            disabled={loading || isRunning}
            style={{ padding: '0.65rem 1.5rem', fontSize: '0.9rem' }}
          >
            {loading || isRunning ? '⏳ Benchmarking in Progress...' : '🚀 Launch Benchmark Experiment'}
          </button>
        </div>
      </form>
    </div>
  );
}
