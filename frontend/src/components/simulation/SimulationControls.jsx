import React from 'react';
import { 
  Play, 
  Pause, 
  RotateCcw, 
  SkipBack, 
  SkipForward, 
  ChevronLeft, 
  ChevronRight, 
  Plus, 
  GitCompare, 
  BarChart3, 
  History,
  Copy,
  Zap
} from 'lucide-react';

export default function SimulationControls({
  currentStep,
  totalSteps,
  isPlaying,
  isRunning,
  onPlayToggle,
  onStepChange,
  onRunSimulation,
  onReset,
  onOpenCreateModal,
  onOpenCloneModal,
  onOpenCompareModal,
  onOpenEvaluationModal,
  onOpenHistoryModal,
  randomSeed,
  onRandomSeedChange
}) {
  return (
    <div className="sim-controls-panel">
      <div className="scrubber-row">
        {/* Run & Quick Action Buttons */}
        <button
          className="btn-sim-primary"
          onClick={onRunSimulation}
          disabled={isRunning}
          title="Execute multi-step discrete simulation"
        >
          <Zap size={16} className={isRunning ? 'animate-spin' : ''} />
          <span>{isRunning ? 'Simulating...' : 'Run Simulation'}</span>
        </button>

        <button
          className="btn-sim-secondary"
          onClick={onReset}
          disabled={isRunning}
          title="Reset canvas back to step 0 baseline"
        >
          <RotateCcw size={15} />
          <span>Reset</span>
        </button>

        {/* Playback Transport Controls */}
        <div className="playback-buttons">
          <button
            className="btn-sim-secondary"
            onClick={() => onStepChange(0)}
            disabled={currentStep <= 0}
            title="Jump to Step 0 (Baseline)"
          >
            <SkipBack size={14} />
          </button>
          <button
            className="btn-sim-secondary"
            onClick={() => onStepChange(Math.max(0, currentStep - 1))}
            disabled={currentStep <= 0}
            title="Previous Step"
          >
            <ChevronLeft size={14} />
          </button>
          <button
            className="btn-sim-secondary"
            onClick={onPlayToggle}
            disabled={totalSteps <= 0}
            title={isPlaying ? 'Pause' : 'Play Timeline'}
            style={{ minWidth: '70px', justifyContent: 'center' }}
          >
            {isPlaying ? <Pause size={14} /> : <Play size={14} />}
            <span>{isPlaying ? 'Pause' : 'Play'}</span>
          </button>
          <button
            className="btn-sim-secondary"
            onClick={() => onStepChange(Math.min(totalSteps, currentStep + 1))}
            disabled={currentStep >= totalSteps}
            title="Next Step"
          >
            <ChevronRight size={14} />
          </button>
          <button
            className="btn-sim-secondary"
            onClick={() => onStepChange(totalSteps)}
            disabled={currentStep >= totalSteps}
            title="Jump to Final Step"
          >
            <SkipForward size={14} />
          </button>
        </div>

        {/* Step Slider */}
        <div className="scrubber-slider-container">
          <span className="scenario-select-label">Time-Step:</span>
          <input
            type="range"
            min={0}
            max={Math.max(1, totalSteps)}
            value={currentStep}
            onChange={(e) => onStepChange(parseInt(e.target.value, 10))}
            className="step-slider"
            disabled={totalSteps === 0}
          />
          <div className="step-indicator">
            Step {currentStep} / {totalSteps}
          </div>
        </div>

        {/* Random Seed Control */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <span className="scenario-select-label" style={{ fontSize: '0.75rem' }}>Seed:</span>
          <input
            type="number"
            placeholder="Random"
            value={randomSeed ?? ''}
            onChange={(e) => onRandomSeedChange(e.target.value ? parseInt(e.target.value, 10) : null)}
            className="sim-form-input"
            style={{ width: '80px', padding: '0.25rem 0.45rem', fontSize: '0.8rem' }}
            title="Optional integer seed for strictly deterministic simulation results"
          />
        </div>
      </div>

      {/* Auxiliary Actions Row */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.6rem', borderTop: '1px solid rgba(255, 255, 255, 0.06)', paddingTop: '0.75rem' }}>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          <button className="btn-sim-secondary" onClick={onOpenCreateModal} title="Create a custom what-if scenario">
            <Plus size={14} />
            <span>New Scenario</span>
          </button>
          <button className="btn-sim-secondary" onClick={onOpenCloneModal} title="Clone current scenario for what-if branching">
            <Copy size={14} />
            <span>Clone Scenario</span>
          </button>
          <button className="btn-sim-secondary" onClick={onOpenCompareModal} title="Side-by-side run comparison matrix">
            <GitCompare size={14} />
            <span>Compare Runs</span>
          </button>
          <button className="btn-sim-secondary" onClick={onOpenEvaluationModal} title="Benchmark evaluation against static baselines">
            <BarChart3 size={14} />
            <span>Benchmarks</span>
          </button>
        </div>

        <button className="btn-sim-secondary" onClick={onOpenHistoryModal} title="View all past simulation runs">
          <History size={14} />
          <span>Run History</span>
        </button>
      </div>
    </div>
  );
}
