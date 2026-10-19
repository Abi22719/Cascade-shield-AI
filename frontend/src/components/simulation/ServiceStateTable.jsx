import React from 'react';

export default function ServiceStateTable({
  services = {},
  selectedServiceId,
  onSelectService
}) {
  const serviceList = Object.values(services);

  if (serviceList.length === 0) {
    return (
      <div style={{ textAlign: 'center', color: '#64748b', padding: '1.5rem', fontSize: '0.85rem' }}>
        No service telemetry loaded.
      </div>
    );
  }

  return (
    <div className="sim-table-container">
      <table className="sim-table">
        <thead>
          <tr>
            <th>Service</th>
            <th>Status</th>
            <th>Latency</th>
            <th>Error Rate</th>
            <th>CPU</th>
            <th>Memory</th>
            <th>Risk Score</th>
            <th>Role</th>
          </tr>
        </thead>
        <tbody>
          {serviceList.map((svc) => {
            const isSelected = svc.service_id === selectedServiceId;
            const health = svc.health_status || 'HEALTHY';

            let roleBadge = <span style={{ color: '#64748b', fontSize: '0.72rem' }}>Normal</span>;
            if (svc.is_initial_failure) {
              roleBadge = <span style={{ color: '#f87171', fontWeight: 700, fontSize: '0.72rem' }}>Initial Injected</span>;
            } else if (svc.is_impacted && !svc.is_recovered) {
              roleBadge = <span style={{ color: '#fbbf24', fontWeight: 600, fontSize: '0.72rem' }}>Cascade Impact</span>;
            } else if (svc.is_recovered) {
              roleBadge = <span style={{ color: '#60a5fa', fontWeight: 600, fontSize: '0.72rem' }}>Recovered</span>;
            }

            return (
              <tr
                key={svc.service_id}
                onClick={() => onSelectService && onSelectService(svc.service_id)}
                style={{
                  cursor: 'pointer',
                  backgroundColor: isSelected ? 'rgba(139, 92, 246, 0.15)' : undefined
                }}
              >
                <td>
                  <div style={{ fontWeight: 600, color: '#f8fafc' }}>{svc.service_name}</div>
                  <div style={{ fontSize: '0.72rem', color: '#64748b' }}>{svc.service_id}</div>
                </td>
                <td>
                  <span className={`health-badge ${health}`}>{health}</span>
                </td>
                <td>
                  <span style={{ color: svc.latency_ms > 300 ? '#fca5a5' : '#cbd5e1', fontWeight: svc.latency_ms > 300 ? 600 : 400 }}>
                    {Math.round(svc.latency_ms)} ms
                  </span>
                </td>
                <td>
                  <span style={{ color: svc.error_rate > 5 ? '#fca5a5' : '#cbd5e1', fontWeight: svc.error_rate > 5 ? 600 : 400 }}>
                    {(svc.error_rate || 0).toFixed(1)}%
                  </span>
                </td>
                <td>
                  <span style={{ color: svc.cpu_usage > 80 ? '#fca5a5' : '#cbd5e1' }}>
                    {Math.round(svc.cpu_usage || 0)}%
                  </span>
                </td>
                <td>
                  <span style={{ color: svc.memory_usage > 80 ? '#fca5a5' : '#cbd5e1' }}>
                    {Math.round(svc.memory_usage || 0)}%
                  </span>
                </td>
                <td>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                    <div style={{
                      width: '40px',
                      height: '6px',
                      background: 'rgba(255,255,255,0.1)',
                      borderRadius: '3px',
                      overflow: 'hidden'
                    }}>
                      <div style={{
                        width: `${Math.min(100, svc.risk_score || 0)}%`,
                        height: '100%',
                        background: (svc.risk_score || 0) > 60 ? '#ef4444' : (svc.risk_score || 0) > 30 ? '#f59e0b' : '#10b981'
                      }} />
                    </div>
                    <span style={{ fontWeight: 600, fontSize: '0.78rem' }}>
                      {(svc.risk_score || 0).toFixed(1)}
                    </span>
                  </div>
                </td>
                <td>{roleBadge}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
