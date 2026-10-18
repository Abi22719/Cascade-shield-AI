import React from 'react';
import { Search, Filter, Layers, X, ShieldAlert } from 'lucide-react';

export default function FilterBar({
  searchQuery,
  onSearchChange,
  selectedType,
  onTypeChange,
  selectedHealth,
  onHealthChange,
  currentLayout,
  onLayoutChange,
  impactActive,
  onClearImpact,
  matchingCount,
  totalCount
}) {
  return (
    <div className="toolbar-container">
      <div className="toolbar-filters">
        {/* Search */}
        <div className="search-input-wrapper">
          <Search size={15} className="search-icon" />
          <input
            type="text"
            className="search-input"
            placeholder="Search service name or ID..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
          />
          {searchQuery && (
            <button 
              className="btn-icon" 
              style={{ position: 'absolute', right: '6px', padding: '2px', background: 'transparent', border: 'none' }}
              onClick={() => onSearchChange('')}
              title="Clear search"
            >
              <X size={14} />
            </button>
          )}
        </div>

        {/* Filter by Type */}
        <select 
          className="filter-select"
          value={selectedType}
          onChange={(e) => onTypeChange(e.target.value)}
        >
          <option value="">All Service Types</option>
          <option value="gateway">Gateway</option>
          <option value="security">Security / Auth</option>
          <option value="compute">Compute / Microservice</option>
          <option value="database">Database</option>
          <option value="cache">Cache</option>
          <option value="messaging">Messaging</option>
          <option value="analytics">Analytics</option>
        </select>

        {/* Filter by Health */}
        <select 
          className="filter-select"
          value={selectedHealth}
          onChange={(e) => onHealthChange(e.target.value)}
        >
          <option value="">All Health Statuses</option>
          <option value="HEALTHY">Healthy Only</option>
          <option value="WARNING">Warning Only</option>
          <option value="CRITICAL">Critical Only</option>
        </select>

        {/* Layout Selector */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Layers size={14} color="var(--text-dim)" />
          <select 
            className="filter-select"
            value={currentLayout}
            onChange={(e) => onLayoutChange(e.target.value)}
            title="Graph Layout Algorithm"
          >
            <option value="dagre-lr">Hierarchical (Left to Right)</option>
            <option value="dagre-tb">Hierarchical (Top to Bottom)</option>
            <option value="breadthfirst">Breadth-First Tree</option>
            <option value="cose">Force-Directed (CoSE)</option>
            <option value="circle">Circular</option>
          </select>
        </div>

        {/* Impact Analysis Mode Indicator */}
        {impactActive && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ 
              display: 'inline-flex', 
              alignItems: 'center', 
              gap: '6px', 
              background: 'rgba(14, 165, 233, 0.2)', 
              color: '#38bdf8', 
              border: '1px solid #0ea5e9',
              padding: '4px 10px', 
              borderRadius: '6px', 
              fontSize: '0.78rem',
              fontWeight: 600
            }}>
              <ShieldAlert size={14} />
              Blast Radius Mode Active
              <button 
                onClick={onClearImpact} 
                style={{ background: 'none', border: 'none', color: 'inherit', cursor: 'pointer', display: 'flex' }}
                title="Exit impact analysis view"
              >
                <X size={14} />
              </button>
            </span>
          </div>
        )}
      </div>

      <div className="toolbar-actions">
        <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>
          Showing <strong>{matchingCount}</strong> of {totalCount} services
        </span>
      </div>
    </div>
  );
}
