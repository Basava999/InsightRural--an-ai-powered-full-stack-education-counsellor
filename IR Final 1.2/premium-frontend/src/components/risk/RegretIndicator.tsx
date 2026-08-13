"use client";

import { motion } from "framer-motion";

export default function RegretIndicator({ probability }: { probability: number }) {
  let color = "bg-green-500";
  let text = "Safe Choice";
  let textColor = "text-green-400";
  let glow = "shadow-green-500/20";
  
  if (probability > 60) {
    color = "bg-red-500";
    text = "High Regret Risk";
    textColor = "text-red-400";
    glow = "shadow-red-500/20";
  } else if (probability > 35) {
    color = "bg-yellow-500";
    text = "Moderate Risk";
    textColor = "text-yellow-400";
    glow = "shadow-yellow-500/20";
  }

  return (
    <div className={`p-5 bg-gray-900 rounded-2xl border border-gray-800 flex items-center justify-between shadow-lg ${glow}`}>
      <div>
        <p className="text-sm text-gray-400 font-medium">Regret Probability</p>
        <p className={`text-xl font-bold mt-1 ${textColor}`}>{text}</p>
      </div>
      <div className="flex items-center gap-3">
        <span className="text-3xl font-black text-white">{probability}%</span>
        <motion.div 
          className={`w-3 h-3 rounded-full ${color}`}
          animate={{ scale: [1, 1.2, 1] }}
          transition={{ repeat: Infinity, duration: 2 }}
        />
      </div>
    </div>
  );
}
