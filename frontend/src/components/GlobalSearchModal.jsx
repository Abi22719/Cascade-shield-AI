import React, { useState, useEffect, useRef } from 'react';
import { Search, X, Server, BellRing, GitBranch, AlertCircle, LifeBuoy, Award, ShieldCheck, ArrowRight } from 'lucide-react';
import { dashboardApi } from '../services/dashboardApi';

export default function GlobalSearchModal({ isOpen, onClose, onNavigateModule }) {
  const [query, setQuery] = useState('');
  const [moduleFilter, setModuleFilter] = useState('');
  const [results, setResults] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const inputRef = useRef(null);

  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 50);
      dashboardApi.getSearchSuggestions().then(res => {
        if (res?.suggestions) setSuggestions(res.suggestions);
      }).catch(() => {});
    } else {
      setQuery('');
      setResults([]);
    }
  }, [isOpen]);

  useEffect(() => {
    if (!isOpen) return;
    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        const res = await dashboardApi.search({
          q: query.trim(),
          module: moduleFilter || undefined,
          limit: 25
        });
        setResults(res?.results || []);
      } catch (err) {
        console.error("Search error:", err);
      } finally {
        setLoading(false);
      }
    }, 200);

    return () => clearTimeout(timer);
  }, [query, moduleFilter, isOpen]);

  if (!isOpen) return null;

  const handleSelectResult = (item) => {
    onClose();
    if (item.source_module === 'module_1') onNavigateModule('digital-twin');
    else if (item.source_module === 'module_2') onNavigateModule('anomaly-detection');
    else if (item.source_module === 'module_3') onNavigateModule('cascade-prediction');
    else if (item.source_module === 'module_4') onNavigateModule('root-cause-analysis');
    else if (item.source_module === 'module_5') onNavigateModule('diagnostic-agent');
    else if (item.source_module === 'module_6') onNavigateModule('what-if-simulation');
    else if (item.source_module === 'module_7') onNavigateModule('recovery-planning');
    else if (item.source_module === 'module_8') onNavigateModule('recovery-validation');
    else if (item.source_module === 'module_9') onNavigateModule('resilience-benchmark');
    else onNavigateModule('unified-dashboard');
  };

  const getRecordIcon = (type) => {
    switch(type) {
      case 'service': return <Server size={16} color="#38bdf8" />;
      case 'alert': return <BellRing size={16} color="#f59e0b" />;
      case 'incident': return <AlertCircle size={16} color="#ec4899" />;
      case 'scenario': return <GitBranch size={16} color="#a855f7" />;
      case 'plan': return <LifeBuoy size={16} color="#06b6d4" />;
      case 'validation': return <ShieldCheck size={16} color="#10b981" />;
      case 'benchmark': return <Award size={16} color="#fbbf24" />;
      default: return <Search size={16} color="#94a3b8" />;
    }
  };

  const filterTabs = [
    { id: '', label: 'All Modules' },
    { id: 'module_1', label: 'Services' },
    { id: 'module_2', label: 'Alerts' },
    { id: 'module_4', label: 'Incidents' },
    { id: 'module_6', label: 'Scenarios' },
    { id: 'module_7', label: 'Plans' },
    { id: 'module_8', label: 'Validations' },
    { id: 'module_9', label: 'Benchmarks' },
  ];

  return (
    <div className="search-modal-backdrop" onClick={onClose}>
      <div className="search-modal-content" onClick={(e) => e.stopPropagation()}>
        {/* Search Input */}
        <div className="search-input-header">
          <Search size={20} color="#38bdf8" />
          <input 
            ref={inputRef}
            type="text"
            placeholder="Search services, alerts, incidents, recovery plans, scenarios..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Escape') onClose();
            }}
          />
          <button 
            onClick={onClose} 
            style={{ background: 'transparent', border: 'none', color: '#94a3b8', cursor: 'pointer' }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Filter Pills */}
        <div style={{ display: 'flex', gap: '0.4rem', padding: '0.65rem 1.25rem', borderBottom: '1px solid rgba(255, 255, 255, 0.08)', overflowX: 'auto' }}>
          {filterTabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setModuleFilter(tab.id)}
              style={{
                background: moduleFilter === tab.id ? 'rgba(56, 189, 248, 0.2)' : 'rgba(255, 255, 255, 0.05)',
                border: moduleFilter === tab.id ? '1px solid #38bdf8' : '1px solid rgba(255, 255, 255, 0.08)',
                color: moduleFilter === tab.id ? '#38bdf8' : '#cbd5e1',
                padding: '0.25rem 0.65rem',
                borderRadius: '16px',
                fontSize: '0.75rem',
                cursor: 'pointer',
                whiteSpace: 'nowrap'
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Results Stream */}
        <div className="search-modal-results">
          {loading && (
            <div style={{ padding: '1rem', color: '#94a3b8', fontSize: '0.85rem' }}>
              Searching cross-module entities...
            </div>
          )}

          {!loading && results.length === 0 && (
            <div style={{ padding: '1.5rem', textAlign: 'center', color: '#64748b', fontSize: '0.85rem' }}>
              {query ? `No entities matching "${query}"` : 'Type to search or select a suggestion:'}
              {!query && suggestions.length > 0 && (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', justifyContent: 'center', marginTop: '0.75rem' }}>
                  {suggestions.map((s, idx) => (
                    <span 
                      key={idx}
                      onClick={() => setQuery(s)}
                      style={{
                        background: 'rgba(255, 255, 255, 0.06)',
                        padding: '0.2rem 0.55rem',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        color: '#94a3b8',
                        fontSize: '0.76rem'
                      }}
                    >
                      {s}
                    </span>
                  ))}
                </div>
              )}
            </div>
          )}

          {results.map((item) => (
            <div 
              key={item.record_id}
              className="search-result-row"
              onClick={() => handleSelectResult(item)}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <div style={{ width: '28px', height: '28px', borderRadius: '6px', background: 'rgba(255, 255, 255, 0.05)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  {getRecordIcon(item.record_type)}
                </div>
                <div style={{ display: 'flex', flexDirection: 'column' }}>
                  <span style={{ fontWeight: 600, color: '#f8fafc', fontSize: '0.86rem' }}>{item.title}</span>
                  <span style={{ color: '#94a3b8', fontSize: '0.75rem' }}>{item.subtitle}</span>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span className="insight-module-badge" style={{ fontSize: '0.68rem' }}>
                  {item.source_module}
                </span>
                <ArrowRight size={14} color="#64748b" />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
