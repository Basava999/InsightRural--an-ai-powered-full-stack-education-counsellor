export default function Admin() {
  return (
    <div>
      <h2 style={{ marginBottom: '1.5rem' }}>Admin Panel</h2>
      <div className="card">
        <p>Admin features: ML retraining, audit logs, data pipeline status.</p>
        <p style={{ color: 'var(--muted)', marginTop: '0.5rem' }}>Requires admin JWT authentication.</p>
      </div>
    </div>
  );
}
