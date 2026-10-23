import React, { useState, useEffect, useCallback } from 'react';
import { 
  Server, 
  ShieldAlert, 
  Network, 
  Settings, 
  Activity, 
  Plus, 
  RefreshCw, 
  Search, 
  Filter, 
  Trash2, 
  Edit3, 
  CheckCircle2, 
  AlertTriangle, 
  XCircle, 
  Clock, 
  Share2, 
  Cpu, 
  HardDrive, 
  Radio, 
  Save, 
  Sliders,
  Layers,
  ChevronRight,
  ExternalLink
} from 'lucide-react';
import { adminApi } from '../services/adminApi';
import { api } from '../services/api';
import { 
  ResponsiveContainer, 
  LineChart, 
  Line, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip as RechartsTooltip, 
  CartesianGrid, 
  Legend 
} from 'recharts';
import StatusBadge from '../components/common/StatusBadge';
import SkeletonLoader from '../components/common/SkeletonLoader';
import EmptyState from '../components/common/EmptyState';
import Tooltip from '../components/common/Tooltip';

export default function CloudAdministratorPortal({ onNavigateModule, onAddToast }) {
  const [activeTab, setActiveTab] = useState('overview'); // 'overview' | 'services' | 'dependencies' | 'metrics' | 'settings'
  const [summary, setSummary] = useState(null);
  const [services, setServices] = useState([]);
  const [dependencies, setDependencies] = useState([]);
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterHealth, setFilterHealth] = useState('ALL');
  const [savingSettings, setSavingSettings] = useState(false);

  // Service form modal state
  const [selectedService, setSelectedService] = useState(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isAddServiceOpen, setIsAddServiceOpen] = useState(false);
  const [serviceFormData, setServiceFormData] = useState({
    name: '',
    service_type: 'compute',
    description: '',
    cpu_usage: 25.0,
    memory_usage: 40.0,
    latency_ms: 30.0,
    error_rate: 0.1,
    request_volume: 1500
  });

  // Settings form state
  const [settingsForm, setSettingsForm] = useState({
    simulation_step_limit: 20,
    simulation_default_duration: 10,
    telemetry_refresh_interval_sec: 5,
    cpu_critical_threshold: 90.0,
    memory_critical_threshold: 90.0,
    latency_critical_threshold_ms: 1000.0,
    error_rate_critical_threshold: 5.0,
    notification_slack_enabled: false
  });

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [sumRes, srvRes, depRes, setRes] = await Promise.all([
        adminApi.getSummary().catch(() => null),
        api.getServices().catch(() => []),
        api.getDependencies().catch(() => []),
        adminApi.getSettings().catch(() => null)
      ]);

      if (sumRes) setSummary(sumRes);
      if (srvRes) setServices(srvRes);
      if (depRes) setDependencies(depRes);
      if (setRes) {
        setSettings(setRes);
        setSettingsForm(setRes);
      }
    } catch (err) {
      if (onAddToast) onAddToast(`Error loading admin data: ${err.message}`, 'error', 'Admin Portal');
    } finally {
      setLoading(false);
    }
  }, [onAddToast]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Save Settings
  const handleSaveSettings = async (e) => {
    e.preventDefault();
    setSavingSettings(true);
    try {
      const res = await adminApi.updateSettings(settingsForm);
      setSettings(res.settings);
      if (onAddToast) onAddToast('Platform and simulation thresholds updated.', 'success', 'Settings Saved');
    } catch (err) {
      if (onAddToast) onAddToast(`Save failed: ${err.message}`, 'error', 'Settings Error');
    } finally {
      setSavingSettings(false);
    }
  };

  // Add Service Submit
  const handleAddServiceSubmit = async (e) => {
    e.preventDefault();
    try {
      const created = await api.createService(serviceFormData);
      setIsAddServiceOpen(false);
      setServiceFormData({
        name: '',
        service_type: 'compute',
        description: '',
        cpu_usage: 25.0,
        memory_usage: 40.0,
        latency_ms: 30.0,
        error_rate: 0.1,
        request_volume: 1500
      });
      await loadData();
      if (onAddToast) onAddToast(`Service '${created.name}' registered into digital twin.`, 'success', 'Service Created');
    } catch (err) {
      if (onAddToast) onAddToast(`Creation failed: ${err.message}`, 'error', 'Error');
    }
  };

  // Delete Service with confirmation
  const handleDeleteService = async (serviceId, serviceName) => {
    if (!window.confirm(`Are you sure you want to permanently delete '${serviceName}' (${serviceId})? Connected dependencies will be unlinked.`)) {
      return;
    }
    try {
      await api.deleteService(serviceId);
      await loadData();
      if (onAddToast) onAddToast(`Service '${serviceName}' deleted.`, 'success', 'Service Removed');
    } catch (err) {
      if (onAddToast) onAddToast(`Delete failed: ${err.message}`, 'error', 'Delete Error');
    }
  };

  // Filtered Services List
  const filteredServices = services.filter(s => {
    const matchesSearch = !searchQuery || 
      s.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
      s.id.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesHealth = filterHealth === 'ALL' || s.health_status === filterHealth;
    return matchesSearch && matchesHealth;
  });

  // Telemetry chart data mapped from current services
  const metricsChartData = services.map(s => ({
    name: s.name.replace(' Service', ''),
    cpu: Math.round(s.cpu_usage || s.cpu_utilization || 0),
    memory: Math.round(s.memory_usage || s.memory_utilization || 0),
    latency: Math.round(s.latency_ms || s.latency_p99 || 0),
    errorRate: Number(s.error_rate || 0).toFixed(2),
    requests: s.request_volume || 1000
  }));

  return (
    <div className="dashboard-container portal-container">
      {/* Header */}
      <div className="db-header">
        <div className="db-title-group">
          <h2>
            <Server size={24} color="#0284c7" />
            <span>Portal 1: Cloud Administrator Portal</span>
          </h2>
          <p>
            Virtual Cloud Infrastructure Governance: Service topology inventory, telemetry thresholds, dependency validation, and platform settings.
          </p>
        </div>

        <div className="db-header-actions">
          <button 
            className="btn btn-primary"
            onClick={() => setIsAddServiceOpen(true)}
          >
            <Plus size={15} />
            <span>Register Service</span>
          </button>

          <button 
            className="btn btn-secondary"
            onClick={loadData}
            disabled={loading}
            title="Refresh infrastructure state"
          >
            <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Portal Tabs Bar */}
      <div className="portal-tabs-nav">
        <button 
          className={`portal-tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          <Activity size={15} />
          <span>Infra Overview</span>
        </button>

        <button 
          className={`portal-tab-btn ${activeTab === 'services' ? 'active' : ''}`}
          onClick={() => setActiveTab('services')}
        >
          <Server size={15} />
          <span>Service Management ({services.length})</span>
        </button>

        <button 
          className={`portal-tab-btn ${activeTab === 'dependencies' ? 'active' : ''}`}
          onClick={() => setActiveTab('dependencies')}
        >
          <Share2 size={15} />
          <span>Dependencies ({dependencies.length})</span>
        </button>

        <button 
          className={`portal-tab-btn ${activeTab === 'metrics' ? 'active' : ''}`}
          onClick={() => setActiveTab('metrics')}
        >
          <Sliders size={15} />
          <span>Infrastructure Metrics</span>
        </button>

        <button 
          className={`portal-tab-btn ${activeTab === 'settings' ? 'active' : ''}`}
          onClick={() => setActiveTab('settings')}
        >
          <Settings size={15} />
          <span>Platform & Thresholds</span>
        </button>
      </div>

      {/* TAB 1: INFRASTRUCTURE OVERVIEW */}
      {activeTab === 'overview' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* Summary Cards */}
          <div className="db-summary-grid">
            <div className="db-stat-card">
              <div className="stat-card-header">
                <span>Total Services</span>
                <Server size={18} color="#0284c7" />
              </div>
              <div className="stat-card-value">{summary?.total_services || services.length}</div>
              <div className="stat-card-subtext">Registered cloud microservices</div>
            </div>

            <div className="db-stat-card">
              <div className="stat-card-header">
                <span>Healthy Services</span>
                <CheckCircle2 size={18} color="#10b981" />
              </div>
              <div className="stat-card-value" style={{ color: '#10b981' }}>
                {summary?.healthy_services ?? services.filter(s => s.health_status === 'HEALTHY').length}
              </div>
              <div className="stat-card-subtext">Operating at baseline SLA</div>
            </div>

            <div className="db-stat-card">
              <div className="stat-card-header">
                <span>Degraded / Warning</span>
                <AlertTriangle size={18} color="#f59e0b" />
              </div>
              <div className="stat-card-value" style={{ color: '#f59e0b' }}>
                {summary?.degraded_services ?? services.filter(s => s.health_status === 'DEGRADED').length}
              </div>
              <div className="stat-card-subtext">Latency or error jitter detected</div>
            </div>

            <div className="db-stat-card">
              <div className="stat-card-header">
                <span>Critical / Unavailable</span>
                <XCircle size={18} color="#ef4444" />
              </div>
              <div className="stat-card-value" style={{ color: '#ef4444' }}>
                {summary?.unavailable_services ?? services.filter(s => s.health_status === 'CRITICAL').length}
              </div>
              <div className="stat-card-subtext">Immediate failover required</div>
            </div>

            <div className="db-stat-card">
              <div className="stat-card-header">
                <span>Total Dependencies</span>
                <Share2 size={18} color="#818cf8" />
              </div>
              <div className="stat-card-value">{summary?.total_dependencies || dependencies.length}</div>
              <div className="stat-card-subtext">Directed dependency edges</div>
            </div>

            <div className="db-stat-card">
              <div className="stat-card-header">
                <span>Platform Uptime</span>
                <Activity size={18} color="#10b981" />
              </div>
              <div className="stat-card-value">{summary?.platform_uptime_pct || 99.98}%</div>
              <div className="stat-card-subtext">Virtual Twin operational status</div>
            </div>
          </div>

          {/* Quick Infrastructure Health Bar Chart */}
          <div className="db-panel">
            <div className="db-panel-header">
              <div className="db-panel-title">
                <Cpu size={18} color="#0284c7" />
                <span>Microservice Resource Utilization Overview</span>
              </div>
              <span className="simulated-pill">Simulated Telemetry Jitter</span>
            </div>

            <div style={{ height: '300px', width: '100%', marginTop: '1rem' }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={metricsChartData} margin={{ top: 10, right: 30, left: 0, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
                  <XAxis dataKey="name" stroke="#64748b" tick={{ fontSize: 11 }} />
                  <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
                  <RechartsTooltip contentStyle={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '6px' }} />
                  <Legend />
                  <Bar dataKey="cpu" name="CPU Usage (%)" fill="#0284c7" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="memory" name="Memory Usage (%)" fill="#818cf8" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: SERVICE MANAGEMENT */}
      {activeTab === 'services' && (
        <div className="db-panel">
          <div className="db-panel-header">
            <div className="db-panel-title">
              <Server size={18} color="#0284c7" />
              <span>Registered Cloud Microservices</span>
            </div>

            {/* Search & Filter Controls */}
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
              <div className="topbar-search-trigger" style={{ width: '220px' }}>
                <Search size={14} />
                <input 
                  type="text"
                  placeholder="Filter services..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  style={{ background: 'transparent', border: 'none', color: 'inherit', outline: 'none', width: '100%' }}
                />
              </div>

              <select 
                className="db-select"
                value={filterHealth}
                onChange={(e) => setFilterHealth(e.target.value)}
                style={{ padding: '4px 8px', fontSize: '0.8rem' }}
              >
                <option value="ALL">All Statuses</option>
                <option value="HEALTHY">Healthy</option>
                <option value="DEGRADED">Degraded</option>
                <option value="CRITICAL">Critical</option>
              </select>
            </div>
          </div>

          {loading && services.length === 0 ? (
            <SkeletonLoader variant="table" count={6} />
          ) : filteredServices.length === 0 ? (
            <EmptyState
              icon={Server}
              title="No Services Found"
              description="No cloud services matched your filter query."
              actionLabel="Clear Filters"
              onAction={() => { setSearchQuery(''); setFilterHealth('ALL'); }}
            />
          ) : (
            <div style={{ overflowX: 'auto', marginTop: '1rem' }}>
              <table className="portal-table">
                <thead>
                  <tr>
                    <th>Service Name & ID</th>
                    <th>Type</th>
                    <th>Health Status</th>
                    <th>CPU</th>
                    <th>Memory</th>
                    <th>Latency P99</th>
                    <th>Error Rate</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredServices.map(srv => (
                    <tr key={srv.id}>
                      <td>
                        <div style={{ fontWeight: 600, color: 'var(--text-main)' }}>{srv.name}</div>
                        <code style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>{srv.id}</code>
                      </td>
                      <td>
                        <span className="risk-pill" style={{ textTransform: 'uppercase' }}>
                          {srv.service_type}
                        </span>
                      </td>
                      <td>
                        <StatusBadge status={srv.health_status} />
                      </td>
                      <td>{Math.round(srv.cpu_usage || srv.cpu_utilization || 0)}%</td>
                      <td>{Math.round(srv.memory_usage || srv.memory_utilization || 0)}%</td>
                      <td>{Math.round(srv.latency_ms || srv.latency_p99 || 0)} ms</td>
                      <td style={{ color: (srv.error_rate || 0) > 2 ? '#ef4444' : 'inherit' }}>
                        {Number(srv.error_rate || 0).toFixed(2)}%
                      </td>
                      <td>
                        <div style={{ display: 'flex', gap: '6px' }}>
                          <button
                            className="btn btn-secondary btn-sm"
                            onClick={() => onNavigateModule && onNavigateModule('digital-twin')}
                            title="Inspect in Digital Twin Canvas"
                          >
                            <ExternalLink size={12} />
                          </button>
                          <button
                            className="btn btn-danger btn-sm"
                            onClick={() => handleDeleteService(srv.id, srv.name)}
                            title="Delete service"
                          >
                            <Trash2 size={12} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* TAB 3: DEPENDENCIES MANAGEMENT */}
      {activeTab === 'dependencies' && (
        <div className="db-panel">
          <div className="db-panel-header">
            <div className="db-panel-title">
              <Share2 size={18} color="#0284c7" />
              <span>Service Dependency Links & Topology Routing</span>
            </div>
            <button 
              className="btn btn-secondary btn-sm"
              onClick={() => onNavigateModule && onNavigateModule('digital-twin')}
            >
              <Network size={14} />
              <span>Open Cytoscape Visualizer</span>
            </button>
          </div>

          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', margin: '0.5rem 0 1rem 0' }}>
            Directed microservice dependencies define call chains. Inverted reverse dependencies determine cascading failure blast radius.
          </p>

          <div style={{ overflowX: 'auto' }}>
            <table className="portal-table">
              <thead>
                <tr>
                  <th>Dependency ID</th>
                  <th>Source Caller</th>
                  <th>Directed Link</th>
                  <th>Target Dependency</th>
                  <th>Protocol Coupling</th>
                  <th>Description</th>
                </tr>
              </thead>
              <tbody>
                {dependencies.map(dep => (
                  <tr key={dep.id}>
                    <td><code>{dep.id}</code></td>
                    <td><strong>{dep.source_service_id}</strong></td>
                    <td style={{ color: '#0284c7', textAlign: 'center' }}>→</td>
                    <td><strong style={{ color: '#38bdf8' }}>{dep.target_service_id}</strong></td>
                    <td>
                      <span className="risk-pill" style={{ textTransform: 'uppercase' }}>
                        {dep.dependency_type || 'sync_http'}
                      </span>
                    </td>
                    <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      {dep.description || 'Standard inter-service RPC'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 4: INFRASTRUCTURE METRICS */}
      {activeTab === 'metrics' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div className="db-panel">
            <div className="db-panel-header">
              <div className="db-panel-title">
                <Activity size={18} color="#0284c7" />
                <span>Microservice P99 Latency Profile (Milliseconds)</span>
              </div>
              <span className="simulated-pill">SLA Threshold: 150ms</span>
            </div>

            <div style={{ height: '280px', width: '100%', marginTop: '1rem' }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={metricsChartData} margin={{ top: 10, right: 30, left: 0, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
                  <XAxis dataKey="name" stroke="#64748b" tick={{ fontSize: 11 }} />
                  <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
                  <RechartsTooltip contentStyle={{ background: '#0f172a', border: '1px solid #334155' }} />
                  <Bar dataKey="latency" name="Latency P99 (ms)" fill="#38bdf8" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="db-panel">
            <div className="db-panel-header">
              <div className="db-panel-title">
                <Radio size={18} color="#ec4899" />
                <span>Error Rate Violation Distribution (%)</span>
              </div>
              <span className="simulated-pill">SLA Threshold: 1.0%</span>
            </div>

            <div style={{ height: '280px', width: '100%', marginTop: '1rem' }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={metricsChartData} margin={{ top: 10, right: 30, left: 0, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
                  <XAxis dataKey="name" stroke="#64748b" tick={{ fontSize: 11 }} />
                  <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
                  <RechartsTooltip contentStyle={{ background: '#0f172a', border: '1px solid #334155' }} />
                  <Bar dataKey="errorRate" name="Error Rate (%)" fill="#ec4899" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}

      {/* TAB 5: PLATFORM & SIMULATION SETTINGS */}
      {activeTab === 'settings' && (
        <div className="db-panel" style={{ maxWidth: '800px' }}>
          <div className="db-panel-header">
            <div className="db-panel-title">
              <Settings size={18} color="#0284c7" />
              <span>Platform & Resilience Simulation Settings</span>
            </div>
            <span className="simulated-pill">Governed by Administrator RBAC</span>
          </div>

          <form onSubmit={handleSaveSettings} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', marginTop: '1.25rem' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Simulation Step Limit</label>
                <input 
                  type="number"
                  className="db-select"
                  value={settingsForm.simulation_step_limit}
                  onChange={(e) => setSettingsForm({ ...settingsForm, simulation_step_limit: parseInt(e.target.value) || 20 })}
                  min="5"
                  max="100"
                />
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Default Duration Steps</label>
                <input 
                  type="number"
                  className="db-select"
                  value={settingsForm.simulation_default_duration}
                  onChange={(e) => setSettingsForm({ ...settingsForm, simulation_default_duration: parseInt(e.target.value) || 10 })}
                  min="3"
                  max="50"
                />
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Telemetry Jitter Interval (sec)</label>
                <input 
                  type="number"
                  className="db-select"
                  value={settingsForm.telemetry_refresh_interval_sec}
                  onChange={(e) => setSettingsForm({ ...settingsForm, telemetry_refresh_interval_sec: parseInt(e.target.value) || 5 })}
                  min="2"
                  max="60"
                />
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>CPU Critical Breach (%)</label>
                <input 
                  type="number"
                  className="db-select"
                  value={settingsForm.cpu_critical_threshold}
                  onChange={(e) => setSettingsForm({ ...settingsForm, cpu_critical_threshold: parseFloat(e.target.value) || 90 })}
                />
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Latency Critical Breach (ms)</label>
                <input 
                  type="number"
                  className="db-select"
                  value={settingsForm.latency_critical_threshold_ms}
                  onChange={(e) => setSettingsForm({ ...settingsForm, latency_critical_threshold_ms: parseFloat(e.target.value) || 1000 })}
                />
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Error Rate Critical Breach (%)</label>
                <input 
                  type="number"
                  className="db-select"
                  value={settingsForm.error_rate_critical_threshold}
                  onChange={(e) => setSettingsForm({ ...settingsForm, error_rate_critical_threshold: parseFloat(e.target.value) || 5 })}
                />
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '0.5rem 0' }}>
              <input 
                type="checkbox"
                id="slack-toggle"
                checked={settingsForm.notification_slack_enabled}
                onChange={(e) => setSettingsForm({ ...settingsForm, notification_slack_enabled: e.target.checked })}
              />
              <label htmlFor="slack-toggle" style={{ fontSize: '0.84rem', color: 'var(--text-main)', cursor: 'pointer' }}>
                Forward Critical Anomaly Alerts to Webhook / Slack Channel
              </label>
            </div>

            <button 
              type="submit"
              className="btn btn-primary"
              disabled={savingSettings}
              style={{ alignSelf: 'flex-start' }}
            >
              <Save size={15} />
              <span>{savingSettings ? 'Persisting...' : 'Save Configuration'}</span>
            </button>
          </form>
        </div>
      )}

      {/* REGISTER SERVICE MODAL */}
      {isAddServiceOpen && (
        <div className="modal-backdrop" onClick={() => setIsAddServiceOpen(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '540px' }}>
            <div className="modal-header">
              <h3>Register Cloud Service</h3>
              <button className="btn-close" onClick={() => setIsAddServiceOpen(false)}>✕</button>
            </div>
            <form onSubmit={handleAddServiceSubmit}>
              <div className="modal-body" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.3rem' }}>
                  <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Service Name</label>
                  <input 
                    type="text" 
                    required
                    className="db-select" 
                    placeholder="e.g. Recommendation Engine" 
                    value={serviceFormData.name}
                    onChange={(e) => setServiceFormData({ ...serviceFormData, name: e.target.value })}
                  />
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.3rem' }}>
                  <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Service Type</label>
                  <select 
                    className="db-select"
                    value={serviceFormData.service_type}
                    onChange={(e) => setServiceFormData({ ...serviceFormData, service_type: e.target.value })}
                  >
                    <option value="compute">Compute / Application</option>
                    <option value="gateway">API Gateway / Edge</option>
                    <option value="database">Database / Persistence</option>
                    <option value="cache">In-Memory Cache</option>
                    <option value="security">Security / Auth</option>
                  </select>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.3rem' }}>
                  <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Description</label>
                  <textarea 
                    className="db-select" 
                    rows={2}
                    placeholder="Role and functionality in cloud architecture"
                    value={serviceFormData.description}
                    onChange={(e) => setServiceFormData({ ...serviceFormData, description: e.target.value })}
                  />
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setIsAddServiceOpen(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Register in Digital Twin
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
