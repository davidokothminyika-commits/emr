import { useEffect, useState } from 'react';
import api from '../api';

export default function Encounters() {
  const [pid, setPid] = useState('P-0001');
  const [obs, setObs] = useState('');
  const [notes, setNotes] = useState<any[]>([]);
  const [current, setCurrent] = useState<any>(null);
  async function draft() {
    const r = await api.post('/api/encounters/draft', { patient_id: pid, observations: obs });
    setCurrent(r.data);
    loadNotes();
  }
  async function loadNotes() {
    const r = await api.get('/api/encounters/notes', { params: { patient_id: pid } });
    setNotes(r.data);
  }
  useEffect(() => { loadNotes(); }, []);
  async function approve(id: string) {
    await api.post(`/api/encounters/notes/${id}/approve`);
    loadNotes();
  }
  async function reject(id: string) {
    await api.post(`/api/encounters/notes/${id}/reject`, { reason: 'Needs revision' });
    loadNotes();
  }
  async function saveEdit() {
    if (!current) return;
    await api.patch(`/api/encounters/notes/${current.id}`, { content: current.content });
  }
  return (
    <div>
      <h1 className="text-3xl font-bold mb-4">Encounter Documentation</h1>
      <div className="bg-white border border-[var(--cv-border)] rounded-lg p-4 mb-4">
        <div className="flex gap-2 mb-2">
          <input className="border border-[var(--cv-border)] rounded-md px-3 py-2" value={pid} onChange={e => setPid(e.target.value)} placeholder="Patient ID" />
        </div>
        <textarea className="w-full border border-[var(--cv-border)] rounded-md px-3 py-2 mb-2" rows={3} value={obs} onChange={e => setObs(e.target.value)} placeholder="Clinician observations" />
        <button onClick={draft} className="bg-[var(--cv-primary)] text-white px-4 py-2 rounded-md text-sm">Generate draft</button>
      </div>
      {current && (
        <div className="bg-white border border-[var(--cv-border)] rounded-lg p-4 mb-4">
          <p className="text-xs text-[var(--cv-warning)] mb-2">AI-generated draft. Requires review and approval by a qualified healthcare professional.</p>
          {Object.keys(current.content).map(k => (
            <div key={k} className="mb-2">
              <label className="block text-xs font-medium mb-1">{k}</label>
              {k === 'disclaimer' ? (
                <input className="w-full border border-[var(--cv-border)] rounded-md px-2 py-1 text-sm" value={current.content[k]} readOnly />
              ) : (
                <textarea className="w-full border border-[var(--cv-border)] rounded-md px-2 py-1 text-sm" rows={2} value={current.content[k]} onChange={e => setCurrent({ ...current, content: { ...current.content, [k]: e.target.value } })} />
              )}
            </div>
          ))}
          <div className="flex gap-2 mt-2">
            <button onClick={saveEdit} className="bg-[var(--cv-primary)] text-white px-3 py-1.5 rounded-md text-sm">Save draft</button>
            <button onClick={() => approve(current.id)} className="bg-[var(--cv-success)] text-white px-3 py-1.5 rounded-md text-sm">Approve</button>
            <button onClick={() => reject(current.id)} className="bg-[var(--cv-danger)] text-white px-3 py-1.5 rounded-md text-sm">Reject</button>
          </div>
        </div>
      )}
      <div className="bg-white border border-[var(--cv-border)] rounded-lg p-4">
        <h2 className="text-lg font-semibold mb-2">Saved notes</h2>
        {notes.map(n => (
          <div key={n.id} className="text-sm py-2 border-b border-[var(--cv-border)]">
            {n.id} — {n.patient_id} — {n.status} ({new Date(n.created_at).toLocaleString()})
          </div>
        ))}
      </div>
    </div>
  );
}
