import React from 'react';
import { 
  ShieldCheck, 
  Plus, 
  Share2, 
  RotateCcw, 
  RefreshCw, 
  Network, 
  BellRing, 
  GitBranch, 
  Search, 
  Bot, 
  FlaskConical, 
  LifeBuoy, 
  Award,
  LayoutDashboard,
  Route,
  FileText,
  Bell
} from 'lucide-react';

export default function Navbar({ 
  activeModule = 'unified-dashboard',
  onSelectModule,
  unacknowledgedAlertsCount = 0,
  unreadNotificationCount = 0,
  onOpenSearch,
  onOpenNotifications,
  onAddService, 
  onAddDependency, 
  onResetTopology, 
  onRefresh, 
  loading 
}) {
  const getModuleBadge = () => {
    switch (activeModule) {
      case 'unified-dashboard': return 'Module 10: Unified Overview';
      case 'incident-workflow': return 'Module 10: Incident Workflow';
      case 'reports-center': return 'Module 10: Reports Center';
      case 'digital-twin': return 'Module 1';
      case 'anomaly-detection': return 'Module 2';
      case 'cascade-prediction': return 'Module 3';
      case 'root-cause-analysis': return 'Module 4';
      case 'diagnostic-agent': return 'Module 5';
      case 'what-if-simulation': return 'Module 6';
      case 'recovery-planning': return 'Module 7';
      case 'recovery-validation': return 'Module 8';
      case 'resilience-benchmark': return 'Module 9';
      default: return 'Module 10';
    }
  };

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
              {getModuleBadge()}
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
          className={`nav-tab-btn ${activeModule === 'unified-dashboard' ? 'active' : ''}`}
          onClick={() => onSelectModule('unified-dashboard')}
          title="Module 10: Unified Overview Dashboard & AI Insights"
        >
          <LayoutDashboard size={15} />
          <span>Overview</span>
        </button>

        <button
          className={`nav-tab-btn ${activeModule === 'digital-twin' ? 'active' : ''}`}
          onClick={() => onSelectModule('digital-twin')}
          title="Module 1: Virtual Cloud Digital Twin & Cytoscape Dependency Map"
        >
          <Network size={15} />
          <span>Digital Twin</span>
        </button>

        <button
          className={`nav-tab-btn ${activeModule === 'anomaly-detection' ? 'active' : ''}`}
          onClick={() => onSelectModule('anomaly-detection')}
          title="Module 2: AI Anomaly Detection & Early Warning"
        >
          <BellRing size={15} />
          <span>Anomalies</span>
          {unacknowledgedAlertsCount > 0 && (
            <span className="badge-counter">{unacknowledgedAlertsCount}</span>
          )}
        </button>

        <button
          className={`nav-tab-btn ${activeModule === 'cascade-prediction' ? 'active' : ''}`}
          onClick={() => onSelectModule('cascade-prediction')}
          title="Module 3: Cascading Failure Prediction Engine"
        >
          <GitBranch size={15} />
          <span>Cascades</span>
        </button>

        <button
          className={`nav-tab-btn ${activeModule === 'root-cause-analysis' ? 'active' : ''}`}
          onClick={() => onSelectModule('root-cause-analysis')}
          title="Module 4: Evidence-Grounded Root Cause Analysis (RCA)"
        >
          <Search size={15} />
          <span>RCA</span>
        </button>

        <button
          className={`nav-tab-btn ${activeModule === 'diagnostic-agent' ? 'active' : ''}`}
          onClick={() => onSelectModule('diagnostic-agent')}
          title="Module 5: Adaptive AI Diagnostic Agent"
        >
          <Bot size={15} />
          <span>Agent</span>
        </button>

        <button
          className={`nav-tab-btn ${activeModule === 'what-if-simulation' ? 'active' : ''}`}
          onClick={() => onSelectModule('what-if-simulation')}
          title="Module 6: What-If Scenario Simulation Engine"
        >
          <FlaskConical size={15} />
          <span>What-If</span>
        </button>

        <button
          className={`nav-tab-btn ${activeModule === 'recovery-planning' ? 'active' : ''}`}
          onClick={() => onSelectModule('recovery-planning')}
          title="Module 7: Intelligent Recovery Planning & Risk Assessment"
        >
          <LifeBuoy size={15} />
          <span>Recovery</span>
        </button>

        <button
          className={`nav-tab-btn ${activeModule === 'recovery-validation' ? 'active' : ''}`}
          onClick={() => onSelectModule('recovery-validation')}
          title="Module 8: Automated Recovery Validation and Verification"
        >
          <ShieldCheck size={15} />
          <span>Validation</span>
        </button>

        <button
          className={`nav-tab-btn ${activeModule === 'resilience-benchmark' ? 'active' : ''}`}
          onClick={() => onSelectModule('resilience-benchmark')}
          title="Module 9: Resilience Benchmarking & Performance Evaluation"
        >
          <Award size={15} />
          <span>Benchmark</span>
        </button>

        <button
          className={`nav-tab-btn ${activeModule === 'incident-workflow' ? 'active' : ''}`}
          onClick={() => onSelectModule('incident-workflow')}
          title="Module 10: 10-Step Guided Incident Lifecycle Investigation"
        >
          <Route size={15} />
          <span>Workflow</span>
        </button>

        <button
          className={`nav-tab-btn ${activeModule === 'reports-center' ? 'active' : ''}`}
          onClick={() => onSelectModule('reports-center')}
          title="Module 10: Reports Center & CSV/JSON Export"
        >
          <FileText size={15} />
          <span>Reports</span>
        </button>
      </div>

      <div className="header-actions">
        <button 
          className="btn btn-secondary" 
          onClick={onOpenSearch}
          title="Global Search across all entities (Ctrl+K)"
          style={{ padding: '0.45rem 0.65rem' }}
        >
          <Search size={15} />
        </button>

        <button 
          className="btn btn-secondary" 
          onClick={onOpenNotifications}
          title="Notifications"
          style={{ padding: '0.45rem 0.65rem', position: 'relative' }}
        >
          <Bell size={15} />
          {unreadNotificationCount > 0 && (
            <span className="badge-counter" style={{ position: 'absolute', top: '-4px', right: '-4px', fontSize: '0.65rem' }}>
              {unreadNotificationCount}
            </span>
          )}
        </button>

        <div className="simulated-pill" title="All telemetry data is dynamically simulated">
          <span className="pulse-dot"></span>
          <span>Simulation Mode</span>
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
              <span>Reset</span>
            </button>

            <button 
              className="btn btn-secondary" 
              onClick={onAddDependency}
              title="Connect two services with a directed dependency"
            >
              <Share2 size={15} />
              <span>Add Dep</span>
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
            title="Refresh active view"
          >
            <RefreshCw size={15} className={loading ? "animate-spin" : ""} />
            <span>Refresh</span>
          </button>
        )}
      </div>
    </header>
  );
}
