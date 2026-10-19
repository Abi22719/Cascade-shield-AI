import React, { useState, useEffect, useCallback, useRef } from 'react';
import { benchmarkApi } from '../services/benchmarkApi';
import BenchmarkOverview from '../components/benchmark/BenchmarkOverview';
import ExperimentBuilder from '../components/benchmark/ExperimentBuilder';
import ExperimentProgress from '../components/benchmark/ExperimentProgress';
import BaselineComparison from '../components/benchmark/BaselineComparison';
import PerformanceCharts from '../components/benchmark/PerformanceCharts';
import ScenarioExplorer from '../components/benchmark/ScenarioExplorer';
import BenchmarkReport from '../components/benchmark/BenchmarkReport';
import BenchmarkHistory from '../components/benchmark/BenchmarkHistory';
import '../styles/benchmark.css';

export default function BenchmarkDashboard({ onAddToast }) {
  const [activeTab, setActiveTab] = useState('overview'); // 'overview' | 'builder' | 'baselines' | 'charts' | 'scenarios' | 'reports' | 'history'
  
  const [summary, setSummary] = useState(null);
  const [datasets, setDatasets] = useState([]);
  const [scenarios, setScenarios] = useState([]);
  const [baselines, setBaselines] = useState({});
  const [experiments, setExperiments] = useState([]);
  
  const [activeExperiment, setActiveExperiment] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  const [comparisonModalData, setComparisonModalData] = useState(null);
  
  const pollIntervalRef = useRef(null);

  // Load baseline metadata, datasets, scenarios, and experiments
  const loadData = useCallback(async () => {
    try {
      const [sumRes, dsRes, scnRes, baseRes, expsRes] = await Promise.all([
        benchmarkApi.getSummary().catch(() => null),
        benchmarkApi.getDatasets(0, 50).catch(() => ({ items: [] })),
        benchmarkApi.getScenarios().catch(() => []),
        benchmarkApi.getBaselines().catch(() => ({})),
        benchmarkApi.getExperiments(0, 50).catch(() => ({ items: [] }))
      ]);

      setSummary(sumRes);
      setDatasets(dsRes?.items || []);
      setScenarios(scnRes || []);
      setBaselines(baseRes || {});
      
      const expList = expsRes?.items || [];
      setExperiments(expList);

      // If active experiment not set and there are experiments, load latest
      if (expList.length > 0 && !activeExperiment) {
        const latest = await benchmarkApi.getExperiment(expList[0].id).catch(() => null);
        if (latest) {
          setActiveExperiment(latest);
          if (latest.status === 'RUNNING') {
            setIsRunning(true);
          }
        }
      }
    } catch (err) {
      console.error('Failed to load benchmark data:', err);
      if (onAddToast) onAddToast(`Error loading benchmark data: ${err.message}`, 'error');
    }
  }, [activeExperiment, onAddToast]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Polling for active running experiment
  useEffect(() => {
    if (!isRunning || !activeExperiment?.id) {
      if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
      return;
    }

    pollIntervalRef.current = setInterval(async () => {
      try {
        const prog = await benchmarkApi.getExperimentProgress(activeExperiment.id);
        if (prog.status !== 'RUNNING') {
          setIsRunning(false);
          clearInterval(pollIntervalRef.current);
          const fullExp = await benchmarkApi.getExperiment(activeExperiment.id);
          setActiveExperiment(fullExp);
          loadData();
          if (onAddToast) {
            onAddToast(`Benchmark experiment completed! Resilience Score: ${fullExp.overall_resilience_score?.toFixed(1) || 'N/A'}/100`, 'success');
          }
        } else {
          setActiveExperiment((prev) => ({
            ...prev,
            progress: prog.progress,
            status: prog.status,
            overall_resilience_score: prog.overall_resilience_score
          }));
        }
      } catch (err) {
        console.error('Polling error:', err);
      }
    }, 1500);

    return () => {
      if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
    };
  }, [isRunning, activeExperiment?.id, loadData, onAddToast]);

  const handleLaunchExperiment = async (payload) => {
    try {
      const created = await benchmarkApi.createExperiment(payload, true);
      setActiveExperiment(created);
      setIsRunning(true);
      setActiveTab('overview');
      loadData();
      if (onAddToast) onAddToast(`Benchmark experiment '${created.name}' launched!`, 'info');
    } catch (err) {
      if (onAddToast) onAddToast(`Failed to launch experiment: ${err.message}`, 'error');
      throw err;
    }
  };

  const handleCancelExperiment = async () => {
    if (!activeExperiment?.id) return;
    try {
      await benchmarkApi.cancelExperiment(activeExperiment.id);
      setIsRunning(false);
      const updated = await benchmarkApi.getExperiment(activeExperiment.id);
      setActiveExperiment(updated);
      loadData();
      if (onAddToast) onAddToast('Experiment run cancelled.', 'warning');
    } catch (err) {
      if (onAddToast) onAddToast(`Failed to cancel experiment: ${err.message}`, 'error');
    }
  };

  const handleSelectExperiment = async (expId) => {
    try {
      const exp = await benchmarkApi.getExperiment(expId);
      setActiveExperiment(exp);
      setIsRunning(exp.status === 'RUNNING');
      setActiveTab('overview');
    } catch (err) {
      if (onAddToast) onAddToast(`Failed to load experiment: ${err.message}`, 'error');
    }
  };

  const handleCompareExperiments = async (selectedIds) => {
    try {
      const compRes = await benchmarkApi.compareExperiments(selectedIds);
      setComparisonModalData(compRes);
    } catch (err) {
      if (onAddToast) onAddToast(`Comparison failed: ${err.message}`, 'error');
    }
  };

  return (
    <div className="benchmark-dashboard">
      {/* Header */}
      <div className="bm-header">
        <div className="bm-title-group">
          <h2>
            <span>🛡️</span> Module 9: Resilience Benchmarking & Performance Evaluation
          </h2>
          <p>
            Standardized evaluation across Modules 1–8 with repeatable failure archetypes, baselines, and safety isolation.
          </p>
        </div>

        <div className="bm-header-actions">
          <button className="btn-bm-secondary" onClick={loadData}>
            🔄 Refresh
          </button>
          <button className="btn-bm-primary" onClick={() => setActiveTab('builder')}>
            ⚡ New Experiment
          </button>
        </div>
      </div>

      {/* Progress Card if running */}
      {isRunning && (
        <ExperimentProgress experiment={activeExperiment} onCancel={handleCancelExperiment} />
      )}

      {/* Tabs */}
      <div className="bm-tabs">
        <button
          className={`bm-tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          <span>🏆</span> Overview
        </button>
        <button
          className={`bm-tab-btn ${activeTab === 'builder' ? 'active' : ''}`}
          onClick={() => setActiveTab('builder')}
        >
          <span>⚙️</span> Run Experiment
        </button>
        <button
          className={`bm-tab-btn ${activeTab === 'baselines' ? 'active' : ''}`}
          onClick={() => setActiveTab('baselines')}
        >
          <span>⚖️</span> Baseline Comparison
        </button>
        <button
          className={`bm-tab-btn ${activeTab === 'charts' ? 'active' : ''}`}
          onClick={() => setActiveTab('charts')}
        >
          <span>📊</span> Per-Module Metrics
        </button>
        <button
          className={`bm-tab-btn ${activeTab === 'scenarios' ? 'active' : ''}`}
          onClick={() => setActiveTab('scenarios')}
        >
          <span>🧪</span> Scenario Catalog
        </button>
        <button
          className={`bm-tab-btn ${activeTab === 'reports' ? 'active' : ''}`}
          onClick={() => setActiveTab('reports')}
        >
          <span>📄</span> Evaluation Report
        </button>
        <button
          className={`bm-tab-btn ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => setActiveTab('history')}
        >
          <span>📜</span> History ({experiments.length})
        </button>
      </div>

      {/* Tab Panels */}
      {activeTab === 'overview' && (
        <BenchmarkOverview
          summary={summary}
          latestExperiment={activeExperiment}
          onLaunchClick={() => setActiveTab('builder')}
        />
      )}

      {activeTab === 'builder' && (
        <ExperimentBuilder
          datasets={datasets}
          baselines={baselines}
          onExperimentCreated={handleLaunchExperiment}
          isRunning={isRunning}
        />
      )}

      {activeTab === 'baselines' && (
        <BaselineComparison comparisons={activeExperiment?.comparisons || []} />
      )}

      {activeTab === 'charts' && (
        <PerformanceCharts results={activeExperiment?.results || []} />
      )}

      {activeTab === 'scenarios' && (
        <ScenarioExplorer scenarios={scenarios} />
      )}

      {activeTab === 'reports' && (
        <BenchmarkReport experimentId={activeExperiment?.id} />
      )}

      {activeTab === 'history' && (
        <BenchmarkHistory
          experiments={experiments}
          onSelectExperiment={handleSelectExperiment}
          onCompare={handleCompareExperiments}
          activeExperimentId={activeExperiment?.id}
        />
      )}

      {/* Comparison Modal */}
      {comparisonModalData && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0, 0, 0, 0.75)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            padding: '1.5rem'
          }}
        >
          <div className="bm-card" style={{ maxWidth: '850px', width: '100%', maxHeight: '90vh', overflowY: 'auto' }}>
            <div className="bm-card-header">
              <h3><span>⚔️</span> Side-by-Side Experiment Comparison</h3>
              <button className="btn-bm-secondary" onClick={() => setComparisonModalData(null)}>
                ✕ Close
              </button>
            </div>

            <div style={{ background: 'rgba(99, 102, 241, 0.1)', border: '1px solid rgba(99, 102, 241, 0.3)', padding: '0.85rem', borderRadius: '6px' }}>
              <strong>Verdict:</strong> {comparisonModalData.summary_verdict}
            </div>

            <div className="bm-table-wrapper" style={{ marginTop: '0.75rem' }}>
              <table className="bm-table">
                <thead>
                  <tr>
                    <th>Experiment Name</th>
                    <th>Status</th>
                    <th>Overall Resilience Score</th>
                    <th>Best Performer</th>
                  </tr>
                </thead>
                <tbody>
                  {comparisonModalData.experiments.map((e) => {
                    const isBest = e.id === comparisonModalData.best_experiment_id;
                    return (
                      <tr key={e.id}>
                        <td style={{ fontWeight: 600, color: '#f8fafc' }}>{e.name}</td>
                        <td>{e.status}</td>
                        <td style={{ fontWeight: 700, color: '#4ade80' }}>
                          {e.overall_resilience_score?.toFixed(1) || '0.0'} / 100
                        </td>
                        <td>{isBest ? '🏆 Top Score' : '—'}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
