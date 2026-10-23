import React, { useState, useEffect, useRef } from 'react';
import {
  Bot,
  Send,
  Sparkles,
  RefreshCw,
  Trash2,
  Copy,
  Check,
  AlertCircle,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  ShieldCheck,
  ShieldAlert,
  Server,
  Layers,
  HelpCircle,
  Clock,
  ArrowRight,
  Database,
  Search
} from 'lucide-react';
import { copilotApi } from '../services/copilotApi';
import { incidentsApi } from '../services/incidentsApi';
import { api } from '../services/api';
import StatusBadge from '../components/common/StatusBadge';
import Tooltip from '../components/common/Tooltip';

export default function AIResilienceCopilotPortal({ onNavigateModule, onAddToast }) {
  const [messages, setMessages] = useState([
    {
      id: 'welcome-msg',
      sender: 'assistant',
      text: "Hello! I am your **CascadeShield Resilience Copilot**. I analyze real telemetry, Bayesian root causes, cascading failure models, and automated sandbox verifications. How can I assist your investigation today?",
      confidence: 0.98,
      evidence_citations: [
        { evidence_id: 'EV-INIT-01', evidence_summary: 'Digital twin active with 12 microservices and live telemetry telemetry streams.', confidence_score: 0.99, data_source: 'SYSTEM_TOPOLOGY' }
      ],
      related_services: ['payment-service', 'auth-service', 'order-service'],
      related_incidents: ['inc-payment-cascade-01'],
      reasoning_chain: ['Queried digital twin state', 'Loaded active incident contexts', 'Ready for resilience queries'],
      limitation_note: 'Grounded exclusively on current digital twin metrics, verified recovery sandboxes, and incident records.',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);

  const [inputQuery, setInputQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [incidents, setIncidents] = useState([]);
  const [services, setServices] = useState([]);
  const [selectedIncidentId, setSelectedIncidentId] = useState('inc-payment-cascade-01');
  const [selectedServiceId, setSelectedServiceId] = useState('');
  const [expandedReasoning, setExpandedReasoning] = useState({});
  const [copiedId, setCopiedId] = useState(null);

  const messagesEndRef = useRef(null);

  // Suggested Prompts
  const suggestedPrompts = [
    {
      label: 'Blast Radius of Payment Service',
      query: 'What happens if the payment service fails? Which downstream services are affected?'
    },
    {
      label: 'Auth Service Dependencies',
      query: 'Which services depend on the authentication service and what is their criticality?'
    },
    {
      label: 'Evidence for Root Cause Candidate',
      query: 'What evidence supports the current root-cause candidate for incident inc-payment-cascade-01?'
    },
    {
      label: 'Compare Recovery Plans',
      query: 'Compare the available recovery plans. Which plan has the lowest estimated blast radius risk?'
    },
    {
      label: 'Sandbox Verification Status',
      query: 'Did the simulated recovery pass automated 5-pillar verification?'
    },
    {
      label: 'Explain Degradation Signals',
      query: 'Why was the payment-service marked as degraded? Explain the underlying metric thresholds.'
    }
  ];

  // Load contextual incidents and services
  useEffect(() => {
    async function loadContext() {
      try {
        const [incList, srvList] = await Promise.all([
          incidentsApi.listIncidents().catch(() => []),
          api.getServices().catch(() => [])
        ]);
        setIncidents(incList || []);
        setServices(srvList || []);
        if (incList && incList.length > 0 && !selectedIncidentId) {
          setSelectedIncidentId(incList[0].id);
        }
      } catch (err) {
        console.warn('Failed to load copilot context:', err);
      }
    }
    loadContext();
  }, []);

  // Auto-scroll to bottom of conversation
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSendMessage = async (queryToSend = null) => {
    const query = (queryToSend || inputQuery).trim();
    if (!query || loading) return;

    const userMessage = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMessage]);
    if (!queryToSend) setInputQuery('');
    setLoading(true);

    try {
      const response = await copilotApi.sendMessage(query, {
        incident_id: selectedIncidentId,
        service_id: selectedServiceId || undefined
      });

      const assistantMessage = {
        id: `assistant-${Date.now()}`,
        sender: 'assistant',
        text: response.answer || "I've analyzed the available telemetry, but no conclusive evidence was found for this query.",
        confidence: response.confidence || 0.85,
        evidence_citations: response.evidence_citations || [],
        related_services: response.related_services || [],
        related_incidents: response.related_incidents || [],
        reasoning_chain: response.reasoning_chain || [],
        limitation_note: response.limitation_note || 'Predictions are bounded by current simulation parameters and model fidelity.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      console.error('Error invoking copilot:', err);
      const errorMessage = {
        id: `err-${Date.now()}`,
        sender: 'assistant',
        isError: true,
        text: `Error contacting resilience copilot engine: ${err.message || 'Service unavailable'}. Please verify backend API status.`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, errorMessage]);
      if (onAddToast) onAddToast(err.message || 'Failed to query copilot', 'error', 'Copilot Error');
    } finally {
      setLoading(false);
    }
  };

  const handleClearChat = () => {
    setMessages([
      {
        id: `welcome-${Date.now()}`,
        sender: 'assistant',
        text: "Conversation cleared. Grounded in the digital twin graph and incident records. Ask any question to start.",
        confidence: 1.0,
        evidence_citations: [],
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
    ]);
  };

  const handleCopyText = (text, id) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const toggleReasoning = (msgId) => {
    setExpandedReasoning(prev => ({ ...prev, [msgId]: !prev[msgId] }));
  };

  return (
    <div className="portal-container animate-fade-in" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', height: 'calc(100vh - 72px)', boxSizing: 'border-box' }}>
      {/* Top Banner */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', flexShrink: 0 }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <div style={{ background: 'rgba(99, 102, 241, 0.15)', padding: '0.4rem', borderRadius: '8px', color: '#818cf8' }}>
              <Bot size={22} />
            </div>
            <h1 style={{ fontSize: '1.4rem', fontWeight: 700, margin: 0, color: 'var(--text-primary, #f8fafc)' }}>
              AI Resilience Copilot Portal
            </h1>
            <span style={{ fontSize: '0.72rem', background: '#3b82f622', color: '#60a5fa', padding: '0.15rem 0.5rem', borderRadius: '4px', border: '1px solid #3b82f644' }}>
              PORTAL 3
            </span>
            <span style={{ fontSize: '0.72rem', background: '#10b98122', color: '#34d399', padding: '0.15rem 0.5rem', borderRadius: '4px', border: '1px solid #10b98144' }}>
              EVIDENCE-GROUNDED
            </span>
          </div>
          <p style={{ margin: '0.25rem 0 0', fontSize: '0.85rem', color: 'var(--text-secondary, #94a3b8)' }}>
            Interactive AI assistant with verifiable causal lineage, Bayesian root-cause reasoning, and blast-radius estimations.
          </p>
        </div>

        {/* Action Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          {/* Incident Selector */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', background: 'var(--card-bg, #0f172a)', padding: '0.35rem 0.6rem', borderRadius: '6px', border: '1px solid var(--border-color, #1e293b)' }}>
            <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Context Incident:</span>
            <select
              value={selectedIncidentId}
              onChange={(e) => setSelectedIncidentId(e.target.value)}
              style={{ background: 'transparent', border: 'none', color: '#f8fafc', fontSize: '0.78rem', outline: 'none', cursor: 'pointer' }}
            >
              {incidents.length === 0 && <option value="inc-payment-cascade-01">inc-payment-cascade-01</option>}
              {incidents.map(inc => (
                <option key={inc.id} value={inc.id} style={{ background: '#0f172a', color: '#f8fafc' }}>
                  {inc.id} ({inc.title?.substring(0, 24)}...)
                </option>
              ))}
            </select>
          </div>

          {/* Service Selector */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', background: 'var(--card-bg, #0f172a)', padding: '0.35rem 0.6rem', borderRadius: '6px', border: '1px solid var(--border-color, #1e293b)' }}>
            <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Service:</span>
            <select
              value={selectedServiceId}
              onChange={(e) => setSelectedServiceId(e.target.value)}
              style={{ background: 'transparent', border: 'none', color: '#f8fafc', fontSize: '0.78rem', outline: 'none', cursor: 'pointer' }}
            >
              <option value="" style={{ background: '#0f172a' }}>All Services</option>
              {services.map(s => (
                <option key={s.id} value={s.id} style={{ background: '#0f172a', color: '#f8fafc' }}>
                  {s.name}
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={handleClearChat}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              padding: '0.45rem 0.75rem',
              borderRadius: '6px',
              border: '1px solid var(--border-color, #1e293b)',
              background: 'transparent',
              color: '#94a3b8',
              cursor: 'pointer',
              fontSize: '0.8rem'
            }}
            title="Clear Chat History"
          >
            <Trash2 size={14} />
            <span>Clear</span>
          </button>
        </div>
      </div>

      {/* Main Chat Workspace */}
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        flex: 1,
        background: 'var(--card-bg, #0b1120)',
        borderRadius: '10px',
        border: '1px solid var(--border-color, #1e293b)',
        overflow: 'hidden'
      }}>
        {/* Messages Stream */}
        <div style={{
          flex: 1,
          overflowY: 'auto',
          padding: '1.25rem',
          display: 'flex',
          flexDirection: 'column',
          gap: '1.25rem'
        }}>
          {messages.map((msg) => (
            <div
              key={msg.id}
              style={{
                display: 'flex',
                gap: '0.85rem',
                alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
                maxWidth: msg.sender === 'user' ? '70%' : '88%'
              }}
            >
              {/* Avatar */}
              {msg.sender === 'assistant' && (
                <div style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '50%',
                  background: msg.isError ? '#ef444422' : 'linear-gradient(135deg, #4f46e5, #06b6d4)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#fff',
                  flexShrink: 0,
                  marginTop: '2px',
                  border: msg.isError ? '1px solid #ef4444' : '1px solid rgba(255,255,255,0.2)'
                }}>
                  {msg.isError ? <AlertCircle size={16} /> : <Bot size={16} />}
                </div>
              )}

              {/* Message Bubble */}
              <div style={{
                background: msg.sender === 'user'
                  ? 'linear-gradient(135deg, #1d4ed8, #2563eb)'
                  : (msg.isError ? 'rgba(239, 68, 68, 0.08)' : 'rgba(30, 41, 59, 0.7)'),
                color: '#f8fafc',
                padding: '1rem 1.15rem',
                borderRadius: msg.sender === 'user' ? '12px 12px 2px 12px' : '12px 12px 12px 2px',
                border: msg.sender === 'user'
                  ? '1px solid #3b82f6'
                  : (msg.isError ? '1px solid #ef444455' : '1px solid rgba(255, 255, 255, 0.08)'),
                boxShadow: '0 4px 14px rgba(0,0,0,0.15)',
                position: 'relative'
              }}>
                {/* Header row for assistant */}
                {msg.sender === 'assistant' && (
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.6rem', borderBottom: '1px solid rgba(255,255,255,0.06)', paddingBottom: '0.4rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span style={{ fontSize: '0.78rem', fontWeight: 600, color: '#93c5fd' }}>
                        CascadeShield Copilot
                      </span>
                      {msg.confidence !== undefined && (
                        <span style={{
                          fontSize: '0.7rem',
                          padding: '0.1rem 0.4rem',
                          borderRadius: '4px',
                          background: msg.confidence >= 0.85 ? 'rgba(16, 185, 129, 0.15)' : 'rgba(245, 158, 11, 0.15)',
                          color: msg.confidence >= 0.85 ? '#34d399' : '#fbbf24',
                          border: `1px solid ${msg.confidence >= 0.85 ? '#10b98144' : '#f59e0b44'}`
                        }}>
                          {(msg.confidence * 100).toFixed(0)}% Confidence
                        </span>
                      )}
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span style={{ fontSize: '0.7rem', color: '#64748b' }}>{msg.timestamp}</span>
                      <button
                        onClick={() => handleCopyText(msg.text, msg.id)}
                        style={{ background: 'transparent', border: 'none', color: '#94a3b8', cursor: 'pointer', padding: '2px' }}
                        title="Copy to clipboard"
                      >
                        {copiedId === msg.id ? <Check size={13} color="#10b981" /> : <Copy size={13} />}
                      </button>
                    </div>
                  </div>
                )}

                {/* Message Body */}
                <div style={{
                  fontSize: '0.9rem',
                  lineHeight: '1.55',
                  whiteSpace: 'pre-line',
                  color: msg.sender === 'user' ? '#ffffff' : '#e2e8f0'
                }}>
                  {msg.text}
                </div>

                {/* Structured Evidence References */}
                {msg.evidence_citations && msg.evidence_citations.length > 0 && (
                  <div style={{ marginTop: '0.85rem', paddingTop: '0.75rem', borderTop: '1px solid rgba(255,255,255,0.06)' }}>
                    <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#38bdf8', marginBottom: '0.4rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                      <Database size={13} />
                      <span>Causal Evidence References ({msg.evidence_citations.length}):</span>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
                      {msg.evidence_citations.map((ev, idx) => (
                        <div key={idx} style={{
                          fontSize: '0.75rem',
                          background: 'rgba(15, 23, 42, 0.6)',
                          padding: '0.4rem 0.6rem',
                          borderRadius: '4px',
                          borderLeft: '3px solid #38bdf8',
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center'
                        }}>
                          <span style={{ color: '#cbd5e1' }}>
                            <strong style={{ color: '#38bdf8' }}>[{ev.evidence_id || `EV-${idx + 1}`}]</strong> {ev.evidence_summary || ev.description}
                          </span>
                          <span style={{ color: '#64748b', fontSize: '0.68rem', marginLeft: '0.5rem', whiteSpace: 'nowrap' }}>
                            {ev.data_source || 'METRIC_TELEMETRY'}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Related Services & Incidents Chips */}
                {((msg.related_services && msg.related_services.length > 0) || (msg.related_incidents && msg.related_incidents.length > 0)) && (
                  <div style={{ marginTop: '0.75rem', display: 'flex', flexWrap: 'wrap', gap: '0.4rem', alignItems: 'center' }}>
                    {msg.related_services?.map(srv => (
                      <button
                        key={srv}
                        onClick={() => onNavigateModule && onNavigateModule('digital-twin')}
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '0.25rem',
                          fontSize: '0.72rem',
                          background: 'rgba(56, 189, 248, 0.1)',
                          color: '#38bdf8',
                          border: '1px solid rgba(56, 189, 248, 0.25)',
                          padding: '0.2rem 0.5rem',
                          borderRadius: '4px',
                          cursor: 'pointer'
                        }}
                        title={`Inspect ${srv} in Digital Twin`}
                      >
                        <Server size={11} />
                        <span>{srv}</span>
                      </button>
                    ))}

                    {msg.related_incidents?.map(inc => (
                      <button
                        key={inc}
                        onClick={() => onNavigateModule && onNavigateModule('portal-incident')}
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '0.25rem',
                          fontSize: '0.72rem',
                          background: 'rgba(239, 68, 68, 0.1)',
                          color: '#f87171',
                          border: '1px solid rgba(239, 68, 68, 0.25)',
                          padding: '0.2rem 0.5rem',
                          borderRadius: '4px',
                          cursor: 'pointer'
                        }}
                        title={`Open ${inc} in Incident Response Portal`}
                      >
                        <ShieldAlert size={11} />
                        <span>{inc}</span>
                      </button>
                    ))}
                  </div>
                )}

                {/* Reasoning Chain Accordion */}
                {msg.reasoning_chain && msg.reasoning_chain.length > 0 && (
                  <div style={{ marginTop: '0.65rem' }}>
                    <button
                      onClick={() => toggleReasoning(msg.id)}
                      style={{
                        background: 'transparent',
                        border: 'none',
                        color: '#94a3b8',
                        fontSize: '0.72rem',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.3rem',
                        padding: 0
                      }}
                    >
                      {expandedReasoning[msg.id] ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
                      <span>{expandedReasoning[msg.id] ? 'Hide' : 'Show'} Diagnostic Reasoning Chain ({msg.reasoning_chain.length} steps)</span>
                    </button>

                    {expandedReasoning[msg.id] && (
                      <div style={{
                        marginTop: '0.4rem',
                        background: 'rgba(15, 23, 42, 0.5)',
                        padding: '0.5rem 0.75rem',
                        borderRadius: '6px',
                        border: '1px solid rgba(255,255,255,0.05)',
                        fontSize: '0.74rem',
                        color: '#94a3b8'
                      }}>
                        <ol style={{ margin: 0, paddingLeft: '1.2rem' }}>
                          {msg.reasoning_chain.map((step, idx) => (
                            <li key={idx} style={{ marginBottom: '0.2rem' }}>{step}</li>
                          ))}
                        </ol>
                      </div>
                    )}
                  </div>
                )}

                {/* Model limitation note */}
                {msg.limitation_note && (
                  <div style={{ marginTop: '0.5rem', fontSize: '0.68rem', color: '#64748b', fontStyle: 'italic' }}>
                    Note: {msg.limitation_note}
                  </div>
                )}
              </div>

              {/* User Avatar */}
              {msg.sender === 'user' && (
                <div style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '50%',
                  background: '#1e293b',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#93c5fd',
                  flexShrink: 0,
                  marginTop: '2px',
                  border: '1px solid #3b82f644'
                }}>
                  <span style={{ fontSize: '0.75rem', fontWeight: 700 }}>YOU</span>
                </div>
              )}
            </div>
          ))}

          {/* Thinking / Loading Indicator */}
          {loading && (
            <div style={{ display: 'flex', gap: '0.85rem', alignSelf: 'flex-start' }}>
              <div style={{
                width: '32px',
                height: '32px',
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #4f46e5, #06b6d4)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#fff',
                animation: 'pulse 1.5s infinite'
              }}>
                <Sparkles size={16} />
              </div>
              <div style={{
                background: 'rgba(30, 41, 59, 0.7)',
                padding: '0.85rem 1.15rem',
                borderRadius: '12px 12px 12px 2px',
                border: '1px solid rgba(255, 255, 255, 0.08)',
                display: 'flex',
                alignItems: 'center',
                gap: '0.6rem'
              }}>
                <RefreshCw size={14} className="spin-icon" style={{ color: '#38bdf8' }} />
                <span style={{ fontSize: '0.85rem', color: '#94a3b8' }}>
                  Evaluating Bayesian candidate graph and blast radius models...
                </span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Suggested Prompts Shelf */}
        <div style={{
          padding: '0.6rem 1.25rem',
          background: 'rgba(15, 23, 42, 0.85)',
          borderTop: '1px solid var(--border-color, #1e293b)',
          display: 'flex',
          gap: '0.5rem',
          overflowX: 'auto',
          whiteSpace: 'nowrap',
          alignItems: 'center'
        }}>
          <span style={{ fontSize: '0.72rem', color: '#64748b', display: 'flex', alignItems: 'center', gap: '0.2rem', flexShrink: 0 }}>
            <Sparkles size={12} color="#818cf8" /> Suggested queries:
          </span>
          {suggestedPrompts.map((p, idx) => (
            <button
              key={idx}
              onClick={() => handleSendMessage(p.query)}
              disabled={loading}
              style={{
                fontSize: '0.74rem',
                padding: '0.3rem 0.65rem',
                borderRadius: '14px',
                background: 'rgba(30, 41, 59, 0.7)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                color: '#cbd5e1',
                cursor: loading ? 'not-allowed' : 'pointer',
                transition: 'all 0.2s',
                flexShrink: 0
              }}
              onMouseEnter={(e) => { e.currentTarget.style.borderColor = '#38bdf8'; e.currentTarget.style.color = '#38bdf8'; }}
              onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)'; e.currentTarget.style.color = '#cbd5e1'; }}
            >
              {p.label}
            </button>
          ))}
        </div>

        {/* Input Bar */}
        <div style={{
          padding: '0.85rem 1.25rem',
          background: 'var(--card-bg, #0f172a)',
          borderTop: '1px solid var(--border-color, #1e293b)',
          display: 'flex',
          gap: '0.75rem',
          alignItems: 'center'
        }}>
          <input
            type="text"
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSendMessage();
              }
            }}
            placeholder="Ask Copilot about service blast radius, root causes, recovery plans, or verification results..."
            style={{
              flex: 1,
              background: 'rgba(15, 23, 42, 0.9)',
              border: '1px solid rgba(255, 255, 255, 0.12)',
              borderRadius: '8px',
              padding: '0.65rem 1rem',
              color: '#f8fafc',
              fontSize: '0.88rem',
              outline: 'none',
              transition: 'border-color 0.2s'
            }}
            onFocus={(e) => { e.target.style.borderColor = '#6366f1'; }}
            onBlur={(e) => { e.target.style.borderColor = 'rgba(255, 255, 255, 0.12)'; }}
          />

          <button
            onClick={() => handleSendMessage()}
            disabled={!inputQuery.trim() || loading}
            style={{
              background: (!inputQuery.trim() || loading) ? '#334155' : 'linear-gradient(135deg, #4f46e5, #06b6d4)',
              color: '#ffffff',
              border: 'none',
              borderRadius: '8px',
              padding: '0.65rem 1.25rem',
              fontSize: '0.85rem',
              fontWeight: 600,
              cursor: (!inputQuery.trim() || loading) ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              boxShadow: (!inputQuery.trim() || loading) ? 'none' : '0 2px 10px rgba(79, 70, 229, 0.35)',
              transition: 'all 0.2s'
            }}
          >
            <span>Send</span>
            <Send size={15} />
          </button>
        </div>
      </div>
    </div>
  );
}
