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

export const incidentsApi = {
  async listIncidents(params = {}) {
    const query = new URLSearchParams();
    if (params.status) query.append('status', params.status);
    if (params.severity) query.append('severity', params.severity);
    if (params.limit) query.append('limit', params.limit);

    const qs = query.toString() ? `?${query.toString()}` : '';
    const res = await fetch(`${API_BASE}/incidents${qs}`);
    return handleResponse(res);
  },

  async getIncidents(params = {}) {
    return this.listIncidents(params);
  },

  async getIncidentDetails(incidentId) {
    const res = await fetch(`${API_BASE}/incidents/${encodeURIComponent(incidentId)}`);
    return handleResponse(res);
  },

  async getIncidentActivity(incidentId) {
    const res = await fetch(`${API_BASE}/incidents/${encodeURIComponent(incidentId)}/activity`);
    return handleResponse(res);
  },

  async createIncident(payload) {
    const res = await fetch(`${API_BASE}/incidents`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    return handleResponse(res);
  }
};
