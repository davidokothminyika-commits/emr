import { useState } from 'react';
import PatientProfile from './PatientProfile';

export default function Summaries() {
  const [pid, setPid] = useState('P-0001');
  const [show, setShow] = useState(false);
  return (
    <div>
      <h1 className="text-3xl font-bold mb-4">Clinical Summaries</h1>
      <div className="flex gap-2 mb-4">
        <input className="border border-[var(--cv-border)] rounded-md px-3 py-2" value={pid} onChange={e => setPid(e.target.value)} placeholder="Patient ID" />
        <button onClick={() => setShow(true)} className="bg-[var(--cv-primary)] text-white px-4 py-2 rounded-md text-sm">Open patient summary</button>
      </div>
      {show && <PatientProfile />}
    </div>
  );
}
