const API_BASE = 'http://127.0.0.1:8000/api/simulation';

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
    console.error(`Simulation API Error [${endpoint}]:`, err);
    throw err;
  }
}

export const simulationApi = {
  getHealth: () => request('/health'),
  getOptions: () => request('/options'),
  getScenarios: (skip = 0, limit = 50, category = null) => {
    let q = `?skip=${skip}&limit=${limit}`;
    if (category) q += `&category=${encodeURIComponent(category)}`;
    return request(`/scenarios${q}`);
  },
  getScenario: (scenarioId) => request(`/scenarios/${scenarioId}`),
  createScenario: (data) => request('/scenarios', { method: 'POST', body: JSON.stringify(data) }),
  updateScenario: (scenarioId, data) => request(`/scenarios/${scenarioId}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteScenario: (scenarioId) => request(`/scenarios/${scenarioId}`, { method: 'DELETE' }),
  cloneScenario: (scenarioId, newName = null) => {
    const q = newName ? `?new_name=${encodeURIComponent(newName)}` : '';
    return request(`/scenarios/${scenarioId}/clone${q}`, { method: 'POST' });
  },
  runScenario: (scenarioId, runConfig = {}) => 
    request(`/scenarios/${scenarioId}/run`, { method: 'POST', body: JSON.stringify(runConfig) }),
  resetScenario: (scenarioId) => request(`/scenarios/${scenarioId}/reset`, { method: 'POST' }),
  getRun: (runId) => request(`/runs/${runId}`),
  getRunTimeline: (runId) => request(`/runs/${runId}/timeline`),
  getRunMetrics: (runId, serviceId = null) => {
    const q = serviceId ? `?service_id=${encodeURIComponent(serviceId)}` : '';
    return request(`/runs/${runId}/metrics${q}`);
  },
  getRunImpact: (runId) => request(`/runs/${runId}/impact`),
  compareRuns: (data) => request('/compare', { method: 'POST', body: JSON.stringify(data) }),
  getEvaluation: () => request('/evaluation'),
};
