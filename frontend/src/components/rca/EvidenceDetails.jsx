import React, { useState } from 'react';
import { X, Layers, Search, Filter } from 'lucide-react';

export default function EvidenceDetails({ evidenceItems = [], onClose }) {
  const [filterType, setFilterType] = useState('ALL');
  const [searchTerm, setSearchTerm] = useState('');

  const filtered = evidenceItems.filter(item => {
    const matchesSearch = item.service_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          item.evidence_summary.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = filterType === 'ALL' || item.evidence_type === filterType;
    return matchesSearch && matchesType;
  });

  return (
    <div className="cascade-modal-overlay" onClick={onClose}>
      <div className="cascade-modal-content" style={{ maxWidth: '950px' }} onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Layers size={18} color="#3b82f6" />
            <div>
              <h3>Normalized Evidence Registry ({filtered.length} of {evidenceItems.length})</h3>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Multi-source evidence collected across Digital Twin, Anomaly Detection & Cascade Prediction
              </span>
            </div>
          </div>
          <button className="modal-close-btn" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <div className="modal-body">
          {/* Controls */}
          <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
            <input
              type="text"
              className="form-input"
              style={{ width: '220px' }}
              placeholder="Search evidence..."
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
            />
            <select
              className="form-select"
              value={filterType}
              onChange={e => setFilterType(e.target.value)}
            >
              <option value="ALL">All Evidence Types</option>
              <option value="metric_breach">Metric Breaches</option>
              <option value="anomaly_alert">Anomaly Alerts</option>
              <option value="health_degraded">Health Degradations</option>
              <option value="cascade_risk">Cascade Predictions</option>
              <option value="contradictory_evidence">Contradictory / Normal</option>
            </select>
          </div>

          <div style={{ overflowX: 'auto', maxHeight: '550px' }}>
            <table className="cascade-table">
              <thead>
                <tr>
                  <th>Evidence ID</th>
                  <th>Service</th>
                  <th>Type</th>
                  <th>Observed / Expected</th>
                  <th>Source Module</th>
                  <th>Reliability</th>
                  <th>Summary</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map(item => (
                  <tr key={item.id} style={{ background: item.is_contradictory ? 'rgba(239, 68, 68, 0.05)' : undefined }}>
                    <td style={{ fontFamily: 'monospace', fontSize: '0.72rem', color: '#60a5fa' }}>
                      {item.id}
                    </td>
                    <td>
                      <div style={{ fontWeight: 600 }}>{item.service_name}</div>
                      <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{item.service_id}</div>
                    </td>
                    <td>
                      <span className="impact-type-tag direct" style={{ fontSize: '0.68rem' }}>
                        {item.evidence_type}
                      </span>
                    </td>
                    <td>
                      {item.observed_value !== null ? (
                        <span>{item.observed_value} / {item.expected_or_threshold_value ?? 'N/A'}</span>
                      ) : '—'}
                    </td>
                    <td style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      {item.source_module}
                    </td>
                    <td style={{ fontWeight: 600 }}>
                      {(item.reliability_score * 100).toFixed(0)}%
                    </td>
                    <td style={{ maxWidth: '280px', fontSize: '0.75rem', lineHeight: 1.35 }}>
                      {item.evidence_summary}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
