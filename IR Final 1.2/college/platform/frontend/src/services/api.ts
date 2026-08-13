import axios from 'axios';

const API = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api/v1',
  headers: { 'Content-Type': 'application/json' },
});

export interface StudentProfile {
  rank: number;
  category: string;
  branch: string;
  city?: string;
  district?: string;
  hostel_required?: boolean;
  budget?: number;
  rural?: boolean;
  kannada_medium?: boolean;
  hk_371j?: boolean;
  college_type?: string;
}

export const api = {
  health: () => API.get('/../health'),
  recommend: (profile: StudentProfile) => API.post('/predict/recommend', profile),
  preferenceOrder: (profile: StudentProfile) => API.post('/predict/preference-order', profile),
  compare: (profile: StudentProfile, collegeIds: string[]) =>
    API.post('/predict/compare', { ...profile, college_ids: collegeIds }),
  strategy: (profile: StudentProfile) => API.post('/predict/strategy', profile),
  searchColleges: (params: Record<string, string | number>) => API.get('/colleges/search', { params }),
  getCollege: (id: string) => API.get(`/colleges/${id}`),
  cutoffTrends: (id: string, branch: string, category: string) =>
    API.get(`/colleges/${id}/cutoff-trends`, { params: { branch, category } }),
  chat: (message: string, profile?: StudentProfile) =>
    API.post('/chat/', { message, profile }),
  hostels: (profile: StudentProfile) => API.post('/hostels/for-recommendations', profile),
  scholarships: (params: Record<string, string | number>) => API.get('/scholarships/eligible', { params }),
  analytics: () => API.get('/analytics/overview'),
};

export default api;
