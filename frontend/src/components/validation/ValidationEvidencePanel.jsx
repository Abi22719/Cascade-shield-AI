import React from 'react';
import { Database, FileText, Layers, Tag } from 'lucide-react';

export default function ValidationEvidencePanel({ evidence }) {
  if (!evidence || evidence.length === 0) {
    return (
      <div className="val-card">
        <div className="val-card-header">
          <h3>Evidence Grounding & Lineage</h3>
        </div>
        <p style={{ fontSize: '0.82rem', color: '#94a3b8' }}>
          No evidence records grounded for this run.
        </p>
      </div>
    );
  }

  const getLineageColor = (lineage) => {
    switch (lineage) {
      case 'observed': return '#10b981';
      case 'simulated': return '#0ea5e9';
      case 'synthetic': return '#f59e0b';
      default: return '#a855f7';
    }
  };

  return (
    <div className="val-card">
      <div className="val-card-header">
        <h3>
          <Layers size={16} color="#0ea5e9" /> Evidence Grounding & Lineage ({evidence.length})
        </h3>
      </div>

      <div style={{ overflowX: 'auto', maxHeight: '350px' }}>
        <table className="val-check-table">
          <thead>
            <tr>
              <th>Type / Source</th>
              <th>Origin Lineage</th>
              <th>Description</th>
              <th>Step / Time</th>
            </tr>
          </thead>
          <tbody>
            {evidence.map(e => (
              <tr key={e.id}>
                <td>
                  <strong style={{ textTransform: 'capitalize' }}>{e.evidence_type.replace('_', ' ')}</strong>
                  <span style={{ display: 'block', fontSize: '0.7rem', color: '#64748b' }}>
                    {e.source_module.toUpperCase()} {e.source_record_id ? `| ${e.source_record_id}` : ''}
                  </span>
                </td>
                <td>
                  <span
                    style={{
                      padding: '0.15rem 0.45rem',
                      borderRadius: '4px',
                      fontSize: '0.68rem',
                      fontWeight: 700,
                      background: 'rgba(255, 255, 255, 0.05)',
                      color: getLineageColor(e.observed_or_simulated),
                      border: `1px solid ${getLineageColor(e.observed_or_simulated)}40`
                    }}
                  >
                    {e.observed_or_simulated.toUpperCase()}
                  </span>
                </td>
                <td style={{ fontSize: '0.75rem', maxWidth: '320px' }}>{e.description}</td>
                <td style={{ fontSize: '0.72rem', color: '#94a3b8' }}>
                  {e.timestamp_or_step ? `Step +${e.timestamp_or_step}` : '-'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
