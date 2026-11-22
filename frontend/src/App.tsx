import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { setToken } from './api';
import Layout from './Layout';
import Dashboard from './pages/Dashboard';
import Patients from './pages/Patients';
import PatientProfile from './pages/PatientProfile';
import Summaries from './pages/Summaries';
import Labs from './pages/Labs';
import Art from './pages/Art';
import Alerts from './pages/Alerts';
import Encounters from './pages/Encounters';
import Followups from './pages/Followups';
import Referrals from './pages/Referrals';
import Audit from './pages/Audit';
import Settings from './pages/Settings';

function Login({ onLogin }: any) {
  const [u, setU] = useState('clinician');
  const [p, setP] = useState('demo123');
  const [err, setErr] = useState('');
  const nav = useNavigate();
  async function submit(e: any) {
    e.preventDefault();
    try {
      const { api } = await import('./api');
      const r = await api.post('/api/auth/login', { username: u, password: p });
      localStorage.setItem('token', r.data.token);
      localStorage.setItem('user', JSON.stringify(r.data.user));
      setToken(r.data.token);
      onLogin(r.data.user);
      nav('/');
    } catch (e: any) {
      setErr(e.response?.data?.detail || 'Login failed');
    }
  }
  return (
    <div className="min-h-screen flex items-center justify-center bg-[var(--cv-background)]">
      <form onSubmit={submit} className="bg-white p-8 rounded-lg shadow-md w-96 border border-[var(--cv-border)]">
        <h1 className="text-2xl font-bold mb-2 text-[var(--cv-primary)]">Clinical Intelligence Copilot</h1>
        <p className="text-sm text-[var(--cv-text-muted)] mb-6">Demo sign-in (synthetic data only)</p>
        <label className="block text-sm font-medium mb-1">Username</label>
        <input className="w-full border border-[var(--cv-border)] rounded-md px-3 py-2 mb-4" value={u} onChange={e => setU(e.target.value)} />
        <label className="block text-sm font-medium mb-1">Password</label>
        <input type="password" className="w-full border border-[var(--cv-border)] rounded-md px-3 py-2 mb-4" value={p} onChange={e => setP(e.target.value)} />
        {err && <div className="text-[var(--cv-danger)] text-sm mb-3">{err}</div>}
        <button className="w-full bg-[var(--cv-primary)] text-white py-2 rounded-md font-medium">Sign in</button>
        <p className="text-xs text-[var(--cv-text-muted)] mt-4">clinician / demo123 or admin / admin123</p>
      </form>
    </div>
  );
}

export default function App() {
  const [user, setUser] = useState<any>(null);
  useEffect(() => {
    const t = localStorage.getItem('token');
    const u = localStorage.getItem('user');
    if (t && u) { setToken(t); setUser(JSON.parse(u)); }
  }, []);
  function logout() {
    localStorage.clear(); setToken(null); setUser(null);
  }
  if (!user) {
    return (
      <BrowserRouter>
        <Routes>
          <Route path="*" element={<Login onLogin={setUser} />} />
        </Routes>
      </BrowserRouter>
    );
  }
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout user={user} onLogout={logout} />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/patients" element={<Patients />} />
          <Route path="/patients/:id" element={<PatientProfile />} />
          <Route path="/summaries" element={<Summaries />} />
          <Route path="/labs" element={<Labs />} />
          <Route path="/art" element={<Art />} />
          <Route path="/alerts" element={<Alerts />} />
          <Route path="/encounters" element={<Encounters />} />
          <Route path="/followups" element={<Followups />} />
          <Route path="/referrals" element={<Referrals />} />
          <Route path="/audit" element={<Audit />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="*" element={<Navigate to="/" />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
