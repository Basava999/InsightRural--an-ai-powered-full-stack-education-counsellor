"use client";

import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, Cell } from "recharts";
import { motion } from "framer-motion";

interface Props {
  careerScore: number;
  branchScore: number;
}

export default function CareerAlignmentChart({ careerScore, branchScore }: Props) {
  const data = [
    { name: "Branch Match", score: branchScore, fill: "#3B82F6" },
    { name: "Career Align", score: careerScore, fill: "#8B5CF6" }
  ];

  return (
    <div className="bg-gray-900 rounded-2xl border border-gray-800 p-6 flex flex-col justify-between shadow-lg h-full">
      <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-4">Career & Skills Alignment</h3>
      
      <div className="flex-1 w-full min-h-[150px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="vertical" margin={{ top: 0, right: 30, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" horizontal={false} />
            <XAxis type="number" domain={[0, 100]} hide />
            <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{ fill: "#9CA3AF", fontSize: 12 }} width={85} />
            <Tooltip 
              cursor={{ fill: "rgba(255,255,255,0.05)" }}
              contentStyle={{ backgroundColor: "#111827", borderColor: "#374151", color: "#F3F4F6", borderRadius: "8px" }}
            />
            <Bar dataKey="score" radius={[0, 4, 4, 0]} animationDuration={1500}>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.fill} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      
      <div className="mt-4 pt-4 border-t border-gray-800 flex justify-between text-xs text-gray-500">
        <p>Evaluates your stated skills against industry requirements for the branch.</p>
      </div>
    </div>
  );
}
