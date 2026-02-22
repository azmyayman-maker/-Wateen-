"use client";

import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";

export const TacticalMissionRadar = () => {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null;

  // Mock Active Units (Nurses/Ambulances)
  const activeUnits = [
    { id: 1, x: "30%", y: "45%", status: "available", name: "N-Ahmed" },
    { id: 2, x: "65%", y: "25%", status: "en-route", name: "N-Sara" },
    { id: 3, x: "80%", y: "70%", status: "available", name: "N-Omar" },
    { id: 4, x: "40%", y: "85%", status: "emergency", name: "Unit-X" },
    { id: 5, x: "15%", y: "60%", status: "en-route", name: "N-Mona" },
  ];

  return (
    <div className="relative w-full h-full min-h-[400px] flex items-center justify-center overflow-hidden rounded-lg bg-[#020617] isolate">
      {/* Background Grid */}
      <div 
        className="absolute inset-0 z-0 opacity-20 pointer-events-none"
        style={{
          backgroundImage: `linear-gradient(to right, #00ffcc 1px, transparent 1px), linear-gradient(to bottom, #00ffcc 1px, transparent 1px)`,
          backgroundSize: "40px 40px"
        }}
      />

      {/* Radar Concentric Rings */}
      <div className="absolute inset-0 flex items-center justify-center z-10 pointer-events-none">
        {[1, 2, 3, 4].map((ring) => (
          <div
            key={ring}
            className="absolute rounded-full border border-cyan-500/20"
            style={{
              width: `${ring * 25}%`,
              height: `${ring * 25}%`,
              animation: `pulse-slow ${ring * 2}s infinite alternate`
            }}
          />
        ))}
        {/* Crosshairs */}
        <div className="absolute w-full h-px bg-cyan-500/30" />
        <div className="absolute h-full w-px bg-cyan-500/30" />
      </div>

      {/* Radar Sweep Shader */}
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ repeat: Infinity, duration: 4, ease: "linear" }}
        className="absolute inset-0 z-20 pointer-events-none origin-center"
        style={{
          background: `conic-gradient(from 0deg, transparent 0deg, rgba(6, 182, 212, 0.1) 260deg, rgba(6, 182, 212, 0.8) 360deg)`
        }}
      />
      
      {/* Blips */}
      <div className="absolute inset-0 z-30 pointer-events-none">
        {activeUnits.map((unit) => {
          const color = 
            unit.status === "available" ? "bg-emerald-400" :
            unit.status === "en-route" ? "bg-amber-400" : "bg-rose-500";
            
          const glowColor = 
            unit.status === "available" ? "shadow-[0_0_15px_rgba(52,211,153,0.8)]" :
            unit.status === "en-route" ? "shadow-[0_0_15px_rgba(251,191,36,0.8)]" : "shadow-[0_0_25px_rgba(244,63,94,1)]";
            
          return (
            <motion.div
              key={unit.id}
              className="absolute group perspective-[1000px] pointer-events-auto cursor-crosshair"
              style={{ left: unit.x, top: unit.y }}
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: Math.random() * 2, duration: 0.5 }}
            >
              <div className="relative flex items-center justify-center w-4 h-4 -translate-x-1/2 -translate-y-1/2">
                <span className={`absolute inline-flex h-full w-full rounded-full ${color} opacity-75 animate-ping`} />
                <span className={`relative inline-flex rounded-full h-2 w-2 ${color} ${glowColor}`} />
                
                {/* Tooltip on Hover */}
                <div className="absolute left-6 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity bg-slate-900/90 border border-slate-700 rounded p-2 backdrop-blur-md whitespace-nowrap z-50">
                   <p className="text-xs font-mono text-slate-300">ID: {unit.name}</p>
                   <p className={`text-[10px] font-bold uppercase tracking-widest ${unit.status === 'emergency' ? 'text-rose-400 animate-pulse' : 'text-cyan-400'}`}>
                     {unit.status}
                   </p>
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>
      
      <style jsx global>{`
        @keyframes pulse-slow {
          0% { opacity: 0.3; }
          100% { opacity: 0.7; }
        }
      `}</style>
    </div>
  );
};
