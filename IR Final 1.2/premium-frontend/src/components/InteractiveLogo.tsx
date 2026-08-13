"use client";

import { motion } from "framer-motion";
import { useState } from "react";

export default function InteractiveLogo() {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <motion.div 
      className="relative flex items-center justify-center cursor-pointer group p-4"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
    >
      {/* Background glow that expands on hover */}
      <motion.div
        className="absolute inset-0 bg-blue-500/20 rounded-full blur-xl"
        animate={{
          scale: isHovered ? 1.5 : 1,
          opacity: isHovered ? 0.8 : 0.4,
          backgroundColor: isHovered ? "rgba(139, 92, 246, 0.4)" : "rgba(59, 130, 246, 0.2)",
        }}
        transition={{ duration: 0.5 }}
      />
      
      <svg width="64" height="64" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg" className="relative z-10 drop-shadow-2xl">
        {/* Outer rotating ring */}
        <motion.circle
          cx="50"
          cy="50"
          r="45"
          stroke="url(#gradient-outer)"
          strokeWidth="2"
          strokeDasharray="20 10 10 30"
          animate={{
            rotate: [0, 360],
            strokeDasharray: isHovered ? ["40 10 5 15", "10 40 20 5", "40 10 5 15"] : ["20 10 10 30", "30 10 20 10", "20 10 10 30"],
          }}
          transition={{
            rotate: { duration: 20, repeat: Infinity, ease: "linear" },
            strokeDasharray: { duration: 3, repeat: Infinity, ease: "easeInOut" }
          }}
        />
        
        {/* Inner neural nodes */}
        <motion.path
          d="M 30 70 L 50 30 L 70 70"
          stroke="url(#gradient-inner)"
          strokeWidth="6"
          strokeLinecap="round"
          strokeLinejoin="round"
          animate={{
            pathLength: isHovered ? [0, 1] : 1,
            stroke: isHovered ? "url(#gradient-hover)" : "url(#gradient-inner)"
          }}
          transition={{ duration: 1, ease: "easeInOut" }}
        />
        
        {/* Horizontal connection for the 'A' / Pathway */}
        <motion.path
          d="M 40 55 L 60 55"
          stroke="url(#gradient-inner)"
          strokeWidth="6"
          strokeLinecap="round"
          animate={{
            scaleX: isHovered ? [0, 1] : 1,
            stroke: isHovered ? "url(#gradient-hover)" : "url(#gradient-inner)"
          }}
          transition={{ duration: 0.5, delay: isHovered ? 0.5 : 0 }}
        />
        
        {/* Central glowing core / Insight Node */}
        <motion.circle
          cx="50"
          cy="45"
          r="6"
          fill="#fff"
          animate={{
            scale: isHovered ? [1, 1.5, 1] : [1, 1.2, 1],
            boxShadow: isHovered ? "0 0 20px #fff" : "0 0 10px #fff",
          }}
          transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
          style={{ filter: "drop-shadow(0px 0px 8px rgba(255,255,255,0.8))" }}
        />
        
        {/* Floating particles */}
        <motion.circle cx="20" cy="40" r="2" fill="#60A5FA" animate={{ y: [0, -10, 0], opacity: [0.3, 1, 0.3] }} transition={{ duration: 2, repeat: Infinity }} />
        <motion.circle cx="80" cy="60" r="3" fill="#A78BFA" animate={{ y: [0, 15, 0], opacity: [0.2, 0.8, 0.2] }} transition={{ duration: 3, repeat: Infinity, delay: 1 }} />
        <motion.circle cx="75" cy="25" r="2" fill="#F472B6" animate={{ x: [0, 10, 0], opacity: [0.5, 1, 0.5] }} transition={{ duration: 2.5, repeat: Infinity, delay: 0.5 }} />

        {/* Gradients Definition */}
        <defs>
          <linearGradient id="gradient-outer" x1="0" y1="0" x2="100" y2="100">
            <stop offset="0%" stopColor="#3B82F6" />
            <stop offset="50%" stopColor="#8B5CF6" />
            <stop offset="100%" stopColor="#EC4899" />
          </linearGradient>
          <linearGradient id="gradient-inner" x1="30" y1="30" x2="70" y2="70">
            <stop offset="0%" stopColor="#60A5FA" />
            <stop offset="100%" stopColor="#3B82F6" />
          </linearGradient>
          <linearGradient id="gradient-hover" x1="30" y1="70" x2="70" y2="30">
            <stop offset="0%" stopColor="#EC4899" />
            <stop offset="100%" stopColor="#8B5CF6" />
          </linearGradient>
        </defs>
      </svg>
      
      {/* Brand Name that reveals completely on hover */}
      <div className="ml-4 flex flex-col justify-center overflow-hidden h-[64px]">
        <motion.div
          className="text-2xl font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-400 flex items-center"
        >
          <span>Insight</span>
          <motion.span 
            className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500 ml-1 inline-block"
            animate={{ 
              backgroundPosition: isHovered ? ["0%", "100%", "0%"] : "0%"
            }}
            transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
            style={{ backgroundSize: "200% auto" }}
          >
            Rural
          </motion.span>
        </motion.div>
        
        <motion.div 
          className="text-[10px] uppercase tracking-[0.2em] font-bold text-gray-500"
          initial={{ opacity: 0.7, y: 0 }}
          animate={{ 
            opacity: isHovered ? 1 : 0.7,
            color: isHovered ? "#9CA3AF" : "#6B7280"
          }}
        >
          AI Admission Intelligence
        </motion.div>
      </div>
    </motion.div>
  );
}
