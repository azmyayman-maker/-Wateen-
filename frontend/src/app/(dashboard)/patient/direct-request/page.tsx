'use client';

import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence, useAnimation, useMotionValue, useTransform } from 'framer-motion';
import { useLanguage } from '@/lib/i18n';
import Link from 'next/link';
import { 
  ArrowRight, 
  ArrowLeft,
  MapPin, 
  Search, 
  Syringe, 
  Stethoscope, 
  Activity, 
  HeartPulse, 
  Baby, 
  Thermometer,
  Pill,
  Scissors,
  Wind,
  Droplets,
  Clock,
  ShieldCheck,
  Check,
  ChevronUp,
  Sparkles,
  UserCircle2,
  Star,
  Navigation
} from 'lucide-react';
import LocationPicker from '@/components/shared/map/LocationPicker';

// ─── Color constants ───
const C = {
  blue: { bg: 'rgba(59,130,246,0.15)', border: 'rgba(59,130,246,0.6)', text: '#60a5fa', glow: 'rgba(59,130,246,0.3)' },
  emerald: { bg: 'rgba(16,185,129,0.15)', border: 'rgba(16,185,129,0.6)', text: '#34d399', glow: 'rgba(16,185,129,0.3)' },
  orange: { bg: 'rgba(249,115,22,0.15)', border: 'rgba(249,115,22,0.6)', text: '#fb923c', glow: 'rgba(249,115,22,0.3)' },
  teal: { bg: 'rgba(20,184,166,0.15)', border: 'rgba(20,184,166,0.6)', text: '#2dd4bf', glow: 'rgba(20,184,166,0.3)' },
  cyan: { bg: 'rgba(6,182,212,0.15)', border: 'rgba(6,182,212,0.6)', text: '#22d3ee', glow: 'rgba(6,182,212,0.3)' },
  red: { bg: 'rgba(239,68,68,0.15)', border: 'rgba(239,68,68,0.6)', text: '#f87171', glow: 'rgba(239,68,68,0.3)' },
};

type ColorKey = keyof typeof C;

// Quick Tag data
const QUICK_TAGS: { id: string; icon: any; labelEn: string; labelAr: string; color: ColorKey }[] = [
  { id: 'iv-drip',       icon: Syringe,      labelEn: 'IV Drip',       labelAr: 'محلول وريدي',     color: 'blue' },
  { id: 'vitals-check',  icon: Activity,     labelEn: 'Vitals Check',  labelAr: 'قياس حيويات',     color: 'emerald' },
  { id: 'wound-care',    icon: HeartPulse,   labelEn: 'Wound Care',    labelAr: 'عناية بالجروح',   color: 'orange' },
  { id: 'post-surgery',  icon: Stethoscope,  labelEn: 'Post-Surgery',  labelAr: 'ما بعد الجراحة',  color: 'teal' },
  { id: 'blood-sampling',icon: Droplets,     labelEn: 'Blood Test',    labelAr: 'تحليل دم',        color: 'red' },
  { id: 'oxygen',        icon: Wind,         labelEn: 'Oxygen',        labelAr: 'أكسجين',          color: 'cyan' },
];

// All services for expanded view
const ALL_SERVICES: { id: string; icon: any; nameEn: string; nameAr: string; descEn: string; descAr: string; price: number; color: ColorKey }[] = [
  { id: 'iv-drip',          icon: Syringe,    nameEn: 'Cannula & IV Fluids',      nameAr: 'تركيب الكانيولا والمحاليل',        descEn: 'Saline, glucose & medication drips',   descAr: 'محلول ملحي، جلوكوز وأدوية وريدية', price: 250, color: 'blue' },
  { id: 'iron-iv',          icon: Pill,       nameEn: 'Iron IV Therapy',           nameAr: 'محاليل الحديد بالإشراف الطبي',      descEn: 'Supervised iron infusion at home',     descAr: 'حقن حديد تحت إشراف طبي بالمنزل',   price: 350, color: 'teal' },
  { id: 'blood-sampling',   icon: Droplets,   nameEn: 'Home Blood Sampling',       nameAr: 'سحب عينات الدم بالمنزل',           descEn: 'CBC, lipids, sugar & more',            descAr: 'صورة دم، دهون، سكر والمزيد',       price: 150, color: 'red' },
  { id: 'injections',       icon: Syringe,    nameEn: 'Injections & Allergy Tests',nameAr: 'الحقن واختبار الحساسية',            descEn: 'IM, IV, SC injections',                descAr: 'حقن عضل، وريد، تحت الجلد',         price: 120, color: 'emerald' },
  { id: 'vitals-check',     icon: Activity,   nameEn: 'Vitals Monitoring',         nameAr: 'قياس المؤشرات الحيوية',             descEn: 'BP, sugar, SpO2, temperature',         descAr: 'ضغط، سكر، أكسجين، حرارة',          price: 100, color: 'emerald' },
  { id: 'wound-care',       icon: HeartPulse, nameEn: 'Wound & Diabetic Foot Care',nameAr: 'العناية بالجروح والقدم السكري',     descEn: 'Professional wound dressing',          descAr: 'تضميد جروح احترافي',                price: 200, color: 'orange' },
  { id: 'post-surgery',     icon: Scissors,   nameEn: 'Post-Surgery & Stitches',   nameAr: 'متابعة ما بعد الجراحة وفك الغرز',  descEn: 'Stitch removal & post-op care',        descAr: 'فك غرز ومتابعة ما بعد العملية',     price: 180, color: 'teal' },
  { id: 'oxygen',           icon: Wind,       nameEn: 'Oxygen Measurement',        nameAr: 'قياس نسبة الأكسجين بالمنزل',       descEn: 'SpO2 monitoring with pulse oximeter',  descAr: 'قياس الأكسجين بجهاز النبض',         price: 80,  color: 'cyan' },
  { id: 'catheter',         icon: Stethoscope,nameEn: 'Catheter & Feeding Tubes',  nameAr: 'تركيب القساطر وأنابيب التغذية',    descEn: 'Urinary & NG tube insertion',          descAr: 'تركيب قسطرة بولية وأنبوب تغذية',   price: 280, color: 'blue' },
];

// Simulated nearby nurses
const NURSE_PINS = [
  { top: '22%', left: '30%', size: 'w-11 h-11', name: 'Amira', rating: 4.9, delay: 0 },
  { top: '45%', left: '65%', size: 'w-9 h-9',   name: 'ElSaeed', rating: 4.8, delay: 0.5 },
  { top: '35%', left: '55%', size: 'w-8 h-8',   name: 'Fatma', rating: 5.0, delay: 1.0 },
  { top: '55%', left: '22%', size: 'w-7 h-7',   name: 'Nour', rating: 4.7, delay: 1.5 },
];

export default function DirectRequestPage() {
  const { t, isRTL, dir } = useLanguage();
  
  const [sheetState, setSheetState] = useState<'collapsed' | 'expanded'>('collapsed');
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [requestConfirmed, setRequestConfirmed] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => setMounted(true), []);

  // Swipe-to-request motion
  const dragX = useMotionValue(0);
  const swipeProgress = useTransform(dragX, [0, 250], [0, 1]);
  const swipeBgOpacity = useTransform(swipeProgress, [0, 1], [0, 1]);

  useEffect(() => {
    const unsubscribe = dragX.on('change', (latest) => {
      if (latest > 235 && !requestConfirmed) {
        setRequestConfirmed(true);
        setTimeout(() => {
          window.location.href = '/patient/simulator';
        }, 1800);
      }
    });
    return unsubscribe;
  }, [dragX, requestConfirmed]);

  // Bottom sheet controls
  const sheetControls = useAnimation();
  const handleSheetDragEnd = (_: any, info: any) => {
    if (info.offset.y < -60) setSheetState('expanded');
    else if (info.offset.y > 60) setSheetState('collapsed');
  };

  useEffect(() => {
    if (!mounted) return;
    if (sheetState === 'expanded') {
      sheetControls.start({ y: 0, transition: { type: 'spring', damping: 30, stiffness: 250 } });
    } else {
      sheetControls.start({ y: 'calc(100dvh - 400px)', transition: { type: 'spring', damping: 30, stiffness: 250 } });
    }
  }, [sheetState, sheetControls, mounted]);

  // Toggle tag selection (multi-select)
  const toggleTag = useCallback((id: string) => {
    setSelectedTags(prev => prev.includes(id) ? prev.filter(t => t !== id) : [...prev, id]);
  }, []);

  // Filter services
  const filteredServices = ALL_SERVICES.filter(s => {
    const q = searchQuery.toLowerCase();
    if (q && !s.nameEn.toLowerCase().includes(q) && !s.nameAr.includes(searchQuery)) return false;
    return true;
  });

  if (!mounted) return null;

  return (
    <div className={`relative h-[100dvh] w-full bg-slate-950 overflow-hidden text-slate-50 select-none ${isRTL ? 'font-arabic' : 'font-sans'}`} dir={dir}>
      
      {/* ── Full-Screen Dark Map ── */}
      <div className="absolute inset-0 z-0">
         <LocationPicker readOnly initialLocation={[30.0444, 31.2357]} className="w-full h-full opacity-60" />
         
         {/* Atmospheric gradient overlays */}
         <div className="absolute inset-0 bg-gradient-to-b from-slate-950/90 via-slate-950/30 to-slate-950/95 pointer-events-none" />
         <div className="absolute inset-0 bg-gradient-to-r from-slate-950/40 via-transparent to-slate-950/40 pointer-events-none" />
          
         {/* Simulated Nurse Pins */}
         {NURSE_PINS.map((nurse, i) => (
           <motion.div
             key={i}
             initial={{ scale: 0, opacity: 0 }}
             animate={{ scale: 1, opacity: 1 }}
             transition={{ delay: 0.5 + nurse.delay, type: 'spring', stiffness: 200 }}
             className={`absolute ${nurse.size} z-10`}
             style={{ top: nurse.top, left: nurse.left }}
           >
             {/* Ping ring */}
             <div className="absolute inset-0 rounded-full bg-emerald-500/20 animate-ping" />
             {/* Inner dot */}
             <div className="relative w-full h-full rounded-full bg-emerald-500/30 border-2 border-emerald-400 flex items-center justify-center shadow-[0_0_25px_rgba(16,185,129,0.5)] backdrop-blur-sm">
               <UserCircle2 className="w-4 h-4 text-emerald-200" />
             </div>
           </motion.div>
         ))}

         {/* Your Location Pin */}
         <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-10">
            <div className="relative flex items-center justify-center">
               <div className="absolute w-20 h-20 rounded-full bg-blue-500/10 animate-pulse" />
               <div className="absolute w-12 h-12 rounded-full bg-blue-500/20 animate-ping" />
               <div className="w-6 h-6 rounded-full bg-blue-500 border-4 border-white shadow-[0_0_30px_rgba(59,130,246,0.6)] relative z-10" />
            </div>
         </div>
      </div>

      {/* ── Top Bar ── */}
      <div className="absolute top-0 left-0 w-full p-4 sm:p-6 z-40 flex justify-between items-start pointer-events-none">
         {/* Back Button */}
         <Link href="/patient" className="pointer-events-auto flex items-center justify-center w-12 h-12 rounded-2xl bg-slate-900/70 border border-white/10 backdrop-blur-xl hover:bg-slate-800 transition-all shadow-2xl active:scale-95">
           {isRTL ? <ArrowRight className="w-5 h-5" /> : <ArrowLeft className="w-5 h-5" />}
         </Link>

         {/* ETA Badge */}
         <motion.div 
           initial={{ y: -30, opacity: 0 }}
           animate={{ y: 0, opacity: 1 }}
           transition={{ delay: 0.3, type: 'spring' }}
           className="pointer-events-auto px-5 py-2.5 rounded-2xl bg-slate-900/70 border border-emerald-500/30 backdrop-blur-xl flex items-center gap-2.5 shadow-2xl"
         >
            <div className="relative">
              <div className="w-2.5 h-2.5 rounded-full bg-emerald-400" />
              <div className="absolute inset-0 w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping" />
            </div>
            <span className="text-sm font-bold text-emerald-100">{isRTL ? 'أقرب ممرض: 8 دقائق' : 'Nearest Nurse: 8 min'}</span>
         </motion.div>
      </div>


      {/* ── Bottom Sheet ── */}
      <motion.div 
        drag="y"
        dragConstraints={{ top: 0, bottom: 0 }}
        dragElastic={0.15}
        onDragEnd={handleSheetDragEnd}
        animate={sheetControls}
        initial={{ y: 'calc(100dvh - 400px)' }}
        className="absolute left-0 w-full h-[92dvh] z-30 flex flex-col will-change-transform"
        style={{ touchAction: 'none' }}
      >
        {/* Glass Panel */}
        <div className="flex-1 bg-slate-900/85 backdrop-blur-3xl border-t border-white/10 rounded-t-[2rem] shadow-[0_-15px_60px_rgba(0,0,0,0.6)] flex flex-col overflow-hidden">
          
          {/* Drag Handle */}
          <div 
            className="w-full flex flex-col items-center pt-3 pb-1 cursor-grab active:cursor-grabbing"
            onClick={() => setSheetState(s => s === 'collapsed' ? 'expanded' : 'collapsed')}
          >
            <div className="w-10 h-1 rounded-full bg-slate-500/60 mb-1" />
            <ChevronUp className={`w-4 h-4 text-slate-500 transition-transform duration-300 ${sheetState === 'expanded' ? 'rotate-180' : ''}`} />
          </div>

          {/* Scrollable Content */}
          <div className="flex-1 overflow-y-auto px-5 sm:px-6 pb-32 overscroll-contain">
            
            {/* Heading */}
            <div className="mb-5 mt-1">
               <h1 className="text-2xl font-black text-white mb-1">
                 {isRTL ? 'ماذا تحتاج اليوم؟' : 'What do you need today?'}
               </h1>
               <p className="text-slate-400 text-sm flex items-center gap-1.5">
                 <Navigation className="w-3.5 h-3.5 text-blue-400" /> 
                 {isRTL ? 'التوصيل إلى موقعك الحالي' : 'Delivering to your current location'}
               </p>
            </div>

            {/* Search */}
            <div className="relative mb-6">
               <div className="absolute inset-y-0 start-0 ps-4 flex items-center pointer-events-none">
                  <Search className="w-5 h-5 text-slate-500" />
               </div>
               <input 
                 type="text" 
                 placeholder={isRTL ? 'ابحث عن خدمة أو اكتب الأعراض...' : 'Search a service or describe symptoms...'}
                 value={searchQuery}
                 onChange={(e) => setSearchQuery(e.target.value)}
                 className="w-full bg-slate-800/60 border border-white/5 focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/30 rounded-2xl py-3.5 ps-12 pe-4 text-white placeholder-slate-500 outline-none transition-all text-sm"
               />
            </div>

            {/* Quick Tags (Horizontal Pills) */}
            <div className="mb-6">
               <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3 px-0.5">
                 {isRTL ? 'اختيار سريع' : 'Quick Select'}
               </h2>
               <div className="flex overflow-x-auto gap-2.5 pb-3 scrollbar-hide -mx-5 px-5 sm:mx-0 sm:px-0">
                 {QUICK_TAGS.map((tag) => {
                   const isSelected = selectedTags.includes(tag.id);
                   const Icon = tag.icon;
                   const palette = C[tag.color];
                   return (
                     <motion.button
                       key={tag.id}
                       whileTap={{ scale: 0.92 }}
                       onClick={() => toggleTag(tag.id)}
                       className="shrink-0 flex flex-col items-center justify-center rounded-2xl border transition-all duration-300 w-[5.5rem] h-[5.5rem] gap-1.5 relative overflow-hidden"
                       style={{
                         background: isSelected ? palette.bg : 'rgba(30,41,59,0.5)',
                         borderColor: isSelected ? palette.border : 'rgba(255,255,255,0.05)',
                         boxShadow: isSelected ? `0 0 20px ${palette.glow}` : 'none'
                       }}
                     >
                       {isSelected && (
                         <motion.div 
                           layoutId="tag-check"
                           className="absolute top-1.5 end-1.5 w-4 h-4 rounded-full flex items-center justify-center"
                           style={{ background: palette.border }}
                         >
                           <Check className="w-2.5 h-2.5 text-white" />
                         </motion.div>
                       )}
                       <Icon className="w-7 h-7" style={{ color: isSelected ? palette.text : '#94a3b8' }} />
                       <span className="text-[10px] font-semibold text-center leading-tight" style={{ color: isSelected ? '#fff' : '#94a3b8' }}>
                         {isRTL ? tag.labelAr : tag.labelEn}
                       </span>
                     </motion.button>
                   );
                 })}
               </div>
            </div>

            {/* Services List (always visible, more when expanded) */}
            <div>
               <div className="flex items-center justify-between mb-3 px-0.5">
                 <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                   {isRTL ? 'جميع الخدمات' : 'All Services'}
                 </h2>
                 <span className="text-xs text-slate-500">{filteredServices.length} {isRTL ? 'خدمة' : 'services'}</span>
               </div>
               
               <div className="space-y-2.5">
                 {filteredServices.slice(0, sheetState === 'expanded' ? filteredServices.length : 3).map((svc) => {
                   const palette = C[svc.color];
                   const Icon = svc.icon;
                   const isActive = selectedTags.includes(svc.id);
                   return (
                     <motion.button
                       key={svc.id}
                       whileTap={{ scale: 0.98 }}
                       onClick={() => toggleTag(svc.id)}
                       className="w-full flex items-center gap-4 p-4 rounded-2xl border transition-all duration-200 text-start"
                       style={{
                         background: isActive ? palette.bg : 'rgba(30,41,59,0.3)',
                         borderColor: isActive ? palette.border : 'rgba(255,255,255,0.04)',
                       }}
                     >
                       <div 
                         className="w-12 h-12 rounded-xl flex items-center justify-center shrink-0"
                         style={{ background: `${palette.bg}`, border: `1px solid ${palette.border}` }}
                       >
                         <Icon className="w-5 h-5" style={{ color: palette.text }} />
                       </div>
                       <div className="flex-1 min-w-0">
                         <p className="font-bold text-white text-sm truncate">{isRTL ? svc.nameAr : svc.nameEn}</p>
                         <p className="text-xs text-slate-400 truncate">{isRTL ? svc.descAr : svc.descEn}</p>
                       </div>
                       <div className="flex flex-col items-end gap-1 shrink-0">
                         <span className="text-sm font-bold" style={{ color: palette.text }}>
                           {svc.price} {isRTL ? 'ج.م' : 'EGP'}
                         </span>
                         {isActive && (
                           <motion.div 
                             initial={{ scale: 0 }} 
                             animate={{ scale: 1 }}
                             className="w-5 h-5 rounded-full flex items-center justify-center"
                             style={{ background: palette.border }}
                           >
                             <Check className="w-3 h-3 text-white" />
                           </motion.div>
                         )}
                       </div>
                     </motion.button>
                   );
                 })}

                 {/* Show more hint when collapsed */}
                 {sheetState === 'collapsed' && filteredServices.length > 3 && (
                   <button 
                     onClick={() => setSheetState('expanded')}
                     className="w-full py-3 text-center text-sm text-blue-400 font-medium hover:text-blue-300 transition-colors"
                   >
                     {isRTL ? `عرض ${filteredServices.length - 3} خدمة أخرى ↑` : `Show ${filteredServices.length - 3} more services ↑`}
                   </button>
                 )}
               </div>
            </div>

            {/* Selection Summary */}
            <AnimatePresence>
              {selectedTags.length > 0 && (
                <motion.div 
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 10 }}
                  className="mt-6 p-4 rounded-2xl bg-slate-800/50 border border-white/5"
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider">
                      {isRTL ? 'ملخص الطلب' : 'Request Summary'}
                    </span>
                    <span className="text-xs font-bold text-emerald-400">
                      {selectedTags.length} {isRTL ? 'خدمة' : selectedTags.length === 1 ? 'service' : 'services'}
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {selectedTags.map(id => {
                      const svc = ALL_SERVICES.find(s => s.id === id) || QUICK_TAGS.find(t => t.id === id);
                      if (!svc) return null;
                      const palette = C[svc.color];
                      return (
                        <span 
                          key={id}
                          className="text-xs px-3 py-1.5 rounded-full font-medium border"
                          style={{ background: palette.bg, borderColor: palette.border, color: palette.text }}
                        >
                          {isRTL ? ('nameAr' in svc ? svc.nameAr : svc.labelAr) : ('nameEn' in svc ? svc.nameEn : svc.labelEn)}
                        </span>
                      );
                    })}
                  </div>
                  <div className="flex items-center justify-between mt-3 pt-3 border-t border-white/5">
                    <span className="text-slate-400 text-sm">{isRTL ? 'التكلفة التقديرية' : 'Estimated Total'}</span>
                    <span className="text-lg font-black text-white">
                      {ALL_SERVICES.filter(s => selectedTags.includes(s.id)).reduce((sum, s) => sum + s.price, 0)} {isRTL ? 'ج.م' : 'EGP'}
                    </span>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* ── Swipe-to-Request Button ── */}
          <div className="absolute bottom-0 left-0 w-full p-5 pb-8 bg-gradient-to-t from-slate-900 via-slate-900/95 to-transparent z-50">
            
            {/* Disabled state overlay */}
            {selectedTags.length === 0 && !requestConfirmed && (
              <div className="text-center mb-3">
                <p className="text-slate-500 text-xs font-medium">
                  {isRTL ? 'اختر خدمة واحدة على الأقل للمتابعة' : 'Select at least one service to continue'}
                </p>
              </div>
            )}

            <div className={`relative h-[60px] w-full max-w-sm mx-auto rounded-full overflow-hidden border shadow-2xl transition-opacity duration-300 ${
              selectedTags.length === 0 && !requestConfirmed 
                ? 'opacity-40 pointer-events-none border-white/5' 
                : 'border-white/10'
            }`}>
              
              {/* Emerald fill from swipe */}
              <motion.div 
                 className="absolute inset-y-0 left-0 w-full origin-left bg-emerald-500 rounded-full"
                 style={{ scaleX: swipeProgress, opacity: swipeBgOpacity }}
              />
              
              {/* Base background */}
              <div className="absolute inset-0 bg-slate-800/90 backdrop-blur-xl rounded-full -z-10" />

              {/* Instruction text */}
              <AnimatePresence mode="wait">
                 {!requestConfirmed ? (
                   <motion.div 
                     key="swipe-hint"
                     exit={{ opacity: 0, scale: 0.9 }}
                     className="absolute inset-0 flex items-center justify-center pointer-events-none z-10 gap-2"
                   >
                     <span className="text-white/50 font-bold text-sm tracking-wide ps-14">
                       {isRTL ? '← اسحب لطلب الممرض' : 'Swipe to Request →'}
                     </span>
                   </motion.div>
                 ) : (
                   <motion.div 
                     key="confirmed"
                     initial={{ opacity: 0, scale: 0.8 }}
                     animate={{ opacity: 1, scale: 1 }}
                     className="absolute inset-0 flex items-center justify-center pointer-events-none z-10 bg-emerald-500 rounded-full"
                   >
                     <span className="text-white font-black text-base flex items-center gap-2">
                       <ShieldCheck className="w-5 h-5" />
                       {isRTL ? '! جاري البث للممرضين' : 'Broadcasting to Nurses!'}
                     </span>
                   </motion.div>
                 )}
              </AnimatePresence>

              {/* Draggable Thumb */}
              {!requestConfirmed && (
                <motion.div
                  drag="x"
                  dragConstraints={{ left: 0, right: 250 }}
                  dragElastic={0}
                  dragMomentum={false}
                  style={{ x: dragX }}
                  whileTap={{ scale: 1.05 }}
                  className="absolute top-1 left-1 bottom-1 w-[52px] rounded-full bg-gradient-to-br from-blue-500 to-blue-600 shadow-[0_0_20px_rgba(59,130,246,0.5)] flex items-center justify-center z-20 cursor-grab active:cursor-grabbing border border-blue-400/50"
                >
                  <ArrowRight className="w-5 h-5 text-white" />
                </motion.div>
              )}
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
