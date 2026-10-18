import React from 'react';
import { 
  AlertTriangle, 
  AlertOctagon, 
  CheckCircle2, 
  Eye, 
  Check, 
  Search, 
  Filter, 
  ChevronLeft, 
  ChevronRight 
} from 'lucide-react';

export default function AnomalyTable({
  alerts = [],
  total = 0,
  page = 1,
  limit = 15,
  onPageChange,
  services = [],
  filterService,
  onFilterServiceChange,
  filterSeverity,
  onFilterSeverityChange,
  filterMethod,
  onFilterMethodChange,
  filterAcknowledged,
  onFilterAcknowledgedChange,
  onAcknowledge,
  onViewDetails
}) {
  const totalPages = Math.max(1, Math.ceil(total / limit));

  return (
    <div className="table-section-card">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '10px' }}>
        <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#f8fafc' }}>
          Anomaly Alerts & Historical Incidents ({total})
        </h3>

        {/* Filters Row */}
        <div className="filter-inputs-group">
          {/* Service Filter */}
          <select
            className="filter-select"
            value={filterService}
            onChange={(e) => onFilterServiceChange(e.target.value)}
          >
            <option value="">All Services</option>
            {services.map(s => (
              <option key={s.id} value={s.id}>{s.name}</option>
            ))}
          </select>

          {/* Severity Filter */}
          <select
            className="filter-select"
            value={filterSeverity}
            onChange={(e) => onFilterSeverityChange(e.target.value)}
          >
            <option value="">All Severities</option>
            <option value="Critical">Critical</option>
            <option value="Warning">Warning</option>
          </select>

          {/* Detection Method Filter */}
          <select
            className="filter-select"
            value={filterMethod}
            onChange={(e) => onFilterMethodChange(e.target.value)}
          >
            <option value="">All Detection Methods</option>
            <option value="combined">Combined</option>
            <option value="threshold">Threshold Rule</option>
            <option value="isolation_forest">Isolation Forest (ML)</option>
          </select>

          {/* Status Filter */}
          <select
            className="filter-select"
            value={filterAcknowledged}
            onChange={(e) => onFilterAcknowledgedChange(e.target.value)}
          >
            <option value="">All Statuses</option>
            <option value="false">Unacknowledged Only</option>
            <option value="true">Acknowledged Only</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div style={{ overflowX: 'auto' }}>
        <table className="custom-table">
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Service</th>
              <th>Metric / Dimension</th>
              <th>Observed / Threshold</th>
              <th>Severity</th>
              <th>Method</th>
              <th>Evidence Summary</th>
              <th>Status</th>
              <th style={{ textAlign: 'right' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {alerts.length > 0 ? (
              alerts.map(alt => {
                const timeStr = new Date(alt.created_at).toLocaleString([], {
                  month: 'short',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit',
                  second: '2-digit'
                });

                return (
                  <tr key={alt.id}>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>
                      {timeStr}
                    </td>
                    <td>
                      <strong>{alt.service_name}</strong>
                      <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
                        {alt.service_id}
                      </div>
                    </td>
                    <td>
                      <span style={{ fontFamily: 'var(--font-mono)', color: '#38bdf8' }}>
                        {alt.metric_name}
                      </span>
                    </td>
                    <td>
                      {alt.observed_value !== null && alt.observed_value !== undefined ? (
                        <span style={{ fontFamily: 'var(--font-mono)' }}>
                          {alt.observed_value.toFixed(1)}
                          {alt.threshold_value ? ` / ${alt.threshold_value.toFixed(1)}` : ''}
                        </span>
                      ) : (
                        <span style={{ color: 'var(--text-dim)' }}>Multivariate</span>
                      )}
                    </td>
                    <td>
                      <span className={`severity-pill ${alt.severity.toLowerCase()}`}>
                        {alt.severity === 'Critical' && <AlertOctagon size={11} />}
                        {alt.severity === 'Warning' && <AlertTriangle size={11} />}
                        {alt.severity === 'Normal' && <CheckCircle2 size={11} />}
                        {alt.severity}
                      </span>
                    </td>
                    <td>
                      <span className="method-tag">
                        {alt.detection_method}
                      </span>
                    </td>
                    <td style={{ maxWidth: '320px', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      <span style={{ display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                        {alt.evidence_summary}
                      </span>
                    </td>
                    <td>
                      {alt.acknowledged ? (
                        <span style={{ color: '#10b981', fontSize: '0.72rem', display: 'flex', alignItems: 'center', gap: '4px' }}>
                          <Check size={13} /> Ack
                        </span>
                      ) : (
                        <span style={{ color: '#f59e0b', fontSize: '0.72rem' }}>
                          Pending
                        </span>
                      )}
                    </td>
                    <td style={{ textAlign: 'right', whiteSpace: 'nowrap' }}>
                      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '6px' }}>
                        {!alt.acknowledged && (
                          <button
                            className="btn btn-secondary"
                            style={{ padding: '4px 8px', fontSize: '0.72rem' }}
                            onClick={() => onAcknowledge(alt.id)}
                            title="Acknowledge alert"
                          >
                            <Check size={12} />
                            <span>Ack</span>
                          </button>
                        )}
                        <button
                          className="btn-icon"
                          style={{ padding: '4px' }}
                          onClick={() => onViewDetails(alt)}
                          title="View evidence details"
                        >
                          <Eye size={14} />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })
            ) : (
              <tr>
                <td colSpan="9" style={{ textAlign: 'center', padding: '30px', color: 'var(--text-dim)' }}>
                  No anomaly alerts match the current filter criteria.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Controls */}
      <div className="pagination-footer">
        <span>
          Showing page <strong>{page}</strong> of {totalPages} ({total} alerts)
        </span>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            className="btn btn-secondary"
            style={{ padding: '4px 10px', fontSize: '0.75rem' }}
            disabled={page <= 1}
            onClick={() => onPageChange(page - 1)}
          >
            <ChevronLeft size={14} /> Previous
          </button>
          <button
            className="btn btn-secondary"
            style={{ padding: '4px 10px', fontSize: '0.75rem' }}
            disabled={page >= totalPages}
            onClick={() => onPageChange(page + 1)}
          >
            Next <ChevronRight size={14} />
          </button>
        </div>
      </div>
    </div>
  );
}
