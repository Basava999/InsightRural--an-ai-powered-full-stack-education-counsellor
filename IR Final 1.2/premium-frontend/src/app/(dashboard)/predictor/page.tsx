"use client";

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Compass, Search, MapPin, Building, GraduationCap, ArrowRight, ShieldCheck, AlertTriangle, Zap } from 'lucide-react';

export default function PredictorPage() {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any[]>([]);
  
  // Form State
  const [rank, setRank] = useState('');
  const [category, setCategory] = useState('GM');
  const [branch, setBranch] = useState('CSE');
  const [budget, setBudget] = useState('');
  const [preferredState, setPreferredState] = useState('Karnataka');

  const handlePredict = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const res = await fetch('http://127.0.0.1:8000/api/data/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          kcet_rank: parseInt(rank) || 0,
          category,
          preferred_branches: [branch],
          budget: budget ? parseInt(budget) : null,
          preferred_state: preferredState
        })
      });
      
      const data = await res.json();
      if (data.success && data.predictions) {
        setResults(data.predictions);
      } else {
        setResults([]);
      }
    } catch (err) {
      console.error(err);
      alert('Failed to connect to ML Engine');
    } finally {
      setLoading(false);
    }
  };

  const getProbabilityColor = (prob: number) => {
    if (prob >= 80) return 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20';
    if (prob >= 45) return 'text-amber-400 bg-amber-400/10 border-amber-400/20';
    return 'text-rose-400 bg-rose-400/10 border-rose-400/20';
  };

  const getProbabilityIcon = (prob: number) => {
    if (prob >= 80) return <ShieldCheck className="w-5 h-5" />;
    if (prob >= 45) return <AlertTriangle className="w-5 h-5" />;
    return <Zap className="w-5 h-5" />;
  };

  return (
    <div className="space-y-8 pb-12">
      {/* Header */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-3xl"
      >
        <div className="inline-flex items-center justify-center p-3 bg-blue-500/10 rounded-2xl mb-4 border border-blue-500/20">
          <Compass className="w-8 h-8 text-blue-400" />
        </div>
        <h1 className="text-4xl lg:text-5xl font-extrabold tracking-tight mb-4">
          Hybrid ML <span className="premium-gradient-text">College Predictor</span>
        </h1>
        <p className="text-white/60 text-lg">
          Discover your chances with our 6-dimensional ML algorithm factoring historical cutoffs, category mapping, placement scores, and financial fit.
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
          <form onSubmit={handlePredict} className="glass-panel rounded-3xl p-6 relative overflow-hidden sticky top-8">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 to-indigo-500" />
            <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
              <Search className="w-5 h-5 text-blue-400" />
              Target Parameters
            </h2>
            
            <div className="space-y-5">
              <div>
                <label className="block text-xs font-semibold text-white/60 mb-2 uppercase tracking-wider">KCET Rank</label>
                <input required type="number" placeholder="Enter your rank" value={rank} onChange={(e) => setRank(e.target.value)} className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white placeholder:text-white/30 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all" />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-white/60 mb-2 uppercase tracking-wider">Category</label>
                  <select value={category} onChange={(e) => setCategory(e.target.value)} className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all appearance-none">
                    {['GM', 'OBC', 'SC', 'ST', '2A', '2B', '3A', '3B'].map(c => <option key={c} value={c}>{c}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-white/60 mb-2 uppercase tracking-wider">Branch</label>
                  <select value={branch} onChange={(e) => setBranch(e.target.value)} className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all appearance-none">
                    {['CSE', 'ECE', 'ISE', 'MECH', 'CIVIL', 'AI'].map(c => <option key={c} value={c}>{c}</option>)}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-white/60 mb-2 uppercase tracking-wider">Annual Budget (₹)</label>
                <input type="number" placeholder="Optional max fee" value={budget} onChange={(e) => setBudget(e.target.value)} className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white placeholder:text-white/30 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all" />
              </div>
            </div>

            <button 
              type="submit"
              disabled={loading || !rank}
              className="w-full mt-8 py-4 rounded-xl bg-blue-500 text-white font-bold hover:bg-blue-400 transition-all active:scale-95 flex justify-center items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-[0_0_20px_rgba(59,130,246,0.4)]"
            >
              {loading ? (
                <>
                  <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1, ease: "linear" }}>
                    <Compass className="w-5 h-5" />
                  </motion.div>
                  Running Hybrid Models...
                </>
              ) : (
                "Predict Top Colleges"
              )}
            </button>
          </form>
        </motion.div>

        {/* RESULTS GRID */}
        <div className="lg:col-span-8">
          <AnimatePresence mode="wait">
            {!loading && results.length === 0 && (
              <motion.div 
                initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                className="h-full min-h-[400px] border-2 border-dashed border-white/10 rounded-3xl flex flex-col items-center justify-center text-center p-8 bg-black/20"
              >
                <Compass className="w-16 h-16 text-white/20 mb-4" />
                <h3 className="text-xl font-bold text-white/60 mb-2">Awaiting Parameters</h3>
                <p className="text-white/40 max-w-sm">Enter your rank and target branch to see your unified admission probabilities.</p>
              </motion.div>
            )}

            {loading && (
              <motion.div 
                initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                className="h-full min-h-[400px] flex items-center justify-center"
              >
                <div className="flex flex-col items-center gap-4 text-blue-400">
                  <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1.5, ease: "linear" }} className="w-16 h-16 border-4 border-blue-500/30 border-t-blue-500 rounded-full" />
                  <p className="font-medium animate-pulse">Computing 6-Dimensional Recommendation Scores...</p>
                </div>
              </motion.div>
            )}

            {!loading && results.length > 0 && (
              <motion.div 
                initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                className="space-y-4"
              >
                <h2 className="text-xl font-bold mb-6 text-white">Top Recommendations ({results.length})</h2>
                {results.map((col, idx) => (
                  <motion.div
                    key={col.college_id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.05 }}
                    className="glass-card rounded-2xl p-6 relative overflow-hidden"
                  >
                    {/* Animated Probability Bar Background */}
                    <div className="absolute bottom-0 left-0 h-1 bg-white/5 w-full">
                      <motion.div 
                        initial={{ width: 0 }}
                        animate={{ width: `${col.probability}%` }}
                        transition={{ duration: 1, delay: 0.2 + idx * 0.05 }}
                        className={`h-full ${
                          col.probability >= 80 ? 'bg-emerald-400' : 
                          col.probability >= 45 ? 'bg-amber-400' : 'bg-rose-400'
                        }`}
                      />
                    </div>

                    <div className="flex flex-col md:flex-row gap-6 justify-between">
                      {/* Left side: Info */}
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <span className={`px-3 py-1 rounded-full text-xs font-bold border flex items-center gap-1 ${getProbabilityColor(col.probability)}`}>
                            {getProbabilityIcon(col.probability)}
                            {col.category} ({col.probability.toFixed(1)}%)
                          </span>
                          <span className="px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs font-medium text-white/70 flex items-center gap-1">
                            <MapPin className="w-3 h-3" />
                            {col.location}
                          </span>
                        </div>
                        <h3 className="text-xl font-bold text-white leading-tight mb-2">
                          {col.college}
                        </h3>
                        <p className="text-sm text-white/60 mb-4">{col.reason}</p>
                        
                        <div className="grid grid-cols-2 gap-4 mt-auto">
                          <div className="bg-black/30 rounded-xl p-3 border border-white/5">
                            <p className="text-xs text-white/40 uppercase font-semibold mb-1">Predicted Cutoff</p>
                            <p className="text-lg font-bold text-white">{col.cutoff}</p>
                          </div>
                          <div className="bg-black/30 rounded-xl p-3 border border-white/5">
                            <p className="text-xs text-white/40 uppercase font-semibold mb-1">Avg Placement</p>
                            <p className="text-lg font-bold text-white">{col.placement_avg_lpa ? `₹${col.placement_avg_lpa} LPA` : 'N/A'}</p>
                          </div>
                        </div>
                      </div>

                      {/* Right side: ML Score Gauge */}
                      <div className="flex flex-col items-center justify-center shrink-0 w-32 border-l border-white/10 pl-6">
                        <div className="relative w-24 h-24 flex items-center justify-center">
                          <svg className="w-full h-full transform -rotate-90">
                            <circle cx="48" cy="48" r="40" className="stroke-white/10" strokeWidth="8" fill="none" />
                            <motion.circle 
                              cx="48" cy="48" r="40" 
                              className="stroke-blue-500" 
                              strokeWidth="8" fill="none" 
                              strokeLinecap="round"
                              initial={{ strokeDasharray: "0 251.2" }}
                              animate={{ strokeDasharray: `${(col.recommendation_score / 100) * 251.2} 251.2` }}
                              transition={{ duration: 1.5, ease: "easeOut" }}
                            />
                          </svg>
                          <div className="absolute inset-0 flex flex-col items-center justify-center">
                            <span className="text-xl font-bold text-white">{col.recommendation_score}</span>
                            <span className="text-[10px] text-white/40 uppercase font-semibold">ML Score</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
