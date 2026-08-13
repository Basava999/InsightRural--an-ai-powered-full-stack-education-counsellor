import { useState } from 'react';
import api, { StudentProfile } from '../services/api';

interface Recommendation {
  college_name: string;
  location: string;
  branch: string;
  admission_probability: number;
  tier: string;
  cutoff_rank: number;
  annual_fee?: number;
  explanation: string[];
}

function TierList({ title, items, badgeClass }: { title: string; items: Recommendation[]; badgeClass: string }) {
  if (!items?.length) return null;
  return (
    <div className="card" style={{ marginBottom: '1.5rem' }}>
      <h3 style={{ marginBottom: '1rem' }}>{title} ({items.length})</h3>
      {items.map((r, i) => (
        <div key={i} style={{ borderBottom: '1px solid #e2e8f0', padding: '1rem 0' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <strong>{r.college_name}</strong>
            <span className={badgeClass}>{r.tier}</span>
          </div>
          <p style={{ color: 'var(--muted)', fontSize: '0.875rem' }}>
            {r.location} · {r.branch} · Cutoff: {r.cutoff_rank} · {r.admission_probability}% probability
            {r.annual_fee ? ` · ₹${r.annual_fee.toLocaleString()}/yr` : ''}
          </p>
          {r.explanation?.[0] && <p style={{ fontSize: '0.8rem', marginTop: 4 }}>{r.explanation[0]}</p>}
        </div>
      ))}
    </div>
  );
}

export default function Predictor() {
  const [profile, setProfile] = useState<StudentProfile>({
    rank: 5000, category: 'GM', branch: 'CSE', city: '', budget: undefined, hostel_required: false,
  });
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const payload = { ...profile };
      if (!payload.city) delete payload.city;
      if (!payload.budget) delete payload.budget;
      const { data } = await api.recommend(payload);
      setResults(data);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to get recommendations');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2 style={{ marginBottom: '1.5rem' }}>College Predictor</h2>
      <form onSubmit={handleSubmit} className="card" style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
          <label>KCET Rank<input type="number" value={profile.rank}
            onChange={e => setProfile({ ...profile, rank: +e.target.value })} required style={{ width: '100%', padding: 8, marginTop: 4 }} /></label>
          <label>Branch<select value={profile.branch} onChange={e => setProfile({ ...profile, branch: e.target.value })}
            style={{ width: '100%', padding: 8, marginTop: 4 }}>
            {['CSE','ECE','ISE','EEE','ME','CIVIL','AI','DS'].map(b => <option key={b}>{b}</option>)}
          </select></label>
          <label>Category<select value={profile.category} onChange={e => setProfile({ ...profile, category: e.target.value })}
            style={{ width: '100%', padding: 8, marginTop: 4 }}>
            {['GM','OBC','SC','ST'].map(c => <option key={c}>{c}</option>)}
          </select></label>
          <label>City (hard filter)<input value={profile.city || ''} placeholder="e.g. Bangalore"
            onChange={e => setProfile({ ...profile, city: e.target.value })} style={{ width: '100%', padding: 8, marginTop: 4 }} /></label>
          <label>Budget (₹/yr)<input type="number" value={profile.budget || ''} placeholder="Max annual fee"
            onChange={e => setProfile({ ...profile, budget: e.target.value ? +e.target.value : undefined })}
            style={{ width: '100%', padding: 8, marginTop: 4 }} /></label>
          <label style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 24 }}>
            <input type="checkbox" checked={profile.hostel_required}
              onChange={e => setProfile({ ...profile, hostel_required: e.target.checked })} />
            Hostel required
          </label>
        </div>
        <button type="submit" disabled={loading} style={{
          marginTop: '1.5rem', background: 'var(--primary)', color: '#fff',
          border: 'none', padding: '0.75rem 2rem', borderRadius: 8, cursor: 'pointer'
        }}>{loading ? 'Analyzing...' : 'Get Recommendations'}</button>
      </form>

      {error && <p style={{ color: 'var(--ambitious)' }}>{error}</p>}

      {results && (
        <>
          <p style={{ marginBottom: '1rem', color: 'var(--muted)' }}>
            Confidence: {(results.confidence * 100).toFixed(0)}% ·
            {results.total_after_filters} colleges match all constraints ·
            Engine v{results.engine_version}
          </p>
          <TierList title="🟢 SAFE" items={results.safe} badgeClass="badge-safe" />
          <TierList title="🟡 MODERATE" items={results.moderate} badgeClass="badge-moderate" />
          <TierList title="🔴 AMBITIOUS" items={results.ambitious} badgeClass="badge-ambitious" />
        </>
      )}
    </div>
  );
}
