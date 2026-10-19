import React, { useState } from 'react';
import { History, CheckCircle2, AlertTriangle, ChevronDown, ChevronRight, Terminal } from 'lucide-react';

export default function AgentExecutionTimeline({ history = [] }) {
  const [expandedStep, setExpandedStep] = useState(null);

  const toggleExpand = (stepNum) => {
    setExpandedStep(prev => prev === stepNum ? null : stepNum);
  };

  return (
    <div className="agent-panel">
      <div className="panel-title">
        <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <History size={16} color="#38bdf8" />
          <span>Diagnostic Execution Timeline</span>
        </span>
        <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
          {history.length} action{history.length === 1 ? '' : 's'} recorded
        </span>
      </div>

      {history.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '2rem', color: '#64748b', fontSize: '0.85rem' }}>
          No diagnostic actions executed yet. Click <strong>"Execute 1 Step"</strong> or <strong>"Run Adaptive Loop"</strong> to begin.
        </div>
      ) : (
        <div className="timeline-stream">
          {history.map((step, idx) => {
            const isExpanded = expandedStep === step.step_number;
            const isSuccess = step.execution_status === 'SUCCESS';

            return (
              <div key={step.step_number} className="timeline-step">
                <div className="step-marker">
                  <div className="step-circle" style={{ background: isSuccess ? '#0284c7' : '#ef4444' }}>
                    {step.step_number}
                  </div>
                  {idx < history.length - 1 && <div className="step-line" />}
                </div>

                <div className="step-content">
                  <div className="step-header">
                    <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span style={{ fontWeight: 600, color: '#f8fafc' }}>{step.action_name}</span>
                      <span 
                        className={`badge ${isSuccess ? 'badge-success' : 'badge-critical'}`}
                        style={{ fontSize: '0.65rem', padding: '1px 6px' }}
                      >
                        {step.execution_status}
                      </span>
                    </span>
                    <span className="step-duration">{step.duration_ms?.toFixed(1)} ms</span>
                  </div>

                  <div className="step-summary">
                    {step.result_summary}
                  </div>

                  {step.raw_result && Object.keys(step.raw_result).length > 0 && (
                    <div style={{ marginTop: '0.3rem' }}>
                      <button 
                        onClick={() => toggleExpand(step.step_number)}
                        style={{ 
                          background: 'none', 
                          border: 'none', 
                          color: '#38bdf8', 
                          fontSize: '0.72rem', 
                          cursor: 'pointer', 
                          display: 'flex', 
                          alignItems: 'center', 
                          gap: '4px',
                          padding: 0 
                        }}
                      >
                        {isExpanded ? <ChevronDown size={13} /> : <ChevronRight size={13} />}
                        <span>{isExpanded ? 'Hide Raw Telemetry' : 'Inspect Raw Output'}</span>
                      </button>

                      {isExpanded && (
                        <pre 
                          style={{ 
                            background: '#090d16', 
                            border: '1px solid #1e293b', 
                            borderRadius: '6px', 
                            padding: '0.6rem', 
                            fontSize: '0.7rem', 
                            color: '#94a3b8', 
                            overflowX: 'auto',
                            marginTop: '0.4rem',
                            maxHeight: '160px'
                          }}
                        >
                          {JSON.stringify(step.raw_result, null, 2)}
                        </pre>
                      )}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
