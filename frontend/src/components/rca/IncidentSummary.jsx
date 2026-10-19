import React from 'react';
import { ShieldAlert, AlertTriangle, CheckCircle2, Clock, GitBranch, Layers } from 'lucide-react';

export default function IncidentSummary({ report }) {
  if (!report) return null;

  const primary = report.primary_root_cause;
  const affectedCount = report.affected_services?.length || 0;
  const candidateCount = report.ranked_candidates?.length || 0;
  const evidenceCount = report.evidence_count || 0;

  const getStatusBadge = (status) => {
    switch (status?.toLowerCase()) {
      case 'completed':
        return <span className="confidence-pill strong">INVESTIGATION COMPLETED</span>;
      case 'inconclusive':
        return <span className="confidence-pill insufficient">INCONCLUSIVE / AMBIGUOUS</span>;
      default:
        return <span className="confidence-pill moderate">INVESTIGATING</span>;
    }
  };

  return (
    <div className="rca-summary-grid">
      <div className="rca-summary-card accent-purple">
        <div className="card-label">
          <span>Primary Root Cause</span>
          <ShieldAlert size={16} />
        </div>
        <div className="card-value" style={{ fontSize: '1.25rem', color: primary ? '#f87171' : '#cbd5e1' }}>
          {primary ? primary.service_name : 'Unknown / Inconclusive'}
        </div>
        <div className="card-subtext">
          {primary ? `${primary.service_id} · Score ${primary.ranking_score}/100` : 'Evidence insufficient to isolate single cause'}
        </div>
      </div>

      <div className="rca-summary-card accent-red">
        <div className="card-label">
          <span>Confidence Assessment</span>
          <AlertTriangle size={16} />
        </div>
        <div className="card-value" style={{ fontSize: '1.25rem' }}>
          {primary?.confidence_label || 'Insufficient Evidence'}
        </div>
        <div className="card-subtext">
          {primary ? `Calibrated confidence: ${(primary.confidence_score * 100).toFixed(0)}%` : 'No candidate met confidence threshold'}
        </div>
      </div>

      <div className="rca-summary-card accent-orange">
        <div className="card-label">
          <span>Affected Microservices</span>
          <GitBranch size={16} />
        </div>
        <div className="card-value">{affectedCount}</div>
        <div className="card-subtext">Degraded callers in failure blast radius</div>
      </div>

      <div className="rca-summary-card accent-blue">
        <div className="card-label">
          <span>Evidence Observations</span>
          <Layers size={16} />
        </div>
        <div className="card-value">{evidenceCount}</div>
        <div className="card-subtext">Normalized signals across Modules 1, 2 & 3</div>
      </div>

      <div className="rca-summary-card accent-green">
        <div className="card-label">
          <span>Investigation Status</span>
          <Clock size={16} />
        </div>
        <div className="card-value" style={{ fontSize: '1rem', marginTop: '12px' }}>
          {getStatusBadge(report.status)}
        </div>
        <div className="card-subtext">
          Algorithm: {report.algorithm_version} · ID: {report.incident_id}
        </div>
      </div>
    </div>
  );
}
