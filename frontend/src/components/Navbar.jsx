import React from 'react';
import { 
  ShieldCheck, 
  Plus, 
  Share2, 
  RotateCcw, 
  RefreshCw,
  Activity
} from 'lucide-react';

export default function Navbar({ 
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
            <span className="module-badge">Module 1</span>
          </h1>
          <p className="brand-subtitle">
            Cloud Digital Twin & Dependency Mapping Engine
          </p>
        </div>
      </div>

      <div className="header-actions">
        <div className="simulated-pill" title="All telemetry data is dynamically simulated">
          <span className="pulse-dot"></span>
          <span>Simulated Telemetry</span>
        </div>

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
      </div>
    </header>
  );
}
