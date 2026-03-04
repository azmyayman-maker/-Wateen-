'use client';

import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';

// Common Floating Particle Component
const FloatingParticles = ({ colorRgb, count = 15, baseSize = 4 }: { colorRgb: string, count?: number, baseSize?: number }) => {
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  if (!mounted) return null;

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none z-0 mix-blend-screen">
      {[...Array(count)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute rounded-full"
          style={{
            background: `radial-gradient(circle at center, rgba(${colorRgb}, 0.8) 0%, transparent 70%)`,
            width: Math.random() * baseSize * 4 + baseSize,
            height: Math.random() * baseSize * 4 + baseSize,
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
            filter: 'blur(1px)'
          }}
          animate={{
            y: [0, Math.random() * -100 - 50],
            x: [0, (Math.random() - 0.5) * 50],
            opacity: [0, 0.6, 0],
            scale: [0.5, 1.5, 0.5]
          }}
          transition={{
            duration: Math.random() * 4 + 3,
            repeat: Infinity,
            ease: "linear",
            delay: Math.random() * 5
          }}
        />
      ))}
    </div>
  );
};

// 1. Fluid Drops (IV Drips, Iron)
const FluidDrops = ({ colorRgb }: { colorRgb: string }) => (
  <div className="absolute inset-0 overflow-hidden rounded-3xl pointer-events-none">
    <FloatingParticles colorRgb={colorRgb} count={8} baseSize={6} />
    <motion.div 
      className="absolute top-0 left-1/4 w-1 h-12 rounded-full"
      style={{ background: `linear-gradient(to bottom, transparent, rgba(${colorRgb}, 0.8))` }}
      animate={{ y: [-50, 200], opacity: [0, 1, 0] }}
      transition={{ duration: 2.5, repeat: Infinity, ease: 'easeIn', delay: 0.5 }}
    />
    <motion.div 
      className="absolute top-0 right-1/3 w-1 h-16 rounded-full"
      style={{ background: `linear-gradient(to bottom, transparent, rgba(${colorRgb}, 0.6))` }}
      animate={{ y: [-50, 200], opacity: [0, 1, 0] }}
      transition={{ duration: 3, repeat: Infinity, ease: 'easeIn', delay: 1.2 }}
    />
  </div>
);

// 2. Crimson Pulse (Blood Sampling, Vitals)
const CrimsonPulse = ({ colorRgb }: { colorRgb: string }) => (
  <div className="absolute inset-0 overflow-hidden rounded-3xl pointer-events-none flex items-center justify-center">
    <FloatingParticles colorRgb={colorRgb} count={20} baseSize={3} />
    <motion.div
        className="absolute inset-0 rounded-3xl"
        style={{ border: `2px solid rgba(${colorRgb}, 0.4)` }}
        animate={{ scale: [1, 1.1, 1], opacity: [0.5, 0, 0.5] }}
        transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
    />
    <motion.div
        className="absolute inset-0 rounded-3xl"
        style={{ border: `1px solid rgba(${colorRgb}, 0.2)` }}
        animate={{ scale: [0.9, 1.3, 0.9], opacity: [0.8, 0, 0.8] }}
        transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut', delay: 0.2 }}
    />
  </div>
);

// 3. Comfort Orange (Wound Care, Injections)
const ComfortGlow = ({ colorRgb }: { colorRgb: string }) => (
  <div className="absolute inset-0 overflow-hidden rounded-3xl pointer-events-none flex items-center justify-center">
     <motion.div
        className="absolute w-[150%] h-[150%] rounded-full blur-[40px] mix-blend-screen"
        style={{ background: `conic-gradient(from 0deg at 50% 50%, transparent, rgba(${colorRgb}, 0.2), transparent)` }}
        animate={{ rotate: 360 }}
        transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
     />
     <FloatingParticles colorRgb={colorRgb} count={12} baseSize={5} />
  </div>
);

// 4. Oxygen Flow (Home Oxygen)
const OxygenFlow = ({ colorRgb }: { colorRgb: string }) => (
  <div className="absolute inset-0 overflow-hidden rounded-3xl pointer-events-none">
     <FloatingParticles colorRgb={colorRgb} count={25} baseSize={2} />
     <motion.div
        className="absolute -bottom-10 left-0 w-full h-[150%] opacity-30"
        style={{ background: `linear-gradient(to top, rgba(${colorRgb}, 0.4), transparent)` }}
        animate={{ y: [0, -20, 0], scaleY: [1, 1.1, 1] }}
        transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
     />
  </div>
);

// 5. Surgical Precision (Catheters, Post-Surgery)
const SurgicalPrecision = ({ colorRgb }: { colorRgb: string }) => (
  <div className="absolute inset-0 overflow-hidden rounded-3xl pointer-events-none">
    {/* Scanning Line */}
    <motion.div
      className="absolute top-0 left-0 w-full h-0.5 shadow-[0_0_10px_rgba(255,255,255,0.8)]"
      style={{ background: `rgba(${colorRgb}, 0.8)` }}
      animate={{ y: [0, 150, 0] }}
      transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
    />
    {/* Grid Background */}
    <div 
      className="absolute inset-0 opacity-20" 
      style={{ 
        backgroundImage: `linear-gradient(rgba(${colorRgb}, 0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(${colorRgb}, 0.3) 1px, transparent 1px)`,
        backgroundSize: '20px 20px'
      }} 
    />
  </div>
);


export function ServiceHeroFactory({ heroType, colorRgb }: { heroType: string, colorRgb: string }) {
  switch (heroType) {
    case 'fluid-drops':
      return <FluidDrops colorRgb={colorRgb} />;
    case 'crimson-pulse':
      return <CrimsonPulse colorRgb={colorRgb} />;
    case 'comfort-orange':
      return <ComfortGlow colorRgb={colorRgb} />;
    case 'oxygen-flow':
      return <OxygenFlow colorRgb={colorRgb} />;
    case 'surgical-precision':
      return <SurgicalPrecision colorRgb={colorRgb} />;
    default:
      return <FloatingParticles colorRgb={colorRgb} />;
  }
}
