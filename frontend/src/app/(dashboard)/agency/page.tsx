'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Users, 
  Map as MapIcon, 
  Zap, 
  Clock, 
  CheckCircle2, 
  TrendingUp, 
  Wallet,
  Settings,
  Bell,
  Navigation
} from 'lucide-react';
import { useLanguage } from '@/lib/i18n';
import Link from 'next/link';

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

export default function AgencyDashboard() {
  const { isRTL, t } = useLanguage();
  const [mounted, setMounted] = useState(false);

  useEffect(() => setMounted(true), []);

  if (!mounted) return null;

  return (
    <div className="space-y-8 pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-black text-white bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
            {isRTL ? 'لوحة تحكم الوكالة' : 'Agency Dashboard'}
          </h1>
          <p className="text-slate-400 font-medium">
            {isRTL ? `مرحباً بك، ${MOCK_STATS.agency_name}` : `Welcome back, ${MOCK_STATS.agency_name}`}
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <div className="px-4 py-2 rounded-xl bg-slate-900/50 border border-emerald-500/20 flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-xs font-bold text-emerald-400 uppercase tracking-widest">
              {isRTL ? 'نظام البث نشط' : 'Dispatch System Active'}
            </span>
          </div>
          <button 
            className="p-2.5 rounded-xl bg-slate-900 border border-white/5 hover:border-white/20 transition-all text-slate-400 hover:text-white"
            aria-label="Open settings"
            title="Open settings"
          >
            <Settings className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Main Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard 
          icon={Clock} 
          label={isRTL ? 'طلبات معلقة' : 'Pending Requests'} 
          value={MOCK_STATS.stats.pending_visits} 
          color="blue"
          trend="+2"
        />
        <StatCard 
          icon={Navigation} 
          label={isRTL ? 'زيارات نشطة' : 'Active Visits'} 
          value={MOCK_STATS.stats.active_visits} 
          color="indigo"
          trend="+12%"
        />
        <StatCard 
          icon={Users} 
          label={isRTL ? 'ممرضين متصلين' : 'Nurses Online'} 
          value={MOCK_STATS.stats.online_nurses} 
          color="emerald"
          trend={`${MOCK_STATS.stats.total_nurses-MOCK_STATS.stats.online_nurses} offline`}
        />
        <StatCard 
          icon={Wallet} 
          label={isRTL ? 'رصيد المحفظة' : 'Wallet Balance'} 
          value={MOCK_STATS.financials.wallet_balance.toLocaleString()} 
          suffix="EGP" 
          color="amber"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Real-time Feed / Review Queue */}
        <div className="lg:col-span-2 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Zap className="w-5 h-5 text-blue-400" />
              {isRTL ? 'طلبات قيد الانتظار' : 'Live Request Queue'}
            </h2>
            <Link 
              href="/agency/dispatch" 
              className="text-sm font-semibold text-blue-400 hover:text-blue-300 transition-colors"
            >
              {isRTL ? 'عرض الكل' : 'View Full Queue'}
            </Link>
          </div>

          <div className="bg-slate-900/40 backdrop-blur-xl border border-white/5 rounded-3xl overflow-hidden shadow-2xl">
            <div className="divide-y divide-white/5">
              {[1, 2, 3].map((_, i) => (
                <div key={i} className="p-6 flex items-center justify-between hover:bg-white/[0.02] transition-colors group">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-2xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center">
                      <Clock className="w-6 h-6 text-blue-400" />
                    </div>
                    <div>
                      <h4 className="font-bold text-white">IV Drip Request</h4>
                      <p className="text-xs text-slate-400">Patient: Ahmed Ali • 1.2km away</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-[10px] font-black text-slate-500 uppercase tracking-tighter bg-slate-800 px-2 py-1 rounded-md">
                      2m ago
                    </span>
                    <button className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold transition-all shadow-lg shadow-blue-600/20 active:scale-95">
                      {isRTL ? 'توزيع' : 'Dispatch'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* System Health / Quick Actions */}
        <div className="space-y-6">
           <h2 className="text-xl font-bold text-white">
             {isRTL ? 'نظرة سريعة' : 'Quick Actions'}
           </h2>
           
           <div className="grid grid-cols-1 gap-4">
             <Link href="/agency/map" className="group p-6 rounded-3xl bg-indigo-500/10 border border-indigo-500/20 hover:bg-indigo-500/15 transition-all">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-12 h-12 rounded-2xl bg-indigo-500/20 flex items-center justify-center text-indigo-400 group-hover:scale-110 transition-transform">
                    <MapIcon className="w-6 h-6" />
                  </div>
                  <TrendingUp className="w-5 h-5 text-indigo-400 opacity-50" />
                </div>
                <h3 className="text-lg font-bold text-white mb-1">{isRTL ? 'خريطة التغطية' : 'Live Coverage Map'}</h3>
                <p className="text-xs text-slate-400">{isRTL ? 'مراقبة الممرضين والزيارات في الوقت الفعلي' : 'Monitor nurses and visits in real-time'}</p>
             </Link>

             <div className="p-6 rounded-3xl bg-emerald-500/10 border border-emerald-500/20">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-12 h-12 rounded-2xl bg-emerald-500/20 flex items-center justify-center text-emerald-400">
                    <CheckCircle2 className="w-6 h-6" />
                  </div>
                  <span className="px-2 py-1 rounded-lg bg-emerald-500/20 text-[10px] font-bold text-emerald-400">AUTO</span>
                </div>
                <h3 className="text-lg font-bold text-white mb-1">{isRTL ? 'آلية التوزيع' : 'Dispatch Protocol'}</h3>
                <p className="text-xs text-slate-400">{isRTL ? 'نظام التوزيع التلقائي نشط حالياً' : 'Automatic dispatch is currently active'}</p>
             </div>
           </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon: Icon, label, value, trend, suffix = '', color }: any) {
  const colors: any = {
    blue: 'from-blue-500/20 to-blue-600/5 border-blue-500/20 text-blue-400',
    indigo: 'from-indigo-500/20 to-indigo-600/5 border-indigo-500/20 text-indigo-400',
    emerald: 'from-emerald-500/20 to-emerald-600/5 border-emerald-500/20 text-emerald-400',
    amber: 'from-amber-500/20 to-amber-600/5 border-amber-500/20 text-amber-400',
  };

  return (
    <motion.div 
      whileHover={{ y: -5 }}
      className={`relative p-6 rounded-3xl bg-gradient-to-br ${colors[color]} border backdrop-blur-md overflow-hidden group shadow-2xl`}
    >
      <div className="flex items-start justify-between mb-4">
        <div className={`p-3 rounded-2xl bg-white/5 border border-white/10 ${colors[color].split(' ')[2]}`}>
          <Icon className="w-6 h-6" />
        </div>
        {trend && (
           <span className="text-[10px] font-bold bg-white/5 px-2 py-1 rounded-lg border border-white/10 uppercase tracking-tighter">
             {trend}
           </span>
        )}
      </div>
      <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">{label}</p>
      <div className="flex items-baseline gap-2">
        <h3 className="text-3xl font-black text-white">{value}</h3>
        {suffix && <span className="text-xs font-bold text-slate-500">{suffix}</span>}
      </div>
      
      {/* Decorative pulse ring */}
      <div className={`absolute -right-4 -bottom-4 w-24 h-24 rounded-full opacity-10 blur-2xl ${colors[color].split(' ')[2].replace('text-', 'bg-')}`} />
    </motion.div>
  );
}
