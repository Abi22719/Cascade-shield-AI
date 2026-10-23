import React from 'react';
import { HelpCircle } from 'lucide-react';

export default function EmptyState({
  icon: Icon = HelpCircle,
  title = 'No Data Available',
  description = 'There are no active records matching the current parameters.',
  actionLabel = null,
  onAction = null,
  className = ''
}) {
  return (
    <div className={`empty-state-container ${className}`}>
      <div className="empty-state-icon-wrapper">
        <Icon size={32} className="empty-state-icon" />
      </div>
      <h3 className="empty-state-title">{title}</h3>
      <p className="empty-state-description">{description}</p>
      {actionLabel && onAction && (
        <button className="btn btn-primary empty-state-btn" onClick={onAction}>
          {actionLabel}
        </button>
      )}
    </div>
  );
}
