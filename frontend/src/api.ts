import axios from 'axios';
const BASE = import.meta.env.VITE_API_BASE || '';
export const api = axios.create({ baseURL: BASE });
export function setToken(t: string | null) {
  if (t) api.defaults.headers.common['Authorization'] = `Bearer ${t}`;
  else delete api.defaults.headers.common['Authorization'];
}
export const auth = {
  login: (u: string, p: string) => api.post('/api/auth/login', { username: u, password: p }).then(r => r.data),
  me: (t: string) => api.get('/api/auth/me', { params: { token: t } }).then(r => r.data),
};
export default api;
