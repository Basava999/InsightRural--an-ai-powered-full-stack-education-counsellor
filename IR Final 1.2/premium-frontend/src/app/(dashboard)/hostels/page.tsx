"use client";

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Building2, Search, MapPin, IndianRupee, BedDouble, CheckCircle2, XCircle } from 'lucide-react';

interface Accommodation {
  type: string;
  avg_annual_cost: number;
  deposit: number;
  food_included: boolean;
  pros: string[];
  cons: string[];
  icon: string;
}

export default function HostelsPage() {
  const [loading, setLoading] = useState(false);
  const [city, setCity] = useState('');
  const [tier, setTier] = useState('3');
  const [results, setResults] = useState<Accommodation[]>([]);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const res = await fetch('http://127.0.0.1:8000/api/hostels/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          city: city || 'Bangalore',
          college_tier: parseInt(tier)
        })
      });
      
      const data = await res.json();
      if (data.success) {
        setResults(data.accommodations);
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
        <div className="inline-flex items-center justify-center p-3 bg-teal-500/10 rounded-2xl mb-4 border border-teal-500/20">
          <Building2 className="w-8 h-8 text-teal-400" />
        </div>
        <h1 className="text-4xl lg:text-5xl font-extrabold tracking-tight mb-4">
          Cost of Living <span className="premium-gradient-text" style={{ backgroundImage: 'linear-gradient(to right, #14b8a6, #3b82f6)' }}>Estimator</span>
        </h1>
        <p className="text-white/60 text-lg">
          Don't get blindsided by the hidden costs of moving to a new city. Estimate and compare actual hostel, PG, and renting costs.
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
          <form onSubmit={handleSearch} className="glass-panel rounded-3xl p-6 relative overflow-hidden sticky top-8">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-teal-500 to-blue-500" />
            <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
              <MapPin className="w-5 h-5 text-teal-400" />
              Target Location
            </h2>
            
            <div className="space-y-5">
              <div>
                <label className="block text-xs font-semibold text-white/60 mb-2 uppercase tracking-wider">Target City</label>
                <input required type="text" placeholder="e.g. Bangalore, Hubli, Mangalore" value={city} onChange={(e) => setCity(e.target.value)} className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white placeholder:text-white/30 focus:outline-none focus:ring-2 focus:ring-teal-500 transition-all" />
              </div>
              
              <div>
                <label className="block text-xs font-semibold text-white/60 mb-2 uppercase tracking-wider">College Type</label>
                <select value={tier} onChange={(e) => setTier(e.target.value)} className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-teal-500 transition-all appearance-none">
                  <option value="1">Top Tier (RVCE, PES, etc)</option>
                  <option value="2">Mid Tier</option>
                  <option value="3">Standard / Govt College</option>
                </select>
              </div>
            </div>

            <button 
              type="submit"
              disabled={loading || !city}
              className="w-full mt-8 py-4 rounded-xl bg-teal-500 text-white font-bold hover:bg-teal-400 transition-all active:scale-95 flex justify-center items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-[0_0_20px_rgba(20,184,166,0.4)]"
            >
              {loading ? (
                <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1, ease: "linear" }}>
                  <Search className="w-5 h-5" />
                </motion.div>
              ) : (
                "Estimate Living Costs"
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
                <BedDouble className="w-16 h-16 text-white/20 mb-4" />
                <h3 className="text-xl font-bold text-white/60 mb-2">Awaiting Parameters</h3>
                <p className="text-white/40 max-w-sm">Enter your target city to compare actual accommodation costs.</p>
              </motion.div>
            )}

            {loading && (
              <motion.div 
                initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                className="h-full min-h-[400px] flex items-center justify-center"
              >
                <div className="flex flex-col items-center gap-4 text-teal-400">
                  <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1.5, ease: "linear" }} className="w-16 h-16 border-4 border-teal-500/30 border-t-teal-500 rounded-full" />
                  <p className="font-medium animate-pulse">Calculating Hyper-Local Cost of Living...</p>
                </div>
              </motion.div>
            )}

            {!loading && results.length > 0 && (
              <motion.div 
                initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                className="space-y-4"
              >
                <h2 className="text-xl font-bold mb-6 text-white">Accommodation Options</h2>
                
                {results.map((acc, idx) => (
                  <motion.div
                    key={acc.type}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.1 }}
                    className="glass-card rounded-2xl p-6 relative overflow-hidden"
                  >
                    <div className="flex flex-col md:flex-row gap-6 justify-between items-start md:items-center">
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-4">
                          <h3 className="text-2xl font-bold text-white leading-tight">{acc.type}</h3>
                          <span className={`px-3 py-1 rounded-full text-xs font-bold border flex items-center gap-1 ${acc.food_included ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' : 'bg-rose-500/20 text-rose-400 border-rose-500/30'}`}>
                            {acc.food_included ? 'Food Included' : 'Food Extra'}
                          </span>
                        </div>
                        
                        <div className="grid grid-cols-2 gap-4 mb-6">
                          <div className="bg-black/30 rounded-xl p-3 border border-white/5">
                            <p className="text-xs text-white/40 uppercase font-semibold mb-1">Annual Cost</p>
                            <p className="text-xl font-bold text-teal-400 flex items-center gap-1">
                              <IndianRupee className="w-4 h-4" />
                              {acc.avg_annual_cost.toLocaleString('en-IN')}
                            </p>
                          </div>
                          <div className="bg-black/30 rounded-xl p-3 border border-white/5">
                            <p className="text-xs text-white/40 uppercase font-semibold mb-1">Deposit Needed</p>
                            <p className="text-lg font-bold text-white flex items-center gap-1">
                              <IndianRupee className="w-3 h-3" />
                              {acc.deposit.toLocaleString('en-IN')}
                            </p>
                          </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <p className="text-xs text-white/40 uppercase font-semibold mb-2">Pros</p>
                            <ul className="space-y-1">
                              {acc.pros.map((pro, i) => (
                                <li key={i} className="text-sm text-white/70 flex items-start gap-2">
                                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                                  {pro}
                                </li>
                              ))}
                            </ul>
                          </div>
                          <div>
                            <p className="text-xs text-white/40 uppercase font-semibold mb-2">Cons</p>
                            <ul className="space-y-1">
                              {acc.cons.map((con, i) => (
                                <li key={i} className="text-sm text-white/70 flex items-start gap-2">
                                  <XCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                                  {con}
                                </li>
                              ))}
                            </ul>
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
