import * as React from 'react';
import { Sidebar as RaSidebar, useSidebarState, MenuItemLink } from 'react-admin';
import { Box, Typography, useMediaQuery, Theme } from '@mui/material';
import { useLocation } from 'react-router-dom';
import {
    DashboardKineticIcon,
    AvailableStaffIcon,
    CoverageAreasIcon,
    ActiveOrdersIcon,
    TodayRevenueIcon,
    AnimatedSettingsIcon,
} from '../../components/icons/KineticIcons';

// ─── Sidebar Menu Item with Kinetic Icon ──────────────────────────
const WateenMenuItem = ({ to, primaryText, icon, exact = false, ...props }: any) => {
    const location = useLocation();
    
    let isActive = false;
    if (exact) {
        isActive = location.pathname === to;
    } else {
        isActive = location.pathname.startsWith(to);
    }

    return (
        <div className="relative mx-3 mb-2 group">
            {/* Active Right Border Highlight (RTL) */}
            {isActive && (
                <div className="absolute right-0 top-1/2 -translate-y-1/2 w-0.5 h-8 bg-[#0066FF] shadow-[2px_0_15px_-3px_rgba(0,102,255,0.4)] rounded-l-md z-20" />
            )}
            
            <div className={`relative z-10 rounded-xl overflow-hidden transition-all duration-300 border border-transparent ${isActive ? 'bg-gradient-to-l from-[#0066FF]/10 to-transparent border-white/5' : 'hover:bg-white/5 hover:border-white/5 drop-shadow-sm'}`}>
                <MenuItemLink 
                    to={to} 
                    primaryText={primaryText} 
                    leftIcon={
                        <div className="transition-transform duration-300 group-hover:scale-110 flex items-center justify-center w-5 h-5">
                            {icon}
                        </div>
                    } 
                    // @ts-ignore
                    sx={{
                        py: 1.5,
                        px: 2,
                        pr: isActive ? 3 : 2,
                        color: isActive ? '#ffffff' : '#94a3b8',
                        fontWeight: isActive ? 600 : 500,
                        fontFamily: "'Amiri', 'Outfit', sans-serif",
                        transition: 'all 0.3s ease',
                        '&:hover': {
                            color: '#ffffff',
                            backgroundColor: 'transparent',
                        },
                        '& .MuiListItemIcon-root': {
                            minWidth: '40px'
                        }
                    }}
                    {...props} 
                />
            </div>
        </div>
    );
};

// ─── Main Sidebar ─────────────────────────────────────────────────
export const WateenSidebar = (props: any) => {
    const [open] = useSidebarState();
    const isSmall = useMediaQuery((theme: Theme) => theme.breakpoints.down('sm'));

    return (
        <RaSidebar 
            {...props} 
            sx={{ 
                ...(isSmall && !open && { display: 'none' }), // Hide completely on mobile when closed
                '& .MuiDrawer-paper': { 
                    pt: 2, 
                    width: isSmall ? (open ? 280 : 0) : (open ? 260 : 65),
                    backgroundColor: isSmall ? 'rgba(2, 4, 10, 0.95) !important' : 'rgba(5, 5, 15, 0.4) !important',
                    backdropFilter: 'blur(24px) saturate(1.4)',
                    WebkitBackdropFilter: 'blur(24px) saturate(1.4)',
                    borderLeft: '1px solid rgba(255,255,255,0.06)',
                    borderRight: 'none',
                    color: '#f8fafc',
                    scrollbarWidth: 'none',
                    transition: 'width 0.3s ease',
                    '&::-webkit-scrollbar': {
                        display: 'none'
                    }
                } 
            }}
        >
            <div className="sticky top-0 z-50 bg-transparent pb-6 pt-5">
                <style dangerouslySetInnerHTML={{__html: `
                    @keyframes float-svg {
                        0%, 100% { transform: translateY(0) scale(1); }
                        50% { transform: translateY(-3px) scale(1.02); }
                    }
                    @keyframes shimmer-sweep {
                        0% { transform: translateX(100%); }
                        100% { transform: translateX(-200%); }
                    }
                    @keyframes gradient-shift {
                        0% { background-position: 0% 50%; }
                        50% { background-position: 100% 50%; }
                        100% { background-position: 0% 50%; }
                    }
                `}} />
                <div className="flex items-center justify-center w-full">
                    <a 
                        href="/" 
                        className="flex items-center gap-1.5 group overflow-hidden transition-all duration-300" 
                        style={{ textDecoration: 'none' }}
                    >
                        {/* Dynamic SVG Icon */}
                        <div className="animate-[float-svg_4s_ease-in-out_infinite] flex-shrink-0 relative group">
                            <div className="absolute inset-0 bg-cyan-400 opacity-20 blur-xl group-hover:opacity-50 transition-opacity duration-500 rounded-full" />
                            <img 
                                src="/images/icon.svg" 
                                alt="Wateen" 
                                className="w-11 h-11 object-contain drop-shadow-[0_0_12px_rgba(0,200,255,0.5)] transition-transform duration-500 group-hover:scale-110 relative z-10" 
                            />
                        </div>
                        
                        {/* Typography & Scanning Line */}
                        <div 
                            className={`flex flex-col justify-center transition-all duration-500 overflow-hidden ${open ? 'w-[140px] opacity-100 pr-2' : 'w-0 opacity-0 pr-0'}`}
                        >
                            <div className="flex items-baseline gap-1.5 relative">
                                <span className="text-[28px] font-black tracking-wider leading-none relative z-10 bg-gradient-to-l from-white via-cyan-300 to-cyan-500 bg-clip-text text-transparent" style={{ 
                                    fontFamily: "'Amiri', 'Outfit', sans-serif"
                                }}>
                                    وَتِين
                                </span>
                                <span className="text-[20px] font-black bg-gradient-to-l from-white via-cyan-300 to-cyan-500 bg-clip-text text-transparent" style={{ fontFamily: "'Amiri', 'Outfit', sans-serif" }}>
                                    للأعمال
                                </span>
                            </div>
                            
                            {/* Animated underline scanning gradient */}
                            <div className="relative w-full h-[2px] mt-[4px] bg-slate-800/50 rounded-full overflow-hidden">
                                <div className="absolute top-0 right-0 h-full w-[80px] bg-gradient-to-r from-transparent via-cyan-400 to-transparent animate-[shimmer-sweep_3s_infinite]" />
                            </div>
                        </div>
                    </a>
                </div>
            </div>
            
            <div className="flex flex-col gap-1 w-full mt-2">
                <WateenMenuItem to="/" primaryText="مركز القيادة" icon={<DashboardKineticIcon className="w-5 h-5" />} exact />
                <WateenMenuItem to="/nurses" primaryText="الكوادر الطبية" icon={<AvailableStaffIcon className="w-5 h-5" />} />
                <WateenMenuItem to="/coverage" primaryText="النطاق الجغرافي" icon={<CoverageAreasIcon className="w-5 h-5" />} />
                <WateenMenuItem to="/operations" primaryText="مركز العمليات" icon={<ActiveOrdersIcon className="w-5 h-5" />} />
                <WateenMenuItem to="/financials" primaryText="السجل المالي" icon={<TodayRevenueIcon className="w-5 h-5" />} />
                
                <div className="mt-8 border-t border-white/10 pt-4 mx-4">
                    <WateenMenuItem to="/settings" primaryText="تكوين النظام" icon={<AnimatedSettingsIcon className="w-5 h-5" />} />
                </div>
            </div>
        </RaSidebar>
    );
};
