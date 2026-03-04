import * as React from 'react';
import { Typography } from '@mui/material';
import { Activity } from 'lucide-react';
import { GlowingEffect } from '../../components/ui/glowing-effect';

export const OperationsCenter = () => {
    return (
        <div className="p-8 max-w-7xl mx-auto w-full">
            <div className="mb-8">
                <Typography variant="h4" className="!font-bold !text-transparent !bg-clip-text !bg-gradient-to-l !from-[#0066FF] !to-[#FFB300] flex items-center gap-3">
                    <Activity size={32} className="text-[#0066FF]" />
                    مركز العمليات
                </Typography>
                <Typography variant="body1" className="!text-slate-400 !mt-2 !font-['Amiri',_'Outfit',_sans-serif]">
                    متابعة وتوجيه طلبات الرعاية الصحية في الوقت الفعلي
                </Typography>
            </div>
            
            <div className="relative group rounded-2xl w-full h-[600px] mb-8">
                <div className="absolute inset-0 z-0 transition-opacity duration-300 opacity-0 group-hover:opacity-100 focus-within:opacity-100">
                    <GlowingEffect spread={40} glow={true} disabled={false} inactiveZone={0.01} borderWidth={2} />
                </div>
                <div className="relative z-10 w-full h-full rounded-2xl bg-[#0a0f1c]/80 backdrop-blur-xl border border-white/10 p-6 flex flex-col">
                    <div className="flex items-center justify-between mb-6 pb-4 border-b border-white/10">
                        <Typography variant="h6" className="!font-bold !text-slate-100">
                            طابور الطلبات النشطة
                        </Typography>
                        <div className="flex gap-2">
                            <span className="px-3 py-1 bg-[#FFB300]/20 text-[#FFB300] rounded-full text-sm font-bold border border-[#FFB300]/30 hidden md:block">
                                5 طلبات طارئة
                            </span>
                            <span className="px-3 py-1 bg-[#0066FF]/20 text-[#0066FF] rounded-full text-sm font-bold border border-[#0066FF]/30 hidden md:block">
                                19 طلب مجدول
                            </span>
                        </div>
                    </div>
                    
                    <div className="flex-1 overflow-y-auto scrollbar-hide flex flex-col gap-4 pr-2">
                        {/* Mock Operations List Items */}
                        {[1, 2, 3, 4, 5, 6].map((item) => (
                            <div key={item} className="p-4 rounded-xl bg-white/5 border border-white/5 hover:bg-white/10 transition-colors duration-300 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 cursor-pointer group/item">
                                <div className="flex items-start gap-4">
                                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center font-bold shadow-lg ${item % 2 === 0 ? 'bg-[#FFB300]/20 text-[#FFB300] border border-[#FFB300]/30' : 'bg-[#0066FF]/20 text-[#0066FF] border border-[#0066FF]/30'}`}>
                                        #{1040 + item}
                                    </div>
                                    <div>
                                        <Typography variant="subtitle1" className="!font-bold !text-slate-100">
                                            {item % 2 === 0 ? 'رعاية مركزة منزلية' : 'متابعة ما بعد العملية'}
                                        </Typography>
                                        <Typography variant="body2" className="!text-slate-400">
                                            المريض: أحمد محمود • المعادي، القاهرة
                                        </Typography>
                                    </div>
                                </div>
                                <div className="flex items-center gap-3 w-full sm:w-auto mt-2 sm:mt-0">
                                    <div className="flex-1 sm:flex-none text-right">
                                        <Typography variant="body2" className="!text-slate-300 !font-bold">
                                            قيد البحث عن ممرض
                                        </Typography>
                                        <Typography variant="caption" className="!text-[#FFB300]">
                                            الوقت المتبقي: 14:00 دقيقة
                                        </Typography>
                                    </div>
                                    <button className="px-4 py-2 rounded-lg bg-gradient-to-l from-[#0066FF] to-blue-600 text-white font-bold opacity-0 group-hover/item:opacity-100 transition-opacity duration-300">
                                        توجيه يدوي
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};
