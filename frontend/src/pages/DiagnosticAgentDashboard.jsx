import React, { useState, useEffect, useCallback } from 'react';
import { 
  Bot, 
  Play, 
  StepForward, 
  Square, 
  RotateCcw, 
  Sliders, 
  Award, 
  FileText, 
  ShieldAlert, 
  RefreshCw 
} from 'lucide-react';

import { agentApi } from '../services/agentApi';
import AgentStatusCard from '../components/agent/AgentStatusCard';
import DiagnosticActionList from '../components/agent/DiagnosticActionList';
import ActionReasoningPanel from '../components/agent/ActionReasoningPanel';
import AgentExecutionTimeline from '../components/agent/AgentExecutionTimeline';
import CandidateComparison from '../components/agent/CandidateComparison';
import AgentConfiguration from '../components/agent/AgentConfiguration';
import AgentAuditLog from '../components/agent/AgentAuditLog';
import AgentEvaluationModal from '../components/agent/AgentEvaluationModal';

import '../styles/agent-dashboard.css';

const INCIDENT_PRESETS = [
  {
    name: 'Payment Latency Storm',
    targetService: 'srv-payment',
    desc: 'Upstream payment degradation propagating to orders and gateway'
  },
  {
    name: 'Database Pool Exhaustion',
    targetService: 'srv-database',
    desc: 'Relational connection starvation impacting product & checkout'
  },
  {
    name: 'Auth Verifier Outage',
    targetService: 'srv-auth',
    desc: 'JWT validation timeout affecting authenticated APIs'
  },
  {
    name: 'Decoupled Queue Worker',
    targetService: 'srv-notify',
    desc: 'Asynchronous event consumer failure without caller backpressure'
  },
  {
    name: 'Ambiguous Jitter',
    targetService: 'srv-gateway',
    desc: 'Transient observation without clear corroborating anomalies'
  }
];

export default function DiagnosticAgentDashboard({ onAddToast }) {
  const [session, setSession] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [history, setHistory] = useState([]);
  const [candidates, setCandidates] = useState([]);
  const [unresolvedQuestions, setUnresolvedQuestions] = useState([]);
  const [config, setConfig] = useState(null);
  const [selectedActionId, setSelectedActionId] = useState(null);
  const [selectedPreset, setSelectedPreset] = useState(INCIDENT_PRESETS[0]);
  const [loading, setLoading] = useState(false);

  // Modals
  const [isConfigOpen, setIsConfigOpen] = useState(false);
  const [isAuditOpen, setIsAuditOpen] = useState(false);
  const [isEvalOpen, setIsEvalOpen] = useState(false);

  // Fetch initial config
  useEffect(() => {
    agentApi.getConfig().then(cfg => setConfig(cfg)).catch(() => {});
  }, []);

  // Initialize or load session
  const initSession = useCallback(async (preset = selectedPreset) => {
    setLoading(true);
    try {
      const res = await agentApi.createSession({
        target_service_id: preset.targetService
      });
      setSession(res);
      setHistory(res.action_history || []);
      setCandidates(res.latest_ranking || []);
      setUnresolvedQuestions(res.unresolved_questions || []);

      // Fetch initial recommendations
      const recs = await agentApi.getRecommendations(res.id);
      setRecommendations(recs);
      if (recs && recs.length > 0 && recs[0].eligible) {
        setSelectedActionId(recs[0].action_id);
      }
      onAddToast?.(`Diagnostic session initialized for ${preset.name}`, 'info');
    } catch (err) {
      console.error(err);
      onAddToast?.(`Failed to initialize session: ${err.message}`, 'error');
    } finally {
      setLoading(false);
    }
  }, [selectedPreset, onAddToast]);

  useEffect(() => {
    initSession(selectedPreset);
  }, [selectedPreset]);

  // Execute 1 step
  const handleStep = async () => {
    if (!session) return;
    setLoading(true);
    try {
      const res = await agentApi.stepSession(session.id);
      setSession(prev => ({
        ...prev,
        status: res.session_status,
        total_steps: res.step_number,
        stopping_reason: res.stopping_reason,
        evidence_completeness: res.evidence_completeness
      }));

      if (res.executed_action) {
        setHistory(prev => [...prev, res.executed_action]);
      }
      setCandidates(res.latest_ranking || []);
      setUnresolvedQuestions(res.unresolved_questions || []);
      setRecommendations(res.next_recommendations || []);

      if (res.next_recommendations && res.next_recommendations.length > 0) {
        const top = res.next_recommendations.find(r => r.eligible);
        if (top) setSelectedActionId(top.action_id);
      }

      onAddToast?.(
        `Step ${res.step_number} completed: ${res.executed_action?.action_name || 'Action finished'}`,
        'success'
      );
    } catch (err) {
      console.error(err);
      onAddToast?.(`Step failed: ${err.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  // Run full adaptive loop
  const handleRunFull = async () => {
    if (!session) return;
    setLoading(true);
    try {
      const res = await agentApi.runSession(session.id);
      setSession(res);
      setHistory(res.action_history || []);
      setCandidates(res.latest_ranking || []);
      setUnresolvedQuestions(res.unresolved_questions || []);

      // Refresh recommendations
      const recs = await agentApi.getRecommendations(session.id).catch(() => []);
      setRecommendations(recs);

      onAddToast?.(`Diagnostic loop completed in ${res.total_steps} steps.`, 'success');
    } catch (err) {
      console.error(err);
      onAddToast?.(`Diagnostic run failed: ${err.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  // Stop session
  const handleStop = async () => {
    if (!session) return;
    setLoading(true);
    try {
      const res = await agentApi.stopSession(session.id);
      setSession(res);
      onAddToast?.('Diagnostic session stopped by operator.', 'warning');
    } catch (err) {
      console.error(err);
      onAddToast?.(`Failed to stop session: ${err.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  // Save Config
  const handleSaveConfig = async (newConfig) => {
    try {
      const updated = await agentApi.updateConfig(newConfig);
      setConfig(updated);
      onAddToast?.('Agent policy configuration updated successfully.', 'success');
    } catch (err) {
      console.error(err);
      onAddToast?.(`Failed to update config: ${err.message}`, 'error');
    }
  };

  const isTerminal = session?.status === 'COMPLETED' || session?.status === 'STOPPED' || session?.status === 'FAILED';
  const latestAction = history.length > 0 ? history[history.length - 1] : null;

  return (
    <div className="agent-dashboard">
      {/* Header bar */}
      <div className="agent-header">
        <div className="agent-title-group">
          <h2>
            <Bot size={24} color="#38bdf8" />
            <span>Module 5: Adaptive AI Diagnostic Agent</span>
          </h2>
          <p>
            Autonomous uncertainty reduction & safe read-only diagnostic action selection
          </p>
        </div>

        <div className="agent-control-buttons">
          <button 
            className="btn-agent-secondary"
            onClick={() => setIsEvalOpen(true)}
            title="View reproducible benchmark evaluation matrix"
          >
            <Award size={15} color="#f59e0b" />
            <span>Benchmark Matrix</span>
          </button>

          <button 
            className="btn-agent-secondary"
            onClick={() => setIsAuditOpen(true)}
            disabled={!session}
            title="Inspect reproducible audit trail"
          >
            <FileText size={15} color="#38bdf8" />
            <span>Audit Trail</span>
          </button>

          <button 
            className="btn-agent-secondary"
            onClick={() => setIsConfigOpen(true)}
            title="Configure utility weights and stopping policy"
          >
            <Sliders size={15} />
            <span>Policy Config</span>
          </button>

          <button 
            className="btn-agent-secondary"
            onClick={() => initSession(selectedPreset)}
            disabled={loading}
            title="Initialize a new diagnostic session"
          >
            <RotateCcw size={15} />
            <span>Reset / New</span>
          </button>

          <button 
            className="btn-agent-primary"
            onClick={handleStep}
            disabled={loading || isTerminal}
            title="Execute exactly 1 diagnostic step"
          >
            <StepForward size={15} />
            <span>Execute 1 Step</span>
          </button>

          <button 
            className="btn-agent-primary"
            onClick={handleRunFull}
            disabled={loading || isTerminal}
            style={{ background: 'linear-gradient(135deg, #10b981, #059669)' }}
            title="Run loop adaptively until stopping criteria met"
          >
            <Play size={15} />
            <span>Run Adaptive Loop</span>
          </button>

          {!isTerminal && (
            <button 
              className="btn-agent-danger"
              onClick={handleStop}
              disabled={loading}
              title="Request safe stop for active session"
            >
              <Square size={14} />
              <span>Stop</span>
            </button>
          )}
        </div>
      </div>

      {/* Preset Incident Selector */}
      <div className="preset-bar">
        <span style={{ fontSize: '0.78rem', color: '#94a3b8', fontWeight: 600, marginRight: '4px' }}>
          Incident Presets:
        </span>
        {INCIDENT_PRESETS.map((p, idx) => (
          <button
            key={idx}
            className={`preset-pill ${selectedPreset.name === p.name ? 'active' : ''}`}
            onClick={() => setSelectedPreset(p)}
            title={p.desc}
          >
            {p.name}
          </button>
        ))}
      </div>

      {/* Status KPI Bar */}
      <AgentStatusCard 
        session={session} 
        targetService={selectedPreset.targetService} 
        config={config} 
      />

      {/* Main 2-Column Dashboard Grid */}
      <div className="agent-main-grid">
        {/* Left Column: Actions & Candidates */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <DiagnosticActionList 
            recommendations={recommendations}
            selectedActionId={selectedActionId}
            onSelectAction={setSelectedActionId}
            loading={loading}
          />

          <CandidateComparison 
            candidates={candidates} 
          />
        </div>

        {/* Right Column: Reasoning & Timeline */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <ActionReasoningPanel 
            session={session}
            unresolvedQuestions={unresolvedQuestions}
            latestAction={latestAction}
            config={config}
          />

          <AgentExecutionTimeline 
            history={history} 
          />
        </div>
      </div>

      {/* Modals */}
      <AgentConfiguration 
        isOpen={isConfigOpen}
        onClose={() => setIsConfigOpen(false)}
        currentConfig={config}
        onSaveConfig={handleSaveConfig}
      />

      <AgentAuditLog 
        isOpen={isAuditOpen}
        onClose={() => setIsAuditOpen(false)}
        session={session}
      />

      <AgentEvaluationModal 
        isOpen={isEvalOpen}
        onClose={() => setIsEvalOpen(false)}
      />
    </div>
  );
}
