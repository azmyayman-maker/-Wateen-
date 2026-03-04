"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import { Zap, Activity, TrendingUp } from "lucide-react";

export const DynamicPricingConsole = () => {
  const [multiplier, setMultiplier] = useState(1.0);
  
  // AI Prediction Mock
  const aiPrediction = 1.35;
  const variance = (multiplier - aiPrediction).toFixed(2);

  return (
    <div className="relative w-full h-full flex flex-col p-4">
      {/* Current Surge Display */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <h3 className="text-slate-400 text-xs font-bold uppercase tracking-widest mb-1">Global Surge</h3>
          <div className="flex items-baseline gap-2">
            <span className="text-4xl font-black text-emerald-400 font-mono tracking-tighter">
              {multiplier.toFixed(2)}x
            </span>
            <span className="text-sm font-mono text-emerald-500/50">OVR</span>
          </div>
        </div>
        
        {/* AI Suggestion Box */}
        <div className="flex flex-col items-end bg-slate-900/80 border border-indigo-500/30 rounded-lg p-2 px-3">
          <div className="flex items-center gap-1.5 mb-1">
            <Zap className="w-3 h-3 text-indigo-400" />
            <span className="text-[10px] font-bold text-indigo-300 uppercase tracking-wider">AI Suggests</span>
          </div>
          <span className="font-mono text-lg font-bold text-indigo-200">{aiPrediction.toFixed(2)}x</span>
        </div>
      </div>

      {/* Interactive Slider */}
      <div className="relative flex-1 flex flex-col justify-center px-2">
        <div className="flex justify-between text-[10px] text-slate-500 font-mono mb-2">
          <span>1.0x (Normal)</span>
          <span>3.0x (Max)</span>
        </div>
        
        <input 
          type="range" 
          min="1.0" 
          max="3.0" 
          step="0.05" 
          value={multiplier}
          onChange={(e) => setMultiplier(parseFloat(e.target.value))}
          className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer
                     accent-emerald-500 hover:accent-emerald-400 transition-all"
          style={{
            background: `linear-gradient(to right, #10b981 0%, #10b981 ${(multiplier - 1) * 50}%, #1e293b ${(multiplier - 1) * 50}%, #1e293b 100%)`
          }}
        />
        
        <div className="mt-4 flex items-center gap-3">
          <Activity className="w-4 h-4 text-emerald-500/50" />
          <p className="text-xs text-slate-400">
             Variance from AI optimal: 
             <span className={`ml-2 font-mono font-bold ${Number(variance) > 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
               {Number(variance) > 0 ? '+' : ''}{variance}x
             </span>
          </p>
        </div>
      </div>
      
      {/* Execute Button */}
      <motion.button 
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        className="mt-auto w-full py-3 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-bold text-sm tracking-widest hover:bg-emerald-500/20 hover:border-emerald-400 transition-all flex items-center justify-center gap-2"
      >
        <TrendingUp className="w-4 h-4" />
        ENGAGE SURGE MULTIPLIER
      </motion.button>
    </div>
  );
};
