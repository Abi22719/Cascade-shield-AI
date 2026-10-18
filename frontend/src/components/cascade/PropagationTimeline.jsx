import React, { useState, useEffect } from 'react';
import { Play, Pause, SkipForward, RotateCcw, Clock, ShieldAlert } from 'lucide-react';

export default function PropagationTimeline({
  timeline = [],
  activeStep,
  setActiveStep
}) {
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    let timer = null;
    if (isPlaying && timeline.length > 0) {
      timer = setInterval(() => {
        setActiveStep(prev => {
          if (prev >= timeline.length - 1) {
            setIsPlaying(false);
            return prev;
          }
          return prev + 1;
        });
      }, 1800);
    }
    return () => clearInterval(timer);
  }, [isPlaying, timeline, setActiveStep]);

  if (!timeline || timeline.length === 0) {
    return null;
  }

  const handleStepForward = () => {
    if (activeStep < timeline.length - 1) {
      setActiveStep(activeStep + 1);
    }
  };

  const handleReset = () => {
    setIsPlaying(false);
    setActiveStep(0);
  };

  const togglePlay = () => {
    if (activeStep >= timeline.length - 1) {
      setActiveStep(0);
    }
    setIsPlaying(!isPlaying);
  };

  return (
    <div className="simulation-timeline-panel">
      <div className="timeline-header">
        <h3>
          <Clock size={16} color="#3b82f6" />
          Discrete Time-Step Failure Wave Simulation
        </h3>

        <div className="timeline-controls">
          <button
            type="button"
            className={`timeline-btn ${isPlaying ? 'active' : ''}`}
            onClick={togglePlay}
          >
            {isPlaying ? <Pause size={14} /> : <Play size={14} />}
            {isPlaying ? 'Pause' : 'Play Timeline'}
          </button>

          <button
            type="button"
            className="timeline-btn"
            onClick={handleStepForward}
            disabled={activeStep >= timeline.length - 1}
          >
            <SkipForward size={14} />
            Next Wave
          </button>

          <button
            type="button"
            className="timeline-btn"
            onClick={handleReset}
            title="Reset to Inception (Step 0)"
          >
            <RotateCcw size={14} />
            Reset
          </button>
        </div>
      </div>

      <div className="steps-track">
        {timeline.map((item) => {
          const isCurrent = activeStep === item.step;
          const isReached = activeStep >= item.step;

          return (
            <div
              key={item.step}
              className={`step-card ${isCurrent ? 'active' : ''} ${isReached ? 'reached' : ''}`}
              onClick={() => {
                setIsPlaying(false);
                setActiveStep(item.step);
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span className="step-card-num">Wave {item.step}</span>
                <span className="step-card-offset">+{item.timestamp_offset_seconds}s</span>
              </div>

              <div className="step-card-affected">
                {item.newly_affected_services?.length > 0
                  ? item.newly_affected_services.join(', ')
                  : 'Wave Stabilized'}
              </div>

              <div className="step-card-desc">
                {item.step_description}
              </div>

              <div style={{ marginTop: '8px', display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                <span>Total Impacted: <b>{item.cumulative_affected_count}</b></span>
                <span>Avg Risk: <b style={{ color: item.average_risk_score >= 70 ? '#ef4444' : '#f97316' }}>{item.average_risk_score}</b></span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
