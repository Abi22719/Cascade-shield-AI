import React, { useState, useEffect, useCallback } from 'react';
import { 
  AlertTriangle, 
  Search, 
  Filter, 
  CheckCircle2, 
  Clock, 
  ArrowRight, 
  RefreshCw, 
  ShieldCheck, 
  ExternalLink, 
  FileText, 
  GitBranch, 
  ChevronRight, 
  LifeBuoy, 
  Activity, 
  AlertCircle,
  Eye,
  Route,
  Zap
} from 'lucide-react';
import { incidentsApi } from '../services/incidentsApi';
import StatusBadge from '../components/common/StatusBadge';
import SkeletonLoader from '../components/common/SkeletonLoader';
import EmptyState from '../components/common/EmptyState';

export default function IncidentResponsePortal({ onNavigateModule, onAddToast }) {
  const [incidents, setIncidents] = useState([]);
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [incidentDetails, setIncidentDetails] = useState(null);
  const [incidentActivity, setIncidentActivity] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingDetails, setLoadingDetails] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');

  const loadIncidents = useCallback(async () => {
    setLoading(true);
    try {
      const data = await incidentsApi.listIncidents();
      setIncidents(data);
      if (data.length > 0 && !selectedIncident) {
        setSelectedIncident(data[0].id);
      }
    } catch (err) {
      if (onAddToast) onAddToast(`Error loading incidents: ${err.message}`, 'error', 'Incident Portal');
    } finally {
      setLoading(false);
    }
  }, [selectedIncident, onAddToast]);

  const loadIncidentDetails = useCallback(async (id) => {
    if (!id) return;
    setLoadingDetails(true);
    try {
      const [details, activity] = await Promise.all([
        incidentsApi.getIncidentDetails(id),
        incidentsApi.getIncidentActivity(id).catch(() => [])
      ]);
      setIncidentDetails(details);
      setIncidentActivity(activity);
    } catch (err) {
      console.error('Error fetching incident details:', err);
    } finally {
      setLoadingDetails(false);
    }
  }, []);

  useEffect(() => {
    loadIncidents();
  }, [loadIncidents]);

  useEffect(() => {
    if (selectedIncident) {
      loadIncidentDetails(selectedIncident);
    }
  }, [selectedIncident, loadIncidentDetails]);

  const filteredIncidents = incidents.filter(inc => {
    const matchesSearch = !searchQuery || 
      inc.title.toLowerCase().includes(searchQuery.toLowerCase()) || 
      inc.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (inc.target_service_id && inc.target_service_id.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesStatus = statusFilter === 'ALL' || inc.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const totalIncidents = incidents.length;
  const openCount = incidents.filter(i => i.status !== 'RESOLVED').length;
  const criticalCount = incidents.filter(i => i.severity === 'CRITICAL').length;
  const verifiedCount = incidents.filter(i => i.verification_status === 'VERIFIED_SUCCESS').length;

  return (
    <div className="dashboard-container portal-container">
      {/* Header */}
      <div className="db-header">
        <div className="db-title-group">
          <h2>
            <AlertTriangle size={24} color="#f59e0b" />
            <span>Portal 2: Incident Response Portal</span>
          </h2>
          <p>
            Centralized Incident War Room: Live triage, root-cause candidate inspection, blast radius evaluation, and recovery validation.
          </p>
        </div>

        <div className="db-header-actions">
          <button 
            className="btn btn-primary"
            onClick={() => onNavigateModule && onNavigateModule('incident-workflow')}
          >
            <Route size={15} />
            <span>10-Step Workflow</span>
          </button>

          <button 
            className="btn btn-secondary"
            onClick={loadIncidents}
            disabled={loading}
          >
            <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Incident KPI Overview */}
      <div className="db-summary-grid">
        <div className="db-stat-card">
          <div className="stat-card-header">
            <span>Active Incidents</span>
            <AlertCircle size={18} color="#ef4444" />
          </div>
          <div className="stat-card-value" style={{ color: openCount > 0 ? '#ef4444' : '#10b981' }}>
            {openCount}
          </div>
          <div className="stat-card-subtext">{totalIncidents} total logged in session</div>
        </div>

        <div className="db-stat-card">
          <div className="stat-card-header">
            <span>Critical Severity</span>
            <ShieldCheck size={18} color="#f59e0b" />
          </div>
          <div className="stat-card-value" style={{ color: '#f59e0b' }}>
            {criticalCount}
          </div>
          <div className="stat-card-subtext">Multi-service blast radius</div>
        </div>

        <div className="db-stat-card">
          <div className="stat-card-header">
            <span>RCA Grounded</span>
            <Search size={18} color="#818cf8" />
          </div>
          <div className="stat-card-value" style={{ color: '#818cf8' }}>
            100%
          </div>
          <div className="stat-card-subtext">Causal evidence correlated</div>
        </div>

        <div className="db-stat-card">
          <div className="stat-card-header">
            <span>Verified Recoveries</span>
            <CheckCircle2 size={18} color="#10b981" />
          </div>
          <div className="stat-card-value" style={{ color: '#10b981' }}>
            {verifiedCount}
          </div>
          <div className="stat-card-subtext">5-Pillar validation verified</div>
        </div>
      </div>

      {/* Split Investigation Workspace */}
      <div className="db-columns-layout" style={{ gridTemplateColumns: 'minmax(320px, 1fr) minmax(480px, 1.6fr)' }}>
        {/* Left: Incident Queue */}
        <div className="db-panel">
          <div className="db-panel-header">
            <div className="db-panel-title">
              <AlertTriangle size={18} color="#f59e0b" />
              <span>Incident Queue ({filteredIncidents.length})</span>
            </div>

            <div style={{ display: 'flex', gap: '6px' }}>
              <select 
                className="db-select"
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                style={{ padding: '3px 8px', fontSize: '0.78rem' }}
              >
                <option value="ALL">All</option>
                <option value="INVESTIGATING">Investigating</option>
                <option value="RESOLVED">Resolved</option>
              </select>
            </div>
          </div>

          <div style={{ margin: '0.75rem 0' }}>
            <input 
              type="text"
              placeholder="Search incidents by title or service..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="db-select"
              style={{ width: '100%', fontSize: '0.82rem' }}
            />
          </div>

          {loading ? (
            <SkeletonLoader variant="card" count={3} height="100px" />
          ) : filteredIncidents.length === 0 ? (
            <EmptyState
              icon={CheckCircle2}
              title="No Incidents Found"
              description="No active incidents match your filter parameters."
            />
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem', maxHeight: '580px', overflowY: 'auto' }}>
              {filteredIncidents.map(inc => {
                const isSelected = selectedIncident === inc.id;
                return (
                  <div
                    key={inc.id}
                    onClick={() => setSelectedIncident(inc.id)}
                    style={{
                      padding: '0.85rem 1rem',
                      borderRadius: '8px',
                      background: isSelected ? 'rgba(56, 189, 248, 0.14)' : 'var(--bg-card)',
                      border: isSelected ? '1px solid #0284c7' : '1px solid var(--border-color)',
                      cursor: 'pointer',
                      transition: 'all 0.15s ease'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span className="risk-pill" style={{ 
                        background: inc.severity === 'CRITICAL' ? 'rgba(239, 68, 68, 0.15)' : 'rgba(245, 158, 11, 0.15)',
                        color: inc.severity === 'CRITICAL' ? '#ef4444' : '#f59e0b',
                        fontSize: '0.68rem',
                        fontWeight: 700
                      }}>
                        {inc.severity}
                      </span>
                      <StatusBadge status={inc.status} size="sm" />
                    </div>

                    <div style={{ fontWeight: 600, color: 'var(--text-main)', fontSize: '0.88rem', margin: '6px 0 3px 0' }}>
                      {inc.title}
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.74rem', color: 'var(--text-muted)' }}>
                      <span>Suspect: <strong style={{ color: '#38bdf8' }}>{inc.top_root_cause}</strong></span>
                      <span>Verification: <strong>{inc.verification_status}</strong></span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Right: Detailed Investigation Workspace */}
        <div className="db-panel">
          <div className="db-panel-header">
            <div className="db-panel-title">
              <Eye size={18} color="#38bdf8" />
              <span>Incident Investigation War Room</span>
            </div>

            {incidentDetails && (
              <div style={{ display: 'flex', gap: '6px' }}>
                <button
                  className="btn btn-secondary btn-sm"
                  onClick={() => onNavigateModule && onNavigateModule('root-cause-analysis')}
                  title="Open in Module 4 RCA"
                >
                  <Search size={13} />
                  <span>RCA (M4)</span>
                </button>
                <button
                  className="btn btn-secondary btn-sm"
                  onClick={() => onNavigateModule && onNavigateModule('recovery-planning')}
                  title="Open in Module 7 Recovery"
                >
                  <LifeBuoy size={13} />
                  <span>Recovery (M7)</span>
                </button>
                <button
                  className="btn btn-primary btn-sm"
                  onClick={() => onNavigateModule && onNavigateModule('incident-workflow')}
                >
                  <Route size={13} />
                  <span>Guided Workflow</span>
                </button>
              </div>
            )}
          </div>

          {loadingDetails ? (
            <SkeletonLoader variant="card" count={3} height="140px" />
          ) : !incidentDetails ? (
            <EmptyState
              icon={AlertTriangle}
              title="Select an Incident"
              description="Choose an incident from the queue on the left to begin investigation."
            />
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', marginTop: '0.5rem' }}>
              {/* Incident Header Details */}
              <div style={{ background: 'rgba(0,0,0,0.15)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '8px' }}>
                  <div>
                    <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>
                      {incidentDetails.title}
                    </h3>
                    <code style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>ID: {incidentDetails.id}</code>
                  </div>
                  <div style={{ display: 'flex', gap: '6px' }}>
                    <StatusBadge status={incidentDetails.status} />
                  </div>
                </div>
                <p style={{ fontSize: '0.84rem', color: 'var(--text-muted)', margin: '0.6rem 0 0 0' }}>
                  {incidentDetails.description}
                </p>
              </div>

              {/* Blast Radius Propagation Chain */}
              {incidentDetails.propagation_paths && incidentDetails.propagation_paths.length > 0 && (
                <div className="drill-blast-preview">
                  <div className="blast-preview-label">
                    <GitBranch size={14} color="#ec4899" />
                    <span>Downstream Cascading Failure Blast Radius:</span>
                  </div>
                  <div className="blast-nodes-chain">
                    {incidentDetails.propagation_paths[0].map((srv, idx) => (
                      <React.Fragment key={srv}>
                        <span className={`blast-node-chip ${idx === 0 ? 'root-suspect' : 'impacted'}`}>
                          {srv}
                          {idx === 0 && <span className="root-tag">ROOT</span>}
                        </span>
                        {idx < incidentDetails.propagation_paths[0].length - 1 && (
                          <ChevronRight size={14} className="blast-arrow" />
                        )}
                      </React.Fragment>
                    ))}
                  </div>
                </div>
              )}

              {/* Root Cause Ranking Suspects */}
              <div>
                <h4 style={{ fontSize: '0.88rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '0.5rem' }}>
                  Root Cause Candidates (Attribution Ranking)
                </h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  {incidentDetails.root_cause_candidates?.map((c, i) => (
                    <div 
                      key={c.service_id}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        padding: '8px 12px',
                        borderRadius: '6px',
                        background: i === 0 ? 'rgba(239, 68, 68, 0.12)' : 'var(--bg-card)',
                        border: i === 0 ? '1px solid rgba(239, 68, 68, 0.4)' : '1px solid var(--border-color)'
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ fontWeight: 700, color: i === 0 ? '#ef4444' : 'var(--text-muted)' }}>#{i + 1}</span>
                        <strong style={{ color: 'var(--text-main)' }}>{c.service_id}</strong>
                        <span className="risk-pill" style={{ fontSize: '0.7rem' }}>{c.verdict || 'Suspect'}</span>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <span style={{ fontSize: '0.76rem', color: 'var(--text-muted)' }}>Score: {c.score}/100</span>
                        <span className="status-pill status-healthy" style={{ fontSize: '0.72rem' }}>{c.confidence} Confidence</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Evidence Lineage & Uncertainty */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '0.75rem' }}>
                <div style={{ background: 'var(--bg-card)', padding: '10px 12px', borderRadius: '6px', border: '1px solid var(--border-color)' }}>
                  <strong style={{ fontSize: '0.8rem', color: '#38bdf8' }}>Grounded Evidence References:</strong>
                  <ul style={{ margin: '6px 0 0 0', paddingLeft: '1.25rem', fontSize: '0.78rem', color: 'var(--text-muted)', lineHeight: '1.5' }}>
                    {incidentDetails.evidence_references?.map((e, idx) => (
                      <li key={idx}>
                        <code>{e.id}</code> ({e.type || e.service}): {e.metric || e.description} — <em style={{ color: '#34d399' }}>{e.lineage}</em>
                      </li>
                    ))}
                  </ul>
                </div>

                {incidentDetails.uncertainty_notes && (
                  <div className="insight-uncertainty">
                    <strong>⚠️ AI Causal Bounds & Limitations: </strong>
                    {incidentDetails.uncertainty_notes}
                  </div>
                )}
              </div>

              {/* Chronological Incident Activity Stream */}
              <div>
                <h4 style={{ fontSize: '0.88rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '0.5rem' }}>
                  Incident Chronological Audit Stream
                </h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
                  {incidentActivity.map((act) => (
                    <div 
                      key={act.id}
                      style={{
                        display: 'flex',
                        alignItems: 'flex-start',
                        gap: '8px',
                        padding: '6px 10px',
                        borderRadius: '4px',
                        background: 'rgba(0,0,0,0.1)',
                        fontSize: '0.78rem'
                      }}
                    >
                      <Clock size={13} style={{ marginTop: '2px', color: '#64748b' }} />
                      <div style={{ flex: 1 }}>
                        <strong style={{ color: 'var(--text-main)' }}>{act.action}: </strong>
                        <span style={{ color: 'var(--text-muted)' }}>{act.description}</span>
                      </div>
                      <span style={{ fontSize: '0.7rem', color: '#64748b', whiteSpace: 'nowrap' }}>{act.timestamp}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
