"use client";

import React from "react";
import { Check, X, Ban, ShieldAlert, Fingerprint } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export const SecurityKYCQueue = () => {
  const queue = [
    {
      id: "NID-84920",
      name: "Applicant 01",
      type: "National ID + Selfie",
      faceScore: 99.9,
      ocrMatch: 95.0,
      status: "pending",
      time: "2m ago"
    },
    {
      id: "SYN-11029",
      name: "Applicant 02",
      type: "Syndicate Card",
      faceScore: 0, 
      ocrMatch: 88.5,
      status: "pending",
      time: "15m ago"
    }
  ];

  return (
    <div className="relative w-full h-full flex flex-col p-4 z-10 overflow-y-auto custom-scrollbar pr-2">
      <div className="flex items-center gap-2 mb-4">
         <ShieldAlert className="w-4 h-4 text-cyan-500" />
         <h3 className="text-slate-400 text-xs font-bold uppercase tracking-widest">Verification Queue</h3>
         <span className="ml-auto bg-cyan-500/20 text-cyan-400 text-[10px] font-mono font-bold px-2 py-0.5 rounded">
           {queue.length} PENDING
         </span>
      </div>

      <div className="flex flex-col gap-3">
        <AnimatePresence>
          {queue.map((item, idx) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ delay: idx * 0.1 }}
              className="bg-slate-900/60 border border-slate-700/50 rounded-lg p-3 hover:border-cyan-500/30 transition-colors"
            >
              <div className="flex justify-between items-start mb-2">
                 <div>
                   <p className="text-sm font-bold text-slate-200">{item.name}</p>
                   <p className="text-[10px] text-slate-500 font-mono tracking-wider">{item.id} • {item.type}</p>
                 </div>
                 <span className="text-[10px] text-slate-500 font-mono">{item.time}</span>
              </div>
            <style>{`
        .holo-grid {
          position: absolute;
          inset: 0;
          background-size: 30px 30px;
          background-image:
            linear-gradient(to right, rgba(0, 255, 255, 0.05) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(0, 255, 255, 0.05) 1px, transparent 1px);
          mask-image: linear-gradient(to bottom, rgba(0,0,0,1) 0%, rgba(0,0,0,0) 100%);
          pointer-events: none;
        }

        .scanning-line {
          position: absolute;
          left: 0;
          right: 0;
          height: 100%;
          background: linear-gradient(
            to bottom,
            transparent,
            rgba(0, 255, 255, 0.05) 50%,
            transparent
          );
          animation: scan-vertical 3s linear infinite;
          pointer-events: none;
        }

        @keyframes scan-vertical {
          0% { transform: translateY(-100%); }
          100% { transform: translateY(100%); }
        }

        .kyc-card {
          position: relative;
          background: rgba(16, 24, 39, 0.6);
          border: 1px solid rgba(0, 255, 255, 0.1);
          backdrop-filter: blur(12px);
          border-radius: 12px;
          padding: 1rem;
          margin-bottom: 0.75rem;
          transition: all 0.3s ease;
        }

        .kyc-card::before {
          content: '';
          position: absolute;
          top: 0; left: 0; right: 0; bottom: 0;
          border-radius: 12px;
          padding: 1px;
          background: linear-gradient(135deg, rgba(0,255,255,0.4), transparent, rgba(255,0,255,0.4));
          -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
          -webkit-mask-composite: xor;
          mask-composite: exclude;
          opacity: 0;
          transition: opacity 0.3s ease;
        }

        .kyc-card:hover::before {
          opacity: 1;
        }
      `}</style>
              {/* AI Confidence Scores */}
              <div className="flex gap-4 mb-3 p-2 bg-slate-950/50 rounded border border-slate-800">
                 {item.faceScore > 0 && (
                   <div className="flex flex-col gap-1">
                      <span className="text-[9px] text-slate-500 uppercase tracking-widest font-bold flex items-center gap-1">
                        <Fingerprint className="w-3 h-3 text-emerald-500/70" /> Face Match
                      </span>
                      <span className={`font-mono font-black text-sm ${item.faceScore > 90 ? 'text-emerald-400' : 'text-amber-400'}`}>
                        {item.faceScore}%
                      </span>
                   </div>
                 )}
                 <div className="flex flex-col gap-1">
                    <span className="text-[9px] text-slate-500 uppercase tracking-widest font-bold flex items-center gap-1">
                      <ShieldAlert className="w-3 h-3 text-cyan-500/70" /> OCR Data
                    </span>
                    <span className={`font-mono font-black text-sm ${item.ocrMatch > 90 ? 'text-emerald-400' : 'text-amber-400'}`}>
                      {item.ocrMatch}%
                    </span>
                 </div>
                 
                 {/* Mini Thumbnail Placeholder */}
                 <div className="ml-auto w-12 h-12 rounded bg-slate-800 border border-slate-700 overflow-hidden flex items-center justify-center opacity-50 grayscale hover:grayscale-0 hover:opacity-100 transition-all cursor-zoom-in">
                    <span className="text-[8px] font-mono text-slate-500">IMG</span>
                 </div>
              </div>

              {/* Tactical Actions */}
              <div className="flex gap-2">
                 <button className="flex-1 flex items-center justify-center gap-1.5 py-1.5 rounded bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 hover:bg-emerald-500 hover:text-white transition-colors text-[10px] font-bold uppercase tracking-widest">
                   <Check className="w-3 h-3" /> Approve
                 </button>
                 <button className="flex-1 flex items-center justify-center gap-1.5 py-1.5 rounded bg-amber-500/10 border border-amber-500/30 text-amber-400 hover:bg-amber-500 hover:text-white transition-colors text-[10px] font-bold uppercase tracking-widest">
                   <X className="w-3 h-3" /> Reject
                 </button>
                 <button className="flex items-center justify-center px-3 py-1.5 rounded bg-rose-500/10 border border-rose-500/30 text-rose-400 hover:bg-rose-500 hover:text-white transition-colors">
                   <Ban className="w-3 h-3" />
                 </button>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      <style>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(15, 23, 42, 0.2); 
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(6, 182, 212, 0.2); 
          border-radius: 4px;
        }
        .custom-scrollbar:hover::-webkit-scrollbar-thumb {
          background: rgba(6, 182, 212, 0.5); 
        }
      `}</style>
    </div>
  );
};
