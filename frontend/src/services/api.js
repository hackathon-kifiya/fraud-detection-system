import axios from "axios";

const API_BASE_URL =
  process.env.REACT_APP_BACKEND_URL || "http://localhost";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor for logging and auth
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("authToken");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    console.log(
      `Making ${config.method?.toUpperCase()} request to ${config.url}`
    );
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
      localStorage.removeItem("authToken");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }
    console.error("API Error:", error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Upload endpoints
export const uploadAPI = {
  transactions: (formData) =>
    api.post("/upload/transactions", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
  loanRequests: (formData) =>
    api.post("/upload/loan_requests", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
  creditHistory: (formData) =>
    api.post("/upload/credit_history", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
  kyc: (formData) =>
    api.post("/upload/kyc", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
  repayments: (formData) =>
    api.post("/upload/repayments", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
};

// Detection endpoints
export const detectionAPI = {
  trigger: (data) => api.post("/api/detect", data),
  triggerByType: (type, data) => api.post(`/api/detect/${type}`, data),
  status: () => api.get("/api/detect/status"),
};

// Flagged items endpoints
export const flaggedAPI = {
  // Create a new flagged item
  create: (data) => api.post("/api/flagged-items", data),

  // Get all flagged items with pagination and filters
  getAll: (params) => api.get("/api/flagged-items", { params }),

  // Get flagged item by ID
  getById: (id) => api.get(`/api/flagged-items/${id}`),

  // Update flagged item
  update: (id, data) => api.put(`/api/flagged-items/${id}`, data),

  // Delete flagged item
  delete: (id) => api.delete(`/api/flagged-items/${id}`),

  // Verify flagged item (confirm or mark as false positive)
  verify: (id, data) => api.post(`/api/flagged-items/${id}/verify`, data),

  // Get statistics
  getStats: () => api.get("/api/flagged-items/stats"),

  // Get flagged items by type
  getByType: (type, params) =>
    api.get(`/api/flagged-items/type/${type}`, { params }),
};

// Health check
export const healthAPI = {
  check: () => api.get("/health"),
};

// User management endpoints
export const userAPI = {
  // Authentication
  register: (userData) => api.post("/api/auth/register", userData),
  login: (credentials) => api.post("/api/auth/login", credentials),

  // User management
  getUsers: (params) => api.get("/api/users", { params }),
  getUser: (id) => api.get(`/api/users/${id}`),
  updateUser: (id, userData) => api.put(`/api/users/${id}`, userData),
  deleteUser: (id) => api.delete(`/api/users/${id}`),
  changePassword: (id, passwordData) =>
    api.post(`/api/users/${id}/change-password`, passwordData),
};

// Auditor endpoints
export const auditAPI = {
  // Get flagged items for auditor review
  getFlaggedItems: (params) => api.get("/api/audit/flagged-items", { params }),

  // Get detailed flagged item with original data
  getFlaggedItemDetail: (id) =>
    api.get(`/api/audit/flagged-items/${id}/detail`),

  // Classify flagged item (confirm fraud or false positive)
  classifyFlaggedItem: (id, data) =>
    api.post(`/api/audit/flagged-items/${id}/classify`, data),

  // Add audit note to flagged item
  addAuditNote: (id, data) =>
    api.post(`/api/audit/flagged-items/${id}/notes`, data),

  // Get audit notes for flagged item
  getAuditNotes: (id) => api.get(`/api/audit/flagged-items/${id}/notes`),

  // Get personal review history
  getPersonalReviewHistory: (params) =>
    api.get("/api/audit/my-reviews", { params }),

  // Get audit trail for flagged item
  getAuditTrail: (id) => api.get(`/api/audit/flagged-items/${id}/audit-trail`),

  // Get audit statistics
  getAuditStats: () => api.get("/api/audit/stats"),
};

// Admin endpoints
export const adminAPI = {
  // Performance Reports
  generatePerformanceReport: (data) =>
    api.post("/api/admin/reports/generate", data),
  getPerformanceReports: (params) => api.get("/api/admin/reports", { params }),
  getPerformanceReport: (id) => api.get(`/api/admin/reports/${id}`),
  downloadPerformanceReport: (id) =>
    api.get(`/api/admin/reports/${id}/download`),

  // KPI Metrics
  getKPIMetrics: () => api.get("/api/admin/kpi/metrics"),
  getKPIHistory: (params) => api.get("/api/admin/kpi/history", { params }),
  getKPIDashboard: () => api.get("/api/admin/kpi/dashboard"),

  // Auditor Performance Auditing
  getAllAuditorsPerformance: (params) =>
    api.get("/api/admin/auditors/performance", { params }),
  getAuditorPerformance: (id, params) =>
    api.get(`/api/admin/auditors/${id}/performance`, { params }),
  getAuditorReviews: (id, params) =>
    api.get(`/api/admin/auditors/${id}/reviews`, { params }),
  getAuditorsEfficiency: (params) =>
    api.get("/api/admin/auditors/efficiency", { params }),
  getAuditorWorkload: (params) =>
    api.get("/api/admin/auditors/workload", { params }),

  // Risk Threshold Management
  getRiskThresholds: () => api.get("/api/admin/config/risk-thresholds"),
  updateRiskThresholds: (data) =>
    api.put("/api/admin/config/risk-thresholds", data),
  getRiskThresholdsHistory: (params) =>
    api.get("/api/admin/config/risk-thresholds/history", { params }),

  // System Configuration
  getSystemConfig: () => api.get("/api/admin/config"),
  updateSystemConfig: (key, data) => api.put(`/api/admin/config/${key}`, data),
  getSystemConfigHistory: (params) =>
    api.get("/api/admin/config/history", { params }),

  // Case Assignment
  assignCase: (data) => api.post("/api/admin/cases/assign", data),
  bulkAssignCases: (data) => api.post("/api/admin/cases/bulk-assign", data),
  getUnassignedCases: (params) =>
    api.get("/api/admin/cases/unassigned", { params }),
  getCaseAssignments: (params) =>
    api.get("/api/admin/cases/assignments", { params }),
  updateCaseAssignment: (id, data) =>
    api.put(`/api/admin/cases/assignments/${id}`, data),
  deleteCaseAssignment: (id) =>
    api.delete(`/api/admin/cases/assignments/${id}`),

  // User Management
  getUsers: (params) => api.get("/api/users", { params }),

  // Analytics
  getSystemOverview: () => api.get("/api/admin/analytics/overview"),
  getTrendAnalysis: (params) =>
    api.get("/api/admin/analytics/trends", { params }),
  getThroughputMetrics: (params) =>
    api.get("/api/admin/analytics/throughput", { params }),
};

// Rule Engine endpoints
export const ruleEngineAPI = {
  // Rule CRUD operations
  createRule: (data) => api.post("/api/rules", data),
  getAllRules: (params) => api.get("/api/rules", { params }),
  getRule: (id) => api.get(`/api/rules/${id}`),
  updateRule: (id, data) => api.put(`/api/rules/${id}`, data),
  deleteRule: (id) => api.delete(`/api/rules/${id}`),

  // Rule activation
  activateRule: (id) => api.post(`/api/rules/${id}/activate`),
  deactivateRule: (id) => api.post(`/api/rules/${id}/deactivate`),

  // Rule validation and versioning
  validateDrl: (data) => api.post("/api/rules/validate", data),
  getRuleVersions: (id) => api.get(`/api/rules/${id}/versions`),
  rollbackRule: (id, version, data) =>
    api.post(`/api/rules/${id}/rollback/${version}`, data),

  // Rule evaluation
  evaluateTransaction: (facts) =>
    api.post("/api/evaluate/transaction", { facts }),
  evaluateKYC: (facts) => api.post("/api/evaluate/kyc", { facts }),
  evaluateLoan: (facts) => api.post("/api/evaluate/loan", { facts }),
  evaluateCredit: (facts) => api.post("/api/evaluate/credit", { facts }),
  evaluateRepayment: (facts) => api.post("/api/evaluate/repayment", { facts }),
  evaluateGeneric: (dataType, facts) =>
    api.post("/api/evaluate/generic", { dataType, facts }),
};

// Risk Aggregation endpoints
export const riskAggregationAPI = {
  // Risk decision parameters
  getParameters: () => api.get("/api/risk/parameters"),
  updateParameters: (data) => api.put("/api/risk/parameters", data),

  // Risk scoring
  calculateRiskScore: (data) => api.post("/api/risk/calculate", data),
  getRiskHistory: (params) => api.get("/api/risk/history", { params }),
};

// Anomaly Detection endpoints
export const anomalyDetectionAPI = {
  // Anomaly detection
  detectAnomalies: (data) => api.post("/api/anomaly/detect", data),
  getAnomalyStats: () => api.get("/api/anomaly/stats"),
  getAnomalyHistory: (params) => api.get("/api/anomaly/history", { params }),
  
  // Model management
  getModelStatus: () => api.get("/api/anomaly/model/status"),
  retrainModel: (data) => api.post("/api/anomaly/model/retrain", data),
  getModelMetrics: () => api.get("/api/anomaly/model/metrics"),
};

// Prediction Engine endpoints
export const predictionAPI = {
  // Fraud prediction
  predictFraud: (data) => api.post("/api/predict/fraud", data),
  getPredictionStats: () => api.get("/api/predict/stats"),
  getPredictionHistory: (params) => api.get("/api/predict/history", { params }),
  
  // Model management
  getModelStatus: () => api.get("/api/predict/model/status"),
  retrainModel: (data) => api.post("/api/predict/model/retrain", data),
  getModelMetrics: () => api.get("/api/predict/model/metrics"),
  getFeatureImportance: () => api.get("/api/predict/features/importance"),
};

export default api;
