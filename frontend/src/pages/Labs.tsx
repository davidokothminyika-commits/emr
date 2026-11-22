import { useEffect, useState } from 'react';
import api from '../api';

export default function Labs() {
  const [labs, setLabs] = useState<any[]>([]);
  const [pid, setPid] = useState('');
  useEffect(() => { api.get('/api/laboratory').then(r => setLabs(r.data)); }, []);
  async function filter() {
    if (pid) {
      const r = await api.get(`/api/patients/${pid}/laboratory`);
      setLabs(r.data);
    } else {
      const r = await api.get('/api/laboratory');
      setLabs(r.data);
    }
  }
  return (
    <div>
      <h1 className="text-3xl font-bold mb-4">Laboratory Intelligence</h1>
      <div className="flex gap-2 mb-4">
        <input className="border border-[var(--cv-border)] rounded-md px-3 py-2" value={pid} onChange={e => setPid(e.target.value)} placeholder="Filter by patient ID" />
        <button onClick={filter} className="bg-[var(--cv-primary)] text-white px-4 py-2 rounded-md text-sm">Apply</button>
      </div>
      <div className="bg-white border border-[var(--cv-border)] rounded-lg overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-[var(--cv-surface-muted)]">
            <tr><th className="p-3 text-left">Patient</th><th className="p-3 text-left">Test</th><th className="p-3 text-left">Result</th><th className="p-3 text-left">Unit</th><th className="p-3 text-left">Date</th><th className="p-3 text-left">Ref range</th><th className="p-3 text-left">Source</th></tr>
          </thead>
          <tbody>
            {labs.map(l => (
              <tr key={l.id} className="border-t border-[var(--cv-border)]">
                <td className="p-3">{l.patient_id}</td><td className="p-3">{l.test_name}</td><td className="p-3">{l.value}</td><td className="p-3">{l.unit}</td><td className="p-3">{l.date}</td><td className="p-3">{l.reference_range}</td><td className="p-3 text-xs text-[var(--cv-text-muted)]">{l.id}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
