import { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import api from '../api';

export default function Patients() {
  const [params] = useSearchParams();
  const [q, setQ] = useState(params.get('q') || '');
  const [list, setList] = useState<any[]>([]);
  const nav = useNavigate();
  async function load() {
    const r = await api.get('/api/patients', { params: { q } });
    setList(r.data);
  }
  useEffect(() => { load(); }, []);
  return (
    <div>
      <h1 className="text-3xl font-bold mb-4">Patients</h1>
      <div className="flex gap-2 mb-4">
        <input className="border border-[var(--cv-border)] rounded-md px-3 py-2 flex-1" value={q} onChange={e => setQ(e.target.value)} placeholder="Search by name or ID" />
        <button onClick={load} className="bg-[var(--cv-primary)] text-white px-4 py-2 rounded-md">Search</button>
      </div>
      <div className="bg-white border border-[var(--cv-border)] rounded-lg overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-[var(--cv-surface-muted)]">
            <tr><th className="p-3 text-left">ID</th><th className="p-3 text-left">Name</th><th className="p-3 text-left">Sex</th><th className="p-3 text-left">Program</th><th className="p-3 text-left">Status</th></tr>
          </thead>
          <tbody>
            {list.map(p => (
              <tr key={p.id} onClick={() => nav(`/patients/${p.id}`)} className="border-t border-[var(--cv-border)] hover:bg-[var(--cv-surface-hover)] cursor-pointer">
                <td className="p-3">{p.id}</td><td className="p-3">{p.name}</td><td className="p-3">{p.sex}</td><td className="p-3">{p.program}</td><td className="p-3">{p.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
