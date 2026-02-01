/**
 * Application constants
 * Centralized configuration values
 */

export const APP_CONFIG = {
  name: import.meta.env.VITE_APP_NAME || 'Chemical Equipment Parameter Visualizer',
  version: import.meta.env.VITE_APP_VERSION || '1.0.0',
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8100/api',
};

export const CHART_COLORS = {
  primary: ['#1E3A8A', '#3B82F6', '#60A5FA', '#93C5FD', '#DBEAFE'],
  secondary: ['#F97316', '#FB923C', '#FDBA74'],
};

export const CSV_REQUIREMENTS = {
  maxSizeMB: 10,
  requiredColumns: ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature'],
  allowedExtensions: ['.csv'],
};

export const ROUTES = {
  LOGIN: '/login',
  DASHBOARD: '/dashboard',
  DATASET_DETAIL: '/dataset/:id',
};

export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
  USERNAME: 'username',
};
