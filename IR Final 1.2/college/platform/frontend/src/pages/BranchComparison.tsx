export default function BranchComparison() {
  return (
    <div>
      <h2 style={{ marginBottom: '1.5rem' }}>Branch Comparison</h2>
      <div className="card">
        <p>Compare branches by cutoff trends, placements, and seat availability.</p>
        <table style={{ width: '100%', marginTop: '1rem', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '2px solid #e2e8f0' }}>
              {['Branch', 'Avg Cutoff (GM)', 'Avg Placement', 'Demand'].map(h => (
                <th key={h} style={{ textAlign: 'left', padding: '0.5rem' }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {[
              { branch: 'CSE', cutoff: 3500, placement: 8.5, demand: 'Very High' },
              { branch: 'ECE', cutoff: 8000, placement: 6.2, demand: 'High' },
              { branch: 'ISE', cutoff: 6000, placement: 7.0, demand: 'High' },
              { branch: 'ME', cutoff: 25000, placement: 4.5, demand: 'Moderate' },
              { branch: 'CIVIL', cutoff: 35000, placement: 3.8, demand: 'Moderate' },
            ].map(r => (
              <tr key={r.branch} style={{ borderBottom: '1px solid #e2e8f0' }}>
                <td style={{ padding: '0.5rem' }}>{r.branch}</td>
                <td style={{ padding: '0.5rem' }}>{r.cutoff.toLocaleString()}</td>
                <td style={{ padding: '0.5rem' }}>{r.placement} LPA</td>
                <td style={{ padding: '0.5rem' }}>{r.demand}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
