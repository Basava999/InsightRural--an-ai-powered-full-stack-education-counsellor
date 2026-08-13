"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import { BrainCircuit, AlertTriangle, ShieldCheck, CheckCircle2, RefreshCw } from "lucide-react";
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  Tooltip,
  Cell
} from "recharts";

export default function RiskAnalyzerPage() {
  const [analyzing, setAnalyzing] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form State
  const [rank, setRank] = useState("8500");
  const [branch, setBranch] = useState("Computer Science");
  const [collegeType, setCollegeType] = useState("Tier 2");

  // API Data State
  const [riskData, setRiskData] = useState<any>(null);
  const [aiExplanation, setAiExplanation] = useState<string>("");

  const handleAnalyze = async () => {
    setAnalyzing(true);
    setShowResults(false);
    setError(null);
    
    try {
      const response = await fetch("http://localhost:8000/api/analyze/risk", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          rank: parseInt(rank),
          branch: branch,
          college_tier: collegeType.includes("Tier 1") ? 1 : collegeType.includes("Tier 2") ? 2 : 3,
          college: "Selected College",
          fees: 200000,
          hostel_fees: 100000,
          income: 500000,
          marks: 85,
          loan_required: true,
          has_scholarship: false
        })
      });
      
      const data = await response.json();
      
      if (!response.ok || !data.success) {
        throw new Error(data.error || "Failed to analyze risk");
      }
      
      setRiskData(data.risk_analysis);
      setAiExplanation(data.ai_explanation);
      setShowResults(true);
      
    } catch (err: any) {
      console.error(err);
      setError(err.message || "Something went wrong.");
    } finally {
      setAnalyzing(false);
    }
  };

  // Transform backend data for charts
  const getRadarData = () => {
    if (!riskData) return [];
    const dims = riskData.dimensions || {};
    return [
      { subject: "Employability", score: dims.employability_score || 0 },
      { subject: "Automation", score: dims.automation_susceptibility_score || 0 },
      { subject: "Academic", score: dims.academic_pressure_score || 0 },
      { subject: "Financial", score: dims.financial_burden_score || 0 },
      { subject: "Mental", score: dims.mental_burnout_score || 0 },
      { subject: "Location", score: dims.location_advantage_score || 0 },
      { subject: "Overall Fit", score: dims.overall_fit_score || 0 },
    ];
  };

  const getBarData = () => {
    if (!riskData) return [];
    return (riskData.roi_projection_5yr || []).map((val: number, i: number) => ({
      name: `Year ${i + 1}`,
      roi: val
    }));
  };

  return (
    <div className="flex flex-col h-full max-w-6xl mx-auto w-full pb-8">
      {/* Header */}
      <div className="mb-8 flex items-center gap-4">
        <div className="h-14 w-14 rounded-2xl bg-gradient-to-br from-rose-500/20 to-orange-500/20 border border-rose-500/30 flex items-center justify-center">
          <BrainCircuit className="text-rose-400" size={28} />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-white/60">
              Risk & Success Analyzer
            </h1>
            <span className="px-2 py-0.5 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/30 text-[10px] font-bold uppercase tracking-wider">
              PRO
            </span>
          </div>
          <p className="text-white/40 text-[15px] mt-1">11-dimensional analysis covering career safety, mental health, and ROI.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column: Input Form */}
        <div className="col-span-1 space-y-6">
          <div className="p-6 rounded-2xl bg-zinc-900 border border-white/10 relative overflow-hidden">
            <div className="absolute top-0 right-0 p-4 opacity-10">
              <BrainCircuit size={100} />
            </div>
            
            <h3 className="text-lg font-semibold mb-6 text-white/90">Configure Profile</h3>
            
            <div className="space-y-5 relative z-10">
              <div>
                <label className="block text-sm font-medium text-white/60 mb-2">KCET Rank</label>
                <input 
                  type="text" 
                  value={rank}
                  onChange={(e) => setRank(e.target.value)}
                  className="w-full bg-black/50 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-rose-500/50 transition-colors"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-white/60 mb-2">Target Branch</label>
                <select 
                  value={branch}
                  onChange={(e) => setBranch(e.target.value)}
                  className="w-full bg-black/50 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-rose-500/50 transition-colors appearance-none"
                >
                  <option>Computer Science</option>
                  <option>Mechanical Engineering</option>
                  <option>Civil Engineering</option>
                  <option>Electronics</option>
                  <option>Artificial Intelligence</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-white/60 mb-2">College Type</label>
                <select 
                  value={collegeType}
                  onChange={(e) => setCollegeType(e.target.value)}
                  className="w-full bg-black/50 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-rose-500/50 transition-colors appearance-none"
                >
                  <option>Tier 1 (Top 10)</option>
                  <option>Tier 2 (Top 30)</option>
                  <option>Tier 3</option>
                </select>
              </div>

              <button 
                onClick={handleAnalyze}
                disabled={analyzing}
                className="w-full mt-4 h-12 rounded-xl bg-gradient-to-r from-rose-500 to-orange-500 hover:from-rose-400 hover:to-orange-400 text-white font-semibold flex items-center justify-center gap-2 transition-all shadow-[0_0_20px_rgba(244,63,94,0.3)] hover:shadow-[0_0_30px_rgba(244,63,94,0.5)] disabled:opacity-50"
              >
                {analyzing ? (
                  <RefreshCw className="animate-spin" size={18} />
                ) : (
                  <BrainCircuit size={18} />
                )}
                {analyzing ? "Running 11-D Analysis..." : "Analyze Regret Risk"}
              </button>
              
              {error && (
                <div className="mt-4 p-3 rounded-lg bg-red-500/20 border border-red-500/50 text-red-200 text-sm">
                  {error}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right Column: Results Dashboard */}
        <div className="col-span-1 lg:col-span-2 relative">
          
          {analyzing && (
            <div className="absolute inset-0 z-20 flex flex-col items-center justify-center bg-black/40 backdrop-blur-sm rounded-2xl border border-white/5">
              <div className="relative w-24 h-24 mb-6">
                <div className="absolute inset-0 border-4 border-rose-500/20 rounded-full"></div>
                <div className="absolute inset-0 border-4 border-rose-500 rounded-full border-t-transparent animate-spin"></div>
                <BrainCircuit className="absolute inset-0 m-auto text-rose-400 animate-pulse" size={32} />
              </div>
              <p className="text-xl font-semibold text-white tracking-wide">Processing ML Models</p>
              <p className="text-rose-400 mt-2 text-sm">Fetching live analysis from InsightRural Intelligence Engine...</p>
            </div>
          )}

          {!analyzing && !showResults && !error && (
            <div className="flex flex-col items-center justify-center h-full bg-zinc-900/50 rounded-2xl border border-white/5 p-12 text-center">
              <BrainCircuit className="text-white/10 mb-4" size={64} />
              <h2 className="text-xl font-medium text-white/50 mb-2">Ready to Analyze</h2>
              <p className="text-white/30 text-sm max-w-sm">Configure your profile on the left and click analyze to run our proprietary 11-dimensional risk assessment.</p>
            </div>
          )}

          {showResults && riskData && (
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="grid grid-cols-2 gap-6 h-full"
            >
              {/* Top Stats */}
              <div className="col-span-2 grid grid-cols-3 gap-6">
                <div className="p-5 rounded-2xl bg-zinc-900/50 border border-emerald-500/20 relative overflow-hidden">
                  <div className="absolute top-0 left-0 w-1 h-full bg-emerald-500"></div>
                  <div className="flex justify-between items-start mb-2">
                    <div className="text-sm font-medium text-white/60">Success Probability</div>
                    <CheckCircle2 className="text-emerald-400" size={18} />
                  </div>
                  <div className="text-3xl font-bold text-white">{riskData.success_probability}%</div>
                </div>

                <div className="p-5 rounded-2xl bg-zinc-900/50 border border-amber-500/20 relative overflow-hidden">
                  <div className="absolute top-0 left-0 w-1 h-full bg-amber-500"></div>
                  <div className="flex justify-between items-start mb-2">
                    <div className="text-sm font-medium text-white/60">Regret Factor</div>
                    <AlertTriangle className="text-amber-400" size={18} />
                  </div>
                  <div className="text-3xl font-bold text-white">{riskData.overall_regret_risk}</div>
                </div>

                <div className="p-5 rounded-2xl bg-zinc-900/50 border border-blue-500/20 relative overflow-hidden">
                  <div className="absolute top-0 left-0 w-1 h-full bg-blue-500"></div>
                  <div className="flex justify-between items-start mb-2">
                    <div className="text-sm font-medium text-white/60">Career Safety</div>
                    <ShieldCheck className="text-blue-400" size={18} />
                  </div>
                  <div className="text-xl font-bold text-white capitalize">{riskData.career_safety_index.replace('_', ' ')}</div>
                </div>
              </div>
              
              {/* AI Explanation Banner */}
              <div className="col-span-2 p-5 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex gap-4 items-start">
                <BrainCircuit className="text-indigo-400 shrink-0 mt-1" size={24} />
                <div>
                  <h4 className="text-indigo-300 font-semibold mb-1">AI Executive Summary</h4>
                  <p className="text-white/80 text-sm leading-relaxed">{aiExplanation}</p>
                </div>
              </div>

              {/* Radar Chart */}
              <div className="col-span-2 md:col-span-1 p-6 rounded-2xl bg-zinc-900 border border-white/10 flex flex-col">
                <h3 className="text-sm font-semibold mb-2 text-white/80 uppercase tracking-widest">Dimension Breakdown</h3>
                <div className="flex-1 min-h-[250px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <RadarChart cx="50%" cy="50%" outerRadius="70%" data={getRadarData()}>
                      <PolarGrid stroke="rgba(255,255,255,0.1)" />
                      <PolarAngleAxis dataKey="subject" tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 11 }} />
                      <Radar
                        name="Score"
                        dataKey="score"
                        stroke="#f43f5e"
                        fill="#f43f5e"
                        fillOpacity={0.3}
                      />
                      <Tooltip 
                        contentStyle={{ backgroundColor: '#18181b', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '8px' }}
                        itemStyle={{ color: '#f43f5e' }}
                      />
                    </RadarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Bar Chart ROI */}
              <div className="col-span-2 md:col-span-1 p-6 rounded-2xl bg-zinc-900 border border-white/10 flex flex-col">
                <h3 className="text-sm font-semibold mb-2 text-white/80 uppercase tracking-widest">ROI Projection (LPA)</h3>
                <div className="flex-1 min-h-[250px] mt-4">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={getBarData()}>
                      <XAxis dataKey="name" stroke="rgba(255,255,255,0.2)" tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 11 }} />
                      <Tooltip 
                        cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                        contentStyle={{ backgroundColor: '#18181b', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '8px' }}
                      />
                      <Bar dataKey="roi" radius={[4, 4, 0, 0]}>
                        {
                          getBarData().map((entry: any, index: number) => (
                            <Cell key={`cell-${index}`} fill={index > 2 ? '#10b981' : '#6366f1'} />
                          ))
                        }
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
              
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}
