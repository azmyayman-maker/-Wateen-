"use client";

import React from "react";
import { Clock, MapPin, User, ChevronRight } from "lucide-react";
import { motion } from "framer-motion";

export const ActiveMissionsFeed = () => {
  const missions = [
    {
      id: "SHL-4092",
      patient: "Patient A",
      nurse: "N-01 (Nurse)",
      service: "IV Drip",
      zone: "Maadi",
      status: "IN_PROGRESS",
      eta: "—",
    },
    {
      id: "SHL-4093",
      patient: "Patient B",
      nurse: "N-02 (Nurse)",
      service: "Wound Care",
      zone: "Zamalek",
      status: "EN_ROUTE",
      eta: "14m",
    },
    {
      id: "SHL-4094",
      patient: "Patient C",
      nurse: "Pending Match",
      service: "Injection",
      zone: "Nasr City",
      status: "PENDING",
      eta: "—",
    },
    {
      id: "SHL-4095",
      patient: "Patient D",
      nurse: "N-03 (Nurse)",
      service: "Vitals Check",
      zone: "New Cairo",
      status: "COMPLETED",
      eta: "—",
    },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case "IN_PROGRESS": return "bg-indigo-500/20 text-indigo-400 border-indigo-500/50";
      case "EN_ROUTE": return "bg-amber-500/20 text-amber-400 border-amber-500/50";
      case "PENDING": return "bg-rose-500/20 text-rose-400 border-rose-500/50 animate-pulse";
      case "COMPLETED": return "bg-emerald-500/20 text-emerald-400 border-emerald-500/50";
      default: return "bg-slate-500/20 text-slate-400 border-slate-500/50";
    }
  };

  return (
    <div className="relative w-full h-full flex flex-col p-4 overflow-y-auto custom-scrollbar pr-2">
      <div className="flex flex-col gap-3">
        {missions.map((mission, idx) => (
          <motion.div
            key={mission.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.1 }}
            className="group flex flex-col sm:flex-row items-start sm:items-center justify-between p-3 rounded-lg bg-slate-900/50 border border-slate-800 hover:border-cyan-500/30 hover:bg-slate-800/50 transition-all cursor-pointer"
          >
            {/* Left Info */}
            <div className="flex flex-col gap-1.5 flex-1 min-w-0">
               <div className="flex items-center gap-2">
                  <span className="text-[10px] font-mono font-bold text-slate-500 tracking-wider mix-blend-screen">{mission.id}</span>
                  <div className={`px-2 py-0.5 rounded text-[10px] uppercase font-bold tracking-widest border ${getStatusColor(mission.status)}`}>
                    {mission.status}
                  </div>
               </div>
               
               <div className="flex items-center gap-4 mt-1">
                  <div className="flex items-center gap-1.5 text-sm text-slate-300 font-medium">
                     <User className="w-3.5 h-3.5 text-slate-500" />
                     {mission.patient}
                  </div>
                  <div className="flex items-center gap-1.5 text-xs text-slate-400">
                     <MapPin className="w-3.5 h-3.5 text-slate-500" />
                     <span className="truncate max-w-[120px]">{mission.zone}</span>
                  </div>
               </div>
            </div>

            {/* Right Info (Nurse & Action) */}
            <div className="mt-3 sm:mt-0 flex items-center justify-between sm:justify-end gap-6 w-full sm:w-auto">
               <div className="flex flex-col sm:items-end gap-1">
                  <span className="text-xs text-slate-400 font-mono">Assigned: {mission.nurse}</span>
                  {mission.eta !== "—" && (
                     <div className="flex items-center gap-1 text-[10px] font-mono text-amber-500/80">
                        <Clock className="w-3 h-3" /> ETA: {mission.eta}
                     </div>
                  )}
               </div>
               
               <div className="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0 border border-slate-700">
                  <ChevronRight className="w-4 h-4 text-cyan-400" />
               </div>
            </div>
          </motion.div>
        ))}
      </div>
      
      <style jsx global>{`
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
