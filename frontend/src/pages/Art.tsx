import { useEffect, useState } from 'react';
import api from '../api';

export default function Art() {
  const [pid, setPid] = useState('P-0002');
  const [timeline, setTimeline] = useState<any[]>([]);
  async function load() {
    const r = await api.get(`/api/patients/${pid}/timeline`);
    setTimeline(r.data.filter((e: any) => e.type === 'medication' || e.type === 'diagnosis'));
  }
  useEffect(() => { load(); }, []);
  return (
    <div>
      <h1 className="text-3xl font-bold mb-4">ART Treatment Timeline</h1>
      <div className="flex gap-2 mb-4">
        <input className="border border-[var(--cv-border)] rounded-md px-3 py-2" value={pid} onChange={e => setPid(e.target.value)} />
        <button onClick={load} className="bg-[var(--cv-primary)] text-white px-4 py-2 rounded-md text-sm">Load</button>
      </div>
      <div className="bg-white border border-[var(--cv-border)] rounded-lg p-4">
        <ul className="space-y-2">
          {timeline.map((e, i) => (
            <li key={i} className="text-sm border-l-2 border-[var(--cv-primary)] pl-3 py-1">
              <span className="font-medium">{e.date}</span> — {e.title} <span className="text-xs text-[var(--cv-text-muted)]">[{e.source_id}]</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
