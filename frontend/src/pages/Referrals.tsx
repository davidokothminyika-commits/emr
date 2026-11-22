import { useEffect, useState } from 'react';
import api from '../api';

export default function Referrals() {
  const [pid, setPid] = useState('P-0001');
  const [reason, setReason] = useState('');
  const [dest, setDest] = useState('');
  const [refs, setRefs] = useState<any[]>([]);
  const [current, setCurrent] = useState<any>(null);
  async function load() { const r = await api.get('/api/referrals'); setRefs(r.data); }
  useEffect(() => { load(); }, []);
  async function gen() {
    const r = await api.post('/api/referrals/generate', { patient_id: pid, reason, destination: dest });
    setCurrent(r.data);
    load();
  }
  return (
    <div>
      <h1 className="text-3xl font-bold mb-4">Referrals</h1>
      <div className="bg-white border border-[var(--cv-border)] rounded-lg p-4 mb-4">
        <div className="flex gap-2 flex-wrap mb-2">
          <input className="border border-[var(--cv-border)] rounded-md px-3 py-2" value={pid} onChange={e => setPid(e.target.value)} placeholder="Patient ID" />
          <input className="border border-[var(--cv-border)] rounded-md px-3 py-2 flex-1" value={reason} onChange={e => setReason(e.target.value)} placeholder="Referral reason" />
          <input className="border border-[var(--cv-border)] rounded-md px-3 py-2" value={dest} onChange={e => setDest(e.target.value)} placeholder="Destination" />
          <button onClick={gen} className="bg-[var(--cv-primary)] text-white px-4 py-2 rounded-md text-sm">Generate</button>
        </div>
      </div>
      {current && (
        <div className="bg-white border border-[var(--cv-border)] rounded-lg p-4 mb-4">
          <pre className="text-xs overflow-auto">{JSON.stringify(current.content, null, 2)}</pre>
        </div>
      )}
      <div className="bg-white border border-[var(--cv-border)] rounded-lg p-4">
        <h2 className="text-lg font-semibold mb-2">Referrals</h2>
        {refs.map(r => <div key={r.id} className="text-sm py-1">{r.id} — {r.patient_id} — {r.status}</div>)}
      </div>
    </div>
  );
}
