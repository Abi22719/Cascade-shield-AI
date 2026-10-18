const API_BASE = '/api/cascade';

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

export const cascadeApi = {
  // Module 3 health status
  async checkHealth() {
    const res = await fetch(`${API_BASE}/health`);
    return handleResponse(res);
  },

  // Summary statistics
  async getSummary() {
    const res = await fetch(`${API_BASE}/summary`);
    return handleResponse(res);
  },

  // Run cascading failure prediction
  async predictCascade(payload) {
    const res = await fetch(`${API_BASE}/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    return handleResponse(res);
  },

  // Run step-by-step simulation
  async simulateCascade(payload) {
    const res = await fetch(`${API_BASE}/simulate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    return handleResponse(res);
  },

  // Get downstream callers impacted by a service failure
  async getServiceImpact(serviceId, maxHops = 5) {
    const res = await fetch(`${API_BASE}/impact/${encodeURIComponent(serviceId)}?max_hops=${maxHops}`);
    return handleResponse(res);
  },

  // Get propagation paths originating from a service
  async getServicePaths(serviceId, maxHops = 5) {
    const res = await fetch(`${API_BASE}/paths/${encodeURIComponent(serviceId)}?max_hops=${maxHops}`);
    return handleResponse(res);
  },

  // List saved scenarios
  async getScenarios(page = 1, limit = 20) {
    const res = await fetch(`${API_BASE}/scenarios?page=${page}&limit=${limit}`);
    return handleResponse(res);
  },

  // Save a simulation scenario
  async saveScenario(payload) {
    const res = await fetch(`${API_BASE}/scenarios`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    return handleResponse(res);
  },

  // Get single scenario
  async getScenario(id) {
    const res = await fetch(`${API_BASE}/scenarios/${encodeURIComponent(id)}`);
    return handleResponse(res);
  },

  // Delete scenario
  async deleteScenario(id) {
    const res = await fetch(`${API_BASE}/scenarios/${encodeURIComponent(id)}`, {
      method: 'DELETE'
    });
    return handleResponse(res);
  },

  // Benchmark ground-truth evaluation
  async getEvaluation() {
    const res = await fetch(`${API_BASE}/evaluation`);
    return handleResponse(res);
  },

  // Compare multiple scenarios
  async compareScenarios(payload) {
    const res = await fetch(`${API_BASE}/compare`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    return handleResponse(res);
  }
};
