import React from 'react';
import { cn } from '../../lib/utils';
import { TopToolbar, useRedirect } from 'react-admin';
import { Typography } from '@mui/material';
import { motion } from 'framer-motion';
import { 
    Stethoscope, 
    Activity, 
    Syringe, 
    HeartPulse, 
    Baby, 
    Microscope, 
    Brain, 
    Bone,
    Star,
    MessageCircle,
    UserPlus,
    FileText
} from 'lucide-react';
// TODO: Replace mock data with real data from React Admin data provider (useListContext)
import { staffDossierData, StaffDossier, StaffStatus } from './mock-staff-data';

// Map specializations to icons
const getIconForSpecialization = (specialization: string, className = "w-8 h-8") => {
    if (specialization.includes("طوارئ")) return <HeartPulse className={className} />;
    if (specialization.includes("مسنين") || specialization.includes("ولادة")) return <Baby className={className} />;
    if (specialization.includes("طبيعي") || specialization.includes("تأهيل")) return <Bone className={className} />;
    if (specialization.includes("عينات") || specialization.includes("كانيولا")) return <Syringe className={className} />;
    if (specialization.includes("نفسية")) return <Brain className={className} />;
    if (specialization.includes("أسرة")) return <Stethoscope className={className} />;
    if (specialization.includes("تحاليل") || specialization.includes("فحوصات")) return <Microscope className={className} />;
    return <Activity className={className} />;
};

// Removed the generic StatusBadge because it is now integrated tightly into the AnimatedProfileCard pattern.

export const HireNurseButton = ({ onClick, className }: { onClick?: () => void, className?: string }) => {
  return (
    <motion.button
      whileHover={{ scale: 1.02, y: -2 }}
      whileTap={{ scale: 0.95 }}
      onClick={onClick}
      className={cn(
        "relative overflow-hidden group flex items-center justify-center gap-2 px-8 py-3.5",
        "rounded-full bg-gradient-to-r from-[#0066FF] to-[#004bb8]",
        "border border-white/20 shadow-[0_0_20px_rgba(0,102,255,0.3)]",
        "hover:shadow-[0_0_30px_rgba(0,102,255,0.6)] hover:border-white/40",
        "transition-all duration-300 ease-out",
        className
      )}
    >
      {/* The Animated Shimmer Overlay */}
      <motion.div 
        className="absolute inset-0 -translate-x-full w-[150%] bg-gradient-to-r from-transparent via-white/20 to-transparent skew-x-12"
        animate={{ translateX: ["-100%", "200%"] }}
        transition={{ repeat: Infinity, duration: 2.5, ease: "linear", repeatDelay: 1 }}
      />
      
      <UserPlus className="w-5 h-5 text-white relative z-10" strokeWidth={2} />
      <span className="text-white font-bold tracking-wide text-sm md:text-base relative z-10" style={{ fontFamily: "'Amiri', 'Outfit', sans-serif" }}>
        توظيف ممرض جديد
      </span>
    </motion.button>
  );
};

export const NurseList = () => {
    const redirect = useRedirect();
    
    return (
        <div className="w-full max-w-7xl mx-auto pb-12 pt-4 px-4 min-h-screen">
            <TopToolbar sx={{ mb: 6, display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center' }}>
                <div>
                    <Typography variant="h3" className="!font-black !text-transparent !bg-clip-text !bg-gradient-to-l !from-white !to-[#0066FF] drop-shadow-[0_0_15px_rgba(0,102,255,0.3)]" style={{ fontFamily: "'Amiri', 'Outfit', sans-serif" }}>
                        الكوادر الطبية
                    </Typography>
                    <Typography className="!text-slate-400 !text-sm mt-2 tracking-wide" style={{ fontFamily: "'Outfit', sans-serif" }}>
                        شبكة الرعاية الحية | 3D Kinetic Roster
                    </Typography>
                </div>
                <div>
                    <HireNurseButton onClick={() => redirect('create', 'nurses')} />
                </div>
            </TopToolbar>

            {/* The 3D Kinetic ID Cards Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
                {staffDossierData.map((staff) => (
                    <StaffIDCard key={staff.id} staff={staff} />
                ))}
            </div>
        </div>
    );
};

const StaffIDCard = ({ staff }: { staff: StaffDossier }) => {
    const redirect = useRedirect();
    
    const handleViewDossier = () => {
        // Route to the comprehensive dossier view within React Admin
        redirect('show', 'nurses', staff.id);
    };

    return (
        <div className="group relative overflow-hidden rounded-3xl bg-[#0a0a1a] p-6 w-full shadow-[12px_12px_24px_rgba(0,0,0,0.5),-12px_-12px_24px_rgba(255,255,255,0.03)] transition-all duration-500 hover:shadow-[20px_20px_40px_rgba(0,0,0,0.7),-20px_-20px_40px_rgba(255,255,255,0.05)] hover:scale-[1.03] hover:-translate-y-2 border border-white/5">
            
            {/* Animated Grid Background for the specific card */}
            <div className="absolute inset-0 opacity-10 group-hover:opacity-30 transition-opacity duration-500 pointer-events-none rounded-3xl overflow-hidden">
                <div
                className="absolute inset-0"
                style={{
                    backgroundImage: `
                    linear-gradient(rgba(0, 102, 255, 0.3) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(0, 102, 255, 0.3) 1px, transparent 1px)
                    `,
                    backgroundSize: "20px 20px",
                }}
                />
            </div>

            {/* Status indicator with pulse animation */}
            <div className="absolute left-6 top-6 z-10">
                <div className="relative">
                    <div
                        className={cn(
                            "h-3 w-3 rounded-full border-2 border-[#0a0a1a] transition-all duration-300 group-hover:scale-125",
                            staff.status === "متاح للتوجيه"
                                ? "bg-emerald-500 group-hover:shadow-[0_0_20px_rgba(16,185,129,0.8)]"
                                : staff.status === "في زيارة نشطة"
                                ? "bg-[#FFB300] group-hover:shadow-[0_0_20px_rgba(255,179,0,0.8)]"
                                : "bg-slate-500"
                        )}
                    ></div>
                    {(staff.status === "متاح للتوجيه" || staff.status === "في زيارة نشطة") && (
                        <div className={cn(
                            "absolute inset-0 h-3 w-3 rounded-full animate-ping opacity-40",
                            staff.status === "متاح للتوجيه" ? "bg-emerald-500" : "bg-[#FFB300]"
                        )}></div>
                    )}
                </div>
            </div>

            {/* Verified badge / Rating with bounce animation */}
            {staff.rating >= 4.5 && (
                <div className="absolute right-6 top-6 z-10">
                    <div className="flex items-center justify-center gap-1 rounded-full bg-gradient-to-br from-[#0066FF] to-[#00E5FF] px-2 py-0.5 shadow-[2px_2px_4px_rgba(0,0,0,0.3)] transition-all duration-300 group-hover:scale-110 group-hover:-rotate-6 group-hover:shadow-[0_0_15px_rgba(0,229,255,0.5)]">
                        <Star className="h-3 w-3 fill-white text-white" />
                        <span className="text-[11px] font-bold text-white pt-0.5">{staff.rating}</span>
                    </div>
                </div>
            )}

            {/* Profile Photo / Icon with enhanced hover effects */}
            <div className="mb-5 flex justify-center relative z-10 mt-2">
                <div className="relative group-hover:animate-pulse">
                    <div className="h-28 w-28 flex items-center justify-center overflow-hidden rounded-full bg-[#050505] shadow-[inset_6px_6px_12px_rgba(0,0,0,0.5),inset_-6px_-6px_12px_rgba(255,255,255,0.03)] transition-all duration-500 group-hover:shadow-[inset_8px_8px_16px_rgba(0,0,0,0.7),inset_-8px_-8px_16px_rgba(255,255,255,0.05)] group-hover:scale-110 border-2 border-transparent">
                        <img
                            src={staff.avatarUrl}
                            alt={staff.name}
                            className="h-full w-full rounded-full object-cover transition-transform duration-500 group-hover:scale-105"
                        />
                    </div>
                    {/* Glowing ring on hover */}
                    <div className="absolute inset-0 rounded-full border-2 border-[#00E5FF] opacity-0 group-hover:opacity-100 transition-all duration-500 animate-pulse pointer-events-none"></div>
                </div>
            </div>

            {/* Profile Info with slide-up animation */}
            <div className="text-center relative z-10 transition-transform duration-300 group-hover:-translate-y-1">
                <h3 className="text-xl font-bold text-gray-100 transition-colors duration-300 group-hover:text-[#00E5FF] drop-shadow-sm" style={{ fontFamily: "'Amiri', 'Outfit', sans-serif" }}>
                    {staff.name}
                </h3>
                <p className="mt-1 text-sm text-slate-400 transition-colors duration-300 group-hover:text-slate-200" style={{ fontFamily: "'Outfit', sans-serif" }}>
                    {staff.specialization}
                </p>

                <p className="mt-3 text-[11px] flex items-center justify-center gap-2 text-slate-500 transition-all duration-300 group-hover:text-[#0066FF] group-hover:font-bold tracking-widest uppercase">
                    <span>خبرة {staff.experience} سنوات</span>
                    <span className="text-white/20">|</span>
                    <span dir="ltr">EGP {staff.totalRevenueGenerated.toLocaleString()}</span>
                </p>
            </div>

            {/* Tags with bounce animation */}
            <div className="mt-5 flex justify-center gap-2 relative z-10">
                <span
                    className={cn(
                        "inline-block rounded-full px-3 py-1 text-xs font-bold shadow-[2px_2px_4px_rgba(0,0,0,0.2),-2px_-2px_4px_rgba(255,255,255,0.02)] transition-all duration-300",
                        "text-[#00E5FF] bg-[#11111a] border border-white/5",
                        "group-hover:bg-[#0066FF]/20 group-hover:scale-105 group-hover:shadow-[0_0_10px_rgba(0,102,255,0.3)] group-hover:border-[#0066FF]/30"
                    )}
                >
                    {staff.syndicateNumber ? "مرخص نقابياً" : "معتمد MoH"}
                </span>
                <span
                    className={cn(
                        "inline-block rounded-full px-3 py-1 text-xs font-bold shadow-[2px_2px_4px_rgba(0,0,0,0.2),-2px_-2px_4px_rgba(255,255,255,0.02)] transition-all duration-300",
                        "text-slate-300 bg-[#11111a] border border-white/5",
                        "group-hover:bg-white/5 group-hover:scale-105"
                    )}
                >
                    {staff.completedVisits} زيارة
                </span>
            </div>

            {/* Action Buttons with enhanced hover effects */}
            <div className="mt-6 flex gap-3 relative z-10">
                <button 
                    onClick={handleViewDossier}
                    className="flex-1 flex justify-center items-center gap-2 rounded-2xl bg-[#0a0a1a] py-3.5 text-sm font-bold text-[#00E5FF] shadow-[6px_6px_12px_rgba(0,0,0,0.4),-6px_-6px_12px_rgba(255,255,255,0.02)] transition-all duration-300 hover:shadow-[2px_2px_4px_rgba(0,0,0,0.2),-2px_-2px_4px_rgba(255,255,255,0.01)] hover:scale-95 active:scale-90 group-hover:bg-[#0066FF]/10 group-hover:text-white"
                >
                    <FileText className="h-4 w-4 transition-transform duration-300 hover:scale-110" />
                    <span>الملف الشامل</span>
                </button>
                <button 
                    className="flex-[0.5] flex justify-center items-center gap-2 rounded-2xl bg-[#0a0a1a] py-3.5 text-sm font-bold text-slate-400 shadow-[6px_6px_12px_rgba(0,0,0,0.4),-6px_-6px_12px_rgba(255,255,255,0.02)] transition-all duration-300 hover:shadow-[2px_2px_4px_rgba(0,0,0,0.2),-2px_-2px_4px_rgba(255,255,255,0.01)] hover:scale-95 active:scale-90 group-hover:bg-white/5 group-hover:text-white"
                >
                    <MessageCircle className="h-4 w-4 transition-transform duration-300 hover:scale-110" />
                </button>
            </div>

            {/* Animated border on hover */}
            <div className="absolute inset-0 rounded-3xl border border-[#0066FF]/40 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"></div>
        </div>
    );
};

