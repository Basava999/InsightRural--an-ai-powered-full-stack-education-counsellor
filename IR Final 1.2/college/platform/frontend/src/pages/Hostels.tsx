import { useState } from 'react';
import api, { StudentProfile } from '../services/api';

export default function Hostels() {
  const [profile] = useState<StudentProfile>({ rank: 5000, category: 'GM', branch: 'CSE', hostel_required: true });
  const [hostels, setHostels] = useState<any[]>([]);

  const load = async () => {
    const { data } = await api.hostels(profile);
    setHostels(data.hostels || []);
  };

  return (
    <div>
      <h2 style={{ marginBottom: '1.5rem' }}>Hostel Information</h2>
      <p style={{ color: 'var(--muted)', marginBottom: '1rem' }}>
        Hostel details are shown only for recommended colleges — never invented.
      </p>
      <button onClick={load} style={{ background: 'var(--primary)', color: '#fff', border: 'none', padding: '8px 24px', borderRadius: 8, marginBottom: '1.5rem' }}>
        Load Hostels for Recommendations
      </button>
      {hostels.map((h, i) => (
        <div key={i} className="card" style={{ marginBottom: '1rem' }}>
          <strong>{h.college_name || h.college}</strong>
          <p style={{ fontSize: '0.875rem', color: 'var(--muted)' }}>
            {h.location || ''} · Verified: {h.verified ? 'Yes' : 'No'}
          </p>
        </div>
      ))}
    </div>
  );
}
