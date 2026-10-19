const API_BASE = '/api/rca';

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
      // response was not json
    }
    throw new Error(errorMessage);
  }
  return response.json();
}

export const rcaApi = {
  // Module 4 health & connectivity check
  async checkHealth() {
    const res = await fetch(`${API_BASE}/health`);
    return handleResponse(res);
  },

  // Trigger RCA investigation
  async analyzeIncident(payload) {
    const res = await fetch(`${API_BASE}/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    return handleResponse(res);
  },

  // List saved investigations
  async getIncidents(params = {}) {
    const query = new URLSearchParams();
    if (params.status) query.append('status', params.status);
    if (params.page) query.append('page', params.page);
    if (params.limit) query.append('limit', params.limit);

    const queryString = query.toString() ? `?${query.toString()}` : '';
    const res = await fetch(`${API_BASE}/incidents${queryString}`);
    return handleResponse(res);
  },

  // Get full incident report
  async getIncident(incidentId) {
    const res = await fetch(`${API_BASE}/incidents/${encodeURIComponent(incidentId)}`);
    return handleResponse(res);
  },

  // Re-run analysis on an existing incident
  async reanalyzeIncident(incidentId) {
    const res = await fetch(`${API_BASE}/incidents/${encodeURIComponent(incidentId)}/reanalyze`, {
      method: 'POST'
    });
    return handleResponse(res);
  },

  // Delete an incident
  async deleteIncident(incidentId) {
    const res = await fetch(`${API_BASE}/incidents/${encodeURIComponent(incidentId)}`, {
      method: 'DELETE'
    });
    return handleResponse(res);
  },

  // Get evidence items for an incident
  async getEvidence(incidentId) {
    const res = await fetch(`${API_BASE}/incidents/${encodeURIComponent(incidentId)}/evidence`);
    return handleResponse(res);
  },

  // Get ranked root cause candidates
  async getCandidates(incidentId) {
    const res = await fetch(`${API_BASE}/incidents/${encodeURIComponent(incidentId)}/candidates`);
    return handleResponse(res);
  },

  // Get event timeline
  async getTimeline(incidentId) {
    const res = await fetch(`${API_BASE}/incidents/${encodeURIComponent(incidentId)}/timeline`);
    return handleResponse(res);
  },

  // Get diagnostic recommendations
  async getRecommendations(incidentId) {
    const res = await fetch(`${API_BASE}/incidents/${encodeURIComponent(incidentId)}/recommendations`);
    return handleResponse(res);
  },

  // Get benchmark evaluation against ground truth
  async getEvaluation() {
    const res = await fetch(`${API_BASE}/evaluation`);
    return handleResponse(res);
  },

  // Compare multiple incidents
  async compareIncidents(payload) {
    const res = await fetch(`${API_BASE}/compare`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    return handleResponse(res);
  }
};
