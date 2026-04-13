import axios from 'axios';

const request = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  timeout: 10000,
});

request.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers = config.headers || {}
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error?.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('current_user')
      const path = window.location.pathname || '/'
      if (path.startsWith('/admin')) {
        if (!path.startsWith('/admin/login')) window.location.href = '/admin/login'
      } else {
        if (!path.startsWith('/login')) window.location.href = '/login'
      }
    }
    return Promise.reject(error);
  }
);

export default request;
