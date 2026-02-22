import React, { useState } from 'react';

// --- MOCK DATA ---
const INCOMING_REQUESTS = [
  { id: "REQ-01", name: "محمود عبد الله", service: "عناية مركزة منزلية", distance: "1.2 كم", timeAgo: "الآن", urgent: true, delay: "50ms" },
  { id: "REQ-02", name: "خديجة الرحمن", service: "تغيير ضمادات", distance: "3.5 كم", timeAgo: "منذ 2 دقيقة", urgent: false, delay: "150ms" },
  { id: "REQ-03", name: "إبراهيم حسن", service: "تحليل دم شامل", distance: "4.1 كم", timeAgo: "منذ 5 دقيقة", urgent: false, delay: "250ms" },
];

const STATS = [
  { id: "stat-1", label: "زيارات اليوم", value: "4", accent: "text-cyan-500" },
  { id: "stat-2", label: "النقاط المكتسبة", value: "320", accent: "text-purple-500" },
  { id: "stat-3", label: "التقييم", value: "4.9", accent: "text-amber-500" },
];

export const NurseDashboard: React.FC = () => {
  const [isOnline, setIsOnline] = useState(false);

  return (
    <div className="relative min-h-screen bg-slate-50 dark:bg-[#0B1120] text-slate-900 dark:text-slate-100 font-sans selection:bg-cyan-200 overflow-hidden select-none" dir="rtl">
      {/* Self-contained Keyframes */}
      <style dangerouslySetInnerHTML={{__html: `
        @keyframes slideSnap {
          from { opacity: 0; transform: translateX(60px); }
          to { opacity: 1; transform: translateX(0); }
        }
        @keyframes radarPing {
          0% { transform: scale(0.8); opacity: 0.6; }
          100% { transform: scale(2.5); opacity: 0; }
        }
        .animate-slide-snap { opacity: 0; animation: slideSnap 0.25s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards; }
        .animate-radar-ring-1 { animation: radarPing 2s infinite ease-out; }
        .animate-radar-ring-2 { animation: radarPing 2s infinite ease-out 0.5s; }
        .animate-radar-ring-3 { animation: radarPing 2s infinite ease-out 1s; }
      `}} />

      {/* Main Container - Mobile First Focus */}
      <main className="max-w-xl mx-auto px-4 py-6 space-y-8">

        {/* ===== HEADER & POWER SWITCH ===== */}
        <section className="flex flex-col items-center justify-center space-y-6 pt-2">
          {/* Avatar + Radar */}
          <div className="relative flex items-center justify-center w-28 h-28">
            {/* Radar Rings (only visible when online) */}
            {isOnline && (
              <>
                <div className="absolute inset-0 rounded-full border-2 border-cyan-400/50 animate-radar-ring-1" />
                <div className="absolute inset-0 rounded-full border-2 border-cyan-300/40 animate-radar-ring-2" />
                <div className="absolute inset-0 rounded-full border-2 border-cyan-200/30 animate-radar-ring-3" />
              </>
            )}
            {/* Avatar */}
            <div className={`relative w-20 h-20 rounded-full border-4 overflow-hidden shadow-lg z-10 transition-all duration-300 ${
              isOnline ? 'border-cyan-400 shadow-[0_0_25px_rgba(6,182,212,0.4)]' : 'border-slate-200 shadow-sm'
            }`}>
              <div className="w-full h-full bg-gradient-to-br from-slate-700 to-slate-900 flex items-center justify-center text-white font-black text-2xl">
                م
              </div>
            </div>
          </div>

          <div className="text-center space-y-1">
            <h1 className="text-3xl font-black tracking-tight text-slate-900 dark:text-slate-100">مركز القيادة</h1>
            <p className="text-sm font-extrabold text-slate-400 uppercase tracking-[0.2em]">حالة التوفر الميداني</p>
          </div>

          <div className="flex items-center justify-between mb-8 select-none">
            <div className="flex flex-col text-start">
              <h2 className="text-3xl font-black tracking-tight text-slate-900 dark:text-slate-100">لوحة التحكم التكتيكية</h2>
              <p className="text-slate-500 dark:text-slate-400 font-medium">متابعة الطلبات المباشرة وحالة الميدان</p>
            </div>
            <div className="flex flex-col items-end text-end">
              <span className="text-sm font-bold text-slate-400 uppercase tracking-widest leading-none mb-1">الحالة الآن</span>
              <p className={`text-xl font-black ${isOnline ? 'text-emerald-500' : 'text-slate-400 dark:text-slate-500'}`}>
                {isOnline ? 'متصل وجاهز' : 'غير متصل'}
              </p>
            </div>
          </div>

          {/* ===== MASSIVE POWER SWITCH ===== */}
          <button 
            onClick={() => setIsOnline(!isOnline)}
            className={`
              relative flex items-center w-[22rem] h-[5rem] p-2 rounded-[2.5rem] cursor-pointer
              transition-all duration-500 ease-[cubic-bezier(0.34,1.56,0.64,1)] active:scale-95 outline-none overflow-hidden
              ${isOnline 
                ? 'bg-[#0F172A] shadow-[inset_0_2px_10px_rgba(0,0,0,0.5),0_15px_30px_rgba(6,182,212,0.25)] border border-slate-800' 
                : 'bg-[#E2E8F0] dark:bg-slate-800/50 dark:border-white/10 shadow-[inset_0_2px_8px_rgba(0,0,0,0.05)] border border-slate-300'
              }
            `}
            role="switch"
            aria-checked={isOnline}
            aria-label="تبديل حالة التوفر"
          >
            {/* Background animated text layer */}
            <div className="absolute inset-0 flex items-center justify-between px-10 pointer-events-none z-0">
              {/* Text on the RIGHT (shown when offline) */}
              <span className={`text-[1.35rem] font-black tracking-wide transition-all duration-500 transform ${
                !isOnline ? 'text-slate-500 dark:text-slate-400 translate-x-0 opacity-100' : 'text-transparent -translate-x-8 opacity-0'
              }`}>
                غير متاح
              </span>
              
              {/* Text on the LEFT (shown when online) */}
              <span className={`text-[1.35rem] font-black tracking-wide transition-all duration-500 transform ${
                isOnline ? 'text-cyan-400 translate-x-0 opacity-100 drop-shadow-[0_0_12px_rgba(34,211,238,0.4)]' : 'text-transparent translate-x-8 opacity-0'
              }`}>
                متاح للخدمة
              </span>
            </div>

            {/* The Knob */}
            <div 
              className={`
                relative flex items-center justify-center w-[4rem] h-[4rem] rounded-full shrink-0
                transform transition-all duration-500 ease-[cubic-bezier(0.34,1.56,0.64,1)] z-10
                ${isOnline 
                  ? 'translate-x-0 bg-[#00BCD4] shadow-[0_0_30px_rgba(0,188,212,0.8),inset_0_-3px_6px_rgba(0,0,0,0.1),inset_0_3px_6px_rgba(255,255,255,0.4)]' 
                  : '-translate-x-[17rem] bg-white dark:bg-slate-700 shadow-[0_4px_12px_rgba(0,0,0,0.15),inset_0_-2px_4px_rgba(0,0,0,0.05)]'
                }
              `}
            >
              <div className={`transition-transform duration-500 ease-[cubic-bezier(0.34,1.56,0.64,1)] ${isOnline ? 'rotate-0 scale-100' : '-rotate-180 scale-90'}`}>
                {isOnline ? (
                  <svg className="w-8 h-8 text-white drop-shadow-md" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                ) : (
                  <svg className="w-8 h-8 text-slate-400 dark:text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M18.364 5.636a9 9 0 010 12.728m0 0l-2.829-2.829m2.829 2.829L21 21M15.536 8.464a5 5 0 010 7.072m0 0l-2.829-2.829m-4.243 2.829a4.978 4.978 0 01-1.414-2.83m-1.414 5.658a9 9 0 01-2.167-9.238L5 3z" />
                  </svg>
                )}
              </div>
            </div>
          </button>
        </section>

        {/* ===== TACTICAL QUICK STATS ===== */}
        <section>
          <div className="grid grid-cols-3 gap-3">
            {STATS.map(stat => (
              <div key={stat.id} className="bg-white dark:bg-slate-900/50 dark:backdrop-blur-3xl border-2 border-slate-200 dark:border-white/10 rounded-2xl p-4 flex flex-col items-center justify-center gap-1 shadow-sm hover:shadow-md hover:border-slate-300 dark:hover:border-cyan-500/30 dark:shadow-[0_8px_30px_rgb(0,0,0,0.5)] transition-all duration-200">
                <span className={`text-3xl font-black ${stat.accent}`}>{stat.value}</span>
                <span className="text-xs font-extrabold text-slate-400 uppercase tracking-widest text-center">{stat.label}</span>
              </div>
            ))}
          </div>
        </section>

        {/* ===== INCOMING REQUESTS (Snap Physics) ===== */}
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-black tracking-tight text-slate-900 dark:text-slate-100 text-start">الطلبات الواردة</h2>
            {isOnline && (
              <span className="flex items-center gap-2 text-xs font-black text-cyan-700 dark:text-cyan-300 bg-cyan-50 dark:bg-cyan-500/10 px-3 py-1.5 rounded-full border border-cyan-100 dark:border-cyan-500/20">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-500 opacity-75" />
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-cyan-600" />
                </span>
                بحث نشط...
              </span>
            )}
          </div>

          <div className="space-y-4">
            {!isOnline ? (
              <div className="flex flex-col items-center justify-center py-14 bg-white dark:bg-slate-900/50 dark:backdrop-blur-3xl rounded-2xl border-2 border-dashed border-slate-200 dark:border-white/10 shadow-sm dark:shadow-[0_8px_30px_rgb(0,0,0,0.5)]">
                <div className="w-16 h-16 bg-slate-100 dark:bg-slate-800 rounded-full flex items-center justify-center mb-4">
                  <svg className="w-8 h-8 text-slate-300 dark:text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M18.364 5.636a9 9 0 010 12.728m0 0l-2.829-2.829m2.829 2.829L21 21M15.536 8.464a5 5 0 010 7.072m0 0l-2.829-2.829m-4.243 2.829a4.978 4.978 0 01-1.414-2.83m-1.414 5.658a9 9 0 01-2.167-9.238L5 3z" />
                  </svg>
                </div>
                <p className="text-slate-500 dark:text-slate-400 font-extrabold text-center text-base leading-relaxed px-6">
                  أنت حالياً في وضع غير متاح.
                  <br />
                  قم بتفعيل الحالة لاستقبال الطلبات.
                </p>
              </div>
            ) : (
              INCOMING_REQUESTS.map((request, index) => (
                <div 
                  key={request.id}
                  className="animate-slide-snap bg-white dark:bg-slate-900/50 dark:backdrop-blur-3xl border-s-8 border-s-cyan-500 shadow-lg dark:shadow-[0_8px_30px_rgb(0,0,0,0.5)] dark:hover:shadow-[0_20px_40px_-15px_rgba(6,182,212,0.15)] rounded-2xl overflow-hidden transition-all active:scale-[0.98]"
                  style={{ animationDelay: request.delay }}
                >
                  <div className="p-5 space-y-4">
                    {/* Request Header */}
                    <div className="flex justify-between items-start select-none">
                      <div className="flex items-center gap-3 flex-wrap">
                        <h3 className="text-xl font-black text-slate-900 dark:text-slate-100">{request.name}</h3>
                        {request.urgent && (
                          <span className="px-2.5 py-1 bg-red-100 dark:bg-red-500/10 text-red-700 dark:text-red-400 text-[11px] font-black rounded-lg uppercase tracking-wider border border-red-200 dark:border-red-500/20">
                            طوارئ
                          </span>
                        )}
                      </div>
                      <span className="text-sm font-extrabold text-slate-400 dark:text-slate-500 shrink-0">{request.timeAgo}</span>
                    </div>

                    {/* Request Details */}
                    <p className="text-base font-extrabold text-slate-600 dark:text-slate-300 text-start">{request.service}</p>
                    
                    <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400 font-extrabold text-sm">
                      <svg className="w-5 h-5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                      {request.distance}
                    </div>

                    {/* MASSIVE Accept Button */}
                    <button className="w-full py-4 bg-slate-900 dark:bg-cyan-600 hover:bg-slate-800 dark:hover:bg-cyan-500 text-white rounded-xl font-black text-lg shadow-md active:scale-[0.98] transition-all duration-150 outline-none focus:ring-4 focus:ring-cyan-500/40">
                      قبول
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </section>

      </main>
    </div>
  );
};

export default NurseDashboard;
