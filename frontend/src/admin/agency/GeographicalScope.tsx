import * as React from 'react';
import { Typography } from '@mui/material';
import { Map as MapIcon, ShieldAlert } from 'lucide-react';
import { GlowingEffect } from '../../components/ui/glowing-effect';
import dynamic from 'next/dynamic';

const CoverageMap = dynamic(() => import('../../components/map/CoverageMap'), { 
    ssr: false,
    loading: () => (
        <div className="w-full h-full flex items-center justify-center bg-slate-900 animate-pulse">
            <Typography className="text-slate-500">جاري تحميل الخريطة التفاعلية...</Typography>
        </div>
    )
});

export const GeographicalScope = () => {
    const handleCoverageChange = (geo: any) => {
        console.log('New coverage:', geo);
    };

    return (
        <div className="p-8 max-w-7xl mx-auto w-full">
            <div className="mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <Typography variant="h4" className="!font-bold !text-transparent !bg-clip-text !bg-gradient-to-l !from-[#0066FF] !to-[#FFB300] flex items-center gap-3">
                        <MapIcon size={32} className="text-[#0066FF]" />
                        النطاق الجغرافي
                    </Typography>
                    <Typography variant="body1" className="!text-slate-400 !mt-2 !font-['Amiri',_'Outfit',_sans-serif]">
                        إدارة التغطية، ورصد الكثافة السكانية، والتحكم في النطاقات الجغرافية لفريق الممرضين.
                    </Typography>
                </div>
                
                <div className="flex bg-[#0a0f1c]/60 backdrop-blur-md p-2 rounded-xl border border-white/10 w-max">
                    <button className="px-6 py-2 bg-[#0066FF]/20 text-white rounded-lg font-bold border border-[#0066FF]/50 shadow-lg text-sm">القاهرة الكبرى</button>
                    <button className="px-6 py-2 text-slate-400 hover:text-slate-200 transition-colors rounded-lg font-semibold text-sm">الجيزة</button>
                    <button className="px-6 py-2 text-slate-400 hover:text-slate-200 transition-colors rounded-lg font-semibold text-sm">الإسكندرية</button>
                </div>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 w-full mb-8">
                <div className="lg:col-span-3 h-[600px] rounded-2xl overflow-hidden border border-white/10">
                    <CoverageMap onCoverageChange={handleCoverageChange} />
                </div>
                
                <div className="lg:col-span-1 flex flex-col gap-6">
                    <div className="relative group rounded-2xl w-full flex-1">
                        <div className="absolute inset-0 z-0 transition-opacity duration-300 opacity-0 group-hover:opacity-100">
                            <GlowingEffect spread={40} glow={true} disabled={false} inactiveZone={0.01} borderWidth={2} />
                        </div>
                        <div className="relative z-10 w-full h-full rounded-2xl bg-[#0a0f1c]/80 backdrop-blur-xl border border-white/10 p-6 flex flex-col">
                            <Typography variant="h6" className="!font-bold !text-slate-100 !mb-4 border-b border-white/10 pb-3">
                                إحصائيات التغطية
                            </Typography>
                            
                            <div className="flex flex-col gap-4 mt-2">
                                <div>
                                    <div className="flex justify-between mb-1">
                                        <Typography variant="body2" className="!text-slate-300 !font-bold">منطقة التجمع الخامس</Typography>
                                        <Typography variant="body2" className="!text-[#0066FF] !font-bold">85%</Typography>
                                    </div>
                                    <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                                        <div className="bg-gradient-to-l from-[#0066FF] to-blue-400 h-2 rounded-full w-[85%]"></div>
                                    </div>
                                </div>
                                
                                <div>
                                    <div className="flex justify-between mb-1">
                                        <Typography variant="body2" className="!text-slate-300 !font-bold">منطقة المعادي</Typography>
                                        <Typography variant="body2" className="!text-emerald-400 !font-bold">92%</Typography>
                                    </div>
                                    <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                                        <div className="bg-gradient-to-l from-emerald-500 to-emerald-400 h-2 rounded-full w-[92%]"></div>
                                    </div>
                                </div>
                                
                                <div>
                                    <div className="flex justify-between mb-1">
                                        <Typography variant="body2" className="!text-slate-300 !font-bold">منطقة مدينة نصر</Typography>
                                        <Typography variant="body2" className="!text-[#FFB300] !font-bold">45%</Typography>
                                    </div>
                                    <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                                        <div className="bg-gradient-to-l from-[#FFB300] to-yellow-400 h-2 rounded-full w-[45%]"></div>
                                    </div>
                                </div>
                            </div>
                            
                            <div className="mt-auto pt-6">
                                <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/20 flex gap-3 text-amber-500 items-start">
                                    <ShieldAlert size={20} className="shrink-0 mt-0.5" />
                                    <div>
                                        <Typography variant="body2" className="!font-bold !mb-1">نقص في الكوادر التمريضية</Typography>
                                        <Typography variant="caption" className="opacity-90 leading-tight">مدينة نصر تشهد طلباً متزايداً مع وجود 3 كادر طبي متاح فقط في المنطقة حالياً.</Typography>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};
