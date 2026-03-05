import * as React from 'react';
import { List, useListContext, TopToolbar, CreateButton } from 'react-admin';
import { GlowingEffect } from '../../components/ui/glowing-effect';
import { Typography, Chip, Switch } from '@mui/material';

const NurseGridLine = () => {
    const { data, isLoading } = useListContext();

    if (isLoading) return <div className="p-8 text-center text-slate-400">جاري التحميل...</div>;
    
    return (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 p-4 w-full">
            {data?.map((record: any) => (
                <div key={record.id} className="relative group rounded-2xl w-full h-[260px]">
                    <div className="absolute inset-0 z-0 transition-opacity duration-300 opacity-0 group-hover:opacity-100">
                        <GlowingEffect 
                            spread={40} 
                            glow={true} 
                            disabled={false} 
                            inactiveZone={0.01} 
                            borderWidth={2} 
                        />
                    </div>
                    <div className="relative z-10 w-full h-full rounded-2xl bg-slate-800/60 backdrop-blur-xl border border-white/10 p-6 flex flex-col justify-between shadow-xl transition-all duration-300">
                        <div>
                            <div className="flex justify-between items-start mb-4">
                                <div>
                                    <Typography variant="h6" className="!font-bold !text-slate-100">
                                        {record.user?.name || `ممرض #${record.id}`}
                                    </Typography>
                                    <Typography variant="body2" className="!text-slate-400">
                                        {record.user?.email || 'لا يوجد بريد الإلكتروني'}
                                    </Typography>
                                </div>
                                <div className="flex flex-col items-center">
                                    <Switch 
                                        checked={record.is_available} 
                                        color="primary" 
                                        sx={{ '& .MuiSwitch-thumb': { backgroundColor: record.is_available ? '#5a922c' : '#94a3b8' }, '& .MuiSwitch-track': { backgroundColor: '#334155' } }}
                                    />
                                    <span className={`text-xs mt-1 font-bold ${record.is_available ? 'text-[#5a922c]' : 'text-slate-400'}`}>
                                        {record.is_available ? 'متاح' : 'غير متاح'}
                                    </span>
                                </div>
                            </div>
                            <div className="flex flex-wrap gap-2 mt-4">
                                {record.specializations?.map((spec: string, idx: number) => (
                                    <Chip 
                                        key={idx} 
                                        label={spec} 
                                        size="small" 
                                        sx={{ backgroundColor: 'rgba(215, 159, 30, 0.2)', color: '#d79f1e', border: '1px solid rgba(215, 159, 30, 0.3)', fontWeight: 'bold' }} 
                                    />
                                ))}
                                {(!record.specializations || record.specializations.length === 0) && (
                                    <span className="text-slate-500 text-sm">لا توجد تخصصات مسجلة</span>
                                )}
                            </div>
                        </div>
                        <div className="mt-4 pt-4 border-t border-white/5 flex justify-between items-center text-slate-400 text-sm">
                            <span>ID: {record.id.toString().slice(0, 8)}...</span>
                            <a href={`#/nurses/${record.id}`} className="text-[#dd7bbb] hover:text-[#f8fafc] transition-colors font-medium px-4 py-1.5 rounded-lg bg-pink-500/10 hover:bg-pink-500/30">
                                تعديل الملف
                            </a>
                        </div>
                    </div>
                </div>
            ))}
            
            {(!data || data.length === 0) && (
                <div className="col-span-full p-8 text-center text-slate-400 bg-slate-800/30 rounded-2xl border border-white/5">
                    لا يوجد ممرضين مضافين للوكالة حتى الآن.
                </div>
            )}
        </div>
    );
};

const CustomToolbar = () => (
    <TopToolbar sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center', px: 2 }}>
        <Typography variant="h4" className="!font-bold !text-transparent !bg-clip-text !bg-gradient-to-r !from-pink-400 !to-amber-300">
            إدارة القوى العاملة
        </Typography>
        <div>
            <CreateButton 
                variant="contained" 
                label="إضافة ممرض جديد"
                sx={{ background: 'linear-gradient(90deg, #dd7bbb, #d79f1e)', color: '#fff', borderRadius: '8px', fontWeight: 'bold', px: 3, boxShadow: '0 4px 15px rgba(221, 123, 187, 0.3)' }} 
            />
        </div>
    </TopToolbar>
);

export const NurseList = () => (
    <List actions={<CustomToolbar />} sx={{ '& .MuiPaper-root': { backgroundColor: 'transparent', boxShadow: 'none' } }}>
        <NurseGridLine />
    </List>
);
