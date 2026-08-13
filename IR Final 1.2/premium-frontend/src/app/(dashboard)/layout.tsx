import React from "react";
import { Sidebar } from "@/components/layout/Sidebar";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex h-screen w-full bg-black text-white overflow-hidden selection:bg-indigo-500/30">
      {/* Premium ambient background for the entire dashboard */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-indigo-900/10 blur-[120px]" />
        <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] rounded-full bg-purple-900/10 blur-[120px]" />
      </div>

      <Sidebar />
      
      <main className="flex-1 relative z-10 flex flex-col h-full overflow-hidden bg-black/40 shadow-[-10px_0_30px_rgba(0,0,0,0.5)] border-l border-white/5">
        {/* Top Navbar / Breadcrumbs area could go here */}
        <div className="flex-1 overflow-y-auto overflow-x-hidden p-6 scrollbar-hide">
          <div className="max-w-6xl mx-auto h-full">
            {children}
          </div>
        </div>
      </main>
    </div>
  );
}
