import axios from 'axios';
import Cookies from 'js-cookie';

// Helper to safely extract error message from API responses
// FastAPI returns {detail: string} OR {detail: [{type, loc, msg, input}]}
export function getErrorMessage(err: any, fallback = 'Une erreur est survenue'): string {
  const detail = err?.response?.data?.detail;
  if (!detail) return fallback;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) {
    return detail.map((e: any) => e.msg || JSON.stringify(e)).join(', ');
  }
  return fallback;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = Cookies.get('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle error responses - normalize validation errors & handle 401
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Normalize Pydantic validation errors: convert detail array to string
    // This prevents React crash: "Objects are not valid as a React child"
    if (error.response?.data?.detail) {
      const detail = error.response.data.detail;
      if (Array.isArray(detail)) {
        error.response.data.detail = detail
          .map((e: any) => typeof e === 'object' ? (e.msg || JSON.stringify(e)) : String(e))
          .join(', ');
      } else if (typeof detail === 'object') {
        error.response.data.detail = detail.msg || JSON.stringify(detail);
      }
    }
    if (error.response?.status === 401) {
      Cookies.remove('access_token');
      Cookies.remove('refresh_token');
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (email: string, password: string) =>
    api.post('/api/auth/login', { email, password }),
  register: (data: {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
    phone?: string;
  }) => api.post('/api/auth/register', data),
  getMe: () => api.get('/api/auth/me'),
  getCompany: () => api.get('/api/auth/company'),
  updateCompany: (data: any) => api.put('/api/auth/company', data),
};

// Dashboard API
export const dashboardAPI = {
  getStats: () => api.get('/api/dashboard/stats'),
};

// Clients API
export const clientsAPI = {
  list: (params?: { search?: string; skip?: number; limit?: number }) =>
    api.get('/api/clients/', { params }),
  get: (id: string) => api.get(`/api/clients/${id}`),
  create: (data: any) => api.post('/api/clients/', data),
  update: (id: string, data: any) => api.put(`/api/clients/${id}`, data),
  delete: (id: string) => api.delete(`/api/clients/${id}`),
};

// Products API
export const productsAPI = {
  list: (params?: { search?: string; category?: string; skip?: number; limit?: number }) =>
    api.get('/api/products/', { params }),
  get: (id: string) => api.get(`/api/products/${id}`),
  create: (data: any) => api.post('/api/products/', data),
  update: (id: string, data: any) => api.put(`/api/products/${id}`, data),
  delete: (id: string) => api.delete(`/api/products/${id}`),
};

// Invoices API
export const invoicesAPI = {
  list: (params?: { invoice_type?: string; status?: string; search?: string; skip?: number; limit?: number }) =>
    api.get('/api/invoices/', { params }),
  get: (id: string) => api.get(`/api/invoices/${id}`),
  create: (data: any) => api.post('/api/invoices/', data),
  update: (id: string, data: any) => api.put(`/api/invoices/${id}`, data),
  delete: (id: string) => api.delete(`/api/invoices/${id}`),
  convert: (id: string) => api.post(`/api/invoices/${id}/convert`),
  downloadPdf: (id: string) => api.get(`/api/invoices/${id}/pdf`, { responseType: 'blob' }),
  downloadXml: (id: string) => api.get(`/api/invoices/${id}/xml`, { responseType: 'blob' }),
};

// Suppliers API
export const suppliersAPI = {
  list: (params?: { search?: string; skip?: number; limit?: number }) =>
    api.get('/api/suppliers/', { params }),
  get: (id: string) => api.get(`/api/suppliers/${id}`),
  create: (data: any) => api.post('/api/suppliers/', data),
  update: (id: string, data: any) => api.put(`/api/suppliers/${id}`, data),
  delete: (id: string) => api.delete(`/api/suppliers/${id}`),
};

export default api;
