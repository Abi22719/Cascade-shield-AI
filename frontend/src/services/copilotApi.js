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

export const copilotApi = {
  async sendMessage(query, context = {}) {
    const res = await fetch(`${API_BASE}/copilot/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query,
        incident_id: context.incident_id || 'inc-payment-cascade-01',
        service_id: context.service_id,
        session_id: context.session_id
      })
    });
    return handleResponse(res);
  }
};
