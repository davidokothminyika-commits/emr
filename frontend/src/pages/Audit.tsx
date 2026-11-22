import { useEffect, useState } from 'react';
import api from '../api';

export default function Audit() {
  const [logs, setLogs] = useState<any[]>([]);
  useEffect(() => { api.get('/api/audit').then(r => setLogs(r.data)); }, []);
  return (
    <div>
      <h1 className="text-3xl font-bold mb-4">Audit Log</h1>
      <div className="bg-white border border-[var(--cv-border)] rounded-lg overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-[var(--cv-surface-muted)]">
            <tr><th className="p-3 text-left">Time</th><th className="p-3 text-left">User</th><th className="p-3 text-left">Action</th><th className="p-3 text-left">Resource</th><th className="p-3 text-left">ID</th></tr>
          </thead>
          <tbody>
            {logs.map(l => (
              <tr key={l.id} className="border-t border-[var(--cv-border)]">
                <td className="p-3">{l.timestamp}</td><td className="p-3">{l.user_id}</td><td className="p-3">{l.action}</td><td className="p-3">{l.resource_type}</td><td className="p-3">{l.resource_id}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
