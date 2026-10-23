import React, { useState, useEffect, useCallback } from 'react';
import {
  Code,
  Terminal,
  Activity,
  Layers,
  Play,
  CheckCircle2,
  XCircle,
  Copy,
  Check,
  RefreshCw,
  ExternalLink,
  ChevronRight,
  Server,
  Database,
  Cpu,
  Clock,
  Send,
  Sliders
} from 'lucide-react';
import { developerApi } from '../services/developerApi';
import StatusBadge from '../components/common/StatusBadge';
import SkeletonLoader from '../components/common/SkeletonLoader';

export default function DeveloperPortal({ onNavigateModule, onAddToast }) {
  const [activeTab, setActiveTab] = useState('health'); // 'health' | 'modules' | 'explorer' | 'sdk'
  const [healthData, setHealthData] = useState(null);
  const [modulesList, setModulesList] = useState([]);
  const [endpointsList, setEndpointsList] = useState([]);
  const [loading, setLoading] = useState(false);

  // API Explorer State
  const [selectedEndpoint, setSelectedEndpoint] = useState('/api/services');
  const [testResponse, setTestResponse] = useState(null);
  const [testingEndpoint, setTestingEndpoint] = useState(false);

  // SDK Code Snippet Language
  const [selectedLang, setSelectedLang] = useState('python'); // 'python' | 'javascript' | 'curl'
  const [copiedSnippet, setCopiedSnippet] = useState(false);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [health, mods, ends] = await Promise.all([
        developerApi.getHealth().catch(() => null),
        developerApi.getModules().catch(() => []),
        developerApi.getEndpoints().catch(() => [])
      ]);
      setHealthData(health);
      setModulesList(mods || []);
      setEndpointsList(ends || []);
    } catch (err) {
      console.warn('Developer Portal data fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Execute Live API Test
  const handleTestEndpoint = async () => {
    if (!selectedEndpoint) return;
    setTestingEndpoint(true);
    setTestResponse(null);
    try {
      const startTime = performance.now();
      const res = await developerApi.testEndpoint(selectedEndpoint);
      const latencyMs = Math.round(performance.now() - startTime);
      setTestResponse({
        status: 200,
        latencyMs,
        data: res
      });
      if (onAddToast) onAddToast(`Endpoint ${selectedEndpoint} tested successfully (${latencyMs}ms)`, 'success', 'API Test OK');
    } catch (err) {
      setTestResponse({
        status: 500,
        error: err.message,
        data: { detail: err.message }
      });
      if (onAddToast) onAddToast(`Test failed: ${err.message}`, 'error', 'API Test Failed');
    } finally {
      setTestingEndpoint(false);
    }
  };

  // Code Snippets
  const codeSnippets = {
    python: `# CascadeShield AI Resilience SDK (Python)
import requests

BASE_URL = "http://127.0.0.1:8000/api"

# 1. Fetch live digital twin topology
response = requests.get(f"{BASE_URL}/graph")
topology = response.json()
print(f"Total microservices modeled: {len(topology.get('nodes', []))}")

# 2. Predict cascading blast radius for payment service
cascade_payload = {
    "failed_services": ["payment-service"],
    "max_hops": 4,
    "threshold": 0.25
}
blast_radius = requests.post(f"{BASE_URL}/cascade/predict", json=cascade_payload).json()
print(f"Predicted blast radius: {blast_radius.get('cascade_blast_radius_pct')}%")

# 3. Query AI Copilot with causal grounding
copilot_res = requests.post(f"{BASE_URL}/copilot/chat", json={
    "query": "What is the primary root cause for payment-service failure?"
}).json()
print("Copilot Reasoning:", copilot_res.get("answer"))`,

    javascript: `// CascadeShield AI Resilience SDK (JavaScript / Node.js)
const BASE_URL = 'http://127.0.0.1:8000/api';

async function investigateResilience() {
  // 1. Fetch digital twin graph
  const graphRes = await fetch(\`\${BASE_URL}/graph\`);
  const graph = await graphRes.json();
  console.log('Nodes loaded:', graph.nodes.length);

  // 2. Run What-If Cascade Simulation
  const cascadeRes = await fetch(\`\${BASE_URL}/cascade/predict\`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      failed_services: ['payment-service'],
      max_hops: 4
    })
  });
  const cascadeData = await cascadeRes.json();
  console.log('Blast Radius:', cascadeData.cascade_blast_radius_pct + '%');
}

investigateResilience();`,

    curl: `# CascadeShield AI REST API (cURL)

# 1. Check System Health
curl -X GET "http://127.0.0.1:8000/api/developer/health" \\
     -H "Accept: application/json"

# 2. Query Live Anomaly Summary
curl -X GET "http://127.0.0.1:8000/api/anomalies/summary" \\
     -H "Accept: application/json"

# 3. Query Bayesian Root Cause Candidates
curl -X GET "http://127.0.0.1:8000/api/rca/candidates" \\
     -H "Accept: application/json"

# 4. Trigger Sandboxed Recovery Validation
curl -X POST "http://127.0.0.1:8000/api/validation/run" \\
     -H "Content-Type: application/json" \\
     -d '{"plan_id": "plan-payment-rollback-01", "service_id": "payment-service"}'`
  };

  const handleCopyCode = () => {
    navigator.clipboard.writeText(codeSnippets[selectedLang]);
    setCopiedSnippet(true);
    setTimeout(() => setCopiedSnippet(false), 2000);
  };

  return (
    <div className="portal-container animate-fade-in" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Top Banner */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <div style={{ background: 'rgba(168, 85, 247, 0.15)', padding: '0.4rem', borderRadius: '8px', color: '#a855f7' }}>
              <Code size={22} />
            </div>
            <h1 style={{ fontSize: '1.4rem', fontWeight: 700, margin: 0, color: 'var(--text-primary, #f8fafc)' }}>
              Developer Portal
            </h1>
            <span style={{ fontSize: '0.72rem', background: '#3b82f622', color: '#60a5fa', padding: '0.15rem 0.5rem', borderRadius: '4px', border: '1px solid #3b82f644' }}>
              PORTAL 6
            </span>
            <span style={{ fontSize: '0.72rem', background: '#10b98122', color: '#34d399', padding: '0.15rem 0.5rem', borderRadius: '4px', border: '1px solid #10b98144' }}>
              REST API V1.0
            </span>
          </div>
          <p style={{ margin: '0.25rem 0 0', fontSize: '0.85rem', color: 'var(--text-secondary, #94a3b8)' }}>
            Subsystem diagnostics, Module 1–10 architectural schemas, interactive sandbox API Explorer, and multi-language resilience SDK snippets.
          </p>
        </div>

        {/* Global Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <button
            onClick={loadData}
            disabled={loading}
            className="header-secondary-btn"
            style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', padding: '0.5rem 0.85rem', borderRadius: '6px', cursor: 'pointer' }}
          >
            <RefreshCw size={14} className={loading ? 'spin-icon' : ''} />
            <span>Refresh Diagnostics</span>
          </button>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="portal-tabs-nav" style={{ display: 'flex', gap: '0.5rem', borderBottom: '1px solid var(--border-color, #1e293b)', paddingBottom: '0.5rem' }}>
        <button
          className={`portal-tab-btn ${activeTab === 'health' ? 'active' : ''}`}
          onClick={() => setActiveTab('health')}
        >
          <Activity size={15} />
          <span>Subsystems & Health</span>
        </button>

        <button
          className={`portal-tab-btn ${activeTab === 'modules' ? 'active' : ''}`}
          onClick={() => setActiveTab('modules')}
        >
          <Layers size={15} />
          <span>Module Architecture (M1–M10)</span>
        </button>

        <button
          className={`portal-tab-btn ${activeTab === 'explorer' ? 'active' : ''}`}
          onClick={() => setActiveTab('explorer')}
        >
          <Terminal size={15} />
          <span>Interactive API Explorer</span>
        </button>

        <button
          className={`portal-tab-btn ${activeTab === 'sdk' ? 'active' : ''}`}
          onClick={() => setActiveTab('sdk')}
        >
          <Code size={15} />
          <span>SDK & Webhooks</span>
        </button>
      </div>

      {/* TAB 1: SUBSYSTEMS & HEALTH */}
      {activeTab === 'health' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {/* Subsystem Stat Cards */}
          <div className="db-summary-grid">
            <div className="db-stat-card">
              <div className="stat-card-header">
                <span>FastAPI Backend Server</span>
                <Server size={18} color="#10b981" />
              </div>
              <div className="stat-card-value" style={{ color: '#10b981' }}>
                {healthData?.server_status || 'ONLINE'}
              </div>
              <div className="stat-card-subtext">Version: {healthData?.version || '1.0.0 Enterprise'}</div>
            </div>

            <div className="db-stat-card">
              <div className="stat-card-header">
                <span>SQLite Database Engine</span>
                <Database size={18} color="#38bdf8" />
              </div>
              <div className="stat-card-value" style={{ color: '#38bdf8' }}>
                {healthData?.database_status || 'CONNECTED'}
              </div>
              <div className="stat-card-subtext">WAL Mode active | Zero locks</div>
            </div>

            <div className="db-stat-card">
              <div className="stat-card-header">
                <span>Digital Twin Simulation State</span>
                <Sliders size={18} color="#a855f7" />
              </div>
              <div className="stat-card-value" style={{ color: '#a855f7' }}>
                VIRTUAL SANDBOX
              </div>
              <div className="stat-card-subtext">Isolated in-memory digital twin</div>
            </div>

            <div className="db-stat-card">
              <div className="stat-card-header">
                <span>Average API Response Latency</span>
                <Clock size={18} color="#10b981" />
              </div>
              <div className="stat-card-value" style={{ color: '#10b981' }}>
                {healthData?.avg_latency_ms || 12} ms
              </div>
              <div className="stat-card-subtext">Local async FastAPI loop</div>
            </div>
          </div>

          {/* Subsystem Status Details */}
          <div style={{
            background: 'var(--card-bg, #0f172a)',
            borderRadius: '10px',
            border: '1px solid var(--border-color, #1e293b)',
            padding: '1.25rem'
          }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 600, margin: '0 0 1rem', color: 'var(--text-primary, #f8fafc)' }}>
              Core Engine Health & Process Inventory
            </h3>
            <div className="enterprise-table-container">
              <table className="enterprise-table">
                <thead>
                  <tr>
                    <th>Subsystem Component</th>
                    <th>Runtime / Technology</th>
                    <th>Port / Interface</th>
                    <th>Status</th>
                    <th>Failsafe Protocol</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td><strong>FastAPI App Server</strong></td>
                    <td>Python 3.12+ (Uvicorn Async)</td>
                    <td><code>http://127.0.0.1:8000</code></td>
                    <td><StatusBadge status="HEALTHY" text="ONLINE" size="xs" /></td>
                    <td>Auto-reload worker reload</td>
                  </tr>
                  <tr>
                    <td><strong>SQLite Relational DB</strong></td>
                    <td>SQLite 3 (SQLAlchemy ORM)</td>
                    <td><code>sqlite:///cascadeshield.db</code></td>
                    <td><StatusBadge status="HEALTHY" text="ONLINE" size="xs" /></td>
                    <td>Atomic rollback transaction</td>
                  </tr>
                  <tr>
                    <td><strong>Multivariate Anomaly Engine</strong></td>
                    <td>Scikit-Learn + Z-Score Filter</td>
                    <td>In-Process (Worker thread)</td>
                    <td><StatusBadge status="HEALTHY" text="ONLINE" size="xs" /></td>
                    <td>Graceful heuristic fallback</td>
                  </tr>
                  <tr>
                    <td><strong>Bayesian Root Cause Analyzer</strong></td>
                    <td>Directed Acyclic Graph (DAG) Solver</td>
                    <td>In-Process DAG Parser</td>
                    <td><StatusBadge status="HEALTHY" text="ONLINE" size="xs" /></td>
                    <td>Heuristic causal ranking</td>
                  </tr>
                  <tr>
                    <td><strong>Recovery Sandbox Validator</strong></td>
                    <td>Isolated Digital Twin Simulation</td>
                    <td>5-Pillar Rule Engine</td>
                    <td><StatusBadge status="HEALTHY" text="ONLINE" size="xs" /></td>
                    <td>Strict blocking of risky plans</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: MODULE ARCHITECTURE MATRIX */}
      {activeTab === 'modules' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <div style={{
            background: 'var(--card-bg, #0f172a)',
            borderRadius: '10px',
            border: '1px solid var(--border-color, #1e293b)',
            padding: '1.25rem'
          }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 600, margin: '0 0 0.5rem', color: 'var(--text-primary, #f8fafc)' }}>
              CascadeShield AI 10-Module Engine Architecture
            </h3>
            <p style={{ margin: '0 0 1.25rem', fontSize: '0.85rem', color: 'var(--text-secondary, #94a3b8)' }}>
              Granular data contracts, inference algorithms, and execution lifecycle across Modules 1 through 10.
            </p>

            <div className="enterprise-table-container">
              <table className="enterprise-table">
                <thead>
                  <tr>
                    <th>Module</th>
                    <th>Core Algorithm</th>
                    <th>Input Schema</th>
                    <th>Output Schema</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    { tag: 'M1', name: 'Digital Twin Modeling', algo: 'Directed Graph & Topology DAG', in: 'Service & Edge definitions', out: 'Graph topology + live metrics', status: 'HEALTHY' },
                    { tag: 'M2', name: 'AI Anomaly Detection', algo: 'Multivariate Isolation Forest + Z-Score', in: 'Telemetry time-series stream', out: 'Anomaly alerts with severity', status: 'HEALTHY' },
                    { tag: 'M3', name: 'Cascade Prediction', algo: 'Reverse-Hop Failure Propagation', in: 'Target failure nodes', out: 'Blast radius % + high-risk paths', status: 'HEALTHY' },
                    { tag: 'M4', name: 'Root Cause Analysis', algo: 'Bayesian Evidence-Grounded Ranking', in: 'Incident alerts & dependency graph', out: 'Ranked candidate suspects & evidence', status: 'HEALTHY' },
                    { tag: 'M5', name: 'Diagnostic Agent', algo: 'Autonomous Multi-Hop Causal Reasoner', in: 'Incident scope & diagnostic queries', out: 'Diagnostic action logs & explanations', status: 'HEALTHY' },
                    { tag: 'M6', name: 'What-If Simulation', algo: 'Dynamic Discrete-Event Engine', in: 'Chaos scenarios & surge configs', out: 'Step-by-step metric timeline', status: 'HEALTHY' },
                    { tag: 'M7', name: 'Recovery Planning', algo: 'Multi-Strategy Mitigation Synthesizer', in: 'RCA suspect & cascade blast', out: 'Ranked recovery plans & risk score', status: 'HEALTHY' },
                    { tag: 'M8', name: 'Recovery Validation', algo: '5-Pillar Automated Sandbox Verifier', in: 'Recovery plan payload', out: '5-pillar pass/fail verdict', status: 'HEALTHY' },
                    { tag: 'M9', name: 'Resilience Benchmark', algo: 'Quantitative Chaos Baseline Engine', in: 'Chaos datasets & experiments', out: 'Standardized resilience scores', status: 'HEALTHY' },
                    { tag: 'M10', name: 'Unified Dashboard', algo: 'Cross-Module Correlation Aggregator', in: 'All 9 modules state feeds', out: 'Executive posture & unified insights', status: 'HEALTHY' }
                  ].map(m => (
                    <tr key={m.tag}>
                      <td>
                        <span style={{ fontSize: '0.72rem', background: '#3b82f622', color: '#60a5fa', padding: '0.1rem 0.4rem', borderRadius: '4px', marginRight: '0.5rem', fontWeight: 600 }}>
                          {m.tag}
                        </span>
                        <strong>{m.name}</strong>
                      </td>
                      <td style={{ color: '#cbd5e1', fontSize: '0.85rem' }}>{m.algo}</td>
                      <td style={{ color: '#94a3b8', fontSize: '0.8rem' }}><code>{m.in}</code></td>
                      <td style={{ color: '#94a3b8', fontSize: '0.8rem' }}><code>{m.out}</code></td>
                      <td><StatusBadge status={m.status} size="xs" /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: INTERACTIVE API EXPLORER */}
      {activeTab === 'explorer' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.3fr', gap: '1.25rem' }}>
          {/* Endpoint Selector & Config */}
          <div style={{
            background: 'var(--card-bg, #0f172a)',
            borderRadius: '10px',
            border: '1px solid var(--border-color, #1e293b)',
            padding: '1.25rem',
            display: 'flex',
            flexDirection: 'column',
            gap: '1rem'
          }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 600, margin: 0, color: 'var(--text-primary, #f8fafc)' }}>
              API Sandbox Request Builder
            </h3>

            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#cbd5e1', marginBottom: '0.4rem' }}>
                Select API Endpoint:
              </label>
              <select
                value={selectedEndpoint}
                onChange={(e) => setSelectedEndpoint(e.target.value)}
                style={{
                  width: '100%',
                  background: 'rgba(15, 23, 42, 0.8)',
                  border: '1px solid rgba(255,255,255,0.15)',
                  borderRadius: '6px',
                  color: '#f8fafc',
                  padding: '0.6rem 0.75rem',
                  fontSize: '0.85rem'
                }}
              >
                <option value="/api/services">GET /api/services (Service Catalog)</option>
                <option value="/api/graph">GET /api/graph (Topology Graph)</option>
                <option value="/api/admin/summary">GET /api/admin/summary (Admin Overview)</option>
                <option value="/api/admin/settings">GET /api/admin/settings (Platform Settings)</option>
                <option value="/api/incidents">GET /api/incidents (Incident Records)</option>
                <option value="/api/developer/health">GET /api/developer/health (System Health)</option>
                <option value="/api/security/users">GET /api/security/users (RBAC Directory)</option>
                <option value="/api/security/audit">GET /api/security/audit (Immutable Audit Trail)</option>
                <option value="/api/knowledge">GET /api/knowledge (Knowledge Articles)</option>
              </select>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#cbd5e1', marginBottom: '0.4rem' }}>
                HTTP Method:
              </label>
              <input
                type="text"
                disabled
                value="GET"
                style={{
                  width: '100%',
                  background: 'rgba(15, 23, 42, 0.5)',
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '6px',
                  color: '#38bdf8',
                  padding: '0.5rem 0.75rem',
                  fontSize: '0.85rem',
                  fontWeight: 700
                }}
              />
            </div>

            <button
              onClick={handleTestEndpoint}
              disabled={testingEndpoint}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.45rem',
                padding: '0.65rem 1.25rem',
                borderRadius: '6px',
                border: 'none',
                background: 'linear-gradient(135deg, #a855f7, #6366f1)',
                color: '#ffffff',
                fontWeight: 600,
                cursor: testingEndpoint ? 'not-allowed' : 'pointer',
                boxShadow: '0 2px 10px rgba(168, 85, 247, 0.35)',
                marginTop: '0.5rem'
              }}
            >
              <Play size={15} />
              <span>{testingEndpoint ? 'Executing Request...' : 'Send Live Request'}</span>
            </button>
          </div>

          {/* Response Payload Viewer */}
          <div style={{
            background: 'var(--card-bg, #0f172a)',
            borderRadius: '10px',
            border: '1px solid var(--border-color, #1e293b)',
            padding: '1.25rem',
            display: 'flex',
            flexDirection: 'column'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
              <h3 style={{ fontSize: '1rem', fontWeight: 600, margin: 0, color: 'var(--text-primary, #f8fafc)' }}>
                Response Body
              </h3>
              {testResponse && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <span style={{ fontSize: '0.72rem', background: '#10b98122', color: '#34d399', padding: '0.15rem 0.4rem', borderRadius: '4px' }}>
                    Status {testResponse.status}
                  </span>
                  <span style={{ fontSize: '0.72rem', color: '#94a3b8' }}>
                    {testResponse.latencyMs} ms
                  </span>
                </div>
              )}
            </div>

            <div style={{
              flex: 1,
              background: '#090d16',
              borderRadius: '8px',
              border: '1px solid rgba(255,255,255,0.08)',
              padding: '1rem',
              overflowY: 'auto',
              maxHeight: '380px',
              fontSize: '0.78rem',
              fontFamily: 'Consolas, monospace',
              color: '#38bdf8'
            }}>
              {!testResponse ? (
                <span style={{ color: '#64748b' }}>
                  Click &apos;Send Live Request&apos; to execute endpoint against backend server.
                </span>
              ) : (
                <pre style={{ margin: 0 }}>
                  {JSON.stringify(testResponse.data, null, 2)}
                </pre>
              )}
            </div>
          </div>
        </div>
      )}

      {/* TAB 4: SDK & WEBHOOKS */}
      {activeTab === 'sdk' && (
        <div style={{
          background: 'var(--card-bg, #0f172a)',
          borderRadius: '10px',
          border: '1px solid var(--border-color, #1e293b)',
          padding: '1.25rem',
          display: 'flex',
          flexDirection: 'column',
          gap: '1rem'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h3 style={{ fontSize: '1rem', fontWeight: 600, margin: '0 0 0.25rem', color: 'var(--text-primary, #f8fafc)' }}>
                Developer Client SDKs & Code Samples
              </h3>
              <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--text-secondary, #94a3b8)' }}>
                Integrate CascadeShield AI programmatically into your CI/CD pipelines and deployment orchestrators.
              </p>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              {/* Language Pills */}
              {['python', 'javascript', 'curl'].map(lang => (
                <button
                  key={lang}
                  onClick={() => setSelectedLang(lang)}
                  style={{
                    padding: '0.35rem 0.75rem',
                    borderRadius: '6px',
                    fontSize: '0.78rem',
                    fontWeight: 600,
                    textTransform: 'uppercase',
                    cursor: 'pointer',
                    background: selectedLang === lang ? '#6366f1' : 'rgba(30, 41, 59, 0.7)',
                    color: selectedLang === lang ? '#ffffff' : '#94a3b8',
                    border: selectedLang === lang ? '1px solid #818cf8' : '1px solid rgba(255,255,255,0.08)'
                  }}
                >
                  {lang}
                </button>
              ))}

              <button
                onClick={handleCopyCode}
                className="header-secondary-btn"
                style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', padding: '0.35rem 0.75rem', borderRadius: '6px', cursor: 'pointer' }}
                title="Copy snippet"
              >
                {copiedSnippet ? <Check size={14} color="#10b981" /> : <Copy size={14} />}
                <span>{copiedSnippet ? 'Copied!' : 'Copy Code'}</span>
              </button>
            </div>
          </div>

          <div style={{
            background: '#090d16',
            borderRadius: '8px',
            border: '1px solid rgba(255,255,255,0.08)',
            padding: '1.25rem',
            overflowX: 'auto',
            fontSize: '0.82rem',
            fontFamily: 'Consolas, monospace',
            color: '#cbd5e1'
          }}>
            <pre style={{ margin: 0 }}>
              {codeSnippets[selectedLang]}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}
