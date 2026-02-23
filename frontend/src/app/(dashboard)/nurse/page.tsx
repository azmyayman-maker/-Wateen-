'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { motion, AnimatePresence, useMotionValue, useTransform } from 'framer-motion';
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
  HeartHandshake,
  ArrowRight,
  ShieldCheck,
  AlertTriangle,
  Zap,
  Timer
} from 'lucide-react';
import { NurseBackground } from '@/components/ui/nurse-background';
import FlipTextReveal from '@/components/ui/next-reveal';
import LocationPicker from '@/components/shared/map/LocationPicker';
import {
  toggleNurseAvailability,
  getPendingVisits,
  respondToVisit,
  type PendingVisit,
} from '@/lib/api/nurse';
import { useWateenWebSocket } from '@/hooks/useWateenWebSocket';

const staggerContainer = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.1 } },
};

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 300, damping: 24 } },
};

const HERO_H = 430;
const COUNTDOWN_SECONDS = 30;

// ─── Status Toggle Switch ────────────────────────────────────────────────────

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

// ─── Countdown Ring ──────────────────────────────────────────────────────────

function CountdownRing({ seconds, total, size = 40 }: { seconds: number; total: number; size?: number }) {
  const radius = (size - 4) / 2;
  const circumference = 2 * Math.PI * radius;
  const progress = seconds / total;
  const strokeDashoffset = circumference * (1 - progress);
  const isUrgent = seconds <= 10;

  return (
    <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
      <svg className="transform -rotate-90" width={size} height={size}>
        <circle
          cx={size / 2} cy={size / 2} r={radius}
          stroke="currentColor" strokeWidth="3" fill="transparent"
          className="text-slate-800"
        />
        <circle
          cx={size / 2} cy={size / 2} r={radius}
          stroke="currentColor" strokeWidth="3" fill="transparent"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          className={cn(
            "transition-all duration-1000 ease-linear",
            isUrgent ? "text-[#F32D17] drop-shadow-[0_0_6px_rgba(243,45,23,0.6)]" : "text-[#FD8839]"
          )}
        />
      </svg>
      <span className={cn(
        "absolute text-[11px] font-black tabular-nums",
        isUrgent ? "text-[#F32D17]" : "text-slate-300"
      )}>
        {seconds}
      </span>
    </div>
  );
}

// ─── Swipe-to-Accept Thumb ───────────────────────────────────────────────────

function SwipeToAccept({ onAccept, isRTL }: { onAccept: () => void; isRTL: boolean }) {
  const dragX = useMotionValue(0);
  const swipeProgress = useTransform(dragX, [0, 200], [0, 1]);
  const bgOpacity = useTransform(swipeProgress, [0, 1], [0, 1]);
  const [confirmed, setConfirmed] = useState(false);

  useEffect(() => {
    const unsub = dragX.on('change', (v) => {
      if (v > 190 && !confirmed) {
        setConfirmed(true);
        onAccept();
      }
    });
    return unsub;
  }, [dragX, confirmed, onAccept]);

  return (
    <div className="relative h-12 w-full min-w-[220px] sm:min-w-[260px] max-w-[260px] shrink-0 rounded-full overflow-hidden border border-white/10 bg-slate-800/80">
      {/* Green fill */}
      <motion.div
        className="absolute inset-y-0 left-0 w-full origin-left bg-[#16615F] rounded-full"
        style={{ scaleX: swipeProgress, opacity: bgOpacity }}
      />
      
      {/* Label */}
      <AnimatePresence mode="wait">
        {!confirmed ? (
          <motion.div key="hint" exit={{ opacity: 0 }} className="absolute inset-0 flex items-center justify-center pointer-events-none z-10">
            <span className="text-white/40 text-xs font-bold tracking-wider ps-12">
              {isRTL ? '← اسحب للقبول' : 'Swipe to Accept →'}
            </span>
          </motion.div>
        ) : (
          <motion.div key="ok" initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} className="absolute inset-0 flex items-center justify-center pointer-events-none z-10 bg-[#16615F] rounded-full">
            <span className="text-white font-bold text-sm flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4" /> {isRTL ? 'تم القبول!' : 'Accepted!'}
            </span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Draggable thumb */}
      {!confirmed && (
        <motion.div
          drag="x"
          dragConstraints={{ left: 0, right: 200 }}
          dragElastic={0}
          dragMomentum={false}
          style={{ x: dragX }}
          whileTap={{ scale: 1.1 }}
          className="absolute top-0.5 left-0.5 bottom-0.5 w-11 rounded-full bg-[#16615F] shadow-[0_0_15px_rgba(22,97,95,0.5)] flex items-center justify-center z-20 cursor-grab active:cursor-grabbing border border-[#79B253]/50"
        >
          <ArrowRight className="w-4 h-4 text-white" />
        </motion.div>
      )}
    </div>
  );
}

// ─── Incoming Request Card ───────────────────────────────────────────────────

interface RequestCardData {
  id: string;
  patient_name: string;
  service_name: string;
  estimated_price: string;
  created_at: string;
  distance_km: number | null;
}

function IncomingRequestCard({
  req,
  onAccept,
  onDecline,
  isRTL,
  t,
}: {
  req: RequestCardData;
  onAccept: (id: string) => void;
  onDecline: (id: string) => void;
  isRTL: boolean;
  t: any;
}) {
  const [countdown, setCountdown] = useState(COUNTDOWN_SECONDS);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    timerRef.current = setInterval(() => {
      setCountdown(prev => {
        if (prev <= 1) {
          clearInterval(timerRef.current!);
          onDecline(req.id);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => { if (timerRef.current) clearInterval(timerRef.current); };
  }, [req.id, onDecline]);

  const handleAccept = useCallback(() => {
    if (timerRef.current) clearInterval(timerRef.current);
    onAccept(req.id);
  }, [req.id, onAccept]);

  const handleDecline = useCallback(() => {
    if (timerRef.current) clearInterval(timerRef.current);
    onDecline(req.id);
  }, [req.id, onDecline]);

  // Pick an icon based on service name
  const getServiceIcon = (name: string) => {
    const lower = name.toLowerCase();
    if (lower.includes('iv') || lower.includes('drip') || lower.includes('محلول')) return Syringe;
    if (lower.includes('injection') || lower.includes('حقن')) return Syringe;
    if (lower.includes('elderly') || lower.includes('مسنين')) return HeartHandshake;
    if (lower.includes('stethoscope') || lower.includes('vitals') || lower.includes('حيوي')) return Stethoscope;
    return Activity;
  };

  const ServiceIcon = getServiceIcon(req.service_name);
  const distanceText = req.distance_km ? `${req.distance_km.toFixed(1)} km` : '—';
  const timeSinceCreated = getTimeSince(req.created_at);

  return (
    <motion.div
      layout
      initial={{ opacity: 0, x: isRTL ? -40 : 40, scale: 0.95 }}
      animate={{ opacity: 1, x: 0, scale: 1 }}
      exit={{ opacity: 0, x: isRTL ? 40 : -40, scale: 0.9, height: 0, marginBottom: 0 }}
      transition={{ type: 'spring', stiffness: 350, damping: 28 }}
      className={cn(
        "border rounded-2xl p-4 backdrop-blur-md transition-colors relative overflow-hidden",
        countdown <= 10
          ? "bg-[#F32D17]/5 border-[#F32D17]/30"
          : "bg-slate-900/60 border-slate-800 hover:border-slate-700"
      )}
    >
      {/* Urgent glow */}
      {countdown <= 10 && (
        <div className="absolute inset-0 bg-gradient-to-r from-[#F32D17]/5 to-transparent pointer-events-none" />
      )}

      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 relative z-10">
        {/* Left: Info */}
        <div className="flex items-center gap-3 w-full sm:w-auto">
          <div className="relative shrink-0">
            <div className="w-12 h-12 rounded-xl bg-[#16615F]/10 border border-[#16615F]/30 flex items-center justify-center">
              <ServiceIcon className="w-5 h-5 text-[#16615F]" />
            </div>
            {/* Countdown ring overlaid on icon */}
            <div className="absolute -top-1.5 -end-1.5">
              <CountdownRing seconds={countdown} total={COUNTDOWN_SECONDS} size={28} />
            </div>
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-0.5">
              <span className="text-[10px] font-mono text-slate-500">{req.id.slice(0, 8).toUpperCase()}</span>
              <span className="text-[10px] text-slate-600">•</span>
              <span className="text-[10px] text-slate-500 flex items-center gap-0.5">
                <Clock className="w-2.5 h-2.5" /> {timeSinceCreated}
              </span>
            </div>
            <h4 className="font-bold text-sm text-white truncate">{req.service_name}</h4>
            <div className="flex items-center gap-3 mt-1 text-xs text-slate-400">
              <span className="flex items-center gap-1"><User className="w-3 h-3" /> {req.patient_name}</span>
              <span className="flex items-center gap-1"><MapPin className="w-3 h-3" /> {distanceText}</span>
              <span className="font-bold text-[#79B253]">{req.estimated_price} EGP</span>
            </div>
          </div>
        </div>

        {/* Right: Actions */}
        <div className="flex items-center gap-2 w-full sm:w-auto">
          <button
            onClick={handleDecline}
            className="flex-1 sm:flex-none flex items-center justify-center gap-1.5 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 hover:border-slate-600 text-slate-300 text-xs font-bold transition-all cursor-pointer"
          >
            <X className="w-3.5 h-3.5" />
            {t.nurse?.declineRequest ?? 'Decline'}
          </button>
          <SwipeToAccept onAccept={handleAccept} isRTL={isRTL} />
        </div>
      </div>
    </motion.div>
  );
}

// ─── Helper ──────────────────────────────────────────────────────────────────

function getTimeSince(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  return `${Math.floor(mins / 60)}h ago`;
}

// ─── Main Dashboard ──────────────────────────────────────────────────────────

export default function NurseDashboard() {
  const { t, isRTL }         = useLanguage();
  const [isOnline, setIsOnline] = useState(false);
  const [mounted, setMounted]   = useState(false);
  const [isToggling, setIsToggling] = useState(false);
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  // Incoming requests — starts with mock data, gets replaced by API response
  const [requests, setRequests] = useState<RequestCardData[]>([
    { id: 'REQ-7201', patient_name: 'Mahmoud Saeed',  service_name: 'IV Drip & Vitals', distance_km: 2.1, estimated_price: '180', created_at: new Date(Date.now() - 120000).toISOString() },
    { id: 'REQ-7198', patient_name: 'Heba Mostafa',   service_name: 'Injection',        distance_km: 3.4, estimated_price: '160', created_at: new Date(Date.now() - 300000).toISOString() },
    { id: 'REQ-7195', patient_name: 'Karim Adel',     service_name: 'Elderly Care',     distance_km: 1.8, estimated_price: '350', created_at: new Date(Date.now() - 480000).toISOString() },
  ]);
  const [acceptedVisit, setAcceptedVisit] = useState<RequestCardData | null>(null);
  const [apiError, setApiError] = useState<string | null>(null);

  // Load toggle state
  useEffect(() => {
    setMounted(true);
    const saved = typeof window !== 'undefined' ? localStorage.getItem('wateen_nurse_online') : null;
    if (saved === 'true') setIsOnline(true);
  }, []);

  // Fetch pending visits when online (with polling every 15s)
  useEffect(() => {
    if (!isOnline || !mounted) return;

    const fetchPending = async () => {
      try {
        const visits = await getPendingVisits();
        if (visits.length > 0) {
          setRequests(visits.map(v => ({
            id: v.id,
            patient_name: v.patient_name,
            service_name: v.service_name,
            distance_km: v.distance_km,
            estimated_price: v.estimated_price,
            created_at: v.created_at,
          })));
        }
        setApiError(null);
      } catch {
        // Silently fall back to mock data — backend may not be running
        setApiError(null);
      }
    };

    fetchPending();
    // Replaced short polling with initial fetch + WebSockets
    // const interval = setInterval(fetchPending, 15000);
    // return () => clearInterval(interval);
  }, [isOnline, mounted]);

  // WebSocket Integration
  const handleWebSocketMessage = useCallback((msg: any) => {
    if (msg.type === 'new_visit' && msg.visit) {
      const v = msg.visit;
      setRequests(prev => {
        if (prev.find(r => r.id === v.id)) return prev;
        return [{
          id: v.id,
          patient_name: v.patient_name,
          service_name: v.service_name,
          distance_km: v.distance_km,
          estimated_price: v.estimated_price,
          created_at: v.created_at,
        }, ...prev];
      });
      // Optionally play a sound or show a toast
      setToast({ message: 'New visit request received!', type: 'success' });
    }
  }, []);

  const wsPath = isOnline ? 'ws/nurse/' : '';
  const { isConnected: wsConnected } = useWateenWebSocket(wsPath, handleWebSocketMessage);

  // Toggle handler
  const handleToggle = useCallback(async () => {
    if (isToggling) return;
    setIsToggling(true);
    setToast({ message: t.nurse?.connectingStatus ?? 'Connecting...', type: 'success' });

    const nextState = !isOnline;

    try {
      await toggleNurseAvailability({
        is_online: nextState,
        latitude: nextState ? 30.0444 : null,  // Cairo as default
        longitude: nextState ? 31.2357 : null,
      });
    } catch {
      // Fallback — allow toggle even without backend
    }

    setIsOnline(nextState);
    localStorage.setItem('wateen_nurse_online', String(nextState));
    setIsToggling(false);
    setToast({
      message: nextState
        ? (t.nurse?.connectedStatus ?? 'Connected to dispatch')
        : (t.nurse?.disconnectedStatus ?? 'Disconnected from dispatch'),
      type: 'success',
    });
    setTimeout(() => setToast(null), 2500);
  }, [isOnline, isToggling, t.nurse]);

  // Accept handler 
  const handleAccept = useCallback(async (id: string) => {
    const accepted = requests.find(r => r.id === id);
    if (accepted) setAcceptedVisit(accepted);
    setRequests(prev => prev.filter(r => r.id !== id));

    try {
      await respondToVisit({ visit_id: id, action: 'accept' });
    } catch {
      // Fallback — allow accept even without backend
    }
  }, [requests]);

  // Decline handler
  const handleDecline = useCallback(async (id: string) => {
    setRequests(prev => prev.filter(r => r.id !== id));
    try {
      await respondToVisit({ visit_id: id, action: 'decline' });
    } catch {
      // Fallback
    }
  }, []);

  if (!mounted) return null;

  const online  = t.nurse?.goOnline  ?? 'Go Online';
  const offline = t.nurse?.goOffline ?? 'Go Offline';

  return (
    <div
      className={`relative min-h-[calc(100vh-4rem)] bg-slate-950 text-slate-50 pb-24 select-none ${isRTL ? 'font-arabic' : 'font-sans'}`}
      dir={isRTL ? 'rtl' : 'ltr'}
    >
      {/* ───── Hero with DotOrbit Background ───── */}
      <div className="relative w-full overflow-hidden" style={{ height: HERO_H }}>
        <NurseBackground isOnline={isOnline} height={HERO_H} />

        <div className="relative z-20 h-full flex flex-col items-center justify-center gap-4 px-6 text-center">
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

          <div className="text-4xl sm:text-5xl md:text-6xl font-black text-white drop-shadow-lg leading-tight flex justify-center w-full mb-2">
            <FlipTextReveal title={t.nurse?.title ?? 'Welcome,'} highlightText="Ahmed" />
          </div>

          <p className="text-base text-slate-300/80 font-mono tracking-wider">
            {t.nurse?.subtitle ?? 'RN-4029 • ICU Unit'}
          </p>

          <StatusToggleSwitch 
            isOnline={isOnline} 
            onToggle={handleToggle} 
            labelOn={online} 
            labelOff={offline} 
          />

          {isToggling && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mt-2 flex items-center gap-2">
              <Loader2 className="w-3.5 h-3.5 text-slate-400 animate-spin" />
              <span className="text-xs text-slate-400 font-mono">{t.nurse?.connectingStatus ?? 'Connecting...'}</span>
            </motion.div>
          )}
        </div>
      </div>

      {/* Toast */}
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
            {isOnline && acceptedVisit && (
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
                          <span className="text-xs text-slate-400 font-mono">{acceptedVisit.id.slice(0, 8).toUpperCase()}</span>
                        </div>
                        <h2 className="text-xl font-bold text-white mb-2">{acceptedVisit.service_name}</h2>
                        <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4 text-sm text-slate-400">
                          <span className="flex items-center gap-1"><User className="w-4 h-4 shrink-0" /> {acceptedVisit.patient_name}</span>
                          <span className="hidden sm:inline text-slate-700">•</span>
                          <span className="flex items-center gap-1"><MapPin className="w-4 h-4 shrink-0" /> {acceptedVisit.distance_km?.toFixed(1) ?? '—'} km</span>
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
                        {requests.map((req) => (
                          <IncomingRequestCard
                            key={req.id}
                            req={req}
                            onAccept={handleAccept}
                            onDecline={handleDecline}
                            isRTL={isRTL}
                            t={t}
                          />
                        ))}
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

              <div className="flex-1 relative bg-[#0f172a] rounded-b-3xl overflow-hidden min-h-[300px]">
                <LocationPicker 
                  readOnly 
                  initialLocation={[30.0444, 31.2357]} 
                  className={cn("w-full h-full min-h-[300px] transition-opacity duration-1000", isOnline ? "opacity-100" : "opacity-30 blur-[2px]")}
                />

                {isOnline && (
                  <div className="absolute inset-0 pointer-events-none z-10 flex items-center justify-center">
                    <div className="absolute inset-0 bg-gradient-to-t from-slate-950/80 via-transparent to-transparent" />
                    <div className="relative w-full h-full max-w-sm max-h-sm origin-center animate-[spin_4s_linear_infinite] opacity-30"
                      style={{ background: 'conic-gradient(from 0deg, transparent 70%, rgba(22, 97, 95, 0.4) 100%)', borderRadius: '50%' }} />
                    
                    <div className="absolute w-4 h-4 rounded-full z-10 bg-[#16615F] shadow-[0_0_15px_rgba(22,97,95,0.8)]" />
                    
                    {/* Simulated nearby requests on the map */}
                    <div className="absolute top-[30%] left-[30%] text-[#FD8839] flex flex-col items-center gap-1 group cursor-pointer z-20 pointer-events-auto transition-transform hover:scale-110">
                      <div className="w-3 h-3 bg-[#FD8839] rounded-full shadow-[0_0_10px_rgba(253,136,57,0.8)] animate-pulse" />
                      <div className="opacity-0 group-hover:opacity-100 absolute top-4 bg-slate-900 border border-slate-700 p-2 rounded text-xs whitespace-nowrap transition-opacity shadow-lg">
                        <div className="font-bold text-white">Wound Care</div>
                        <div className="text-slate-400">2.4 km • 150 EGP</div>
                      </div>
                    </div>
                    <div className="absolute bottom-[35%] right-[25%] text-[#79B253] flex flex-col items-center gap-1 group cursor-pointer z-20 pointer-events-auto transition-transform hover:scale-110">
                      <div className="w-3 h-3 bg-[#79B253] rounded-full shadow-[0_0_10px_rgba(121,178,83,0.8)]" />
                      <div className="opacity-0 group-hover:opacity-100 absolute top-4 bg-slate-900 border border-slate-700 p-2 rounded text-xs whitespace-nowrap transition-opacity shadow-lg">
                        <div className="font-bold text-white">Vitals Check</div>
                        <div className="text-slate-400">4.1 km • 100 EGP</div>
                      </div>
                    </div>
                  </div>
                )}

                {!isOnline && (
                  <div className="absolute inset-0 bg-slate-950/40 z-20 flex items-center justify-center p-4">
                    <div className="bg-slate-900/90 border border-slate-800 px-6 py-5 rounded-xl text-center shadow-xl max-w-sm backdrop-blur-md">
                      <ShieldAlert className="w-8 h-8 text-slate-500 mx-auto mb-3" />
                      <p className="text-slate-300 font-medium">
                        {t.nurse?.radarOfflineMsg ?? 'Map offline. Activate your status to receive requests.'}
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
