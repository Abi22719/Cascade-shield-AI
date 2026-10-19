import React, { useState, useEffect, useCallback } from 'react';
import { 
  LifeBuoy, 
  Sparkles, 
  Play, 
  GitCompare, 
  BarChart3, 
  RotateCcw, 
  ShieldCheck, 
  ListOrdered, 
  Clock, 
  AlertTriangle,
  Award
} from 'lucide-react';
import { recoveryApi } from '../services/recoveryApi';
import { api } from '../services/api';
import RecoveryOverview from '../components/recovery/RecoveryOverview';
import RecoveryActionList from '../components/recovery/RecoveryActionList';
import RecoveryRiskPanel from '../components/recovery/RecoveryRiskPanel';
import RecoveryTimeline from '../components/recovery/RecoveryTimeline';
import RecoveryPlanComparison from '../components/recovery/RecoveryPlanComparison';
import RecoveryRecommendation from '../components/recovery/RecoveryRecommendation';
import RecoveryPlanBuilder from '../components/recovery/RecoveryPlanBuilder';
import RecoveryEvaluationModal from '../components/recovery/RecoveryEvaluationModal';
import '../styles/recovery.css';

export default function RecoveryDashboard({ onAddToast }) {
  // State
  const [plans, setPlans] = useState([]);
  const [selectedPlanId, setSelectedPlanId] = useState(null);
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [options, setOptions] = useState(null);
  const [servicesList, setServicesList] = useState([]);

  // Simulation Results & Timeline
  const [timelineEvents, setTimelineEvents] = useState([]);
  const [simulationOutcome, setSimulationOutcome] = useState(null);
  const [comparisonResult, setComparisonResult] = useState(null);

  // Loading States
  const [isSimulating, setIsSimulating] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);

  // Tab selections
  const [leftTab, setLeftTab] = useState('actions'); // 'actions' | 'timeline'
  const [rightTab, setRightTab] = useState('risk'); // 'risk' | 'recommendation' | 'comparison'

  // Modals
  const [isBuilderOpen, setIsBuilderOpen] = useState(false);
  const [isEvaluationOpen, setIsEvaluationOpen] = useState(false);

  // 1. Initial Load
  const loadInitialData = useCallback(async () => {
    try {
      const [opts, services, plansRes] = await Promise.all([
        recoveryApi.getOptions(),
        api.getServices(),
        recoveryApi.getPlans(0, 50)
      ]);

      setOptions(opts);
      setServicesList(services);

      const planItems = plansRes.plans || [];
      setPlans(planItems);

      if (planItems.length > 0 && !selectedPlanId) {
        setSelectedPlanId(planItems[0].id);
        setSelectedPlan(planItems[0]);
      } else if (planItems.length === 0) {
        // Auto-generate candidate plans for payment service if empty
        const generated = await recoveryApi.generatePlans({
          target_service_id: 'srv-payment',
          optimization_goal: 'balanced'
        });
        setPlans(generated);
        if (generated.length > 0) {
          setSelectedPlanId(generated[0].id);
          setSelectedPlan(generated[0]);
        }
      }
    } catch (err) {
      console.error('Error loading recovery planner data:', err);
      if (onAddToast) onAddToast(err.message, 'error', 'Recovery Initialization Error');
    }
  }, [selectedPlanId, onAddToast]);

  useEffect(() => {
    loadInitialData();
  }, [loadInitialData]);

  // 2. Fetch selected plan details & timeline
  useEffect(() => {
    if (!selectedPlanId) return;

    async function loadPlanDetails() {
      try {
        const [plan, timeline, results] = await Promise.all([
          recoveryApi.getPlan(selectedPlanId),
          recoveryApi.getPlanTimeline(selectedPlanId).catch(() => []),
          recoveryApi.getPlanResults(selectedPlanId).catch(() => null)
        ]);

        setSelectedPlan(plan);
        setTimelineEvents(timeline);
        setSimulationOutcome(results?.outcome || null);
      } catch (err) {
        console.error('Error fetching plan details:', err);
      }
    }

    loadPlanDetails();
  }, [selectedPlanId]);

  // 3. Action: Generate Candidate Plans
  const handleGeneratePlans = async (genReq) => {
    setIsGenerating(true);
    try {
      const generated = await recoveryApi.generatePlans(genReq);
      setPlans(generated);
      setIsBuilderOpen(false);

      if (generated.length > 0) {
        // Find balanced plan or first
        const balanced = generated.find(p => p.strategy_type === 'balanced') || generated[0];
        setSelectedPlanId(balanced.id);
        setSelectedPlan(balanced);

        // Auto compare candidate plans
        const comp = await recoveryApi.comparePlans({
          plan_ids: generated.map(p => p.id),
          optimization_priority: genReq.optimization_goal || 'balanced'
        });
        setComparisonResult(comp);
        setRightTab('recommendation');
      }

      if (onAddToast) {
        onAddToast(
          `Generated ${generated.length} candidate recovery strategies (Lowest-Risk, Fastest, Lowest-Cost, Balanced).`,
          'success',
          'Recovery Plans Generated'
        );
      }
    } catch (err) {
      if (onAddToast) onAddToast(err.message, 'error', 'Plan Generation Failed');
    } finally {
      setIsGenerating(false);
    }
  };

  // 4. Action: Create Custom Plan
  const handleCreateCustomPlan = async (customReq) => {
    try {
      const created = await recoveryApi.createPlan(customReq);
      setPlans((prev) => [created, ...prev]);
      setSelectedPlanId(created.id);
      setSelectedPlan(created);
      setIsBuilderOpen(false);
      setRightTab('risk');
      if (onAddToast) onAddToast(`Custom plan '${created.plan_name}' validated and saved.`, 'success', 'Plan Created');
    } catch (err) {
      if (onAddToast) onAddToast(err.message, 'error', 'Validation Failed');
    }
  };

  // 5. Action: Simulate Selected Plan
  const handleSimulatePlan = async () => {
    if (!selectedPlanId) return;

    setIsSimulating(true);
    try {
      const simRes = await recoveryApi.simulatePlan(selectedPlanId, { random_seed: 42 });
      setSimulationOutcome(simRes.outcome);
      setTimelineEvents(simRes.events || []);
      setLeftTab('timeline');

      // Refresh plan to update status
      const updatedPlan = await recoveryApi.getPlan(selectedPlanId);
      setSelectedPlan(updatedPlan);

      if (onAddToast) {
        onAddToast(
          `Virtual recovery simulation finished: ${simRes.outcome.replace('_', ' ')} in ${simRes.total_recovery_time} steps.`,
          simRes.outcome === 'SUCCESSFUL_RECOVERY' ? 'success' : 'warning',
          'Recovery Simulation Completed'
        );
      }
    } catch (err) {
      if (onAddToast) onAddToast(err.message, 'error', 'Simulation Failed');
    } finally {
      setIsSimulating(false);
    }
  };

  // 6. Action: Compare Candidate Plans
  const handleComparePlans = async () => {
    if (plans.length < 2) {
      if (onAddToast) onAddToast('At least 2 recovery plans are required to perform comparative trade-off analysis.', 'warning');
      return;
    }

    try {
      const planIds = plans.slice(0, 4).map(p => p.id);
      const res = await recoveryApi.comparePlans({ plan_ids: planIds, optimization_priority: 'balanced' });
      setComparisonResult(res);
      setRightTab('comparison');
      if (onAddToast) onAddToast('Compared candidate recovery strategies.', 'info', 'Comparison Ready');
    } catch (err) {
      if (onAddToast) onAddToast(err.message, 'error', 'Comparison Failed');
    }
  };

  const recommendedPlanObj = plans.find(p => p.id === comparisonResult?.recommended_plan_id) || selectedPlan;

  return (
    <div className="recovery-dashboard">
      {/* Header */}
      <div className="rec-header">
        <div className="rec-title-group">
          <h2>
            <LifeBuoy size={24} color="#10b981" />
            <span>Intelligent Recovery Planning & Risk Assessment</span>
            <span className="strategy-badge balanced">Module 7</span>
          </h2>
          <p>
            Multi-strategy recovery generation, transparent risk breakdown, constraint validation, and non-destructive virtual sandbox simulation.
          </p>
        </div>

        <div className="sim-control-buttons">
          <div className="execution-status-pill completed">
            <span className="pulse-dot"></span>
            <span>Non-Destructive Simulation (Real Cloud Modifying Prohibited)</span>
          </div>

          <button
            className="btn-rec-primary"
            onClick={() => setIsBuilderOpen(true)}
            disabled={isGenerating}
          >
            <Sparkles size={15} />
            <span>Plan Generator</span>
          </button>

          <button
            className="btn-rec-secondary"
            onClick={handleSimulatePlan}
            disabled={isSimulating || !selectedPlanId}
          >
            <Play size={15} className={isSimulating ? 'animate-spin' : ''} />
            <span>{isSimulating ? 'Simulating...' : 'Simulate Recovery'}</span>
          </button>

          <button
            className="btn-rec-secondary"
            onClick={handleComparePlans}
            disabled={plans.length < 2}
          >
            <GitCompare size={15} />
            <span>Compare Strategies</span>
          </button>

          <button
            className="btn-rec-secondary"
            onClick={() => setIsEvaluationOpen(true)}
          >
            <BarChart3 size={15} />
            <span>Benchmarks</span>
          </button>
        </div>
      </div>

      {/* KPI Overview */}
      <RecoveryOverview
        plans={plans}
        activeIncidentsCount={1}
      />

      {/* Plan Selector Bar */}
      <div className="rec-control-bar">
        <div className="rec-select-group">
          <span className="scenario-select-label">Active Plan:</span>
          <select
            value={selectedPlanId || ''}
            onChange={(e) => setSelectedPlanId(e.target.value)}
            className="rec-dropdown"
          >
            {plans.map(p => (
              <option key={p.id} value={p.id}>
                {p.plan_name} ({p.strategy_type}) - Risk: {p.risk_score.toFixed(1)}/100
              </option>
            ))}
          </select>

          {selectedPlan && (
            <span className={`strategy-badge ${selectedPlan.strategy_type}`}>
              {selectedPlan.strategy_type.replace('_', ' ')}
            </span>
          )}
        </div>

        {selectedPlan && (
          <div style={{ fontSize: '0.8rem', color: '#94a3b8', display: 'flex', alignItems: 'center', gap: '0.8rem' }}>
            <span>Target: <b>{selectedPlan.actions?.[0]?.target_service_id || 'N/A'}</b></span>
            <span>•</span>
            <span>Duration: <b>{selectedPlan.estimated_recovery_time} steps</b></span>
            <span>•</span>
            <span>Cost: <b>{selectedPlan.estimated_cost.toFixed(1)} units</b></span>
            <span>•</span>
            <span>Risk: <b style={{ color: selectedPlan.risk_score > 50 ? '#f87171' : '#34d399' }}>{selectedPlan.risk_score.toFixed(1)} ({selectedPlan.risk_level})</b></span>
          </div>
        )}
      </div>

      {/* Main Two-Column Workspace */}
      <div className="rec-workspace-grid">
        {/* Left Column: Plan Actions Sequence or Simulation Timeline */}
        <div className="rec-panel">
          <div className="rec-panel-header">
            <div style={{ display: 'flex', gap: '0.4rem' }}>
              <button
                className={`btn-rec-secondary ${leftTab === 'actions' ? 'active' : ''}`}
                style={{
                  fontSize: '0.78rem',
                  padding: '0.3rem 0.65rem',
                  backgroundColor: leftTab === 'actions' ? 'rgba(16, 185, 129, 0.2)' : undefined,
                  borderColor: leftTab === 'actions' ? '#10b981' : undefined,
                  color: leftTab === 'actions' ? '#6ee7b7' : undefined
                }}
                onClick={() => setLeftTab('actions')}
              >
                <ListOrdered size={14} />
                <span>Action Sequence ({selectedPlan?.actions?.length || 0})</span>
              </button>

              <button
                className={`btn-rec-secondary ${leftTab === 'timeline' ? 'active' : ''}`}
                style={{
                  fontSize: '0.78rem',
                  padding: '0.3rem 0.65rem',
                  backgroundColor: leftTab === 'timeline' ? 'rgba(16, 185, 129, 0.2)' : undefined,
                  borderColor: leftTab === 'timeline' ? '#10b981' : undefined,
                  color: leftTab === 'timeline' ? '#6ee7b7' : undefined
                }}
                onClick={() => setLeftTab('timeline')}
              >
                <Clock size={14} />
                <span>Simulation Events ({timelineEvents.length})</span>
              </button>
            </div>

            <span style={{ fontSize: '0.72rem', color: '#94a3b8' }}>
              Status: <b style={{ color: '#f8fafc' }}>{selectedPlan?.status || 'DRAFT'}</b>
            </span>
          </div>

          <div className="rec-panel-body">
            {leftTab === 'actions' ? (
              <RecoveryActionList actions={selectedPlan?.actions || []} />
            ) : (
              <RecoveryTimeline events={timelineEvents} outcome={simulationOutcome} />
            )}
          </div>
        </div>

        {/* Right Column: Risk Assessment, Recommendation, or Plan Comparison */}
        <div className="rec-panel">
          <div className="rec-panel-header">
            <div style={{ display: 'flex', gap: '0.4rem' }}>
              <button
                className={`btn-rec-secondary ${rightTab === 'risk' ? 'active' : ''}`}
                style={{
                  fontSize: '0.78rem',
                  padding: '0.3rem 0.65rem',
                  backgroundColor: rightTab === 'risk' ? 'rgba(16, 185, 129, 0.2)' : undefined,
                  borderColor: rightTab === 'risk' ? '#10b981' : undefined,
                  color: rightTab === 'risk' ? '#6ee7b7' : undefined
                }}
                onClick={() => setRightTab('risk')}
              >
                <AlertTriangle size={14} />
                <span>Risk Assessment</span>
              </button>

              <button
                className={`btn-rec-secondary ${rightTab === 'recommendation' ? 'active' : ''}`}
                style={{
                  fontSize: '0.78rem',
                  padding: '0.3rem 0.65rem',
                  backgroundColor: rightTab === 'recommendation' ? 'rgba(16, 185, 129, 0.2)' : undefined,
                  borderColor: rightTab === 'recommendation' ? '#10b981' : undefined,
                  color: rightTab === 'recommendation' ? '#6ee7b7' : undefined
                }}
                onClick={() => setRightTab('recommendation')}
              >
                <Award size={14} />
                <span>AI Recommendation</span>
              </button>

              <button
                className={`btn-rec-secondary ${rightTab === 'comparison' ? 'active' : ''}`}
                style={{
                  fontSize: '0.78rem',
                  padding: '0.3rem 0.65rem',
                  backgroundColor: rightTab === 'comparison' ? 'rgba(16, 185, 129, 0.2)' : undefined,
                  borderColor: rightTab === 'comparison' ? '#10b981' : undefined,
                  color: rightTab === 'comparison' ? '#6ee7b7' : undefined
                }}
                onClick={() => setRightTab('comparison')}
              >
                <GitCompare size={14} />
                <span>Strategy Matrix</span>
              </button>
            </div>
          </div>

          <div className="rec-panel-body">
            {rightTab === 'risk' && (
              <RecoveryRiskPanel plan={selectedPlan} />
            )}

            {rightTab === 'recommendation' && (
              <RecoveryRecommendation
                comparisonResult={comparisonResult}
                recommendedPlan={recommendedPlanObj}
              />
            )}

            {rightTab === 'comparison' && (
              <RecoveryPlanComparison
                comparisonResult={comparisonResult}
                onSelectPlan={(id) => {
                  setSelectedPlanId(id);
                  setRightTab('risk');
                }}
              />
            )}
          </div>
        </div>
      </div>

      {/* Modals */}
      <RecoveryPlanBuilder
        isOpen={isBuilderOpen}
        onClose={() => setIsBuilderOpen(false)}
        onGeneratePlans={handleGeneratePlans}
        onCreateCustomPlan={handleCreateCustomPlan}
        services={servicesList}
        options={options}
      />

      <RecoveryEvaluationModal
        isOpen={isEvaluationOpen}
        onClose={() => setIsEvaluationOpen(false)}
      />
    </div>
  );
}
