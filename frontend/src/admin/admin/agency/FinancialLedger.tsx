import * as React from 'react';
import { Typography } from '@mui/material';
import { Wallet, TrendingUp, TrendingDown, DollarSign } from 'lucide-react';
import { GlowingEffect } from '../../components/ui/glowing-effect';

const MetricCard = ({ title, amount, percentage, isPositive }: any) => {
    return (
        <div className="relative group rounded-2xl w-full">
            <div className="absolute inset-0 z-0 transition-opacity duration-300 opacity-0 group-hover:opacity-100">
                <GlowingEffect spread={40} glow={true} disabled={false} inactiveZone={0.01} borderWidth={2} />
            </div>
            <div className="relative z-10 w-full h-full rounded-2xl bg-[#0a0f1c]/80 backdrop-blur-xl border border-white/10 p-6 shadow-xl transition-all duration-300">
                <Typography variant="body1" className="!text-slate-400 !mb-3 font-semibold font-['Amiri',_'Outfit',_sans-serif]">
                    {title}
                </Typography>
                <div className="flex items-end justify-between">
                    <Typography variant="h4" className="!font-bold !text-white flex items-center gap-1">
                        <span className="text-lg text-slate-500 mb-1 ml-1">EGP</span>
                        {amount}
                    </Typography>
                    <div className={`flex items-center gap-1 text-sm font-bold ${isPositive ? 'text-emerald-400 bg-emerald-400/10' : 'text-rose-400 bg-rose-400/10'} px-2 py-1 rounded-lg border ${isPositive ? 'border-emerald-400/20' : 'border-rose-400/20'}`}>
                        {isPositive ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
                        <span dir="ltr">{percentage}%</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export const FinancialLedger = () => {
    return (
        <div className="p-8 max-w-7xl mx-auto w-full">
            <div className="mb-8 flex flex-col md:flex-row md:items-end justify-between gap-4">
                <div>
                    <Typography variant="h4" className="!font-bold !text-transparent !bg-clip-text !bg-gradient-to-l !from-[#0066FF] !to-[#FFB300] flex items-center gap-3">
                        <Wallet size={32} className="text-[#0066FF]" />
                        السجل المالي
                    </Typography>
                    <Typography variant="body1" className="!text-slate-400 !mt-2 !font-['Amiri',_'Outfit',_sans-serif]">
                        البيانات المالية للمكتب، والفواتير، والمدفوعات الخاصة بطواقم التمريض والمرضى.
                    </Typography>
                </div>
                
                <div className="flex gap-2">
                    <button className="px-5 py-2 rounded-lg bg-white/5 border border-white/10 text-white font-semibold hover:bg-white/10 transition flex items-center gap-2">
                        <DollarSign size={18} className="text-slate-400" />
                        سحب رصيد (Withdraw)
                    </button>
                    <button className="px-5 py-2 rounded-lg bg-[#0066FF] border border-[#0066FF] text-white font-bold hover:shadow-[0_0_15px_rgba(0,102,255,0.5)] transition hover:-translate-y-0.5">
                        إنشاء تقرير مالية جديد
                    </button>
                </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full mb-8">
                <MetricCard title="الإيرادات الكلية (الشهر الحيالي)" amount="345,000" percentage="12.5" isPositive={true} />
                <MetricCard title="مستحقات الممرضين المُعلقة" amount="89,250" percentage="4.2" isPositive={false} />
                <MetricCard title="صافي أرباح المكتب" amount="255,750" percentage="15.8" isPositive={true} />
            </div>
            
            <div className="relative group rounded-2xl w-full">
                <div className="absolute inset-0 z-0 transition-opacity duration-300 opacity-0 group-hover:opacity-100 focus-within:opacity-100">
                    <GlowingEffect spread={40} glow={true} disabled={false} inactiveZone={0.01} borderWidth={2} />
                </div>
                <div className="relative z-10 w-full rounded-2xl bg-[#0a0f1c]/80 backdrop-blur-xl border border-white/10 p-2 overflow-hidden">
                    <div className="p-4 border-b border-white/5 flex justify-between items-center">
                        <Typography variant="h6" className="!font-bold !text-slate-100">
                            أحدث المعاملات (Ledger Entries)
                        </Typography>
                    </div>
                    
                    <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse" dir="rtl">
                            <thead>
                                <tr className="border-b border-white/5 text-slate-400 font-semibold font-['Amiri',_'Outfit',_sans-serif]">
                                    <th className="p-4 rounded-tr-lg">رقم المعاملة</th>
                                    <th className="p-4">التاريخ</th>
                                    <th className="p-4">البيان / الوصف</th>
                                    <th className="p-4">النوع</th>
                                    <th className="p-4 text-left">المبلغ (EGP)</th>
                                </tr>
                            </thead>
                            <tbody>
                                {[
                                    { id: 'TRX-9942', date: '2026-03-02', desc: 'تحصيل خدمة من أحمد علي (رعاية منزلية)', type: 'إيداع', amount: '+ 1,200', isCredit: true },
                                    { id: 'TRX-9941', date: '2026-03-02', desc: 'تسوية مستحقات للممرض: محمود حسن', type: 'سحب', amount: '- 850', isCredit: false },
                                    { id: 'TRX-9940', date: '2026-03-01', desc: 'تحصيل خدمة من سارة محمد (تركيب محاليل)', type: 'إيداع', amount: '+ 450', isCredit: true },
                                    { id: 'TRX-9939', date: '2026-03-01', desc: 'رسوم تشغيل المنصة (Wateen Platform)', type: 'خصم', amount: '- 150', isCredit: false },
                                    { id: 'TRX-9938', date: '2026-02-28', desc: 'تحصيل خدمة من يوسف أمين (حقن عضوية)', type: 'إيداع', amount: '+ 200', isCredit: true },
                                ].map((trx, index) => (
                                    <tr key={index} className="border-b border-white/5 hover:bg-white/5 transition-colors group/row cursor-pointer">
                                        <td className="p-4 font-mono text-sm text-slate-300 group-hover/row:text-white transition-colors">{trx.id}</td>
                                        <td className="p-4 text-slate-400 text-sm">{trx.date}</td>
                                        <td className="p-4 text-slate-200 font-semibold">{trx.desc}</td>
                                        <td className="p-4">
                                            <span className={`px-3 py-1 rounded-full text-xs font-bold border ${trx.isCredit ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-slate-500/10 text-slate-300 border-slate-500/20'}`}>
                                                {trx.type}
                                            </span>
                                        </td>
                                        <td className={`p-4 font-mono text-left font-bold ${trx.isCredit ? 'text-emerald-400' : 'text-slate-300'}`}>
                                            {trx.amount}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
};
