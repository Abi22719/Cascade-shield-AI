import React from 'react';
import { CheckCircle2, AlertTriangle, AlertOctagon, X } from 'lucide-react';

export default function NotificationToast({ toasts, onDismiss }) {
  if (!toasts || toasts.length === 0) return null;

  return (
    <div className="toast-container">
      {toasts.map(t => (
        <div key={t.id} className={`toast ${t.type || 'info'}`}>
          {t.type === 'success' && <CheckCircle2 size={18} color="#10b981" style={{ flexShrink: 0 }} />}
          {t.type === 'warning' && <AlertTriangle size={18} color="#f59e0b" style={{ flexShrink: 0 }} />}
          {t.type === 'error' && <AlertOctagon size={18} color="#ef4444" style={{ flexShrink: 0 }} />}
          
          <div style={{ flex: 1 }}>
            {t.title && <strong style={{ display: 'block', fontSize: '0.85rem' }}>{t.title}</strong>}
            <span style={{ fontSize: '0.8rem' }}>{t.message}</span>
          </div>

          <button className="toast-close" onClick={() => onDismiss(t.id)}>
            <X size={15} />
          </button>
        </div>
      ))}
    </div>
  );
}
