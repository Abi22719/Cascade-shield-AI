const API_BASE = '/api/benchmark';

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
    // Check if response is text/markdown
    const contentType = response.headers.get('content-type');
    if (contentType && (contentType.includes('text/markdown') || contentType.includes('text/plain'))) {
      return await response.text();
    }
    return await response.json();
  } catch (err) {
    console.error(`Benchmark API Error [${endpoint}]:`, err);
    throw err;
  }
}

export const benchmarkApi = {
  getHealth: () => request('/health'),
  getConfig: () => request('/config'),
  updateConfig: (cfg) => request('/config', { method: 'PUT', body: JSON.stringify(cfg) }),
  
  getDatasets: (skip = 0, limit = 50) => request(`/datasets?skip=${skip}&limit=${limit}`),
  getDataset: (id) => request(`/datasets/${id}`),
  generateDataset: (data) => request('/datasets/generate', { method: 'POST', body: JSON.stringify(data) }),

  getScenarios: (datasetId = null) => {
    const q = datasetId ? `?dataset_id=${encodeURIComponent(datasetId)}` : '';
    return request(`/scenarios${q}`);
  },
  getScenario: (id) => request(`/scenarios/${id}`),

  getBaselines: () => request('/baselines'),

  createExperiment: (data, autoRun = true) => request(`/experiments?auto_run=${autoRun}`, { method: 'POST', body: JSON.stringify(data) }),
  getExperiments: (skip = 0, limit = 50, status = null) => {
    let q = `?skip=${skip}&limit=${limit}`;
    if (status) q += `&status=${encodeURIComponent(status)}`;
    return request(`/experiments${q}`);
  },
  getExperiment: (id) => request(`/experiments/${id}`),
  runExperiment: (id) => request(`/experiments/${id}/run`, { method: 'POST' }),
  cancelExperiment: (id) => request(`/experiments/${id}/cancel`, { method: 'POST' }),
  getExperimentProgress: (id) => request(`/experiments/${id}/progress`),
  getExperimentResults: (id, moduleName = null) => {
    const q = moduleName ? `?module_name=${encodeURIComponent(moduleName)}` : '';
    return request(`/experiments/${id}/results${q}`);
  },

  compareExperiments: (experimentIds) => request('/compare', { method: 'POST', body: JSON.stringify({ experiment_ids: experimentIds }) }),
  getSummary: () => request('/summary'),

  getReport: (id, format = 'markdown') => request(`/reports/${id}?format=${format}`),
  getExportCsvUrl: (id) => `${API_BASE}/export/${id}/csv`,
  getExportJson: (id) => request(`/export/${id}/json`)
};
