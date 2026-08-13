"use client";

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Award, Wallet, ArrowRight, Filter, AlertCircle, Sparkles } from 'lucide-react';

interface Scholarship {
  id: string;
  name: string;
  provider: string;
  amount: string;
  eligibility: string;
  deadline: string;
  difficulty: string;
}

export default function ScholarshipsPage() {
  const [scholarships, setScholarships] = useState<Scholarship[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [category, setCategory] = useState('All');
  const [income, setIncome] = useState('');

  useEffect(() => {
    const fetchScholarships = async () => {
      setLoading(true);
      try {
        const res = await fetch('http://127.0.0.1:8000/api/scholarships/match', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            family_income: income ? parseInt(income) * 100000 : 900000,
            category: category === 'All' ? 'GM' : category,
            state: 'Karnataka'
          })
        });
        
        const data = await res.json();
        if (data.success) {
          setScholarships(data.scholarships);
        } else {
          setScholarships([]);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchScholarships();
  }, [category, income]);

  return (
    <div className="space-y-8 pb-12">
      {/* Header */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-3xl"
      >
        <div className="inline-flex items-center justify-center p-3 bg-amber-500/10 rounded-2xl mb-4 border border-amber-500/20">
          <Award className="w-8 h-8 text-amber-400" />
        </div>
        <h1 className="text-4xl lg:text-5xl font-extrabold tracking-tight mb-4">
          AI Scholarship <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-400 to-orange-500">Matcher</span>
        </h1>
        <p className="text-white/60 text-lg">
          We scanned 50+ government and private scholarship databases to find the best financial aid tailored to your exact demographic and merit profile.
        </p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Filters Panel */}
        <motion.div 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="lg:col-span-4"
        >
          <div className="glass-panel rounded-3xl p-6 sticky top-8">
            <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
              <Filter className="w-5 h-5 text-amber-400" />
              Eligibility Filters
            </h2>
            
            <div className="space-y-5">
              <div>
                <label className="block text-xs font-semibold text-white/60 mb-2 uppercase tracking-wider">Social Category</label>
                <select value={category} onChange={(e) => setCategory(e.target.value)} className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-amber-500 transition-all appearance-none">
                  {['All', 'GM', 'OBC', 'SC', 'ST', 'Minority'].map(c => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>
              
              <div>
                <label className="block text-xs font-semibold text-white/60 mb-2 uppercase tracking-wider">Family Income (Lakhs/Year)</label>
                <input type="number" placeholder="e.g. 2.5" value={income} onChange={(e) => setIncome(e.target.value)} className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white placeholder:text-white/30 focus:outline-none focus:ring-2 focus:ring-amber-500 transition-all" />
              </div>

              <div className="p-4 bg-amber-500/10 border border-amber-500/20 rounded-xl mt-6">
                <div className="flex items-start gap-3">
                  <Sparkles className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
                  <div>
                    <h4 className="text-sm font-bold text-amber-400 mb-1">AI Auto-Match Active</h4>
                    <p className="text-xs text-amber-400/70">Your profile details (Rank: 5400, State: KA) are already applied to these results.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Scholarships List */}
        <div className="lg:col-span-8">
          <AnimatePresence mode="wait">
            {loading ? (
              <motion.div 
                key="loading"
                initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                className="h-full min-h-[400px] flex items-center justify-center"
              >
                <div className="flex flex-col items-center gap-4 text-amber-400">
                  <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1.5, ease: "linear" }} className="w-16 h-16 border-4 border-amber-500/30 border-t-amber-500 rounded-full" />
                  <p className="font-medium animate-pulse">Scanning databases for matches...</p>
                </div>
              </motion.div>
            ) : (
              <motion.div 
                key="results"
                initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                className="space-y-4"
              >
                <h2 className="text-xl font-bold mb-6 text-white flex items-center gap-2">
                  Top Eligible Schemes <span className="px-2 py-0.5 rounded-full bg-white/10 text-xs font-medium">{scholarships.length}</span>
                </h2>
                
                {scholarships.map((scholarship, idx) => (
                  <motion.div
                    key={scholarship.name}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.1 }}
                    className="glass-card rounded-2xl p-6 relative overflow-hidden group"
                  >
                    <div className="absolute top-0 right-0 p-6 opacity-10 group-hover:opacity-20 transition-opacity">
                      <Wallet className="w-24 h-24 text-amber-400" />
                    </div>
                    
                    <div className="relative z-10">
                      <div className="flex justify-between items-start mb-4">
                        <span className="px-3 py-1 bg-amber-500/20 text-amber-400 border border-amber-500/30 rounded-full text-xs font-bold flex items-center gap-1">
                          <Sparkles className="w-3 h-3" />
                          {scholarship.difficulty}
                        </span>
                        <span className="text-xs font-medium text-white/50 uppercase tracking-wider">{scholarship.provider}</span>
                      </div>
                      
                      <h3 className="text-2xl font-bold text-white mb-2 pr-12">{scholarship.name}</h3>
                      
                      <div className="bg-black/30 border border-white/5 rounded-xl p-4 mb-4">
                        <p className="text-sm font-medium text-emerald-400 flex items-center gap-2 mb-2">
                          <Wallet className="w-4 h-4" />
                          {scholarship.amount}
                        </p>
                        <p className="text-xs text-white/60">
                          <span className="font-semibold text-white/80">Eligibility:</span> {scholarship.eligibility}
                        </p>
                        <p className="text-xs text-white/60 mt-1">
                          <span className="font-semibold text-white/80">Deadline:</span> {scholarship.deadline}
                        </p>
                      </div>
                      
                      <button 
                        className="inline-flex items-center gap-2 text-sm font-bold text-white bg-white/10 hover:bg-white/20 px-5 py-2.5 rounded-xl transition-all"
                      >
                        Apply Now
                        <ArrowRight className="w-4 h-4" />
                      </button>
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
