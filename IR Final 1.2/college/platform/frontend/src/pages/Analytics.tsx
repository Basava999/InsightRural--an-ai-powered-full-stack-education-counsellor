import { useEffect, useState } from 'react';
import api from '../services/api';

export default function Analytics() {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    api.analytics().then(r => setData(r.data)).catch(() => {});
  }, []);

  if (!data) return <p>Loading analytics...</p>;

  return (
    <div>
      <h2 style={{ marginBottom: '1.5rem' }}>Analytics Dashboard</h2>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
        <div className="card"><h3>{data.total_colleges}</h3><p style={{ color: 'var(--muted)' }}>Colleges</p></div>
        <div className="card"><h3>{data.total_scholarships}</h3><p style={{ color: 'var(--muted)' }}>Scholarships</p></div>
        <div className="card"><h3>{data.total_hostels}</h3><p style={{ color: 'var(--muted)' }}>Hostel Records</p></div>
        <div className="card"><h3>v{data.engine_version}</h3><p style={{ color: 'var(--muted)' }}>Engine Version</p></div>
      </div>
    </div>
  );
}
