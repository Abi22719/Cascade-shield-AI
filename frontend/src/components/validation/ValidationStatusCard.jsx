import React from 'react';
import { CheckCircle2, AlertTriangle, XCircle, HelpCircle, Shield, Clock } from 'lucide-react';

export default function ValidationStatusCard({ validationRun }) {
  if (!validationRun) {
    return (
      <div className="val-status-card">
        <div className="val-outcome-banner outcome-not-run">
          <span>Validation Status: NOT_RUN</span>
          <Shield size={18} />
        </div>
        <p style={{ fontSize: '0.82rem', color: '#94a3b8', margin: 0 }}>
          Select a Module 7 recovery plan and click "Run Recovery Validation" to evaluate simulated recovery fidelity.
        </p>
      </div>
    );
  }

  const {
    overall_outcome,
    total_checks,
    passed_checks,
    failed_checks,
    warning_checks,
    unknown_checks,
    verification_window_steps,
    summary
  } = validationRun;

  const outcomeClass = {
    VERIFIED_SUCCESS: 'outcome-verified-success',
    PARTIAL_SUCCESS: 'outcome-partial-success',
    FAILED: 'outcome-failed',
    INCONCLUSIVE: 'outcome-inconclusive',
  }[overall_outcome] || 'outcome-not-run';

  const OutcomeIcon = {
    VERIFIED_SUCCESS: CheckCircle2,
    PARTIAL_SUCCESS: AlertTriangle,
    FAILED: XCircle,
    INCONCLUSIVE: HelpCircle,
  }[overall_outcome] || Shield;

  const unhealthyTargets = summary?.unhealthy_targets || [];
  const newFailures = summary?.new_failures || [];

  return (
    <div className="val-status-card">
      <div className={`val-outcome-banner ${outcomeClass}`}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <OutcomeIcon size={20} />
          <span>Outcome: {overall_outcome.replace('_', ' ')}</span>
        </div>
        <span style={{ fontSize: '0.75rem', opacity: 0.9 }}>
          Window: {verification_window_steps} steps
        </span>
      </div>

      <div className="val-checks-counter">
        <span className="counter-pill pill-pass">
          <CheckCircle2 size={12} /> {passed_checks} Passed
        </span>
        <span className="counter-pill pill-fail">
          <XCircle size={12} /> {failed_checks} Failed
        </span>
        <span className="counter-pill pill-warn">
          <AlertTriangle size={12} /> {warning_checks} Warnings
        </span>
        {unknown_checks > 0 && (
          <span className="counter-pill pill-unknown">
            <HelpCircle size={12} /> {unknown_checks} Unknown
          </span>
        )}
        <span style={{ fontSize: '0.75rem', color: '#94a3b8', marginLeft: 'auto', alignSelf: 'center' }}>
          Total Checks: <strong>{total_checks}</strong>
        </span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', fontSize: '0.8rem', borderTop: '1px solid rgba(255,255,255,0.06)', paddingTop: '0.6rem' }}>
        {unhealthyTargets.length > 0 ? (
          <div style={{ color: '#f87171' }}>
            Residual Unhealthy Targets: <strong>{unhealthyTargets.join(', ')}</strong>
          </div>
        ) : (
          <div style={{ color: '#34d399' }}>
            All target services resolved to HEALTHY.
          </div>
        )}

        {newFailures.length > 0 && (
          <div style={{ color: '#fbbf24' }}>
            Secondary Cascade Degradations: <strong>{newFailures.join(', ')}</strong>
          </div>
        )}

        {summary?.has_rollback && (
          <div style={{ color: '#f87171', fontWeight: 600 }}>
            Rollback contingency was triggered during simulation run due to precondition violation.
          </div>
        )}
      </div>
    </div>
  );
}
