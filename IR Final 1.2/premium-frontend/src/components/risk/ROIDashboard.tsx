"use client";

import { TrendingUp, Award, IndianRupee } from "lucide-react";
import { motion } from "framer-motion";

interface Props {
  roiScore: number;
  tier: number;
  branch: string;
}

export default function ROIDashboard({ roiScore, tier, branch }: Props) {
  let message = "Excellent return on investment expected.";
  let bgGradient = "from-emerald-900/40 to-green-900/10";
  let textColor = "text-emerald-400";
  
  if (roiScore < 40) {
    message = "Low ROI. High fees vs expected starting salary.";
    bgGradient = "from-red-900/40 to-orange-900/10";
    textColor = "text-red-400";
  } else if (roiScore < 70) {
    message = "Moderate ROI. Break-even will take a few years.";
    bgGradient = "from-yellow-900/40 to-orange-900/10";
    textColor = "text-yellow-400";
  }

  return (
    <div className={`bg-gradient-to-br ${bgGradient} rounded-2xl border border-gray-800 p-6 shadow-lg h-full flex flex-col justify-between`}>
      <div className="flex items-center gap-2 mb-4">
        <TrendingUp className={textColor} size={20} />
        <h3 className={`text-sm font-bold uppercase tracking-wider ${textColor}`}>ROI Dashboard</h3>
      </div>
      
      <div className="flex items-end gap-3 mb-6">
        <span className="text-5xl font-black text-white">{roiScore}</span>
        <span className="text-sm text-gray-400 mb-2">/ 100</span>
      </div>

      <p className="text-sm text-gray-300 mb-6">{message}</p>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-black/30 rounded-xl p-3 border border-white/5">
          <div className="flex items-center gap-2 text-xs text-gray-500 mb-1">
            <Award size={14} /> Tier Assumed
          </div>
          <div className="font-semibold text-gray-200">Tier {tier}</div>
        </div>
        <div className="bg-black/30 rounded-xl p-3 border border-white/5">
          <div className="flex items-center gap-2 text-xs text-gray-500 mb-1">
            <IndianRupee size={14} /> Branch Type
          </div>
          <div className="font-semibold text-gray-200 truncate">{branch}</div>
        </div>
      </div>
    </div>
  );
}
