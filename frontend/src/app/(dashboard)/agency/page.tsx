"use client";

import React, { useState, useEffect, useRef } from 'react';
import { motion, animate } from 'framer-motion';
import { useLanguage } from '@/lib/i18n';
import Link from 'next/link';
import { BeamsBackground } from '@/components/ui/BeamsBackground';
import { 
  ActiveOrdersIcon, 
  AvailableStaffIcon, 
  CoverageAreasIcon, 
  TodayRevenueIcon,
  AnimatedSettingsIcon,
  AnimatedZapIcon,
  AnimatedClockIcon
} from '@/components/icons/KineticIcons';
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer 
} from 'recharts';

// Mock data based on the API response we implemented
const MOCK_STATS = {
  agency_name: "Wateen Care Cairo",
  stats: {
    pending_visits: 5,
    active_visits: 12,
    completed_today: 8,
    online_nurses: 15,
    total_nurses: 42,
  },
  financials: {
    daily_revenue: 1250,
    wallet_balance: 8540.20,
  },
  settings: {
    dispatch_mode: 'AUTO',
    has_coverage: true,
  }
};

const chartData = [
  { time: '08:00', operations: 24 },
  { time: '10:00', operations: 13 },
  { time: '12:00', operations: 38 },
  { time: '14:00', operations: 39 },
  { time: '16:00', operations: 48 },
  { time: '18:00', operations: 38 },
  { time: '20:00', operations: 43 },
];

function AnimatedNumber({ value }: { value: number }) {
  const nodeRef = useRef<HTMLSpanElement>(null);
  
  useEffect(() => {
    const node = nodeRef.current;
    if (node) {
      const controls = animate(0, value, {
        duration: 2.5,
        ease: "easeOut",
        onUpdate(val) {
          node.textContent = Math.round(val).toLocaleString();
        }
      });
      return () => controls.stop();
    }
  }, [value]);
  
  return <span ref={nodeRef}>0</span>;
}

export default function CommandCenter() {
  const { isRTL } = useLanguage();
  const [mounted, setMounted] = useState(false);

  useEffect(() => setMounted(true), []);

  if (!mounted) return null;

  return (
    <BeamsBackground>
      <div className="space-y-8 pb-12 relative z-10 w-full max-w-7xl mx-auto" dir={isRTL ? 'rtl' : 'ltr'}>
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-4xl font-black text-white bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400 tracking-tight">
              {isRTL ? 'مركز القيادة' : 'Command Center'}
            </h1>
            <p className="text-slate-400 font-medium mt-1">
              {isRTL ? `نظام إدارة عمليات ${MOCK_STATS.agency_name}` : `Operations Management for ${MOCK_STATS.agency_name}`}
            </p>
          </div>
          
          <div className="flex items-center gap-3">
            <div className="px-5 py-2.5 rounded-xl bg-slate-900/50 backdrop-blur-xl border border-emerald-500/20 shadow-[0_0_15px_rgba(0,200,83,0.1)] flex items-center gap-3">
              <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_8px_rgba(0,200,83,0.8)]" />
              <span className="text-xs font-bold text-emerald-400 uppercase tracking-widest">
                {isRTL ? 'نظام البث نشط' : 'Dispatch System Active'}
              </span>
            </div>
            <button 
              className="p-3 rounded-xl bg-slate-900/50 border border-white/[0.03] hover:border-white/[0.1] transition-all text-slate-400 hover:text-white backdrop-blur-[40px] shadow-[0_8px_30px_rgb(0,0,0,0.5)]"
              aria-label="Open settings"
              title="Open settings"
            >
              <AnimatedSettingsIcon className="w-5 h-5" color="currentColor" />
            </button>
          </div>
        </div>

        {/* The Command Center Grid Layout - Top Row: 4 Metric Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* 1. Active Orders */}
          <MetricCard 
            title={isRTL ? 'الطلبات النشطة' : 'Active Orders'}
            value={MOCK_STATS.stats.active_visits}
            icon={<ActiveOrdersIcon className="w-8 h-8" />}
            trend="+12%"
            hoverColor="rgba(0,102,255,0.15)"
          />

          {/* 2. Available Staff */}
          <MetricCard 
            title={isRTL ? 'الكوادر المتاحة' : 'Available Staff'}
            value={MOCK_STATS.stats.online_nurses}
            icon={<AvailableStaffIcon className="w-8 h-8" />}
            trend={`${MOCK_STATS.stats.total_nurses-MOCK_STATS.stats.online_nurses} offline`}
            hoverColor="rgba(0,200,83,0.15)"
          />

          {/* 3. Coverage Areas */}
          <MetricCard 
            title={isRTL ? 'المناطق المغطاة' : 'Coverage Areas'}
            value={24}
            icon={<CoverageAreasIcon className="w-8 h-8" />}
            trend="Expanded"
            hoverColor="rgba(0,229,255,0.15)"
          />

          {/* 4. Today's Revenue */}
          <MetricCard 
            title={isRTL ? 'إيرادات اليوم' : "Today's Revenue"}
            value={MOCK_STATS.financials.daily_revenue}
            icon={<TodayRevenueIcon className="w-8 h-8" />}
            suffix="EGP"
            trend="+5%"
            hoverColor="rgba(255,179,0,0.15)"
          />
        </div>

        {/* Middle Row (The Radar & Charts) */}
        <div className="grid grid-cols-1 lg:grid-cols-12 md:gap-8 gap-6 pt-4">
          
          {/* Right (RTL Start) - 8 Cols: Live Operations Radar */}
          <div className="lg:col-span-8 space-y-4">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <AnimatedZapIcon className="w-6 h-6" color="#3b82f6" />
              {isRTL ? 'رادار العمليات الحية' : 'Live Operations Radar'}
            </h2>
            <div className="h-[400px] bg-neutral-950/40 backdrop-blur-[40px] border border-white/[0.03] rounded-3xl p-6 shadow-[0_8px_30px_rgb(0,0,0,0.5)] hover:border-white/[0.08] hover:-translate-y-1 transition-all duration-500">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorOper" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#0066FF" stopOpacity={0.4}/>
                      <stop offset="95%" stopColor="#0066FF" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
                  <XAxis dataKey="time" stroke="#ffffff50" axisLine={false} tickLine={false} tickMargin={10} />
                  <YAxis stroke="#ffffff50" axisLine={false} tickLine={false} tickMargin={10} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0A0A1A', borderColor: '#ffffff10', borderRadius: '12px' }}
                    itemStyle={{ color: '#fff' }}
                  />
                  <Area type="monotone" dataKey="operations" stroke="#0066FF" strokeWidth={3} fillOpacity={1} fill="url(#colorOper)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Left (RTL End) - 4 Cols: Recent Alerts/Dispatch Queue */}
          <div className="lg:col-span-4 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-bold text-white flex items-center gap-2">
                <div className="relative flex h-3 w-3">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-3 w-3 bg-amber-500"></span>
                </div>
                {isRTL ? 'أحدث التنبيهات' : 'Recent Alerts'}
              </h2>
              <Link 
                href="/agency/dispatch" 
                className="text-sm font-semibold text-slate-400 hover:text-white transition-colors"
              >
                {isRTL ? 'عرض الكل' : 'View All'}
              </Link>
            </div>
            
            <div className="bg-neutral-950/40 backdrop-blur-[40px] border border-white/[0.03] rounded-3xl overflow-hidden shadow-[0_8px_30px_rgb(0,0,0,0.5)] hover:border-white/[0.08] transition-all duration-500">
              <div className="divide-y divide-white/5">
                {[1, 2, 3, 4].map((_, i) => (
                  <div key={i} className="p-5 flex items-center justify-between hover:bg-white/[0.02] transition-colors group cursor-pointer">
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 rounded-2xl bg-white/5 border border-white/[0.04] flex items-center justify-center shadow-inner">
                        <AnimatedClockIcon className="w-6 h-6" color="#94a3b8" />
                      </div>
                      <div>
                        <h4 className="font-bold text-white text-sm">Emergency IV Drip</h4>
                        <p className="text-xs text-slate-400 mt-0.5">Patient: Ahmed Ali • 1.2km</p>
                      </div>
                    </div>
                    <div className="flex flex-col items-end gap-1.5">
                      <span className="text-[10px] font-black text-slate-500 uppercase tracking-tighter">
                        {2 * (i + 1)}m ago
                      </span>
                      <button className="px-3 py-1 rounded-lg bg-white/5 hover:bg-blue-600 border border-white/5 text-white text-[10px] font-bold transition-all active:scale-95 group-hover:border-blue-500/50">
                        {isRTL ? 'توزيع' : 'Dispatch'}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
          
        </div>
      </div>
    </BeamsBackground>
  );
}

// Ultra-Clear Glassmorphic Card (The Harmony Fix)
function MetricCard({ title, value, icon, trend, suffix = '', hoverColor }: any) {
  return (
    <motion.div 
      whileHover={{ y: -4 }}
      className={`relative p-6 rounded-3xl bg-neutral-950/40 backdrop-blur-[40px] border border-white/[0.03] overflow-hidden group shadow-[0_8px_30px_rgb(0,0,0,0.5)] transition-all duration-500`}
      style={{
        // Dynamically apply the soft glow on hover based on the passed color
        '--hover-glow': hoverColor
      } as any}
      // Tailwind arbitrary values don't support dynamic variables easily for deep shadows without plugins, 
      // so we will use a small inline style trick or just rely on the class hover effect for a generic glow if needed.
      // Better approach: we mapped the hover color directly using inline style for box-shadow on hover via Framer Motion, 
      // but to keep it simple with standard tailwind, we can use an absolute inset shadow element.
    >
      <div 
        className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500"
        style={{ boxShadow: `inset 0 0 20px ${hoverColor}` }}
      />
      
      <div className="relative z-10 flex items-start justify-between mb-6">
        <div className="w-14 h-14 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center p-3 shadow-inner">
          {icon}
        </div>
        {trend && (
           <span className="text-[10px] font-bold bg-white/5 px-2 py-1.5 rounded-lg border border-white/10 uppercase tracking-tighter text-slate-300 group-hover:bg-white/10 transition-colors">
             {trend}
           </span>
        )}
      </div>
      
      <div className="relative z-10">
        <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">{title}</p>
        <div className="flex items-baseline gap-2">
          <h3 className="text-4xl font-black text-white tracking-tight">
            <AnimatedNumber value={value} />
          </h3>
          {suffix && <span className="text-sm font-bold text-slate-500">{suffix}</span>}
        </div>
      </div>
    </motion.div>
  );
}
