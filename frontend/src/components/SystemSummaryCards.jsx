import React from 'react';
import { 
  Server, 
  CheckCircle2, 
  AlertTriangle, 
  XCircle, 
  BellRing, 
  GitBranch, 
  Search, 
  LifeBuoy, 
  Award, 
  ShieldCheck 
} from 'lucide-react';

export default function SystemSummaryCards({ summary, loading, onNavigateModule }) {
  if (loading && !summary) {
    return (
      <div className="db-summary-grid">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="db-stat-card animate-pulse" style={{ height: '110px' }} />
        ))}
      </div>
    );
  }

  const s = summary || {
    total_services: 9,
    healthy_services: 7,
    degraded_services: 1,
    unavailable_services: 1,
    active_anomalies: 2,
    high_risk_predictions: 1,
    open_incidents: 1,
    recovery_plans_pending: 1,
    latest_benchmark_score: 87.5,
    simulation_mode: true
  };

  const cards = [
    {
      id: 'services',
      title: 'Digital Twin Services',
      value: `${s.healthy_services}/${s.total_services}`,
      subtext: `${s.degraded_services} degraded, ${s.unavailable_services} unavailable`,
      icon: Server,
      color: '#38bdf8',
      module: 'digital-twin'
    },
    {
      id: 'anomalies',
      title: 'Active Anomalies',
      value: s.active_anomalies,
      subtext: s.active_anomalies > 0 ? 'Threshold & ML breaches' : 'Telemetry normal',
      icon: BellRing,
      color: s.active_anomalies > 0 ? '#f59e0b' : '#10b981',
      module: 'anomaly-detection'
    },
    {
      id: 'cascade',
      title: 'High-Risk Cascades',
      value: s.high_risk_predictions,
      subtext: 'Blast radius evaluated',
      icon: GitBranch,
      color: '#ec4899',
      module: 'cascade-prediction'
    },
    {
      id: 'rca',
      title: 'RCA Incidents',
      value: s.open_incidents,
      subtext: 'Root cause suspects ranked',
      icon: Search,
      color: '#a855f7',
      module: 'root-cause-analysis'
    },
    {
      id: 'recovery',
      title: 'Recovery Plans Pending',
      value: s.recovery_plans_pending,
      subtext: 'Ready for validation',
      icon: LifeBuoy,
      color: '#06b6d4',
      module: 'recovery-planning'
    },
    {
      id: 'benchmark',
      title: 'Resilience Benchmark',
      value: s.latest_benchmark_score ? `${s.latest_benchmark_score.toFixed(1)}/100` : 'N/A',
      subtext: 'Evaluation score (Module 9)',
      icon: Award,
      color: '#10b981',
      module: 'resilience-benchmark'
    }
  ];

  return (
    <div className="db-summary-grid">
      {cards.map(c => {
        const IconComponent = c.icon;
        return (
          <div 
            key={c.id} 
            className="db-stat-card"
            style={{ cursor: onNavigateModule ? 'pointer' : 'default' }}
            onClick={() => onNavigateModule && onNavigateModule(c.module)}
            title={`Navigate to ${c.title}`}
          >
            <div className="stat-card-header">
              <span>{c.title}</span>
              <div className="stat-card-icon" style={{ color: c.color }}>
                <IconComponent size={18} />
              </div>
            </div>
            <div className="stat-card-value">{c.value}</div>
            <div className="stat-card-subtext">{c.subtext}</div>
          </div>
        );
      })}
    </div>
  );
}
