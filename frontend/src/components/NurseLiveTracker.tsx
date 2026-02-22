import React from 'react';
import { useLanguage } from '@/lib/i18n/context';

// --- MOCK CONSTANTS ---
const MOCK_MAP_BG = "repeating-linear-gradient(-45deg, #f1f5f9 25%, transparent 25%, transparent 75%, #f1f5f9 75%, #f1f5f9), repeating-linear-gradient(-45deg, #f1f5f9 25%, #f8fafc 25%, #f8fafc 75%, #f1f5f9 75%, #f1f5f9)";

export const NurseLiveTracker: React.FC = () => {
  const { dir } = useLanguage();
  
  return (
    <div className="relative w-full h-screen bg-[#F0F4F8] dark:bg-[#0B1120] overflow-hidden font-sans selection:bg-cyan-200 select-none" dir={dir}>
      {/* Self-contained Keyframes */}
      <style dangerouslySetInnerHTML={{__html: `
        @keyframes sonarPing1 {
          0% { transform: scale(0.6); opacity: 0.7; border-color: rgba(34,211,238,0.6); }
          100% { transform: scale(3); opacity: 0; border-color: rgba(34,211,238,0); }
        }
        @keyframes sonarPing2 {
          0% { transform: scale(0.6); opacity: 0.6; border-color: rgba(34,211,238,0.5); }
          100% { transform: scale(3.5); opacity: 0; border-color: rgba(34,211,238,0); }
        }
        @keyframes sonarPing3 {
          0% { transform: scale(0.6); opacity: 0.5; border-color: rgba(34,211,238,0.4); }
          100% { transform: scale(4); opacity: 0; border-color: rgba(34,211,238,0); }
        }
        .sonar-ring-1 { animation: sonarPing1 2.5s infinite ease-out; }
        .sonar-ring-2 { animation: sonarPing2 2.5s infinite ease-out 0.7s; }
        .sonar-ring-3 { animation: sonarPing3 2.5s infinite ease-out 1.4s; }
        @keyframes audioBar {
          0%, 100% { height: 3px; }
          50% { height: 10px; }
        }
        .audio-1 { animation: audioBar 1s infinite ease-in-out; }
        .audio-2 { animation: audioBar 1s infinite ease-in-out 0.25s; }
        .audio-3 { animation: audioBar 1s infinite ease-in-out 0.5s; }
      `}} />

      {/* 1. The Map Environment (Simulated) */}
      <div
        className="absolute inset-0 w-full h-full z-0"
        style={{
          backgroundImage: MOCK_MAP_BG,
          backgroundPosition: '0 0, 25px 25px',
          backgroundSize: '50px 50px',
        }}
      >
        {/* Top fade */}
        <div className="absolute inset-x-0 top-0 h-40 bg-gradient-to-b from-[#F0F4F8] dark:from-[#0B1120] to-transparent pointer-events-none" />
        {/* Bottom fade for island blending */}
        <div className="absolute inset-x-0 bottom-0 h-60 bg-gradient-to-t from-[#F0F4F8]/80 dark:from-[#0B1120]/80 to-transparent pointer-events-none" />
      </div>

      {/* Shield Indicator (Safe Visit) — Top End */}
      <div className="absolute top-5 end-5 z-40">
        <div className="flex items-center gap-2 bg-emerald-500/10 backdrop-blur-md border border-emerald-500/20 px-3.5 py-2 rounded-full shadow-sm">
          <svg className="w-4 h-4 text-emerald-600" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 1.944A11.954 11.954 0 012.166 5C2.056 5.642 2 6.319 2 7c0 5.225 3.34 9.67 8 11.317C14.66 16.67 18 12.225 18 7c0-.682-.057-1.358-.166-2.001A11.954 11.954 0 0110 1.944zM11 14a1 1 0 11-2 0 1 1 0 012 0zm0-7a1 1 0 10-2 0v3a1 1 0 102 0V7z" clipRule="evenodd" />
          </svg>
          <span className="text-xs font-black text-emerald-700 dark:text-emerald-400 tracking-wide">زيارة آمنة</span>
          <div className="flex items-end gap-0.5 h-3 ms-1">
            <div className="w-1 bg-emerald-500 rounded-full audio-1" />
            <div className="w-1 bg-emerald-500 rounded-full audio-2" />
            <div className="w-1 bg-emerald-500 rounded-full audio-3" />
          </div>
        </div>
      </div>

      {/* ETA Header — Top Start */}
      <div className="absolute top-5 start-5 z-40">
        <div className="flex items-center gap-2 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border border-white/60 dark:border-white/10 px-4 py-2 rounded-full shadow-sm dark:shadow-[0_8px_30px_rgb(0,0,0,0.5)]">
          <svg className="w-4 h-4 text-slate-500 dark:text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span className="text-xs font-black text-slate-700 dark:text-slate-200">الوصول خلال <span className="text-cyan-600 dark:text-cyan-400">3 دقائق</span></span>
        </div>
      </div>

      {/* ===== 3. SONAR AVATAR ON MAP ===== */}
      <div className="absolute top-[38%] left-1/2 -translate-x-1/2 -translate-y-1/2 z-20 flex items-center justify-center w-44 h-44">
        {/* Sonar Radar Rings — 3 absolutely positioned divs with staggered delays */}
        <div className="absolute inset-0 rounded-full border-[3px] border-cyan-400/50 sonar-ring-1" />
        <div className="absolute inset-0 rounded-full border-[3px] border-cyan-400/50 sonar-ring-2" />
        <div className="absolute inset-0 rounded-full border-[3px] border-cyan-400/50 sonar-ring-3" />

        {/* Static inner glow */}
        <div className="absolute w-16 h-16 rounded-full bg-cyan-400/20 blur-lg" />

        {/* The Avatar */}
        <div className="relative w-[4.5rem] h-[4.5rem] rounded-full border-4 border-white dark:border-slate-800 overflow-hidden shadow-[0_8px_25px_rgba(6,182,212,0.5)] z-10 bg-slate-200 dark:bg-slate-800">
          <div className="w-full h-full bg-gradient-to-br from-slate-700 to-slate-900 flex items-center justify-center text-white font-black text-2xl">
            أ
          </div>
        </div>
      </div>

      {/* Simulated route line from avatar downward */}
      <div className="absolute top-[52%] left-1/2 -translate-x-1/2 w-0.5 h-[18%] z-10">
        <div className="w-full h-full bg-gradient-to-b from-cyan-400/60 via-cyan-300/30 to-transparent" style={{backgroundSize: '2px 12px', backgroundImage: 'linear-gradient(to bottom, rgba(34,211,238,0.5) 50%, transparent 50%)'}} />
      </div>

      {/* Destination marker */}
      <div className="absolute top-[72%] left-1/2 -translate-x-1/2 z-10 flex flex-col items-center">
        <div className="w-4 h-4 rounded-full bg-white dark:bg-slate-900 border-[3px] border-cyan-500 shadow-md" />
        <span className="mt-1 text-[10px] font-black text-slate-500 dark:text-slate-400 bg-white/80 dark:bg-slate-900/80 px-2 py-0.5 rounded-full shadow-sm">موقعك</span>
      </div>

      {/* ===== 2. THE FLOATING COMMAND ISLAND ===== */}
      <div className="absolute bottom-8 start-4 end-4 z-30">
        <div className="relative max-w-lg mx-auto bg-white/95 dark:bg-slate-900/50 backdrop-blur-3xl rounded-[2.5rem] p-6 shadow-[0_20px_60px_-15px_rgba(0,136,255,0.3)] dark:shadow-[0_8px_30px_rgb(0,0,0,0.5)] border border-white dark:border-white/10">

          {/* ===== FLOATING ACTION BUTTONS (overlapping top edge) ===== */}
          {/* Call FAB */}
          <button className="absolute -top-6 end-6 w-14 h-14 rounded-full bg-cyan-500 shadow-[0_10px_20px_rgba(6,182,212,0.4)] flex items-center justify-center text-white active:scale-95 transition-transform duration-150 outline-none focus:ring-4 focus:ring-cyan-300 hover:bg-cyan-400 z-20">
            <svg className="w-6 h-6 animate-pulse" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
            </svg>
          </button>

          {/* Message FAB */}
          <button className="absolute -top-6 end-24 w-14 h-14 rounded-full bg-white dark:bg-slate-800 shadow-[0_10px_20px_rgba(0,0,0,0.08)] dark:shadow-[0_8px_30px_rgb(0,0,0,0.5)] border border-slate-100 dark:border-white/10 flex items-center justify-center text-slate-400 dark:text-slate-500 hover:text-cyan-500 dark:hover:text-cyan-400 active:scale-95 transition-all duration-150 outline-none focus:ring-4 focus:ring-slate-200 z-20">
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
          </button>

          {/* Island Content */}
          <div className="flex items-center gap-5 pt-2">
            {/* ETA Progress Ring */}
            <div className="relative flex items-center justify-center w-[5rem] h-[5rem] shrink-0">
              <svg className="absolute w-full h-full -rotate-90" viewBox="0 0 36 36">
                <path
                  className="text-slate-100 dark:text-slate-800"
                  strokeWidth="3"
                  stroke="currentColor"
                  fill="none"
                  strokeLinecap="round"
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                />
                <path
                  className="text-cyan-500 drop-shadow-[0_0_6px_rgba(6,182,212,0.5)]"
                  strokeDasharray="75, 100"
                  strokeWidth="3.5"
                  stroke="currentColor"
                  fill="none"
                  strokeLinecap="round"
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                />
              </svg>
              <div className="w-[3.5rem] h-[3.5rem] rounded-full overflow-hidden border-2 border-white dark:border-slate-800 bg-slate-200 dark:bg-slate-800 shadow-sm z-10">
                <div className="w-full h-full bg-gradient-to-br from-slate-700 to-slate-900 flex items-center justify-center text-white font-black text-lg">
                  أ
                </div>
              </div>
            </div>

            {/* Typography */}
            <div className="flex flex-col text-start justify-center flex-1 select-none">
              <span className="text-4xl font-black text-slate-900 dark:text-slate-100 leading-none mb-1.5">3 <span className="text-lg font-extrabold text-slate-400 dark:text-slate-500">دقائق</span></span>
              <h3 className="text-lg font-black text-slate-700 dark:text-slate-200 line-clamp-1">أحمد محمود</h3>
              <span className="text-sm font-extrabold text-cyan-600 dark:text-cyan-400">ممرض طوارئ — في الطريق</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NurseLiveTracker;
