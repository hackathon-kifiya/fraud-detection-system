import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8081';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Upload endpoints
export const uploadAPI = {
  transactions: (formData) => api.post('/upload/transactions', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  loanRequests: (formData) => api.post('/upload/loan_requests', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  creditHistory: (formData) => api.post('/upload/credit_history', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  kyc: (formData) => api.post('/upload/kyc', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  repayments: (formData) => api.post('/upload/repayments', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
};

// Detection endpoints
export const detectionAPI = {
  trigger: (data) => api.post('/api/detect', data),
  triggerByType: (type, data) => api.post(`/api/detect/${type}`, data),
  status: () => api.get('/api/detect/status'),
};

// Flagged items endpoints
export const flaggedAPI = {
  getAll: (params) => api.get('/api/flagged', { params }),
  getById: (id) => api.get(`/api/flagged/${id}`),
  verify: (id, data) => api.post(`/api/verify/${id}`, data),
  getStats: () => api.get('/api/flagged/stats'),
};

// Health check
export const healthAPI = {
  check: () => api.get('/health'),
};

export default api;
