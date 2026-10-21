const API_BASE = '/api';

/**
 * Helper to handle fetch responses and parse error messages
 */
async function handleResponse(response) {
  if (!response.ok) {
    let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
    try {
      const errorData = await response.json();
      if (errorData.detail) {
        if (typeof errorData.detail === 'string') {
          errorMessage = errorData.detail;
        } else if (Array.isArray(errorData.detail)) {
          errorMessage = errorData.detail.map(d => `${d.loc?.join('.') || ''}: ${d.msg}`).join(', ');
        }
      }
    } catch {
      // response wasn't json, use statusText
    }
    throw new Error(errorMessage);
  }
  return response.json();
}

export const api = {
  // System Health
  async getHealth() {
    const res = await fetch(`${API_BASE}/health`);
    return handleResponse(res);
  },

  // Services
  async getServices(params = {}) {
    const query = new URLSearchParams();
    if (params.service_type) query.append('service_type', params.service_type);
    if (params.health_status) query.append('health_status', params.health_status);
    if (params.search) query.append('search', params.search);

    const queryString = query.toString() ? `?${query.toString()}` : '';
    const res = await fetch(`${API_BASE}/services${queryString}`);
    return handleResponse(res);
  },

  async getServiceDetail(serviceId) {
    const res = await fetch(`${API_BASE}/services/${encodeURIComponent(serviceId)}`);
    return handleResponse(res);
  },

  async createService(data) {
    const res = await fetch(`${API_BASE}/services`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse(res);
  },

  async updateService(serviceId, data) {
    const res = await fetch(`${API_BASE}/services/${encodeURIComponent(serviceId)}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse(res);
  },

  async deleteService(serviceId) {
    const res = await fetch(`${API_BASE}/services/${encodeURIComponent(serviceId)}`, {
      method: 'DELETE',
    });
    return handleResponse(res);
  },

  // Dependencies
  async getDependencies(params = {}) {
    const query = new URLSearchParams();
    if (params.source_id) query.append('source_id', params.source_id);
    if (params.target_id) query.append('target_id', params.target_id);

    const queryString = query.toString() ? `?${query.toString()}` : '';
    const res = await fetch(`${API_BASE}/dependencies${queryString}`);
    return handleResponse(res);
  },

  async createDependency(data) {
    const res = await fetch(`${API_BASE}/dependencies`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse(res);
  },

  async deleteDependency(dependencyId) {
    const res = await fetch(`${API_BASE}/dependencies/${encodeURIComponent(dependencyId)}`, {
      method: 'DELETE',
    });
    return handleResponse(res);
  },

  // Graph & Impact
  async getGraph() {
    const res = await fetch(`${API_BASE}/graph`);
    return handleResponse(res);
  },

  async getDownstreamImpact(serviceId) {
    const res = await fetch(`${API_BASE}/graph/impact/${encodeURIComponent(serviceId)}`);
    return handleResponse(res);
  },

  async resetTopology() {
    const res = await fetch(`${API_BASE}/graph/reset`, {
      method: 'POST',
    });
    return handleResponse(res);
  },

  // Metrics Summary
  async getMetricsSummary() {
    const res = await fetch(`${API_BASE}/metrics/summary`);
    return handleResponse(res);
  },

  // Telemetry Refresh (Module 1 / Global Refresh)
  async refreshTelemetry(jitter = true) {
    const res = await fetch(`${API_BASE}/metrics/refresh?jitter=${jitter}`, {
      method: 'POST',
    });
    return handleResponse(res);
  },
};
