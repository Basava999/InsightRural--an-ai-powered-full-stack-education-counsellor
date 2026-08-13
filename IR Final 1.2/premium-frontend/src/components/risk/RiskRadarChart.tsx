"use client";

import { ResponsiveContainer, Radar, RadarChart, PolarGrid, PolarAngleAxis, Tooltip } from "recharts";
import { motion } from "framer-motion";

interface RiskRadarChartProps {
  data: {
    academic: number;
    financial: number;
    placement: number;
    careerAlignment: number;
    branchCompatibility: number;
  };
}

export default function RiskRadarChart({ data }: RiskRadarChartProps) {
  const chartData = [
    { subject: "Academic Fit", A: 100 - data.academic, fullMark: 100 },
    { subject: "Financial Fit", A: 100 - data.financial, fullMark: 100 },
    { subject: "Placement", A: 100 - data.placement, fullMark: 100 },
    { subject: "Career Alignment", A: data.careerAlignment, fullMark: 100 },
    { subject: "Branch Match", A: data.branchCompatibility, fullMark: 100 },
  ];

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5, delay: 0.2 }}
      className="w-full h-[300px] flex items-center justify-center p-4 bg-gray-900 rounded-2xl border border-gray-800 shadow-[0_0_40px_-15px_rgba(59,130,246,0.3)]"
    >
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart cx="50%" cy="50%" outerRadius="70%" data={chartData}>
          <PolarGrid stroke="#374151" />
          <PolarAngleAxis dataKey="subject" tick={{ fill: "#9CA3AF", fontSize: 12 }} />
          <Tooltip 
            contentStyle={{ backgroundColor: "#111827", borderColor: "#374151", color: "#F3F4F6", borderRadius: "8px" }}
            itemStyle={{ color: "#60A5FA" }}
          />
          <Radar 
            name="Score" 
            dataKey="A" 
            stroke="#3B82F6" 
            fill="#3B82F6" 
            fillOpacity={0.4} 
            isAnimationActive={true}
          />
        </RadarChart>
      </ResponsiveContainer>
    </motion.div>
  );
}
