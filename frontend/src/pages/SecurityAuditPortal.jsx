import React, { useState, useEffect, useCallback } from 'react';
import {
  ShieldCheck,
  Lock,
  UserCheck,
  Users,
  FileCheck,
  Search,
  Filter,
  RefreshCw,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Clock,
  Eye,
  Key,
  ShieldAlert,
  ChevronRight,
  Database
} from 'lucide-react';
import { securityApi } from '../services/securityApi';
import StatusBadge from '../components/common/StatusBadge';
import SkeletonLoader from '../components/common/SkeletonLoader';

export default function SecurityAuditPortal({ onNavigateModule, onAddToast }) {
  const [activeTab, setActiveTab] = useState('users'); // 'users' | 'roles' | 'audit'
  const [users, setUsers] = useState([]);
  const [roles, setRoles] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [overview, setOverview] = useState(null);
  const [loading, setLoading] = useState(false);

  // Filters
  const [searchUser, setSearchUser] = useState('');
  const [searchAudit, setSearchAudit] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');

  // Selected Log Modal
  const [selectedLog, setSelectedLog] = useState(null);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [uList, rList, aList, ov] = await Promise.all([
        securityApi.getUsers().catch(() => []),
        securityApi.getRoles().catch(() => []),
        securityApi.getAuditLogs({ limit: 100 }).catch(() => []),
        securityApi.getOverview().catch(() => null)
      ]);
      setUsers(uList || []);
      setRoles(rList || []);
      setAuditLogs(aList || []);
      setOverview(ov);
    } catch (err) {
      console.warn('Security portal data fetch:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Role Assignment
  const handleRoleChange = async (userId, newRole) => {
    try {
      await securityApi.updateUserRole(userId, newRole);
      setUsers(prev => prev.map(u => u.id === userId ? { ...u, role: newRole } : u));
      if (onAddToast) onAddToast(`Updated role for ${userId} to ${newRole}`, 'success', 'Role Updated');
      // Refresh audit logs to record the role change
      const freshLogs = await securityApi.getAuditLogs({ limit: 100 }).catch(() => []);
      setAuditLogs(freshLogs);
    } catch (err) {
      console.error('Failed to update role:', err);
      if (onAddToast) onAddToast(err.message, 'error', 'Role Update Failed');
    }
  };

  const filteredUsers = users.filter(u => {
    if (!searchUser) return true;
    const q = searchUser.toLowerCase();
    return u.username?.toLowerCase().includes(q) || u.email?.toLowerCase().includes(q) || u.role?.toLowerCase().includes(q);
  });

  const filteredLogs = auditLogs.filter(l => {
    const matchesSearch = !searchAudit || 
      l.action?.toLowerCase().includes(searchAudit.toLowerCase()) || 
      l.actor_id?.toLowerCase().includes(searchAudit.toLowerCase()) || 
      l.resource_id?.toLowerCase().includes(searchAudit.toLowerCase());
    const matchesStatus = statusFilter === 'ALL' || l.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="portal-container animate-fade-in" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Top Banner */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <div style={{ background: 'rgba(239, 68, 68, 0.15)', padding: '0.4rem', borderRadius: '8px', color: '#ef4444' }}>
              <Lock size={22} />
            </div>
            <h1 style={{ fontSize: '1.4rem', fontWeight: 700, margin: 0, color: 'var(--text-primary, #f8fafc)' }}>
              Security and Audit Portal
            </h1>
            <span style={{ fontSize: '0.72rem', background: '#3b82f622', color: '#60a5fa', padding: '0.15rem 0.5rem', borderRadius: '4px', border: '1px solid #3b82f644' }}>
              PORTAL 7
            </span>
            <span style={{ fontSize: '0.72rem', background: '#10b98122', color: '#34d399', padding: '0.15rem 0.5rem', borderRadius: '4px', border: '1px solid #10b98144' }}>
              IMMUTABLE AUDIT TRAIL
            </span>
          </div>
          <p style={{ margin: '0.25rem 0 0', fontSize: '0.85rem', color: 'var(--text-secondary, #94a3b8)' }}>
            Enterprise Role-Based Access Control (RBAC), multi-role permissions matrix, and tamper-resistant audit logs.
          </p>
        </div>

        {/* Global Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <button
            onClick={loadData}
            disabled={loading}
            className="header-secondary-btn"
            style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', padding: '0.5rem 0.85rem', borderRadius: '6px', cursor: 'pointer' }}
          >
            <RefreshCw size={14} className={loading ? 'spin-icon' : ''} />
            <span>Refresh Security Data</span>
          </button>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="portal-tabs-nav" style={{ display: 'flex', gap: '0.5rem', borderBottom: '1px solid var(--border-color, #1e293b)', paddingBottom: '0.5rem' }}>
        <button
          className={`portal-tab-btn ${activeTab === 'users' ? 'active' : ''}`}
          onClick={() => setActiveTab('users')}
        >
          <Users size={15} />
          <span>User Directory ({users.length})</span>
        </button>

        <button
          className={`portal-tab-btn ${activeTab === 'roles' ? 'active' : ''}`}
          onClick={() => setActiveTab('roles')}
        >
          <ShieldCheck size={15} />
          <span>RBAC Permission Matrix</span>
        </button>

        <button
          className={`portal-tab-btn ${activeTab === 'audit' ? 'active' : ''}`}
          onClick={() => setActiveTab('audit')}
        >
          <FileCheck size={15} />
          <span>Immutable Audit Log ({auditLogs.length})</span>
        </button>
      </div>

      {/* TAB 1: USER DIRECTORY & ROLE ASSIGNMENT */}
      {activeTab === 'users' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {/* Quick Metrics */}
          <div className="db-summary-grid">
            <div className="db-stat-card">
              <div className="stat-card-header">
                <span>Total Registered Users</span>
                <Users size={18} color="#38bdf8" />
              </div>
              <div className="stat-card-value" style={{ color: '#38bdf8' }}>{users.length}</div>
              <div className="stat-card-subtext">Active operator and analyst accounts</div>
            </div>

            <div className="db-stat-card">
              <div className="stat-card-header">
                <span>Active Admins</span>
                <Key size={18} color="#ef4444" />
              </div>
              <div className="stat-card-value" style={{ color: '#ef4444' }}>
                {users.filter(u => u.role === 'Administrator').length}
              </div>
              <div className="stat-card-subtext">Full platform privilege</div>
            </div>

            <div className="db-stat-card">
              <div className="stat-card-header">
                <span>Assigned RBAC Roles</span>
                <UserCheck size={18} color="#10b981" />
              </div>
              <div className="stat-card-value" style={{ color: '#10b981' }}>6 Roles</div>
              <div className="stat-card-subtext">Principle of least privilege enforced</div>
            </div>

            <div className="db-stat-card">
              <div className="stat-card-header">
                <span>Security Events Logged</span>
                <FileCheck size={18} color="#a855f7" />
              </div>
              <div className="stat-card-value" style={{ color: '#a855f7' }}>{auditLogs.length}</div>
              <div className="stat-card-subtext">Stored in cascadeshield.db</div>
            </div>
          </div>

          {/* User Table */}
          <div style={{
            background: 'var(--card-bg, #0f172a)',
            borderRadius: '10px',
            border: '1px solid var(--border-color, #1e293b)',
            padding: '1.25rem'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.75rem' }}>
              <h3 style={{ fontSize: '1rem', fontWeight: 600, margin: 0, color: 'var(--text-primary, #f8fafc)' }}>
                User Accounts & Role Assignments
              </h3>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'rgba(15, 23, 42, 0.8)', padding: '0.35rem 0.65rem', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.1)' }}>
                <Search size={14} color="#94a3b8" />
                <input
                  type="text"
                  placeholder="Filter users..."
                  value={searchUser}
                  onChange={(e) => setSearchUser(e.target.value)}
                  style={{ background: 'transparent', border: 'none', color: '#f8fafc', fontSize: '0.8rem', outline: 'none' }}
                />
              </div>
            </div>

            <div className="enterprise-table-container">
              <table className="enterprise-table">
                <thead>
                  <tr>
                    <th>Username</th>
                    <th>Email</th>
                    <th>Current RBAC Role</th>
                    <th>Status</th>
                    <th>Action: Assign Role</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredUsers.map(user => (
                    <tr key={user.id}>
                      <td><strong>{user.username}</strong></td>
                      <td style={{ color: '#94a3b8' }}>{user.email}</td>
                      <td>
                        <span style={{
                          fontSize: '0.74rem',
                          fontWeight: 600,
                          padding: '0.2rem 0.5rem',
                          borderRadius: '4px',
                          background: user.role === 'Administrator' ? '#ef444422' : '#3b82f622',
                          color: user.role === 'Administrator' ? '#f87171' : '#60a5fa',
                          border: `1px solid ${user.role === 'Administrator' ? '#ef444444' : '#3b82f644'}`
                        }}>
                          {user.role}
                        </span>
                      </td>
                      <td>
                        <StatusBadge status={user.is_active ? 'HEALTHY' : 'UNAVAILABLE'} text={user.is_active ? 'ACTIVE' : 'SUSPENDED'} size="xs" />
                      </td>
                      <td>
                        <select
                          value={user.role}
                          onChange={(e) => handleRoleChange(user.id, e.target.value)}
                          style={{
                            background: 'rgba(15, 23, 42, 0.9)',
                            border: '1px solid rgba(255,255,255,0.15)',
                            borderRadius: '4px',
                            color: '#f8fafc',
                            fontSize: '0.78rem',
                            padding: '0.25rem 0.5rem',
                            cursor: 'pointer'
                          }}
                        >
                          <option value="Administrator">Administrator</option>
                          <option value="Cloud Operator">Cloud Operator</option>
                          <option value="Incident Responder">Incident Responder</option>
                          <option value="Reliability Analyst">Reliability Analyst</option>
                          <option value="Developer">Developer</option>
                          <option value="Read-Only Viewer">Read-Only Viewer</option>
                        </select>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: RBAC PERMISSION MATRIX */}
      {activeTab === 'roles' && (
        <div style={{
          background: 'var(--card-bg, #0f172a)',
          borderRadius: '10px',
          border: '1px solid var(--border-color, #1e293b)',
          padding: '1.25rem'
        }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, margin: '0 0 0.5rem', color: 'var(--text-primary, #f8fafc)' }}>
            Enterprise Role Permission Matrix (6 Tiers)
          </h3>
          <p style={{ margin: '0 0 1.25rem', fontSize: '0.85rem', color: 'var(--text-secondary, #94a3b8)' }}>
            Strict granular privilege enforcement ensuring zero unauthorized topology, recovery, or threshold modifications.
          </p>

          <div className="enterprise-table-container">
            <table className="enterprise-table">
              <thead>
                <tr>
                  <th>Platform Capability</th>
                  <th>Administrator</th>
                  <th>Cloud Operator</th>
                  <th>Incident Responder</th>
                  <th>Reliability Analyst</th>
                  <th>Developer</th>
                  <th>Read-Only Viewer</th>
                </tr>
              </thead>
              <tbody>
                {[
                  { perm: 'View Digital Twin Topology', adm: true, op: true, inc: true, rel: true, dev: true, ro: true },
                  { perm: 'Add / Edit Microservice', adm: true, op: true, inc: false, rel: false, dev: false, ro: false },
                  { perm: 'Create / Sever Dependencies', adm: true, op: true, inc: false, rel: false, dev: false, ro: false },
                  { perm: 'Execute Chaos What-If Simulation', adm: true, op: true, inc: true, rel: false, dev: true, ro: false },
                  { perm: 'Acknowledge Anomalies & Alerts', adm: true, op: true, inc: true, rel: false, dev: false, ro: false },
                  { perm: 'Trigger Bayesian Root Cause Analysis', adm: true, op: true, inc: true, rel: true, dev: true, ro: false },
                  { perm: 'Execute Autonomous Recovery Plan', adm: true, op: false, inc: true, rel: false, dev: false, ro: false },
                  { perm: 'Run 5-Pillar Sandbox Verification', adm: true, op: false, inc: true, rel: true, dev: true, ro: false },
                  { perm: 'Modify Platform Thresholds & Settings', adm: true, op: false, inc: false, rel: false, dev: false, ro: false },
                  { perm: 'Manage Users & Security Roles', adm: true, op: false, inc: false, rel: false, dev: false, ro: false },
                  { perm: 'Inspect Immutable Audit Trails', adm: true, op: false, inc: true, rel: true, dev: false, ro: false }
                ].map((row, idx) => (
                  <tr key={idx}>
                    <td><strong>{row.perm}</strong></td>
                    <td style={{ textAlign: 'center' }}>{row.adm ? <CheckCircle2 size={15} color="#10b981" /> : <XCircle size={15} color="#475569" />}</td>
                    <td style={{ textAlign: 'center' }}>{row.op ? <CheckCircle2 size={15} color="#10b981" /> : <XCircle size={15} color="#475569" />}</td>
                    <td style={{ textAlign: 'center' }}>{row.inc ? <CheckCircle2 size={15} color="#10b981" /> : <XCircle size={15} color="#475569" />}</td>
                    <td style={{ textAlign: 'center' }}>{row.rel ? <CheckCircle2 size={15} color="#10b981" /> : <XCircle size={15} color="#475569" />}</td>
                    <td style={{ textAlign: 'center' }}>{row.dev ? <CheckCircle2 size={15} color="#10b981" /> : <XCircle size={15} color="#475569" />}</td>
                    <td style={{ textAlign: 'center' }}>{row.ro ? <CheckCircle2 size={15} color="#10b981" /> : <XCircle size={15} color="#475569" />}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 3: IMMUTABLE AUDIT TRAIL */}
      {activeTab === 'audit' && (
        <div style={{
          background: 'var(--card-bg, #0f172a)',
          borderRadius: '10px',
          border: '1px solid var(--border-color, #1e293b)',
          padding: '1.25rem',
          display: 'flex',
          flexDirection: 'column',
          gap: '1rem'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.75rem' }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 600, margin: 0, color: 'var(--text-primary, #f8fafc)' }}>
              Append-Only Security Audit Records
            </h3>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              {/* Status Filter */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', background: 'rgba(15, 23, 42, 0.8)', padding: '0.35rem 0.6rem', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.1)' }}>
                <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Status:</span>
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  style={{ background: 'transparent', border: 'none', color: '#f8fafc', fontSize: '0.78rem', outline: 'none', cursor: 'pointer' }}
                >
                  <option value="ALL" style={{ background: '#0f172a' }}>All Statuses</option>
                  <option value="SUCCESS" style={{ background: '#0f172a' }}>SUCCESS</option>
                  <option value="DENIED" style={{ background: '#0f172a' }}>DENIED</option>
                  <option value="WARNING" style={{ background: '#0f172a' }}>WARNING</option>
                </select>
              </div>

              {/* Search */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'rgba(15, 23, 42, 0.8)', padding: '0.35rem 0.65rem', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.1)' }}>
                <Search size={14} color="#94a3b8" />
                <input
                  type="text"
                  placeholder="Search logs..."
                  value={searchAudit}
                  onChange={(e) => setSearchAudit(e.target.value)}
                  style={{ background: 'transparent', border: 'none', color: '#f8fafc', fontSize: '0.8rem', outline: 'none' }}
                />
              </div>
            </div>
          </div>

          <div className="enterprise-table-container">
            <table className="enterprise-table">
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Actor / User</th>
                  <th>Action</th>
                  <th>Target Resource</th>
                  <th>Status</th>
                  <th>Inspect</th>
                </tr>
              </thead>
              <tbody>
                {filteredLogs.map(log => (
                  <tr key={log.id}>
                    <td style={{ color: '#94a3b8', fontSize: '0.78rem' }}>
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                    <td><strong>{log.actor_id}</strong></td>
                    <td><code>{log.action}</code></td>
                    <td style={{ color: '#cbd5e1' }}>
                      {log.resource_type}: <strong>{log.resource_id}</strong>
                    </td>
                    <td>
                      <StatusBadge
                        status={log.status === 'SUCCESS' ? 'HEALTHY' : (log.status === 'DENIED' ? 'UNAVAILABLE' : 'DEGRADED')}
                        text={log.status}
                        size="xs"
                      />
                    </td>
                    <td>
                      <button
                        onClick={() => setSelectedLog(log)}
                        style={{
                          background: 'transparent',
                          border: 'none',
                          color: '#38bdf8',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.2rem',
                          fontSize: '0.75rem'
                        }}
                      >
                        <Eye size={13} /> View
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Audit Log Detail Modal */}
      {selectedLog && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.75)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 9999,
          padding: '1rem'
        }}>
          <div style={{
            background: '#0f172a',
            border: '1px solid #334155',
            borderRadius: '10px',
            width: '100%',
            maxWidth: '550px',
            padding: '1.5rem',
            display: 'flex',
            flexDirection: 'column',
            gap: '1rem',
            boxShadow: '0 10px 25px rgba(0,0,0,0.5)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 600, margin: 0, color: '#f8fafc' }}>
                Audit Record #{selectedLog.id}
              </h3>
              <button
                onClick={() => setSelectedLog(null)}
                style={{ background: 'transparent', border: 'none', color: '#94a3b8', cursor: 'pointer', fontSize: '1.2rem' }}
              >
                &times;
              </button>
            </div>

            <div style={{ fontSize: '0.85rem', color: '#cbd5e1', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <div><strong>Actor:</strong> {selectedLog.actor_id}</div>
              <div><strong>Action:</strong> <code>{selectedLog.action}</code></div>
              <div><strong>Resource:</strong> {selectedLog.resource_type} ({selectedLog.resource_id})</div>
              <div><strong>Status:</strong> {selectedLog.status}</div>
              <div><strong>Timestamp:</strong> {new Date(selectedLog.timestamp).toISOString()}</div>
              <div><strong>Client IP:</strong> {selectedLog.ip_address || '127.0.0.1'}</div>
              <div>
                <strong>Payload / Details:</strong>
                <pre style={{
                  background: '#090d16',
                  padding: '0.75rem',
                  borderRadius: '6px',
                  color: '#38bdf8',
                  fontSize: '0.78rem',
                  maxHeight: '180px',
                  overflowY: 'auto'
                }}>
                  {JSON.stringify(selectedLog.details, null, 2)}
                </pre>
              </div>
            </div>

            <button
              onClick={() => setSelectedLog(null)}
              className="header-secondary-btn"
              style={{ alignSelf: 'flex-end', padding: '0.45rem 1rem', borderRadius: '6px', cursor: 'pointer' }}
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
