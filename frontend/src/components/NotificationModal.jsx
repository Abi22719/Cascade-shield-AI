import React, { useState, useEffect, useCallback } from 'react';
import { Bell, X, Check, CheckCheck, RefreshCw, AlertTriangle, AlertCircle, Info } from 'lucide-react';
import { dashboardApi } from '../services/dashboardApi';

export default function NotificationModal({ isOpen, onClose }) {
  const [notifications, setNotifications] = useState([]);
  const [unreadOnly, setUnreadOnly] = useState(false);
  const [loading, setLoading] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);

  const loadNotifications = useCallback(async () => {
    setLoading(true);
    try {
      const res = await dashboardApi.getNotifications({ unread_only: unreadOnly });
      setNotifications(res?.notifications || []);
      setUnreadCount(res?.unread_count || 0);
    } catch (err) {
      console.error("Error loading notifications:", err);
    } finally {
      setLoading(false);
    }
  }, [unreadOnly]);

  useEffect(() => {
    if (isOpen) {
      loadNotifications();
    }
  }, [isOpen, loadNotifications]);

  if (!isOpen) return null;

  const handleMarkRead = async (id) => {
    try {
      await dashboardApi.markNotificationRead(id);
      loadNotifications();
    } catch (err) {
      console.error("Mark read error:", err);
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await dashboardApi.markAllNotificationsRead();
      loadNotifications();
    } catch (err) {
      console.error("Mark all read error:", err);
    }
  };

  const getSeverityIcon = (sev) => {
    switch (sev) {
      case 'CRITICAL': return <AlertCircle size={15} color="#ef4444" />;
      case 'WARNING': return <AlertTriangle size={15} color="#f59e0b" />;
      default: return <Info size={15} color="#38bdf8" />;
    }
  };

  return (
    <div className="search-modal-backdrop" onClick={onClose}>
      <div className="search-modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '640px' }}>
        <div className="search-input-header">
          <Bell size={20} color="#38bdf8" />
          <div style={{ flex: 1, fontWeight: 600, fontSize: '1rem', color: '#f8fafc' }}>
            System Notifications ({unreadCount} unread)
          </div>
          <button 
            onClick={onClose} 
            style={{ background: 'transparent', border: 'none', color: '#94a3b8', cursor: 'pointer' }}
          >
            <X size={20} />
          </button>
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.65rem 1.25rem', borderBottom: '1px solid rgba(255, 255, 255, 0.08)' }}>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button
              onClick={() => setUnreadOnly(false)}
              style={{
                background: !unreadOnly ? 'rgba(56, 189, 248, 0.2)' : 'transparent',
                border: !unreadOnly ? '1px solid #38bdf8' : '1px solid rgba(255, 255, 255, 0.1)',
                color: !unreadOnly ? '#38bdf8' : '#94a3b8',
                padding: '0.2rem 0.6rem',
                borderRadius: '4px',
                fontSize: '0.75rem',
                cursor: 'pointer'
              }}
            >
              All
            </button>
            <button
              onClick={() => setUnreadOnly(true)}
              style={{
                background: unreadOnly ? 'rgba(56, 189, 248, 0.2)' : 'transparent',
                border: unreadOnly ? '1px solid #38bdf8' : '1px solid rgba(255, 255, 255, 0.1)',
                color: unreadOnly ? '#38bdf8' : '#94a3b8',
                padding: '0.2rem 0.6rem',
                borderRadius: '4px',
                fontSize: '0.75rem',
                cursor: 'pointer'
              }}
            >
              Unread Only
            </button>
          </div>

          {unreadCount > 0 && (
            <button
              onClick={handleMarkAllRead}
              className="btn btn-secondary"
              style={{ padding: '0.25rem 0.65rem', fontSize: '0.74rem' }}
            >
              <CheckCheck size={13} />
              <span>Mark All Read</span>
            </button>
          )}
        </div>

        <div className="search-modal-results" style={{ maxHeight: '400px' }}>
          {loading && (
            <div style={{ padding: '1rem', color: '#94a3b8', fontSize: '0.85rem' }}>
              Loading notifications...
            </div>
          )}

          {!loading && notifications.length === 0 && (
            <div style={{ padding: '2rem', textAlign: 'center', color: '#64748b', fontSize: '0.85rem' }}>
              No notifications to display.
            </div>
          )}

          {notifications.map((n) => (
            <div 
              key={n.id}
              className="search-result-row"
              style={{ 
                borderLeft: n.read_status ? '3px solid transparent' : '3px solid #38bdf8',
                opacity: n.read_status ? 0.7 : 1
              }}
            >
              <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-start' }}>
                <div style={{ marginTop: '2px' }}>
                  {getSeverityIcon(n.severity)}
                </div>
                <div>
                  <div style={{ fontWeight: 600, color: '#f8fafc', fontSize: '0.86rem' }}>{n.title}</div>
                  <div style={{ color: '#94a3b8', fontSize: '0.78rem', marginTop: '0.15rem' }}>{n.message}</div>
                  <div style={{ fontSize: '0.7rem', color: '#64748b', marginTop: '0.35rem' }}>
                    Module: {n.source_module} • {new Date(n.created_at).toLocaleTimeString()}
                  </div>
                </div>
              </div>

              {!n.read_status && (
                <button
                  onClick={() => handleMarkRead(n.id)}
                  title="Mark as read"
                  style={{
                    background: 'rgba(255, 255, 255, 0.05)',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    color: '#cbd5e1',
                    borderRadius: '4px',
                    padding: '0.25rem 0.45rem',
                    cursor: 'pointer'
                  }}
                >
                  <Check size={12} />
                </button>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
