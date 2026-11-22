import { useEffect, useState } from 'react';
import api from '../api';

export default function FollowUpModal({ open, onClose, onCreated, presetPatient, presetTitle, presetDescription, presetRelatedType, presetRelatedId }: any) {
  const [patients, setPatients] = useState<any[]>([]);
  // clinicians not used
  const [pid, setPid] = useState(presetPatient || '');
  const [title, setTitle] = useState(presetTitle || '');
  const [desc, setDesc] = useState(presetDescription || '');
  const [due, setDue] = useState('');
  const [priority, setPriority] = useState('medium');
  const [clinician, setClinician] = useState('Dr. Amina Odhiambo');
  // notes not used
  const [err, setErr] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!open) return;
    api.get('/api/patients').then(r => setPatients(r.data));
  }, [open]);

  useEffect(() => { if (presetPatient) setPid(presetPatient); }, [presetPatient]);
  useEffect(() => { if (presetTitle) setTitle(presetTitle); }, [presetTitle]);
  useEffect(() => { if (presetDescription) setDesc(presetDescription); }, [presetDescription]);

  if (!open) return null;
  async function submit(e: any) {
    e.preventDefault();
    if (!pid) { setErr('Select a patient'); return; }
    if (!title && !desc) { setErr('Title or description required'); return; }
    if (!due) { setErr('Due date required'); return; }
    setSaving(true); setErr('');
    try {
      await api.post('/api/followups', {
        patient_id: pid, title, description: desc, due_date: due, priority,
        assigned_clinician: clinician, related_record_type: presetRelatedType, related_record_id: presetRelatedId,
      });
      onCreated && onCreated();
      onClose();
    } catch (e: any) {
      setErr(e.response?.data?.detail || 'Failed');
    } finally { setSaving(false); }
  }
  return (
    <div className="fixed inset-0 bg-[var(--cv-overlay)] flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-lg shadow-lg">
        <h2 className="text-xl font-semibold mb-4">New Follow-up</h2>
        <form onSubmit={submit} className="space-y-3">
          <div>
            <label className="block text-sm font-medium mb-1">Patient</label>
            <select className="w-full border border-[var(--cv-border)] rounded-md px-3 py-2" value={pid} onChange={e => setPid(e.target.value)}>
              <option value="">Select patient</option>
              {patients.map(p => <option key={p.id} value={p.id}>{p.id} - {p.name}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Title</label>
            <input className="w-full border border-[var(--cv-border)] rounded-md px-3 py-2" value={title} onChange={e => setTitle(e.target.value)} />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Description</label>
            <textarea className="w-full border border-[var(--cv-border)] rounded-md px-3 py-2" rows={3} value={desc} onChange={e => setDesc(e.target.value)} />
          </div>
          <div className="flex gap-2">
            <div className="flex-1">
              <label className="block text-sm font-medium mb-1">Due date</label>
              <input type="date" className="w-full border border-[var(--cv-border)] rounded-md px-3 py-2" value={due} onChange={e => setDue(e.target.value)} />
            </div>
            <div className="flex-1">
              <label className="block text-sm font-medium mb-1">Priority</label>
              <select className="w-full border border-[var(--cv-border)] rounded-md px-3 py-2" value={priority} onChange={e => setPriority(e.target.value)}>
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Assigned clinician</label>
            <input className="w-full border border-[var(--cv-border)] rounded-md px-3 py-2" value={clinician} onChange={e => setClinician(e.target.value)} />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Additional notes</label>
            <textarea className="w-full border border-[var(--cv-border)] rounded-md px-3 py-2" rows={2} />
          </div>
          {err && <div className="text-[var(--cv-danger)] text-sm">{err}</div>}
          <div className="flex justify-end gap-2 mt-4">
            <button type="button" onClick={onClose} className="px-4 py-2 border border-[var(--cv-border)] rounded-md text-sm">Cancel</button>
            <button type="submit" disabled={saving} className="px-4 py-2 bg-[var(--cv-primary)] text-white rounded-md text-sm disabled:opacity-50">{saving ? 'Saving...' : 'Create Follow-up'}</button>
          </div>
        </form>
      </div>
    </div>
  );
}
