'use client';

import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useLanguage } from '@/lib/i18n';
import { cn } from '@/lib/utils';
import {
  Map, 
  Navigation, 
  Activity, 
  Wallet, 
  Star, 
  Clock, 
  Power,
  ShieldAlert,
  Target,
  User,
  MapPin,
  Loader2,
  Check,
  X,
  Syringe,
  Stethoscope,
  HeartHandshake
} from 'lucide-react';
import { NurseBackground } from '@/components/ui/nurse-background';
import FlipTextReveal from '@/components/ui/next-reveal';

const staggerContainer = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.1 } },
};

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 300, damping: 24 } },
};

const HERO_H = 430;

function StatusToggleSwitch({ 
  isOnline, 
  onToggle, 
  labelOn, 
  labelOff 
}: { 
  isOnline: boolean; 
  onToggle: () => void; 
  labelOn: string; 
  labelOff: string; 
}) {
  return (
    <div 
      onClick={onToggle}
      className={cn(
        "mt-6 relative flex items-center w-[220px] h-[56px] rounded-full p-1.5 cursor-pointer select-none overflow-hidden transition-colors duration-500 border",
        isOnline ? "justify-end bg-[#16615F]/30 border-[#79B253]/40" : "justify-start bg-[#0f172a] border-white/10"
      )}
      style={{
        boxShadow: isOnline 
          ? 'inset 0 4px 10px rgba(0,0,0,0.5), 0 0 20px rgba(121,178,83,0.15)' 
          : 'inset 0 4px 10px rgba(0,0,0,0.8)'
      }}
    >
      <div className={cn(
        "absolute inset-0 flex items-center px-6 pointer-events-none z-0",
        isOnline ? "justify-start" : "justify-end"
      )}>
        <motion.span 
          key={isOnline ? "on" : "off"}
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className={cn(
            "font-extrabold text-[13px] uppercase tracking-wider",
            isOnline ? "text-[#79B253]" : "text-[#F32D17]"
          )}
        >
          {isOnline ? labelOn : labelOff}
        </motion.span>
      </div>

      <motion.div
        layout
        transition={{ type: "spring", stiffness: 500, damping: 30 }}
        className="w-[44px] h-[44px] rounded-full flex items-center justify-center relative z-10"
        style={{
           backgroundColor: '#020617',
           boxShadow: '0 4px 10px rgba(0,0,0,0.5), inset 0 1px 1px rgba(255,255,255,0.15)'
        }}
      >
        <Power className="w-5 h-5 transition-colors duration-500 relative z-10" style={{ color: isOnline ? '#79B253' : '#F32D17' }} />
        <div 
          className="absolute inset-0 rounded-full blur-[8px] opacity-60 transition-colors duration-500" 
          style={{ backgroundColor: isOnline ? '#79B253' : '#F32D17' }} 
        />
      </motion.div>
    </div>
  );
}

export default function NurseDashboard() {
  const { t, isRTL }         = useLanguage();
  const [isOnline, setIsOnline] = useState(false);
  const [mounted, setMounted]   = useState(false);
  const [isToggling, setIsToggling] = useState(false);
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  // --- Incoming Requests State ---
  const [requests, setRequests] = useState([
    { id: 'REQ-7201', patient: 'Mahmoud Saeed',  service: t.nurse?.activeMission ?? 'IV Drip & Vitals',  distance: '2.1 km', price: 180, time: '2 min', icon: Stethoscope },
    { id: 'REQ-7198', patient: 'Heba Mostafa',   service: t.patient?.serviceInjection ?? 'Injection',     distance: '3.4 km', price: 160, time: '5 min', icon: Syringe      },
    { id: 'REQ-7195', patient: 'Karim Adel',     service: t.patient?.serviceElderly ?? 'Elderly Care',    distance: '1.8 km', price: 350, time: '8 min', icon: HeartHandshake },
  ]);

  // --- Load toggle state from localStorage ---
  useEffect(() => {
    setMounted(true);
    const saved = typeof window !== 'undefined' ? localStorage.getItem('wateen_nurse_online') : null;
    if (saved === 'true') setIsOnline(true);
  }, []);

  // --- Mock API toggle handler ---
  const handleToggle = useCallback(async () => {
    if (isToggling) return;
    setIsToggling(true);
    setToast({ message: t.nurse?.connectingStatus ?? 'Connecting...', type: 'success' });

    // Simulate 800ms API call
    await new Promise(resolve => setTimeout(resolve, 800));

    const nextState = !isOnline;
    setIsOnline(nextState);
    localStorage.setItem('wateen_nurse_online', String(nextState));
    setIsToggling(false);
    setToast({
      message: nextState
        ? (t.nurse?.connectedStatus ?? 'Connected to dispatch')
        : (t.nurse?.disconnectedStatus ?? 'Disconnected from dispatch'),
      type: 'success',
    });

    // Auto-hide toast
    setTimeout(() => setToast(null), 2500);
  }, [isOnline, isToggling, t.nurse]);

  // --- Accept / Decline handlers ---
  const handleAccept = (id: string) => {
    setRequests(prev => prev.filter(r => r.id !== id));
  };
  const handleDecline = (id: string) => {
    setRequests(prev => prev.filter(r => r.id !== id));
  };

  if (!mounted) return null;

  const online  = t.nurse?.goOnline  ?? 'Go Online';
  const offline = t.nurse?.goOffline ?? 'Go Offline';

  return (
    <div
      className={`relative min-h-[calc(100vh-4rem)] bg-slate-950 text-slate-50 pb-24 ${isRTL ? 'font-arabic' : 'font-sans'}`}
      dir={isRTL ? 'rtl' : 'ltr'}
    >
      {/* ───── Hero with DotOrbit Background ───── */}
      <div className="relative w-full overflow-hidden" style={{ height: HERO_H }}>
        <NurseBackground isOnline={isOnline} height={HERO_H} />

        {/* Hero content */}
        <div className="relative z-20 h-full flex flex-col items-center justify-center gap-4 px-6 text-center">
          {/* Status LED */}
          <div className="flex items-center gap-2 mb-2">
            <span
              className={`w-2.5 h-2.5 rounded-full transition-colors duration-700 ${
                isOnline ? 'bg-[#79B253] shadow-[0_0_10px_rgba(121,178,83,0.9)] animate-pulse' : 'bg-slate-500'
              }`}
            />
            <span className="text-xs font-mono text-slate-400 uppercase tracking-widest">
              {isOnline ? 'ONLINE' : 'STANDBY'}
            </span>
          </div>

          {/* Title */}
          <div className="text-4xl sm:text-5xl md:text-6xl font-black text-white drop-shadow-lg leading-tight flex justify-center w-full mb-2">
            <FlipTextReveal title={t.nurse?.title ?? 'Welcome,'} highlightText="Ahmed" />
          </div>

          {/* Subtitle */}
          <p className="text-base text-slate-300/80 font-mono tracking-wider">
            {t.nurse?.subtitle ?? 'RN-4029 • ICU Unit'}
          </p>

          {/* Premium Physical Switch Toggle */}
          <StatusToggleSwitch 
            isOnline={isOnline} 
            onToggle={handleToggle} 
            labelOn={online} 
            labelOff={offline} 
          />

          {/* Toggle loading indicator */}
          {isToggling && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="mt-2 flex items-center gap-2"
            >
              <Loader2 className="w-3.5 h-3.5 text-slate-400 animate-spin" />
              <span className="text-xs text-slate-400 font-mono">{t.nurse?.connectingStatus ?? 'Connecting...'}</span>
            </motion.div>
          )}
        </div>
      </div>

      {/* Toast notification */}
      <AnimatePresence>
        {toast && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="fixed top-6 left-1/2 -translate-x-1/2 z-50 flex items-center gap-2 px-5 py-3 rounded-xl bg-slate-900/95 border border-slate-700 shadow-2xl backdrop-blur-xl"
          >
            <Check className="w-4 h-4 text-[#79B253]" />
            <span className="text-sm text-white font-medium">{toast.message}</span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ───── Main Content ───── */}
      <main id="main-content" className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-8">
        <motion.div variants={staggerContainer} initial="hidden" animate="show" className="space-y-6">

          {/* Active Visit Command Center */}
          <AnimatePresence>
            {isOnline && (
              <motion.div
                initial={{ opacity: 0, height: 0, scale: 0.95 }}
                animate={{ opacity: 1, height: 'auto', scale: 1 }}
                exit={{ opacity: 0, height: 0, scale: 0.95 }}
                className="overflow-hidden"
              >
                <div className="bg-gradient-to-r from-slate-900 to-slate-800 border border-[#16615F]/50 p-1 rounded-3xl relative">
                  <div className="absolute inset-0 bg-[#16615F]/5 blur-xl rounded-3xl" />
                  <div className="relative bg-slate-950/80 backdrop-blur-md rounded-[22px] p-5 sm:p-6 flex flex-col md:flex-row gap-6 items-start md:items-center justify-between border border-white/5">

                    <div className="flex gap-4 items-center">
                      <div className="relative shrink-0">
                        <div className="w-14 h-14 rounded-full bg-[#16615F]/10 border border-[#16615F]/40 flex items-center justify-center">
                          <Activity className="w-6 h-6 text-[#16615F]" />
                        </div>
                        <div className="absolute inset-0 rounded-full border-r border-[#16615F] animate-spin" style={{ animationDuration: '3s' }} />
                      </div>
                      <div>
                        <div className="flex flex-wrap items-center gap-2 mb-1">
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#16615F]/20 text-[#16615F] uppercase tracking-wider border border-[#16615F]/30">
                            {t.nurse?.activeMission ?? 'Active Mission'}
                          </span>
                          <span className="text-xs text-slate-400 font-mono">REQ-8942</span>
                        </div>
                        <h2 className="text-xl font-bold text-white mb-2">IV Drip & Vitals Check</h2>
                        <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4 text-sm text-slate-400">
                          <span className="flex items-center gap-1"><User className="w-4 h-4 shrink-0" /> Mahmoud Kamal</span>
                          <span className="hidden sm:inline text-slate-700">•</span>
                          <span className="flex items-center gap-1"><Map className="w-4 h-4 shrink-0" /> Maadi, Cairo</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex flex-col sm:flex-row items-center gap-4 w-full md:w-auto mt-4 md:mt-0">
                      <div className="bg-slate-900 border border-slate-800 rounded-xl px-4 py-3 flex items-center justify-center gap-3 w-full sm:w-auto">
                        <Clock className="w-5 h-5 text-[#FD8839]" />
                        <div className="text-left" dir="ltr">
                          <div className="text-xs text-slate-500 uppercase font-bold tracking-wider">ETA</div>
                          <div className="text-lg font-bold text-white leading-none">12 min</div>
                        </div>
                      </div>
                      <button className="w-full sm:w-auto bg-[#16615F] hover:bg-[#16615F]/80 text-white font-bold px-6 py-3.5 rounded-xl transition-all shadow-[0_0_20px_rgba(22,97,95,0.3)] hover:shadow-[0_0_30px_rgba(22,97,95,0.5)] flex items-center justify-center gap-2 cursor-pointer">
                        <Navigation className="w-5 h-5" />
                        {t.nurse?.navigate ?? 'Navigate'}
                      </button>
                    </div>

                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* ─── Incoming Requests Queue ─── */}
          <AnimatePresence>
            {isOnline && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="overflow-hidden"
              >
                <div className="mb-2">
                  <h2 className="text-base font-bold text-slate-300 flex items-center gap-2 mb-4">
                    <span className="w-1.5 h-5 rounded-full bg-[#FD8839]" />
                    {t.nurse?.incomingRequests ?? 'Incoming Requests'}
                    {requests.length > 0 && (
                      <span className="ml-2 px-2 py-0.5 text-[10px] font-bold rounded-full bg-[#FD8839]/15 text-[#FD8839] border border-[#FD8839]/20">
                        {requests.length}
                      </span>
                    )}
                  </h2>

                  {requests.length === 0 ? (
                    /* Empty incoming requests state */
                    <div className="bg-slate-900/30 border border-dashed border-slate-700 rounded-2xl p-8 flex flex-col items-center text-center">
                      <div className="w-12 h-12 rounded-full bg-slate-800/80 border border-slate-700 flex items-center justify-center mb-3">
                        <Activity className="w-5 h-5 text-slate-500" />
                      </div>
                      <h3 className="text-sm font-bold text-slate-400">{t.nurse?.noRequests ?? 'No Incoming Requests'}</h3>
                      <p className="text-xs text-slate-500 max-w-xs mt-1">{t.nurse?.noRequestsDesc ?? 'New requests will show here.'}</p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      <AnimatePresence>
                        {requests.map((req) => {
                          const ReqIcon = req.icon;
                          return (
                            <motion.div
                              key={req.id}
                              layout
                              initial={{ opacity: 0, x: isRTL ? -30 : 30 }}
                              animate={{ opacity: 1, x: 0 }}
                              exit={{ opacity: 0, x: isRTL ? 30 : -30, height: 0, marginBottom: 0 }}
                              transition={{ type: 'spring', stiffness: 400, damping: 28 }}
                              className="bg-slate-900/60 backdrop-blur-md border border-slate-800 hover:border-slate-700 rounded-2xl p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 transition-colors"
                            >
                              {/* Request Info */}
                              <div className="flex items-center gap-3 w-full sm:w-auto">
                                <div className="w-10 h-10 rounded-xl bg-[#16615F]/10 border border-[#16615F]/30 flex items-center justify-center shrink-0">
                                  <ReqIcon className="w-5 h-5 text-[#16615F]" />
                                </div>
                                <div className="flex-1 min-w-0">
                                  <div className="flex items-center gap-2 mb-0.5">
                                    <span className="text-[10px] font-mono text-slate-500">{req.id}</span>
                                    <span className="text-[10px] text-slate-600">•</span>
                                    <span className="text-[10px] text-slate-500 flex items-center gap-0.5">
                                      <Clock className="w-2.5 h-2.5" /> {req.time} {t.nurse?.timeAgo ?? 'ago'}
                                    </span>
                                  </div>
                                  <h4 className="font-bold text-sm text-white truncate">{req.service}</h4>
                                  <div className="flex items-center gap-3 mt-1 text-xs text-slate-400">
                                    <span className="flex items-center gap-1"><User className="w-3 h-3" /> {req.patient}</span>
                                    <span className="flex items-center gap-1"><MapPin className="w-3 h-3" /> {req.distance}</span>
                                    <span className="font-bold text-[#79B253]">{req.price} EGP</span>
                                  </div>
                                </div>
                              </div>

                              {/* Action Buttons */}
                              <div className="flex items-center gap-2 w-full sm:w-auto">
                                <button
                                  onClick={() => handleDecline(req.id)}
                                  className="flex-1 sm:flex-none flex items-center justify-center gap-1.5 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 hover:border-slate-600 text-slate-300 text-xs font-bold transition-all cursor-pointer"
                                >
                                  <X className="w-3.5 h-3.5" />
                                  {t.nurse?.declineRequest ?? 'Decline'}
                                </button>
                                <button
                                  onClick={() => handleAccept(req.id)}
                                  className="flex-1 sm:flex-none flex items-center justify-center gap-1.5 px-5 py-2.5 rounded-xl bg-[#16615F] hover:bg-[#16615F]/80 text-white text-xs font-bold transition-all shadow-[0_0_15px_rgba(22,97,95,0.3)] hover:shadow-[0_0_25px_rgba(22,97,95,0.5)] cursor-pointer"
                                >
                                  <Check className="w-3.5 h-3.5" />
                                  {t.nurse?.acceptRequest ?? 'Accept'}
                                </button>
                              </div>
                            </motion.div>
                          );
                        })}
                      </AnimatePresence>
                    </div>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Grid: Radar + Stats */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">

            {/* Tactical Radar Map */}
            <motion.div variants={fadeUp} className="lg:col-span-8 bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-3xl overflow-hidden flex flex-col min-h-[400px]">
              <div className="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-900/80">
                <div className="flex items-center gap-2">
                  <Target className="w-5 h-5 text-[#16615F]" />
                  <h3 className="font-bold text-white">
                    {t.nurse?.radarTitle ?? 'Mission Radar'}
                  </h3>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`w-2 h-2 rounded-full ${isOnline ? 'bg-[#79B253] animate-pulse' : 'bg-slate-500'}`} />
                  <span className="text-xs text-slate-400 font-mono hidden sm:inline">
                    {isOnline ? (t.nurse?.radarScanning ?? 'SCANNING SECTOR 7G') : (t.nurse?.radarStandby ?? 'SYSTEM STANDBY')}
                  </span>
                </div>
              </div>

              <div className="flex-1 relative bg-[#0f172a] flex items-center justify-center overflow-hidden min-h-[300px]">
                <div className="absolute inset-0 border border-slate-800/50 rounded-full scale-[2] opacity-20" />
                <div className="absolute inset-0 border border-slate-800/50 rounded-full scale-[1.5] opacity-20" />
                <div className="absolute inset-0 border border-slate-800/50 rounded-full scale-[1] opacity-20" />
                <div className="absolute inset-0 border border-slate-800/50 rounded-full scale-[0.5] opacity-20" />

                {isOnline && (
                  <div className="absolute w-[200%] h-[200%] origin-center animate-[spin_4s_linear_infinite]"
                    style={{ background: 'conic-gradient(from 0deg, transparent 70%, rgba(22, 97, 95, 0.4) 100%)' }} />
                )}

                <div className={`absolute w-4 h-4 rounded-full z-10 ${isOnline ? 'bg-[#16615F] shadow-[0_0_15px_rgba(22,97,95,0.8)]' : 'bg-slate-600'}`} />

                {isOnline && (
                  <>
                    <div className="absolute top-[30%] left-[30%] text-[#FD8839] flex flex-col items-center gap-1 group cursor-pointer z-10 transition-transform hover:scale-110">
                      <div className="w-3 h-3 bg-[#FD8839] rounded-full shadow-[0_0_10px_rgba(253,136,57,0.8)] animate-pulse" />
                      <div className="opacity-0 group-hover:opacity-100 absolute top-4 bg-slate-900 border border-slate-700 p-2 rounded text-xs whitespace-nowrap transition-opacity shadow-lg">
                        <div className="font-bold text-white">Wound Care</div>
                        <div className="text-slate-400">2.4 km • 150 EGP</div>
                      </div>
                    </div>
                    <div className="absolute bottom-[25%] right-[25%] text-[#79B253] flex flex-col items-center gap-1 group cursor-pointer z-10 transition-transform hover:scale-110">
                      <div className="w-3 h-3 bg-[#79B253] rounded-full shadow-[0_0_10px_rgba(121,178,83,0.8)]" />
                      <div className="opacity-0 group-hover:opacity-100 absolute top-4 bg-slate-900 border border-slate-700 p-2 rounded text-xs whitespace-nowrap transition-opacity shadow-lg">
                        <div className="font-bold text-white">Vitals Check</div>
                        <div className="text-slate-400">4.1 km • 100 EGP</div>
                      </div>
                    </div>
                  </>
                )}

                {!isOnline && (
                  <div className="absolute inset-0 bg-slate-950/60 backdrop-blur-[2px] z-20 flex items-center justify-center p-4">
                    <div className="bg-slate-900/90 border border-slate-800 px-6 py-5 rounded-xl text-center shadow-xl max-w-sm">
                      <ShieldAlert className="w-8 h-8 text-slate-500 mx-auto mb-3" />
                      <p className="text-slate-300 font-medium">
                        {t.nurse?.radarOfflineMsg ?? 'Radar offline. Activate your status to receive requests.'}
                      </p>
                      <button
                        onClick={() => setIsOnline(true)}
                        className="mt-4 bg-slate-800 hover:bg-slate-700 text-white text-sm font-bold py-2 px-4 rounded-lg transition-colors border border-slate-700 hover:border-slate-600 cursor-pointer"
                      >
                        {t.nurse?.activateNow ?? 'Activate Now'}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </motion.div>

            {/* Performance & Earnings */}
            <motion.div variants={fadeUp} className="lg:col-span-4 flex flex-col gap-6">

              {/* Today's Earnings */}
              <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 p-6 rounded-3xl relative overflow-hidden group hover:border-[#79B253]/30 transition-colors">
                <div className="absolute top-0 right-0 w-32 h-32 bg-[#79B253]/5 rounded-full blur-3xl group-hover:bg-[#79B253]/10 transition-colors" />
                <h3 className="font-bold text-slate-300 mb-6 flex items-center gap-2">
                  <Wallet className="w-5 h-5 text-[#79B253]" />
                  {t.nurse?.todayEarnings ?? "Today's Earnings"}
                </h3>
                <div className="flex items-end gap-2 mb-8">
                  <span className="text-5xl font-black text-white tracking-tight">1,250</span>
                  <span className="text-lg text-slate-500 font-bold mb-1">EGP</span>
                </div>
                <div className="space-y-4 relative z-10">
                  <div className="flex justify-between items-center bg-slate-800/50 px-4 py-3 rounded-xl border border-slate-700/50">
                    <span className="text-slate-400 text-sm font-medium">{t.nurse?.completedVisits ?? 'Completed Visits'}</span>
                    <span className="font-bold text-white bg-slate-700/50 px-3 py-1 rounded-md">4</span>
                  </div>
                  <div className="flex justify-between items-center bg-slate-800/50 px-4 py-3 rounded-xl border border-slate-700/50">
                    <span className="text-slate-400 text-sm font-medium">{t.nurse?.zoneMultiplier ?? 'Zone Multiplier'}</span>
                    <span className="font-bold text-[#FD8839] flex items-center gap-1.5 bg-[#FD8839]/10 px-3 py-1 rounded-md border border-[#FD8839]/20">
                      1.2x <Activity className="w-3 h-3" />
                    </span>
                  </div>
                </div>
              </div>

              {/* Performance */}
              <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 p-6 rounded-3xl flex-1 group hover:border-[#FD8839]/30 transition-colors">
                <h3 className="font-bold text-slate-300 mb-6 flex items-center gap-2">
                  <Star className="w-5 h-5 text-[#FD8839]" />
                  {t.nurse?.performance ?? 'Performance'}
                </h3>
                <div className="flex items-center gap-6 mb-2">
                  <div className="relative w-24 h-24 flex items-center justify-center shrink-0">
                    <svg className="w-full h-full transform -rotate-90">
                      <circle cx="48" cy="48" r="40" stroke="currentColor" strokeWidth="8" fill="transparent" className="text-slate-800" />
                      <circle cx="48" cy="48" r="40" stroke="currentColor" strokeWidth="8" fill="transparent"
                        strokeDasharray="251.2" strokeDashoffset="25.12"
                        className="text-[#FD8839] transition-all duration-1000 ease-out drop-shadow-[0_0_8px_rgba(253,136,57,0.5)]"
                        strokeLinecap="round" />
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                      <span className="text-2xl font-bold text-white">4.9</span>
                    </div>
                  </div>
                  <div className="flex-1 space-y-3">
                    <div>
                      <div className="flex justify-between text-sm mb-1.5">
                        <span className="text-slate-400 font-medium">{t.nurse?.acceptanceRate ?? 'Acceptance Rate'}</span>
                        <span className="text-[#79B253] font-bold">98%</span>
                      </div>
                      <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                        <div className="bg-[#79B253] h-full rounded-full w-[98%] relative">
                          <div className="absolute inset-0 bg-white/20 w-1/2 rounded-full" />
                        </div>
                      </div>
                    </div>
                    <div className="flex justify-between text-sm pt-2 border-t border-slate-800/50">
                      <span className="text-slate-400 font-medium">{t.nurse?.avgResponse ?? 'Avg. Response'}</span>
                      <span className="text-white font-bold bg-slate-800 px-2 py-0.5 rounded text-xs">12s</span>
                    </div>
                  </div>
                </div>
              </div>

            </motion.div>
          </div>

        </motion.div>
      </main>
    </div>
  );
}
