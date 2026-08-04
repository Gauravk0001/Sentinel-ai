import axios from 'axios';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('sentinelai_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor to handle 401
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('sentinelai_token');
      localStorage.removeItem('sentinelai_user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth APIs
export const authAPI = {
  login: (username: string, password: string) =>
    api.post('/auth/login', new URLSearchParams({ username, password }), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    }),
  register: (data: { email: string; username: string; password: string; full_name: string; role?: string }) =>
    api.post('/auth/register', data),
  me: () => api.get('/auth/me'),
  getUsers: () => api.get('/auth/users'),
};

// Dashboard APIs
export const dashboardAPI = {
  getStats: () => api.get('/dashboard/stats'),
  getRiskDistribution: () => api.get('/dashboard/risk-distribution'),
  getRecentActivities: (limit = 10) => api.get(`/dashboard/recent-activities?limit=${limit}`),
  getRiskTrend: (days = 30) => api.get(`/dashboard/risk-trend?days=${days}`),
  getHeatmap: () => api.get('/dashboard/heatmap'),
  getOverview: () => api.get('/dashboard/overview'),
};

// Employee APIs
export const employeeAPI = {
  getAll: (params?: { department?: string; risk_level?: string; search?: string; page?: number; limit?: number }) =>
    api.get('/employees/', { params }),
  getById: (id: string) => api.get(`/employees/${id}`),
  getRiskHistory: (id: string, days = 30) => api.get(`/employees/${id}/risk-history?days=${days}`),
  getActivities: (id: string, params?: { limit?: number; activity_type?: string }) =>
    api.get(`/employees/${id}/activities`, { params }),
  getHighRisk: (threshold = 60, limit = 10) => api.get(`/employees/high-risk?threshold=${threshold}&limit=${limit}`),
  getDepartments: () => api.get('/employees/departments'),
};

// Alert APIs
export const alertAPI = {
  getAll: (params?: { status?: string; severity?: string; type?: string; employee_id?: string; page?: number; limit?: number }) =>
    api.get('/alerts/', { params }),
  getById: (id: string) => api.get(`/alerts/${id}`),
  getStats: () => api.get('/alerts/stats'),
  acknowledge: (id: string) => api.put(`/alerts/${id}/acknowledge`),
  updateStatus: (id: string, status: string) => api.put(`/alerts/${id}/status`, { status }),
};

// Incident APIs
export const incidentAPI = {
  getAll: (params?: { status?: string; severity?: string; type?: string; page?: number; limit?: number }) =>
    api.get('/incidents/', { params }),
  getById: (id: string) => api.get(`/incidents/${id}`),
  getStats: () => api.get('/incidents/stats'),
  updateStatus: (id: string, status: string) => api.put(`/incidents/${id}/status`, { status }),
  assign: (id: string, analyst: string) => api.put(`/incidents/${id}/assign`, { analyst_name: analyst }),
  escalate: (id: string, reason: string) => api.post(`/incidents/${id}/escalate`, { reason }),
};

// AI Engine APIs
export const aiAPI = {
  predict: (employee_id: string) => api.post('/ai/predict', { employee_id }),
  getEmployeeRisk: (employee_id: string) => api.get(`/ai/employee-risk?employee_id=${employee_id}`),
  getRiskHistory: (employee_id: string, days = 30) => api.get(`/ai/risk-history?employee_id=${employee_id}&days=${days}`),
  getLiveAlerts: (limit = 20) => api.get(`/ai/alerts/live?limit=${limit}`),
  getTimeline: (employee_id: string) => api.get(`/ai/timeline?employee_id=${employee_id}`),
  getHighRisk: (threshold = 60, limit = 10) => api.get(`/ai/high-risk?threshold=${threshold}&limit=${limit}`),
  getModelInfo: () => api.get('/ai/model-info'),
  getBaseline: (employee_id: string) => api.get(`/ai/baseline/${employee_id}`),
  retrain: () => api.post('/ai/train'),
};

// Report APIs
export const reportAPI = {
  getDailySummary: () => api.get('/reports/daily-summary'),
};

export default api;


