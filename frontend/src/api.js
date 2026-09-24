// API Client for Qanoon Sahayak Backend

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function getAuthHeaders() {
  const token = localStorage.getItem('qanoon_auth_token');
  const betaCode = localStorage.getItem('qanoon_beta_code');
  const headers = { 'Content-Type': 'application/json' };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  if (betaCode) {
    headers['X-Beta-Code'] = betaCode;
  }
  return headers;
}

export const api = {
  // Auth & Beta Gate
  async verifyBetaCode(code) {
    const res = await fetch(`${API_BASE}/api/auth/verify-beta-code`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Invalid beta invitation code');
    }
    const data = await res.json();
    localStorage.setItem('qanoon_beta_code', code.trim());
    return data;
  },

  async getBetaInfo() {
    try {
      const res = await fetch(`${API_BASE}/api/beta-info`);
      if (res.ok) return await res.json();
      return { beta_enabled: true };
    } catch {
      return { beta_enabled: true };
    }
  },

  async login(email, password) {
    const res = await fetch(`${API_BASE}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Login failed');
    }
    const data = await res.json();
    localStorage.setItem('qanoon_auth_token', data.access_token);
    return data;
  },

  async register(email, password, fullName, betaCode = null) {
    const code = betaCode || localStorage.getItem('qanoon_beta_code') || '';
    const res = await fetch(`${API_BASE}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, full_name: fullName, beta_code: code })
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Registration failed');
    }
    const data = await res.json();
    localStorage.setItem('qanoon_auth_token', data.access_token);
    return data;
  },

  async getMe() {
    const token = localStorage.getItem('qanoon_auth_token');
    if (!token) return null;
    try {
      const res = await fetch(`${API_BASE}/api/auth/me`, {
        headers: getAuthHeaders()
      });
      if (res.ok) return await res.json();
      return null;
    } catch {
      return null;
    }
  },

  logout() {
    localStorage.removeItem('qanoon_auth_token');
  },

  // Chat & Intake Sessions
  async createSession(language = 'en', title = 'New Legal Consultation') {
    const res = await fetch(`${API_BASE}/api/chat/sessions`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ language, title })
    });
    if (!res.ok) throw new Error('Failed to create consultation session');
    return await res.json();
  },

  async listSessions() {
    const res = await fetch(`${API_BASE}/api/chat/sessions`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) return [];
    return await res.json();
  },

  async getSession(sessionId) {
    const res = await fetch(`${API_BASE}/api/chat/sessions/${sessionId}`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error('Failed to load session');
    return await res.json();
  },

  async sendMessage(sessionId, content, language = 'en') {
    const res = await fetch(`${API_BASE}/api/chat/sessions/${sessionId}/messages`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ content, language })
    });
    if (!res.ok) throw new Error('Failed to send message');
    return await res.json();
  },

  async uploadDocument(sessionId, file) {
    const formData = new FormData();
    formData.append('file', file);
    const token = localStorage.getItem('qanoon_auth_token');
    const headers = {};
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const res = await fetch(`${API_BASE}/api/chat/sessions/${sessionId}/upload`, {
      method: 'POST',
      headers,
      body: formData
    });
    if (!res.ok) throw new Error('Failed to upload document');
    return await res.json();
  },

  getExportUrl(sessionId, format = 'html') {
    return `${API_BASE}/api/chat/sessions/${sessionId}/export/${format}`;
  },

  // Lawyer & Legal Aid Directory
  async getLawyers(params = {}) {
    const query = new URLSearchParams();
    if (params.city) query.append('city', params.city);
    if (params.province) query.append('province', params.province);
    if (params.specialty) query.append('specialty', params.specialty);
    if (params.free_aid_only) query.append('free_aid_only', 'true');
    if (params.search) query.append('search', params.search);

    const res = await fetch(`${API_BASE}/api/lawyers?${query.toString()}`);
    if (!res.ok) return { results: [] };
    return await res.json();
  },

  // Emergency Resources
  async getEmergencyResources() {
    const res = await fetch(`${API_BASE}/api/emergency/resources`);
    if (!res.ok) return { resources: [] };
    return await res.json();
  },

  // Legal Corpus Search
  async searchStatutes(q, category = null, jurisdiction = null) {
    const query = new URLSearchParams({ q });
    if (category) query.append('category', category);
    if (jurisdiction) query.append('jurisdiction', jurisdiction);

    const res = await fetch(`${API_BASE}/api/corpus/search?${query.toString()}`);
    if (!res.ok) return { results: [] };
    return await res.json();
  },

  async getSectionDetail(sectionId) {
    const res = await fetch(`${API_BASE}/api/corpus/section/${encodeURIComponent(sectionId)}`);
    if (!res.ok) throw new Error('Statutory section not found');
    return await res.json();
  },

  // Feedback Collection
  async submitFeedback({ sessionId, messageId, feedbackType, category, comment, queryExcerpt, citationsFlagged }) {
    const res = await fetch(`${API_BASE}/api/feedback`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        session_id: sessionId || null,
        message_id: messageId || null,
        feedback_type: feedbackType,
        category: category || 'general',
        comment: comment || null,
        query_excerpt: queryExcerpt || null,
        citations_flagged: citationsFlagged || []
      })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to submit feedback');
    }
    return await res.json();
  },

  async getFeedbackSummary() {
    const res = await fetch(`${API_BASE}/api/feedback/summary`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) return { total_feedbacks: 0, by_type: {} };
    return await res.json();
  }
};
