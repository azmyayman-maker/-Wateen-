"use client";

import React from "react";
import { motion } from "framer-motion";
import { Award, ShieldCheck, Star, BadgeCheck } from "lucide-react";
import { useLanguage } from "@/lib/i18n";

export const TrustedAgenciesSection = () => {
  const { t, isRTL } = useLanguage();

  const containerVariants = {
    hidden: {},
    visible: { transition: { staggerChildren: 0.1, delayChildren: 0.2 } },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: [0.22, 1, 0.36, 1] } },
  };

  const FEATURES = [
    { icon: Award, title: t.landing.topAgencies, desc: t.landing.topAgenciesDesc },
    { icon: ShieldCheck, title: t.landing.certifiedNurses, desc: t.landing.certifiedNursesDesc },
    { icon: Star, title: t.landing.qualityCare, desc: t.landing.qualityCareDesc },
  ];

  return (
    <div className="relative flex items-center overflow-hidden py-16 md:py-24 w-full" style={{ transformStyle: "preserve-3d" }}>
      {/* Subtle Ambient Glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] md:w-[800px] md:h-[800px] bg-emerald-500/5 mix-blend-screen blur-[100px] md:blur-[120px] rounded-full pointer-events-none" />

      <div className="relative z-10 w-full max-w-[1300px] mx-auto px-4 sm:px-6 md:px-8 lg:px-12 grid grid-cols-1 lg:grid-cols-2 gap-10 md:gap-12 lg:gap-20 items-center">
        
        {/* Visual Column / Video */}
        <motion.div
            className="relative w-full order-1 lg:order-1 flex items-center justify-center perspective-[2000px] px-2 sm:px-0"
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true, amount: 0.2 }}
            transition={{ duration: 1, ease: [0.22, 1, 0.36, 1] }}
            style={{ transformStyle: "preserve-3d", transform: "translateZ(80px)" }}
        >
          {/* Sleek Video Container */}
          <div className="relative w-full aspect-[4/5] sm:aspect-square max-w-[500px] rounded-[1.5rem] md:rounded-[2rem] overflow-hidden shadow-[0_20px_50px_-20px_rgba(0,0,0,0.7)] group z-10 bg-slate-900 border border-white/10 ring-1 ring-white/5">
            
            {/* The Video */}
            <video 
              autoPlay 
              loop 
              muted 
              playsInline
              className="absolute inset-0 w-full h-full object-cover opacity-90 transition-transform duration-[2s] group-hover:scale-105"
            >
              <source src="/videos/agency-partnership.mp4" type="video/mp4" />
              Your browser does not support the video tag.
            </video>

            {/* Gradient Overlay for Text Readability & Premium Fade */}
            <div className="absolute inset-0 bg-gradient-to-tr from-slate-950/80 via-slate-900/20 to-transparent pointer-events-none z-10" />
            
            {/* Inner Border */}
            <div className="absolute inset-0 rounded-[1.5rem] md:rounded-[2rem] border border-white/5 pointer-events-none z-20" />

            {/* Floating Quality Badge */}
            <motion.div 
              className={`absolute bottom-4 md:bottom-8 ${isRTL ? 'right-4 md:right-8' : 'left-4 md:left-8'} z-30 flex items-center gap-2 md:gap-3 bg-slate-900/60 backdrop-blur-md px-3 py-2 md:px-5 md:py-3 rounded-xl md:rounded-2xl border border-white/10 shadow-2xl`}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5, duration: 0.6 }}
            >
              <div className="flex items-center justify-center p-1.5 md:p-2 bg-emerald-500/20 rounded-lg md:rounded-xl border border-emerald-500/30">
                <BadgeCheck className="w-4 h-4 md:w-5 md:h-5 text-emerald-400" />
              </div>
              <div className="flex flex-col">
                <span className="text-white font-bold text-xs md:text-sm tracking-wide">MoH Certified</span>
                <span className="text-slate-300 text-[10px] md:text-xs font-medium">Licensed Agencies Only</span>
              </div>
            </motion.div>
          </div>
        </motion.div>

        {/* Content Column */}
        <motion.div
           variants={containerVariants}
           initial="hidden"
           whileInView="visible"
           viewport={{ once: true, amount: 0.3 }}
           className="flex flex-col justify-center order-2 lg:order-2"
           style={{ translateZ: 120 }}
        >
          {/* Tagline */}
          <motion.div variants={itemVariants} className="inline-flex items-center gap-2 mb-6 px-4 py-2 rounded-full bg-slate-800/50 border border-slate-700/50 w-fit backdrop-blur-sm">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span className="text-slate-300 font-semibold tracking-wide text-xs uppercase">B2B Healthcare Network</span>
          </motion.div>

          {/* Heading */}
          <motion.h2
            variants={itemVariants}
            className="text-3xl md:text-4xl lg:text-5xl font-black text-white leading-[1.15] tracking-tight text-start"
          >
            {t.landing.trustedPartners}
          </motion.h2>

          {/* Description */}
          <motion.p
            variants={itemVariants}
            className="mt-6 text-base md:text-lg text-slate-400 leading-relaxed font-medium text-start max-w-lg"
          >
            {t.landing.trustedPartnersDesc}
          </motion.p>

          {/* Feature Cards - Sleek Layout */}
          <motion.div variants={itemVariants} className="mt-8 md:mt-10 grid gap-3 md:gap-4">
            {FEATURES.map((feature, i) => {
              const Icon = feature.icon;
              return (
                <div key={i} className="group relative flex items-start gap-4 md:gap-5 p-4 md:p-5 rounded-2xl bg-slate-900/40 hover:bg-slate-800/60 border border-slate-800 hover:border-slate-700 transition-all duration-300 backdrop-blur-sm">
                  
                  <div className="flex-shrink-0 w-10 h-10 md:w-12 md:h-12 rounded-xl bg-slate-800/80 border border-slate-700 flex items-center justify-center transition-all duration-300 group-hover:scale-110 group-hover:bg-emerald-500/10 group-hover:border-emerald-500/30 group-hover:shadow-[0_0_15px_rgba(52,211,153,0.15)]">
                    <Icon className="w-4 h-4 md:w-5 md:h-5 text-slate-400 transition-colors duration-300 group-hover:text-emerald-400" />
                  </div>
                  
                  <div className="flex flex-col pt-0.5 text-start flex-1">
                    <span className="text-base md:text-lg font-bold text-slate-100 group-hover:text-white transition-colors duration-300">
                      {feature.title}
                    </span>
                    <span className="text-xs md:text-sm font-medium text-slate-400 mt-1 md:mt-1.5 leading-relaxed">
                      {feature.desc}
                    </span>
                  </div>
                </div>
              );
            })}
          </motion.div>
        </motion.div>

      </div>
    </div>
  );
};
