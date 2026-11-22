import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import FollowUpModal from '../components/FollowUpModal';

export default function Patients() {
  const [q, setQ] = useState('');
  const [list, setList] = useState<any[]>([]);
  const [modalPid, setModalPid] = useState<string | null>(null);
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
            <tr><th className="p-3 text-left">ID</th><th className="p-3 text-left">Name</th><th className="p-3 text-left">Sex</th><th className="p-3 text-left">Program</th><th className="p-3 text-left">Status</th><th className="p-3 text-left">Actions</th></tr>
          </thead>
          <tbody>
            {list.map(p => (
              <tr key={p.id} className="border-t border-[var(--cv-border)] hover:bg-[var(--cv-surface-hover)]">
                <td className="p-3 cursor-pointer" onClick={() => nav(`/patients/${p.id}`)}>{p.id}</td>
                <td className="p-3 cursor-pointer" onClick={() => nav(`/patients/${p.id}`)}>{p.name}</td>
                <td className="p-3">{p.sex}</td><td className="p-3">{p.program}</td><td className="p-3">{p.status}</td>
                <td className="p-3"><button onClick={() => setModalPid(p.id)} className="text-xs px-2 py-1 border border-[var(--cv-border)] rounded">Follow-up</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {modalPid && <FollowUpModal open={true} onClose={() => setModalPid(null)} onCreated={() => {}} presetPatient={modalPid} />}
    </div>
  );
}
