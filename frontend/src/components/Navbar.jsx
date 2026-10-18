import React from 'react';
import { 
  ShieldCheck, 
  Plus, 
  Share2, 
  RotateCcw, 
  RefreshCw,
  Activity,
  Network,
  BellRing
} from 'lucide-react';

export default function Navbar({ 
  activeModule = 'digital-twin',
  onSelectModule,
  unacknowledgedAlertsCount = 0,
  onAddService, 
  onAddDependency, 
  onResetTopology, 
  onRefresh, 
  loading 
}) {
  return (
    <header className="app-header">
      <div className="brand-section">
        <div className="brand-icon-wrapper">
          <ShieldCheck size={26} />
        </div>
        <div className="brand-title-group">
          <h1>
            CascadeShield AI
            <span className="module-badge">
              {activeModule === 'digital-twin' ? 'Module 1' : 'Module 2'}
            </span>
          </h1>
          <p className="brand-subtitle">
            Cloud Digital Twin & Intelligent Resilience Engine
          </p>
        </div>
      </div>

      {/* Module Navigation Tabs */}
      <div className="nav-tab-switcher">
        <button
          className={`nav-tab-btn ${activeModule === 'digital-twin' ? 'active' : ''}`}
          onClick={() => onSelectModule('digital-twin')}
          title="Module 1: Virtual Cloud Digital Twin & Cytoscape Dependency Map"
        >
          <Network size={15} />
          <span>Digital Twin & Graph</span>
        </button>
        <button
          className={`nav-tab-btn ${activeModule === 'anomaly-detection' ? 'active' : ''}`}
          onClick={() => onSelectModule('anomaly-detection')}
          title="Module 2: AI Anomaly Detection & Early Warning"
        >
          <BellRing size={15} />
          <span>Anomaly Detection</span>
          {unacknowledgedAlertsCount > 0 && (
            <span className="badge-counter">{unacknowledgedAlertsCount}</span>
          )}
        </button>
      </div>

      <div className="header-actions">
        <div className="simulated-pill" title="All telemetry data is dynamically simulated">
          <span className="pulse-dot"></span>
          <span>Simulated Telemetry</span>
        </div>

        {activeModule === 'digital-twin' ? (
          <>
            <button 
              className="btn btn-secondary" 
              onClick={onRefresh}
              disabled={loading}
              title="Refresh topology and metrics"
            >
              <RefreshCw size={15} className={loading ? "animate-spin" : ""} />
              <span>Refresh</span>
            </button>

            <button 
              className="btn btn-secondary" 
              onClick={onResetTopology}
              title="Reset to default 9 sample services"
            >
              <RotateCcw size={15} />
              <span>Reset Default</span>
            </button>

            <button 
              className="btn btn-secondary" 
              onClick={onAddDependency}
              title="Connect two services with a directed dependency"
            >
              <Share2 size={15} />
              <span>Add Dependency</span>
            </button>

            <button 
              className="btn btn-primary" 
              onClick={onAddService}
              title="Register a new service in the cloud digital twin"
            >
              <Plus size={16} />
              <span>Add Service</span>
            </button>
          </>
        ) : (
          <button 
            className="btn btn-secondary" 
            onClick={onRefresh}
            disabled={loading}
            title="Refresh anomalies and metrics"
          >
            <RefreshCw size={15} className={loading ? "animate-spin" : ""} />
            <span>Refresh</span>
          </button>
        )}
      </div>
    </header>
  );
}
