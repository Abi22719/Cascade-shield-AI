import React, { useState } from 'react';
import {
  Search,
  Bell,
  RefreshCw,
  RotateCcw,
  Share2,
  Plus,
  Menu,
  ShieldCheck,
  ChevronRight,
  Sparkles,
  Zap,
  Sun,
  Moon,
  Activity,
  User,
  Radio,
  ChevronDown
} from 'lucide-react';

export default function TopHeader({
  activeModule = 'unified-dashboard',
  sidebarCollapsed = false,
  onToggleSidebar,
  onOpenSearch,
  onOpenNotifications,
  unreadNotificationCount = 0,
  onRefresh,
  loading = false,
  onAddService,
  onAddDependency,
  onResetTopology,
  theme = 'dark',
  onToggleTheme,
  onOpenDrills,
  resilienceScore = 89.4,
  currentUser = { username: 'admin', role: 'Administrator' },
  onRoleChange = null
}) {
  const [roleMenuOpen, setRoleMenuOpen] = useState(false);

  const getModuleMeta = () => {
    switch (activeModule) {
      // 8 ENTERPRISE PORTALS
      case 'portal-admin':
        return {
          moduleNum: 'Portal 1',
          title: 'Cloud Administrator Portal',
          category: 'Infrastructure Administration'
        };
      case 'portal-incident':
        return {
          moduleNum: 'Portal 2',
          title: 'Incident Response Portal',
          category: 'Triage & War Room'
        };
      case 'portal-copilot':
        return {
          moduleNum: 'Portal 3',
          title: 'AI Resilience Copilot Portal',
          category: 'Autonomous Intelligence'
        };
      case 'portal-digital-twin':
        return {
          moduleNum: 'Portal 4',
          title: 'Digital Twin Simulation Portal',
          category: 'Chaos & Blast Radius Sandbox'
        };
      case 'portal-analytics':
        return {
          moduleNum: 'Portal 5',
          title: 'Reliability Analytics Portal',
          category: 'Metrics & Model Accuracy'
        };
      case 'portal-developer':
        return {
          moduleNum: 'Portal 6',
          title: 'Developer Portal',
          category: 'APIs, Schemas & SDKs'
        };
      case 'portal-security':
        return {
          moduleNum: 'Portal 7',
          title: 'Security and Audit Portal',
          category: 'RBAC & Immutable Governance'
        };
      case 'portal-reports':
        return {
          moduleNum: 'Portal 8',
          title: 'Reports and Knowledge Portal',
          category: 'Post-Mortems & Playbooks'
        };

      // MODULES 1 - 10
      case 'unified-dashboard':
        return {
          moduleNum: 'Module 10',
          title: 'Unified Executive Overview & AI Insights',
          category: 'Observability & Control'
        };
      case 'digital-twin':
        return {
          moduleNum: 'Module 1',
          title: 'Virtual Cloud Digital Twin & Topology Map',
          category: 'Dependency Modeling'
        };
      case 'anomaly-detection':
        return {
          moduleNum: 'Module 2',
          title: 'AI Anomaly Detection & Early Warning',
          category: 'Statistical & ML Alerts'
        };
      case 'cascade-prediction':
        return {
          moduleNum: 'Module 3',
          title: 'Cascading Failure Prediction & Blast Radius',
          category: 'Failure Propagation'
        };
      case 'root-cause-analysis':
        return {
          moduleNum: 'Module 4',
          title: 'Evidence-Grounded Root Cause Analysis (RCA)',
          category: 'Causal Inference'
        };
      case 'diagnostic-agent':
        return {
          moduleNum: 'Module 5',
          title: 'Adaptive AI Diagnostic Agent',
          category: 'Autonomous Investigation'
        };
      case 'what-if-simulation':
        return {
          moduleNum: 'Module 6',
          title: 'What-If Failure Scenario Simulation Engine',
          category: 'Chaos & Surge Modeling'
        };
      case 'recovery-planning':
        return {
          moduleNum: 'Module 7',
          title: 'Intelligent Recovery Planning & Risk Assessment',
          category: 'Remediation Synthesis'
        };
      case 'recovery-validation':
        return {
          moduleNum: 'Module 8',
          title: 'Automated Recovery Validation & Verification',
          category: 'Sandbox Testing'
        };
      case 'resilience-benchmark':
        return {
          moduleNum: 'Module 9',
          title: 'Resilience Benchmarking & Quantitative Evaluation',
          category: 'Standardized Baselines'
        };
      case 'incident-workflow':
        return {
          moduleNum: 'Module 10',
          title: '10-Step Guided Incident Lifecycle Investigation',
          category: 'End-to-End Workflow'
        };
      case 'reports-center':
        return {
          moduleNum: 'Module 10',
          title: 'Unified Reports Center & Post-Mortem Export',
          category: 'Audit & Compliance'
        };
      default:
        return {
          moduleNum: 'Enterprise',
          title: 'CascadeShield AI Command Center',
          category: 'Resilience Suite'
        };
    }
  };

  const meta = getModuleMeta();

  const roles = [
    'Administrator',
    'Cloud Operator',
    'Incident Responder',
    'Reliability Analyst',
    'Developer',
    'Read-Only Viewer'
  ];

  return (
    <header className="enterprise-topbar">
      {/* Left: Mobile Toggle & Breadcrumbs */}
      <div className="topbar-left-section">
        {onToggleSidebar && (
          <button
            className="topbar-mobile-menu-btn"
            onClick={onToggleSidebar}
            title={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            aria-label="Toggle navigation sidebar"
          >
            <Menu size={18} />
          </button>
        )}

        <div className="topbar-breadcrumb-trail">
          <span className="breadcrumb-root">CascadeShield AI</span>
          <ChevronRight size={14} className="breadcrumb-separator" />
          <span className="breadcrumb-module-badge">{meta.moduleNum}</span>
          <span className="breadcrumb-title" title={meta.title}>{meta.title}</span>
        </div>
      </div>

      {/* Center: Global Quick Search Trigger */}
      <div className="topbar-center-section">
        <button
          className="topbar-search-trigger"
          onClick={onOpenSearch}
          title="Search services, alerts, incidents (Ctrl + K)"
        >
          <Search size={14} className="search-trigger-icon" />
          <span className="search-trigger-text">
            Search services, incidents, metrics, alerts...
          </span>
          <kbd className="search-trigger-kbd">Ctrl K</kbd>
        </button>
      </div>

      {/* Right: Actions, Simulation Mode, Refresh, Theme Toggle, Notifications */}
      <div className="topbar-right-section" style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
        {/* Simulation Only Badge */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.35rem',
          background: 'rgba(234, 179, 8, 0.12)',
          border: '1px solid rgba(234, 179, 8, 0.3)',
          color: '#facc15',
          padding: '0.25rem 0.55rem',
          borderRadius: '14px',
          fontSize: '0.7rem',
          fontWeight: 600,
          letterSpacing: '0.03em'
        }} title="Simulation environment only. Zero mutations to actual cloud infrastructure.">
          <Radio size={11} className="pulse-dot" style={{ background: '#facc15', borderRadius: '50%' }} />
          <span>SIMULATION MODE</span>
        </div>

        {/* API Connection Indicator */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.3rem',
          fontSize: '0.7rem',
          color: '#10b981',
          padding: '0.2rem 0.4rem'
        }} title="FastAPI backend connected (12ms)">
          <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#10b981' }}></span>
          <span>ONLINE</span>
        </div>

        {/* Resilience Posture Pill */}
        <div 
          className="resilience-posture-pill" 
          title={`Overall Resilience Index: ${resilienceScore}/100. Multi-pillar health verified.`}
        >
          <span className="posture-icon-wrapper">
            <ShieldCheck size={13} />
          </span>
          <span className="posture-score">{resilienceScore}%</span>
          <span className="posture-label">Resilient</span>
        </div>

        {/* Resilience Drill Trigger Button */}
        {onOpenDrills && (
          <button
            className="btn btn-drill-trigger"
            onClick={onOpenDrills}
            title="Launch interactive cloud failure chaos drills"
          >
            <Zap size={14} className="drill-icon-pulse" />
            <span className="drill-btn-text">Chaos Drill</span>
          </button>
        )}

        {/* Digital Twin Context Actions */}
        {activeModule === 'digital-twin' && (
          <div className="topbar-context-actions">
            <button
              className="btn btn-secondary topbar-action-btn"
              onClick={onResetTopology}
              title="Reset digital twin to default sample services"
            >
              <RotateCcw size={14} />
              <span>Reset</span>
            </button>

            <button
              className="btn btn-secondary topbar-action-btn"
              onClick={onAddDependency}
              title="Connect two services with a directed dependency"
            >
              <Share2 size={14} />
              <span>Add Dep</span>
            </button>

            <button
              className="btn btn-primary topbar-action-btn"
              onClick={onAddService}
              title="Register a new microservice in the digital twin"
            >
              <Plus size={15} />
              <span>Add Service</span>
            </button>
          </div>
        )}

        {/* Global Refresh Button */}
        <button
          className="btn btn-secondary topbar-refresh-btn"
          onClick={onRefresh}
          disabled={loading}
          title="Trigger live telemetry refresh and reload active view"
        >
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
          <span className="refresh-btn-label">Refresh</span>
        </button>

        {/* Light/Dark Theme Toggle Button */}
        <button
          className="topbar-icon-btn theme-toggle-btn"
          onClick={onToggleTheme}
          title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`}
          aria-label="Toggle Theme Mode"
        >
          {theme === 'dark' ? (
            <Sun size={16} className="theme-icon sun-icon" />
          ) : (
            <Moon size={16} className="theme-icon moon-icon" />
          )}
        </button>

        {/* Notifications Bell Button */}
        <button
          className="topbar-icon-btn notification-bell-btn"
          onClick={onOpenNotifications}
          title="System notifications and alerts"
          aria-label="System notifications"
        >
          <Bell size={16} />
          {unreadNotificationCount > 0 && (
            <span className="badge-counter topbar-notification-badge">
              {unreadNotificationCount}
            </span>
          )}
        </button>

        {/* User Role Switcher Pill */}
        <div style={{ position: 'relative' }}>
          <button
            onClick={() => setRoleMenuOpen(!roleMenuOpen)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              background: 'rgba(30, 41, 59, 0.7)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              padding: '0.3rem 0.65rem',
              borderRadius: '20px',
              cursor: 'pointer',
              color: '#f8fafc'
            }}
            title="Current User Profile & Active Role"
          >
            <div style={{
              width: '20px',
              height: '20px',
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #4f46e5, #06b6d4)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#fff',
              fontSize: '0.65rem',
              fontWeight: 700
            }}>
              {currentUser.username?.[0]?.toUpperCase() || 'A'}
            </div>
            <span style={{ fontSize: '0.75rem', fontWeight: 600 }}>{currentUser.role}</span>
            <ChevronDown size={12} color="#94a3b8" />
          </button>

          {roleMenuOpen && (
            <div style={{
              position: 'absolute',
              top: '110%',
              right: 0,
              background: '#0f172a',
              border: '1px solid #334155',
              borderRadius: '8px',
              boxShadow: '0 8px 24px rgba(0,0,0,0.5)',
              padding: '0.5rem',
              minWidth: '180px',
              zIndex: 1000
            }}>
              <div style={{ fontSize: '0.68rem', color: '#94a3b8', padding: '0.3rem 0.5rem', textTransform: 'uppercase', fontWeight: 600 }}>
                Switch Active Role:
              </div>
              {roles.map(r => (
                <button
                  key={r}
                  onClick={() => {
                    if (onRoleChange) onRoleChange(r);
                    setRoleMenuOpen(false);
                  }}
                  style={{
                    width: '100%',
                    textAlign: 'left',
                    background: currentUser.role === r ? 'rgba(56, 189, 248, 0.15)' : 'transparent',
                    border: 'none',
                    color: currentUser.role === r ? '#38bdf8' : '#f8fafc',
                    padding: '0.4rem 0.6rem',
                    borderRadius: '4px',
                    fontSize: '0.78rem',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between'
                  }}
                >
                  <span>{r}</span>
                  {currentUser.role === r && <span style={{ width: '5px', height: '5px', borderRadius: '50%', background: '#38bdf8' }}></span>}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
