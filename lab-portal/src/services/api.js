import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8081';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (data) => api.post('/api/auth/login', data),
  getProfile: () => api.get('/api/auth/profile'),
};

// Lab-specific APIs (these will be the same as the main app for now)
export const labAPI = {
  // Sandbox APIs
  getSandboxData: (params) => api.get('/api/sandbox/data', { params }),
  runSandboxTest: (data) => api.post('/api/sandbox/test', data),
  
  // Data Synthesis APIs
  generateSyntheticData: (data) => api.post('/api/data-synthesis/generate', data),
  downloadSyntheticData: (id) => api.get(`/api/data-synthesis/download/${id}`),
  
  // File Upload APIs
  uploadFile: (formData) => api.post('/api/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  }),
};

export default api;

