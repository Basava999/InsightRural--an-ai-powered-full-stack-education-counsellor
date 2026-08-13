import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Home from './pages/Home';
import Predictor from './pages/Predictor';
import Explorer from './pages/Explorer';
import Scholarships from './pages/Scholarships';
import Hostels from './pages/Hostels';
import BranchComparison from './pages/BranchComparison';
import Chatbot from './pages/Chatbot';
import Analytics from './pages/Analytics';
import Admin from './pages/Admin';

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/predictor" element={<Predictor />} />
        <Route path="/explorer" element={<Explorer />} />
        <Route path="/scholarships" element={<Scholarships />} />
        <Route path="/hostels" element={<Hostels />} />
        <Route path="/compare" element={<BranchComparison />} />
        <Route path="/chat" element={<Chatbot />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/admin" element={<Admin />} />
      </Routes>
    </Layout>
  );
}
