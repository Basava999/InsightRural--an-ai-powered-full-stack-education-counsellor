import { useState } from 'react';
import api, { StudentProfile } from '../services/api';

export default function Chatbot() {
  const [message, setMessage] = useState('');
  const [profile] = useState<StudentProfile>({ rank: 5000, category: 'GM', branch: 'CSE', city: 'Bangalore' });
  const [messages, setMessages] = useState<{ role: string; text: string }[]>([]);
  const [loading, setLoading] = useState(false);

  const send = async () => {
    if (!message.trim()) return;
    setMessages(m => [...m, { role: 'user', text: message }]);
    setLoading(true);
    try {
      const { data } = await api.chat(message, profile);
      setMessages(m => [...m, { role: 'assistant', text: data.answer }]);
    } catch {
      setMessages(m => [...m, { role: 'assistant', text: 'Error connecting to counselling engine.' }]);
    } finally {
      setLoading(false);
      setMessage('');
    }
  };

  return (
    <div>
      <h2 style={{ marginBottom: '1.5rem' }}>Counselling Chatbot</h2>
      <p style={{ color: 'var(--muted)', marginBottom: '1rem' }}>
        Algorithm selects colleges. AI only explains the results.
      </p>
      <div className="card" style={{ minHeight: 400, display: 'flex', flexDirection: 'column' }}>
        <div style={{ flex: 1, overflowY: 'auto', marginBottom: '1rem' }}>
          {messages.map((m, i) => (
            <div key={i} style={{
              marginBottom: '0.75rem', padding: '0.75rem', borderRadius: 8,
              background: m.role === 'user' ? '#eff6ff' : '#f1f5f9',
              marginLeft: m.role === 'user' ? '2rem' : 0,
              marginRight: m.role === 'assistant' ? '2rem' : 0,
            }}>
              <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit', fontSize: '0.875rem' }}>{m.text}</pre>
            </div>
          ))}
        </div>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <input value={message} onChange={e => setMessage(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && send()}
            placeholder="Ask about colleges, cutoffs, hostels..."
            style={{ flex: 1, padding: '0.75rem', borderRadius: 8, border: '1px solid #e2e8f0' }} />
          <button onClick={send} disabled={loading} style={{
            background: 'var(--primary)', color: '#fff', border: 'none', padding: '0.75rem 1.5rem', borderRadius: 8
          }}>{loading ? '...' : 'Send'}</button>
        </div>
      </div>
    </div>
  );
}
