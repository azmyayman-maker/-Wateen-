import React from "react";
import { Layout, LayoutProps, useSidebarState } from "react-admin";
import { WateenSidebar } from "./Sidebar";
import { MyMenu } from "./MyMenu";
import { BeamsBackground } from "../../components/ui/BeamsBackground";
import { AppBar, Toolbar, IconButton } from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';

const CustomAppBar = (props: any) => {
    const [open, setOpen] = useSidebarState();
    return (
        <AppBar 
            {...props} 
            elevation={0}
            sx={{ 
                display: { xs: 'flex', md: 'none' }, 
                backgroundColor: 'rgba(2, 4, 10, 0.85) !important', 
                backdropFilter: 'blur(16px)',
                WebkitBackdropFilter: 'blur(16px)',
                borderBottom: '1px solid rgba(255,255,255,0.08)',
                color: 'white',
                zIndex: 50,
            }}
        >
            <Toolbar sx={{ minHeight: '60px !important', px: 2 }}>
                <IconButton color="inherit" onClick={() => setOpen(!open)} edge="start">
                    <MenuIcon />
                </IconButton>
                <div className="flex-grow flex justify-center items-center gap-2">
                    <img src="/images/icon.svg" alt="Wateen" className="w-7 h-7 object-contain drop-shadow-[0_0_8px_rgba(0,136,255,0.5)] animate-pulse" />
                    <span className="text-xl font-black" style={{ color: '#0088FF', fontFamily: "'Amiri', 'Outfit', sans-serif" }}>وَتِين</span>
                </div>
                <div style={{ width: 40 }} /> {/* Spacer */}
            </Toolbar>
        </AppBar>
    );
};

export const WateenLayout = (props: LayoutProps) => {
    return (
        <BeamsBackground intensity="strong" className="fixed inset-0 z-0">
            {/* 
              The BeamsBackground now covers the ENTIRE viewport as the base layer.
              Everything — sidebar, content, pages — renders ON TOP of it.
            */}
            <div className="relative z-10 w-full min-h-screen" dir="rtl">
                <Layout 
                    {...props} 
                    appBar={CustomAppBar}
                    sidebar={WateenSidebar} 
                    menu={MyMenu} 
                    sx={{
                        // Make ALL MUI backgrounds transparent so beams show through
                        backgroundColor: 'transparent !important',
                        '& .RaLayout-root': {
                            backgroundColor: 'transparent !important',
                        },
                        '& .RaLayout-appFrame': {
                            backgroundColor: 'transparent !important',
                            marginTop: { xs: 0, md: 0 }
                        },
                        '& .RaLayout-contentWithSidebar': {
                            backgroundColor: 'transparent !important',
                        },
                        '& .RaLayout-content': { 
                            backgroundColor: 'transparent !important',
                            paddingTop: { xs: '12px', md: '24px' },
                            paddingX: { xs: 2, md: 4, lg: 6 },
                            overflowY: 'auto',
                            scrollbarWidth: 'none',
                            '&::-webkit-scrollbar': { display: 'none' },
                        },
                        '& .MuiDrawer-root': { zIndex: 100 },
                        '& .MuiDrawer-paper': {
                            backgroundColor: 'transparent !important',
                        },
                        '& .MuiPaper-root': {
                            backgroundColor: 'transparent !important',
                        },
                    }}
                />
            </div>
        </BeamsBackground>
    );
};
