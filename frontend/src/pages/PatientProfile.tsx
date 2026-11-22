import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import api from '../api';
import FollowUpModal from '../components/FollowUpModal';

export default function PatientProfile() {
  const { id } = useParams();
  const [hist, setHist] = useState<any>(null);
  const [summary, setSummary] = useState<any>(null);
  const [timeline, setTimeline] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [followups, setFollowups] = useState<any[]>([]);
  const [modal, setModal] = useState(false);
  const [sourceDetail, setSourceDetail] = useState<any>(null);

  async function load() {
    const h = await api.get(`/api/patients/${id}/history`);
    setHist(h.data);
    const t = await api.get(`/api/patients/${id}/timeline`);
    setTimeline(t.data);
    const a = await api.get(`/api/patients/${id}/alerts`);
    setAlerts(a.data);
    const f = await api.get(`/api/patients/${id}/followups`);
    setFollowups(f.data);
  }
  useEffect(() => { load(); }, [id]);

  async function genSummary() {
    const r = await api.post(`/api/patients/${id}/generate-summary`);
    setSummary(r.data);
  }

  function inspectSource(sid: string) {
    if (!hist) return;
    const all = [...hist.diagnoses, ...hist.medications, ...hist.allergies, ...hist.labs, ...hist.encounters];
    const found = all.find((x: any) => x.id === sid);
    setSourceDetail(found);
  }

  if (!hist) return <div>Loading...</div>;
  return (
    <div>
      <h1 className="text-3xl font-bold mb-2">{hist.patient.name}</h1>
      <p className="text-sm text-[var(--cv-text-muted)] mb-4">{hist.patient.id} • {hist.patient.sex} • {hist.patient.program} • {hist.patient.status}</p>
      <div className="flex gap-2 mb-6">
        <button onClick={genSummary} className="bg-[var(--cv-primary)] text-white px-4 py-2 rounded-md text-sm">Generate summary</button>
        <button onClick={() => setModal(true)} className="bg-[var(--cv-surface)] border border-[var(--cv-border-strong)] px-4 py-2 rounded-md text-sm">Add to Follow-up</button>
      </div>

      {summary && (
        <div className="bg-white border border-[var(--cv-border)] rounded-lg p-4 mb-6">
          <h2 className="text-lg font-semibold mb-3">Clinical Summary (draft)</h2>
          <p className="text-xs text-[var(--cv-text-muted)] mb-3">AI-generated draft. Requires review.</p>
          <ul className="space-y-2">
            {summary.content.summary?.map((s: any, i: number) => (
              <li key={i} className="text-sm border-b border-[var(--cv-border)] pb-2">
                <span className="font-medium text-[var(--cv-primary)]">[{s.category}]</span> {s.statement}
                <div className="text-xs text-[var(--cv-text-muted)] mt-1">
                  Sources: {s.source_ids?.map((sid: string) => (
                    <button key={sid} onClick={() => inspectSource(sid)} className="underline mr-2">{sid}</button>
                  ))}
                  • confidence: {s.confidence}
                </div>
              </li>
            ))}
          </ul>
          {summary.content.uncertainties?.length > 0 && <div className="mt-3 text-xs text-[var(--cv-warning)]">Uncertainties: {summary.content.uncertainties.join('; ')}</div>}
        </div>
      )}

      {sourceDetail && (
        <div className="bg-[var(--cv-surface-muted)] border border-[var(--cv-border)] rounded-lg p-4 mb-6">
          <h3 className="font-semibold mb-2">Source record</h3>
          <pre className="text-xs">{JSON.stringify(sourceDetail, null, 2)}</pre>
          <button onClick={() => setSourceDetail(null)} className="text-xs mt-2 underline">Close</button>
        </div>
      )}

      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-white border border-[var(--cv-border)] rounded-lg p-4">
          <h2 className="text-lg font-semibold mb-2">Diagnoses</h2>
          {hist.diagnoses.map((d: any) => <div key={d.id} className="text-sm py-1">{d.name} ({d.code}) — {d.date} <span className="text-xs text-[var(--cv-text-muted)]">[{d.id}]</span></div>)}
        </div>
        <div className="bg-white border border-[var(--cv-border)] rounded-lg p-4">
          <h2 className="text-lg font-semibold mb-2">Medications</h2>
          {hist.medications.map((m: any) => <div key={m.id} className="text-sm py-1">{m.name} {m.dosage} — {m.start_date}→{m.end_date || 'ongoing'} <span className="text-xs text-[var(--cv-text-muted)]">[{m.id}]</span></div>)}
        </div>
        <div className="bg-white border border-[var(--cv-border)] rounded-lg p-4">
          <h2 className="text-lg font-semibold mb-2">Allergies</h2>
          {hist.allergies.length === 0 ? <p className="text-sm text-[var(--cv-text-muted)]">None recorded.</p> : hist.allergies.map((a: any) => <div key={a.id} className="text-sm py-1">{a.allergen} ({a.reaction}) <span className="text-xs text-[var(--cv-text-muted)]">[{a.id}]</span></div>)}
        </div>
        <div className="bg-white border border-[var(--cv-border)] rounded-lg p-4">
          <h2 className="text-lg font-semibold mb-2">Laboratory</h2>
          {hist.labs.map((l: any) => <div key={l.id} className="text-sm py-1">{l.test_name}: {l.value} {l.unit} ({l.date}) <span className="text-xs text-[var(--cv-text-muted)]">[{l.id}]</span></div>)}
        </div>
      </div>

      <div className="bg-white border border-[var(--cv-border)] rounded-lg p-4 mb-6">
        <h2 className="text-lg font-semibold mb-2">Chronological timeline</h2>
        <ul className="text-sm space-y-1">
          {timeline.map((e: any, i: number) => <li key={i}>{e.date} — [{e.type}] {e.title} <span className="text-xs text-[var(--cv-text-muted)]">({e.source_id})</span></li>)}
        </ul>
      </div>

      <div className="bg-white border border-[var(--cv-border)] rounded-lg p-4 mb-6">
        <h2 className="text-lg font-semibold mb-2">Follow-ups</h2>
        {followups.length === 0 ? <p className="text-sm text-[var(--cv-text-muted)]">No follow-up tasks.</p> : followups.map((f:any) => (
          <div key={f.id} className="text-sm py-1 border-b border-[var(--cv-border)]">{f.title || f.description} — {f.status} (due {f.due_date})</div>
        ))}
      </div>
      <div className="bg-white border border-[var(--cv-border)] rounded-lg p-4">
        <h2 className="text-lg font-semibold mb-2">Alerts</h2>
        {alerts.length === 0 ? <p className="text-sm text-[var(--cv-text-muted)]">No alerts.</p> : alerts.map((a: any) => (
          <div key={a.id} className="text-sm py-2 border-b border-[var(--cv-border)]">
            <span className={`font-medium ${a.severity === 'Critical' ? 'text-[var(--cv-danger)]' : 'text-[var(--cv-warning)]'}`}>{a.severity}</span> {a.title} — {a.reason}
          </div>
        ))}
      </div>
      <FollowUpModal open={modal} onClose={() => setModal(false)} onCreated={() => { load(); }} presetPatient={id} />
    </div>
  );
}
