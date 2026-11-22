import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { Activity, Users, FileText, FlaskConical, Pill, AlertTriangle, Stethoscope, CheckSquare, Send, ScrollText, Settings, LogOut, Search } from 'lucide-react';
import { useState } from 'react';

const nav = [
  { to: '/', label: 'Dashboard', icon: Activity },
  { to: '/patients', label: 'Patients', icon: Users },
  { to: '/summaries', label: 'Clinical Summaries', icon: FileText },
  { to: '/labs', label: 'Laboratory Intelligence', icon: FlaskConical },
  { to: '/art', label: 'ART Treatment Timeline', icon: Pill },
  { to: '/alerts', label: 'Clinical Alerts', icon: AlertTriangle },
  { to: '/encounters', label: 'Encounter Documentation', icon: Stethoscope },
  { to: '/followups', label: 'Follow-up Tasks', icon: CheckSquare },
  { to: '/referrals', label: 'Referrals', icon: Send },
  { to: '/audit', label: 'Audit Log', icon: ScrollText },
  { to: '/settings', label: 'System Settings', icon: Settings },
];

export default function Layout({ user, onLogout }: any) {
  const [q, setQ] = useState('');
  const navigate = useNavigate();
  return (
    <div className="flex h-screen">
      <aside className="w-60 bg-white border-r border-[var(--cv-border)] flex flex-col">
        <div className="h-14 flex items-center px-4 border-b border-[var(--cv-border)]">
          <span className="font-bold text-[var(--cv-primary)]">Clinical Intelligence Copilot</span>
        </div>
        <nav className="flex-1 overflow-y-auto p-2">
          {nav.map(n => (
            <NavLink key={n.to} to={n.to} end={n.to === '/'} className={({ isActive }) =>
              `flex items-center gap-2 px-3 py-2 rounded-md text-sm mb-1 ${isActive ? 'bg-[var(--cv-primary-subtle)] text-[var(--cv-primary)] font-medium' : 'text-[var(--cv-text)] hover:bg-[var(--cv-surface-hover)]'}`}>
              <n.icon size={16} /> {n.label}
            </NavLink>
          ))}
        </nav>
        <div className="p-3 border-t border-[var(--cv-border)] text-xs text-[var(--cv-text-muted)]">
          Demo environment • Synthetic data only
        </div>
      </aside>
      <div className="flex-1 flex flex-col">
        <header className="h-14 bg-white border-b border-[var(--cv-border)] flex items-center px-4 gap-4">
          <div className="flex items-center gap-2 flex-1">
            <Search size={16} className="text-[var(--cv-text-muted)]" />
            <input value={q} onChange={e => setQ(e.target.value)} onKeyDown={e => { if (e.key === 'Enter') navigate(`/patients?q=${encodeURIComponent(q)}`); }}
              placeholder="Search patient..." className="border border-[var(--cv-border)] rounded-md px-3 py-1.5 text-sm w-64" />
          </div>
          <span className="text-sm text-[var(--cv-text-muted)]">EMR mode: synthetic</span>
          <span className="text-sm font-medium">{user?.full_name}</span>
          <button onClick={onLogout} className="text-sm text-[var(--cv-text-muted)] flex items-center gap-1"><LogOut size={14} /> Logout</button>
        </header>
        <main className="flex-1 overflow-y-auto p-6 bg-[var(--cv-background)]">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
