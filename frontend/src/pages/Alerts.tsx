import { useEffect, useState } from 'react';
import api from '../api';
import FollowUpModal from '../components/FollowUpModal';

export default function Alerts() {
  const [alerts, setAlerts] = useState<any[]>([]);
  const [sev, setSev] = useState('');
  const [modalAlert, setModalAlert] = useState<any>(null);
  async function load() {
    const r = await api.get('/api/alerts', { params: sev ? { severity: sev } : {} });
    setAlerts(r.data);
  }
  useEffect(() => { load(); }, []);
  async function action(id: string, act: string) {
    if (act === 'review') await api.patch(`/api/alerts/${id}/review`);
    if (act === 'dismiss') await api.patch(`/api/alerts/${id}/dismiss`, null, { params: { reason: 'Reviewed by clinician' } });
    if (act === 'reopen') await api.patch(`/api/alerts/${id}/reopen`);
    load();
  }
  return (
    <div>
      <h1 className="text-3xl font-bold mb-4">Clinical Alerts</h1>
      <div className="flex gap-2 mb-4">
        <select className="border border-[var(--cv-border)] rounded-md px-3 py-2" value={sev} onChange={e => setSev(e.target.value)}>
          <option value="">All severities</option>
          <option>Critical</option><option>High</option><option>Medium</option><option>Low</option><option>Informational</option>
        </select>
        <button onClick={load} className="bg-[var(--cv-primary)] text-white px-4 py-2 rounded-md text-sm">Filter</button>
      </div>
      <div className="space-y-3">
        {alerts.map(a => (
          <div key={a.id} className="bg-white border border-[var(--cv-border)] rounded-lg p-4">
            <div className="flex justify-between">
              <div>
                <span className={`font-semibold ${a.severity === 'Critical' ? 'text-[var(--cv-danger)]' : 'text-[var(--cv-warning)]'}`}>{a.severity}</span>
                <span className="ml-2 font-medium">{a.title}</span>
                <span className="ml-2 text-xs text-[var(--cv-text-muted)]">({a.patient_id})</span>
              </div>
              <span className="text-xs text-[var(--cv-text-muted)]">{a.status}</span>
            </div>
            <p className="text-sm mt-1">{a.reason}</p>
            <p className="text-xs text-[var(--cv-text-muted)] mt-1">Sources: {a.source_ids?.join(', ') || 'none'} • Evidence dates: {a.evidence_dates?.join(', ')}</p>
            <div className="flex gap-2 mt-2">
              <button onClick={() => action(a.id, 'review')} className="text-xs px-2 py-1 border border-[var(--cv-border)] rounded">Mark reviewed</button>
              <button onClick={() => action(a.id, 'dismiss')} className="text-xs px-2 py-1 border border-[var(--cv-border)] rounded">Dismiss</button>
              <button onClick={() => action(a.id, 'reopen')} className="text-xs px-2 py-1 border border-[var(--cv-border)] rounded">Reopen</button>
              <button onClick={() => setModalAlert(a)} className="text-xs px-2 py-1 border border-[var(--cv-border)] rounded">Create Follow-up</button>
            </div>
          </div>
        ))}
      </div>
      {modalAlert && (
        <FollowUpModal
          open={true}
          onClose={() => setModalAlert(null)}
          onCreated={() => {}}
          presetPatient={modalAlert.patient_id}
          presetTitle={modalAlert.title}
          presetDescription={modalAlert.reason}
          presetRelatedType="alert"
          presetRelatedId={modalAlert.id}
        />
      )}
    </div>
  );
}
