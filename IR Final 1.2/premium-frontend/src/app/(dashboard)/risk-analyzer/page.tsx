"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowRight, ShieldAlert, BookOpen, Banknote, Briefcase, Sparkles, TrendingUp } from "lucide-react";
import RiskRadarChart from "@/components/risk/RiskRadarChart";
import ScoreGauge from "@/components/risk/ScoreGauge";
import RegretIndicator from "@/components/risk/RegretIndicator";
import FinancialHealthMeter from "@/components/risk/FinancialHealthMeter";
import CareerAlignmentChart from "@/components/risk/CareerAlignmentChart";
import ROIDashboard from "@/components/risk/ROIDashboard";

export default function RiskAnalyzerPage() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");

  const [formData, setFormData] = useState({
    rank: 15000,
    college: "RV College of Engineering",
    college_tier: 1,
    branch: "Computer Science",
    fees: 150000,
    hostel_fees: 80000,
    income: 600000,
    marks: 85,
    skills: "coding, math",
    interests: "software, ai",
    loan_required: false,
    has_scholarship: false
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    
    // Parse skills and interests into arrays
    const payload = {
      ...formData,
      skills: formData.skills.split(",").map(s => s.trim()),
      interests: formData.interests.split(",").map(s => s.trim()),
    };

    try {
      const token = localStorage.getItem("token") || "";
      const response = await fetch("http://localhost:8000/api/analyze/risk", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });
      
      const data = await response.json();
      if (data.success) {
        setResult(data);
      } else {
        setError(data.error || "Failed to analyze risk.");
      }
    } catch (err) {
      setError("Server error. Ensure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: any) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  return (
    <div className="min-h-screen bg-[#0A0A0A] text-white p-6 md:p-12 font-sans overflow-x-hidden selection:bg-blue-500/30">
      <div className="max-w-7xl mx-auto space-y-12">
        
        {/* Header Section */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center space-y-4"
        >
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-sm font-medium mb-4">
            <Sparkles size={14} />
            <span>AI Admission Intelligence</span>
          </div>
          <h1 className="text-4xl md:text-6xl font-bold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-gray-100 to-gray-500">
            Counseling Risk Analyzer
          </h1>
          <p className="text-gray-400 max-w-2xl mx-auto text-lg">
            Don't just predict if you can get in. Predict if you'll succeed. 
            Our AI evaluates academic, financial, and career alignment to prevent admission regrets.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          
          {/* Input Form Column */}
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="lg:col-span-4 bg-gray-900/50 backdrop-blur-xl border border-gray-800 rounded-3xl p-6 shadow-2xl"
          >
            <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
              <ShieldAlert className="text-blue-400" size={20} />
              Configure Profile
            </h2>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-gray-400 mb-1 uppercase tracking-wider">KCET Rank</label>
                  <input type="number" name="rank" value={formData.rank} onChange={handleInputChange} className="w-full bg-black/50 border border-gray-800 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-blue-500 transition-colors" />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-400 mb-1 uppercase tracking-wider">PUC Marks (%)</label>
                  <input type="number" name="marks" value={formData.marks} onChange={handleInputChange} className="w-full bg-black/50 border border-gray-800 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-blue-500 transition-colors" />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-400 mb-1 uppercase tracking-wider">Target College</label>
                <input type="text" name="college" value={formData.college} onChange={handleInputChange} className="w-full bg-black/50 border border-gray-800 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-blue-500 transition-colors" />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-gray-400 mb-1 uppercase tracking-wider">Target Branch</label>
                  <input type="text" name="branch" value={formData.branch} onChange={handleInputChange} className="w-full bg-black/50 border border-gray-800 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-blue-500 transition-colors" />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-400 mb-1 uppercase tracking-wider">College Tier</label>
                  <select name="college_tier" value={formData.college_tier} onChange={handleInputChange} className="w-full bg-black/50 border border-gray-800 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-blue-500 transition-colors text-white">
                    <option value={1}>Tier 1 (Top)</option>
                    <option value={2}>Tier 2 (Mid)</option>
                    <option value={3}>Tier 3 (Low)</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-gray-400 mb-1 uppercase tracking-wider">Tuition Fee</label>
                  <input type="number" name="fees" value={formData.fees} onChange={handleInputChange} className="w-full bg-black/50 border border-gray-800 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-blue-500 transition-colors" />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-400 mb-1 uppercase tracking-wider">Hostel Fee</label>
                  <input type="number" name="hostel_fees" value={formData.hostel_fees} onChange={handleInputChange} className="w-full bg-black/50 border border-gray-800 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-blue-500 transition-colors" />
                </div>
              </div>
              
              <div>
                <label className="block text-xs font-medium text-gray-400 mb-1 uppercase tracking-wider">Family Income (INR)</label>
                <input type="number" name="income" value={formData.income} onChange={handleInputChange} className="w-full bg-black/50 border border-gray-800 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-blue-500 transition-colors" />
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-400 mb-1 uppercase tracking-wider">Your Skills (comma separated)</label>
                <input type="text" name="skills" value={formData.skills} onChange={handleInputChange} className="w-full bg-black/50 border border-gray-800 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-blue-500 transition-colors" placeholder="math, coding, design" />
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-400 mb-1 uppercase tracking-wider">Interests (comma separated)</label>
                <input type="text" name="interests" value={formData.interests} onChange={handleInputChange} className="w-full bg-black/50 border border-gray-800 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-blue-500 transition-colors" placeholder="robotics, AI, writing" />
              </div>
              
              <div className="flex gap-6 pt-2">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" name="loan_required" checked={formData.loan_required} onChange={handleInputChange} className="rounded bg-gray-800 border-gray-700 text-blue-500 focus:ring-blue-500" />
                  <span className="text-sm text-gray-300">Need Loan</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" name="has_scholarship" checked={formData.has_scholarship} onChange={handleInputChange} className="rounded bg-gray-800 border-gray-700 text-blue-500 focus:ring-blue-500" />
                  <span className="text-sm text-gray-300">Scholarship</span>
                </label>
              </div>

              <button 
                type="submit" 
                disabled={loading}
                className="w-full mt-6 bg-white text-black hover:bg-gray-200 transition-colors py-3 rounded-xl font-semibold flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {loading ? "Analyzing Profile..." : "Analyze Risk"} 
                {!loading && <ArrowRight size={18} />}
              </button>
              {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
            </form>
          </motion.div>

          {/* Results Dashboard Column */}
          <div className="lg:col-span-8">
            <AnimatePresence mode="wait">
              {!result && !loading ? (
                <motion.div 
                  initial={{ opacity: 0 }} 
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="h-full flex flex-col items-center justify-center text-gray-500 border border-dashed border-gray-800 rounded-3xl p-12 min-h-[500px]"
                >
                  <TrendingUp size={48} className="mb-4 opacity-50" />
                  <p className="text-lg">Submit your profile to generate your custom Risk & Success analysis.</p>
                </motion.div>
              ) : loading ? (
                <motion.div 
                  initial={{ opacity: 0 }} 
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="h-full flex flex-col items-center justify-center border border-gray-800 rounded-3xl p-12 min-h-[500px]"
                >
                  <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-4"></div>
                  <p className="text-gray-400">Our AI is predicting your success trajectory...</p>
                </motion.div>
              ) : (
                <motion.div 
                  initial={{ opacity: 0, y: 20 }} 
                  animate={{ opacity: 1, y: 0 }}
                  className="space-y-6"
                >
                  
                  {/* Top Metrics Row */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <ScoreGauge score={result.risk_analysis.success_score} label="Overall Success Score" />
                    <RegretIndicator probability={result.risk_analysis.regret_probability} />
                  </div>

                  {/* Comprehensive 3-Column Charts Row */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <FinancialHealthMeter 
                      income={formData.income}
                      totalCost={formData.fees + formData.hostel_fees}
                      loan={formData.loan_required}
                      scholarship={formData.has_scholarship}
                      riskLevel={result.risk_analysis.financial_risk}
                    />
                    <CareerAlignmentChart 
                      careerScore={result.risk_analysis.career_alignment_score}
                      branchScore={result.risk_analysis.branch_compatibility_score}
                    />
                    <ROIDashboard 
                      roiScore={result.risk_analysis.college_roi_score}
                      tier={formData.college_tier}
                      branch={formData.branch}
                    />
                  </div>

                  {/* Visualizations & Explanations Row */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Radar Chart */}
                    <div className="bg-gray-900 rounded-2xl border border-gray-800 p-6 flex flex-col">
                      <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-4">Dimensional Analysis</h3>
                      <div className="flex-1 min-h-[250px]">
                        <RiskRadarChart 
                          data={{
                            academic: result.risk_analysis.academic_risk === "High" ? 80 : result.risk_analysis.academic_risk === "Medium" ? 50 : 20,
                            financial: result.risk_analysis.financial_risk === "High" ? 80 : result.risk_analysis.financial_risk === "Medium" ? 50 : 20,
                            placement: result.risk_analysis.placement_risk === "High" ? 80 : result.risk_analysis.placement_risk === "Medium" ? 50 : 20,
                            careerAlignment: result.risk_analysis.career_alignment_score,
                            branchCompatibility: result.risk_analysis.branch_compatibility_score
                          }} 
                        />
                      </div>
                    </div>
                    
                    {/* Detailed Risks */}
                    <div className="bg-gray-900 rounded-2xl border border-gray-800 p-6 flex flex-col gap-4 justify-between">
                      <div className="space-y-4">
                        <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider">Specific Risk Factors</h3>
                        
                        <div className="flex items-center justify-between p-3 rounded-xl bg-gray-950 border border-gray-800">
                          <div className="flex items-center gap-3">
                            <BookOpen className="text-blue-400" size={18} />
                            <span className="font-medium text-gray-300">Academic Target</span>
                          </div>
                          <span className={`px-2 py-1 rounded text-xs font-bold ${result.risk_analysis.academic_risk === 'High' ? 'bg-red-500/20 text-red-400' : result.risk_analysis.academic_risk === 'Medium' ? 'bg-yellow-500/20 text-yellow-400' : 'bg-green-500/20 text-green-400'}`}>
                            {result.risk_analysis.academic_risk} Risk
                          </span>
                        </div>
                        
                        <div className="flex items-center justify-between p-3 rounded-xl bg-gray-950 border border-gray-800">
                          <div className="flex items-center gap-3">
                            <Banknote className="text-green-400" size={18} />
                            <span className="font-medium text-gray-300">Financial Burden</span>
                          </div>
                          <span className={`px-2 py-1 rounded text-xs font-bold ${result.risk_analysis.financial_risk === 'High' ? 'bg-red-500/20 text-red-400' : result.risk_analysis.financial_risk === 'Medium' ? 'bg-yellow-500/20 text-yellow-400' : 'bg-green-500/20 text-green-400'}`}>
                            {result.risk_analysis.financial_risk} Risk
                          </span>
                        </div>
                        
                        <div className="flex items-center justify-between p-3 rounded-xl bg-gray-950 border border-gray-800">
                          <div className="flex items-center gap-3">
                            <Briefcase className="text-purple-400" size={18} />
                            <span className="font-medium text-gray-300">Placement Record</span>
                          </div>
                          <span className={`px-2 py-1 rounded text-xs font-bold ${result.risk_analysis.placement_risk === 'High' ? 'bg-red-500/20 text-red-400' : result.risk_analysis.placement_risk === 'Medium' ? 'bg-yellow-500/20 text-yellow-400' : 'bg-green-500/20 text-green-400'}`}>
                            {result.risk_analysis.placement_risk} Risk
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* AI Counselor Explanation */}
                  <div className="bg-gradient-to-br from-blue-900/20 to-gray-900 rounded-2xl border border-blue-500/20 p-6 relative overflow-hidden">
                    <div className="absolute top-0 right-0 p-6 opacity-10 pointer-events-none">
                      <Sparkles size={100} />
                    </div>
                    <h3 className="text-sm font-medium text-blue-400 uppercase tracking-wider mb-4 flex items-center gap-2">
                      <Sparkles size={16} /> AI Counselor Insight
                    </h3>
                    <p className="text-gray-300 leading-relaxed text-lg">
                      {result.ai_explanation}
                    </p>
                  </div>

                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </div>
  );
}
