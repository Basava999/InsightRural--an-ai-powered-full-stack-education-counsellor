"use client";

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { User, CheckCircle2, GraduationCap, Target, Heart } from 'lucide-react';

export default function ProfilePage() {
  const [activeTab, setActiveTab] = useState<'academic' | 'preferences'>('academic');
  const [saved, setSaved] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-12">
      {/* Header */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="inline-flex items-center justify-center p-3 bg-fuchsia-500/10 rounded-2xl mb-4 border border-fuchsia-500/20">
          <User className="w-8 h-8 text-fuchsia-400" />
        </div>
        <h1 className="text-4xl font-extrabold tracking-tight mb-4">
          Student <span className="text-transparent bg-clip-text bg-gradient-to-r from-fuchsia-400 to-pink-500">Profile</span>
        </h1>
        <p className="text-white/60 text-lg">
          Keep your academic and preference data updated to ensure the AI Admission Consultant gives you the most accurate recommendations.
        </p>
      </motion.div>

      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="glass-panel rounded-3xl overflow-hidden"
      >
        {/* Tabs */}
        <div className="flex border-b border-white/10">
          <button 
            className={`flex-1 py-4 text-sm font-bold flex items-center justify-center gap-2 transition-colors ${activeTab === 'academic' ? 'bg-white/10 text-white' : 'text-white/50 hover:bg-white/5 hover:text-white'}`}
            onClick={() => setActiveTab('academic')}
          >
            <GraduationCap className="w-4 h-4" /> Academic Records
          </button>
          <button 
            className={`flex-1 py-4 text-sm font-bold flex items-center justify-center gap-2 transition-colors ${activeTab === 'preferences' ? 'bg-white/10 text-white' : 'text-white/50 hover:bg-white/5 hover:text-white'}`}
            onClick={() => setActiveTab('preferences')}
          >
            <Target className="w-4 h-4" /> Goals & Preferences
          </button>
        </div>

        {/* Form Content */}
        <form onSubmit={handleSave} className="p-8">
          {activeTab === 'academic' && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-xs font-semibold text-white/60 mb-2 uppercase tracking-wider">KCET Rank</label>
                  <input type="number" defaultValue="5400" className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-fuchsia-500" />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-white/60 mb-2 uppercase tracking-wider">JEE Main Percentile</label>
                  <input type="number" step="0.01" defaultValue="89.5" className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-fuchsia-500" />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-white/60 mb-2 uppercase tracking-wider">PUC / 12th Percentage (%)</label>
                  <input type="number" step="0.1" defaultValue="92.4" className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-fuchsia-500" />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-white/60 mb-2 uppercase tracking-wider">Social Category</label>
                  <select defaultValue="GM" className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-fuchsia-500 appearance-none">
                    {['GM', 'OBC', 'SC', 'ST', '2A', '2B', '3A', '3B'].map(c => <option key={c} value={c}>{c}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-white/60 mb-2 uppercase tracking-wider">Special Quotas (SNQ, NCC, etc.)</label>
                  <input type="text" defaultValue="SNQ" className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-fuchsia-500" />
                </div>
              </div>
            </motion.div>
          )}

          {activeTab === 'preferences' && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
              <div>
                <label className="block text-xs font-semibold text-white/60 mb-2 uppercase tracking-wider">Target Branches (Comma separated)</label>
                <input type="text" defaultValue="Computer Science, Information Science, AI & ML" className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-fuchsia-500" />
              </div>
              <div>
                <label className="block text-xs font-semibold text-white/60 mb-2 uppercase tracking-wider">Preferred Location</label>
                <input type="text" defaultValue="Bengaluru, Mysuru" className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-fuchsia-500" />
              </div>
              <div>
                <label className="block text-xs font-semibold text-white/60 mb-2 uppercase tracking-wider">Career Aspirations</label>
                <textarea rows={3} defaultValue="Software Engineer at a top MNC or starting my own tech company." className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-fuchsia-500 resize-none" />
              </div>
              <div className="flex items-center gap-4 p-4 bg-white/5 rounded-xl border border-white/10">
                <input type="checkbox" id="hostel" defaultChecked className="w-5 h-5 rounded border-white/20 bg-black/40 text-fuchsia-500 focus:ring-fuchsia-500" />
                <label htmlFor="hostel" className="text-sm font-medium text-white">I will need hostel accommodation</label>
              </div>
            </motion.div>
          )}

          <div className="mt-8 pt-8 border-t border-white/10 flex justify-end">
            <button 
              type="submit"
              className="px-8 py-3 rounded-xl bg-fuchsia-500 hover:bg-fuchsia-400 text-white font-bold transition-all active:scale-95 flex items-center gap-2 hover:shadow-[0_0_20px_rgba(217,70,239,0.4)]"
            >
              {saved ? (
                <><CheckCircle2 className="w-5 h-5" /> Saved Successfully</>
              ) : (
                'Save Profile'
              )}
            </button>
          </div>
        </form>
      </motion.div>
    </div>
  );
}
