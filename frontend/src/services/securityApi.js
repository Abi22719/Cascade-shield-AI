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

export const securityApi = {
  async getUsers() {
    const res = await fetch(`${API_BASE}/security/users`);
    return handleResponse(res);
  },

  async updateUserRole(userId, newRole) {
    const res = await fetch(`${API_BASE}/security/users/${encodeURIComponent(userId)}/role`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ role: newRole })
    });
    return handleResponse(res);
  },

  async getRoles() {
    const res = await fetch(`${API_BASE}/security/roles`);
    return handleResponse(res);
  },

  async getAuditLogs(params = {}) {
    const query = new URLSearchParams();
    if (params.actor_id) query.append('actor_id', params.actor_id);
    if (params.action) query.append('action', params.action);
    if (params.resource_type) query.append('resource_type', params.resource_type);
    if (params.status) query.append('status', params.status);
    if (params.limit) query.append('limit', params.limit);

    const qs = query.toString() ? `?${query.toString()}` : '';
    const res = await fetch(`${API_BASE}/security/audit${qs}`);
    return handleResponse(res);
  },

  async getOverview() {
    const res = await fetch(`${API_BASE}/security/overview`);
    return handleResponse(res);
  }
};
