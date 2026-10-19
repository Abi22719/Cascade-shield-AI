const API_BASE = 'http://127.0.0.1:8000/api/agent';

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP Error ${response.status}: ${response.statusText}`);
    }
    return await response.json();
  } catch (err) {
    console.error(`Agent API Error [${endpoint}]:`, err);
    throw err;
  }
}

export const agentApi = {
  getHealth: () => request('/health'),
  getActions: () => request('/actions'),
  getConfig: () => request('/config'),
  updateConfig: (cfg) => request('/config', { method: 'PUT', body: JSON.stringify(cfg) }),
  createSession: (data) => request('/sessions', { method: 'POST', body: JSON.stringify(data) }),
  stepSession: (sessionId) => request(`/sessions/${sessionId}/step`, { method: 'POST' }),
  runSession: (sessionId, maxSteps = null) => 
    request(`/sessions/${sessionId}/run`, { method: 'POST', body: JSON.stringify({ max_steps: maxSteps }) }),
  stopSession: (sessionId) => request(`/sessions/${sessionId}/stop`, { method: 'POST' }),
  getSessions: (skip = 0, limit = 50, incidentId = null) => {
    let q = `?skip=${skip}&limit=${limit}`;
    if (incidentId) q += `&incident_id=${encodeURIComponent(incidentId)}`;
    return request(`/sessions${q}`);
  },
  getSession: (sessionId) => request(`/sessions/${sessionId}`),
  getSessionHistory: (sessionId) => request(`/sessions/${sessionId}/history`),
  getRecommendations: (sessionId) => request(`/sessions/${sessionId}/recommendations`),
  deleteSession: (sessionId) => request(`/sessions/${sessionId}`, { method: 'DELETE' }),
  getEvaluation: () => request('/evaluation'),
  comparePolicies: (data) => request('/compare', { method: 'POST', body: JSON.stringify(data) }),
};
