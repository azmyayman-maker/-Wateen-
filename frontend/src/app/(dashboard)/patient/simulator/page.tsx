'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useLanguage } from '@/lib/i18n';
import Link from 'next/link';
const THEME = {
  emerald: '16, 185, 129',
  teal: '20, 184, 166',
  cyan: '6, 182, 212',
  blue: '59, 130, 246',
  neonBlue: '0, 240, 255',
  green: '34, 197, 94',
  red: '239, 68, 68',
  orange: '249, 115, 22',
};
import { 
  Signal, 
  MapPin, 
  UserCircle2, 
  Star, 
  PhoneCall, 
  MessageSquare, 
  Clock, 
  Activity, 
  ShieldCheck, 
  CheckCircle2, 
  ArrowRight,
  ArrowLeft
} from 'lucide-react';
import LocationPicker from '@/components/shared/map/LocationPicker';

type SimulatorState = 'searching' | 'matched' | 'en_route' | 'arrived' | 'in_progress' | 'completed';

export default function VisitLifecycleSimulator() {
  const { isRTL } = useLanguage();
  const [currentState, setCurrentState] = useState<SimulatorState>('searching');
  const [progress, setProgress] = useState(0);

  // Auto-advance the simulator
  useEffect(() => {
    let timeout: NodeJS.Timeout;
    
    switch (currentState) {
      case 'searching':
        timeout = setTimeout(() => setCurrentState('matched'), 4000);
        break;
      case 'matched':
        timeout = setTimeout(() => setCurrentState('en_route'), 3000);
        break;
      case 'en_route':
        timeout = setTimeout(() => setCurrentState('arrived'), 5000);
        break;
      case 'arrived':
        timeout = setTimeout(() => setCurrentState('in_progress'), 3000);
        break;
      case 'in_progress':
        // Progress bar simulation
        const interval = setInterval(() => {
          setProgress(p => {
            if (p >= 100) {
              clearInterval(interval);
              setCurrentState('completed');
              return 100;
            }
            return p + 2;
          });
        }, 100);
        return () => clearInterval(interval);
      default:
        break;
    }

    return () => clearTimeout(timeout);
  }, [currentState]);

  return (
    <div className="min-h-[100dvh] w-full bg-[#030712] text-slate-50 overflow-x-hidden pt-20 pb-24 flex flex-col relative">
      
      {/* Background Ambience */}
      <div 
        className="fixed inset-0 pointer-events-none opacity-20 transition-all duration-1000"
        style={{
          background: currentState === 'searching' 
              ? `radial-gradient(circle at center, rgba(${THEME.neonBlue}, 0.5) 0%, transparent 70%)`
            : currentState === 'in_progress'
              ? `radial-gradient(circle at center, rgba(${THEME.green}, 0.5) 0%, transparent 70%)`
            : currentState === 'completed'
              ? `radial-gradient(circle at center, rgba(${THEME.teal}, 0.5) 0%, transparent 70%)`
            : `radial-gradient(circle at center, rgba(${THEME.orange}, 0.5) 0%, transparent 70%)`
        }}
      />

      <div className="w-full flex-1 max-w-2xl mx-auto px-4 sm:px-8 relative z-10 flex flex-col justify-center min-h-[600px]">
        
        {/* Header Back Link */}
        {(currentState === 'completed' || currentState === 'searching') && (
           <Link href="/patient" className="absolute top-4 left-4 z-50 flex items-center gap-2 text-slate-400 hover:text-white transition-colors bg-slate-900/50 px-4 py-2 rounded-full border border-white/5 backdrop-blur-md">
             {isRTL ? <ArrowRight className="w-4 h-4" /> : <ArrowLeft className="w-4 h-4" />}
             {isRTL ? 'إلغاء / عودة' : 'Cancel / Back'}
           </Link>
        )}

        <AnimatePresence mode="wait">

          {/* 1. Searching (Radar) */}
          {currentState === 'searching' && (
            <motion.div
              key="searching"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 1.1 }}
              className="flex flex-col items-center justify-center text-center gap-8"
            >
              <div className="relative w-48 h-48 sm:w-64 sm:h-64 flex items-center justify-center">
                {/* Radar Rings */}
                {[0, 1, 2].map(i => (
                  <motion.div
                    key={i}
                    className="absolute inset-0 rounded-full border-2 border-[#3b82f6]/40"
                    animate={{ scale: [1, 2.5], opacity: [0.8, 0] }}
                    transition={{ duration: 3, repeat: Infinity, delay: i * 1, ease: "linear" }}
                  />
                ))}
                
                {/* Sweeping Radar Arm */}
                <motion.div 
                  className="absolute inset-0 rounded-full border border-[#3b82f6]/20 bg-[conic-gradient(from_0deg_at_50%_50%,transparent_0deg,rgba(59,130,246,0.3)_360deg)] overflow-hidden"
                  animate={{ rotate: 360 }}
                  transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                />

                <div className="absolute z-10 w-16 h-16 rounded-full bg-slate-900 border border-[#3b82f6]/50 shadow-[0_0_30px_rgba(59,130,246,0.5)] flex items-center justify-center">
                  <Signal className="w-8 h-8 text-[#3b82f6] animate-pulse" />
                </div>
              </div>
              
              <div>
                <h2 className="text-3xl font-bold text-white mb-2">{isRTL ? 'جاري البحث عن ممرض...' : 'Searching for a Nurse...'}</h2>
                <p className="text-slate-400 max-w-sm mx-auto">
                  {isRTL ? 'نبحث في نطاق 5 كم عن أقرب ممرض متاح ومؤهل لخدمتك.' : 'Scanning within a 5km radius for the nearest qualified and available nurse.'}
                </p>
              </div>
            </motion.div>
          )}

          {/* 2. Matched */}
          {currentState === 'matched' && (
            <motion.div
              key="matched"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 1.1 }}
              className="flex flex-col items-center justify-center text-center gap-8"
            >
              <motion.div 
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", stiffness: 200, damping: 20 }}
                className="w-24 h-24 rounded-full bg-emerald-500/20 border border-emerald-500 flex items-center justify-center shadow-[0_0_50px_rgba(16,185,129,0.3)]"
              >
                <CheckCircle2 className="w-12 h-12 text-emerald-400" />
              </motion.div>
              
              <div>
                <h2 className="text-3xl font-bold text-white mb-2">{isRTL ? 'تم العثور على ممرض!' : 'Nurse Match Found!'}</h2>
                <p className="text-emerald-400 font-medium">
                  {isRTL ? 'يقوم الممرض السعيد بقبول طلبك الآن.' : 'ElSaeed is accepting your request now.'}
                </p>
              </div>
            </motion.div>
          )}

          {/* 3. En Route (Live Map / ETA) */}
          {currentState === 'en_route' && (
            <motion.div
              key="en_route"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -30 }}
              className="flex flex-col w-full gap-6 bg-slate-900/60 p-6 sm:p-8 rounded-3xl border border-white/10 backdrop-blur-2xl shadow-2xl"
            >
              <div className="flex items-center justify-between">
                <div>
                   <h2 className="text-2xl font-bold text-white mb-1">{isRTL ? 'الممرض في الطريق' : 'Nurse is En Route'}</h2>
                   <p className="text-slate-400 flex items-center gap-2">
                     <Clock className="w-4 h-4 text-orange-400" />
                     {isRTL ? 'الوقت المتوقع للوصول: 12 دقيقة' : 'ETA: 12 Minutes'}
                   </p>
                </div>
                <div className="w-12 h-12 rounded-full border border-white/20 overflow-hidden bg-slate-800 flex items-center justify-center shrink-0">
                  <UserCircle2 className="w-10 h-10 text-slate-400 mt-2" />
                </div>
              </div>

              {/* Mock Map View */}
              <div className="w-full h-48 sm:h-64 rounded-2xl overflow-hidden border border-white/10 relative">
                 <LocationPicker readOnly initialLocation={[30.0444, 31.2357]} className="w-full h-full" />
                 
                 {/* Moving Element Overlay */}
                 <motion.div 
                   className="absolute z-[400] w-10 h-10 -ml-5 -mt-5"
                   animate={{ 
                     top: ['20%', '50%', '80%'],
                     left: ['20%', '40%', '60%']
                   }}
                   transition={{ duration: 10, ease: 'linear' }}
                 >
                   <div className="relative flex items-center justify-center">
                     <div className="absolute w-8 h-8 rounded-full bg-blue-500/30 animate-ping" />
                     <div className="w-8 h-8 rounded-full bg-blue-500 border-2 border-white flex items-center justify-center shadow-lg relative z-10">
                       <UserCircle2 className="w-5 h-5 text-white" />
                     </div>
                   </div>
                 </motion.div>
              </div>

              <div className="p-4 rounded-xl bg-slate-950 border border-white/5 flex items-center justify-between gap-4">
                 <div>
                   <p className="font-bold text-white">ElSaeed Ahmed</p>
                   <p className="text-sm text-slate-400 flex items-center gap-1">
                     <Star className="w-3 h-3 text-yellow-500 fill-yellow-500" /> 4.9 (120 reviews)
                   </p>
                 </div>
                 <div className="flex gap-2 shrink-0">
                   <button className="w-10 h-10 rounded-full bg-slate-800 border border-white/10 flex items-center justify-center text-white hover:bg-slate-700 transition-colors">
                     <MessageSquare className="w-4 h-4" />
                   </button>
                   <button className="w-10 h-10 rounded-full bg-green-500/20 border border-green-500/50 flex items-center justify-center text-green-400 hover:bg-green-500/30 transition-colors">
                     <PhoneCall className="w-4 h-4" />
                   </button>
                 </div>
              </div>
            </motion.div>
          )}

          {/* 4. Arrived */}
          {currentState === 'arrived' && (
            <motion.div
              key="arrived"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 1.1 }}
              className="flex flex-col items-center justify-center text-center gap-6"
            >
              <motion.div 
                 animate={{ y: [0, -10, 0] }}
                 transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
                 className="w-24 h-24 rounded-full bg-blue-500/20 border border-blue-500 flex items-center justify-center shadow-[0_0_50px_rgba(59,130,246,0.3)] mb-4"
              >
                <MapPin className="w-10 h-10 text-blue-400" />
              </motion.div>
              
              <div>
                <h2 className="text-3xl font-bold text-white mb-2">{isRTL ? 'لقد وصل الممرض!' : 'The Nurse has Arrived!'}</h2>
                <p className="text-slate-400">
                  {isRTL ? 'الرجاء تحضير رمز التحقق (OTP) أو الهوية الوطنية' : 'Please have your OTP or National ID ready for verification.'}
                </p>
              </div>
            </motion.div>
          )}

          {/* 5. In Progress (Live Vitals Streaming) */}
          {currentState === 'in_progress' && (
            <motion.div
              key="in_progress"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -30 }}
              className="flex flex-col w-full gap-6 bg-slate-900/60 p-6 sm:p-8 rounded-3xl border border-white/10 backdrop-blur-2xl shadow-2xl relative overflow-hidden"
            >
              <div className="absolute top-0 left-0 w-full h-1 bg-slate-800">
                <motion.div className="h-full bg-emerald-500" style={{ width: `${progress}%` }} />
              </div>

              <div className="flex items-center justify-between">
                <div>
                   <h2 className="text-2xl font-bold text-white mb-1 flex items-center gap-3">
                     <div className="w-3 h-3 rounded-full bg-emerald-500 animate-pulse" />
                     {isRTL ? 'الخدمة قيد التنفيذ' : 'Service in Progress'}
                   </h2>
                   <p className="text-slate-400">
                     {isRTL ? 'يتم حفظ السجلات الحيوية في الـ Health Wallet الخاصة بك بشكل آمن.' : 'Vitals are being securely stored in your Health Wallet.'}
                   </p>
                </div>
              </div>

              {/* Streaming Vitals Grid */}
              <div className="grid grid-cols-2 gap-4">
                 <div className="bg-slate-950/50 border border-emerald-500/20 rounded-2xl p-5 flex flex-col gap-2 relative overflow-hidden">
                    <div className="absolute -right-4 -top-4 w-24 h-24 bg-emerald-500/10 blur-xl rounded-full" />
                    <Activity className="w-6 h-6 text-emerald-400 mb-2" />
                    <p className="text-slate-400 text-sm">{isRTL ? 'معدل نبضات القلب' : 'Heart Rate'}</p>
                    <div className="flex items-end gap-2">
                       <motion.span 
                         key={progress} 
                         className="text-3xl font-black text-white"
                         initial={{ scale: 1.1, color: '#10b981' }}
                         animate={{ scale: 1, color: '#ffffff' }}
                       >
                         {Math.floor(75 + Math.random() * 5)}
                       </motion.span>
                       <span className="text-emerald-500 font-medium mb-1 tracking-wider uppercase">BPM</span>
                    </div>
                 </div>
                 
                 <div className="bg-slate-950/50 border border-blue-500/20 rounded-2xl p-5 flex flex-col gap-2 relative overflow-hidden">
                    <div className="absolute -right-4 -top-4 w-24 h-24 bg-blue-500/10 blur-xl rounded-full" />
                    <ShieldCheck className="w-6 h-6 text-blue-400 mb-2" />
                    <p className="text-slate-400 text-sm">{isRTL ? 'المصادقة والتشفير' : 'Auth & Encryption'}</p>
                    <div className="flex items-end gap-2 mt-auto">
                       <span className="text-lg font-bold text-white tracking-widest font-mono">SECURE</span>
                    </div>
                 </div>
              </div>

              {/* Simulated ECG Wave */}
              <div className="h-24 w-full bg-slate-950 border border-white/5 rounded-2xl flex items-center justify-center p-4 relative overflow-hidden">
                <svg className="w-[150%] h-full opacity-60 stroke-[#10b981] fill-none stroke-[2]" viewBox="0 0 500 100" preserveAspectRatio="none">
                  <motion.path
                    d="M 0,50 L 50,50 L 60,20 L 70,80 L 80,50 L 130,50 L 140,20 L 150,80 L 160,50 L 210,50 L 220,20 L 230,80 L 240,50 L 290,50 L 300,20 L 310,80 L 320,50 L 370,50 L 380,20 L 390,80 L 400,50 L 450,50 L 460,20 L 470,80 L 480,50 L 500,50"
                    initial={{ pathLength: 0, pathOffset: 1 }}
                    animate={{ pathLength: 1, pathOffset: 0 }}
                    transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                  />
                </svg>
                {/* Overlay gradient to fade out edges */}
                <div className="absolute inset-0 bg-gradient-to-r from-slate-950 via-transparent to-slate-950 pointer-events-none" />
              </div>
            </motion.div>
          )}

          {/* 6. Completed */}
          {currentState === 'completed' && (
            <motion.div
              key="completed"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="flex flex-col w-full gap-6 bg-slate-900/60 p-6 sm:p-8 rounded-3xl border border-white/10 backdrop-blur-2xl shadow-2xl items-center text-center"
            >
              <div className="w-20 h-20 rounded-full bg-emerald-500/20 flex items-center justify-center border border-emerald-500/50 mb-2">
                 <CheckCircle2 className="w-10 h-10 text-emerald-400" />
              </div>
              
              <div>
                <h2 className="text-3xl font-bold text-white mb-2">{isRTL ? 'اكتملت الخدمة' : 'Service Completed'}</h2>
                <p className="text-slate-400">
                  {isRTL ? 'شكراً لثقتك بمنصة وتين.' : 'Thank you for trusting Wateen Platform.'}
                </p>
              </div>

              <div className="w-full bg-slate-950 p-6 rounded-2xl border border-white/5 mt-4">
                 <h3 className="text-white font-bold mb-4">{isRTL ? 'كيف كانت تجربتك؟' : 'How was your experience?'}</h3>
                 <div className="flex justify-center gap-2 mb-6">
                    {[1,2,3,4,5].map(star => (
                      <button key={star} className="p-2 transition-transform hover:scale-125 hover:text-yellow-500 text-slate-600">
                        <Star className="w-8 h-8 fill-current" />
                      </button>
                    ))}
                 </div>
                 
                 <Link href="/patient">
                   <button className="w-full py-4 rounded-xl font-bold text-white flex items-center justify-center gap-2 transition-all shadow-lg shadow-blue-500/20 bg-blue-500 hover:bg-blue-600 active:scale-95 text-lg">
                     {isRTL ? 'العودة للرئيسية' : 'Return to Home'}
                   </button>
                 </Link>
              </div>
            </motion.div>
          )}

        </AnimatePresence>
      </div>
    </div>
  );
}
