"use client";

import React, { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { AlertTriangle, PhoneCall, ArrowRight, ActivitySquare } from "lucide-react";

export const VitalsAnomalyScanner = () => {
  const [anomalyCounter, setAnomalyCounter] = useState(0);

  // Simulate incoming anomalies 
  useEffect(() => {
    const interval = setInterval(() => {
      setAnomalyCounter(prev => (prev < 3 ? prev + 1 : prev));
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="relative w-full h-full flex flex-col p-4 z-10">
      
      {/* Header Stats */}
      <div className="flex justify-between items-start mb-6">
        <div>
           <div className="flex items-center gap-2 mb-1">
             <div className="w-2 h-2 rounded-full bg-rose-500 animate-pulse" />
             <h3 className="text-slate-400 text-xs font-bold uppercase tracking-widest">Global IoT Net</h3>
           </div>
           <p className="text-2xl font-black text-white font-mono">{142 - anomalyCounter}</p>
           <p className="text-[10px] text-emerald-400 font-mono tracking-widest uppercase">Nominal Patients</p>
        </div>
        
        <div className="text-right">
           <h3 className="text-rose-400 text-xs font-bold uppercase tracking-widest mb-1">Active Alerts</h3>
           <p className="text-2xl font-black text-rose-500 font-mono animate-pulse">{anomalyCounter}</p>
        </div>
      </div>

      {/* Simulated ECG Graph Area */}
      <div className="relative flex-1 bg-[#1a0f14] border border-rose-900/30 rounded-lg overflow-hidden flex flex-col justify-end p-3 isolation-auto">
         {/* Grid lines */}
         <div 
            className="absolute inset-0 opacity-10 pointer-events-none"
            style={{
              backgroundImage: `linear-gradient(to right, #f43f5e 1px, transparent 1px), linear-gradient(to bottom, #f43f5e 1px, transparent 1px)`,
              backgroundSize: "20px 20px"
            }}
         />

         <AnimatePresence>
            {anomalyCounter > 0 ? (
              <motion.div 
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="relative z-10 bg-rose-950/80 border border-rose-500/50 p-3 rounded backdrop-blur-md"
              >
                 <div className="flex items-start justify-between">
                    <div>
                      <h4 className="flex items-center gap-1.5 text-xs font-bold tracking-widest uppercase text-white mb-1">
                        <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                        SpO2 Drop Detected
                      </h4>
                      <p className="font-mono text-[10px] text-rose-300">Patient: #1042-M</p>
                      <p className="font-mono text-xl font-bold text-rose-400 mt-1">88% <span className="text-[10px] text-rose-500">SpO2</span></p>
                    </div>
                    
                    <button className="flex items-center justify-center p-2 rounded bg-rose-500 hover:bg-rose-400 text-white transition-colors">
                      <PhoneCall className="w-4 h-4" />
                    </button>
                 </div>
                 
                 <button className="mt-3 w-full py-2 bg-slate-900 border border-rose-500/30 text-[10px] font-bold tracking-widest text-slate-300 uppercase hover:bg-rose-900 hover:text-white transition-all flex justify-between items-center px-4 rounded">
                   Dispatch Nearest Nurse
                   <ArrowRight className="w-3 h-3" />
                 </button>
              </motion.div>
            ) : (
              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="absolute inset-0 flex flex-col items-center justify-center opacity-50 z-10"
              >
                 <ActivitySquare className="w-8 h-8 text-emerald-500/30 mb-2" />
                 <p className="text-xs font-mono tracking-widest text-emerald-500/40 uppercase">Scanning Vitals...</p>
              </motion.div>
            )}
         </AnimatePresence>
         
         {/* Simulated running line that shifts color */}
         <div className="absolute bottom-4 inset-x-0 h-0.5 bg-gradient-to-r from-transparent via-emerald-500 to-transparent opacity-30 animate-pulse" />
      </div>

    </div>
  );
};
