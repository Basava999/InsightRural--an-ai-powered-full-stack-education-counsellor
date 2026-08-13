"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import { 
  MessageSquare, 
  Target, 
  BrainCircuit, 
  Compass, 
  GraduationCap, 
  Building2, 
  LayoutDashboard,
  ChevronLeft,
  ChevronRight,
  Settings
} from "lucide-react";
import clsx from "clsx";

const NAV_ITEMS = [
  { group: "Overview", items: [
    { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  ]},
  { group: "Intelligence", items: [
    { label: "AI Counselor", href: "/chat", icon: MessageSquare, badge: "AI" },
    { label: "College Predictor", href: "/predictor", icon: Target, badge: "98%" },
    { label: "Risk Analyzer", href: "/risk-analyzer", icon: BrainCircuit, badge: "PRO", glow: true },
    { label: "Career Simulator", href: "/career", icon: Compass },
  ]},
  { group: "Resources", items: [
    { label: "Scholarships", href: "/scholarships", icon: GraduationCap },
    { label: "Hostels", href: "/hostels", icon: Building2 },
  ]}
];

export function Sidebar() {
  const pathname = usePathname();
  const [isCollapsed, setIsCollapsed] = useState(false);

  return (
    <motion.aside 
      initial={false}
      animate={{ width: isCollapsed ? 80 : 280 }}
      className="relative flex flex-col h-screen border-r border-white/10 bg-black/40 backdrop-blur-xl shrink-0"
    >
      {/* Collapse Toggle */}
      <button 
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="absolute -right-4 top-8 z-50 flex h-8 w-8 items-center justify-center rounded-full border border-white/10 bg-zinc-900 text-white/70 hover:text-white hover:bg-zinc-800 transition-colors"
      >
        {isCollapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
      </button>

      {/* Brand Header */}
      <div className="flex items-center h-20 px-6 shrink-0 border-b border-white/5">
        <div className="flex items-center gap-3 w-full">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 shadow-[0_0_20px_rgba(99,102,241,0.4)]">
            <span className="font-bold text-white text-sm">IR</span>
          </div>
          {!isCollapsed && (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex flex-col overflow-hidden whitespace-nowrap"
            >
              <span className="font-bold text-white text-lg tracking-tight leading-none">InsightRural</span>
              <span className="text-[10px] text-white/40 uppercase tracking-widest mt-1 font-semibold">Premium</span>
            </motion.div>
          )}
        </div>
      </div>

      {/* Navigation */}
      <div className="flex-1 overflow-y-auto overflow-x-hidden py-6 px-4 space-y-8 scrollbar-hide">
        {NAV_ITEMS.map((group, gIdx) => (
          <div key={gIdx}>
            {!isCollapsed && (
              <div className="mb-2 px-2 text-[11px] font-bold uppercase tracking-[0.2em] text-white/30">
                {group.group}
              </div>
            )}
            <div className="space-y-1">
              {group.items.map((item, iIdx) => {
                const isActive = pathname === item.href || (pathname === '/' && item.href === '/dashboard');
                return (
                  <Link href={item.href} key={iIdx}>
                    <div className={clsx(
                      "group relative flex items-center gap-3 rounded-xl px-3 py-2.5 transition-all duration-200",
                      isActive 
                        ? "bg-white/10 text-white" 
                        : "text-white/60 hover:bg-white/5 hover:text-white"
                    )}>
                      {isActive && (
                        <motion.div 
                          layoutId="activeNav"
                          className="absolute inset-0 rounded-xl border border-white/10 bg-white/5"
                          initial={false}
                          transition={{ type: "spring", stiffness: 300, damping: 30 }}
                        />
                      )}
                      
                      <div className={clsx(
                        "relative z-10 flex h-5 w-5 shrink-0 items-center justify-center transition-colors",
                        item.glow && isActive ? "text-pink-400 drop-shadow-[0_0_10px_rgba(236,72,153,0.5)]" : ""
                      )}>
                        <item.icon size={20} strokeWidth={isActive ? 2.5 : 2} />
                      </div>

                      {!isCollapsed && (
                        <div className="relative z-10 flex flex-1 items-center justify-between overflow-hidden whitespace-nowrap">
                          <span className={clsx("text-sm font-medium", item.glow && isActive && "text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400")}>
                            {item.label}
                          </span>
                          {item.badge && (
                            <span className={clsx(
                              "text-[10px] font-bold px-2 py-0.5 rounded-full",
                              item.glow 
                                ? "bg-gradient-to-r from-purple-500/20 to-pink-500/20 text-pink-300 border border-pink-500/20"
                                : "bg-white/10 text-white/70"
                            )}>
                              {item.badge}
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {/* Footer Profile */}
      <div className="p-4 border-t border-white/5">
        <div className="flex items-center gap-3 rounded-xl p-2 hover:bg-white/5 transition-colors cursor-pointer">
          <div className="h-9 w-9 rounded-full bg-zinc-800 border border-white/10 flex items-center justify-center shrink-0">
            <span className="text-white/70 text-sm font-medium">S</span>
          </div>
          {!isCollapsed && (
            <div className="flex flex-1 flex-col overflow-hidden whitespace-nowrap">
              <span className="text-sm font-medium text-white">Student Profile</span>
              <span className="text-xs text-white/40">Rank: 8,500</span>
            </div>
          )}
          {!isCollapsed && <Settings size={16} className="text-white/40 shrink-0" />}
        </div>
      </div>
    </motion.aside>
  );
}
