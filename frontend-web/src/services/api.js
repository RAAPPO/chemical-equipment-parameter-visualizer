import axios from 'axios';
import { APP_CONFIG, STORAGE_KEYS } from '../constants';

// Configuration
const API_CONFIG = {
  baseURL: APP_CONFIG.apiBaseUrl,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
};
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

// Response interceptor - Refresh token on 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If error is 401 and we haven't retried yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
          refresh: refreshToken,
        });

        // Save new token and retry original request
        localStorage.setItem('access_token', response.data.access);
        originalRequest.headers.Authorization = `Bearer ${response.data.access}`;

        return api(originalRequest);
      } catch (err) {
        // Clear storage and redirect on failed refresh
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(err);
      }
    }

    return Promise.reject(error);
  }
);

// API methods
export const authAPI = {
  login: (username, password) =>
    axios.post(`${API_BASE_URL}/auth/token/`, { username, password }),

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },
};

export const datasetAPI = {
  getAll: () => api.get('/datasets/'),
  getById: (id) => api.get(`/datasets/${id}/`),
  getAnalytics: (id) => api.get(`/datasets/${id}/analytics/`),
  upload: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/upload/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  downloadPDF: (id) =>
    api.get(`/datasets/${id}/pdf/`, { responseType: 'blob' }),
};

export const equipmentAPI = {
  getAll: (datasetId) =>
    api.get('/equipment/', { params: { dataset_id: datasetId } }),
};

export const healthCheck = () => axios.get(`${API_BASE_URL}/health/`);

export default api;