"use client";

import React from 'react';
import { WateenAnimatedLogo } from './WateenAnimatedLogo';

// --- MOCK DATA ---
const ACTIVE_BOOKING = {
  id: "BKG-9921",
  title: "زيارة منزلية قادمة",
  description: "الممرض أحمد في طريقه إليك",
  time: "اليوم، 10:30 صباحاً",
  status: "في الطريق",
  nurse: { name: "أحمد رياض", role: "ممرض أول" },
};

const SERVICES = [
  { id: 1, title: "التمريض المنزلي", description: "رعاية متكاملة في راحة منزلك", icon: "nurse", delay: "0ms" },
  { id: 2, title: "التحاليل المخبرية", description: "سحب العينات وتوصيل النتائج", icon: "lab", delay: "100ms" },
  { id: 3, title: "العلاج الطبيعي", description: "برامج تأهيلية متخصصة", icon: "therapy", delay: "200ms" },
  { id: 4, title: "رعاية كبار السن", description: "مرافقة طبية وعناية مستمرة", icon: "heart", delay: "300ms" },
];

const HISTORY = [
  { id: 101, title: "تحليل دم شامل", date: "15 أكتوبر 2025", status: "completed" as const },
  { id: 102, title: "جلسة علاج طبيعي", date: "10 أكتوبر 2025", status: "cancelled" as const },
  { id: 103, title: "زيارة طبيب عام", date: "1 أكتوبر 2025", status: "completed" as const },
];

// === BREATHING SERVICE ICON (Mandate 2) ===
// Each icon breathes (scale+translate) continuously and reacts to parent hover with magnetic pull.
const BreathingServiceIcon = ({ icon, gradId }: { icon: string; gradId: string }) => {
  const getPath = () => {
    switch (icon) {
      case 'nurse':
        return <path d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />;
      case 'lab':
        return <path d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />;
      case 'therapy':
        return <><path d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" /><path d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></>;
      case 'heart':
        return <path d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />;
      default:
        return <path d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />;
    }
  };

  return (
    <div className="animate-breathe-icon group-hover:scale-125 group-hover:-translate-y-3 group-hover:drop-shadow-[0_10px_15px_rgba(0,136,255,0.4)] transition-all duration-700 ease-out">
      <svg
        className="w-10 h-10"
        viewBox="0 0 24 24"
        fill="none"
        stroke={`url(#${gradId})`}
        strokeWidth={1.5}
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        {getPath()}
        <defs>
          <linearGradient id={gradId} x1="0" y1="0" x2="24" y2="24" gradientUnits="userSpaceOnUse">
            <stop stopColor="#4DEEEA" />
            <stop offset="0.5" stopColor="#0088FF" />
            <stop offset="1" stopColor="#8A2BE2" />
          </linearGradient>
        </defs>
      </svg>
    </div>
  );
};

const StatusIcon = ({ status }: { status: 'completed' | 'cancelled' }) => {
  if (status === 'completed') {
    return (
      <svg className="w-5 h-5 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
      </svg>
    );
  }
  return (
    <svg className="w-5 h-5 text-rose-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
    </svg>
  );
};

export const PatientDashboard: React.FC = () => {
  return (
    <div className="relative min-h-screen bg-[#F8FAFC] dark:bg-[#0B1120] text-slate-900 dark:text-slate-100 font-sans overflow-hidden select-none" dir="rtl">
      {/* Self-contained Keyframes */}
      <style dangerouslySetInnerHTML={{__html: `
        @keyframes breathingShadow {
          0%, 100% { box-shadow: 0 20px 40px -15px rgba(77,238,234,0.15); }
          50% { box-shadow: 0 20px 60px -10px rgba(77,238,234,0.35); }
        }
        @keyframes fadeUp {
          from { opacity: 0; transform: translateY(24px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes breatheIcon {
          0%, 100% { transform: scale(1) translateY(0); }
          50% { transform: scale(1.08) translateY(-3px); }
        }
        .animate-breathing-shadow { animation: breathingShadow 4s ease-in-out infinite; }
        .animate-fade-up { opacity: 0; animation: fadeUp 0.6s ease-out forwards; }
        .animate-breathe-icon { animation: breatheIcon 3s ease-in-out infinite; }
      `}} />

      {/* ===== AMBIENT MESH GRADIENT BACKGROUND ===== */}
      <div className="absolute top-[-10%] start-[-10%] w-[500px] h-[500px] bg-cyan-300/20 mix-blend-multiply dark:mix-blend-screen dark:opacity-20 blur-[120px] rounded-full animate-pulse" />
      <div className="absolute top-[20%] end-[-10%] w-[400px] h-[400px] bg-purple-300/20 mix-blend-multiply dark:mix-blend-screen dark:opacity-20 blur-[120px] rounded-full animate-pulse" style={{animationDelay: '2s'}} />
      <div className="absolute bottom-[-5%] start-[30%] w-[350px] h-[350px] bg-blue-300/15 mix-blend-multiply dark:mix-blend-screen dark:opacity-20 blur-[120px] rounded-full animate-pulse" style={{animationDelay: '4s'}} />

      {/* Main Scrollable Content */}
      <main className="relative z-10 max-w-5xl mx-auto px-5 md:px-8 py-10 md:py-16 space-y-10">

        {/* ===== MANDATE 1: SELF-DRAWING ANIMATED LOGO ===== */}
        <section className="animate-fade-up flex flex-col items-center justify-center py-4">
          <WateenAnimatedLogo width={300} height={90} />
        </section>

        {/* Dashboard Header */}
        <header className="space-y-2 animate-fade-up" style={{animationDelay: '100ms'}}>
          <p className="text-sm font-bold text-[#0088FF]/80 tracking-widest uppercase text-start">صباح الخير</p>
          <h1 className="text-3xl md:text-5xl font-black tracking-tight text-slate-900 dark:text-slate-100 select-none">
              صباح الخير، <span className="bg-gradient-to-l from-cyan-600 to-blue-600 bg-clip-text text-transparent">أحمد</span>
            </h1>
          <p className="text-lg md:text-xl text-slate-500 dark:text-slate-400 font-semibold text-start">
            كيف يمكننا الاعتناء بك اليوم؟
          </p>
        </header>

        {/* ===== ACTIVE BOOKING CARD (Premium Glassmorphism) ===== */}
        <section className="animate-fade-up" style={{animationDelay: '200ms'}}>
          <div className="animate-breathing-shadow bg-white/60 dark:bg-slate-900/50 backdrop-blur-2xl dark:backdrop-blur-3xl border border-white/80 dark:border-white/10 rounded-[2.5rem] p-6 md:p-8 shadow-[0_20px_40px_-15px_rgba(77,238,234,0.25)] dark:shadow-[0_8px_30px_rgb(0,0,0,0.5)] relative overflow-hidden group">
            <div className="absolute -top-20 -end-20 w-60 h-60 bg-gradient-to-br from-cyan-400/10 to-purple-400/10 rounded-full blur-3xl pointer-events-none" />

            <div className="relative flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
              <div className="flex items-start gap-4">
                {/* Pulsing Cyan Dot */}
                <div className="mt-2 relative flex h-5 w-5 shrink-0 items-center justify-center">
                  <span className="absolute inline-flex h-full w-full rounded-full bg-cyan-400/40 animate-ping" />
                  <span className="absolute inline-flex h-3.5 w-3.5 rounded-full bg-cyan-300/50 animate-pulse" />
                  <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-cyan-500 shadow-[0_0_8px_rgba(77,238,234,0.8)]" />
                </div>

                <div className="space-y-2.5">
                  <p className="text-sm font-black text-cyan-600 tracking-wider uppercase text-start">
                    {ACTIVE_BOOKING.status}
                  </p>
                  <h2 className="text-2xl md:text-3xl font-black text-slate-800 dark:text-slate-100 text-start leading-snug">
                    {ACTIVE_BOOKING.title}
                  </h2>
                  <p className="text-base text-slate-500 dark:text-slate-400 font-semibold text-start leading-relaxed">
                    {ACTIVE_BOOKING.description}
                  </p>
                  <div className="flex items-center gap-2 pt-1">
                    <div className="px-4 py-2 bg-white/70 dark:bg-white/5 backdrop-blur-sm rounded-full text-sm font-bold text-slate-600 dark:text-slate-300 flex items-center gap-2 border border-white/60 dark:border-white/10 shadow-sm">
                      <svg className="w-4 h-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      {ACTIVE_BOOKING.time}
                    </div>
                  </div>
                </div>
              </div>

              {/* Nurse Info Pill */}
              <div className="flex items-center gap-4 group cursor-pointer select-none bg-white/50 dark:bg-white/5 backdrop-blur-lg p-4 rounded-[1.5rem] border border-white/70 dark:border-white/10 w-full md:w-auto shadow-sm">
                <div className="w-14 h-14 bg-gradient-to-br from-[#4DEEEA] to-[#0088FF] rounded-full flex items-center justify-center text-white font-black text-xl shadow-[0_4px_15px_rgba(0,136,255,0.3)]">
                  أ
                </div>
                <div className="flex flex-col text-start">
                  <span className="font-black text-slate-800 dark:text-slate-100 text-lg">{ACTIVE_BOOKING.nurse.name}</span>
                  <span className="text-sm font-semibold text-slate-400">{ACTIVE_BOOKING.nurse.role}</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ===== MANDATE 2: BREATHING SERVICE GRID ===== */}
        <section>
          <div className="flex items-center justify-between mb-6">
            <div className="flex flex-col text-start">
              <h2 className="text-xl font-black text-slate-900 dark:text-slate-100 mb-1 select-none">حجز زيارة منزلية</h2>
              <p className="text-slate-500 dark:text-slate-400 text-sm font-medium select-none">نخبة من الممارسين الصحيين في خدمتك</p>
            </div>
            <button className="text-sm font-black text-[#0088FF] hover:text-[#8A2BE2] transition-colors focus:ring-2 focus:ring-[#0088FF]/30 rounded-xl px-3 py-1.5 outline-none">
              عرض الكل
            </button>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {SERVICES.map((service) => (
              <div
                key={service.id}
                className="group animate-fade-up bg-white dark:bg-slate-900/50 dark:backdrop-blur-3xl rounded-[2rem] p-6 shadow-[0_8px_30px_rgb(0,0,0,0.03)] dark:shadow-[0_8px_30px_rgb(0,0,0,0.5)] hover:-translate-y-2 hover:shadow-[0_20px_40px_-15px_rgba(0,0,0,0.08)] dark:hover:shadow-[0_20px_40px_-15px_rgba(6,182,212,0.15)] transition-all duration-500 ease-out cursor-pointer flex flex-col items-start gap-5 border border-white/50 dark:border-white/10 dark:hover:border-cyan-500/30"
                style={{ animationDelay: service.delay }}
              >
                {/* Icon Container — Breathing + Hover Magnetic Pull */}
                <div className="p-4 rounded-[1.25rem] bg-gradient-to-br from-slate-50 to-slate-100/80 dark:from-white/5 dark:to-white/10 group-hover:from-cyan-50 group-hover:to-purple-50 dark:group-hover:from-cyan-500/20 dark:group-hover:to-purple-500/20 transition-all duration-500 shadow-inner dark:shadow-none">
                  <BreathingServiceIcon icon={service.icon} gradId={`grad-${service.id}`} />
                </div>

                <div className="space-y-1.5 text-start">
                  <h4 className="font-black text-lg text-slate-800 dark:text-slate-100 group-hover:text-transparent group-hover:bg-clip-text group-hover:bg-gradient-to-l group-hover:from-[#0088FF] group-hover:to-[#8A2BE2] transition-all duration-300">
                    {service.title}
                  </h4>
                  <p className="text-sm text-slate-400 dark:text-slate-400 leading-relaxed font-semibold">{service.description}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* ===== VISIT HISTORY ===== */}
        <section className="animate-fade-up" style={{animationDelay: '400ms'}}>
          <h3 className="text-2xl font-black text-slate-800 dark:text-slate-100 mb-5 text-start">السجل الطبي الأخير</h3>
          <div className="bg-white/50 dark:bg-slate-900/50 backdrop-blur-xl dark:backdrop-blur-3xl rounded-[2rem] border border-white/70 dark:border-white/10 p-2 shadow-[0_8px_30px_rgb(0,0,0,0.02)] dark:shadow-[0_8px_30px_rgb(0,0,0,0.5)]">
            <ul className="divide-y divide-slate-100/80 dark:divide-white/5">
              {HISTORY.map((item) => (
                <li key={item.id} className="flex items-center justify-between p-4 md:p-5 hover:bg-white/70 dark:hover:bg-white/5 rounded-[1.5rem] cursor-pointer transition-all duration-300 group">
                  <div className="flex items-center gap-4">
                    <div className={`p-3 rounded-[1.25rem] shadow-sm transition-all duration-300 ${
                      item.status === 'completed'
                        ? 'bg-emerald-50 dark:bg-emerald-500/10 text-emerald-500 group-hover:bg-emerald-100 dark:group-hover:bg-emerald-500/20 group-hover:shadow-emerald-100 dark:group-hover:shadow-none'
                        : 'bg-rose-50 dark:bg-rose-500/10 text-rose-400 group-hover:bg-rose-100 dark:group-hover:bg-rose-500/20 group-hover:shadow-rose-100 dark:group-hover:shadow-none'
                    }`}>
                      <StatusIcon status={item.status} />
                    </div>
                    <div className="flex flex-col text-start space-y-0.5">
                      <span className="font-black text-slate-800 dark:text-slate-100 text-base md:text-lg">{item.title}</span>
                      <span className="text-sm font-semibold text-slate-400">{item.date}</span>
                    </div>
                  </div>
                  <button className="p-3 bg-slate-50/80 dark:bg-white/5 rounded-xl text-slate-300 dark:text-slate-500 group-hover:text-[#0088FF] group-hover:bg-white dark:group-hover:bg-white/10 transition-all duration-300 outline-none focus:ring-2 focus:ring-[#0088FF]/30" aria-label="عرض التفاصيل">
                    <svg className="w-5 h-5 rtl:rotate-180" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
                    </svg>
                  </button>
                </li>
              ))}
            </ul>
          </div>
        </section>

      </main>
    </div>
  );
};

export default PatientDashboard;
