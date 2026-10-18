const API_BASE = '/api/anomalies';

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

export const anomalyApi = {
  // Anomaly subsystem health
  async checkHealth() {
    const res = await fetch(`${API_BASE}/health`);
    return handleResponse(res);
  },

  // Summary statistics
  async getSummary() {
    const res = await fetch(`${API_BASE}/summary`);
    return handleResponse(res);
  },

  // Paginated and filtered anomaly alerts
  async getAnomalies(params = {}) {
    const query = new URLSearchParams();
    if (params.service_id) query.append('service_id', params.service_id);
    if (params.severity) query.append('severity', params.severity);
    if (params.detection_method) query.append('detection_method', params.detection_method);
    if (params.acknowledged !== undefined && params.acknowledged !== '') {
      query.append('acknowledged', params.acknowledged);
    }
    if (params.page) query.append('page', params.page);
    if (params.limit) query.append('limit', params.limit);

    const queryString = query.toString() ? `?${query.toString()}` : '';
    const res = await fetch(`${API_BASE}${queryString}`);
    return handleResponse(res);
  },

  // Alert detail
  async getAlertDetail(alertId) {
    const res = await fetch(`${API_BASE}/${encodeURIComponent(alertId)}`);
    return handleResponse(res);
  },

  // Trigger anomaly detection batch
  async runDetection(payload = {}) {
    const res = await fetch(`${API_BASE}/detect`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse(res);
  },

  // Historical service metrics
  async getServiceMetrics(serviceId, points = 35) {
    const res = await fetch(`${API_BASE}/metrics/${encodeURIComponent(serviceId)}?points=${points}`);
    return handleResponse(res);
  },

  // Thresholds configuration
  async getThresholds() {
    const res = await fetch(`${API_BASE}/thresholds`);
    return handleResponse(res);
  },

  async updateThresholds(config) {
    const res = await fetch(`${API_BASE}/thresholds`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config),
    });
    return handleResponse(res);
  },

  // Benchmark evaluation metrics
  async getEvaluation() {
    const res = await fetch(`${API_BASE}/evaluation`);
    return handleResponse(res);
  },

  // Acknowledge alert
  async acknowledgeAlert(alertId) {
    const res = await fetch(`${API_BASE}/${encodeURIComponent(alertId)}/acknowledge`, {
      method: 'POST',
    });
    return handleResponse(res);
  },
};
