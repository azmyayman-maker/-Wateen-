'use client';

import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useLanguage } from '@/lib/i18n';
import { 
  Heart, 
  Droplets,
  Video,
  AlertTriangle,
  ChevronRight,
  ChevronLeft,
  Clock,
  Activity,
  MapPin,
  Syringe,
  Scissors,
  Stethoscope,
  Dumbbell,
  HeartHandshake,
  CalendarCheck,
  X,
  Star,
  CheckCircle2
} from 'lucide-react';
import Image from 'next/image';
import Link from 'next/link';
import { HeroSection } from '@/components/ui/hero-section-with-smooth-bg-shader';
import { SlideButton } from '@/components/ui/slide-button';
import { useDataFetch } from '@/hooks/useDataFetch';
import { useWateenWebSocket } from '@/hooks/useWateenWebSocket';
import { 
  CannulaFluidsSVG, IronIV_SVG, CatheterFeedingSVG, BloodSamplingSVG,
  InjectionsSVG, VitalsMonitorSVG, WoundCareSVG, StitchRemovalSVG, 
  OxygenMeasurementSVG, HolographicPulse 
} from '@/components/services/ServicesGrid';

// --- Brand Color Palette ---
// Teal:   #16615F — Primary, Trust
// Green:  #79B253 — Success, Healthy
// Red:    #F32D17 — Alert, SOS
// Orange: #FD8839 — Warning, Action

const THEME = {
  teal:   '22, 97, 95',
  green:  '121, 178, 83',
  red:    '243, 45, 23',
  orange: '253, 136, 57',
};

const staggerContainer = {
  hidden: { opacity: 0 },
  show:   { opacity: 1, transition: { staggerChildren: 0.1 } },
};

const slideUp = {
  hidden: { opacity: 0, y: 30 },
  show:   { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 300, damping: 24 } },
};

const scaleIn = {
  hidden: { opacity: 0, scale: 0.9 },
  show:   { opacity: 1, scale: 1, transition: { type: 'spring', stiffness: 300, damping: 24 } },
};

// --- Sub-components ---

interface HealthOrbProps {
  icon: React.ComponentType<{ className?: string; style?: React.CSSProperties }>;
  value: string;
  unit: string;
  label: string;
  colorRgb: string;
  delay?: number;
}

interface VisitData {
  service: string;
  nurse: string;
  date: string;
  price: number;
  status: 'completed' | 'cancelled' | 'rated';
  rating: number;
}

const HealthOrb = ({ icon: Icon, value, unit, label, colorRgb, delay = 0 }: HealthOrbProps) => (
  <motion.div
    variants={scaleIn}
    animate={{ y: [0, -8, 0] }}
    transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut', delay }}
    className="relative flex flex-col items-center justify-center w-[110px] h-[110px] rounded-full backdrop-blur-xl border border-white/10 group cursor-pointer overflow-hidden shadow-2xl"
    style={{
      background:  `linear-gradient(145deg, rgba(${colorRgb}, 0.15) 0%, rgba(0,0,0,0.6) 100%)`,
      boxShadow:   `0 10px 30px rgba(0,0,0,0.5), inset 0 0 20px rgba(${colorRgb}, 0.1)`,
    }}
  >
    <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent z-0 pointer-events-none" />
    <Icon className="w-6 h-6 mb-1 relative z-10" style={{ color: `rgb(${colorRgb})` }} />
    <div className="flex items-baseline gap-1 relative z-10">
      <span className="text-xl font-bold text-white tracking-tight">{value}</span>
      {unit && <span className="text-[10px] text-slate-300">{unit}</span>}
    </div>
    <span className="text-[9px] uppercase font-bold tracking-widest text-slate-400 mt-1 relative z-10">
      {label}
    </span>
    <div
      className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 z-0 pointer-events-none"
      style={{ background: `radial-gradient(circle at center, rgba(${colorRgb}, 0.4) 0%, transparent 70%)` }}
    />
  </motion.div>
);

// --- Page ---

export default function PatientDashboard() {
  const { t, isRTL, dir } = useLanguage();
  const [mounted, setMounted] = useState(false);
  const [hasActiveBooking, setHasActiveBooking] = useState(false);
  const [activeVisitData, setActiveVisitData] = useState<any>(null);

  const handleWebSocketMessage = useCallback((msg: any) => {
    if (msg.type === 'visit_accepted' && msg.visit) {
      setActiveVisitData(msg);
      setHasActiveBooking(true);
    }
  }, []);

  useWateenWebSocket('ws/patient/', handleWebSocketMessage);

  // --- Data Fetching (Caching Scaffolding) ---
  const { data: visitHistory, isLoading: isLoadingHistory } = useDataFetch<VisitData[]>('/patient/history/', {
    fallbackData: [
      { service: t.patient?.serviceInjection ?? 'Injection',   nurse: 'Sara Ahmed',   date: '18 Feb 2026', price: 165, status: 'completed' as const, rating: 5 },
      { service: t.patient?.serviceWoundCare ?? 'Wound Care',  nurse: 'Mona Ali',     date: '14 Feb 2026', price: 220, status: 'rated' as const,     rating: 4 },
      { service: t.patient?.serviceVitals ?? 'Vitals Check',   nurse: 'Amira Khaled', date: '10 Feb 2026', price: 100, status: 'completed' as const, rating: 5 },
      { service: t.patient?.serviceIVDrip ?? 'IV Drip',        nurse: 'Fatma Hassan', date: '5 Feb 2026',  price: 275, status: 'cancelled' as const, rating: 0 },
      { service: t.patient?.servicePhysio ?? 'Physiotherapy',  nurse: 'Nour Ibrahim', date: '1 Feb 2026',  price: 310, status: 'rated' as const,     rating: 5 },
    ]
  });

  useEffect(() => setMounted(true), []);
  if (!mounted) return null;

  // --- Services Data ---
  const services = [
    { svg: CannulaFluidsSVG,       name: isRTL ? 'تركيب الكانيولا والمحاليل' : 'Cannula & IV Fluids', color: THEME.green, id: 'iv-drip' },
    { svg: IronIV_SVG,       name: isRTL ? 'محاليل الحديد (إشراف طبي)' : 'Iron IV (Medical Supervision)', color: THEME.teal, id: 'iron-iv' },
    { svg: CatheterFeedingSVG,    name: isRTL ? 'تركيب القساطر وأنابيب التغذية' : 'Catheters & Feeding Tubes', color: THEME.orange, id: 'catheters-feeding' },
    { svg: BloodSamplingSVG,        name: isRTL ? 'سحب عينات الدم بالمنزل' : 'Home Blood Sampling', color: THEME.red, id: 'blood-sampling' },
    { svg: InjectionsSVG,        name: isRTL ? 'الحقن واختبار الحساسية' : 'Injections & Allergy Tests', color: THEME.teal, id: 'injections' },
    { svg: VitalsMonitorSVG,          name: isRTL ? 'قياس نسبة السكر والضغط' : 'Blood Sugar & Pressure', color: THEME.red, id: 'vitals-check' },
    { svg: WoundCareSVG, name: isRTL ? 'العناية بالجروح والقدم السكري' : 'Wound Care & Diabetic Foot', color: THEME.orange, id: 'wound-care' },
    { svg: StitchRemovalSVG,       name: isRTL ? 'متابعة ما بعد الجراحة وفك الغرز' : 'Post-Surgery & Stitch Removal', color: THEME.teal, id: 'post-surgery' },
    { svg: OxygenMeasurementSVG,       name: isRTL ? 'قياس نسبة الأكسجين بالمنزل' : 'Home Oxygen Measurement', color: THEME.green, id: 'oxygen-measurement' },
  ];


  const statusConfig = {
    completed: { label: t.patient?.visitCompleted ?? 'Completed', icon: CheckCircle2, color: 'text-[#79B253]', bg: 'bg-[#79B253]/10 border-[#79B253]/20' },
    cancelled: { label: t.patient?.visitCancelled ?? 'Cancelled', icon: X,            color: 'text-red-400',   bg: 'bg-red-500/10 border-red-500/20'   },
    rated:     { label: t.patient?.visitRated ?? 'Rated',         icon: Star,         color: 'text-[#FD8839]', bg: 'bg-[#FD8839]/10 border-[#FD8839]/20' },
  };

  return (
    <div
      className={`relative min-h-[calc(100vh-4rem)] bg-slate-950 text-slate-50 pb-24 ${isRTL ? 'font-arabic' : 'font-sans'}`}
      dir={isRTL ? 'rtl' : 'ltr'}
    >
      {/* ── Hero Shader ── */}
      <HeroSection
        title={t.patient?.heroTitle ?? 'مرحباً بك،'}
        highlightText={t.patient?.heroHighlight ?? 'أحمد'}
        description={t.patient?.heroDesc ?? 'رعاية صحية متكاملة — بين يديك.'}
        colors={['#16615F', '#79B253', '#F32D17', '#FD8839', '#114D4C', '#5C8B3E']}
        buttonText={t.patient?.requestNurse ?? 'Request Nurse'}
        onButtonClick={() => window.location.href = '/patient/direct-request'}
      />

      {/* ── Main Content ── */}
      <main id="main-content" className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-10">
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          animate="show"
          className="space-y-10"
        >

          {/* ── Floating Health Orbs ── */}
          <motion.div variants={slideUp} className="flex justify-center gap-4 sm:gap-8 lg:gap-12 flex-wrap">
            <HealthOrb
              icon={Heart}
              value="72"
              unit="BPM"
              label={t.patient?.vitalsSync ?? 'النبض'}
              colorRgb={THEME.red}
              delay={0}
            />
            <HealthOrb
              icon={Droplets}
              value="98"
              unit="%"
              label="SpO2"
              colorRgb={THEME.teal}
              delay={0.2}
            />
            <HealthOrb
              icon={Activity}
              value="120/80"
              unit=""
              label={t.patient?.activeBooking ?? 'الضغط'}
              colorRgb={THEME.green}
              delay={0.4}
            />
          </motion.div>

          {/* ── Services Grid ── */}
          <motion.div variants={slideUp}>
            <h2 className="text-lg font-bold text-slate-300 mb-4 flex items-center gap-2">
              <span className="w-1.5 h-5 rounded-full bg-[#16615F]" />
              {t.patient?.servicesTitle ?? 'Available Services'}
            </h2>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              {services.map((svc, i) => {
                const SvgComponent = svc.svg;
                return (
                  <Link href={`/patient/service/${svc.id}`} key={svc.id}>
                    <motion.div
                      whileHover={{ scale: 1.03, y: -3 }}
                      whileTap={{ scale: 0.97 }}
                      className="relative group overflow-hidden rounded-2xl border border-white/10 cursor-pointer p-5 flex flex-col items-center text-center gap-3 transition-colors hover:border-white/20 h-full"
                      style={{ background: `linear-gradient(160deg, rgba(${svc.color}, 0.12) 0%, rgba(11,17,32,0.85) 100%)` }}
                    >
                      <div className={`w-16 h-16 md:w-20 md:h-20 rounded-xl bg-slate-800/50 border flex items-center justify-center relative overflow-hidden group-hover:shadow-[0_0_30px_rgba(0,0,0,0)] transition-all duration-500`} style={{ borderColor: `rgba(${svc.color}, 0.3)`, boxShadow: `0 0 10px rgba(${svc.color}, 0.1)`}}>
                        <div className={`absolute inset-0 opacity-10`} style={{ background: `linear-gradient(to bottom right, rgb(${svc.color}), transparent)` }} />
                        <HolographicPulse />
                        <div className="w-12 h-12 md:w-16 md:h-16 relative z-10 p-1">
                          <SvgComponent />
                        </div>
                      </div>
                      <div className="flex-1 flex flex-col justify-center">
                        <p className="font-bold text-white text-sm">{svc.name}</p>
                      </div>
                      {/* Hover glow  */}
                      <div
                        className="absolute -bottom-6 left-1/2 -translate-x-1/2 w-24 h-24 rounded-full blur-2xl opacity-0 group-hover:opacity-40 transition-opacity duration-500 pointer-events-none"
                        style={{ background: `rgb(${svc.color})` }}
                      />
                    </motion.div>
                  </Link>
                );
              })}
            </div>
          </motion.div>

          {/* ── Quick Actions Row ── */}
          <motion.div variants={slideUp} className="grid grid-cols-1 gap-3">

            {/* Emergency SOS */}
            <div
              className="relative group overflow-hidden rounded-2xl border border-red-500/20 cursor-pointer"
              style={{ background: `linear-gradient(135deg, rgba(${THEME.red}, 0.15) 0%, rgba(11,17,32,0.9) 100%)` }}
            >
              <div className="p-5 relative z-10 flex items-center gap-4">
                <div className="w-10 h-10 rounded-full flex items-center justify-center bg-[#F32D17]/15 border border-[#F32D17]/30 shrink-0">
                  <AlertTriangle className="w-5 h-5 animate-pulse" style={{ color: `rgb(${THEME.red})` }} />
                </div>
                <div className="flex-1">
                  <h3 className="text-base font-bold text-white">{t.common?.emergency ?? 'SOS Emergency'}</h3>
                  <p className="text-xs text-slate-400">{t.patient?.emergencySupport ?? 'Rapid response 24/7'}</p>
                </div>
                {isRTL ? <ChevronLeft className="w-4 h-4 text-slate-500" /> : <ChevronRight className="w-4 h-4 text-slate-500" />}
              </div>
              <div className="absolute top-0 right-0 w-24 h-24 bg-[#F32D17]/10 blur-2xl rounded-full pointer-events-none" />
            </div>
          </motion.div>

          {/* ── Active Booking Tracker (or Empty State) ── */}
          <motion.div variants={slideUp}>
            {hasActiveBooking ? (
              <Link href="/patient/simulator" className="block">
                <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 relative overflow-hidden hover:bg-slate-800/60 transition-colors cursor-pointer group">
                  <div className="absolute top-0 left-0 w-1 h-full rounded-l-2xl group-hover:w-2 transition-all duration-300" style={{ backgroundColor: `rgb(${THEME.green})` }} />
                  <div className="flex flex-col md:flex-row items-center justify-between gap-6 ps-2">
                    <div className="flex items-center gap-4 w-full md:w-auto">
                      <div className="relative shrink-0">
                        <div className="w-14 h-14 rounded-xl bg-slate-800 p-1 border border-slate-700">
                          <Image src="https://i.pravatar.cc/150?img=33" alt="Nurse" width={56} height={56} className="rounded-lg object-cover" />
                        </div>
                      <div className="absolute -bottom-1 -end-1 w-4 h-4 rounded-full border-2 border-slate-900 bg-[#79B253]">
                        <motion.div animate={{ scale: [1,1.8,1], opacity: [1,0,1] }} transition={{ duration: 2, repeat: Infinity }} className="w-full h-full bg-[#79B253] rounded-full" />
                      </div>
                    </div>
                    <div>
                      <p className="text-xs font-semibold mb-1" style={{ color: `rgb(${THEME.green})` }}>{t.patient?.nurseOnTheWay ?? 'Nurse on the way'}</p>
                      <h3 className="text-base font-bold text-white">{activeVisitData?.nurse?.name || (t.patient?.nurseName ?? 'Amira Khaled')}</h3>
                      <p className="text-xs text-slate-400">{activeVisitData?.visit?.service_type || (t.patient?.nurseSpecialty ?? 'Wound Care • 4.9 ⭐')}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-5 text-center">
                    <div>
                      <p className="text-[10px] text-slate-400 mb-1">{t.patient?.eta ?? 'ETA'}</p>
                      <p className="text-lg font-bold text-white">12 min</p>
                    </div>
                    <div className="h-8 w-px bg-slate-700" />
                    <div>
                      <p className="text-[10px] text-slate-400 mb-1">{t.patient?.distance ?? 'Distance'}</p>
                      <p className="text-lg font-bold text-white">3.2 km</p>
                    </div>
                    <div className="hidden sm:flex items-center justify-center w-10 h-10 rounded-full border border-slate-700 bg-slate-800 group-hover:bg-slate-700 transition-colors">
                      <MapPin className="w-4 h-4 text-white" />
                    </div>
                  </div>
                </div>
              </div>
              </Link>
            ) : (
              /* Empty State */
              <div className="bg-slate-900/30 backdrop-blur-sm border border-dashed border-slate-700 rounded-2xl p-8 flex flex-col items-center justify-center text-center">
                <div className="w-16 h-16 rounded-full bg-slate-800/80 border border-slate-700 flex items-center justify-center mb-4">
                  <CalendarCheck className="w-7 h-7 text-slate-500" />
                </div>
                <h3 className="text-base font-bold text-slate-300 mb-1">{t.patient?.noActiveBooking ?? 'No Active Bookings'}</h3>
                <p className="text-sm text-slate-500 max-w-xs">{t.patient?.noActiveBookingDesc ?? 'When you request a nurse, live tracking will appear here.'}</p>
              </div>
            )}
          </motion.div>

          {/* ── Visit History ── */}
          <motion.div variants={slideUp} className="pt-2">
            <h2 className="text-lg font-bold text-slate-300 mb-4 flex items-center gap-2">
              <span className="w-1.5 h-5 rounded-full bg-[#FD8839]" />
              {t.patient?.visitHistory ?? 'Visit History'}
              {isLoadingHistory && <Activity className="w-4 h-4 ml-2 animate-spin text-slate-500" />}
            </h2>
            <div className="space-y-3">
              {(visitHistory || []).map((visit, idx) => {
                const cfg = statusConfig[visit.status];
                const StatusIcon = cfg.icon;
                return (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, y: 12 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.06 }}
                    className="flex items-center justify-between p-4 rounded-xl bg-slate-900/40 border border-slate-800 hover:border-slate-700 transition-colors group cursor-pointer"
                  >
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 rounded-full bg-slate-800 flex items-center justify-center text-slate-400 group-hover:bg-[#16615F]/15 group-hover:text-[#16615F] transition-colors shrink-0">
                        <Activity className="w-4 h-4" />
                      </div>
                      <div>
                        <h4 className="font-bold text-sm text-slate-200">{visit.service}</h4>
                        <p className="text-xs text-slate-500 flex items-center gap-2 mt-0.5">
                          <span>{visit.nurse}</span>
                          <span className="text-slate-700">•</span>
                          <span className="flex items-center gap-1"><Clock className="w-3 h-3" />{visit.date}</span>
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-sm font-bold text-white hidden sm:block">{visit.price} EGP</span>
                      <span className={`inline-flex items-center gap-1 text-[11px] font-bold px-2.5 py-1 rounded-full border ${cfg.bg} ${cfg.color}`}>
                        <StatusIcon className="w-3 h-3" />
                        {cfg.label}
                      </span>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </motion.div>

        </motion.div>
      </main>
    </div>
  );
}
