import React from 'react';
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
  Activity
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
  resilienceScore = 89.4
}) {
  const getModuleMeta = () => {
    switch (activeModule) {
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
          moduleNum: 'Module 10',
          title: 'Cloud Resilience Platform',
          category: 'Enterprise Suite'
        };
    }
  };

  const meta = getModuleMeta();

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
      <div className="topbar-right-section">
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
            <span className="drill-btn-text">Resilience Drill</span>
          </button>
        )}

        {/* Digital Twin Context Actions */}
        {activeModule === 'digital-twin' && (
          <div className="topbar-context-actions">
            <button
              className="btn btn-secondary topbar-action-btn"
              onClick={onResetTopology}
              title="Reset digital twin to default 9 sample services"
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
          title="Trigger live telemetry jitter refresh and reload active view"
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
      </div>
    </header>
  );
}
