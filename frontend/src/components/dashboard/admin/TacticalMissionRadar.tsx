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

  const TacticalMapSVG = () => (
    <svg className="absolute inset-0 w-full h-full p-4 pointer-events-none z-[5]" viewBox="0 0 800 500" preserveAspectRatio="xMidYMid slice">
      <defs>
        <filter id="glow-map" x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur stdDeviation="4" result="blur" />
          <feComposite in="SourceGraphic" in2="blur" operator="over" />
        </filter>
        <linearGradient id="line-glow" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#0891b2" stopOpacity="0" />
          <stop offset="50%" stopColor="#22d3ee" stopOpacity="0.8" />
          <stop offset="100%" stopColor="#0891b2" stopOpacity="0" />
        </linearGradient>
      </defs>

      {/* Abstract Grid Details */}
      <g stroke="#0f172a" strokeWidth="1" opacity="0.5">
        <line x1="200" y1="0" x2="200" y2="500" />
        <line x1="600" y1="0" x2="600" y2="500" />
        <line x1="0" y1="150" x2="800" y2="150" />
        <line x1="0" y1="350" x2="800" y2="350" />
      </g>

      {/* Main Map Boundaries (Abstract City/Zones) */}
      <motion.path
        d="M 50 100 L 150 50 L 300 120 L 280 250 L 100 300 Z M 400 80 L 650 110 L 750 220 L 600 380 L 450 350 L 350 200 Z"
        fill="none"
        stroke="#1e293b"
        strokeWidth="3"
        initial={{ pathLength: 0, opacity: 0 }}
        animate={{ pathLength: 1, opacity: 0.8 }}
        transition={{ duration: 4, ease: "easeInOut" }}
      />
      <motion.path
        d="M 120 400 L 250 350 L 380 450 L 200 480 Z M 650 450 L 780 320 L 700 250 Z"
        fill="none"
        stroke="#0f172a"
        strokeWidth="2"
        initial={{ pathLength: 0, opacity: 0 }}
        animate={{ pathLength: 1, opacity: 0.6 }}
        transition={{ duration: 3, delay: 1, ease: "easeInOut" }}
      />

      {/* Dynamic Data Lines simulating traffic/info */}
      <motion.path
        d="M 50 100 L 150 50 L 300 120 L 400 80 L 650 110"
        fill="none"
        stroke="url(#line-glow)"
        strokeWidth="2"
        filter="url(#glow-map)"
        initial={{ pathLength: 0, pathOffset: 1 }}
        animate={{ pathLength: 0.2, pathOffset: 0 }}
        transition={{ repeat: Infinity, duration: 6, ease: "linear" }}
      />
      <motion.path
        d="M 100 300 L 280 250 L 350 200 L 450 350 L 600 380 L 650 450"
        fill="none"
        stroke="rgba(16, 185, 129, 0.5)"
        strokeWidth="1.5"
        filter="url(#glow-map)"
        initial={{ pathLength: 0, pathOffset: 1 }}
        animate={{ pathLength: 0.3, pathOffset: 0 }}
        transition={{ repeat: Infinity, duration: 8, ease: "linear", delay: 2 }}
      />
      <motion.path
        d="M 200 480 L 380 450 L 600 380 L 750 220"
        fill="none"
        stroke="rgba(244, 63, 94, 0.4)"
        strokeWidth="1.5"
        filter="url(#glow-map)"
        initial={{ pathLength: 0, pathOffset: 1 }}
        animate={{ pathLength: 0.25, pathOffset: 0 }}
        transition={{ repeat: Infinity, duration: 5, ease: "linear", delay: 1 }}
      />

      {/* Static Nodes (representing key hospitals/hubs) */}
      {[
        { cx: 150, cy: 50, r: 4 }, { cx: 300, cy: 120, r: 6 }, { cx: 400, cy: 80, r: 5 }, { cx: 650, cy: 110, r: 8 },
        { cx: 750, cy: 220, r: 4 }, { cx: 600, cy: 380, r: 6 }, { cx: 450, cy: 350, r: 5 }, { cx: 350, cy: 200, r: 7 },
        { cx: 280, cy: 250, r: 5 }, { cx: 100, cy: 300, r: 6 }, { cx: 380, cy: 450, r: 4 }
      ].map((node, i) => (
        <motion.circle
          key={i}
          cx={node.cx}
          cy={node.cy}
          r={node.r}
          fill="#334155"
          stroke="#0f172a"
          strokeWidth="1.5"
          initial={{ opacity: 0, r: 0 }}
          animate={{ opacity: [0.5, 1, 0.5], r: [node.r, node.r + 2, node.r] }}
          transition={{ repeat: Infinity, duration: 3 + (i % 3), delay: i * 0.2 }}
        />
      ))}
    </svg>
  );

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

      {/* SVG Tactical Map */}
      <TacticalMapSVG />

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
