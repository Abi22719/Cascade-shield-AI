import React, { useState, useEffect, useCallback } from 'react';
import { 
  LayoutDashboard, 
  RefreshCw, 
  Route, 
  FileText, 
  Award, 
  Search, 
  ShieldCheck,
  Zap,
  Layers
} from 'lucide-react';
import SystemSummaryCards from '../components/SystemSummaryCards';
import ExplainabilityPanel from '../components/ExplainabilityPanel';
import ActivityTimeline from '../components/ActivityTimeline';
import { dashboardApi } from '../services/dashboardApi';

export default function UnifiedDashboard({ onNavigateModule, onOpenSearch }) {
  const [summary, setSummary] = useState(null);
  const [insights, setInsights] = useState([]);
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadDashboardData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [sumRes, insRes, actRes] = await Promise.all([
        dashboardApi.getSummary().catch(e => {
          console.error("Summary load error:", e);
          return null;
        }),
        dashboardApi.getInsights(8).catch(e => {
          console.error("Insights load error:", e);
          return [];
        }),
        dashboardApi.getActivityTimeline(30).catch(e => {
          console.error("Activities load error:", e);
          return [];
        })
      ]);

      if (sumRes) setSummary(sumRes);
      if (insRes) setInsights(insRes);
      if (actRes) setActivities(actRes);
    } catch (err) {
      setError(err.message || "Failed to load unified dashboard");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDashboardData();
  }, [loadDashboardData]);

  return (
    <div className="dashboard-container">
      {/* Header */}
      <div className="db-header">
        <div className="db-title-group">
          <h2>
            <LayoutDashboard size={24} color="#38bdf8" />
            <span>Unified Executive Dashboard & AI Insights</span>
          </h2>
          <p>
            Grand Integration Hub: Live telemetry, explainable root cause reasoning, and end-to-end cloud resilience.
          </p>
        </div>

        <div className="db-header-actions">
          <button 
            className="btn-db-secondary"
            onClick={onOpenSearch}
            title="Search services, alerts, incidents, plans, and benchmarks (Ctrl+K)"
          >
            <Search size={15} />
            <span>Global Search</span>
          </button>

          <button 
            className="btn-db-secondary"
            onClick={() => onNavigateModule('reports-center')}
            title="Generate and export system reports"
          >
            <FileText size={15} />
            <span>Reports Center</span>
          </button>

          <button 
            className="btn-db-primary"
            onClick={() => onNavigateModule('incident-workflow')}
            title="Follow 10-step guided cloud failure investigation"
          >
            <Route size={15} />
            <span>Incident Workflow</span>
          </button>

          <button 
            className="btn btn-secondary"
            onClick={loadDashboardData}
            disabled={loading}
            title="Refresh dashboard state"
          >
            <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
          </button>
        </div>
      </div>

      {error && (
        <div style={{ background: 'rgba(239, 68, 68, 0.15)', border: '1px solid rgba(239, 68, 68, 0.4)', borderRadius: '8px', padding: '0.75rem 1rem', color: '#fca5a5' }}>
          <strong>Error loading dashboard: </strong> {error}
        </div>
      )}

      {/* Cross-Module KPI Summary Cards */}
      <SystemSummaryCards 
        summary={summary} 
        loading={loading} 
        onNavigateModule={onNavigateModule} 
      />

      {/* Main Two-Column Layout */}
      <div className="db-columns-layout">
        {/* Left Column: Explainable AI Insights */}
        <ExplainabilityPanel 
          insights={insights} 
          loading={loading} 
          onNavigateModule={onNavigateModule} 
        />

        {/* Right Column: Live Cross-Module Activity Stream */}
        <ActivityTimeline 
          activities={activities} 
          loading={loading} 
          onRefresh={loadDashboardData} 
        />
      </div>
    </div>
  );
}
