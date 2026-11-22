import { useEffect, useState } from 'react';
import api from '../api';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

export default function Dashboard() {
  const [d, setD] = useState<any>(null);
  useEffect(() => { api.get('/api/dashboard').then(r => setD(r.data)); }, []);
  if (!d) return <div>Loading...</div>;
  const cards = [
    ['Total patients', d.total_patients],
    ['Patients requiring review', d.patients_requiring_review],
    ['Outstanding alerts', d.outstanding_alerts],
    ['Overdue investigations', d.overdue_investigations],
    ['Pending approvals', d.pending_approvals],
    ['Upcoming follow-ups', d.upcoming_followups],
    ['Pending follow-ups', d.pending_followups],
    ['Overdue follow-ups', d.overdue_followups],
    ['Completed follow-ups', d.completed_followups],
    ['Due today', d.due_today],
    ['Due within 7 days', d.due_within_7],
  ];
  const labData = Object.entries(d.lab_overview).map(([k, v]) => ({ name: k, count: v }));
  const alertData = Object.entries(d.alert_distribution).map(([k, v]) => ({ name: k, count: v }));
  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Dashboard</h1>
      <div className="grid grid-cols-3 gap-4 mb-6">
        {cards.map(([label, val]) => (
          <div key={label as string} className="bg-white border border-[var(--cv-border)] rounded-lg p-4 shadow-xs">
            <div className="text-sm text-[var(--cv-text-muted)]">{label}</div>
            <div className="text-2xl font-bold text-[var(--cv-primary)]">{val}</div>
          </div>
        ))}
      </div>
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-white border border-[var(--cv-border)] rounded-lg p-4">
          <h2 className="text-lg font-semibold mb-3">Laboratory overview</h2>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={labData}><XAxis dataKey="name" /><YAxis /><Tooltip /><Bar dataKey="count" fill="var(--cv-primary)" /></BarChart>
          </ResponsiveContainer>
        </div>
        <div className="bg-white border border-[var(--cv-border)] rounded-lg p-4">
          <h2 className="text-lg font-semibold mb-3">Alert distribution</h2>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={alertData}><XAxis dataKey="name" /><YAxis /><Tooltip /><Bar dataKey="count" fill="var(--cv-danger)" /></BarChart>
          </ResponsiveContainer>
        </div>
      </div>
      <div className="bg-white border border-[var(--cv-border)] rounded-lg p-4">
        <h2 className="text-lg font-semibold mb-3">Review queue</h2>
        {d.review_queue.length === 0 ? <p className="text-sm text-[var(--cv-text-muted)]">No patients in review queue.</p> : (
          <ul className="text-sm">{d.review_queue.map((pid: string) => <li key={pid}>{pid}</li>)}</ul>
        )}
      </div>
    </div>
  );
}
