import React, { useState, useEffect, useCallback } from 'react';
import { 
  ShieldCheck, 
  RotateCw, 
  Award, 
  CheckSquare, 
  GitCompare, 
  Clock, 
  Layers, 
  Lightbulb,
  FileCheck
} from 'lucide-react';
import { validationApi } from '../services/validationApi';
import { recoveryApi } from '../services/recoveryApi';
import ValidationOverview from '../components/validation/ValidationOverview';
import RecoveryRunSelector from '../components/validation/RecoveryRunSelector';
import ValidationStatusCard from '../components/validation/ValidationStatusCard';
import ValidationCheckList from '../components/validation/ValidationCheckList';
import BeforeAfterComparison from '../components/validation/BeforeAfterComparison';
import ValidationTimeline from '../components/validation/ValidationTimeline';
import ValidationEvidencePanel from '../components/validation/ValidationEvidencePanel';
import ValidationRecommendations from '../components/validation/ValidationRecommendations';
import ValidationEvaluationModal from '../components/validation/ValidationEvaluationModal';
import '../styles/validation.css';

export default function RecoveryValidationDashboard({ onAddToast }) {
  const [plans, setPlans] = useState([]);
  const [selectedPlanId, setSelectedPlanId] = useState(null);
  const [verificationSteps, setVerificationSteps] = useState(3);

  const [validationRuns, setValidationRuns] = useState([]);
  const [activeValidation, setActiveValidation] = useState(null);
  const [timelineEvents, setTimelineEvents] = useState([]);

  const [loading, setLoading] = useState(false);
  const [activeViewTab, setActiveViewTab] = useState('checks'); // 'checks' | 'comparison' | 'timeline' | 'evidence' | 'recommendations'
  const [isEvaluationOpen, setIsEvaluationOpen] = useState(false);

  // 1. Initial Load of Plans and Runs
  const loadInitialData = useCallback(async () => {
    setLoading(true);
    try {
      const [plansRes, runsRes] = await Promise.all([
        recoveryApi.getPlans(0, 50).catch(() => ({ items: [] })),
        validationApi.getRuns(0, 50).catch(() => ({ items: [] }))
      ]);

      const planList = plansRes.items || [];
      setPlans(planList);

      const runList = runsRes.items || [];
      setValidationRuns(runList);

      if (planList.length > 0 && !selectedPlanId) {
        setSelectedPlanId(planList[0].id);
      }

      if (runList.length > 0) {
        // Load latest validation run detail
        const latestDetail = await validationApi.getRun(runList[0].id);
        setActiveValidation(latestDetail);
        loadTimeline(runList[0].id);
      }
    } catch (err) {
      if (onAddToast) onAddToast(err.message, 'error', 'Data Load Failed');
    } finally {
      setLoading(false);
    }
  }, [onAddToast, selectedPlanId]);

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadTimeline = async (valId) => {
    try {
      const tlRes = await validationApi.getTimeline(valId);
      setTimelineEvents(tlRes.timeline || []);
    } catch (err) {
      console.error('Failed to load timeline:', err);
    }
  };

  // 2. Run Validation Handler
  const handleRunValidation = async (forceRerun = false) => {
    if (!selectedPlanId) return;
    setLoading(true);
    try {
      const result = await validationApi.runValidation({
        recovery_plan_id: selectedPlanId,
        verification_window_steps: verificationSteps,
        force_rerun: forceRerun
      });

      setActiveValidation(result);
      await loadTimeline(result.id);

      // Refresh runs list
      const runsRes = await validationApi.getRuns(0, 50);
      setValidationRuns(runsRes.items || []);

      if (onAddToast) {
        onAddToast(
          `Validation finished with outcome: ${result.overall_outcome}`,
          result.overall_outcome === 'VERIFIED_SUCCESS' ? 'success' : (result.overall_outcome === 'FAILED' ? 'error' : 'warning'),
          'Validation Completed'
        );
      }
    } catch (err) {
      if (onAddToast) onAddToast(err.message, 'error', 'Validation Failed');
    } finally {
      setLoading(false);
    }
  };

  // Calculate summary stats for KPI cards
  const summaryStats = {
    total: validationRuns.length,
    verified_success: validationRuns.filter(r => r.overall_outcome === 'VERIFIED_SUCCESS').length,
    partial_success: validationRuns.filter(r => r.overall_outcome === 'PARTIAL_SUCCESS').length,
    failed: validationRuns.filter(r => r.overall_outcome === 'FAILED').length,
    inconclusive: validationRuns.filter(r => r.overall_outcome === 'INCONCLUSIVE').length,
  };

  return (
    <div className="validation-dashboard">
      {/* Header */}
      <div className="val-header">
        <div className="val-title-group">
          <h2>
            <ShieldCheck size={26} color="#0ea5e9" />
            Module 8: Automated Recovery Validation and Verification
          </h2>
          <p>
            Verifies simulated recovery success across service health, telemetry SLA thresholds, downstream dependencies, and multi-step stability.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.6rem' }}>
          <button
            className="btn-val-secondary"
            onClick={() => setIsEvaluationOpen(true)}
          >
            <Award size={14} color="#0ea5e9" />
            Strategy Benchmark
          </button>
          <button
            className="btn-val-secondary"
            onClick={loadInitialData}
            disabled={loading}
          >
            <RotateCw size={14} className={loading ? 'spin' : ''} />
            Refresh
          </button>
        </div>
      </div>

      {/* KPI Overview Cards */}
      <ValidationOverview summaryStats={summaryStats} />

      {/* Selector & Run Control Bar */}
      <RecoveryRunSelector
        plans={plans}
        selectedPlanId={selectedPlanId}
        onSelectPlan={setSelectedPlanId}
        verificationSteps={verificationSteps}
        onChangeVerificationSteps={setVerificationSteps}
        onRunValidation={handleRunValidation}
        loading={loading}
      />

      {/* Outcome Status Card */}
      <ValidationStatusCard validationRun={activeValidation} />

      {/* Main View Tabs */}
      <div style={{ display: 'flex', gap: '0.5rem', borderBottom: '1px solid rgba(255, 255, 255, 0.08)', paddingBottom: '0.4rem' }}>
        <button
          onClick={() => setActiveViewTab('checks')}
          style={{
            background: activeViewTab === 'checks' ? 'rgba(14, 165, 233, 0.2)' : 'transparent',
            color: activeViewTab === 'checks' ? '#38bdf8' : '#94a3b8',
            border: activeViewTab === 'checks' ? '1px solid rgba(14, 165, 233, 0.4)' : '1px solid transparent',
            borderRadius: '6px',
            padding: '0.4rem 0.85rem',
            fontSize: '0.8rem',
            fontWeight: 600,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem'
          }}
        >
          <CheckSquare size={14} /> 5-Pillar Checks ({activeValidation?.checks?.length || 0})
        </button>

        <button
          onClick={() => setActiveViewTab('comparison')}
          style={{
            background: activeViewTab === 'comparison' ? 'rgba(14, 165, 233, 0.2)' : 'transparent',
            color: activeViewTab === 'comparison' ? '#38bdf8' : '#94a3b8',
            border: activeViewTab === 'comparison' ? '1px solid rgba(14, 165, 233, 0.4)' : '1px solid transparent',
            borderRadius: '6px',
            padding: '0.4rem 0.85rem',
            fontSize: '0.8rem',
            fontWeight: 600,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem'
          }}
        >
          <GitCompare size={14} /> Before-and-After Comparison
        </button>

        <button
          onClick={() => setActiveViewTab('timeline')}
          style={{
            background: activeViewTab === 'timeline' ? 'rgba(14, 165, 233, 0.2)' : 'transparent',
            color: activeViewTab === 'timeline' ? '#38bdf8' : '#94a3b8',
            border: activeViewTab === 'timeline' ? '1px solid rgba(14, 165, 233, 0.4)' : '1px solid transparent',
            borderRadius: '6px',
            padding: '0.4rem 0.85rem',
            fontSize: '0.8rem',
            fontWeight: 600,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem'
          }}
        >
          <Clock size={14} /> Validation Timeline ({timelineEvents.length})
        </button>

        <button
          onClick={() => setActiveViewTab('evidence')}
          style={{
            background: activeViewTab === 'evidence' ? 'rgba(14, 165, 233, 0.2)' : 'transparent',
            color: activeViewTab === 'evidence' ? '#38bdf8' : '#94a3b8',
            border: activeViewTab === 'evidence' ? '1px solid rgba(14, 165, 233, 0.4)' : '1px solid transparent',
            borderRadius: '6px',
            padding: '0.4rem 0.85rem',
            fontSize: '0.8rem',
            fontWeight: 600,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem'
          }}
        >
          <Layers size={14} /> Evidence Grounding ({activeValidation?.evidence?.length || 0})
        </button>

        <button
          onClick={() => setActiveViewTab('recommendations')}
          style={{
            background: activeViewTab === 'recommendations' ? 'rgba(14, 165, 233, 0.2)' : 'transparent',
            color: activeViewTab === 'recommendations' ? '#38bdf8' : '#94a3b8',
            border: activeViewTab === 'recommendations' ? '1px solid rgba(14, 165, 233, 0.4)' : '1px solid transparent',
            borderRadius: '6px',
            padding: '0.4rem 0.85rem',
            fontSize: '0.8rem',
            fontWeight: 600,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem'
          }}
        >
          <Lightbulb size={14} /> Next Steps ({activeValidation?.recommendations?.length || 0})
        </button>
      </div>

      {/* Tab Panels */}
      <div>
        {activeViewTab === 'checks' && (
          <ValidationCheckList checks={activeValidation?.checks} />
        )}

        {activeViewTab === 'comparison' && (
          <BeforeAfterComparison comparison={activeValidation?.comparison} />
        )}

        {activeViewTab === 'timeline' && (
          <ValidationTimeline timeline={timelineEvents} />
        )}

        {activeViewTab === 'evidence' && (
          <ValidationEvidencePanel evidence={activeValidation?.evidence} />
        )}

        {activeViewTab === 'recommendations' && (
          <ValidationRecommendations recommendations={activeValidation?.recommendations} />
        )}
      </div>

      {/* Evaluation Modal */}
      <ValidationEvaluationModal
        isOpen={isEvaluationOpen}
        onClose={() => setIsEvaluationOpen(false)}
      />
    </div>
  );
}
