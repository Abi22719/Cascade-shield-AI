import React, { useState } from 'react';
import { X, Copy, Download, FileText, Check } from 'lucide-react';

export default function RCAReportPanel({ report, onClose }) {
  const [copied, setCopied] = useState(false);

  if (!report) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(JSON.stringify(report, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  const handleDownload = () => {
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `rca_report_${report.incident_id}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="cascade-modal-overlay" onClick={onClose}>
      <div className="cascade-modal-content" style={{ maxWidth: '900px' }} onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <FileText size={18} color="#8b5cf6" />
            <div>
              <h3>Auditable Root Cause Analysis Investigation Report</h3>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Incident: {report.title} · ID: {report.incident_id}
              </span>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '8px' }}>
            <button className="timeline-btn" onClick={handleCopy}>
              {copied ? <Check size={14} color="#10b981" /> : <Copy size={14} />}
              {copied ? 'Copied' : 'Copy JSON'}
            </button>
            <button className="timeline-btn" onClick={handleDownload}>
              <Download size={14} />
              Export Report
            </button>
            <button className="modal-close-btn" onClick={onClose}>
              <X size={18} />
            </button>
          </div>
        </div>

        <div className="modal-body" style={{ maxHeight: '75vh', overflowY: 'auto' }}>
          {/* Executive Summary */}
          <div style={{ background: 'var(--bg-hover)', padding: '14px', borderRadius: 'var(--radius-sm)' }}>
            <h4 style={{ color: '#c4b5fd', margin: '0 0 6px 0', fontSize: '0.9rem' }}>
              Executive Attribution Summary
            </h4>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-main)', lineHeight: 1.4 }}>
              {report.confidence_and_uncertainty_explanation}
            </div>
          </div>

          {/* Primary Root Cause Attribution */}
          {report.primary_root_cause && (
            <div style={{ background: 'var(--bg-hover)', padding: '14px', borderRadius: 'var(--radius-sm)' }}>
              <h4 style={{ color: '#f87171', margin: '0 0 8px 0', fontSize: '0.9rem' }}>
                Primary Root Cause: {report.primary_root_cause.service_name} ({report.primary_root_cause.service_id})
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '8px', fontSize: '0.75rem', marginBottom: '8px' }}>
                <div>Ranking Score: <b>{report.primary_root_cause.ranking_score} / 100</b></div>
                <div>Confidence: <b>{report.primary_root_cause.confidence_label}</b></div>
                <div>Affected Callers: <b>{report.primary_root_cause.affected_services?.length || 0}</b></div>
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                {report.primary_root_cause.explanation}
              </div>
            </div>
          )}

          {/* Missing Data Gaps */}
          <div>
            <h4 style={{ color: '#60a5fa', margin: '0 0 6px 0', fontSize: '0.85rem' }}>
              Identified Observability & Data Gaps
            </h4>
            <ul style={{ paddingLeft: '18px', fontSize: '0.75rem', color: 'var(--text-muted)', margin: 0 }}>
              {report.missing_data_gaps?.map((gap, i) => (
                <li key={i}>{gap}</li>
              ))}
            </ul>
          </div>

          {/* Investigation Limitations */}
          <div>
            <h4 style={{ color: '#cbd5e1', margin: '0 0 6px 0', fontSize: '0.85rem' }}>
              Methodological Assumptions & Limitations
            </h4>
            <ul style={{ paddingLeft: '18px', fontSize: '0.75rem', color: 'var(--text-muted)', margin: 0 }}>
              {report.investigation_limitations?.map((lim, i) => (
                <li key={i}>{lim}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
