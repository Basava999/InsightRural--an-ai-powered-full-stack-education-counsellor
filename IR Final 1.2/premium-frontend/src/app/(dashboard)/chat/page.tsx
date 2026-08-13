"use client";

import React, { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Bot, User, Sparkles, Building2, TrendingUp, GraduationCap } from "lucide-react";
import clsx from "clsx";

// Types
type Role = "user" | "ai";

interface Message {
  id: string;
  role: Role;
  content: string;
  widget?: "college_list" | "scholarship_list" | "risk_chart";
}

const SUGGESTED_PROMPTS = [
  "Predict my college options for KCET Rank 8500",
  "What are the best scholarships for SC students?",
  "Analyze the risk of choosing Mechanical Engineering",
  "Compare RVCE vs MSRIT for Computer Science",
];

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome-1",
      role: "ai",
      content: "Hello! I am InsightRural AI, your premium admission counselor. I can predict colleges, find scholarships, and analyze the long-term risk of your career choices. How can I guide your future today?",
    }
  ]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSend = async (text: string = input) => {
    if (!text.trim()) return;

    const userMsg: Message = { id: Date.now().toString(), role: "user", content: text };
    const aiMessageId = (Date.now() + 1).toString();
    
    // Add user message and a placeholder AI message
    setMessages(prev => [...prev, userMsg, { id: aiMessageId, role: "ai", content: "" }]);
    setInput("");
    setIsTyping(true);

    try {
      // Connect to the new FastAPI streaming endpoint
      const response = await fetch("http://localhost:8000/api/chat/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, history: messages.slice(-5) })
      });

      if (!response.ok || !response.body) {
        throw new Error("Failed to connect to Intelligence Engine");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      
      let aiContent = "";
      let widget: Message["widget"] = undefined;

      // Real-time chunk reading
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        // Handle SSE format "data: <chunk>\n\n"
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') break;
            
            try {
              const parsed = JSON.parse(data);
              
              if (parsed.content) {
                aiContent += parsed.content;
                // Update the UI character by character
                setMessages(prev => prev.map(msg => 
                  msg.id === aiMessageId ? { ...msg, content: aiContent } : msg
                ));
              }
              
              // If the backend attached citations or widgets to the final chunk
              if (parsed.widget) {
                widget = parsed.widget;
                setMessages(prev => prev.map(msg => 
                  msg.id === aiMessageId ? { ...msg, widget: widget } : msg
                ));
              }
            } catch (e) {
              console.error("Error parsing stream chunk", e);
            }
          }
        }
      }
    } catch (error) {
      setMessages(prev => prev.map(msg => 
        msg.id === aiMessageId 
          ? { ...msg, content: "Error: Could not reach the FastAPI streaming backend on port 8000." } 
          : msg
      ));
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto w-full pb-4">
      
      {/* Header */}
      <div className="mb-6 flex items-center gap-3">
        <div className="h-12 w-12 rounded-2xl bg-gradient-to-br from-indigo-500/20 to-purple-500/20 border border-indigo-500/30 flex items-center justify-center">
          <Sparkles className="text-indigo-400" size={24} />
        </div>
        <div>
          <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-white/60">
            AI Counselor
          </h1>
          <p className="text-white/40 text-sm">Powered by InsightRural Intelligence Engine</p>
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto mb-6 pr-4 space-y-6 scrollbar-hide">
        <AnimatePresence initial={false}>
          {messages.map((msg) => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={clsx(
                "flex gap-4 max-w-[85%]",
                msg.role === "user" ? "ml-auto flex-row-reverse" : ""
              )}
            >
              {/* Avatar */}
              <div className={clsx(
                "h-8 w-8 rounded-full flex items-center justify-center shrink-0 mt-1",
                msg.role === "user" 
                  ? "bg-zinc-800 border border-white/10" 
                  : "bg-indigo-500/20 border border-indigo-500/30"
              )}>
                {msg.role === "user" ? <User size={16} className="text-white/70" /> : <Bot size={16} className="text-indigo-400" />}
              </div>

              {/* Message Bubble */}
              <div className="flex flex-col gap-3 min-w-0">
                <div className={clsx(
                  "px-5 py-3.5 rounded-2xl text-[15px] leading-relaxed break-words",
                  msg.role === "user" 
                    ? "bg-zinc-800 text-white rounded-tr-sm" 
                    : "bg-white/5 border border-white/10 text-white/90 rounded-tl-sm"
                )}>
                  {msg.content}
                </div>
                
                {/* Widgets */}
                {msg.widget === "college_list" && (
                  <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-hide">
                    {[1, 2, 3].map((i) => (
                      <div key={i} className="min-w-[240px] p-4 rounded-xl bg-zinc-900 border border-white/10 hover:border-indigo-500/50 transition-colors cursor-pointer shrink-0">
                        <div className="flex items-center gap-2 mb-2">
                          <Building2 size={16} className="text-indigo-400" />
                          <span className="font-semibold text-sm">RV College of Engineering</span>
                        </div>
                        <div className="text-xs text-white/50 mb-3">Computer Science (CSE)</div>
                        <div className="flex items-center justify-between">
                          <span className="text-xs bg-green-500/20 text-green-400 px-2 py-1 rounded-md">92% Match</span>
                          <span className="text-xs text-white/40">Cutoff: 4500</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {msg.widget === "scholarship_list" && (
                  <div className="grid grid-cols-2 gap-3">
                    <div className="p-4 rounded-xl bg-zinc-900 border border-white/10 hover:border-yellow-500/50 transition-colors cursor-pointer">
                      <div className="flex items-center gap-2 mb-2">
                        <GraduationCap size={16} className="text-yellow-400" />
                        <span className="font-semibold text-sm">Post-Matric Scholarship</span>
                      </div>
                      <div className="text-xs text-white/50 mb-3">100% Tuition Fee Waiver</div>
                      <button className="text-xs bg-white/10 hover:bg-white/20 text-white px-3 py-1.5 rounded-md transition-colors w-full">Apply Now</button>
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          ))}
          
          {/* Typing Indicator */}
          {isTyping && (
             <motion.div
             initial={{ opacity: 0, y: 10 }}
             animate={{ opacity: 1, y: 0 }}
             className="flex gap-4 max-w-[85%]"
           >
             <div className="h-8 w-8 rounded-full bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center shrink-0 mt-1">
               <Bot size={16} className="text-indigo-400" />
             </div>
             <div className="px-5 py-4 rounded-2xl bg-white/5 border border-white/10 rounded-tl-sm flex items-center gap-1.5 h-[52px]">
               <motion.div className="w-1.5 h-1.5 rounded-full bg-indigo-400" animate={{ y: [0, -5, 0] }} transition={{ duration: 0.6, repeat: Infinity, delay: 0 }} />
               <motion.div className="w-1.5 h-1.5 rounded-full bg-indigo-400" animate={{ y: [0, -5, 0] }} transition={{ duration: 0.6, repeat: Infinity, delay: 0.2 }} />
               <motion.div className="w-1.5 h-1.5 rounded-full bg-indigo-400" animate={{ y: [0, -5, 0] }} transition={{ duration: 0.6, repeat: Infinity, delay: 0.4 }} />
             </div>
           </motion.div>
          )}
        </AnimatePresence>
        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Prompts (if chat is empty or short) */}
      {messages.length === 1 && (
        <div className="grid grid-cols-2 gap-3 mb-6">
          {SUGGESTED_PROMPTS.map((prompt, idx) => (
            <button 
              key={idx}
              onClick={() => handleSend(prompt)}
              className="text-left p-3 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 hover:border-white/20 transition-all text-sm text-white/70 hover:text-white"
            >
              {prompt}
            </button>
          ))}
        </div>
      )}

      {/* Input Area */}
      <div className="relative">
        <div className="absolute inset-0 bg-gradient-to-r from-indigo-500/20 via-purple-500/20 to-pink-500/20 blur-xl rounded-full" />
        <div className="relative bg-zinc-900 border border-white/10 rounded-2xl flex items-end p-2 focus-within:border-indigo-500/50 focus-within:ring-1 focus-within:ring-indigo-500/50 transition-all shadow-2xl">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            placeholder="Ask about colleges, ranks, scholarships..."
            className="w-full max-h-32 min-h-[44px] bg-transparent border-none text-white placeholder-white/30 resize-none py-3 px-4 focus:outline-none scrollbar-hide text-[15px]"
            rows={1}
          />
          <button
            onClick={() => handleSend()}
            disabled={!input.trim() || isTyping}
            className="h-11 w-11 shrink-0 rounded-xl bg-white text-black flex items-center justify-center hover:bg-white/90 disabled:opacity-50 disabled:cursor-not-allowed transition-all mb-0.5 mr-0.5"
          >
            <Send size={18} className="ml-1" />
          </button>
        </div>
        <div className="text-center mt-3 text-xs text-white/30 font-medium">
          InsightRural AI can make mistakes. Verify important information with KEA/JoSAA.
        </div>
      </div>

    </div>
  );
}
