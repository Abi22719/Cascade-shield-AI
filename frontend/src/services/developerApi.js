const API_BASE = '/api';

async function handleResponse(response) {
  if (!response.ok) {
    let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
    try {
      const err = await response.json();
      if (err.detail) {
        errorMessage = typeof err.detail === 'string' ? err.detail : JSON.stringify(err.detail);
      }
    } catch {}
    throw new Error(errorMessage);
  }
  return response.json();
}

export const developerApi = {
  async getHealth() {
    const res = await fetch(`${API_BASE}/developer/health`);
    return handleResponse(res);
  },

  async getModules() {
    const res = await fetch(`${API_BASE}/developer/modules`);
    return handleResponse(res);
  },

  async getEndpoints() {
    const res = await fetch(`${API_BASE}/developer/endpoints`);
    return handleResponse(res);
  },

  async testEndpoint(endpointPath) {
    const res = await fetch(`${API_BASE}/developer/test-endpoint`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ endpoint_path: endpointPath })
    });
    return handleResponse(res);
  }
};
