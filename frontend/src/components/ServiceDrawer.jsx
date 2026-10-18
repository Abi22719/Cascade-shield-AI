import React, { useState, useEffect } from 'react';
import { 
  X, 
  Activity, 
  Layers, 
  Sliders, 
  Trash2, 
  Edit3, 
  CheckCircle2, 
  AlertTriangle, 
  AlertOctagon, 
  ShieldAlert, 
  ArrowRight, 
  Clock, 
  Cpu, 
  HardDrive, 
  Zap,
  TrendingUp,
  Share2
} from 'lucide-react';
import { api } from '../services/api';

export default function ServiceDrawer({
  selectedNode,
  selectedEdge,
  onClose,
  onUpdateService,
  onDeleteService,
  onDeleteDependency,
  onAnalyzeImpact,
  impactData,
  onClearImpact
}) {
  const [activeTab, setActiveTab] = useState('overview'); // 'overview', 'dependencies', 'simulate', 'edit'
  const [detailedService, setDetailedService] = useState(null);
  const [loadingDetails, setLoadingDetails] = useState(false);

  // Simulation slider states
  const [simCpu, setSimCpu] = useState(25);
  const [simMemory, setSimMemory] = useState(35);
  const [simLatency, setSimLatency] = useState(50);
  const [simErrorRate, setSimErrorRate] = useState(0.1);
  const [simRequestVolume, setSimRequestVolume] = useState(1500);

  // Metadata edit states
  const [editName, setEditName] = useState('');
  const [editType, setEditType] = useState('');
  const [editDescription, setEditDescription] = useState('');

  // Fetch full details when selectedNode changes
  useEffect(() => {
    if (!selectedNode) {
      setDetailedService(null);
      return;
    }

    setLoadingDetails(true);
    api.getServiceDetail(selectedNode.id)
      .then(data => {
        setDetailedService(data);
        // Initialize sliders with existing telemetry
        setSimCpu(data.cpu_usage || 20);
        setSimMemory(data.memory_usage || 30);
        setSimLatency(data.latency_ms || 45);
        setSimErrorRate(data.error_rate || 0.1);
        setSimRequestVolume(data.request_volume || 1000);

        // Initialize metadata fields
        setEditName(data.name || '');
        setEditType(data.service_type || '');
        setEditDescription(data.description || '');
      })
      .catch(err => {
        console.error('Failed to load service detail:', err);
      })
      .finally(() => {
        setLoadingDetails(false);
      });
  }, [selectedNode?.id]);

  if (!selectedNode && !selectedEdge) return null;

  // Render Edge Inspector if an edge is selected
  if (selectedEdge) {
    return (
      <div className="side-drawer">
        <div className="drawer-header">
          <div className="drawer-title-group">
            <h2>Dependency Details</h2>
            <div className="drawer-service-id">{selectedEdge.id}</div>
          </div>
          <button className="btn-icon" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <div className="drawer-body">
          <div className="edge-inspector-card">
            <h4 style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Dependency Flow</h4>
            <div className="edge-flow-diagram">
              <span className="edge-node-badge">{selectedEdge.source}</span>
              <ArrowRight size={18} color="#0ea5e9" />
              <span className="edge-node-badge">{selectedEdge.target}</span>
            </div>

            <div style={{ marginTop: '10px' }}>
              <div className="form-label">Protocol / Type</div>
              <div style={{ 
                marginTop: '4px', 
                fontSize: '0.85rem', 
                fontFamily: 'var(--font-mono)', 
                color: '#38bdf8' 
              }}>
                {selectedEdge.dependency_type}
              </div>
            </div>

            {selectedEdge.description && (
              <div style={{ marginTop: '8px' }}>
                <div className="form-label">Description / Rationale</div>
                <p style={{ marginTop: '4px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  {selectedEdge.description}
                </p>
              </div>
            )}

            <div style={{ marginTop: '16px', paddingTop: '16px', borderTop: '1px solid var(--border-color)' }}>
              <button 
                className="btn btn-danger"
                style={{ width: '100%' }}
                onClick={() => onDeleteDependency(selectedEdge.id)}
              >
                <Trash2 size={16} />
                <span>Remove Dependency</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Calculate projected health in real time for simulation tab
  const getProjectedHealth = () => {
    if (simErrorRate >= 10.0 || simLatency >= 1000.0 || simCpu >= 90.0 || simMemory >= 92.0) {
      return { status: 'CRITICAL', color: '#ef4444' };
    }
    if (simErrorRate >= 2.0 || simLatency >= 400.0 || simCpu >= 75.0 || simMemory >= 80.0) {
      return { status: 'WARNING', color: '#f59e0b' };
    }
    return { status: 'HEALTHY', color: '#10b981' };
  };

  const projected = getProjectedHealth();

  // Apply simulated telemetry changes
  const handleApplySimulation = () => {
    onUpdateService(selectedNode.id, {
      cpu_usage: parseFloat(simCpu),
      memory_usage: parseFloat(simMemory),
      latency_ms: parseFloat(simLatency),
      error_rate: parseFloat(simErrorRate),
      request_volume: parseInt(simRequestVolume, 10)
    });
  };

  // Apply scenario preset
  const handleApplyPreset = (preset) => {
    if (preset === 'normal') {
      setSimCpu(22);
      setSimMemory(35);
      setSimLatency(30);
      setSimErrorRate(0.05);
      setSimRequestVolume(1200);
    } else if (preset === 'surge') {
      setSimCpu(78);
      setSimMemory(72);
      setSimLatency(460);
      setSimErrorRate(2.8);
      setSimRequestVolume(6500);
    } else if (preset === 'outage') {
      setSimCpu(94);
      setSimMemory(95);
      setSimLatency(1450);
      setSimErrorRate(22.5);
      setSimRequestVolume(3100);
    } else if (preset === 'latency') {
      setSimCpu(45);
      setSimMemory(50);
      setSimLatency(1150);
      setSimErrorRate(6.2);
      setSimRequestVolume(1800);
    }
  };

  // Save metadata changes
  const handleSaveMetadata = (e) => {
    e.preventDefault();
    onUpdateService(selectedNode.id, {
      name: editName,
      service_type: editType,
      description: editDescription
    });
  };

  const currentStatus = detailedService?.health_status || selectedNode.health_status;

  return (
    <div className="side-drawer">
      {/* Drawer Header */}
      <div className="drawer-header">
        <div className="drawer-title-group">
          <h2>
            {detailedService?.name || selectedNode.name}
            <span style={{ 
              fontSize: '0.7rem', 
              padding: '2px 8px', 
              borderRadius: '9999px',
              backgroundColor: currentStatus === 'HEALTHY' ? 'rgba(16, 185, 129, 0.2)' : currentStatus === 'WARNING' ? 'rgba(245, 158, 11, 0.2)' : 'rgba(239, 68, 68, 0.2)',
              color: currentStatus === 'HEALTHY' ? '#10b981' : currentStatus === 'WARNING' ? '#f59e0b' : '#ef4444',
              border: `1px solid ${currentStatus === 'HEALTHY' ? '#10b981' : currentStatus === 'WARNING' ? '#f59e0b' : '#ef4444'}`
            }}>
              {currentStatus}
            </span>
          </h2>
          <div className="drawer-service-id">
            ID: {selectedNode.id} • Type: {detailedService?.service_type || selectedNode.service_type}
          </div>
        </div>
        <button className="btn-icon" onClick={onClose} title="Close drawer">
          <X size={18} />
        </button>
      </div>

      {/* Tabs */}
      <div className="drawer-tabs">
        <button 
          className={`drawer-tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          <Activity size={14} style={{ display: 'inline', marginRight: '4px' }} />
          Overview
        </button>
        <button 
          className={`drawer-tab ${activeTab === 'dependencies' ? 'active' : ''}`}
          onClick={() => setActiveTab('dependencies')}
        >
          <Share2 size={14} style={{ display: 'inline', marginRight: '4px' }} />
          Blast Radius
        </button>
        <button 
          className={`drawer-tab ${activeTab === 'simulate' ? 'active' : ''}`}
          onClick={() => setActiveTab('simulate')}
        >
          <Sliders size={14} style={{ display: 'inline', marginRight: '4px' }} />
          Simulate
        </button>
        <button 
          className={`drawer-tab ${activeTab === 'edit' ? 'active' : ''}`}
          onClick={() => setActiveTab('edit')}
        >
          <Edit3 size={14} style={{ display: 'inline', marginRight: '4px' }} />
          Edit
        </button>
      </div>

      {/* Drawer Body Content */}
      <div className="drawer-body">
        {/* TAB 1: OVERVIEW & TELEMETRY */}
        {activeTab === 'overview' && (
          <>
            {/* Status explanation banner */}
            <div className={`status-indicator-banner ${currentStatus.toLowerCase()}`}>
              {currentStatus === 'HEALTHY' && <CheckCircle2 size={20} style={{ flexShrink: 0 }} />}
              {currentStatus === 'WARNING' && <AlertTriangle size={20} style={{ flexShrink: 0 }} />}
              {currentStatus === 'CRITICAL' && <AlertOctagon size={20} style={{ flexShrink: 0 }} />}
              <div className="status-banner-content">
                <h4>Health Status: {currentStatus}</h4>
                {detailedService?.health_reasons && detailedService.health_reasons.length > 0 ? (
                  <ul className="status-banner-reasons">
                    {detailedService.health_reasons.map((r, i) => (
                      <li key={i}>{r}</li>
                    ))}
                  </ul>
                ) : (
                  <p style={{ fontSize: '0.75rem', marginTop: '2px' }}>
                    Calculated by configurable digital twin health evaluation rules.
                  </p>
                )}
              </div>
            </div>

            {/* Service Description */}
            {(detailedService?.description || selectedNode.description) && (
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: '1.4' }}>
                {detailedService?.description || selectedNode.description}
              </div>
            )}

            {/* Telemetry Metrics Grid */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-dim)' }}>
                  Live Telemetry Metrics
                </span>
                <span className="simulated-pill" style={{ padding: '2px 8px', fontSize: '0.68rem' }}>
                  Simulated Telemetry
                </span>
              </div>

              <div className="telemetry-grid">
                {/* CPU */}
                <div className="telemetry-item">
                  <div className="telemetry-label">CPU Usage</div>
                  <div className="telemetry-value-row">
                    <span className="telemetry-val">
                      {detailedService?.cpu_usage ?? selectedNode.cpu_usage}%
                    </span>
                    <Cpu size={14} color="var(--text-dim)" />
                  </div>
                  <div className="telemetry-progress-bg">
                    <div 
                      className="telemetry-progress-fill" 
                      style={{ 
                        width: `${Math.min(100, detailedService?.cpu_usage ?? selectedNode.cpu_usage)}%`,
                        backgroundColor: (detailedService?.cpu_usage ?? selectedNode.cpu_usage) > 85 ? '#ef4444' : '#0ea5e9'
                      }}
                    ></div>
                  </div>
                </div>

                {/* Memory */}
                <div className="telemetry-item">
                  <div className="telemetry-label">Memory Usage</div>
                  <div className="telemetry-value-row">
                    <span className="telemetry-val">
                      {detailedService?.memory_usage ?? selectedNode.memory_usage}%
                    </span>
                    <HardDrive size={14} color="var(--text-dim)" />
                  </div>
                  <div className="telemetry-progress-bg">
                    <div 
                      className="telemetry-progress-fill" 
                      style={{ 
                        width: `${Math.min(100, detailedService?.memory_usage ?? selectedNode.memory_usage)}%`,
                        backgroundColor: (detailedService?.memory_usage ?? selectedNode.memory_usage) > 85 ? '#ef4444' : '#10b981'
                      }}
                    ></div>
                  </div>
                </div>

                {/* Response Latency */}
                <div className="telemetry-item">
                  <div className="telemetry-label">Response Latency</div>
                  <div className="telemetry-value-row">
                    <span className="telemetry-val">
                      {detailedService?.latency_ms ?? selectedNode.latency_ms}
                    </span>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>ms</span>
                  </div>
                  <div className="telemetry-progress-bg">
                    <div 
                      className="telemetry-progress-fill" 
                      style={{ 
                        width: `${Math.min(100, ((detailedService?.latency_ms ?? selectedNode.latency_ms) / 1200) * 100)}%`,
                        backgroundColor: (detailedService?.latency_ms ?? selectedNode.latency_ms) > 400 ? '#f59e0b' : '#38bdf8'
                      }}
                    ></div>
                  </div>
                </div>

                {/* Error Rate */}
                <div className="telemetry-item">
                  <div className="telemetry-label">Error Rate</div>
                  <div className="telemetry-value-row">
                    <span className="telemetry-val">
                      {detailedService?.error_rate ?? selectedNode.error_rate}%
                    </span>
                    <Zap size={14} color="var(--text-dim)" />
                  </div>
                  <div className="telemetry-progress-bg">
                    <div 
                      className="telemetry-progress-fill" 
                      style={{ 
                        width: `${Math.min(100, ((detailedService?.error_rate ?? selectedNode.error_rate) / 20) * 100)}%`,
                        backgroundColor: (detailedService?.error_rate ?? selectedNode.error_rate) > 5 ? '#ef4444' : '#10b981'
                      }}
                    ></div>
                  </div>
                </div>
              </div>

              {/* Request Volume Row */}
              <div className="telemetry-item" style={{ marginTop: '12px' }}>
                <div className="telemetry-label">Traffic Throughput</div>
                <div className="telemetry-value-row">
                  <span className="telemetry-val" style={{ fontSize: '1.3rem' }}>
                    {(detailedService?.request_volume ?? selectedNode.request_volume)?.toLocaleString()}
                  </span>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>requests / sec</span>
                </div>
              </div>
            </div>

            {/* Quick action to blast radius */}
            <button 
              className="btn btn-secondary" 
              style={{ width: '100%', marginTop: '4px' }}
              onClick={() => onAnalyzeImpact(selectedNode.id)}
            >
              <ShieldAlert size={16} color="#0ea5e9" />
              <span>Inspect Downstream Blast Radius</span>
            </button>
          </>
        )}

        {/* TAB 2: DEPENDENCIES & DOWNSTREAM IMPACT */}
        {activeTab === 'dependencies' && (
          <>
            {/* Blast Radius Section */}
            <div className="impact-card">
              <div className="impact-header">
                <div>
                  <h4 style={{ fontSize: '0.9rem', fontWeight: 700, color: '#f8fafc' }}>
                    Downstream Blast Radius
                  </h4>
                  <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                    Reachable services if this service suffers an outage
                  </p>
                </div>
                <button 
                  className="btn btn-primary"
                  style={{ fontSize: '0.75rem', padding: '5px 10px' }}
                  onClick={() => onAnalyzeImpact(selectedNode.id)}
                >
                  <ShieldAlert size={14} />
                  <span>Analyze</span>
                </button>
              </div>

              {impactData && impactData.service_id === selectedNode.id ? (
                <>
                  <div className="impact-stats-row">
                    <div className="impact-stat-box">
                      <div className="impact-stat-number">{impactData.reachable_count}</div>
                      <div className="impact-stat-label">Total Reachable</div>
                    </div>
                    <div className="impact-stat-box">
                      <div className="impact-stat-number">{impactData.direct_dependents_count}</div>
                      <div className="impact-stat-label">Direct (Hop 1)</div>
                    </div>
                    <div className="impact-stat-box">
                      <div className="impact-stat-number">{impactData.indirect_dependents_count}</div>
                      <div className="impact-stat-label">Transitive (Hop 2+)</div>
                    </div>
                  </div>

                  <div className="impact-services-list">
                    {impactData.reachable_services?.length > 0 ? (
                      impactData.reachable_services.map((item) => (
                        <div key={item.id} className="impact-service-item">
                          <div>
                            <strong>{item.name}</strong>
                            <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>{item.id}</div>
                          </div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                            <span className="impact-tier-tag">Hop {item.distance_hops}</span>
                            <span style={{ 
                              fontSize: '0.7rem', 
                              color: item.health_status === 'HEALTHY' ? '#10b981' : item.health_status === 'WARNING' ? '#f59e0b' : '#ef4444' 
                            }}>
                              {item.health_status}
                            </span>
                          </div>
                        </div>
                      ))
                    ) : (
                      <p style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textAlign: 'center', padding: '10px' }}>
                        This service is a leaf service with no downstream dependents.
                      </p>
                    )}
                  </div>
                </>
              ) : (
                <div style={{ textAlign: 'center', padding: '12px 0' }}>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '8px' }}>
                    Click Analyze to calculate downstream dependency impact.
                  </p>
                </div>
              )}
            </div>

            {/* Direct Dependencies */}
            <div>
              <h4 style={{ fontSize: '0.85rem', fontWeight: 700, marginBottom: '8px', color: 'var(--text-muted)' }}>
                Direct Dependencies ({detailedService?.outgoing_dependencies?.length || 0})
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {detailedService?.outgoing_dependencies?.length > 0 ? (
                  detailedService.outgoing_dependencies.map(dep => (
                    <div key={dep.id} className="impact-service-item">
                      <div>
                        <span>{dep.service_name || dep.target_service_id}</span>
                        <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>
                          Type: {dep.dependency_type}
                        </div>
                      </div>
                      <button 
                        className="btn-icon" 
                        style={{ padding: '4px', color: '#ef4444' }}
                        title="Disconnect dependency"
                        onClick={() => onDeleteDependency(dep.id)}
                      >
                        <Trash2 size={13} />
                      </button>
                    </div>
                  ))
                ) : (
                  <p style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>No outgoing dependencies.</p>
                )}
              </div>
            </div>

            {/* Callers (Incoming) */}
            <div>
              <h4 style={{ fontSize: '0.85rem', fontWeight: 700, marginBottom: '8px', color: 'var(--text-muted)' }}>
                Incoming Callers ({detailedService?.incoming_dependencies?.length || 0})
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {detailedService?.incoming_dependencies?.length > 0 ? (
                  detailedService.incoming_dependencies.map(dep => (
                    <div key={dep.id} className="impact-service-item">
                      <div>
                        <span>{dep.service_name || dep.source_service_id}</span>
                        <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>
                          Type: {dep.dependency_type}
                        </div>
                      </div>
                      <button 
                        className="btn-icon" 
                        style={{ padding: '4px', color: '#ef4444' }}
                        title="Disconnect caller"
                        onClick={() => onDeleteDependency(dep.id)}
                      >
                        <Trash2 size={13} />
                      </button>
                    </div>
                  ))
                ) : (
                  <p style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>No incoming callers.</p>
                )}
              </div>
            </div>
          </>
        )}

        {/* TAB 3: SIMULATE CONDITIONS */}
        {activeTab === 'simulate' && (
          <div className="simulation-section">
            <div>
              <h4 style={{ fontSize: '0.85rem', fontWeight: 700, marginBottom: '6px', color: '#f8fafc' }}>
                Scenario Presets
              </h4>
              <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: '10px' }}>
                Quickly test how rule-based health responds to simulated failure conditions.
              </p>
              <div className="preset-buttons-group">
                <button className="preset-btn" onClick={() => handleApplyPreset('normal')}>
                  ✅ Normal Baseline
                </button>
                <button className="preset-btn" onClick={() => handleApplyPreset('surge')}>
                  ⚠️ Traffic Surge
                </button>
                <button className="preset-btn" onClick={() => handleApplyPreset('outage')}>
                  🛑 Critical Outage
                </button>
                <button className="preset-btn" onClick={() => handleApplyPreset('latency')}>
                  ⏱️ Latency Spike
                </button>
              </div>
            </div>

            {/* Projected Health Preview */}
            <div style={{ 
              padding: '10px 14px', 
              borderRadius: 'var(--radius-sm)', 
              backgroundColor: 'var(--bg-card)',
              border: `1px solid ${projected.color}`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between'
            }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Projected Health:</span>
              <strong style={{ color: projected.color, fontSize: '0.85rem' }}>{projected.status}</strong>
            </div>

            {/* Slider Controls */}
            <div className="slider-group">
              <div className="slider-header">
                <span>CPU Utilization:</span>
                <span className="slider-val">{simCpu}%</span>
              </div>
              <input 
                type="range" 
                min="0" 
                max="100" 
                step="1"
                className="telemetry-range"
                value={simCpu}
                onChange={(e) => setSimCpu(parseFloat(e.target.value))}
              />
            </div>

            <div className="slider-group">
              <div className="slider-header">
                <span>Memory Utilization:</span>
                <span className="slider-val">{simMemory}%</span>
              </div>
              <input 
                type="range" 
                min="0" 
                max="100" 
                step="1"
                className="telemetry-range"
                value={simMemory}
                onChange={(e) => setSimMemory(parseFloat(e.target.value))}
              />
            </div>

            <div className="slider-group">
              <div className="slider-header">
                <span>Response Latency:</span>
                <span className="slider-val">{simLatency} ms</span>
              </div>
              <input 
                type="range" 
                min="1" 
                max="2500" 
                step="10"
                className="telemetry-range"
                value={simLatency}
                onChange={(e) => setSimLatency(parseFloat(e.target.value))}
              />
            </div>

            <div className="slider-group">
              <div className="slider-header">
                <span>Error Rate:</span>
                <span className="slider-val">{simErrorRate}%</span>
              </div>
              <input 
                type="range" 
                min="0" 
                max="50" 
                step="0.1"
                className="telemetry-range"
                value={simErrorRate}
                onChange={(e) => setSimErrorRate(parseFloat(e.target.value))}
              />
            </div>

            <div className="slider-group">
              <div className="slider-header">
                <span>Request Volume:</span>
                <span className="slider-val">{simRequestVolume} req/s</span>
              </div>
              <input 
                type="range" 
                min="0" 
                max="15000" 
                step="100"
                className="telemetry-range"
                value={simRequestVolume}
                onChange={(e) => setSimRequestVolume(parseInt(e.target.value, 10))}
              />
            </div>

            <button 
              className="btn btn-primary"
              style={{ width: '100%', marginTop: '6px' }}
              onClick={handleApplySimulation}
            >
              Apply Simulated Telemetry
            </button>
          </div>
        )}

        {/* TAB 4: EDIT METADATA & DELETE */}
        {activeTab === 'edit' && (
          <form onSubmit={handleSaveMetadata} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <div className="form-group">
              <label className="form-label">Service Name</label>
              <input 
                type="text" 
                className="form-input"
                value={editName}
                onChange={(e) => setEditName(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Service Type</label>
              <select 
                className="form-select"
                value={editType}
                onChange={(e) => setEditType(e.target.value)}
              >
                <option value="gateway">Gateway</option>
                <option value="security">Security / Auth</option>
                <option value="compute">Compute / Microservice</option>
                <option value="database">Database</option>
                <option value="cache">Cache</option>
                <option value="messaging">Messaging</option>
                <option value="analytics">Analytics</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Description</label>
              <textarea 
                className="form-textarea"
                rows="3"
                value={editDescription}
                onChange={(e) => setEditDescription(e.target.value)}
              />
            </div>

            <button type="submit" className="btn btn-primary" style={{ width: '100%' }}>
              Save Service Details
            </button>

            <div style={{ marginTop: '20px', paddingTop: '16px', borderTop: '1px solid var(--border-color)' }}>
              <div style={{ fontSize: '0.8rem', color: '#ef4444', fontWeight: 700, marginBottom: '6px' }}>
                Danger Zone
              </div>
              <p style={{ fontSize: '0.72rem', color: 'var(--text-dim)', marginBottom: '10px' }}>
                Deleting this service will also cascade delete all its connected incoming and outgoing dependencies.
              </p>
              <button 
                type="button"
                className="btn btn-danger" 
                style={{ width: '100%' }}
                onClick={() => onDeleteService(selectedNode.id, detailedService?.name || selectedNode.name)}
              >
                <Trash2 size={16} />
                <span>Delete Service</span>
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
