import { useState } from 'react';
import api from '../services/api';

export default function Explorer() {
  const [query, setQuery] = useState('');
  const [city, setCity] = useState('');
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const search = async () => {
    setLoading(true);
    try {
      const { data } = await api.searchColleges({ q: query, city, limit: 20 });
      setResults(data.colleges || []);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2 style={{ marginBottom: '1.5rem' }}>College Explorer</h2>
      <div className="card" style={{ marginBottom: '1.5rem', display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
        <input placeholder="Search college name" value={query} onChange={e => setQuery(e.target.value)}
          style={{ flex: 1, minWidth: 200, padding: 8 }} />
        <input placeholder="City filter" value={city} onChange={e => setCity(e.target.value)}
          style={{ width: 150, padding: 8 }} />
        <button onClick={search} disabled={loading} style={{
          background: 'var(--primary)', color: '#fff', border: 'none', padding: '8px 24px', borderRadius: 8
        }}>{loading ? 'Searching...' : 'Search'}</button>
      </div>
      <div style={{ display: 'grid', gap: '1rem' }}>
        {results.map(c => (
          <div key={c.college_id} className="card">
            <strong>{c.name}</strong>
            <p style={{ color: 'var(--muted)', fontSize: '0.875rem' }}>
              {c.location} · {c.type} · NAAC: {c.naac_grade || 'N/A'} ·
              Avg Pkg: {c.placement_avg_lpa || 'N/A'} LPA
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
