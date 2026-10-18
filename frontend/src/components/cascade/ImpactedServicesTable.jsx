import React, { useState, useMemo } from 'react';
import { Search, Filter, GitFork, AlertCircle, Shield, ChevronRight } from 'lucide-react';

export default function ImpactedServicesTable({
  impactedServices = [],
  onSelectService,
  onViewPaths,
  selectedServiceId
}) {
  const [searchTerm, setSearchTerm] = useState('');
  const [impactFilter, setImpactFilter] = useState('ALL');
  const [riskFilter, setRiskFilter] = useState('ALL');

  const filteredServices = useMemo(() => {
    return impactedServices.filter((s) => {
      // Search filter
      const matchesSearch =
        s.service_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        s.service_id.toLowerCase().includes(searchTerm.toLowerCase());

      // Impact type filter
      const matchesImpact =
        impactFilter === 'ALL' ||
        (impactFilter === 'ROOT' && s.impact_type === 'Root Failure') ||
        (impactFilter === 'DIRECT' && s.impact_type === 'Direct') ||
        (impactFilter === 'INDIRECT' && s.impact_type === 'Indirect');

      // Risk level filter
      const matchesRisk =
        riskFilter === 'ALL' || s.risk_level.toUpperCase() === riskFilter;

      return matchesSearch && matchesImpact && matchesRisk;
    });
  }, [impactedServices, searchTerm, impactFilter, riskFilter]);

  const getRiskBadgeClass = (level) => {
    switch (level?.toLowerCase()) {
      case 'critical':
        return 'risk-badge critical';
      case 'high':
        return 'risk-badge high';
      case 'moderate':
        return 'risk-badge moderate';
      default:
        return 'risk-badge low';
    }
  };

  const getImpactTagClass = (type) => {
    switch (type) {
      case 'Root Failure':
        return 'impact-type-tag root';
      case 'Direct':
        return 'impact-type-tag direct';
      default:
        return 'impact-type-tag indirect';
    }
  };

  return (
    <div className="cascade-table-wrapper">
      <div className="table-top-bar">
        <h3>
          <Shield size={16} color="#3b82f6" />
          Impacted Services Assessment ({filteredServices.length} of {impactedServices.length})
        </h3>

        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          {/* Search Input */}
          <div style={{ position: 'relative' }}>
            <input
              type="text"
              className="form-input"
              style={{ paddingLeft: '28px', width: '180px' }}
              placeholder="Search service..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <Search
              size={14}
              style={{
                position: 'absolute',
                left: '8px',
                top: '50%',
                transform: 'translateY(-50%)',
                color: 'var(--text-muted)'
              }}
            />
          </div>

          {/* Impact Type Filter */}
          <select
            className="form-select"
            value={impactFilter}
            onChange={(e) => setImpactFilter(e.target.value)}
          >
            <option value="ALL">All Impact Types</option>
            <option value="ROOT">Root Failure Only</option>
            <option value="DIRECT">Direct Callers (Hop 1)</option>
            <option value="INDIRECT">Indirect Callers (Hop 2+)</option>
          </select>

          {/* Risk Level Filter */}
          <select
            className="form-select"
            value={riskFilter}
            onChange={(e) => setRiskFilter(e.target.value)}
          >
            <option value="ALL">All Risk Levels</option>
            <option value="CRITICAL">Critical Risk (75-100)</option>
            <option value="HIGH">High Risk (50-74)</option>
            <option value="MODERATE">Moderate Risk (25-49)</option>
            <option value="LOW">Low Risk (0-24)</option>
          </select>
        </div>
      </div>

      <div style={{ overflowX: 'auto' }}>
        <table className="cascade-table">
          <thead>
            <tr>
              <th>Service</th>
              <th>Impact Scope</th>
              <th>Hops</th>
              <th>Risk Score</th>
              <th>Failure Probability</th>
              <th>Recommended Resilience Action</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredServices.length === 0 ? (
              <tr>
                <td colSpan="7" style={{ textAlign: 'center', padding: '30px', color: 'var(--text-muted)' }}>
                  No services match the active filter criteria or no cascade prediction has been generated yet.
                </td>
              </tr>
            ) : (
              filteredServices.map((svc) => {
                const isSelected = selectedServiceId === svc.service_id;
                return (
                  <tr
                    key={svc.service_id}
                    style={{
                      background: isSelected ? 'rgba(59, 130, 246, 0.12)' : undefined,
                      cursor: 'pointer'
                    }}
                    onClick={() => onSelectService && onSelectService(svc.service_id)}
                  >
                    <td>
                      <div style={{ fontWeight: 600, color: 'var(--text-main)' }}>
                        {svc.service_name}
                      </div>
                      <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                        {svc.service_id} · {svc.service_type}
                      </div>
                    </td>

                    <td>
                      <span className={getImpactTagClass(svc.impact_type)}>
                        {svc.impact_type}
                      </span>
                    </td>

                    <td style={{ fontWeight: 600 }}>
                      {svc.hop_distance === 0 ? 'Origin' : `${svc.hop_distance} hop${svc.hop_distance > 1 ? 's' : ''}`}
                    </td>

                    <td>
                      <span className={getRiskBadgeClass(svc.risk_level)}>
                        {svc.estimated_risk_score} pts · {svc.risk_level}
                      </span>
                    </td>

                    <td style={{ fontWeight: 600 }}>
                      {(svc.propagation_probability_estimate * 100).toFixed(0)}%
                    </td>

                    <td style={{ maxWidth: '320px', fontSize: '0.78rem', color: 'var(--text-muted)', lineHeight: 1.3 }}>
                      {svc.recommended_monitoring_action}
                    </td>

                    <td>
                      <button
                        type="button"
                        className="timeline-btn"
                        style={{ padding: '4px 8px', fontSize: '0.75rem' }}
                        onClick={(e) => {
                          e.stopPropagation();
                          if (onViewPaths) onViewPaths(svc);
                        }}
                        title="View Detailed Propagation Paths"
                      >
                        <GitFork size={12} />
                        Paths ({svc.failure_paths?.length || 0})
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
