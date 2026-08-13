import { Link, useLocation } from 'react-router-dom';
import { ReactNode } from 'react';

const NAV = [
  { path: '/', label: 'Home' },
  { path: '/predictor', label: 'College Predictor' },
  { path: '/explorer', label: 'College Explorer' },
  { path: '/scholarships', label: 'Scholarships' },
  { path: '/hostels', label: 'Hostels' },
  { path: '/compare', label: 'Branch Comparison' },
  { path: '/chat', label: 'Counselling Chat' },
  { path: '/analytics', label: 'Analytics' },
  { path: '/admin', label: 'Admin' },
];

export default function Layout({ children }: { children: ReactNode }) {
  const { pathname } = useLocation();
  return (
    <div>
      <header style={{ background: '#1e293b', color: '#fff', padding: '1rem 0' }}>
        <div className="container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <h1 style={{ fontSize: '1.25rem' }}>KCET Counselling Platform</h1>
          <nav style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
            {NAV.map(n => (
              <Link key={n.path} to={n.path}
                style={{ color: pathname === n.path ? '#93c5fd' : '#cbd5e1', fontSize: '0.875rem' }}>
                {n.label}
              </Link>
            ))}
          </nav>
        </div>
      </header>
      <main className="container" style={{ padding: '2rem 1.5rem' }}>{children}</main>
    </div>
  );
}
