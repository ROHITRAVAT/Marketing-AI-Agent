import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

/**
 * Centralized gate for mock fallbacks.
 * In production or normal development, this is false, ensuring real backend errors
 * are surfaced rather than deceptive fabricated successes.
 * To enable local offline mock simulation during isolated dev work, set VITE_ENABLE_DEV_FALLBACK=true in .env.
 */
export const IS_DEV_FALLBACK_ENABLED =
  import.meta.env.DEV && import.meta.env.VITE_ENABLE_DEV_FALLBACK === 'true';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
});

// Request interceptor: attach token if available
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('auth_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError) => Promise.reject(error)
);

// Response interceptor: handle unauthorized/errors gracefully
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Clear token if expired or unauthorized
      localStorage.removeItem('auth_token');
      if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;
