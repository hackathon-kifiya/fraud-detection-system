import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:4000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging and auth
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
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
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
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
  // Create a new flagged item
  create: (data) => api.post('/api/flagged-items', data),
  
  // Get all flagged items with pagination and filters
  getAll: (params) => api.get('/api/flagged-items', { params }),
  
  // Get flagged item by ID
  getById: (id) => api.get(`/api/flagged-items/${id}`),
  
  // Update flagged item
  update: (id, data) => api.put(`/api/flagged-items/${id}`, data),
  
  // Delete flagged item
  delete: (id) => api.delete(`/api/flagged-items/${id}`),
  
  // Verify flagged item (confirm or mark as false positive)
  verify: (id, data) => api.post(`/api/flagged-items/${id}/verify`, data),
  
  // Get statistics
  getStats: () => api.get('/api/flagged-items/stats'),
  
  // Get flagged items by type
  getByType: (type, params) => api.get(`/api/flagged-items/type/${type}`, { params }),
};

// Health check
export const healthAPI = {
  check: () => api.get('/health'),
};

// User management endpoints
export const userAPI = {
  // Authentication
  register: (userData) => api.post('/api/auth/register', userData),
  login: (credentials) => api.post('/api/auth/login', credentials),
  
  // User management
  getUsers: (params) => api.get('/api/users', { params }),
  getUser: (id) => api.get(`/api/users/${id}`),
  updateUser: (id, userData) => api.put(`/api/users/${id}`, userData),
  deleteUser: (id) => api.delete(`/api/users/${id}`),
  changePassword: (id, passwordData) => api.post(`/api/users/${id}/change-password`, passwordData),
};


export default api;
