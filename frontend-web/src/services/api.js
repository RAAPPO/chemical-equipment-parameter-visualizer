/**
 * API Client for Chemical Equipment Parameter Visualizer
 * Centralized HTTP client with interceptors and error handling
 */
import axios from 'axios';

// Configuration
const API_CONFIG = {
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8100/api',
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
};

// Create axios instance
const api = axios.create(API_CONFIG);

// Request interceptor - Add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - Handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (!error.response) {
      alert("Network Error: Please check if the backend server is running at http://127.0.0.1:8100");
      return Promise.reject(error);
    }
    const originalRequest = error.config;
    // Handle 401 Unauthorized - Attempt token refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');

        if (!refreshToken) {
          throw new Error('No refresh token available');
        }

        const response = await axios.post(
          `${API_CONFIG.baseURL}/auth/token/refresh/`,
          { refresh: refreshToken }
        );

        const { access } = response.data;
        localStorage.setItem('access_token', access);

        // Retry original request with new token
        originalRequest.headers.Authorization = `Bearer ${access}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed - logout user
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// API Service Objects
export const authAPI = {
  /**
   * Authenticate user and get JWT tokens
   */
  login: async (username, password) => {
    const response = await axios.post(
      `${API_CONFIG.baseURL}/auth/token/`,
      { username, password }
    );
    return response.data;
  },

  /**
   * Clear authentication tokens and logout
   */
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('username');
  },
};

export const datasetAPI = {
  /**
   * Get all datasets (paginated)
   */
  getAll: async () => {
    const response = await api.get('/datasets/');
    return response;
  },

  /**
   * Get single dataset by ID
   */
  getById: async (id) => {
    const response = await api.get(`/datasets/${id}/`);
    return response;
  },

  /**
   * Get analytics for a dataset
   */
  getAnalytics: async (id) => {
    const response = await api.get(`/datasets/${id}/analytics/`);
    return response;
  },

  /**
   * Upload CSV file
   */
  upload: async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/upload/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response;
  },

  /**
   * Download PDF report for a dataset
   */
  downloadPDF: async (id) => {
    const response = await api.get(`/datasets/${id}/pdf/`, {
      responseType: 'blob',
    });
    return response;
  },

  // NEW: Update equipment parameters
  updateEquipment: (id, data) => api.put(`/equipment/${id}/`, data),

  // NEW: Delete equipment and trigger stat recalculation
  deleteEquipment: (id) => api.delete(`/equipment/${id}/`),
};

export const equipmentAPI = {
  /**
   * Get all equipment, optionally filtered by dataset
   */
  getAll: async (datasetId) => {
    const params = datasetId ? { dataset_id: datasetId } : {};
    const response = await api.get('/equipment/', { params });
    return response;
  },
};

/**
 * Health check endpoint (public)
 */
export const healthCheck = async () => {
  const response = await axios.get(`${API_CONFIG.baseURL}/health/`);
  return response.data;
};

// Export default api instance for custom requests
export default api;