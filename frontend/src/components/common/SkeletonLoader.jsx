import React from 'react';

export default function SkeletonLoader({ 
  variant = 'card', 
  count = 1, 
  height = null, 
  width = '100%',
  className = '' 
}) {
  const items = Array.from({ length: count }, (_, i) => i);

  if (variant === 'card') {
    return (
      <div className={`skeleton-grid ${className}`}>
        {items.map(idx => (
          <div key={idx} className="skeleton-card" style={{ height: height || '120px' }}>
            <div className="skeleton-line title" style={{ width: '40%' }}></div>
            <div className="skeleton-line metric" style={{ width: '60%', height: '28px' }}></div>
            <div className="skeleton-line text" style={{ width: '80%' }}></div>
          </div>
        ))}
      </div>
    );
  }

  if (variant === 'table') {
    return (
      <div className={`skeleton-table-wrapper ${className}`}>
        {items.map(idx => (
          <div key={idx} className="skeleton-table-row">
            <div className="skeleton-line" style={{ width: '20%' }}></div>
            <div className="skeleton-line" style={{ width: '35%' }}></div>
            <div className="skeleton-line" style={{ width: '15%' }}></div>
            <div className="skeleton-line" style={{ width: '15%' }}></div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className={`skeleton-generic-list ${className}`}>
      {items.map(idx => (
        <div 
          key={idx} 
          className="skeleton-line" 
          style={{ 
            height: height || '20px', 
            width: width, 
            marginBottom: '8px' 
          }} 
        />
      ))}
    </div>
  );
}
