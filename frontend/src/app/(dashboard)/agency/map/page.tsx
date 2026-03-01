'use client';

import React from 'react';
import { ArrowLeft, Filter, Layers, Navigation } from 'lucide-react';
import Link from 'next/link';
import DispatchMap from '@/components/map/DispatchMap';
import { useLanguage } from '@/lib/i18n';

export default function AgencyMapPage() {
  const { isRTL } = useLanguage();
  
  // In a real app, we'd get the agencyId from the signed-in user's context/token
  const agencyId = "4044680601076201931";

  return (
    <div className="h-[calc(100vh-120px)] flex flex-col gap-6">
      {/* Top Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link 
            href="/agency" 
            className="p-2.5 rounded-xl bg-slate-900 border border-white/5 hover:border-white/20 transition-all text-slate-400 hover:text-white"
          >
            <ArrowLeft className={`w-5 h-5 ${isRTL ? 'rotate-180' : ''}`} />
          </Link>
          <div>
            <h1 className="text-2xl font-black text-white">{isRTL ? 'الخريطة المباشرة' : 'Live Fleet Map'}</h1>
            <p className="text-xs text-slate-400 font-medium">Monitoring 15 active nurses in Cairo North</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
           <button className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-900 border border-white/5 text-sm font-semibold text-slate-300 hover:bg-slate-800 transition-all">
             <Filter className="w-4 h-4" />
             {isRTL ? 'تصفية' : 'Filter'}
           </button>
           <button className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-blue-600 text-sm font-bold text-white hover:bg-blue-500 transition-all shadow-lg shadow-blue-600/20">
             <Layers className="w-4 h-4" />
             {isRTL ? 'الطبقات' : 'Layers'}
           </button>
        </div>
      </div>

      {/* Main Map Area */}
      <div className="flex-1 relative">
        <DispatchMap agencyId={agencyId} />
      </div>
    </div>
  );
}
