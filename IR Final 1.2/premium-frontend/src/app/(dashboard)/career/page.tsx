"use client";

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Compass, Briefcase, TrendingUp, Building2, AlertCircle, ArrowRight, X } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function CareerSimulatorPage() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  
  // Form State
  const [interests, setInterests] = useState('');
  const [branch, setBranch] = useState('CSE');
  const [skillInput, setSkillInput] = useState('');
  const [skills, setSkills] = useState<string[]>([]);

  const handleAddSkill = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && skillInput.trim()) {
      e.preventDefault();
      if (!skills.includes(skillInput.trim())) {
        setSkills([...skills, skillInput.trim()]);
      }
      setSkillInput('');
    }
  };

  const removeSkill = (sk: string) => {
    setSkills(skills.filter(s => s !== sk));
  };

  const handleSimulate = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const res = await fetch('http://127.0.0.1:8000/api/career/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          interests,
          skills,
          proposed_branch: branch
        })
      });
      
      const data = await res.json();
      if (data.success) {
        setResult(data);
      }
    } catch (err) {
      console.error(err);
      alert('Failed to connect to ML Engine');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 pb-12">
      {/* Header */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-3xl"
      >
        <div className="inline-flex items-center justify-center p-3 bg-purple-500/10 rounded-2xl mb-4 border border-purple-500/20">
          <Briefcase className="w-8 h-8 text-purple-400" />
        </div>
        <h1 className="text-4xl lg:text-5xl font-extrabold tracking-tight mb-4">
          Future <span className="premium-gradient-text" style={{ backgroundImage: 'linear-gradient(to right, #a855f7, #ec4899)' }}>Career Simulator</span>
        </h1>
        <p className="text-white/60 text-lg">
          Don't pick a branch just because your friends are. Find your true compatibility score and see 5-year data-driven salary projections.
        </p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* INPUT FORM */}
        <motion.div 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="lg:col-span-4"
        >
          <form onSubmit={handleSimulate} className="glass-panel rounded-3xl p-6 relative overflow-hidden sticky top-8">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-purple-500 to-pink-500" />
            <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
              <Compass className="w-5 h-5 text-purple-400" />
              Your Profile
            </h2>
            
            <div className="space-y-5">
              <div>
                <label className="block text-xs font-semibold text-white/60 mb-2 uppercase tracking-wider">What are your interests?</label>
                <textarea 
                  required 
                  rows={3}
                  placeholder="e.g., I like building computers, playing video games, and math..." 
                  value={interests} 
                  onChange={(e) => setInterests(e.target.value)} 
                  className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white placeholder:text-white/30 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all resize-none" 
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-white/60 mb-2 uppercase tracking-wider">Target Branch</label>
                <select value={branch} onChange={(e) => setBranch(e.target.value)} className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all appearance-none">
                  {['CSE', 'ECE', 'ISE', 'MECH', 'CIVIL', 'AI'].map(c => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>
              
              <div>
                <label className="block text-xs font-semibold text-white/60 mb-2 uppercase tracking-wider">Specific Skills (Press Enter)</label>
                <input 
                  type="text" 
                  placeholder="e.g., Python, Arduino, AutoCAD" 
                  value={skillInput} 
                  onChange={(e) => setSkillInput(e.target.value)}
                  onKeyDown={handleAddSkill}
                  className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white placeholder:text-white/30 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all" 
                />
                {skills.length > 0 && (
                  <div className="flex flex-wrap gap-2 mt-3">
                    {skills.map(sk => (
                      <span key={sk} className="bg-purple-500/20 text-purple-300 px-3 py-1 rounded-full text-xs font-medium flex items-center gap-1 border border-purple-500/30">
                        {sk}
                        <button type="button" onClick={() => removeSkill(sk)} className="hover:text-white transition-colors">
                          <X className="w-3 h-3" />
                        </button>
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>

            <button 
              type="submit"
              disabled={loading || !interests}
              className="w-full mt-8 py-4 rounded-xl bg-purple-500 text-white font-bold hover:bg-purple-400 transition-all active:scale-95 flex justify-center items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-[0_0_20px_rgba(168,85,247,0.4)]"
            >
              {loading ? (
                <>
                  <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1, ease: "linear" }}>
                    <Compass className="w-5 h-5" />
                  </motion.div>
                  Simulating Future...
                </>
              ) : (
                "Run Simulator"
              )}
            </button>
          </form>
        </motion.div>

        {/* RESULTS GRID */}
        <div className="lg:col-span-8">
          <AnimatePresence mode="wait">
            {!loading && !result && (
              <motion.div 
                initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                className="h-full min-h-[400px] border-2 border-dashed border-white/10 rounded-3xl flex flex-col items-center justify-center text-center p-8 bg-black/20"
              >
                <Compass className="w-16 h-16 text-white/20 mb-4" />
                <h3 className="text-xl font-bold text-white/60 mb-2">Awaiting Parameters</h3>
                <p className="text-white/40 max-w-sm">Enter your interests and targeted branch to see your projected career outcomes.</p>
              </motion.div>
            )}

            {loading && (
              <motion.div 
                initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                className="h-full min-h-[400px] flex items-center justify-center"
              >
                <div className="flex flex-col items-center gap-4 text-purple-400">
                  <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1.5, ease: "linear" }} className="w-16 h-16 border-4 border-purple-500/30 border-t-purple-500 rounded-full" />
                  <p className="font-medium animate-pulse">Running Neural Projections...</p>
                </div>
              </motion.div>
            )}

            {!loading && result && (
              <motion.div 
                initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                className="space-y-6"
              >
                {/* Score Card */}
                <div className="glass-card rounded-3xl p-8 relative overflow-hidden border border-white/10">
                  <div className="absolute right-0 top-0 w-64 h-64 bg-purple-500/10 blur-[100px] rounded-full pointer-events-none" />
                  
                  <div className="flex flex-col md:flex-row items-center justify-between gap-8">
                    <div>
                      <h2 className="text-2xl font-bold text-white mb-2">Branch Compatibility</h2>
                      <p className="text-white/60 max-w-md">
                        Based on your expressed interests and skills, here is how well you match with {result.branch}.
                      </p>
                      
                      {result.compatibility_score < 60 && (
                        <div className="mt-4 p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl flex items-start gap-3">
                          <AlertCircle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
                          <div>
                            <p className="text-sm font-semibold text-rose-300 mb-1">Low Match Warning</p>
                            <p className="text-xs text-rose-200/70">Your interests might not align well with this field. Consider looking into: <span className="font-bold text-white">{result.alternatives.join(", ")}</span>.</p>
                          </div>
                        </div>
                      )}
                    </div>
                    
                    <div className="relative w-32 h-32 flex items-center justify-center shrink-0">
                      <svg className="w-full h-full transform -rotate-90">
                        <circle cx="64" cy="64" r="56" className="stroke-white/10" strokeWidth="12" fill="none" />
                        <motion.circle 
                          cx="64" cy="64" r="56" 
                          className={result.compatibility_score >= 75 ? "stroke-emerald-400" : result.compatibility_score >= 60 ? "stroke-amber-400" : "stroke-rose-400"} 
                          strokeWidth="12" fill="none" 
                          strokeLinecap="round"
                          initial={{ strokeDasharray: "0 351.8" }}
                          animate={{ strokeDasharray: `${(result.compatibility_score / 100) * 351.8} 351.8` }}
                          transition={{ duration: 1.5, ease: "easeOut" }}
                        />
                      </svg>
                      <div className="absolute inset-0 flex flex-col items-center justify-center">
                        <span className="text-3xl font-bold text-white">{result.compatibility_score}%</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Salary Chart */}
                <div className="glass-card rounded-3xl p-8 border border-white/10">
                  <h3 className="text-xl font-bold text-white flex items-center gap-2 mb-6">
                    <TrendingUp className="w-5 h-5 text-emerald-400" />
                    5-Year Salary Projection (LPA)
                  </h3>
                  <div className="h-[300px] w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={result.salary_projection} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                        <defs>
                          <linearGradient id="colorMedian" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#a855f7" stopOpacity={0.3}/>
                            <stop offset="95%" stopColor="#a855f7" stopOpacity={0}/>
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
                        <XAxis dataKey="year" stroke="#ffffff60" tick={{fill: '#ffffff60'}} axisLine={false} tickLine={false} />
                        <YAxis stroke="#ffffff60" tick={{fill: '#ffffff60'}} axisLine={false} tickLine={false} tickFormatter={(val) => `₹${val}L`} />
                        <Tooltip 
                          contentStyle={{ backgroundColor: '#000000dd', borderColor: '#ffffff20', borderRadius: '12px' }}
                          itemStyle={{ color: '#fff' }}
                        />
                        <Area type="monotone" dataKey="median" name="Expected (Median)" stroke="#a855f7" strokeWidth={3} fillOpacity={1} fill="url(#colorMedian)" />
                        <Area type="monotone" dataKey="high" name="Top 10% Scenario" stroke="#10b981" strokeWidth={2} fillOpacity={0} strokeDasharray="5 5" />
                        <Area type="monotone" dataKey="low" name="Bottom 20% Scenario" stroke="#f43f5e" strokeWidth={2} fillOpacity={0} strokeDasharray="5 5" />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Top Recruiters */}
                <div className="glass-card rounded-3xl p-8 border border-white/10">
                  <h3 className="text-xl font-bold text-white flex items-center gap-2 mb-6">
                    <Building2 className="w-5 h-5 text-blue-400" />
                    Top Industry Recruiters for {result.branch}
                  </h3>
                  <div className="flex flex-wrap gap-3">
                    {result.top_recruiters.map((recruiter: string, idx: number) => (
                      <motion.div 
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: 0.5 + (idx * 0.1) }}
                        key={recruiter}
                        className="px-4 py-2 bg-blue-500/10 border border-blue-500/20 text-blue-100 rounded-lg text-sm font-medium"
                      >
                        {recruiter}
                      </motion.div>
                    ))}
                  </div>
                </div>

              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
