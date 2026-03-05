"use client";

import React from "react";
import { motion } from "framer-motion";
import { Fingerprint, Key, Network, Shield, Lock, Database } from "lucide-react";
import { useLanguage } from "@/lib/i18n";

export function HealthWalletSection() {
  const { t } = useLanguage();

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { 
      opacity: 1,
      transition: { staggerChildren: 0.08 }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 24 },
    visible: { 
      opacity: 1, y: 0, 
      transition: { duration: 0.7, ease: [0.16, 1, 0.3, 1] }
    }
  };

  const PILLARS = [
    {
      icon: Fingerprint,
      title: t.healthWallet.zkpTitle,
      tag: "ZKP",
      desc: t.healthWallet.zkpDesc,
      gradient: "from-violet-500/20 to-indigo-500/10",
      iconColor: "text-violet-400",
      borderColor: "border-violet-500/15",
    },
    {
      icon: Key,
      title: t.healthWallet.didTitle,
      tag: "DID",
      desc: t.healthWallet.didDesc,
      gradient: "from-cyan-500/20 to-blue-500/10",
      iconColor: "text-cyan-400",
      borderColor: "border-cyan-500/15",
    },
    {
      icon: Shield,
      title: t.healthWallet.immutableTitle,
      tag: "Immutable",
      desc: t.healthWallet.immutableDesc,
      gradient: "from-emerald-500/20 to-teal-500/10",
      iconColor: "text-emerald-400",
      borderColor: "border-emerald-500/15",
    },
    {
      icon: Lock,
      title: t.healthWallet.patientOwnedTitle,
      tag: "Patient-Owned",
      desc: t.healthWallet.patientOwnedDesc,
      gradient: "from-amber-500/20 to-orange-500/10",
      iconColor: "text-amber-400",
      borderColor: "border-amber-500/15",
    },
  ];

  const STATS = [
    { value: "AES-256", label: t.healthWallet.statEncryption },
    { value: "100%", label: t.healthWallet.statOwnership },
    { value: "24/7", label: t.healthWallet.statProtection },
  ];

  return (
    <div 
      className="absolute inset-0 w-full h-full flex items-center bg-[#050B14] overflow-y-auto overflow-x-hidden md:overflow-hidden rounded-xl sm:rounded-2xl md:rounded-[2.5rem] select-none shadow-[0_0_120px_-20px_rgba(79,70,229,0.15)] ring-1 ring-white/5"
      style={{ transformStyle: "preserve-3d" }}
    >
      {/* Ambient Glow */}
      <div 
        className="absolute top-1/2 left-1/4 -translate-y-1/2 w-[500px] h-[700px] bg-indigo-500/8 mix-blend-screen blur-[140px] pointer-events-none rounded-full" 
        style={{ transform: "translateZ(-50px)" }} 
      />
      
      {/* Background Grid */}
      <div 
        className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.015)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.015)_1px,transparent_1px)] bg-[size:3rem_3rem] [mask-image:radial-gradient(ellipse_60%_60%_at_50%_50%,#000_20%,transparent_100%)] pointer-events-none opacity-50" 
        style={{ transform: "translateZ(-20px)" }} 
      />

      <div className="w-full h-full mx-auto px-3 sm:px-4 md:px-8 lg:px-12 xl:px-20 2xl:px-28 relative z-10 flex items-center py-4 md:py-0" style={{ transformStyle: "preserve-3d" }}>
        <div className="grid grid-cols-1 lg:grid-cols-[1.1fr_0.9fr] gap-6 md:gap-10 xl:gap-20 w-full" style={{ transformStyle: "preserve-3d" }}>
          
          {/* Right Column: Typography + Pillars */}
          <motion.div 
            className="flex flex-col space-y-3 sm:space-y-4 lg:space-y-7"
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-100px" }}
          >
            {/* Header */}
            <div className="space-y-2 sm:space-y-3.5">
              <motion.div variants={itemVariants} className="inline-flex items-center space-x-2 space-x-reverse bg-indigo-500/10 border border-indigo-500/20 rounded-full px-3 py-1.5 w-fit backdrop-blur-md">
                <Network className="w-3 h-3 text-indigo-400" />
                <span className="text-xs font-semibold text-indigo-300 tracking-wide">{t.healthWallet.badge}</span>
              </motion.div>

              <motion.h2 variants={itemVariants} className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl xl:text-[3.5rem] 2xl:text-[4rem] font-bold text-white tracking-tight leading-snug pb-1 sm:pb-2">
                {t.healthWallet.title1}
                <br />
                <span className="text-transparent bg-clip-text bg-gradient-to-l from-indigo-400 via-white to-slate-400">
                  {t.healthWallet.title2}
                </span>
              </motion.h2>

              <motion.p variants={itemVariants} className="text-xs sm:text-sm md:text-base xl:text-lg text-slate-400 max-w-xl leading-relaxed mt-2 sm:mt-4">
                {t.healthWallet.description.split(/(مصر|Egypt)/).map((part, i) => 
                  part === "مصر" || part === "Egypt" ? (
                    <span key={i} className="egypt-gradient">{part}</span>
                  ) : (
                    part
                  )
                )} <span className="text-slate-200 font-medium">{t.healthWallet.hyperledger}</span>. {t.healthWallet.zkpDesc}
              </motion.p>
            </div>

            {/* 4 Tech Pillars — 2×2 Grid */}
            <motion.div variants={containerVariants} className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
              {PILLARS.map((pillar, idx) => {
                const Icon = pillar.icon;
                return (
                  <motion.div 
                    key={idx}
                    variants={itemVariants}
                    className={`group relative p-2.5 sm:p-3.5 rounded-xl bg-white/[0.015] border ${pillar.borderColor} hover:border-white/15 transition-all duration-500 overflow-hidden`}
                  >
                    {/* Hover gradient */}
                    <div className={`absolute inset-0 bg-gradient-to-br ${pillar.gradient} opacity-0 group-hover:opacity-100 transition-opacity duration-500`} />
                    
                    <div className="relative z-10">
                      <div className="flex items-center gap-2.5 mb-2">
                        <div className="w-8 h-8 rounded-lg bg-white/[0.04] border border-white/[0.06] flex items-center justify-center group-hover:bg-white/[0.08] transition-colors duration-300">
                          <Icon className={`w-4 h-4 ${pillar.iconColor}`} />
                        </div>
                        <div className="flex items-center gap-2">
                          <h3 className="text-sm font-bold text-white leading-tight">{pillar.title}</h3>
                          <span className="text-[9px] font-mono font-semibold text-slate-500 bg-white/[0.04] px-1.5 py-0.5 rounded">{pillar.tag}</span>
                        </div>
                      </div>
                      <p className="text-[11px] text-slate-400 leading-relaxed">{pillar.desc}</p>
                    </div>
                  </motion.div>
                );
              })}
            </motion.div>

            {/* Trust Stats Strip */}
            <motion.div variants={itemVariants} className="flex items-center gap-2 sm:gap-3 pt-1">
              {STATS.map((stat, i) => (
                <div 
                  key={i} 
                  className="flex-1 text-center py-2 sm:py-3 rounded-xl bg-white/[0.02] border border-white/[0.05] backdrop-blur-sm"
                >
                  <div className="text-sm sm:text-base md:text-lg font-bold text-white font-mono tracking-tight">{stat.value}</div>
                  <div className="text-[9px] sm:text-[10px] text-slate-500 font-medium mt-0.5">{stat.label}</div>
                </div>
              ))}
            </motion.div>

          </motion.div>

          {/* Left Column: Shader — Hidden on mobile */}
          <motion.div 
            className="hidden lg:flex w-full items-center justify-center lg:justify-end"
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 1.5, ease: "easeOut" }}
          >
            <div className="h-[400px] lg:h-[500px] xl:h-[600px] w-full max-w-[500px] lg:max-w-[650px] xl:max-w-[800px] relative flex items-center justify-center">
              
              {/* Central Glowing Core */}
              <div className="absolute inset-0 bg-indigo-500/5 rounded-full blur-[80px] pointer-events-none" />

              <div 
                className="absolute inset-0 z-10 w-full h-full pointer-events-none flex items-center justify-center"
                style={{ WebkitMaskImage: 'radial-gradient(ellipse at center, black 30%, transparent 70%)' }}
              >
                <iframe 
                  src="/shaders/blockchain-orb.html" 
                  frameBorder="0" 
                  width="100%" 
                  height="100%" 
                  className="w-[120%] h-[120%] border-0 pointer-events-auto mix-blend-screen opacity-80"
                ></iframe>
              </div>
            </div>
          </motion.div>

        </div>
      </div>
    </div>
  );
}

export default HealthWalletSection;
