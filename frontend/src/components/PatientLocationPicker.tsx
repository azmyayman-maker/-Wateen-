import React, { useState, useRef } from 'react';
import { useLanguage } from '@/lib/i18n/context';

// --- MOCK CONSTANTS ---
const MOCK_MAP_BG = "repeating-linear-gradient(45deg, #f0f0f0 25%, transparent 25%, transparent 75%, #f0f0f0 75%, #f0f0f0), repeating-linear-gradient(45deg, #f0f0f0 25%, #ffffff 25%, #ffffff 75%, #f0f0f0 75%, #f0f0f0)";

export const PatientLocationPicker: React.FC = () => {
  const [isPanning, setIsPanning] = useState(false);
  const mapRef = useRef<HTMLDivElement>(null);
  const { dir } = useLanguage();

  // Simulate Map Panning
  const handlePointerDown = () => setIsPanning(true);
  const handlePointerUp = () => setIsPanning(false);

  return (
    <div className="relative w-full h-screen bg-white dark:bg-[#0B1120] overflow-hidden font-sans selection:bg-cyan-200 select-none" dir={dir}>
      {/* Inline Styles for Custom Animations strictly for self-contained functionality */}
      <style dangerouslySetInnerHTML={{__html: `
        @keyframes subtlePulse {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-4px); }
        }
        .animate-subtle-pulse {
          animation: subtlePulse 3s ease-in-out infinite;
        }
        @keyframes beaconPulse {
          0% { transform: scale(0.5); opacity: 0.8; }
          100% { transform: scale(2.5); opacity: 0; }
        }
        .animate-beacon-pulse {
          animation: beaconPulse 2.5s cubic-bezier(0.215, 0.610, 0.355, 1) infinite;
        }
      `}} />

      {/* 1. The Map Canvas */}
      <div 
        ref={mapRef}
        className="absolute inset-0 w-full h-full cursor-grab active:cursor-grabbing transition-transform duration-300 z-0"
        style={{
          backgroundImage: MOCK_MAP_BG,
          backgroundPosition: '0 0, 20px 20px',
          backgroundSize: '40px 40px',
          opacity: 0.6
        }}
        onPointerDown={handlePointerDown}
        onPointerUp={handlePointerUp}
        onPointerLeave={handlePointerUp}
        onPointerCancel={handlePointerUp}
        aria-label="خريطة تحدد الموقع"
      >
        {/* Subtle Map Overlays to enhance the "world" illusion */}
        <div className="absolute inset-0 bg-gradient-to-t from-white/90 dark:from-[#0B1120]/90 via-transparent to-white/40 dark:to-[#0B1120]/40 pointer-events-none" />
        <div className="absolute inset-x-0 bottom-[35%] h-[200px] bg-gradient-to-t from-white dark:from-[#0B1120] to-transparent pointer-events-none z-10" />
      </div>

      {/* 2. The Custom "Breathing" Center Pin */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 pointer-events-none z-20 flex flex-col items-center justify-end h-32 w-32 mt-[-4rem]">
        {/* The Drop Zone Beacon (Pulsing expanding ring under the pin) */}
        <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-8 h-8 rounded-full border-2 border-[#4DEEEA]/80 animate-beacon-pulse" />
        <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-2 h-2 rounded-full bg-[#4DEEEA] shadow-[0_0_10px_#4DEEEA]" />

        {/* The SVG Teardrop Pin Container */}
        <div className={`relative transition-all duration-300 ease-out mb-2
            ${isPanning ? '-translate-y-6 drop-shadow-2xl scale-105' : 'animate-subtle-pulse drop-shadow-md'}
        `}>
          {/* Custom Medical Cross / Wateen Pin SVG */}
          <div className="relative">
             <svg width="48" height="64" viewBox="0 0 48 64" fill="none" className="text-white drop-shadow-[0_4px_12px_rgba(0,136,255,0.4)]">
                <path d="M24 0C10.745 0 0 10.745 0 24C0 42 24 64 24 64C24 64 48 42 48 24C48 10.745 37.255 0 24 0Z" fill="url(#pinGradient)" />
                <path d="M24 4C12.954 4 4 12.954 4 24C4 39.5 24 58 24 58C24 58 44 39.5 44 24C44 12.954 35.046 4 24 4Z" fill="white" />
                {/* Wateen Peak/Heart in Center */}
                <path d="M16 26L20 18L26 32L30 22L34 26" stroke="url(#peakGradient)" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
                <defs>
                  <linearGradient id="pinGradient" x1="0" y1="0" x2="48" y2="64" gradientUnits="userSpaceOnUse">
                    <stop stopColor="#0088FF" />
                    <stop offset="1" stopColor="#8A2BE2" />
                  </linearGradient>
                  <linearGradient id="peakGradient" x1="16" y1="18" x2="34" y2="32" gradientUnits="userSpaceOnUse">
                    <stop stopColor="#4DEEEA" />
                    <stop offset="1" stopColor="#0088FF" />
                  </linearGradient>
                </defs>
              </svg>
          </div>
          
          {/* Subtle Shadow underneath the pin that shrinks when panning */}
          <div className={`absolute -bottom-2 left-1/2 -translate-x-1/2 h-1.5 rounded-full bg-slate-900/10 dark:bg-cyan-500/20 blur-sm transition-all duration-300
            ${isPanning ? 'w-4 opacity-30' : 'w-8 opacity-60'}
          `} />
        </div>
      </div>

      {/* 3. The Bottom Action Sheet (Soft-Matte Glass) */}
      <div className="absolute bottom-0 left-0 right-0 bg-white/90 dark:bg-slate-900/80 backdrop-blur-xl dark:backdrop-blur-3xl rounded-t-[2.5rem] shadow-[0_-10px_40px_rgba(0,0,0,0.05)] dark:shadow-[0_-8px_30px_rgb(0,0,0,0.5)] border-t border-white/60 dark:border-white/10 p-6 md:p-8 z-30 transition-transform">
        {/* Drag Handle */}
        <div className="w-12 h-1.5 bg-slate-200 dark:bg-slate-700 rounded-full mx-auto mb-6" />

        <div className="space-y-6 max-w-lg mx-auto">
          {/* Location Information Header */}
          <div className="text-center space-y-1 select-none">
            <h2 className="text-xl font-bold text-slate-800 dark:text-slate-100 tracking-wide">أين تتواجد حالياً؟</h2>
            <p className="text-sm font-semibold text-slate-500 dark:text-slate-400">سيتم توجيه الفريق الطبي إلى هذا الموقع</p>
          </div>

          {/* Location Display Area */}
          <div className="bg-slate-50 dark:bg-slate-800/50 border border-slate-100/80 dark:border-white/5 rounded-2xl p-4 flex items-center gap-4 transition-all hover:bg-slate-100 dark:hover:bg-slate-800">
             <div className="p-3 bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-slate-100 dark:border-slate-700 text-[#0088FF] dark:text-cyan-400">
               <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                 <path strokeLinecap="round" strokeLinejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                 <path strokeLinecap="round" strokeLinejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
               </svg>
             </div>
             <div className="flex-1 flex flex-col text-start justify-center">
               <span className="text-sm font-bold tracking-wider text-slate-400 dark:text-slate-500 uppercase">الموقع المحدد</span>
               <span className="text-lg font-black text-slate-900 dark:text-slate-200 line-clamp-1">المعادي، شارع 9، القاهرة</span>
             </div>
          </div>

          {/* Primary Action Button */}
          <button className="w-full relative group outline-none overflow-hidden rounded-[1.5rem] bg-gradient-to-r from-[#0088FF] to-[#8A2BE2] shadow-[0_8px_20px_rgba(0,136,255,0.25)] hover:shadow-[0_12px_25px_rgba(0,136,255,0.35)] active:scale-[0.97] transition-all duration-150">
            <span className="absolute inset-0 w-full h-full bg-white/20 scale-x-0 group-hover:scale-x-100 origin-left transition-transform duration-500 ease-out" />
            <div className="relative w-full py-4 text-center font-black text-xl text-white tracking-wide">
              تأكيد موقع الطوارئ
            </div>
          </button>
        </div>
      </div>
      
    </div>
  );
};

export default PatientLocationPicker;
