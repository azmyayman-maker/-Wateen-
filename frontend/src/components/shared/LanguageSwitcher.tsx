'use client';

import React, { useEffect, useState, useRef } from 'react';
import { motion, AnimatePresence, useSpring, useMotionValue, useTransform } from 'framer-motion';
import { useLanguage } from '@/lib/i18n';

interface LanguageSwitcherProps {
  /** 'light' for dark backgrounds (white text), 'dark' for light backgrounds */
  variant?: 'light' | 'dark';
  className?: string;
}

export function LanguageSwitcher({ variant = 'light', className = '' }: LanguageSwitcherProps) {
  const { locale, toggleLocale } = useLanguage();
  const [mounted, setMounted] = useState(false);
  const containerRef = useRef<HTMLButtonElement>(null);

  // Magnetic hover effect values
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);
  
  const springConfig = { damping: 25, stiffness: 400 };
  const translateX = useSpring(mouseX, springConfig);
  const translateY = useSpring(mouseY, springConfig);

  useEffect(() => setMounted(true), []);

  const isArabic = locale === 'ar';
  const isLight = variant === 'light';

  const handleMouseMove = (e: React.MouseEvent<HTMLButtonElement>) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    mouseX.set((e.clientX - centerX) * 0.2);
    mouseY.set((e.clientY - centerY) * 0.2);
  };

  const handleMouseLeave = () => {
    mouseX.set(0);
    mouseY.set(0);
  };

  if (!mounted) return null;

  return (
    <motion.button
      ref={containerRef}
      onClick={toggleLocale}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      dir="ltr"
      style={{ x: translateX, y: translateY, transformStyle: 'preserve-3d' }}
      className={`
        group relative inline-flex items-center justify-between
        h-10 w-[84px] p-1 rounded-full
        cursor-pointer select-none
        transition-colors duration-500
        outline-none focus-visible:ring-2 focus-visible:ring-offset-2
        ${isLight
          ? 'bg-white/[0.03] backdrop-blur-xl border border-white/[0.08] hover:border-white/[0.2] focus-visible:ring-cyan-400/50 focus-visible:ring-offset-slate-930'
          : 'bg-slate-950/[0.03] backdrop-blur-xl border border-slate-900/[0.08] hover:border-slate-900/[0.2] focus-visible:ring-cyan-600/50 focus-visible:ring-offset-white'
        }
        ${className}
      `}
      aria-label={isArabic ? 'Switch to English' : 'التبديل إلى العربية'}
    >
      {/* Liquid Indicator Pill */}
      <motion.div
        layoutId="pill"
        className={`
          absolute top-1 h-8 w-[38px] rounded-full z-0
          transition-colors duration-500
          ${isLight
            ? 'bg-gradient-to-br from-cyan-400/20 via-indigo-500/20 to-purple-500/20'
            : 'bg-gradient-to-br from-cyan-600/20 via-indigo-600/20 to-purple-600/20'
          }
        `}
        initial={false}
        animate={{
          left: isArabic ? 4 : 42,
        }}
        transition={{
          type: 'spring',
          stiffness: 300,
          damping: 30,
        }}
      >
        {/* Holographic Grain Overaly */}
        <div className="absolute inset-0 rounded-full opacity-30 mix-blend-overlay pointer-events-none bg-[url('https://grainy-gradients.vercel.app/noise.svg')]" />
        
        {/* Internal Glow */}
        <div className={`
          absolute inset-0 rounded-full blur-[2px] opacity-50
          ${isLight ? 'bg-white/10' : 'bg-cyan-400/5'}
        `} />
      </motion.div>

      {/* Labels */}
      <div className="relative flex-1 text-center flex items-center justify-around h-full z-10 pointer-events-none">
        <span
          className={`
            text-[14px] font-bold leading-none transition-all duration-300
            ${isArabic 
              ? (isLight ? 'text-white scale-110' : 'text-slate-900 scale-110') 
              : (isLight ? 'text-white/30 hover:text-white/50' : 'text-slate-430 hover:text-slate-600')
            }
          `}
          style={{ fontFamily: 'Cairo, system-ui, sans-serif' }}
        >
          ع
        </span>
        
        {/* Separator Line (Animated) */}
        <motion.div 
          className={`h-3 w-[1px] rounded-full transition-colors duration-500 ${isLight ? 'bg-white/10' : 'bg-slate-900/10'}`}
          animate={{ opacity: isLight ? 0.2 : 0.4 }}
        />

        <span
          className={`
            text-[11px] font-black tracking-widest leading-none transition-all duration-300
            ${!isArabic 
              ? (isLight ? 'text-white scale-110' : 'text-slate-900 scale-110') 
              : (isLight ? 'text-white/30 hover:text-white/50' : 'text-slate-430 hover:text-slate-600')
            }
          `}
        >
          EN
        </span>
      </div>

      {/* Outer Holographic Glow (Spectrum) */}
      <AnimatePresence>
        <motion.div
           initial={{ opacity: 0 }}
           whileHover={{ opacity: 1 }}
           className={`
             absolute -inset-[1px] rounded-full pointer-events-none -z-10 blur-[1px]
             before:absolute before:inset-0 before:rounded-full before:p-[1px]
             before:bg-gradient-to-r before:from-cyan-500/50 before:via-indigo-500/50 before:to-purple-500/50
             before:[mask-image:linear-gradient(white,white)_padding-box,linear-gradient(white,white)]
             before:[mask-composite:compare_xor]
           `}
        />
      </AnimatePresence>

      {/* Radial Hover Highlight */}
      <motion.div
        className="absolute inset-0 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-500 -z-10 pointer-events-none"
        style={{
          background: isLight 
            ? 'radial-gradient(circle at center, rgba(255,255,255,0.06) 0%, transparent 70%)'
            : 'radial-gradient(circle at center, rgba(15,23,42,0.04) 0%, transparent 70%)'
        }}
      />
    </motion.button>
  );
}
