import React, { useState } from 'react';
import { CheckCircle2, AlertTriangle, XCircle, HelpCircle, Filter } from 'lucide-react';

export default function ValidationCheckList({ checks }) {
  const [activeTab, setActiveTab] = useState('ALL');
  const [searchTerm, setSearchTerm] = useState('');

  if (!checks || checks.length === 0) {
    return (
      <div className="val-card">
        <div className="val-card-header">
          <h3>Validation Checks</h3>
        </div>
        <p style={{ fontSize: '0.82rem', color: '#94a3b8' }}>
          No validation checks recorded yet. Run a validation to generate check findings.
        </p>
      </div>
    );
  }

  const tabs = [
    { id: 'ALL', label: 'All Checks' },
    { id: 'service_health', label: 'Health' },
    { id: 'metrics', label: 'Metrics' },
    { id: 'dependency', label: 'Dependency' },
    { id: 'stability', label: 'Stability' },
    { id: 'side_effects', label: 'Side-Effects' },
    { id: 'evidence', label: 'Evidence' },
  ];

  const filteredChecks = checks.filter(c => {
    const matchesTab = activeTab === 'ALL' || c.check_type === activeTab;
    const matchesSearch = searchTerm === '' ||
      c.check_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.explanation.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (c.target_service_id && c.target_service_id.toLowerCase().includes(searchTerm.toLowerCase()));
    return matchesTab && matchesSearch;
  });

  const getStatusBadge = (status) => {
    switch (status) {
      case 'PASS':
        return <span className="counter-pill pill-pass"><CheckCircle2 size={10} /> PASS</span>;
      case 'FAIL':
        return <span className="counter-pill pill-fail"><XCircle size={10} /> FAIL</span>;
      case 'WARNING':
        return <span className="counter-pill pill-warn"><AlertTriangle size={10} /> WARN</span>;
      default:
        return <span className="counter-pill pill-unknown"><HelpCircle size={10} /> UNKNOWN</span>;
    }
  };

  return (
    <div className="val-card">
      <div className="val-card-header">
        <h3>5-Pillar Validation Checks ({checks.length})</h3>
        <input
          type="text"
          placeholder="Filter checks..."
          className="val-input"
          style={{ width: '180px', fontSize: '0.75rem', padding: '0.3rem 0.6rem' }}
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap', marginBottom: '0.8rem' }}>
        {tabs.map(t => (
          <button
            key={t.id}
            onClick={() => setActiveTab(t.id)}
            style={{
              background: activeTab === t.id ? '#0ea5e9' : 'rgba(255, 255, 255, 0.05)',
              color: activeTab === t.id ? '#ffffff' : '#94a3b8',
              border: 'none',
              borderRadius: '4px',
              padding: '0.25rem 0.55rem',
              fontSize: '0.72rem',
              fontWeight: 600,
              cursor: 'pointer'
            }}
          >
            {t.label}
          </button>
        ))}
      </div>

      <div style={{ overflowX: 'auto', maxHeight: '380px' }}>
        <table className="val-check-table">
          <thead>
            <tr>
              <th>Status</th>
              <th>Pillar</th>
              <th>Check / Target</th>
              <th>Expected</th>
              <th>Actual</th>
              <th>Finding Explanation</th>
            </tr>
          </thead>
          <tbody>
            {filteredChecks.map(c => (
              <tr key={c.id}>
                <td>{getStatusBadge(c.status)}</td>
                <td style={{ fontSize: '0.72rem', color: '#94a3b8', textTransform: 'capitalize' }}>
                  {c.check_type.replace('_', ' ')}
                </td>
                <td>
                  <strong>{c.check_name}</strong>
                  {c.target_service_id && (
                    <span style={{ display: 'block', fontSize: '0.7rem', color: '#64748b' }}>
                      {c.target_service_id}
                    </span>
                  )}
                </td>
                <td style={{ color: '#94a3b8', fontSize: '0.75rem' }}>{c.expected_value || '-'}</td>
                <td style={{ fontWeight: 600, fontSize: '0.75rem' }}>{c.actual_value || '-'}</td>
                <td style={{ fontSize: '0.75rem', maxWidth: '280px' }}>{c.explanation}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
