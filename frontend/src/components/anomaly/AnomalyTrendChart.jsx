import React, { useState } from 'react';
import { 
  ResponsiveContainer, 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ReferenceLine 
} from 'recharts';
import { Activity, Clock, ShieldAlert } from 'lucide-react';

export default function AnomalyTrendChart({
  metricsData = [],
  services = [],
  selectedServiceId,
  onSelectService,
  thresholds
}) {
  const [activeMetric, setActiveMetric] = useState('latency_ms'); // 'latency_ms', 'error_rate', 'cpu_usage', 'memory_usage'

  // Metric configuration
  const metricConfigs = {
    latency_ms: {
      label: 'Response Latency',
      unit: 'ms',
      color: '#38bdf8',
      warningRef: thresholds?.latency_warning || 500,
      criticalRef: thresholds?.latency_critical || 1000,
      minY: 0,
      maxY: (dataMax) => Math.max(dataMax * 1.15, (thresholds?.latency_critical || 1000) * 1.2)
    },
    error_rate: {
      label: 'Error Rate',
      unit: '%',
      color: '#f87171',
      warningRef: thresholds?.error_rate_warning || 5.0,
      criticalRef: thresholds?.error_rate_critical || 10.0,
      minY: 0,
      maxY: (dataMax) => Math.max(dataMax * 1.2, 12)
    },
    cpu_usage: {
      label: 'CPU Utilization',
      unit: '%',
      color: '#a855f7',
      warningRef: thresholds?.cpu_warning || 75.0,
      criticalRef: thresholds?.cpu_critical || 90.0,
      minY: 0,
      maxY: 100
    },
    memory_usage: {
      label: 'Memory Utilization',
      unit: '%',
      color: '#10b981',
      warningRef: thresholds?.memory_warning || 80.0,
      criticalRef: thresholds?.memory_critical || 95.0,
      minY: 0,
      maxY: 100
    }
  };

  const currentCfg = metricConfigs[activeMetric];

  // Format data for Recharts
  const chartPoints = metricsData.map((pt, idx) => {
    const timeStr = new Date(pt.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    const val = pt[activeMetric];
    const isAboveWarn = val >= currentCfg.warningRef;
    const isAboveCrit = val >= currentCfg.criticalRef;

    return {
      index: idx,
      time: timeStr,
      value: val,
      isAboveWarn,
      isAboveCrit,
      raw: pt
    };
  });

  return (
    <div className="chart-section-card">
      <div className="chart-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Activity size={18} color="#0ea5e9" />
            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#f8fafc' }}>
              Service Telemetry & Threshold Analysis
            </h3>
          </div>

          {/* Service Selector Dropdown */}
          <div className="service-selector-label">
            <span>Service:</span>
            <select
              className="filter-select"
              value={selectedServiceId}
              onChange={(e) => onSelectService(e.target.value)}
            >
              {services.map(s => (
                <option key={s.id} value={s.id}>
                  {s.name} ({s.id})
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Metric Selector Tabs */}
        <div className="metric-tabs">
          <button
            className={`metric-tab-btn ${activeMetric === 'latency_ms' ? 'active' : ''}`}
            onClick={() => setActiveMetric('latency_ms')}
          >
            Latency (ms)
          </button>
          <button
            className={`metric-tab-btn ${activeMetric === 'error_rate' ? 'active' : ''}`}
            onClick={() => setActiveMetric('error_rate')}
          >
            Error Rate (%)
          </button>
          <button
            className={`metric-tab-btn ${activeMetric === 'cpu_usage' ? 'active' : ''}`}
            onClick={() => setActiveMetric('cpu_usage')}
          >
            CPU (%)
          </button>
          <button
            className={`metric-tab-btn ${activeMetric === 'memory_usage' ? 'active' : ''}`}
            onClick={() => setActiveMetric('memory_usage')}
          >
            Memory (%)
          </button>
        </div>
      </div>

      {/* Chart Area */}
      <div className="chart-wrapper">
        {chartPoints.length > 0 ? (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartPoints} margin={{ top: 10, right: 25, left: -10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis 
                dataKey="time" 
                stroke="#64748b" 
                fontSize={11} 
                tickLine={false}
              />
              <YAxis 
                stroke="#64748b" 
                fontSize={11} 
                domain={[currentCfg.minY, currentCfg.maxY]}
                tickFormatter={(v) => `${v}${currentCfg.unit === '%' ? '%' : ''}`}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#0f172a',
                  borderColor: '#334155',
                  borderRadius: '8px',
                  boxShadow: '0 4px 12px rgba(0,0,0,0.5)',
                  fontSize: '12px'
                }}
                formatter={(val) => [`${val} ${currentCfg.unit}`, currentCfg.label]}
                labelFormatter={(label) => `Timestamp: ${label}`}
              />
              
              {/* Warning Threshold Reference Line */}
              <ReferenceLine 
                y={currentCfg.warningRef} 
                stroke="#f59e0b" 
                strokeDasharray="4 4" 
                strokeWidth={1.5}
                label={{ 
                  value: `Warning (${currentCfg.warningRef}${currentCfg.unit})`, 
                  fill: '#f59e0b', 
                  position: 'top',
                  fontSize: 10 
                }} 
              />

              {/* Critical Threshold Reference Line */}
              <ReferenceLine 
                y={currentCfg.criticalRef} 
                stroke="#ef4444" 
                strokeDasharray="4 4" 
                strokeWidth={1.5}
                label={{ 
                  value: `Critical (${currentCfg.criticalRef}${currentCfg.unit})`, 
                  fill: '#ef4444', 
                  position: 'top',
                  fontSize: 10 
                }} 
              />

              {/* Telemetry Metric Curve */}
              <Line
                type="monotone"
                dataKey="value"
                stroke={currentCfg.color}
                strokeWidth={2.5}
                dot={{ r: 2.5, fill: currentCfg.color }}
                activeDot={{ r: 6, stroke: '#fff', strokeWidth: 2 }}
                animationDuration={600}
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-dim)' }}>
            No telemetry stream points available.
          </div>
        )}
      </div>

      {/* Chart Footer Legend */}
      <div className="chart-legend-row">
        <div className="legend-line-item">
          <span className="legend-dot-ref" style={{ backgroundColor: currentCfg.color }}></span>
          <span>Observed Telemetry</span>
        </div>
        <div className="legend-line-item">
          <span className="legend-dot-ref" style={{ backgroundColor: '#f59e0b', borderTop: '2px dashed #f59e0b' }}></span>
          <span>Warning Threshold</span>
        </div>
        <div className="legend-line-item">
          <span className="legend-dot-ref" style={{ backgroundColor: '#ef4444', borderTop: '2px dashed #ef4444' }}></span>
          <span>Critical Threshold</span>
        </div>
      </div>
    </div>
  );
}
