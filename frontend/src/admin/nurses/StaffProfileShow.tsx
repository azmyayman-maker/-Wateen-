import React from 'react';
import { useParams } from 'react-router-dom';
import { cn } from '../../lib/utils';
import { staffDossierData, StaffStatus } from './mock-staff-data';
import { 
    MapPin, 
    Star, 
    TrendingUp, 
    CalendarCheck, 
    Clock, 
    FileText,
    CheckCircle2,
    AlertCircle,
    Power
} from 'lucide-react';
import { Typography } from '@mui/material';

// --- Custom Components for Bento Box ---

const GlassPanel = ({ children, className }: { children: React.ReactNode, className?: string }) => (
    <div className={cn("bg-[#0a0a1a]/80 backdrop-blur-2xl border border-white/5 rounded-3xl p-6 relative overflow-hidden", className)}>
        {/* Subtle top reflection */}
        <div className="absolute top-0 inset-x-0 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />
        {children}
    </div>
);

const StatusIndicator = ({ status }: { status: StaffStatus }) => {
    let colorClass, dotClass, text;
    
    switch (status) {
        case 'متاح للتوجيه':
            colorClass = 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20';
            dotClass = 'bg-emerald-400 shadow-[0_0_12px_currentColor] animate-pulse';
            text = 'متاح للتوجيه | Online';
            break;
        case 'في زيارة نشطة':
            colorClass = 'text-[#FFB300] bg-[#FFB300]/10 border-[#FFB300]/20';
            dotClass = 'bg-[#FFB300] shadow-[0_0_12px_currentColor] animate-pulse';
            text = 'في زيارة نشطة | Active';
            break;
        case 'غير متصل':
        default:
            colorClass = 'text-slate-400 bg-slate-800/50 border-white/5';
            dotClass = 'bg-slate-500 shadow-none';
            text = 'غير متصل | Offline';
            break;
    }

    return (
        <div className={cn("flex items-center gap-3 px-4 py-2 rounded-full border", colorClass)}>
            <div className={cn("w-2.5 h-2.5 rounded-full", dotClass)} style={{ color: "currentColor" }} />
            <span className="text-sm font-bold tracking-wide" style={{ fontFamily: "'Outfit', sans-serif" }}>
                {text}
            </span>
        </div>
    );
};

export const StaffProfileShow = () => {
    const { id } = useParams();
    
    // In a real app, React Admin's useShowController fetches data.
    // For this tier-0 override, we match the ID from our hyper-realistic mock data.
    const staff = staffDossierData.find(s => s.id === id) || staffDossierData[0];

    if (!staff) return <div>Loading Dossier...</div>;

    return (
        <div className="w-full max-w-7xl mx-auto pb-12 pt-10 px-4 min-h-screen text-white" dir="rtl">

            {/* BENTO BOX GRID LAYOUT */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                
                {/* SECTION A: Profile Header (Spans full width on mobile, 2 cols on md) */}
                <GlassPanel className="md:col-span-2 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
                    <div className="flex items-center gap-6">
                        <div className="w-24 h-24 rounded-full bg-gradient-to-br from-[#0066FF] to-[#00E5FF] p-1 shadow-[0_0_30px_rgba(0,102,255,0.3)]">
                            <div className="w-full h-full rounded-full bg-[#050505] flex items-center justify-center overflow-hidden">
                                <img src={staff.avatarUrl} alt={staff.name} className="w-full h-full object-cover" />
                            </div>
                        </div>
                        <div>
                            <h2 className="text-3xl font-bold mb-2" style={{ fontFamily: "'Amiri', 'Outfit', sans-serif" }}>{staff.name}</h2>
                            <p className="text-[#00E5FF] font-medium text-lg" style={{ fontFamily: "'Outfit', sans-serif" }}>{staff.specialization}</p>
                            <div className="flex gap-4 mt-3 text-sm text-slate-400 font-mono">
                                <span>ID: {staff.nationalId}</span>
                                <span className="text-white/20">|</span>
                                <span>نقابة: {staff.syndicateNumber}</span>
                            </div>
                        </div>
                    </div>
                    
                    <div className="flex flex-col items-end gap-4 w-full md:w-auto mt-4 md:mt-0 border-t md:border-t-0 md:border-r border-white/5 pt-4 md:pt-0 md:pr-6">
                        <StatusIndicator status={staff.status} />
                        <button className="flex items-center gap-2 px-4 py-2 rounded-xl bg-red-500/10 text-red-400 border border-red-500/20 hover:bg-red-500/20 transition-colors w-full md:w-auto justify-center">
                            <Power className="w-4 h-4" />
                            <span className="text-xs font-bold">فرض حالة &quot;غير متصل&quot;</span>
                        </button>
                    </div>
                </GlassPanel>

                {/* SECTION C: Performance Metrics (1 col) */}
                <GlassPanel className="flex flex-col justify-center gap-6">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="p-2 rounded-lg bg-[#0066FF]/20 text-[#0066FF]">
                                <TrendingUp className="w-5 h-5" />
                            </div>
                            <span className="text-slate-400 text-sm">إجمالي العوائد</span>
                        </div>
                        <span className="text-xl font-black font-mono text-white tracking-wider">{staff.totalRevenueGenerated.toLocaleString()} ج.م</span>
                    </div>
                    
                    <div className="h-px w-full bg-gradient-to-r from-transparent via-white/10 to-transparent" />
                    
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="p-2 rounded-lg bg-emerald-500/20 text-emerald-400">
                                <CalendarCheck className="w-5 h-5" />
                            </div>
                            <span className="text-slate-400 text-sm">زيارات مكتملة</span>
                        </div>
                        <span className="text-xl font-black font-mono text-white">{staff.completedVisits}</span>
                    </div>

                    <div className="h-px w-full bg-gradient-to-r from-transparent via-white/10 to-transparent" />
                    
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="p-2 rounded-lg bg-[#FFB300]/20 text-[#FFB300]">
                                <Star className="w-5 h-5" />
                            </div>
                            <span className="text-slate-400 text-sm">التقييم العام</span>
                        </div>
                        <span className="text-xl font-black font-mono text-white flex items-center gap-1">
                            {staff.rating} <span className="text-sm text-slate-500">/ 5.0</span>
                        </span>
                    </div>
                </GlassPanel>

                {/* SECTION B: Live Operations Map (2 cols) */}
                <GlassPanel className="md:col-span-2 relative p-0 overflow-hidden min-h-[300px] border border-[#0066FF]/20 shadow-[0_0_30px_rgba(0,102,255,0.05)]">
                    <div className="absolute top-4 right-4 z-10 bg-[#050505]/80 backdrop-blur-md border border-white/10 px-4 py-3 rounded-xl">
                        <h3 className="text-sm font-bold text-white flex items-center gap-2">
                            <MapPin className="w-4 h-4 text-[#00E5FF]" />
                            العمليات الميدانية الحية
                        </h3>
                        {staff.status === 'في زيارة نشطة' && staff.currentAssignment ? (
                            <div className="mt-2 text-xs text-slate-300 flex flex-col gap-1">
                                <p><span className="text-slate-500">الموقع:</span> {staff.currentAssignment.patientLocation}</p>
                                <p><span className="text-slate-500">الخدمة:</span> {staff.currentAssignment.service}</p>
                                <p className="text-[#FFB300] font-bold"><span className="text-slate-500">الحالة:</span> {staff.currentAssignment.eta}</p>
                            </div>
                        ) : (
                            <p className="mt-2 text-xs text-slate-500">لا توجد زيارات ميدانية نشطة حالياً</p>
                        )}
                    </div>
                    {/* Placeholder for actual Leaflet Map. Using a sleek grid background for the mock */}
                    <div className="w-full h-full absolute inset-0 bg-[#020205]" style={{
                        backgroundImage: 'radial-gradient(#0066FF33 1px, transparent 1px)',
                        backgroundSize: '20px 20px'
                    }}>
                        {/* Radar scanning effect */}
                        <div className="absolute inset-0 bg-gradient-to-tr from-[#0066FF]/10 to-transparent opacity-50 mix-blend-screen" />
                        {staff.status === 'في زيارة نشطة' && (
                            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2">
                                <div className="w-4 h-4 bg-[#00E5FF] rounded-full shadow-[0_0_20px_#00E5FF] animate-ping absolute inset-0" />
                                <div className="w-4 h-4 bg-[#00E5FF] rounded-full relative z-10" />
                            </div>
                        )}
                    </div>
                </GlassPanel>

                {/* SECTION D: Activity Timeline (1 col) */}
                <GlassPanel className="flex flex-col">
                    <h3 className="text-lg font-bold mb-6 flex items-center gap-2">
                        <Clock className="w-5 h-5 text-[#0066FF]" />
                        سجل النشاط الأخير
                    </h3>
                    <div className="flex-1 relative pl-2 pr-4 border-r-2 border-white/5 space-y-6">
                        {staff.recentActivity.map((activity, idx) => (
                            <div key={activity.id} className="relative pr-6">
                                {/* Timeline Dot */}
                                <div className={cn(
                                    "absolute top-1 -right-[7px] w-3 h-3 rounded-full border-2 border-[#0a0a1a]",
                                    activity.status === 'success' ? "bg-emerald-400" : "bg-[#FFB300]"
                                )} />
                                <div className="flex flex-col gap-1">
                                    <span className="text-xs font-mono text-slate-500">{activity.date}</span>
                                    <div className="flex items-start gap-2">
                                        {activity.status === 'success' ? (
                                            <CheckCircle2 className="w-4 h-4 text-emerald-400 mt-0.5 shrink-0" />
                                        ) : (
                                            <AlertCircle className="w-4 h-4 text-[#FFB300] mt-0.5 shrink-0" />
                                        )}
                                        <p className="text-sm text-slate-300 leading-snug">{activity.action}</p>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                    <button className="mt-6 w-full py-3 rounded-xl border border-white/5 hover:bg-white/5 transition-colors text-xs font-bold text-slate-400 flex items-center justify-center gap-2">
                        <FileText className="w-4 h-4" />
                        السجل الكامل
                    </button>
                </GlassPanel>

            </div>
        </div>
    );
};
