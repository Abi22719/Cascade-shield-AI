import React from 'react';

export default function StatusBadge({ 
  status = 'HEALTHY', 
  pulse = true, 
  size = 'md',
  label = null,
  className = '' 
}) {
  const norm = String(status || '').toUpperCase();
  
  let variant = 'healthy';
  let displayLabel = label || norm;

  if (norm.includes('CRIT') || norm.includes('FAIL') || norm.includes('UNAVAIL') || norm === 'DOWN') {
    variant = 'critical';
  } else if (norm.includes('WARN') || norm.includes('DEGRAD') || norm.includes('PARTIAL') || norm === 'IN_PROGRESS') {
    variant = 'warning';
  } else if (norm.includes('HEALTH') || norm.includes('SUCCESS') || norm.includes('VERIFIED') || norm === 'COMPLETED' || norm === 'PASS') {
    variant = 'healthy';
  } else if (norm.includes('SIM') || norm.includes('INFO') || norm.includes('ACTIVE')) {
    variant = 'info';
  } else {
    variant = 'neutral';
  }

  return (
    <span className={`status-badge-pill status-${variant} size-${size} ${className}`}>
      {pulse && <span className={`status-dot status-dot-${variant}`} />}
      <span className="status-badge-text">{displayLabel}</span>
    </span>
  );
}
