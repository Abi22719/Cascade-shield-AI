const API_BASE = '/api';

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
      // response wasn't json
    }
    throw new Error(errorMessage);
  }
  return response.json();
}

export const dashboardApi = {
  // --- Dashboard Summary & Health ---
  async getSummary() {
    const res = await fetch(`${API_BASE}/dashboard/summary`);
    return handleResponse(res);
  },

  async getHealth() {
    const res = await fetch(`${API_BASE}/dashboard/health`);
    return handleResponse(res);
  },

  async getActivityTimeline(limit = 40) {
    const res = await fetch(`${API_BASE}/dashboard/activity?limit=${limit}`);
    return handleResponse(res);
  },

  async getInsights(limit = 10) {
    const res = await fetch(`${API_BASE}/dashboard/insights?limit=${limit}`);
    return handleResponse(res);
  },

  // --- Search ---
  async search(params = {}) {
    const query = new URLSearchParams();
    if (params.q) query.append('q', params.q);
    if (params.module) query.append('module', params.module);
    if (params.severity) query.append('severity', params.severity);
    if (params.service_id) query.append('service_id', params.service_id);
    if (params.limit) query.append('limit', params.limit);
    if (params.skip) query.append('skip', params.skip);

    const queryString = query.toString() ? `?${query.toString()}` : '';
    const res = await fetch(`${API_BASE}/search${queryString}`);
    return handleResponse(res);
  },

  async getSearchSuggestions(limit = 8) {
    const res = await fetch(`${API_BASE}/search/suggestions?limit=${limit}`);
    return handleResponse(res);
  },

  // --- Notifications ---
  async getNotifications(params = {}) {
    const query = new URLSearchParams();
    if (params.unread_only !== undefined) query.append('unread_only', params.unread_only);
    if (params.severity) query.append('severity', params.severity);
    if (params.source_module) query.append('source_module', params.source_module);
    if (params.limit) query.append('limit', params.limit);

    const queryString = query.toString() ? `?${query.toString()}` : '';
    const res = await fetch(`${API_BASE}/notifications${queryString}`);
    return handleResponse(res);
  },

  async markNotificationRead(id) {
    const res = await fetch(`${API_BASE}/notifications/${encodeURIComponent(id)}/read`, {
      method: 'POST'
    });
    return handleResponse(res);
  },

  async markAllNotificationsRead() {
    const res = await fetch(`${API_BASE}/notifications/read-all`, {
      method: 'POST'
    });
    return handleResponse(res);
  },

  // --- Reports ---
  async listReports(reportType = null, limit = 50) {
    const query = new URLSearchParams();
    if (reportType) query.append('report_type', reportType);
    if (limit) query.append('limit', limit);

    const queryString = query.toString() ? `?${query.toString()}` : '';
    const res = await fetch(`${API_BASE}/reports${queryString}`);
    return handleResponse(res);
  },

  async getReport(id) {
    const res = await fetch(`${API_BASE}/reports/${encodeURIComponent(id)}`);
    return handleResponse(res);
  },

  async generateReport(payload) {
    const res = await fetch(`${API_BASE}/reports/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    return handleResponse(res);
  },

  async exportReportCsv(id) {
    const res = await fetch(`${API_BASE}/reports/${encodeURIComponent(id)}/export/csv`);
    if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to export CSV`);
    return res.text();
  },

  async exportReportJson(id) {
    const res = await fetch(`${API_BASE}/reports/${encodeURIComponent(id)}/export/json`);
    if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to export JSON`);
    return res.json();
  },

  // --- Guided Investigation Workflow ---
  async getIncidentWorkflow(incidentId = null, serviceId = null) {
    let url = `${API_BASE}/workflow/incidents/default`;
    if (incidentId) {
      url = `${API_BASE}/workflow/incidents/${encodeURIComponent(incidentId)}`;
    }
    if (serviceId) {
      url += `?service_id=${encodeURIComponent(serviceId)}`;
    }
    const res = await fetch(url);
    return handleResponse(res);
  },

  async getWorkflowSummary() {
    const res = await fetch(`${API_BASE}/workflow/summary`);
    return handleResponse(res);
  }
};
