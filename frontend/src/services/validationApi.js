const API_BASE = '/api/validation';

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
    console.error(`Validation API Error [${endpoint}]:`, err);
    throw err;
  }
}

export const validationApi = {
  getHealth: () => request('/health'),
  getConfig: () => request('/config'),
  updateConfig: (cfg) => request('/config', { method: 'PUT', body: JSON.stringify(cfg) }),
  getRules: () => request('/rules'),
  runValidation: (data) => request('/run', { method: 'POST', body: JSON.stringify(data) }),
  getRuns: (skip = 0, limit = 50, outcome = null, planId = null) => {
    let q = `?skip=${skip}&limit=${limit}`;
    if (outcome) q += `&outcome=${encodeURIComponent(outcome)}`;
    if (planId) q += `&plan_id=${encodeURIComponent(planId)}`;
    return request(`/runs${q}`);
  },
  getRun: (id) => request(`/runs/${id}`),
  getChecks: (id) => request(`/runs/${id}/checks`),
  getEvidence: (id) => request(`/runs/${id}/evidence`),
  getTimeline: (id) => request(`/runs/${id}/timeline`),
  getComparison: (id) => request(`/runs/${id}/comparison`),
  getRecommendations: (id) => request(`/runs/${id}/recommendations`),
  getEvaluation: () => request('/evaluation'),
  compareValidations: (validationIds) => request('/compare', { method: 'POST', body: JSON.stringify({ validation_ids: validationIds }) }),
};
