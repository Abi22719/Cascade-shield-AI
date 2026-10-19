import React, { useState } from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend
} from 'recharts';
import { Activity } from 'lucide-react';

export default function MetricEvolutionChart({
  timelineSteps = [],
  services = [],
  selectedServiceId,
  onSelectService
}) {
  const [metricKey, setMetricKey] = useState('latency_ms'); // latency_ms, error_rate, cpu_usage, risk_score

  if (!timelineSteps || timelineSteps.length === 0) {
    return (
      <div style={{ textAlign: 'center', color: '#64748b', padding: '2rem', fontSize: '0.85rem' }}>
        No metric timeline data available. Execute a simulation run to view metric progression.
      </div>
    );
  }

  // Build chart dataset per step
  const serviceIds = services.map(s => s.id || s.service_id);
  const chartData = timelineSteps.map(step => {
    const row = { step: `Step ${step.step_number}` };
    const stepServices = step.services || {};

    Object.keys(stepServices).forEach(sid => {
      const s = stepServices[sid];
      row[sid] = s ? s[metricKey] : null;
    });

    return row;
  });

  const metricLabels = {
    latency_ms: { label: 'Latency', unit: 'ms', color: '#38bdf8' },
    error_rate: { label: 'Error Rate', unit: '%', color: '#f87171' },
    cpu_usage: { label: 'CPU Usage', unit: '%', color: '#fbbf24' },
    risk_score: { label: 'Risk Score', unit: '/100', color: '#a855f7' }
  };

  const colors = [
    '#38bdf8', '#f87171', '#fbbf24', '#34d399', '#a855f7', 
    '#ec4899', '#f97316', '#06b6d4', '#6366f1', '#eab308'
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', width: '100%', height: '100%' }}>
      {/* Metric & Service Filter Bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
        <div style={{ display: 'flex', gap: '0.35rem' }}>
          {Object.entries(metricLabels).map(([key, cfg]) => (
            <button
              key={key}
              className={`btn-sim-secondary ${metricKey === key ? 'active' : ''}`}
              style={{
                fontSize: '0.75rem',
                padding: '0.25rem 0.55rem',
                backgroundColor: metricKey === key ? 'rgba(139, 92, 246, 0.25)' : undefined,
                borderColor: metricKey === key ? '#8b5cf6' : undefined,
                color: metricKey === key ? '#c4b5fd' : undefined
              }}
              onClick={() => setMetricKey(key)}
            >
              {cfg.label} ({cfg.unit})
            </button>
          ))}
        </div>

        {/* Focus Service Selector */}
        <select
          value={selectedServiceId || ''}
          onChange={(e) => onSelectService && onSelectService(e.target.value || null)}
          className="sim-form-select"
          style={{ padding: '0.2rem 0.5rem', fontSize: '0.75rem', maxWidth: '180px' }}
        >
          <option value="">All Services</option>
          {services.map(s => (
            <option key={s.id || s.service_id} value={s.id || s.service_id}>
              {s.name || s.service_name || s.id}
            </option>
          ))}
        </select>
      </div>

      {/* Chart Canvas */}
      <div style={{ width: '100%', height: 280 }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.06)" />
            <XAxis dataKey="step" stroke="#64748b" fontSize={11} tickLine={false} />
            <YAxis stroke="#64748b" fontSize={11} tickLine={false} unit={` ${metricLabels[metricKey].unit}`} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#0f172a',
                border: '1px solid rgba(255,255,255,0.12)',
                borderRadius: '6px',
                fontSize: '12px'
              }}
            />
            <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '6px' }} />

            {/* If a service is selected, highlight only that service */}
            {selectedServiceId ? (
              <Line
                type="monotone"
                dataKey={selectedServiceId}
                name={selectedServiceId}
                stroke={metricLabels[metricKey].color}
                strokeWidth={3}
                dot={{ r: 4 }}
                activeDot={{ r: 6 }}
              />
            ) : (
              // Otherwise show top services
              serviceIds.slice(0, 7).map((sid, idx) => (
                <Line
                  key={sid}
                  type="monotone"
                  dataKey={sid}
                  name={sid}
                  stroke={colors[idx % colors.length]}
                  strokeWidth={1.75}
                  dot={{ r: 2 }}
                />
              ))
            )}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
