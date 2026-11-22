import { useEffect, useState, useMemo } from 'react';
import api from '../api';
import FollowUpModal from '../components/FollowUpModal';

export default function Followups() {
  const [tasks, setTasks] = useState<any[]>([]);
  const [modal, setModal] = useState(false);
  const [preset, setPreset] = useState<any>({});
  const [q, setQ] = useState('');
  const [status, setStatus] = useState('');
  const [priority, setPriority] = useState('');
  const [sort, setSort] = useState('due_date');
  // editing not used

  async function load() {
    const r = await api.get('/api/followups', { params: { status: status || undefined, priority: priority || undefined } });
    setTasks(r.data);
  }
  useEffect(() => { load(); }, [status, priority]);

  const filtered = useMemo(() => {
    let list = tasks.filter(t => {
      const s = (t.title || '') + ' ' + (t.description || '') + ' ' + t.patient_id;
      if (q && !s.toLowerCase().includes(q.toLowerCase())) return false;
      return true;
    });
    list.sort((a, b) => {
      if (sort === 'due_date') return a.due_date.localeCompare(b.due_date);
      if (sort === 'priority') return a.priority.localeCompare(b.priority);
      if (sort === 'created_at') return a.created_at.localeCompare(b.created_at);
      if (sort === 'patient_id') return a.patient_id.localeCompare(b.patient_id);
      return 0;
    });
    return list;
  }, [tasks, q, sort]);

  const counts = {
    total: tasks.length,
    pending: tasks.filter(t => t.status === 'pending').length,
    overdue: tasks.filter(t => t.status === 'overdue').length,
    completed: tasks.filter(t => t.status === 'completed').length,
    cancelled: tasks.filter(t => t.status === 'cancelled').length,
  };

  async function complete(id: string) {
    await api.patch(`/api/followups/${id}/complete`, { notes: 'Completed via UI' });
    load();
  }
  async function cancel(id: string) {
    if (!confirm('Cancel this task?')) return;
    await api.patch(`/api/followups/${id}/cancel`, { reason: 'Cancelled via UI' });
    load();
  }
  async function reopen(id: string) {
    await api.patch(`/api/followups/${id}/reopen`);
    load();
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-3xl font-bold">Follow-up Tasks</h1>
        <button onClick={() => { setPreset({}); setModal(true); }} className="bg-[var(--cv-primary)] text-white px-4 py-2 rounded-md text-sm">New Follow-up</button>
      </div>
      <div className="grid grid-cols-5 gap-3 mb-4">
        {Object.entries(counts).map(([k, v]) => (
          <div key={k} className="bg-white border border-[var(--cv-border)] rounded-lg p-3">
            <div className="text-xs text-[var(--cv-text-muted)] capitalize">{k}</div>
            <div className="text-xl font-bold text-[var(--cv-primary)]">{v}</div>
          </div>
        ))}
      </div>
      <div className="flex gap-2 mb-4 flex-wrap">
        <input className="border border-[var(--cv-border)] rounded-md px-3 py-2" value={q} onChange={e => setQ(e.target.value)} placeholder="Search patient/task" />
        <select className="border border-[var(--cv-border)] rounded-md px-3 py-2" value={status} onChange={e => setStatus(e.target.value)}>
          <option value="">All statuses</option>
          <option value="pending">Pending</option>
          <option value="overdue">Overdue</option>
          <option value="completed">Completed</option>
          <option value="cancelled">Cancelled</option>
        </select>
        <select className="border border-[var(--cv-border)] rounded-md px-3 py-2" value={priority} onChange={e => setPriority(e.target.value)}>
          <option value="">All priorities</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
        <select className="border border-[var(--cv-border)] rounded-md px-3 py-2" value={sort} onChange={e => setSort(e.target.value)}>
          <option value="due_date">Sort: Due date</option>
          <option value="priority">Sort: Priority</option>
          <option value="created_at">Sort: Created</option>
          <option value="patient_id">Sort: Patient</option>
        </select>
      </div>
      <div className="bg-white border border-[var(--cv-border)] rounded-lg overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-[var(--cv-surface-muted)]">
            <tr><th className="p-3 text-left">ID</th><th className="p-3 text-left">Patient</th><th className="p-3 text-left">Title</th><th className="p-3 text-left">Due</th><th className="p-3 text-left">Priority</th><th className="p-3 text-left">Clinician</th><th className="p-3 text-left">Status</th><th className="p-3 text-left">Actions</th></tr>
          </thead>
          <tbody>
            {filtered.map(t => (
              <tr key={t.id} className="border-t border-[var(--cv-border)]">
                <td className="p-3 text-xs">{t.id}</td>
                <td className="p-3">{t.patient_id}</td>
                <td className="p-3">{t.title || t.description}</td>
                <td className="p-3">{t.due_date}</td>
                <td className="p-3">{t.priority}</td>
                <td className="p-3">{t.assigned_clinician}</td>
                <td className="p-3">{t.status}</td>
                <td className="p-3 flex gap-1">
                  {t.status !== 'completed' && <button onClick={() => complete(t.id)} className="text-xs px-2 py-1 border border-[var(--cv-border)] rounded">Complete</button>}
                  {t.status !== 'cancelled' && <button onClick={() => cancel(t.id)} className="text-xs px-2 py-1 border border-[var(--cv-border)] rounded">Cancel</button>}
                  {(t.status === 'completed' || t.status === 'cancelled') && <button onClick={() => reopen(t.id)} className="text-xs px-2 py-1 border border-[var(--cv-border)] rounded">Reopen</button>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <FollowUpModal open={modal} onClose={() => setModal(false)} onCreated={load} presetPatient={preset.patient_id} presetTitle={preset.title} presetDescription={preset.description} presetRelatedType={preset.related_type} presetRelatedId={preset.related_id} />
    </div>
  );
}
