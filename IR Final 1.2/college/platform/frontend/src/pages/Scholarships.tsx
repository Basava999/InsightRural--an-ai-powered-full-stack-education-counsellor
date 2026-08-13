import { useState } from 'react';
import api from '../services/api';

export default function Scholarships() {
  const [category, setCategory] = useState('SC');
  const [results, setResults] = useState<any[]>([]);

  const check = async () => {
    const { data } = await api.scholarships({ category });
    setResults(data.scholarships || []);
  };

  return (
    <div>
      <h2 style={{ marginBottom: '1.5rem' }}>Scholarship Eligibility Checker</h2>
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <select value={category} onChange={e => setCategory(e.target.value)} style={{ padding: 8, marginRight: 8 }}>
          {['GM','OBC','SC','ST'].map(c => <option key={c}>{c}</option>)}
        </select>
        <button onClick={check} style={{ background: 'var(--primary)', color: '#fff', border: 'none', padding: '8px 24px', borderRadius: 8 }}>
          Check Eligibility
        </button>
      </div>
      {results.map((s, i) => (
        <div key={i} className="card" style={{ marginBottom: '1rem' }}>
          <strong>{s.name || s.title}</strong>
          <p style={{ color: 'var(--muted)', fontSize: '0.875rem' }}>{s.provider || s.description}</p>
        </div>
      ))}
    </div>
  );
}
