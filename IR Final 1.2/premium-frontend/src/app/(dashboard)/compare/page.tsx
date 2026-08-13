"use client";

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowLeftRight, Search, MapPin, DollarSign, Building, Briefcase } from 'lucide-react';

export default function ComparePage() {
  const [colleges, setColleges] = useState<any[]>([]);
  const [search, setSearch] = useState('');
  
  const handleAddMock = () => {
    if (colleges.length >= 3) return;
    setColleges([...colleges, {
      id: Date.now(),
      name: "RV College of Engineering",
      location: "Bengaluru",
      type: "Private",
      fee: "₹2,50,000",
      placement: "₹14.5 LPA",
      cutoff: "450"
    }]);
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
          <ArrowLeftRight className="w-8 h-8 text-teal-400" />
        </div>
        <h1 className="text-4xl lg:text-5xl font-extrabold tracking-tight mb-4">
          Head-to-Head <span className="text-transparent bg-clip-text bg-gradient-to-r from-teal-400 to-emerald-500">Compare</span>
        </h1>
        <p className="text-white/60 text-lg">
          Side-by-side comparison of placement metrics, fee structures, and location factors to help you make the right choice.
        </p>
      </motion.div>

      <div className="glass-panel rounded-3xl p-6">
        <div className="flex gap-4 mb-8">
          <div className="flex-1 relative">
            <input 
              type="text" 
              placeholder="Search to add a college (e.g. RVCE, PES)..." 
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-black/40 border border-white/10 rounded-xl px-12 py-4 text-white placeholder:text-white/30 focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white/30" />
          </div>
          <button 
            onClick={handleAddMock}
            disabled={colleges.length >= 3}
            className="px-8 py-4 rounded-xl bg-teal-500 hover:bg-teal-400 text-white font-bold transition-all disabled:opacity-50 flex items-center gap-2"
          >
            Add
          </button>
        </div>

        {colleges.length === 0 ? (
          <div className="h-64 border-2 border-dashed border-white/10 rounded-2xl flex flex-col items-center justify-center text-white/40">
            <ArrowLeftRight className="w-12 h-12 mb-4 opacity-50" />
            <p>Search and add up to 3 colleges to compare.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {colleges.map((c, i) => (
              <motion.div 
                key={c.id}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="glass-card rounded-2xl overflow-hidden border border-white/10"
              >
                <div className="p-6 bg-white/5 border-b border-white/10">
                  <h3 className="text-xl font-bold text-white mb-2">{c.name}</h3>
                  <div className="flex gap-2 text-xs font-medium text-white/50">
                    <span className="flex items-center gap-1"><MapPin className="w-3 h-3" /> {c.location}</span>
                    <span>•</span>
                    <span className="flex items-center gap-1"><Building className="w-3 h-3" /> {c.type}</span>
                  </div>
                </div>
                <div className="p-6 space-y-6">
                  <div>
                    <p className="text-xs text-white/40 uppercase font-bold mb-1 flex items-center gap-1">
                      <Briefcase className="w-4 h-4 text-teal-400" /> Avg Placement
                    </p>
                    <p className="text-xl font-bold text-white">{c.placement}</p>
                  </div>
                  <div>
                    <p className="text-xs text-white/40 uppercase font-bold mb-1 flex items-center gap-1">
                      <DollarSign className="w-4 h-4 text-teal-400" /> Annual Fee
                    </p>
                    <p className="text-xl font-bold text-white">{c.fee}</p>
                  </div>
                  <div>
                    <p className="text-xs text-white/40 uppercase font-bold mb-1 flex items-center gap-1">
                      <ArrowLeftRight className="w-4 h-4 text-teal-400" /> Prev Cutoff
                    </p>
                    <p className="text-xl font-bold text-white">{c.cutoff}</p>
                  </div>
                  <button 
                    onClick={() => setColleges(colleges.filter(col => col.id !== c.id))}
                    className="w-full py-2 rounded-lg bg-rose-500/10 text-rose-400 text-sm font-bold hover:bg-rose-500/20 transition-colors"
                  >
                    Remove
                  </button>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
