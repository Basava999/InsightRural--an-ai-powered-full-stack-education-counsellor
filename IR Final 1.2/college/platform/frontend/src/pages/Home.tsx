import { Link } from 'react-router-dom';

export default function Home() {
  return (
    <div>
      <section className="card" style={{ marginBottom: '2rem', textAlign: 'center', padding: '3rem' }}>
        <h2 style={{ fontSize: '2rem', marginBottom: '1rem' }}>AI-Powered KCET Counselling Assistant</h2>
        <p style={{ color: 'var(--muted)', maxWidth: 600, margin: '0 auto 2rem' }}>
          Deterministic college recommendations based on official KEA cutoff data.
          The algorithm selects colleges — AI only explains why.
        </p>
        <Link to="/predictor" style={{
          background: 'var(--primary)', color: '#fff', padding: '0.75rem 2rem',
          borderRadius: 8, display: 'inline-block'
        }}>
          Get Recommendations
        </Link>
      </section>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem' }}>
        {[
          { title: 'College Predictor', desc: 'SAFE / MODERATE / AMBITIOUS tiers', path: '/predictor' },
          { title: 'College Explorer', desc: 'Search 200+ Karnataka colleges', path: '/explorer' },
          { title: 'Scholarships', desc: 'Eligibility checker', path: '/scholarships' },
          { title: 'Counselling Chat', desc: 'Ask questions, get verified answers', path: '/chat' },
        ].map(f => (
          <Link key={f.path} to={f.path} className="card" style={{ display: 'block' }}>
            <h3 style={{ marginBottom: '0.5rem' }}>{f.title}</h3>
            <p style={{ color: 'var(--muted)', fontSize: '0.875rem' }}>{f.desc}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
