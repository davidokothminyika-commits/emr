import { useEffect, useState } from 'react';
import api from '../api';

export default function Followups() {
  const [tasks, setTasks] = useState<any[]>([]);
  const [form, setForm] = useState({ patient_id: 'P-0006', description: '', due_date: '2025-01-01', priority: 'medium' });
  async function load() { const r = await api.get('/api/followups'); setTasks(r.data); }
  useEffect(() => { load(); }, []);
  async function create() {
    await api.post('/api/followups', form);
    setForm({ ...form, description: '' });
    load();
  }
  async function update(id: string, status: string) {
    await api.patch(`/api/followups/${id}`, { status });
    load();
  }
  return (
    <div>
      <h1 className="text-3xl font-bold mb-4">Follow-up Tasks</h1>
      <div className="bg-white border border-[var(--cv-border)] rounded-lg p-4 mb-4">
        <div className="flex gap-2 flex-wrap">
          <input className="border border-[var(--cv-border)] rounded-md px-3 py-2" value={form.patient_id} onChange={e => setForm({ ...form, patient_id: e.target.value })} placeholder="Patient ID" />
          <input className="border border-[var(--cv-border)] rounded-md px-3 py-2 flex-1" value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} placeholder="Description" />
          <input type="date" className="border border-[var(--cv-border)] rounded-md px-3 py-2" value={form.due_date} onChange={e => setForm({ ...form, due_date: e.target.value })} />
          <select className="border border-[var(--cv-border)] rounded-md px-3 py-2" value={form.priority} onChange={e => setForm({ ...form, priority: e.target.value })}>
            <option>low</option><option>medium</option><option>high</option>
          </select>
          <button onClick={create} className="bg-[var(--cv-primary)] text-white px-4 py-2 rounded-md text-sm">Add</button>
        </div>
      </div>
      <div className="space-y-2">
        {tasks.map(t => (
          <div key={t.id} className="bg-white border border-[var(--cv-border)] rounded-lg p-3 flex justify-between items-center">
            <div>
              <div className="font-medium text-sm">{t.description}</div>
              <div className="text-xs text-[var(--cv-text-muted)]">{t.patient_id} • due {t.due_date} • {t.priority} • {t.status}</div>
            </div>
            <div className="flex gap-1">
              <button onClick={() => update(t.id, 'completed')} className="text-xs px-2 py-1 border border-[var(--cv-border)] rounded">Complete</button>
              <button onClick={() => update(t.id, 'cancelled')} className="text-xs px-2 py-1 border border-[var(--cv-border)] rounded">Cancel</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
