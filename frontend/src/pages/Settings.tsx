import { useEffect, useState } from 'react';
import api from '../api';

export default function Settings() {
  const [rules, setRules] = useState<any[]>([]);
  useEffect(() => { api.get('/api/rules').then(r => setRules(r.data)); }, []);
  async function toggle(r: any) {
    await api.patch(`/api/rules/${r.rule_id}`, { enabled: !r.enabled });
    const rr = await api.get('/api/rules');
    setRules(rr.data);
  }
  return (
    <div>
      <h1 className="text-3xl font-bold mb-4">System Settings</h1>
      <div className="bg-white border border-[var(--cv-border)] rounded-lg p-4">
        <h2 className="text-lg font-semibold mb-2">Clinical rules</h2>
        {rules.map(r => (
          <div key={r.rule_id} className="flex justify-between items-center py-2 border-b border-[var(--cv-border)]">
            <div>
              <div className="font-medium text-sm">{r.rule_id}</div>
              <div className="text-xs text-[var(--cv-text-muted)]">{r.description}</div>
            </div>
            <button onClick={() => toggle(r)} className={`text-xs px-2 py-1 rounded ${r.enabled ? 'bg-[var(--cv-success-subtle)] text-[var(--cv-success)]' : 'bg-[var(--cv-surface-muted)]'}`}>
              {r.enabled ? 'Enabled' : 'Disabled'}
            </button>
          </div>
        ))}
      </div>
      <div className="bg-white border border-[var(--cv-border)] rounded-lg p-4 mt-4">
        <h2 className="text-lg font-semibold mb-2">EMR connection</h2>
        <p className="text-sm">Active mode: synthetic (SyntheticEMRAdapter). OpenMRS adapter available but not configured.</p>
      </div>
    </div>
  );
}
