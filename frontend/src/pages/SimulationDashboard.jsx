import React, { useState, useEffect, useCallback, useRef } from 'react';
import { 
  Play, 
  RotateCcw, 
  Layers, 
  Activity, 
  Flame, 
  Network, 
  GitBranch, 
  Table, 
  Clock, 
  TrendingUp,
  Sparkles,
  Info
} from 'lucide-react';
import { simulationApi } from '../services/simulationApi';
import { api } from '../services/api';
import SimulationSummaryCards from '../components/simulation/SimulationSummaryCards';
import SimulationControls from '../components/simulation/SimulationControls';
import SimulationGraph from '../components/simulation/SimulationGraph';
import SimulationTimeline from '../components/simulation/SimulationTimeline';
import ServiceStateTable from '../components/simulation/ServiceStateTable';
import MetricEvolutionChart from '../components/simulation/MetricEvolutionChart';
import ScenarioBuilderModal from '../components/simulation/ScenarioBuilderModal';
import ScenarioComparisonModal from '../components/simulation/ScenarioComparisonModal';
import SimulationEvaluationModal from '../components/simulation/SimulationEvaluationModal';
import SimulationHistoryDrawer from '../components/simulation/SimulationHistoryDrawer';
import '../styles/simulation-dashboard.css';

export default function SimulationDashboard({ onAddToast }) {
  // Scenarios State
  const [scenarios, setScenarios] = useState([]);
  const [selectedScenarioId, setSelectedScenarioId] = useState(null);
  const [selectedScenario, setSelectedScenario] = useState(null);
  const [simulationOptions, setSimulationOptions] = useState(null);
  const [topologyGraph, setTopologyGraph] = useState({ nodes: [], edges: [] });
  const [servicesList, setServicesList] = useState([]);

  // Simulation Run & Playback State
  const [currentRun, setCurrentRun] = useState(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const [randomSeed, setRandomSeed] = useState(42);
  const [selectedServiceId, setSelectedServiceId] = useState(null);
  const [activeRightTab, setActiveRightTab] = useState('table'); // 'table' | 'timeline' | 'charts'

  // Modals
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isCompareOpen, setIsCompareOpen] = useState(false);
  const [isEvaluationOpen, setIsEvaluationOpen] = useState(false);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [availableRuns, setAvailableRuns] = useState([]);

  // Playback Timer
  const playTimerRef = useRef(null);

  // 1. Initial Load: Options, Topology Graph, Services, Scenarios
  const loadInitialData = useCallback(async () => {
    try {
      const [opts, graph, services, scenRes] = await Promise.all([
        simulationApi.getOptions(),
        api.getGraph(),
        api.getServices(),
        simulationApi.getScenarios(0, 50)
      ]);

      setSimulationOptions(opts);
      setTopologyGraph(graph);
      setServicesList(services);

      const scenList = scenRes.scenarios || [];
      setScenarios(scenList);

      if (scenList.length > 0 && !selectedScenarioId) {
        setSelectedScenarioId(scenList[0].id);
        setSelectedScenario(scenList[0]);
      } else if (scenList.length === 0) {
        // If no scenarios exist, create a default one from presets
        const defaultPreset = opts.presets?.[0];
        if (defaultPreset) {
          const created = await simulationApi.createScenario({
            name: defaultPreset.name,
            category: defaultPreset.category || 'failure_propagation',
            description: defaultPreset.description || 'Simulated what-if scenario',
            config: {
              failures: [{
                target_service_ids: defaultPreset.target_services || ['srv-payment'],
                failure_type: defaultPreset.failure_type || 'service_unavailable',
                severity: defaultPreset.severity || 'severe',
                start_step: 1,
                duration_steps: 4
              }],
              propagation: { max_steps: 6, attenuation_factor: 0.75, propagation_threshold: 25.0 },
              recovery: { recovery_mode: defaultPreset.recovery_mode || 'gradual', recovery_step: defaultPreset.recovery_step || 5, recovery_rate: 0.4 }
            },
            source_data_type: 'digital_twin'
          });
          setScenarios([created]);
          setSelectedScenarioId(created.id);
          setSelectedScenario(created);
        }
      }
    } catch (err) {
      console.error('Error loading simulation options or scenarios:', err);
      if (onAddToast) onAddToast(err.message, 'error', 'Simulation Initialization Error');
    }
  }, [selectedScenarioId, onAddToast]);

  useEffect(() => {
    loadInitialData();
  }, [loadInitialData]);

  // 2. Fetch specific scenario details when selection changes
  useEffect(() => {
    if (!selectedScenarioId) return;

    async function loadScenarioDetails() {
      try {
        const sc = await simulationApi.getScenario(selectedScenarioId);
        setSelectedScenario(sc);

        // If scenario has a latest run, fetch it
        if (sc.latest_run_id) {
          const run = await simulationApi.getRun(sc.latest_run_id);
          setCurrentRun(run);
          setCurrentStep(run.total_steps || 0);
        } else {
          setCurrentRun(null);
          setCurrentStep(0);
        }
      } catch (err) {
        console.error('Error fetching scenario:', err);
      }
    }

    loadScenarioDetails();
  }, [selectedScenarioId]);

  // 3. Playback scrubbing loop
  useEffect(() => {
    if (isPlaying && currentRun && currentRun.total_steps > 0) {
      playTimerRef.current = setInterval(() => {
        setCurrentStep((prev) => {
          if (prev >= currentRun.total_steps) {
            setIsPlaying(false);
            return prev;
          }
          return prev + 1;
        });
      }, 1100);
    } else {
      if (playTimerRef.current) clearInterval(playTimerRef.current);
    }

    return () => {
      if (playTimerRef.current) clearInterval(playTimerRef.current);
    };
  }, [isPlaying, currentRun]);

  // 4. Action: Run Simulation
  const handleRunSimulation = async () => {
    if (!selectedScenarioId) return;

    setIsRunning(true);
    setIsPlaying(false);
    try {
      const runRes = await simulationApi.runScenario(selectedScenarioId, {
        random_seed: randomSeed,
        max_steps_override: selectedScenario?.config?.propagation?.max_steps
      });

      setCurrentRun(runRes);
      setCurrentStep(runRes.total_steps || 0);
      setAvailableRuns((prev) => [runRes, ...prev.filter(r => r.id !== runRes.id)]);

      if (onAddToast) {
        onAddToast(
          `What-if simulation completed in ${runRes.total_steps} steps. Blast radius: ${runRes.summary?.total_impacted_services || 0} services impacted.`,
          'success',
          'Simulation Completed'
        );
      }
    } catch (err) {
      console.error('Simulation run failed:', err);
      if (onAddToast) onAddToast(err.message, 'error', 'Simulation Run Failed');
    } finally {
      setIsRunning(false);
    }
  };

  // 5. Action: Reset
  const handleReset = async () => {
    if (!selectedScenarioId) return;
    try {
      await simulationApi.resetScenario(selectedScenarioId);
      setCurrentStep(0);
      setIsPlaying(false);
      if (onAddToast) onAddToast('Canvas timeline reset to step 0 clean digital twin baseline.', 'info', 'Simulation Reset');
    } catch (err) {
      if (onAddToast) onAddToast(err.message, 'error', 'Reset Failed');
    }
  };

  // 6. Action: Create Scenario
  const handleCreateScenario = async (payload) => {
    try {
      const created = await simulationApi.createScenario(payload);
      setScenarios((prev) => [created, ...prev]);
      setSelectedScenarioId(created.id);
      setSelectedScenario(created);
      setIsCreateOpen(false);
      if (onAddToast) onAddToast(`Scenario '${created.name}' created successfully.`, 'success', 'Scenario Created');
    } catch (err) {
      if (onAddToast) onAddToast(err.message, 'error', 'Failed to Create Scenario');
    }
  };

  // 7. Action: Clone Scenario
  const handleCloneScenario = async () => {
    if (!selectedScenarioId) return;
    try {
      const newName = `${selectedScenario?.name || 'Scenario'} (Clone)`;
      const cloned = await simulationApi.cloneScenario(selectedScenarioId, newName);
      setScenarios((prev) => [cloned, ...prev]);
      setSelectedScenarioId(cloned.id);
      setSelectedScenario(cloned);
      if (onAddToast) onAddToast(`Cloned scenario '${cloned.name}' ready for what-if branching.`, 'success', 'Scenario Cloned');
    } catch (err) {
      if (onAddToast) onAddToast(err.message, 'error', 'Cloning Failed');
    }
  };

  // 8. Action: Select Historical Run
  const handleSelectRun = async (runId) => {
    try {
      const run = await simulationApi.getRun(runId);
      setCurrentRun(run);
      setCurrentStep(run.total_steps || 0);
      if (onAddToast) onAddToast(`Loaded simulation run '${run.id}'.`, 'info', 'Run Loaded');
    } catch (err) {
      if (onAddToast) onAddToast(err.message, 'error', 'Failed to load run');
    }
  };

  // Compute Current Step State
  // If currentStep === 0 or no run, state is baseline healthy
  const totalSteps = currentRun?.total_steps || selectedScenario?.config?.propagation?.max_steps || 6;
  const stepSnapshot = currentRun?.timeline_steps?.find(st => st.step_number === currentStep);
  
  // Extract services map for current step
  const currentStepServices = stepSnapshot?.services || (
    // Fallback baseline services from servicesList
    servicesList.reduce((acc, s) => {
      acc[s.id] = {
        service_id: s.id,
        service_name: s.name,
        health_status: s.health_status || 'HEALTHY',
        cpu_usage: s.cpu_usage || 20.0,
        memory_usage: s.memory_usage || 30.0,
        latency_ms: s.latency_ms || 40.0,
        error_rate: s.error_rate || 0.0,
        risk_score: 0.0,
        is_initial_failure: false,
        is_impacted: false,
        is_recovered: false
      };
      return acc;
    }, {})
  );

  const activeEvents = stepSnapshot?.events || [];

  return (
    <div className="simulation-dashboard">
      {/* Header */}
      <div className="sim-header">
        <div className="sim-title-group">
          <h2>
            <Flame size={24} color="#8b5cf6" />
            <span>What-If Scenario Simulation Engine</span>
            <span className="scenario-category-badge">Module 6</span>
          </h2>
          <p>
            Deterministic discrete time-step failure injection, callee-to-caller multi-hop propagation, and dynamic recovery modeling.
          </p>
        </div>

        <div className="sim-control-buttons">
          <div className="execution-status-pill completed">
            <span className="pulse-dot"></span>
            <span>Isolated In-Memory Sandbox (Zero DB Mutation)</span>
          </div>
        </div>
      </div>

      {/* Scenario Selection Bar */}
      <div className="sim-scenario-bar">
        <div className="scenario-select-wrapper">
          <span className="scenario-select-label">Active Scenario:</span>
          <select
            value={selectedScenarioId || ''}
            onChange={(e) => setSelectedScenarioId(e.target.value)}
            className="scenario-dropdown"
          >
            {scenarios.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name} ({s.category})
              </option>
            ))}
          </select>
          {selectedScenario && (
            <span className="scenario-category-badge">{selectedScenario.category}</span>
          )}
        </div>

        {selectedScenario && (
          <div style={{ fontSize: '0.8rem', color: '#94a3b8', display: 'flex', alignItems: 'center', gap: '0.8rem' }}>
            <span>Target: <b>{selectedScenario.config?.failures?.[0]?.target_service_ids?.join(', ') || 'N/A'}</b></span>
            <span>•</span>
            <span>Mode: <b>{selectedScenario.config?.failures?.[0]?.failure_type}</b></span>
            <span>•</span>
            <span>Recovery: <b>{selectedScenario.config?.recovery?.recovery_mode}</b></span>
          </div>
        )}
      </div>

      {/* KPI Cards */}
      <SimulationSummaryCards
        summary={currentRun?.summary}
        currentStep={currentStep}
        totalSteps={totalSteps}
      />

      {/* Time-Step Controls & Scrubber */}
      <SimulationControls
        currentStep={currentStep}
        totalSteps={totalSteps}
        isPlaying={isPlaying}
        isRunning={isRunning}
        onPlayToggle={() => setIsPlaying(!isPlaying)}
        onStepChange={(step) => setCurrentStep(step)}
        onRunSimulation={handleRunSimulation}
        onReset={handleReset}
        onOpenCreateModal={() => setIsCreateOpen(true)}
        onOpenCloneModal={handleCloneScenario}
        onOpenCompareModal={() => setIsCompareOpen(true)}
        onOpenEvaluationModal={() => setIsEvaluationOpen(true)}
        onOpenHistoryModal={() => setIsHistoryOpen(true)}
        randomSeed={randomSeed}
        onRandomSeedChange={setRandomSeed}
      />

      {/* Main Two-Column Simulation Workspace */}
      <div className="sim-workspace-grid">
        {/* Left Column: Cytoscape Live Graph Canvas */}
        <div className="sim-panel">
          <div className="sim-panel-header">
            <span className="sim-panel-title">
              <Network size={16} color="#8b5cf6" />
              <span>Simulated Architecture Topology (Step {currentStep})</span>
            </span>
            <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
              Callee-to-caller propagation waves
            </span>
          </div>
          <div className="sim-panel-body" style={{ padding: 0 }}>
            <SimulationGraph
              topologyGraph={topologyGraph}
              stepServices={currentStepServices}
              activeEvents={activeEvents}
              selectedServiceId={selectedServiceId}
              onSelectService={setSelectedServiceId}
            />
          </div>
        </div>

        {/* Right Column: Tabbed State Inspector */}
        <div className="sim-panel">
          <div className="sim-panel-header">
            <div style={{ display: 'flex', gap: '0.4rem' }}>
              <button
                className={`btn-sim-secondary ${activeRightTab === 'table' ? 'active' : ''}`}
                style={{
                  fontSize: '0.78rem',
                  padding: '0.3rem 0.65rem',
                  backgroundColor: activeRightTab === 'table' ? 'rgba(139, 92, 246, 0.25)' : undefined,
                  borderColor: activeRightTab === 'table' ? '#8b5cf6' : undefined,
                  color: activeRightTab === 'table' ? '#c4b5fd' : undefined
                }}
                onClick={() => setActiveRightTab('table')}
              >
                <Table size={13} />
                <span>Service Telemetry</span>
              </button>

              <button
                className={`btn-sim-secondary ${activeRightTab === 'timeline' ? 'active' : ''}`}
                style={{
                  fontSize: '0.78rem',
                  padding: '0.3rem 0.65rem',
                  backgroundColor: activeRightTab === 'timeline' ? 'rgba(139, 92, 246, 0.25)' : undefined,
                  borderColor: activeRightTab === 'timeline' ? '#8b5cf6' : undefined,
                  color: activeRightTab === 'timeline' ? '#c4b5fd' : undefined
                }}
                onClick={() => setActiveRightTab('timeline')}
              >
                <Clock size={13} />
                <span>Propagation Events ({currentRun?.timeline_steps?.flatMap(s => s.events || []).length || 0})</span>
              </button>

              <button
                className={`btn-sim-secondary ${activeRightTab === 'charts' ? 'active' : ''}`}
                style={{
                  fontSize: '0.78rem',
                  padding: '0.3rem 0.65rem',
                  backgroundColor: activeRightTab === 'charts' ? 'rgba(139, 92, 246, 0.25)' : undefined,
                  borderColor: activeRightTab === 'charts' ? '#8b5cf6' : undefined,
                  color: activeRightTab === 'charts' ? '#c4b5fd' : undefined
                }}
                onClick={() => setActiveRightTab('charts')}
              >
                <TrendingUp size={13} />
                <span>Metric Evolution</span>
              </button>
            </div>
          </div>

          <div className="sim-panel-body">
            {activeRightTab === 'table' && (
              <ServiceStateTable
                services={currentStepServices}
                selectedServiceId={selectedServiceId}
                onSelectService={setSelectedServiceId}
              />
            )}

            {activeRightTab === 'timeline' && (
              <SimulationTimeline
                timelineSteps={currentRun?.timeline_steps || []}
                currentStep={currentStep}
                onSelectStep={(step) => setCurrentStep(step)}
              />
            )}

            {activeRightTab === 'charts' && (
              <MetricEvolutionChart
                timelineSteps={currentRun?.timeline_steps || []}
                services={servicesList}
                selectedServiceId={selectedServiceId}
                onSelectService={setSelectedServiceId}
              />
            )}
          </div>
        </div>
      </div>

      {/* Modals */}
      <ScenarioBuilderModal
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        onSubmit={handleCreateScenario}
        simulationOptions={simulationOptions}
        services={servicesList}
      />

      <ScenarioComparisonModal
        isOpen={isCompareOpen}
        onClose={() => setIsCompareOpen(false)}
        currentRunId={currentRun?.id}
        availableRuns={availableRuns.length > 0 ? availableRuns : (currentRun ? [currentRun] : [])}
      />

      <SimulationEvaluationModal
        isOpen={isEvaluationOpen}
        onClose={() => setIsEvaluationOpen(false)}
      />

      <SimulationHistoryDrawer
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
        runs={availableRuns.length > 0 ? availableRuns : (currentRun ? [currentRun] : [])}
        currentRunId={currentRun?.id}
        onSelectRun={handleSelectRun}
      />
    </div>
  );
}
