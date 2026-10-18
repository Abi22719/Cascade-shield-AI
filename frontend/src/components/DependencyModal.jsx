import React, { useState } from 'react';
import { X, Share2, AlertTriangle, ArrowRight } from 'lucide-react';

export default function DependencyModal({ 
  isOpen, 
  onClose, 
  onSubmit, 
  services = [],
  existingEdges = [] 
}) {
  const [sourceId, setSourceId] = useState('');
  const [targetId, setTargetId] = useState('');
  const [dependencyType, setDependencyType] = useState('sync_http');
  const [description, setDescription] = useState('');

  if (!isOpen) return null;

  // Validation checks
  const isSelf = sourceId && targetId && sourceId === targetId;
  const isDuplicate = sourceId && targetId && existingEdges.some(
    e => e.data.source === sourceId && e.data.target === targetId
  );

  // Check if target can reach source (forming cycle)
  const checkCycle = () => {
    if (!sourceId || !targetId || isSelf) return false;
    
    // BFS to find if path exists from targetId to sourceId in existingEdges
    const adj = {};
    existingEdges.forEach(e => {
      const u = e.data.source;
      const v = e.data.target;
      if (!adj[u]) adj[u] = [];
      adj[u].push(v);
    });

    const queue = [targetId];
    const visited = new Set([targetId]);

    while (queue.length > 0) {
      const curr = queue.shift();
      if (curr === sourceId) {
        return true;
      }
      for (const neighbor of (adj[curr] || [])) {
        if (!visited.has(neighbor)) {
          visited.add(neighbor);
          queue.push(neighbor);
        }
      }
    }
    return false;
  };

  const willCauseCycle = checkCycle();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!sourceId || !targetId || isSelf || isDuplicate) return;

    onSubmit({
      source_service_id: sourceId,
      target_service_id: targetId,
      dependency_type: dependencyType,
      description: description.trim() || undefined
    });
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Share2 size={18} color="#0ea5e9" />
            <h3>Add Directed Dependency</h3>
          </div>
          <button className="btn-icon" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            <div className="form-group">
              <label className="form-label">Source Service (Caller) *</label>
              <select
                className="form-select"
                value={sourceId}
                onChange={(e) => setSourceId(e.target.value)}
                required
              >
                <option value="">-- Select Source Service --</option>
                {services.map(s => (
                  <option key={s.id} value={s.id}>
                    {s.name} ({s.id})
                  </option>
                ))}
              </select>
            </div>

            <div style={{ display: 'flex', justifyContent: 'center', margin: '4px 0' }}>
              <ArrowRight size={20} color="var(--color-primary)" />
            </div>

            <div className="form-group">
              <label className="form-label">Target Service (Dependency) *</label>
              <select
                className="form-select"
                value={targetId}
                onChange={(e) => setTargetId(e.target.value)}
                required
              >
                <option value="">-- Select Target Service --</option>
                {services.map(s => (
                  <option key={s.id} value={s.id} disabled={s.id === sourceId}>
                    {s.name} ({s.id})
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Dependency Type</label>
              <select
                className="form-select"
                value={dependencyType}
                onChange={(e) => setDependencyType(e.target.value)}
              >
                <option value="sync_http">Synchronous HTTP / REST</option>
                <option value="async_message">Asynchronous Event / Queue</option>
                <option value="database_read_write">Database Read / Write</option>
                <option value="cache_lookup">In-Memory Cache Lookup</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Description / Rationale</label>
              <textarea
                className="form-textarea"
                rows="2"
                placeholder="Why does this service depend on the target?..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>

            {/* Validation Warnings */}
            {isSelf && (
              <div style={{ color: '#ef4444', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <AlertTriangle size={15} />
                Self-dependencies are not permitted.
              </div>
            )}

            {isDuplicate && (
              <div style={{ color: '#ef4444', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <AlertTriangle size={15} />
                A directed dependency already exists between these two services.
              </div>
            )}

            {willCauseCycle && !isSelf && !isDuplicate && (
              <div style={{ 
                background: 'rgba(245, 158, 11, 0.12)', 
                border: '1px solid rgba(245, 158, 11, 0.4)',
                borderRadius: 'var(--radius-sm)',
                padding: '8px 12px',
                color: '#fde68a', 
                fontSize: '0.78rem', 
                display: 'flex', 
                alignItems: 'flex-start', 
                gap: '8px' 
              }}>
                <AlertTriangle size={16} color="#f59e0b" style={{ flexShrink: 0, marginTop: '2px' }} />
                <div>
                  <strong>Circular Dependency Warning:</strong> Adding this edge will introduce a circular loop into the topology. The backend will flag this cycle.
                </div>
              </div>
            )}
          </div>

          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button 
              type="submit" 
              className="btn btn-primary"
              disabled={!sourceId || !targetId || isSelf || isDuplicate}
            >
              <Share2 size={16} />
              <span>Connect Services</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
