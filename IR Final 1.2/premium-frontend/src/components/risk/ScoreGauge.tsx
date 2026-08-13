"use client";

import { motion } from "framer-motion";
import { useEffect, useState } from "react";

export default function ScoreGauge({ score, label }: { score: number, label: string }) {
  const [currentScore, setCurrentScore] = useState(0);

  useEffect(() => {
    const timer = setTimeout(() => {
      setCurrentScore(score);
    }, 300);
    return () => clearTimeout(timer);
  }, [score]);

  // Circumference calculation
  const radius = 60;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (currentScore / 100) * circumference;

  let color = "#10B981"; // green
  if (score < 50) color = "#EF4444"; // red
  else if (score < 75) color = "#F59E0B"; // yellow

  return (
    <div className="flex flex-col items-center justify-center p-6 bg-gray-900 rounded-2xl border border-gray-800 shadow-xl relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-gray-800/50 to-transparent pointer-events-none" />
      <svg className="w-40 h-40 transform -rotate-90">
        {/* Background circle */}
        <circle
          cx="80"
          cy="80"
          r={radius}
          stroke="currentColor"
          strokeWidth="12"
          fill="transparent"
          className="text-gray-800"
        />
        {/* Progress circle */}
        <motion.circle
          cx="80"
          cy="80"
          r={radius}
          stroke={color}
          strokeWidth="12"
          fill="transparent"
          strokeLinecap="round"
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset }}
          transition={{ duration: 1.5, ease: "easeOut" }}
          style={{ strokeDasharray: circumference }}
          className="drop-shadow-lg"
        />
      </svg>
      
      <div className="absolute flex flex-col items-center justify-center">
        <motion.span 
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="text-4xl font-bold text-white tracking-tighter"
        >
          {currentScore}
        </motion.span>
        <span className="text-xs text-gray-400 font-medium uppercase tracking-wider">{label}</span>
      </div>
    </div>
  );
}
