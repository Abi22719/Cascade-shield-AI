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

export const adminApi = {
  async getSummary() {
    const res = await fetch(`${API_BASE}/admin/summary`);
    return handleResponse(res);
  },

  async getSettings() {
    const res = await fetch(`${API_BASE}/admin/settings`);
    return handleResponse(res);
  },

  async updateSettings(payload) {
    const res = await fetch(`${API_BASE}/admin/settings`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    return handleResponse(res);
  }
};
