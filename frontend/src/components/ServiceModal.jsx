import React, { useState } from 'react';
import { X, Plus, Server } from 'lucide-react';

export default function ServiceModal({ isOpen, onClose, onSubmit }) {
  const [name, setName] = useState('');
  const [id, setId] = useState('');
  const [serviceType, setServiceType] = useState('compute');
  const [description, setDescription] = useState('');
  const [cpuUsage, setCpuUsage] = useState(25.0);
  const [memoryUsage, setMemoryUsage] = useState(35.0);
  const [latencyMs, setLatencyMs] = useState(40.0);
  const [errorRate, setErrorRate] = useState(0.1);
  const [requestVolume, setRequestVolume] = useState(1200);

  if (!isOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!name.trim()) return;

    const payload = {
      name: name.trim(),
      id: id.trim() || undefined,
      service_type: serviceType,
      description: description.trim() || undefined,
      cpu_usage: parseFloat(cpuUsage),
      memory_usage: parseFloat(memoryUsage),
      latency_ms: parseFloat(latencyMs),
      error_rate: parseFloat(errorRate),
      request_volume: parseInt(requestVolume, 10)
    };

    onSubmit(payload);
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Server size={18} color="#0ea5e9" />
            <h3>Add New Cloud Service</h3>
          </div>
          <button className="btn-icon" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            <div className="form-group">
              <label className="form-label">Service Name *</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g., Inventory Service"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Custom Service ID (optional)</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g., srv-inventory (auto-generated if empty)"
                value={id}
                onChange={(e) => setId(e.target.value)}
              />
              <span className="form-hint">Leave blank to automatically slugify from name.</span>
            </div>

            <div className="form-group">
              <label className="form-label">Service Type</label>
              <select
                className="form-select"
                value={serviceType}
                onChange={(e) => setServiceType(e.target.value)}
              >
                <option value="gateway">Gateway</option>
                <option value="security">Security / Auth</option>
                <option value="compute">Compute / Microservice</option>
                <option value="database">Database</option>
                <option value="cache">Cache</option>
                <option value="messaging">Messaging / Queue</option>
                <option value="analytics">Analytics</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Description</label>
              <textarea
                className="form-textarea"
                rows="2"
                placeholder="Role and functionality of this cloud service..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>

            <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '12px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span className="form-label" style={{ fontWeight: 700 }}>Initial Simulated Telemetry</span>
                <span className="simulated-pill" style={{ padding: '2px 8px', fontSize: '0.68rem' }}>
                  Simulated
                </span>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                <div className="form-group">
                  <label className="form-label">CPU Usage (%)</label>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    step="0.1"
                    className="form-input"
                    value={cpuUsage}
                    onChange={(e) => setCpuUsage(e.target.value)}
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Memory Usage (%)</label>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    step="0.1"
                    className="form-input"
                    value={memoryUsage}
                    onChange={(e) => setMemoryUsage(e.target.value)}
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Latency (ms)</label>
                  <input
                    type="number"
                    min="1"
                    step="1"
                    className="form-input"
                    value={latencyMs}
                    onChange={(e) => setLatencyMs(e.target.value)}
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Error Rate (%)</label>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    step="0.01"
                    className="form-input"
                    value={errorRate}
                    onChange={(e) => setErrorRate(e.target.value)}
                  />
                </div>
              </div>

              <div className="form-group" style={{ marginTop: '10px' }}>
                <label className="form-label">Requests / Sec</label>
                <input
                  type="number"
                  min="0"
                  step="10"
                  className="form-input"
                  value={requestVolume}
                  onChange={(e) => setRequestVolume(e.target.value)}
                />
              </div>
            </div>
          </div>

          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary">
              <Plus size={16} />
              <span>Create Service</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
