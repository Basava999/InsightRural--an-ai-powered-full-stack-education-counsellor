"use client";

import { motion } from "framer-motion";

interface Props {
  income: number;
  totalCost: number;
  loan: boolean;
  scholarship: boolean;
  riskLevel: string;
}

export default function FinancialHealthMeter({ income, totalCost, loan, scholarship, riskLevel }: Props) {
  // Simple calculation for UI purposes
  const affordability = totalCost > 0 ? Math.min((income / totalCost) * 100, 100) : 100;
  
  let barColor = "bg-green-500";
  if (riskLevel === "Medium") barColor = "bg-yellow-500";
  if (riskLevel === "High") barColor = "bg-red-500";

  return (
    <div className="bg-gray-900 rounded-2xl border border-gray-800 p-6 flex flex-col justify-between shadow-lg">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider">Financial Health</h3>
        <span className={`px-2 py-1 rounded text-xs font-bold ${
          riskLevel === 'High' ? 'bg-red-500/20 text-red-400' : 
          riskLevel === 'Medium' ? 'bg-yellow-500/20 text-yellow-400' : 
          'bg-green-500/20 text-green-400'
        }`}>
          {riskLevel} Risk
        </span>
      </div>
      
      <div className="space-y-4">
        <div>
          <div className="flex justify-between text-xs text-gray-500 mb-1">
            <span>Affordability Index</span>
            <span className="font-mono">{affordability.toFixed(0)}%</span>
          </div>
          <div className="w-full bg-gray-800 rounded-full h-2">
            <motion.div 
              initial={{ width: 0 }}
              animate={{ width: `${affordability}%` }}
              transition={{ duration: 1, ease: "easeOut" }}
              className={`h-2 rounded-full ${barColor}`} 
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-800">
          <div>
            <p className="text-xs text-gray-500 mb-1">Est. Total Cost</p>
            <p className="font-mono text-lg text-gray-200">₹{(totalCost/100000).toFixed(1)}L</p>
          </div>
          <div>
            <p className="text-xs text-gray-500 mb-1">Family Income</p>
            <p className="font-mono text-lg text-gray-200">₹{(income/100000).toFixed(1)}L</p>
          </div>
        </div>

        <div className="flex gap-2 mt-2">
          {scholarship && <span className="text-[10px] bg-blue-500/20 text-blue-400 px-2 py-1 rounded border border-blue-500/20">Scholarship Applied</span>}
          {loan && <span className="text-[10px] bg-purple-500/20 text-purple-400 px-2 py-1 rounded border border-purple-500/20">Loan Factored</span>}
        </div>
      </div>
    </div>
  );
}
