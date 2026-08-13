"use client";

import React from 'react';
import { motion } from 'framer-motion';
import { Sparkles, BrainCircuit, LineChart, ShieldCheck } from 'lucide-react';

const stats = [
  { name: 'Admission Probability', value: '84%', change: '+2.5%', icon: LineChart },
  { name: 'AI Success Score', value: '92/100', change: 'High ROI', icon: BrainCircuit },
  { name: 'Matched Colleges', value: '14', change: '3 new', icon: Sparkles },
  { name: 'Risk Profile', value: 'Low', change: 'Safe', icon: ShieldCheck },
];

export default function DashboardHome() {
  return (
    <div className="space-y-8">
      {/* Header */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-4xl font-extrabold tracking-tight mb-2">
          Welcome back, <span className="premium-gradient-text">Student</span>
        </h1>
        <p className="text-white/60 text-lg">Here is your AI counseling summary for today.</p>
      </motion.div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, idx) => (
          <motion.div
            key={stat.name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: idx * 0.1 }}
            className="glass-card rounded-2xl p-6"
          >
            <div className="flex justify-between items-start mb-4">
              <div className="p-2 rounded-lg bg-white/5 border border-white/10">
                <stat.icon className="h-6 w-6 text-indigo-400" />
              </div>
              <span className="text-xs font-medium text-emerald-400 bg-emerald-400/10 px-2 py-1 rounded-full">
                {stat.change}
              </span>
            </div>
            <p className="text-sm font-medium text-white/50 mb-1">{stat.name}</p>
            <p className="text-3xl font-bold tracking-tight text-white">{stat.value}</p>
          </motion.div>
        ))}
      </div>

      {/* Main Content Area */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Chart Area */}
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="lg:col-span-2 glass-panel rounded-2xl p-6 min-h-[400px]"
        >
          <h2 className="text-xl font-bold mb-4">Probability Trend</h2>
          <div className="flex items-center justify-center h-[300px] border border-dashed border-white/10 rounded-xl bg-black/20 text-white/40">
            [Recharts Area Chart will go here]
          </div>
        </motion.div>

        {/* Action Panel */}
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.5 }}
          className="glass-panel rounded-2xl p-6 flex flex-col"
        >
          <h2 className="text-xl font-bold mb-4">AI Recommendations</h2>
          <div className="flex-1 space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="p-4 rounded-xl bg-white/5 border border-white/5 hover:bg-white/10 transition-colors cursor-pointer">
                <p className="text-sm font-bold text-white mb-1">Update Your Profile</p>
                <p className="text-xs text-white/50">Add your 12th marks for a more accurate prediction.</p>
              </div>
            ))}
          </div>
          <button className="mt-4 w-full py-3 rounded-xl bg-white text-black font-bold hover:bg-white/90 transition-all active:scale-95 shadow-[0_0_20px_rgba(255,255,255,0.3)]">
            Run AI Analysis
          </button>
        </motion.div>
      </div>
    </div>
  );
}
