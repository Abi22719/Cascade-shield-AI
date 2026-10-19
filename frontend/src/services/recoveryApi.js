const API_BASE = 'http://127.0.0.1:8000/api/recovery';

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
    console.error(`Recovery API Error [${endpoint}]:`, err);
    throw err;
  }
}

export const recoveryApi = {
  getHealth: () => request('/health'),
  getOptions: () => request('/options'),
  getConfig: () => request('/config'),
  updateConfig: (cfg) => request('/config', { method: 'PUT', body: JSON.stringify(cfg) }),
  generatePlans: (data) => request('/plan', { method: 'POST', body: JSON.stringify(data) }),
  createPlan: (data) => request('/plans', { method: 'POST', body: JSON.stringify(data) }),
  getPlans: (skip = 0, limit = 50, incidentId = null, scenarioId = null) => {
    let q = `?skip=${skip}&limit=${limit}`;
    if (incidentId) q += `&incident_id=${encodeURIComponent(incidentId)}`;
    if (scenarioId) q += `&scenario_id=${encodeURIComponent(scenarioId)}`;
    return request(`/plans${q}`);
  },
  getPlan: (planId) => request(`/plans/${planId}`),
  updatePlan: (planId, data) => request(`/plans/${planId}`, { method: 'PUT', body: JSON.stringify(data) }),
  deletePlan: (planId) => request(`/plans/${planId}`, { method: 'DELETE' }),
  simulatePlan: (planId, data = {}) => request(`/plans/${planId}/simulate`, { method: 'POST', body: JSON.stringify(data) }),
  getPlanResults: (planId) => request(`/plans/${planId}/results`),
  getPlanTimeline: (planId) => request(`/plans/${planId}/timeline`),
  comparePlans: (data) => request('/compare', { method: 'POST', body: JSON.stringify(data) }),
  getEvaluation: () => request('/evaluation'),
};
