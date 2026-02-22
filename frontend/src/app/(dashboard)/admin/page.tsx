"use client";

import React, { useEffect } from "react";
import { useLanguage } from "@/lib/i18n";
import { motion } from "framer-motion";

import { TacticalMissionRadar } from "@/components/dashboard/admin/TacticalMissionRadar";
import { ActiveMissionsFeed } from "@/components/dashboard/admin/ActiveMissionsFeed";
import { VitalsAnomalyScanner } from "@/components/dashboard/admin/VitalsAnomalyScanner";
import { DynamicPricingConsole } from "@/components/dashboard/admin/DynamicPricingConsole";
import { SecurityKYCQueue } from "@/components/dashboard/admin/SecurityKYCQueue";

export default function AdminDashboard() {
  const { dir } = useLanguage();

  return (
    <div
      dir={dir}
      className={`relative min-h-screen w-full bg-slate-950 text-slate-50 overflow-hidden font-sans select-none flex flex-col p-4 md:p-6 lg:p-8`}
    >
      {/* Background Deep Tactical Pulse */}
      <div className="absolute inset-0 z-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-emerald-900/10 blur-[120px] rounded-full mix-blend-screen" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-cyan-900/10 blur-[120px] rounded-full mix-blend-screen" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-full bg-[radial-gradient(circle_at_center,rgba(0,0,0,0)_0%,rgba(2,6,23,1)_100%)] opacity-80" />
      </div>

      <div className="relative z-10 w-full max-w-[1920px] mx-auto h-full flex flex-col gap-6">
        
        {/* Header Strip */}
        <header className="flex items-center justify-between border-b border-white/5 pb-4">
          <div className="flex items-center gap-4">
            <div className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
            </div>
            <div>
              <h1 className="text-2xl font-black tracking-tight text-white uppercase drop-shadow-[0_0_10px_rgba(255,255,255,0.1)] pb-1">
                Omni-Command Center
              </h1>
              <p className="text-sm font-medium text-emerald-400/80 uppercase tracking-[0.2em]">
                System Status: Nominal
              </p>
            </div>
          </div>
          
          <div className="flex gap-4">
            {/* Clock / Quick Stats placeholder */}
            <div className="flex flex-col items-end">
              <span className="text-xs text-slate-500 font-mono tracking-widest">LOCAL TIME</span>
              <span className="text-lg font-mono font-bold text-slate-300">16:55:00</span>
            </div>
          </div>
        </header>

        {/* Tactical Omni-Grid Layout */}
        <div className="flex-1 grid grid-cols-1 md:grid-cols-12 gap-6 h-[calc(100vh-140px)] min-h-[800px]">
          
          {/* Left Column: Radar & Active Missions (col-span 7) */}
          <div className="md:col-span-12 lg:col-span-8 xl:col-span-9 flex flex-col gap-6 h-full">
            {/* Radar / Map View Placeholder */}
            <div className="flex-1 rounded-2xl border border-white/10 bg-slate-900/40 backdrop-blur-xl shadow-2xl relative overflow-hidden group">
               <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-cyan-500/50 to-transparent" />
               <div className="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-cyan-500/10 to-transparent" />
               <div className="absolute inset-y-0 left-0 w-px bg-gradient-to-b from-transparent via-cyan-500/10 to-transparent" />
               <div className="absolute inset-y-0 right-0 w-px bg-gradient-to-b from-transparent via-cyan-500/10 to-transparent" />
               <div className="p-6 h-full flex flex-col">
                  <h2 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-4 flex items-center gap-2">
                     <span className="text-cyan-400">01</span> Tactical Radar
                  </h2>
                  <div className="flex-1 rounded-lg bg-slate-950/50 border border-slate-800 flex items-center justify-center overflow-hidden">
                    <TacticalMissionRadar />
                  </div>
               </div>
            </div>

            {/* Bottom Row inside left col: Missions feed & KYC queue */}
            <div className="h-[350px] grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Active Missions Bottom Panel */}
              <div className="h-full rounded-2xl border border-white/10 bg-slate-900/40 backdrop-blur-xl shadow-2xl relative overflow-hidden">
                 <div className="p-6 h-full flex flex-col">
                    <h2 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-4 flex items-center gap-2">
                       <span className="text-cyan-400">02</span> Active Missions
                    </h2>
                    <div className="flex-1 -mx-2 overflow-hidden">
                      <ActiveMissionsFeed />
                    </div>
                 </div>
              </div>

              {/* KYC Queue Panel */}
              <div className="h-full rounded-2xl border border-white/10 bg-slate-900/40 backdrop-blur-xl shadow-2xl relative overflow-hidden">
                 <div className="p-6 h-full flex flex-col">
                    <h2 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-0 flex items-center gap-2">
                       <span className="text-emerald-400">03</span> KYC Verify
                    </h2>
                    <div className="flex-1 -mx-2 overflow-hidden">
                      <SecurityKYCQueue />
                    </div>
                 </div>
              </div>
            </div>
          </div>

          {/* Right Column: Vitals, Pricing (col-span 5) */}
          <div className="md:col-span-12 lg:col-span-4 xl:col-span-3 flex flex-col gap-6 h-full">
            
            {/* Emergency Vitals Anomaly Scanner */}
            <div className="flex-1 rounded-2xl border border-rose-500/20 bg-rose-950/10 backdrop-blur-xl shadow-[0_0_30px_rgba(225,29,72,0.05)] relative overflow-hidden">
                <div className="absolute top-0 inset-x-0 h-1 bg-gradient-to-r from-transparent via-rose-500/50 to-transparent animate-pulse" />
                <div className="h-full flex flex-col">
                  <VitalsAnomalyScanner />
               </div>
            </div>

            {/* Dynamic Pricing Console */}
            <div className="h-[300px] rounded-2xl border border-white/10 bg-slate-900/40 backdrop-blur-xl shadow-2xl relative overflow-hidden">
                <div className="h-full flex flex-col">
                  <DynamicPricingConsole />
               </div>
            </div>

          </div>

        </div>
      </div>
    </div>
  );
}
