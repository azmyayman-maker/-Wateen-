"use client";

import React from "react";
import { motion } from "framer-motion";

// --- 3D SVG Illustrations ---

export const HolographicPulse = () => (
  <svg width="0" height="0">
    <defs>
      <filter id="holographic-glow" x="-20%" y="-20%" width="140%" height="140%">
        <feGaussianBlur stdDeviation="8" result="blur" />
        <feComposite in="SourceGraphic" in2="blur" operator="over" />
      </filter>
      <filter id="inner-shadow" x="-10%" y="-10%" width="120%" height="120%">
        <feOffset dx="0" dy="4"/>
        <feGaussianBlur stdDeviation="5" result="offset-blur"/>
        <feComposite operator="out" in="SourceGraphic" in2="offset-blur" result="inverse"/>
        <feFlood floodColor="black" floodOpacity="0.7" result="color"/>
        <feComposite operator="in" in="color" in2="inverse" result="shadow"/>
        <feComposite operator="over" in="shadow" in2="SourceGraphic"/>
      </filter>
    </defs>
  </svg>
);

export const NursingVisitSVG = () => (
  <motion.svg
    viewBox="0 0 100 100"
    className="w-full h-full drop-shadow-2xl"
    animate={{ y: [0, -8, 0] }}
    transition={{ repeat: Infinity, duration: 4, ease: "easeInOut" }}
  >
    <defs>
      <linearGradient id="nursingGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#60A5FA" />
        <stop offset="100%" stopColor="#4338CA" />
      </linearGradient>
      <radialGradient id="nursingGlow" cx="50%" cy="50%" r="50%">
        <stop offset="0%" stopColor="#60A5FA" stopOpacity="0.5" />
        <stop offset="100%" stopColor="#4338CA" stopOpacity="0" />
      </radialGradient>
    </defs>
    <circle cx="50" cy="50" r="40" fill="url(#nursingGlow)" className="animate-pulse" />
    <path
      d="M30 50 A20 20 0 0 1 70 50 A20 20 0 0 1 30 50 Z"
      fill="url(#nursingGrad)"
      filter="url(#inner-shadow)"
      opacity="0.9"
    />
    <path
      d="M50 35 L60 45 L50 65 L40 45 Z"
      fill="#FFFFFF"
      opacity="0.8"
      className="drop-shadow-lg"
    />
    <motion.circle
      cx="50" cy="50" r="45"
      fill="none" stroke="#60A5FA" strokeWidth="1"
      strokeDasharray="4 8"
      animate={{ rotate: 360 }}
      transition={{ repeat: Infinity, duration: 20, ease: "linear" }}
    />
    <motion.path
      d="M20 60 L35 60 L45 35 L55 85 L65 50 L80 50"
      fill="none" stroke="#FFFFFF" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
      initial={{ pathLength: 0 }}
      animate={{ pathLength: 1 }}
      transition={{ repeat: Infinity, duration: 3, ease: "easeInOut", repeatDelay: 1 }}
    />
  </motion.svg>
);

export const InjectionsSVG = () => (
  <motion.svg
    viewBox="0 0 100 100"
    className="w-full h-full drop-shadow-xl"
    animate={{ y: [0, -6, 0] }}
    transition={{ repeat: Infinity, duration: 3.5, ease: "easeInOut", delay: 0.5 }}
  >
    <defs>
      <linearGradient id="injectionGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#34D399" />
        <stop offset="100%" stopColor="#0F766E" />
      </linearGradient>
      <linearGradient id="liquidGrad" x1="0%" y1="100%" x2="0%" y2="0%">
        <stop offset="0%" stopColor="#10B981" />
        <stop offset="100%" stopColor="#A7F3D0" stopOpacity="0.8" />
      </linearGradient>
    </defs>
    {/* Vial */}
    <rect x="25" y="40" width="20" height="30" rx="4" fill="url(#injectionGrad)" filter="url(#inner-shadow)" opacity="0.6"/>
    <rect x="30" y="30" width="10" height="10" fill="#94A3B8" />
    <rect x="25" y="55" width="20" height="15" rx="2" fill="url(#liquidGrad)" />
    {/* Syringe */}
    <motion.g animate={{ rotate: [-5, 5, -5] }} transition={{ repeat: Infinity, duration: 3, ease: "easeInOut" }}>
      <rect x="65" y="20" width="10" height="40" rx="2" fill="url(#injectionGrad)" filter="url(#inner-shadow)" opacity="0.8" transform="rotate(45 70 40)"/>
      <rect x="60" y="15" width="20" height="5" fill="#E2E8F0" transform="rotate(45 70 40)"/>
      <line x1="70" y1="60" x2="70" y2="75" stroke="#E2E8F0" strokeWidth="2" transform="rotate(45 70 40)"/>
      <motion.rect 
        x="66" y="30" width="8" height="20" fill="url(#liquidGrad)" transform="rotate(45 70 40)"
        animate={{ height: [20, 5, 20], y: [30, 45, 30] }}
        transition={{ repeat: Infinity, duration: 4, ease: "easeInOut" }}
      />
    </motion.g>
  </motion.svg>
);

export const CannulaFluidsSVG = () => (
  <motion.svg
    viewBox="0 0 100 100"
    className="w-full h-full drop-shadow-xl"
    animate={{ y: [0, -5, 0] }}
    transition={{ repeat: Infinity, duration: 3.2, ease: "easeInOut", delay: 1 }}
  >
    <defs>
      <linearGradient id="ivGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#22D3EE" />
        <stop offset="100%" stopColor="#1D4ED8" />
      </linearGradient>
      <linearGradient id="dropsGrad" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stopColor="#7DD3FC" />
        <stop offset="100%" stopColor="#0EA5E9" />
      </linearGradient>
    </defs>
    {/* IV Bag */}
    <rect x="35" y="20" width="30" height="40" rx="10" fill="url(#ivGrad)" filter="url(#inner-shadow)" opacity="0.7"/>
    <rect x="45" y="10" width="10" height="10" fill="#94A3B8" rx="2"/>
    <path d="M48 12 L52 12" stroke="#475569" strokeWidth="2"/>
    <rect x="38" y="30" width="24" height="25" fill="#FFFFFF" opacity="0.9" rx="4"/>
    <line x1="42" y1="35" x2="58" y2="35" stroke="#cbd5e1" strokeWidth="2" strokeLinecap="round"/>
    <line x1="42" y1="42" x2="52" y2="42" stroke="#cbd5e1" strokeWidth="2" strokeLinecap="round"/>
    
    {/* Tube & Drop */}
    <path d="M50 60 L50 90" stroke="#94A3B8" strokeWidth="3" fill="none" opacity="0.5"/>
    <motion.circle 
      cx="50" cy="70" r="4" fill="url(#dropsGrad)"
      animate={{ cy: [65, 85], opacity: [1, 0] }}
      transition={{ repeat: Infinity, duration: 1.5, ease: "easeIn" }}
    />
  </motion.svg>
);

export const WoundCareSVG = () => (
  <motion.svg
    viewBox="0 0 100 100"
    className="w-full h-full drop-shadow-xl"
    animate={{ scale: [1, 1.05, 1], rotate: [0, 2, -2, 0] }}
    transition={{ repeat: Infinity, duration: 4, ease: "easeInOut", delay: 0.2 }}
  >
    <defs>
      <linearGradient id="woundGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#FB7185" />
        <stop offset="100%" stopColor="#BE123C" />
      </linearGradient>
    </defs>
    <rect x="25" y="25" width="50" height="50" rx="15" fill="#FFFFFF" filter="url(#inner-shadow)" opacity="0.9" transform="rotate(45 50 50)"/>
    
    <g transform="rotate(45 50 50)">
      <rect x="30" y="40" width="40" height="20" fill="#E2E8F0" opacity="0.5" />
      <rect x="40" y="30" width="20" height="40" fill="#E2E8F0" opacity="0.5" />
      
      {/* Medical Cross */}
      <rect x="42" y="35" width="16" height="30" fill="url(#woundGrad)" rx="2"/>
      <rect x="35" y="42" width="30" height="16" fill="url(#woundGrad)" rx="2"/>
    </g>
    <motion.circle cx="50" cy="50" r="35" fill="none" stroke="#FB7185" strokeWidth="1" strokeDasharray="5 5" animate={{rotate: -360}} transition={{repeat: Infinity, duration: 25, ease: "linear"}} />
  </motion.svg>
);

export const CatheterFeedingSVG = () => (
  <motion.svg
    viewBox="0 0 100 100"
    className="w-full h-full drop-shadow-xl"
    animate={{ y: [0, -4, 0] }}
    transition={{ repeat: Infinity, duration: 3.8, ease: "easeInOut", delay: 0.7 }}
  >
    <defs>
      <linearGradient id="flaskGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#FB923C" />
        <stop offset="100%" stopColor="#D97706" />
      </linearGradient>
    </defs>
    {/* Flask base */}
    <path d="M40 30 L30 70 A10 10 0 0 0 40 80 L60 80 A10 10 0 0 0 70 70 L60 30 Z" fill="url(#flaskGrad)" filter="url(#inner-shadow)" opacity="0.8"/>
    <rect x="45" y="15" width="10" height="15" fill="#CBD5E1" />
    <path d="M40 30 L60 30" stroke="#FFFFFF" strokeWidth="2" opacity="0.5"/>
    <path d="M35 55 L65 55" stroke="#FFFFFF" strokeWidth="2" opacity="0.5"/>
    
    {/* Liquid inside */}
    <motion.path 
      d="M32 65 C 40 60, 60 70, 68 65 L 65 75 A5 5 0 0 1 60 80 L 40 80 A5 5 0 0 1 35 75 Z" 
      fill="#FDE68A" opacity="0.9"
      animate={{ d: [
        "M32 65 C 40 60, 60 70, 68 65 L 65 75 A5 5 0 0 1 60 80 L 40 80 A5 5 0 0 1 35 75 Z",
        "M32 65 C 40 70, 60 60, 68 65 L 65 75 A5 5 0 0 1 60 80 L 40 80 A5 5 0 0 1 35 75 Z",
        "M32 65 C 40 60, 60 70, 68 65 L 65 75 A5 5 0 0 1 60 80 L 40 80 A5 5 0 0 1 35 75 Z"
      ]}}
      transition={{ repeat: Infinity, duration: 2, ease: "easeInOut" }}
    />
    
    {/* Tubes */}
    <path d="M50 15 C 50 -10, 85 0, 85 40" fill="none" stroke="#94A3B8" strokeWidth="4" opacity="0.7"/>
  </motion.svg>
);

export const ElderlyCareSVG = () => (
  <motion.svg
    viewBox="0 0 100 100"
    className="w-full h-full drop-shadow-xl"
    animate={{ y: [0, -5, 0] }}
    transition={{ repeat: Infinity, duration: 4.5, ease: "easeInOut", delay: 0.3 }}
  >
    <defs>
      <linearGradient id="careGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#C084FC" />
        <stop offset="100%" stopColor="#9333EA" />
      </linearGradient>
    </defs>
    <circle cx="50" cy="50" r="35" fill="none" stroke="url(#careGrad)" strokeWidth="4" strokeDasharray="10 5" className="animate-spin-slow" style={{ animationDuration: '30s' }}/>
    
    {/* Heart symbol representing care */}
    <motion.path 
      d="M50 70 C 50 70, 25 50, 25 35 A 15 15 0 0 1 50 30 A 15 15 0 0 1 75 35 C 75 50, 50 70, 50 70 Z" 
      fill="url(#careGrad)" filter="url(#inner-shadow)" opacity="0.9"
      animate={{ scale: [1, 1.1, 1] }}
      transition={{ repeat: Infinity, duration: 2.5, ease: "easeInOut" }}
    />
    {/* Gentle hands holding */}
    <path d="M20 60 Q 50 85 80 60" fill="none" stroke="#FFFFFF" strokeWidth="4" strokeLinecap="round" opacity="0.7"/>
    <path d="M30 65 Q 50 80 70 65" fill="none" stroke="#E2E8F0" strokeWidth="3" strokeLinecap="round" opacity="0.5"/>
  </motion.svg>
);

export const VitalsMonitorSVG = () => (
  <motion.svg
    viewBox="0 0 100 100"
    className="w-full h-full drop-shadow-xl"
    animate={{ y: [0, -3, 0] }}
    transition={{ repeat: Infinity, duration: 3, ease: "easeInOut", delay: 0.8 }}
  >
    <defs>
      <linearGradient id="vitalsGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#F87171" />
        <stop offset="100%" stopColor="#E11D48" />
      </linearGradient>
    </defs>
    {/* Monitor Screen */}
    <rect x="15" y="25" width="70" height="50" rx="6" fill="#1E293B" filter="url(#inner-shadow)" stroke="url(#vitalsGrad)" strokeWidth="2"/>
    <rect x="25" y="75" width="50" height="5" fill="#475569" rx="2" />
    <polygon points="40,80 60,80 55,90 45,90" fill="#334155" />
    
    {/* ECG Wave on screen */}
    <motion.path 
      d="M20 50 L35 50 L42 30 L50 70 L58 50 L80 50" 
      fill="none" stroke="url(#vitalsGrad)" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"
      initial={{ pathOffset: 0 }}
      animate={{ pathOffset: [0, 1] }}
      transition={{ repeat: Infinity, duration: 2, ease: "linear" }}
      style={{ strokeDasharray: "100", strokeDashoffset: "0" }}
    />
    {/* Blinking indicator */}
    <motion.circle 
      cx="75" cy="35" r="3" fill="#34D399"
      animate={{ opacity: [1, 0, 1] }}
      transition={{ repeat: Infinity, duration: 1 }}
    />
  </motion.svg>
);

export const IronIV_SVG = () => (
  <motion.svg
    viewBox="0 0 100 100"
    className="w-full h-full drop-shadow-xl"
    animate={{ y: [0, -5, 0] }}
    transition={{ repeat: Infinity, duration: 3.2, ease: "easeInOut", delay: 1 }}
  >
    <defs>
      <linearGradient id="ironGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#FB7185" />
        <stop offset="100%" stopColor="#9F1239" />
      </linearGradient>
      <linearGradient id="ironDropsGrad" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stopColor="#FDA4AF" />
        <stop offset="100%" stopColor="#E11D48" />
      </linearGradient>
    </defs>
    {/* IV Bag */}
    <rect x="35" y="20" width="30" height="40" rx="10" fill="url(#ironGrad)" filter="url(#inner-shadow)" opacity="0.8"/>
    <rect x="45" y="10" width="10" height="10" fill="#94A3B8" rx="2"/>
    <path d="M48 12 L52 12" stroke="#475569" strokeWidth="2"/>
    <rect x="38" y="30" width="24" height="25" fill="#FFFFFF" opacity="0.9" rx="4"/>
    <line x1="42" y1="35" x2="58" y2="35" stroke="#cbd5e1" strokeWidth="2" strokeLinecap="round"/>
    <line x1="42" y1="42" x2="52" y2="42" stroke="#cbd5e1" strokeWidth="2" strokeLinecap="round"/>
    
    {/* Tube & Drop */}
    <path d="M50 60 L50 90" stroke="#94A3B8" strokeWidth="3" fill="none" opacity="0.5"/>
    <motion.circle 
      cx="50" cy="70" r="4" fill="url(#ironDropsGrad)"
      animate={{ cy: [65, 85], opacity: [1, 0] }}
      transition={{ repeat: Infinity, duration: 1.5, ease: "easeIn" }}
    />
  </motion.svg>
);

export const BloodSamplingSVG = () => (
  <motion.svg
    viewBox="0 0 100 100"
    className="w-full h-full drop-shadow-xl"
    animate={{ y: [0, -6, 0] }}
    transition={{ repeat: Infinity, duration: 3.5, ease: "easeInOut", delay: 0.5 }}
  >
    <defs>
      <linearGradient id="bloodGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#F43F5E" />
        <stop offset="100%" stopColor="#9F1239" />
      </linearGradient>
    </defs>
    {/* Vial */}
    <rect x="40" y="30" width="20" height="40" rx="4" fill="#E2E8F0" filter="url(#inner-shadow)" opacity="0.6"/>
    <rect x="42" y="25" width="16" height="5" fill="#EF4444" rx="1" />
    <path d="M40 50 L60 50" stroke="#FFFFFF" strokeWidth="2" opacity="0.5"/>
    
    <motion.rect 
      x="40" y="55" width="20" height="15" rx="2" fill="url(#bloodGrad)"
      animate={{ height: [15, 20, 15], y: [55, 50, 55] }}
      transition={{ repeat: Infinity, duration: 4, ease: "easeInOut" }}
    />
    
    {/* Blood Drop */}
    <motion.path 
      d="M30 60 C 30 70, 20 80, 20 80 C 20 80, 10 70, 10 60 A 10 10 0 0 1 30 60 Z" 
      fill="url(#bloodGrad)" filter="url(#inner-shadow)" opacity="0.9" transform="rotate(-30 20 60) scale(0.6) translate(10 0)"
      animate={{ scale: [0.6, 0.65, 0.6] }}
      transition={{ repeat: Infinity, duration: 2, ease: "easeInOut" }}
    />
    {/* Needle */}
    <path d="M65 80 L80 20" stroke="#CBD5E1" strokeWidth="3" strokeLinecap="round" />
  </motion.svg>
);

export const StitchRemovalSVG = () => (
  <motion.svg
    viewBox="0 0 100 100"
    className="w-full h-full drop-shadow-xl"
    animate={{ scale: [1, 1.05, 1] }}
    transition={{ repeat: Infinity, duration: 4, ease: "easeInOut", delay: 0.4 }}
  >
    <defs>
      <linearGradient id="scissorGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#14B8A6" />
        <stop offset="100%" stopColor="#0F766E" />
      </linearGradient>
      <linearGradient id="bladeGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#CBD5E1" />
        <stop offset="100%" stopColor="#64748B" />
      </linearGradient>
    </defs>

    {/* Stitch Line */}
    <path d="M20 70 Q 50 60 80 50" fill="none" stroke="#F43F5E" strokeWidth="8" strokeLinecap="round" opacity="0.3" />
    <path d="M25 60 L35 75 M45 55 L55 70 M65 50 L75 65" stroke="#FFFFFF" strokeWidth="3" strokeLinecap="round" opacity="0.8" />

    {/* Scissors */}
    <g transform="rotate(-15 50 50)">
      <motion.path d="M50 50 L30 20" stroke="url(#bladeGrad)" strokeWidth="6" strokeLinecap="round" animate={{ d: ["M50 50 L30 20", "M50 50 L35 25", "M50 50 L30 20"]}} transition={{ repeat: Infinity, duration: 1.5, ease: "easeInOut" }} />
      <motion.path d="M50 50 L70 20" stroke="url(#bladeGrad)" strokeWidth="6" strokeLinecap="round" animate={{ d: ["M50 50 L70 20", "M50 50 L65 25", "M50 50 L70 20"]}} transition={{ repeat: Infinity, duration: 1.5, ease: "easeInOut" }} />
      <circle cx="50" cy="50" r="4" fill="#475569" />
      
      {/* Handles */}
      <motion.g animate={{ rotate: [0, 5, 0] }} transformOrigin="50 50" transition={{ repeat: Infinity, duration: 1.5, ease: "easeInOut" }}>
        <path d="M50 50 L40 70 A10 10 0 1 1 25 65 L50 50" fill="none" stroke="url(#scissorGrad)" strokeWidth="6" filter="url(#inner-shadow)" />
      </motion.g>
      <motion.g animate={{ rotate: [0, -5, 0] }} transformOrigin="50 50" transition={{ repeat: Infinity, duration: 1.5, ease: "easeInOut" }}>
        <path d="M50 50 L60 70 A10 10 0 1 0 75 65 L50 50" fill="none" stroke="url(#scissorGrad)" strokeWidth="6" filter="url(#inner-shadow)" />
      </motion.g>
    </g>
  </motion.svg>
);

export const OxygenMeasurementSVG = () => (
  <motion.svg
    viewBox="0 0 100 100"
    className="w-full h-full drop-shadow-xl"
    animate={{ scale: [1, 1.05, 1] }}
    transition={{ repeat: Infinity, duration: 3, ease: "easeInOut", delay: 0.1 }}
  >
    <defs>
      <linearGradient id="oxygenGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#38BDF8" />
        <stop offset="100%" stopColor="#0284C7" />
      </linearGradient>
      <linearGradient id="lungsGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#A7F3D0" />
        <stop offset="100%" stopColor="#10B981" />
      </linearGradient>
    </defs>
    
    {/* Trachea */}
    <path d="M50 20 L50 40" stroke="#94A3B8" strokeWidth="6" strokeLinecap="round" />
    <path d="M50 40 L40 50" stroke="#94A3B8" strokeWidth="5" strokeLinecap="round" />
    <path d="M50 40 L60 50" stroke="#94A3B8" strokeWidth="5" strokeLinecap="round" />

    {/* Lungs */}
    <motion.path 
      d="M45 45 C 20 40, 15 70, 30 85 C 40 95, 45 70, 45 45 Z" 
      fill="url(#lungsGrad)" filter="url(#inner-shadow)" opacity="0.8"
      animate={{ scale: [1, 1.1, 1], x: [0, -1, 0] }}
      transition={{ repeat: Infinity, duration: 3, ease: "easeInOut" }}
    />
    <motion.path 
      d="M55 45 C 80 40, 85 70, 70 85 C 60 95, 55 70, 55 45 Z" 
      fill="url(#lungsGrad)" filter="url(#inner-shadow)" opacity="0.8"
      animate={{ scale: [1, 1.1, 1], x: [0, 1, 0] }}
      transition={{ repeat: Infinity, duration: 3, ease: "easeInOut" }}
    />

    {/* O2 bubbles */}
    <motion.circle cx="30" cy="30" r="4" fill="url(#oxygenGrad)" animate={{ cy: [30, 20], opacity: [1, 0] }} transition={{ repeat: Infinity, duration: 1.5, delay: 0.2 }} />
    <motion.circle cx="70" cy="35" r="3" fill="url(#oxygenGrad)" animate={{ cy: [35, 25], opacity: [1, 0] }} transition={{ repeat: Infinity, duration: 1.8, delay: 0.5 }} />
    <motion.circle cx="50" cy="15" r="5" fill="url(#oxygenGrad)" animate={{ cy: [15, 5], opacity: [1, 0] }} transition={{ repeat: Infinity, duration: 1.2 }} />
  </motion.svg>
);

// --- React Components ---

export interface ServiceCardProps {
  title: string;
  desc: string;
  color: string;
  shadow: string;
  colSpan: string;
  SvgComponent: React.FC;
  isMain?: boolean;
}

const ServiceCard = ({ title, desc, color, shadow, colSpan, SvgComponent, isMain }: ServiceCardProps) => {
  return (
    <motion.div
      className={`group relative overflow-hidden rounded-[2rem] bg-slate-900/40 backdrop-blur-xl border border-white/5 hover:border-white/10 transition-all duration-500 flex flex-col justify-between p-6 md:p-8 ${colSpan}`}
      initial={{ opacity: 0, scale: 0.95 }}
      whileInView={{ opacity: 1, scale: 1 }}
      viewport={{ once: true, margin: "-50px" }}
      transition={{ duration: 0.5 }}
      whileHover={{ y: -5 }}
    >
      <div className={`absolute inset-0 bg-gradient-to-br ${color} opacity-0 group-hover:opacity-5 transition-opacity duration-500`} />
      
      <div className="flex justify-between items-start mb-6">
        <div className={`w-20 h-20 md:w-24 md:h-24 rounded-2xl bg-slate-800/50 border border-white/10 flex items-center justify-center relative overflow-hidden group-hover:shadow-[0_0_40px_rgba(0,0,0,0)] group-hover:${shadow} transition-all duration-500`}>
          <div className={`absolute inset-0 bg-gradient-to-br ${color} opacity-10`} />
          <HolographicPulse />
          <div className="w-16 h-16 md:w-20 md:h-20 relative z-10 p-2">
            <SvgComponent />
          </div>
        </div>
        {/* Tiny visual pulse for the main big tile */}
        {isMain && (
          <span className="flex h-3 w-3 relative">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-cyan-500"></span>
          </span>
        )}
      </div>

      <div>
        <h3 className={`text-xl md:text-2xl font-bold text-white mb-3 group-hover:text-transparent group-hover:bg-clip-text group-hover:bg-gradient-to-r ${color} transition-all duration-300`}>
          {title}
        </h3>
        <p className={`text-slate-400 font-medium leading-relaxed ${isMain ? "text-lg max-w-md" : "text-sm md:text-base"}`}>
          {desc}
        </p>
      </div>
      
      {/* Glass reflection */}
      <div className="absolute -inset-full top-0 z-0 block h-full w-1/2 -skew-x-12 transform bg-gradient-to-r from-transparent via-white/5 to-transparent opacity-0 group-hover:animate-shine" />
    </motion.div>
  );
};

interface ServicesGridProps {
  isRTL: boolean;
}

export function ServicesGrid({ isRTL }: ServicesGridProps) {
  const services = isRTL ? [
    { title: "زيارة تمريضية شاملة", desc: "رعاية تمريضية متكاملة في راحة منزلك بواسطة نخبة من الممرضين المؤهلين.", svg: NursingVisitSVG, color: "from-blue-400 to-indigo-500", shadow: "shadow-blue-500/30", colSpan: "lg:col-span-2 lg:row-span-2", isMain: true },
    { title: "الحقن الوريدي والعضلي", desc: "إعطاء الحقن بجميع أنواعها بأعلى معايير التعقيم.", svg: InjectionsSVG, color: "from-emerald-400 to-teal-500", shadow: "shadow-emerald-500/30", colSpan: "lg:col-span-2" },
    { title: "تركيب الكانيولا والمحاليل", desc: "تركيب الكانيولا الوريدية والمحاليل باحترافية وبدون ألم.", svg: CannulaFluidsSVG, color: "from-cyan-400 to-blue-500", shadow: "shadow-cyan-500/30", colSpan: "lg:col-span-1" },
    { title: "العناية المتقدمة بالجروح", desc: "تغيير على الجروح الجراحية باستخدام أحدث الغيارات.", svg: WoundCareSVG, color: "from-rose-400 to-red-500", shadow: "shadow-rose-500/30", colSpan: "lg:col-span-1" },
    { title: "القسطرة البولية والأنبوب المعدي", desc: "تركيب وتغيير القسطرة البولية وأنبوب التغذية بعناية.", svg: CatheterFeedingSVG, color: "from-orange-400 to-amber-500", shadow: "shadow-orange-500/30", colSpan: "lg:col-span-2" },
    { title: "رعاية كبار السن", desc: "برامج رعاية مخصصة لكبار السن تشمل النظافة والمتابعة.", svg: ElderlyCareSVG, color: "from-purple-400 to-fuchsia-500", shadow: "shadow-purple-500/30", colSpan: "lg:col-span-1" },
    { title: "قياس العلامات الحيوية", desc: "قياس دقيق لضغط الدم، السكر، النبض، ونسبة الأكسجين.", svg: VitalsMonitorSVG, color: "from-red-400 to-rose-500", shadow: "shadow-red-500/30", colSpan: "lg:col-span-1" }
  ] : [
    { title: "Comprehensive Nursing Visit", desc: "Full nursing care in the comfort of your home by highly qualified nurses.", svg: NursingVisitSVG, color: "from-blue-400 to-indigo-500", shadow: "shadow-blue-500/30", colSpan: "lg:col-span-2 lg:row-span-2", isMain: true },
    { title: "IV & IM Injections", desc: "Administration of all types of injections with strict sterilization.", svg: InjectionsSVG, color: "from-emerald-400 to-teal-500", shadow: "shadow-emerald-500/30", colSpan: "lg:col-span-2" },
    { title: "Cannula & IV Fluids", desc: "Professional and painless insertion of IV cannulas and therapeutic fluids.", svg: CannulaFluidsSVG, color: "from-cyan-400 to-blue-500", shadow: "shadow-cyan-500/30", colSpan: "lg:col-span-1" },
    { title: "Advanced Wound Care", desc: "Dressing surgical wounds using the latest medical dressings.", svg: WoundCareSVG, color: "from-rose-400 to-red-500", shadow: "shadow-rose-500/30", colSpan: "lg:col-span-1" },
    { title: "Catheter & Feeding", desc: "Insertion and changing of catheters and feeding tubes with utmost care.", svg: CatheterFeedingSVG, color: "from-orange-400 to-amber-500", shadow: "shadow-orange-500/30", colSpan: "lg:col-span-2" },
    { title: "Elderly Care", desc: "Tailored care programs for the elderly including hygiene and monitoring.", svg: ElderlyCareSVG, color: "from-purple-400 to-fuchsia-500", shadow: "shadow-purple-500/30", colSpan: "lg:col-span-1" },
    { title: "Vitals Monitoring", desc: "Accurate measurement of blood pressure, blood sugar, pulse, and SpO2.", svg: VitalsMonitorSVG, color: "from-red-400 to-rose-500", shadow: "shadow-red-500/30", colSpan: "lg:col-span-1" }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6 auto-rows-fr">
      {services.map((service, idx) => (
        <ServiceCard
          key={idx}
          title={service.title}
          desc={service.desc}
          color={service.color}
          shadow={service.shadow}
          colSpan={service.colSpan}
          SvgComponent={service.svg}
          isMain={service.isMain}
        />
      ))}
    </div>
  );
}
