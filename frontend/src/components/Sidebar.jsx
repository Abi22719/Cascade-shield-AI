import React from 'react';
import {
  ShieldCheck,
  LayoutDashboard,
  Network,
  BellRing,
  GitBranch,
  Search,
  Bot,
  Route,
  FlaskConical,
  LifeBuoy,
  Award,
  FileText,
  ChevronLeft,
  ChevronRight,
  Activity,
  Layers
} from 'lucide-react';

export default function Sidebar({
  activeModule = 'unified-dashboard',
  onSelectModule,
  collapsed = false,
  onToggleCollapse,
  unacknowledgedAlertsCount = 0
}) {
  const navSections = [
    {
      title: 'Platform Overview',
      items: [
        {
          id: 'unified-dashboard',
          label: 'Unified Overview',
          moduleTag: 'M10',
          icon: LayoutDashboard,
          description: 'Executive cross-module health and AI insights'
        },
        {
          id: 'digital-twin',
          label: 'Digital Twin Map',
          moduleTag: 'M1',
          icon: Network,
          description: 'Virtual cloud infrastructure and directed topology graph'
        }
      ]
    },
    {
      title: 'Detect & Predict',
      items: [
        {
          id: 'anomaly-detection',
          label: 'Anomaly Detection',
          moduleTag: 'M2',
          icon: BellRing,
          badge: unacknowledgedAlertsCount > 0 ? unacknowledgedAlertsCount : null,
          description: 'Multivariate statistical & Isolation Forest anomaly alerts'
        },
        {
          id: 'cascade-prediction',
          label: 'Cascade Prediction',
          moduleTag: 'M3',
          icon: GitBranch,
          description: 'Reverse-propagation cascading failure blast radius simulation'
        }
      ]
    },
    {
      title: 'Diagnostics & RCA',
      items: [
        {
          id: 'root-cause-analysis',
          label: 'Root Cause (RCA)',
          moduleTag: 'M4',
          icon: Search,
          description: 'Evidence-grounded Bayesian/graph suspect ranking'
        },
        {
          id: 'diagnostic-agent',
          label: 'AI Diagnostic Agent',
          moduleTag: 'M5',
          icon: Bot,
          description: 'Adaptive diagnostic session and autonomous evidence collection'
        },
        {
          id: 'incident-workflow',
          label: 'Incident Workflow',
          moduleTag: '10-Step',
          icon: Route,
          description: 'End-to-end guided incident lifecycle investigation'
        }
      ]
    },
    {
      title: 'Simulate & Validate',
      items: [
        {
          id: 'what-if-simulation',
          label: 'What-If Simulation',
          moduleTag: 'M6',
          icon: FlaskConical,
          description: 'Dynamic failure scenarios, node outages, and load surges'
        },
        {
          id: 'recovery-planning',
          label: 'Recovery Planning',
          moduleTag: 'M7',
          icon: LifeBuoy,
          description: 'Multi-strategy recovery generation and risk scoring'
        },
        {
          id: 'recovery-validation',
          label: 'Recovery Validation',
          moduleTag: 'M8',
          icon: ShieldCheck,
          description: '5-pillar automated verification across isolated sandboxes'
        },
        {
          id: 'resilience-benchmark',
          label: 'Resilience Benchmark',
          moduleTag: 'M9',
          icon: Award,
          description: 'Quantitative resilience scoring against chaos baseline datasets'
        }
      ]
    },
    {
      title: 'Audit & Governance',
      items: [
        {
          id: 'reports-center',
          label: 'Reports Center',
          moduleTag: 'M10',
          icon: FileText,
          description: 'Post-mortem export, executive summaries, and CSV data'
        }
      ]
    }
  ];

  return (
    <aside className={`enterprise-sidebar ${collapsed ? 'collapsed' : ''}`}>
      {/* Brand Section */}
      <div className="sidebar-brand-wrapper">
        <div className="sidebar-brand-left">
          <div className="sidebar-brand-icon">
            <ShieldCheck size={22} />
          </div>
          {!collapsed && (
            <div className="sidebar-brand-text">
              <span className="sidebar-brand-title">CascadeShield AI</span>
              <span className="sidebar-brand-subtitle">Cloud Resilience Twin</span>
            </div>
          )}
        </div>
        <button
          className="sidebar-collapse-btn"
          onClick={onToggleCollapse}
          title={collapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
          aria-label={collapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
        >
          {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
        </button>
      </div>

      {/* Navigation Sections */}
      <nav className="sidebar-nav-container">
        {navSections.map((section) => (
          <div key={section.title} className="sidebar-nav-group">
            {!collapsed && (
              <div className="sidebar-group-header">
                <span>{section.title}</span>
              </div>
            )}
            <div className="sidebar-group-items">
              {section.items.map((item) => {
                const IconComponent = item.icon;
                const isActive = activeModule === item.id;

                return (
                  <button
                    key={item.id}
                    className={`sidebar-nav-item ${isActive ? 'active' : ''}`}
                    onClick={() => onSelectModule(item.id)}
                    title={`${item.label} (${item.moduleTag}) - ${item.description}`}
                  >
                    <div className="nav-item-icon-wrapper">
                      <IconComponent size={18} />
                      {collapsed && item.badge && (
                        <span className="sidebar-collapsed-badge">{item.badge}</span>
                      )}
                    </div>

                    {!collapsed && (
                      <div className="nav-item-content">
                        <span className="nav-item-label">{item.label}</span>
                        <div className="nav-item-tags">
                          <span className="nav-item-module-badge">{item.moduleTag}</span>
                          {item.badge && (
                            <span className="nav-item-counter-badge">{item.badge}</span>
                          )}
                        </div>
                      </div>
                    )}
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      {/* Sidebar Footer */}
      <div className="sidebar-footer">
        {!collapsed ? (
          <div className="sidebar-status-box">
            <div className="status-indicator-row">
              <span className="pulse-dot"></span>
              <span className="status-label">Simulation Engine</span>
            </div>
            <span className="status-version">CascadeShield v10.0 Enterprise</span>
          </div>
        ) : (
          <div className="sidebar-status-collapsed" title="Simulation Engine Active (v10.0)">
            <span className="pulse-dot"></span>
          </div>
        )}
      </div>
    </aside>
  );
}
