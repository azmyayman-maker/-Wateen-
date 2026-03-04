import * as React from 'react';
import { Typography } from '@mui/material';
import { Form, BooleanInput, SaveButton, Toolbar, TextInput, useNotify } from 'react-admin';
import { GlowingEffect } from '../../components/ui/glowing-effect';

const GlowingCard = ({ title, children }: any) => {
    return (
        <div className="relative mb-6 group rounded-2xl w-full">
            <div className="absolute inset-0 z-0 transition-opacity duration-300 opacity-0 group-hover:opacity-100 focus-within:opacity-100">
                <GlowingEffect 
                    spread={40} 
                    glow={true} 
                    disabled={false} 
                    inactiveZone={0.01} 
                    borderWidth={2} 
                />
            </div>
            <div className="relative z-10 w-full h-full rounded-2xl bg-slate-800/60 backdrop-blur-xl border border-white/10 p-6 shadow-xl transition-all duration-300">
                <Typography variant="h6" className="!font-bold !text-slate-100 !mb-4 !border-b !border-slate-700/50 !pb-2">
                    {title}
                </Typography>
                <div className="mt-4 flex flex-col gap-4">
                    {children}
                </div>
            </div>
        </div>
    );
};

export const AgencySettings = () => {
    const notify = useNotify();

    const onSubmit = (data: any) => {
        console.log("Settings Saved:", data);
        notify('تم حفظ الإعدادات بنجاح', { type: 'success' });
    };

    return (
        <div className="p-8 max-w-5xl mx-auto w-full">
            <div className="mb-8">
                <Typography variant="h4" className="!font-bold !text-transparent !bg-clip-text !bg-gradient-to-r !from-pink-400 !to-amber-300">
                    إعدادات المكتب
                </Typography>
                <Typography variant="body1" className="!text-slate-400 !mt-2">
                    تحكم بجميع تفضيلات عملك وإعدادات التوجيه التلقائي لطاقم التمريض
                </Typography>
            </div>
            
            <Form onSubmit={onSubmit} defaultValues={{ dispatch_mode: true, name: 'وكالة وتين الطبية', hours: '08:00 - 17:00' }}>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full">
                    
                    {/* Agency Details */}
                    <div className="md:col-span-2">
                        <GlowingCard title="تفاصيل المكتب">
                            <TextInput 
                                source="name" 
                                label="اسم المكتب" 
                                fullWidth 
                                variant="outlined" 
                                sx={{ '& .MuiOutlinedInput-root': { '& fieldset': { borderColor: 'rgba(255,255,255,0.2)' }, '&:hover fieldset': { borderColor: 'rgba(255,255,255,0.4)' }, '&.Mui-focused fieldset': { borderColor: '#dd7bbb' } }, '& .MuiInputLabel-root': { color: '#94a3b8' }, '& .MuiInputBase-input': { color: '#f8fafc' } }} 
                            />
                            <TextInput 
                                source="email" 
                                label="البريد الإلكتروني للتواصل" 
                                type="email"
                                fullWidth 
                                variant="outlined"
                                sx={{ '& .MuiOutlinedInput-root': { '& fieldset': { borderColor: 'rgba(255,255,255,0.2)' }, '&:hover fieldset': { borderColor: 'rgba(255,255,255,0.4)' }, '&.Mui-focused fieldset': { borderColor: '#dd7bbb' } }, '& .MuiInputLabel-root': { color: '#94a3b8' }, '& .MuiInputBase-input': { color: '#f8fafc' } }} 
                            />
                        </GlowingCard>
                    </div>

                    {/* Dispatch Mode */}
                    <GlowingCard title="وضع التوجيه (Dispatch Mode)">
                        <Typography variant="body2" className="!text-slate-400 !mb-2">
                            اختر ما إذا كنت تريد توزيع الطلبات على الممرضين بشكل آلي أو يدوي.
                        </Typography>
                        <BooleanInput 
                            source="dispatch_mode" 
                            label="تفعيل التوجيه التلقائي (AUTO)" 
                            sx={{ '& .MuiFormControlLabel-label': { color: '#f8fafc', fontWeight: 600 } }}
                        />
                    </GlowingCard>

                    {/* B2B Hours */}
                    <GlowingCard title="ساعات العمل">
                        <Typography variant="body2" className="!text-slate-400 !mb-2">
                            حدد أوقات العمل الرسمية للمكتب.
                        </Typography>
                        <TextInput 
                            source="hours" 
                            label="فترة العمل" 
                            fullWidth 
                            variant="outlined"
                            sx={{ '& .MuiOutlinedInput-root': { '& fieldset': { borderColor: 'rgba(255,255,255,0.2)' }, '&:hover fieldset': { borderColor: 'rgba(255,255,255,0.4)' }, '&.Mui-focused fieldset': { borderColor: '#dd7bbb' } }, '& .MuiInputLabel-root': { color: '#94a3b8' }, '& .MuiInputBase-input': { color: '#f8fafc' } }} 
                        />
                    </GlowingCard>

                </div>
                
                <Toolbar sx={{ backgroundColor: 'transparent', display: 'flex', justifyContent: 'flex-end', mt: 4 }}>
                    <SaveButton 
                        label="حفظ التغييرات" 
                        alwaysEnable 
                        sx={{ 
                            background: 'linear-gradient(90deg, #dd7bbb, #d79f1e)', 
                            color: '#fff', 
                            px: 4, 
                            py: 1.5, 
                            borderRadius: '12px',
                            fontWeight: 'bold',
                            boxShadow: '0 4px 15px rgba(221, 123, 187, 0.4)',
                            transition: 'all 0.3s ease',
                            '&:hover': {
                                transform: 'translateY(-2px)',
                                boxShadow: '0 6px 20px rgba(215, 159, 30, 0.5)'
                            }
                        }} 
                    />
                </Toolbar>
            </Form>
        </div>
    );
};
