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

export const knowledgeApi = {
  async listArticles(params = {}) {
    const query = new URLSearchParams();
    if (params.category) query.append('category', params.category);
    if (params.service_id) query.append('service_id', params.service_id);
    if (params.q) query.append('q', params.q);

    const qs = query.toString() ? `?${query.toString()}` : '';
    const res = await fetch(`${API_BASE}/knowledge${qs}`);
    return handleResponse(res);
  },

  async getArticle(articleId) {
    const res = await fetch(`${API_BASE}/knowledge/${encodeURIComponent(articleId)}`);
    return handleResponse(res);
  },

  async createArticle(payload) {
    const res = await fetch(`${API_BASE}/knowledge`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    return handleResponse(res);
  },

  async updateArticle(articleId, payload) {
    const res = await fetch(`${API_BASE}/knowledge/${encodeURIComponent(articleId)}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    return handleResponse(res);
  },

  async deleteArticle(articleId) {
    const res = await fetch(`${API_BASE}/knowledge/${encodeURIComponent(articleId)}`, {
      method: 'DELETE'
    });
    return handleResponse(res);
  }
};
