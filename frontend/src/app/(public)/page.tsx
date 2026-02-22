"use client";


import React, { useRef, useState, useEffect, useCallback } from "react";
import {
  motion,
  useScroll,
  useTransform,
  useSpring,
  useMotionValue,
  type MotionValue,
} from "framer-motion";
import { LogIn, UserPlus, Activity, BrainCircuit, ShieldCheck, Calculator, ShieldAlert, HeartPulse, Database } from "lucide-react";
import { HealthWalletSection } from "@/components/landing/HealthWalletSection";
import { LiveECGMonitor } from "@/components/landing/LiveECGMonitor";

// --- 0. MOBILE DETECTION HOOK ---
function useIsMobile(breakpoint = 768) {
  const [isMobile, setIsMobile] = useState(false);
  useEffect(() => {
    const check = () => setIsMobile(window.innerWidth < breakpoint);
    check();
    window.addEventListener('resize', check, { passive: true });
    return () => window.removeEventListener('resize', check);
  }, [breakpoint]);
  return isMobile;
}

// --- 1. CONFIGURATION ---

export default function LandingPage() {
  const containerRef = useRef<HTMLDivElement>(null);
  const SECTION_COUNT = 5;
  
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end end"]
  });

  // Smooth infinite scroll loop
  useEffect(() => {
    let ticking = false;
    const handleScroll = () => {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(() => {
        const el = containerRef.current;
        if (!el) { ticking = false; return; }
        const scrollTop = window.scrollY;
        const maxScroll = el.scrollHeight - window.innerHeight;
        // Seamless loop at boundaries
        if (scrollTop >= maxScroll - 2) {
          window.scrollTo({ top: 2, behavior: 'instant' as ScrollBehavior });
        } else if (scrollTop <= 1) {
          window.scrollTo({ top: maxScroll - 3, behavior: 'instant' as ScrollBehavior });
        }
        ticking = false;
      });
    };
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <main dir="rtl" className="relative bg-[#020408] text-slate-50 overflow-clip">
      <div ref={containerRef} className="h-[600vh] relative">
        <Section3D index={0} scrollYProgress={scrollYProgress} total={SECTION_COUNT} id="hero">
          <HeroContent />
        </Section3D>
        <Section3D index={1} scrollYProgress={scrollYProgress} total={SECTION_COUNT} id="vitals">
          <IoTVitalsContent />
        </Section3D>
        <Section3D index={2} scrollYProgress={scrollYProgress} total={SECTION_COUNT} id="ai">
          <AICopilotContent />
        </Section3D>
        <Section3D index={3} scrollYProgress={scrollYProgress} total={SECTION_COUNT} id="health-wallet">
          <HealthWalletSection />
        </Section3D>
        <Section3D index={4} scrollYProgress={scrollYProgress} total={SECTION_COUNT} id="shield">
          <ShieldContent />
        </Section3D>
      </div>
      <TopNavbar />
    </main>
  );
}

function use3DTilt(ref: React.RefObject<HTMLElement>) {
  const mouseX = useMotionValue(0.5);
  const mouseY = useMotionValue(0.5);
  const rotateX = useSpring(useTransform(mouseY, [0, 1], [15, -15]), { stiffness: 100, damping: 20 });
  const rotateY = useSpring(useTransform(mouseX, [0, 1], [-15, 15]), { stiffness: 100, damping: 20 });

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (!ref.current) return;
    const rect = ref.current.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width;
    const y = (e.clientY - rect.top) / rect.height;
    mouseX.set(x);
    mouseY.set(y);
  }, [mouseX, mouseY, ref]);

  const handleMouseLeave = useCallback(() => {
    mouseX.set(0.5);
    mouseY.set(0.5);
  }, [mouseX, mouseY]);

  return { rotateX, rotateY, handleMouseMove, handleMouseLeave };
}

const Section3D = ({ children, index, scrollYProgress, total, id }: { children: React.ReactNode, index: number, scrollYProgress: MotionValue<number>, total: number, id: string }) => {
  const ref = useRef<HTMLDivElement>(null);
  const isMobile = useIsMobile();
  const { rotateX, rotateY, handleMouseMove, handleMouseLeave } = use3DTilt(ref);
  const current = index / total;
  const step = 1 / total;
  const smoothProgress = useSpring(scrollYProgress, { stiffness: 150, damping: 24, mass: 0.5 });
  // Softer 3D on mobile
  const sectionRotateX = useTransform(smoothProgress, [current - step, current, current + step], isMobile ? [20, 0, -20] : [75, 0, -75]);
  const sectionScale = useTransform(smoothProgress, [current - step, current, current + step], isMobile ? [0.85, 1, 0.85] : [0.4, 1, 0.4]);
  const sectionOpacity = useTransform(smoothProgress, [current - step * 0.8, current, current + step * 0.8], [0, 1, 0]);
  const zOffset = useTransform(smoothProgress, [current - step, current, current + step], isMobile ? [-400, 0, -400] : [-2000, 0, -2000]);
  
  const [isActive, setIsActive] = useState(index === 0);
  useEffect(() => {
    const unsub = smoothProgress.onChange((v) => setIsActive(Math.abs(v - current) < 0.12));
    return () => unsub();
  }, [smoothProgress, current]);

  return (
    <div id={id} className="h-screen w-full flex items-center justify-center fixed top-0 left-0 perspective-[2000px] md:perspective-[2000px] select-none overflow-hidden" style={{ pointerEvents: isActive ? 'auto' : 'none' }}>
      <motion.div 
        className="w-full h-full flex items-center justify-center p-1 md:p-4"
        style={{ rotateX: sectionRotateX, scale: sectionScale, opacity: sectionOpacity, z: zOffset, transformStyle: "preserve-3d" }}
      >
        <motion.div 
          ref={ref as React.RefObject<HTMLDivElement>}
          onMouseMove={isMobile ? undefined : handleMouseMove}
          onMouseLeave={isMobile ? undefined : handleMouseLeave}
          className={`relative w-full max-w-[100vw] md:max-w-[90vw] xl:max-w-[1200px] 2xl:max-w-[1400px] mx-auto min-h-[85vh] ${index === 0 ? 'md:h-[68vh]' : 'md:h-[80vh]'} flex flex-col md:flex-row items-center justify-center rounded-2xl md:rounded-[2.5rem]`}
          style={{ rotateX: isMobile ? 0 : rotateX, rotateY: isMobile ? 0 : rotateY, transformStyle: isMobile ? undefined : "preserve-3d" }}
        >
          {children}
        </motion.div>
      </motion.div>
    </div>
  );
};

const DomainReveal = () => {
  const text = "wateen.live";
  
  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.1, delayChildren: 1.5 }
    }
  };

  const item = {
    hidden: { opacity: 0, scale: 0.5, y: 10, filter: "blur(10px)" },
    show: { opacity: 1, scale: 1, y: 0, filter: "blur(0px)", transition: { type: "spring", stiffness: 300, damping: 20 } }
  };

  return (
    <motion.div 
      className="mt-6 md:mt-8 px-6 py-2.5 rounded-full bg-slate-900/60 backdrop-blur-xl border border-cyan-500/10 shadow-[0_0_40px_-10px_rgba(34,211,238,0.2)] z-20 flex items-center justify-center cursor-pointer hover:border-cyan-400/30 transition-colors group mx-auto w-fit"
      style={{ translateZ: 200 }}
      variants={container}
      initial="hidden"
      animate="show"
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
    >
      <div className="flex gap-[0.1em]" dir="ltr">
        {text.split("").map((char, index) => (
          <motion.span 
            key={index} 
            variants={item}
            className="text-lg md:text-2xl font-mono font-bold bg-gradient-to-r from-cyan-400 to-emerald-400 text-transparent bg-clip-text drop-shadow-[0_0_15px_rgba(34,211,238,0.8)]"
          >
            {char}
          </motion.span>
        ))}
      </div>
      <motion.div 
        className="absolute inset-0 rounded-full border border-cyan-400/0 group-hover:border-cyan-400/50"
        animate={{ boxShadow: ["0 0 0px rgba(34,211,238,0)", "0 0 20px rgba(34,211,238,0.4)", "0 0 0px rgba(34,211,238,0)"] }}
        transition={{ duration: 3, repeat: Infinity, ease: "easeInOut", delay: 2.5 }}
      />
    </motion.div>
  );
};

const HeroContent = () => (
  <div className="flex flex-col items-center justify-center w-full h-full relative" style={{ transformStyle: "preserve-3d" }}>
    
    {/* Dynamic Background Radial Breathing Mesh */}
    <div className="absolute inset-0 flex items-center justify-center pointer-events-none" style={{ transformStyle: "preserve-3d", transform: "translateZ(-100px)" }}>
      <motion.div 
        className="w-[50vw] h-[50vw] max-w-[600px] max-h-[600px] rounded-full opacity-30 blur-[100px] bg-gradient-to-tr from-emerald-500/40 via-cyan-500/20 to-purple-500/40 will-change-transform"
        animate={{ scale: [0.8, 1.2, 0.8], opacity: [0.2, 0.4, 0.2] }}
        transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
      />
    </div>

    {/* Floating Badges (Glassmorphic) */}
    <motion.div className="flex flex-wrap items-center justify-center gap-3 md:gap-4 mb-4 md:mb-6 z-10" style={{ translateZ: 150 }}
       initial={{ opacity: 0, y: 20 }}
       animate={{ opacity: 1, y: 0 }}
       transition={{ duration: 0.8, delay: 0.2 }}>
      <div className="px-3 py-1.5 md:px-4 md:py-1.5 rounded-full bg-slate-800/60 backdrop-blur-md border border-white/10 text-[10px] md:text-xs font-semibold text-emerald-300 flex items-center gap-2 shadow-lg">
        <span className="w-1.5 h-1.5 md:w-2 md:h-2 rounded-full bg-emerald-400 animate-pulse" /> رعاية فورية (IoT)
      </div>
      <div className="px-3 py-1.5 md:px-4 md:py-1.5 rounded-full bg-slate-800/60 backdrop-blur-md border border-white/10 text-[10px] md:text-xs font-semibold text-cyan-300 flex items-center gap-2 shadow-lg">
        <span className="w-1.5 h-1.5 md:w-2 md:h-2 rounded-full bg-cyan-400 animate-pulse" /> ذكاء مدمج (AI Copilot)
      </div>
      <div className="px-3 py-1.5 md:px-4 md:py-1.5 rounded-full bg-slate-800/60 backdrop-blur-md border border-white/10 text-[10px] md:text-xs font-semibold text-indigo-300 flex items-center gap-2 shadow-lg">
        <span className="w-1.5 h-1.5 md:w-2 md:h-2 rounded-full bg-indigo-400 animate-pulse" /> أمان لا مركزي (Blockchain)
      </div>
    </motion.div>

    <motion.div className="relative flex items-center justify-center w-28 h-28 md:w-32 md:h-32 lg:w-40 lg:h-40 z-10" style={{ transformStyle: "preserve-3d", transform: "translateZ(120px)" }}>
      <div className="absolute inset-0 bg-cyan-500/20 blur-[100px] rounded-full will-change-transform" style={{ transform: "translateZ(-50px)" }} />
      <motion.img 
        src="/images/icon.svg" 
        alt="Wateen" 
        className="w-full h-full object-contain filter drop-shadow-[0_20px_50px_rgba(0,180,255,0.4)] will-change-transform"
        animate={{ y: [-10, 10, -10] }} transition={{ duration: 5, repeat: Infinity, ease: "easeInOut" }}
      />
    </motion.div>

    <motion.h1 
      className="mt-3 md:mt-5 text-4xl md:text-5xl lg:text-[4.5rem] font-bold tracking-tight leading-snug bg-gradient-to-b from-white via-slate-100 to-slate-400 text-transparent bg-clip-text text-center px-4 z-10 max-w-5xl" 
      style={{ translateZ: 180 }}
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8, delay: 0.4 }}>
      مستقبل الرعاية الصحية في مصر
    </motion.h1>
    
    <motion.p 
      className="mt-2 text-sm md:text-base text-slate-400 text-center max-w-xl leading-relaxed px-4 font-medium z-10 opacity-80" 
      style={{ translateZ: 90 }}
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8, delay: 0.6 }}>
      منصة وَتِين الرقمية — نظام بيئي رائد يجمع بين الرعاية الفورية، الذكاء الاصطناعي السريري، وتأمين السجلات بتقنية البلوكشين.
    </motion.p>

    {/* Dynamic Domain Reveal */}
    <DomainReveal />

  </div>
);

const IoTVitalsContent = () => (
  <div className="flex flex-col items-center justify-center w-full h-full px-4 md:px-0" style={{ transformStyle: "preserve-3d" }}>
    <motion.div className="flex flex-col items-center gap-3 md:gap-6 mb-6 md:mb-16" style={{ translateZ: 160 }}>
      <Activity className="w-10 h-10 md:w-12 md:h-12 text-rose-500" />
      <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-white text-center shadow-black drop-shadow-lg leading-snug">نبض متصل لحظياً</h2>
    </motion.div>

    {/* Desktop: Absolute positioned cards around ECG. Mobile: Vertical stack */}
    <div className="relative w-full max-w-[1300px] flex flex-col lg:flex-row items-center justify-center lg:min-h-[400px]" style={{ transformStyle: "preserve-3d", transform: "translateZ(60px)" }}>
      
      {/* Central Heartbeat Grid Box */}
      <motion.div className="w-full max-w-3xl aspect-[16/9] md:aspect-[21/9] bg-slate-900/50 backdrop-blur-2xl rounded-2xl md:rounded-[2.5rem] border border-white/10 shadow-[0_0_120px_-20px_rgba(225,29,72,0.25)] overflow-hidden z-10 relative" style={{ transformStyle: "preserve-3d" }}>
        
        {/* Live Canvas ECG */}
        <div className="absolute inset-0 z-10">
          <LiveECGMonitor />
        </div>

        {/* BPM Display */}
        <div className="absolute top-3 md:top-5 right-4 md:right-6 flex items-center gap-2 z-20">
          <motion.div 
            className="w-2 h-2 md:w-2.5 md:h-2.5 rounded-full bg-rose-500"
            animate={{ scale: [1, 1.4, 1], opacity: [1, 0.6, 1] }}
            transition={{ duration: 0.8, repeat: Infinity, ease: "easeInOut" }}
          />
          <span className="text-rose-400 font-mono text-sm md:text-base font-bold tracking-wider">72 BPM</span>
        </div>
      </motion.div>

      {/* Mobile: Grid of feature cards below ECG */}
      <div className="grid grid-cols-2 gap-2.5 mt-4 w-full lg:hidden">
        {[
          { icon: BrainCircuit, title: "اكتشاف التشوهات", desc: "تحليل المؤشرات لاكتشاف أي تشوهات مبكراً.", color: "emerald" },
          { icon: Activity, title: "مراقبة مستمرة", desc: "تتبع لحظي لنبض القلب والضغط.", color: "cyan" },
          { icon: ShieldAlert, title: "تنبيهات طوارئ", desc: "تنبيهات فورية عند تخطي المعدلات.", color: "rose" },
          { icon: Database, title: "تسجيل زمني", desc: "توثيق مستمر في محفظتك المشفرة.", color: "purple" },
        ].map((card, i) => {
          const Icon = card.icon;
          const colorMap: Record<string, { bg: string; border: string; text: string; iconBg: string; iconBorder: string }> = {
            emerald: { bg: "bg-emerald-500/5", border: "border-emerald-500/20", text: "text-emerald-400", iconBg: "bg-emerald-500/20", iconBorder: "border-emerald-500/30" },
            cyan: { bg: "bg-cyan-500/5", border: "border-cyan-500/20", text: "text-cyan-400", iconBg: "bg-cyan-500/20", iconBorder: "border-cyan-500/30" },
            rose: { bg: "bg-rose-500/5", border: "border-rose-500/20", text: "text-rose-400", iconBg: "bg-rose-500/20", iconBorder: "border-rose-500/30" },
            purple: { bg: "bg-purple-500/5", border: "border-purple-500/20", text: "text-purple-400", iconBg: "bg-purple-500/20", iconBorder: "border-purple-500/30" },
          };
          const c = colorMap[card.color];
          return (
            <motion.div
              key={i}
              className={`${c.bg} backdrop-blur-xl p-3 rounded-xl border ${c.border} select-none`}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 * i, duration: 0.5 }}
            >
              <div className="flex items-center gap-2 mb-1.5">
                <div className={`p-1.5 rounded-lg ${c.iconBg} border ${c.iconBorder}`}>
                  <Icon className={`w-3.5 h-3.5 ${c.text}`} />
                </div>
                <span className="text-white font-bold text-[11px] leading-tight">{card.title}</span>
              </div>
              <p className="text-slate-400 text-[10px] leading-relaxed font-medium">{card.desc}</p>
            </motion.div>
          );
        })}
      </div>

      {/* Desktop: Original absolute-positioned floating cards */}
      <motion.div 
        className="hidden lg:block absolute top-0 right-0 lg:-top-4 lg:-right-4 bg-slate-900/80 backdrop-blur-xl p-4 rounded-2xl border border-emerald-500/20 shadow-[0_20px_40px_-15px_rgba(16,185,129,0.2)] w-[240px] select-none z-20"
        style={{ translateZ: 180 }}
        animate={{ y: [-8, 8, -8] }}
        transition={{ duration: 4.5, repeat: Infinity, ease: "easeInOut", delay: 0 }}
      >
        <div className="flex items-center gap-3 mb-2 md:mb-3">
          <div className="p-2 rounded-lg bg-emerald-500/20 border border-emerald-500/30">
            <BrainCircuit className="w-4 h-4 md:w-5 md:h-5 text-emerald-400" />
          </div>
          <div className="text-white font-bold text-xs md:text-sm">اكتشاف مبكر للتشوهات</div>
        </div>
        <p className="text-slate-300 text-xs md:text-sm leading-relaxed font-medium">
          الذكاء الاصطناعي يحلل المؤشرات لاكتشاف أي تشوهات قبل تفاقمها.
        </p>
      </motion.div>

      <motion.div 
        className="hidden lg:block absolute bottom-0 right-0 lg:-bottom-4 lg:-right-4 bg-slate-900/80 backdrop-blur-xl p-4 rounded-2xl border border-cyan-500/20 shadow-[0_20px_40px_-15px_rgba(6,182,212,0.2)] w-[240px] select-none z-20"
        style={{ translateZ: 140 }}
        animate={{ y: [8, -8, 8] }}
        transition={{ duration: 5.5, repeat: Infinity, ease: "easeInOut", delay: 1 }}
      >
        <div className="flex items-center gap-3 mb-2 md:mb-3">
          <div className="p-2 rounded-lg bg-cyan-500/20 border border-cyan-500/30">
            <Activity className="w-4 h-4 md:w-5 md:h-5 text-cyan-400" />
          </div>
          <div className="text-white font-bold text-xs md:text-sm">مراقبة حيوية مستمرة</div>
        </div>
        <p className="text-slate-300 text-xs md:text-sm leading-relaxed font-medium">
          تتبع لحظي لنبض القلب والضغط عبر الأجهزة الذكية القابلة للارتداء.
        </p>
      </motion.div>

      <motion.div 
        className="hidden lg:block absolute top-0 left-0 lg:-top-4 lg:-left-4 bg-slate-900/80 backdrop-blur-xl p-4 rounded-2xl border border-rose-500/20 shadow-[0_20px_40px_-15px_rgba(225,29,72,0.2)] w-[240px] select-none z-20"
        style={{ translateZ: 190 }}
        animate={{ y: [10, -10, 10] }}
        transition={{ duration: 5, repeat: Infinity, ease: "easeInOut", delay: 0.5 }}
      >
        <div className="flex items-center gap-3 mb-2 md:mb-3">
          <div className="p-2 rounded-lg bg-rose-500/20 border border-rose-500/30">
            <ShieldAlert className="w-4 h-4 md:w-5 md:h-5 text-rose-400" />
          </div>
          <div className="text-white font-bold text-xs md:text-sm">تنبيهات طوارئ استباقية</div>
        </div>
        <p className="text-slate-300 text-xs md:text-sm leading-relaxed font-medium">
          إرسال تنبيهات فورية للفريق الطبي عند تخطي المؤشرات المعدلات الطبيعية.
        </p>
      </motion.div>

      <motion.div 
        className="hidden lg:block absolute bottom-0 left-0 lg:-bottom-4 lg:-left-4 bg-slate-900/80 backdrop-blur-xl p-4 rounded-2xl border border-purple-500/20 shadow-[0_20px_40px_-15px_rgba(168,85,247,0.2)] w-[240px] select-none z-20"
        style={{ translateZ: 150 }}
        animate={{ y: [-6, 6, -6] }}
        transition={{ duration: 4.8, repeat: Infinity, ease: "easeInOut", delay: 1.5 }}
      >
        <div className="flex items-center gap-3 mb-2 md:mb-3">
          <div className="p-2 rounded-lg bg-purple-500/20 border border-purple-500/30">
            <Database className="w-4 h-4 md:w-5 md:h-5 text-purple-400" />
          </div>
          <div className="text-white font-bold text-xs md:text-sm">تسجيل زمني دقيق</div>
        </div>
        <p className="text-slate-300 text-xs md:text-sm leading-relaxed font-medium">
          توثيق مستمر للتغيرات الحيوية في قاعدة بيانات محفظتك الصحية المشفرة.
        </p>
      </motion.div>
    </div>
  </div>
);

const AICopilotContent = () => {
  const containerVariants = {
    hidden: {},
    visible: { transition: { staggerChildren: 0.15, delayChildren: 0.2 } },
  };

  const itemVariants = {
    hidden: { opacity: 0, x: 50 },
    visible: { opacity: 1, x: 0, transition: { duration: 0.7, ease: [0.22, 1, 0.36, 1] } },
  };

  const BULLETS = [
    { icon: Activity, text: "تحليل حيوي لحظي", desc: "مراقبة مستمرة للعلامات الحيوية مع تنبيهات ذكية فورية لحالتك" },
    { icon: BrainCircuit, text: "توقع المخاطر قبل حدوثها", desc: "خوارزميات تنبؤية تحلل الأنماط لاكتشاف الأزمات الصحية مبكراً" },
    { icon: Calculator, text: "دعم القرار الطبي الدقيق", desc: "حساب معقد لجرعات الأدوية استناداً إلى حالة المريض والوزن" },
    { icon: ShieldAlert, text: "تحليل التداخلات الدوائية", desc: "تحليل متقدم لتفاعلات الأدوية المتعددة لضمان أقصى درجات السلامة" },
    { icon: HeartPulse, text: "استجابة فائقة للطوارئ", desc: "حزمة بروتوكولات طبية وتوجيهات لحظية للتعامل مع المواقف الحرجة" },
  ];

  return (
    <div dir="rtl" className="min-h-screen relative flex items-center overflow-hidden py-8 md:py-16 lg:py-24 w-full px-4 md:px-0" style={{ transformStyle: "preserve-3d" }}>
      {/* Background Aura */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[300px] h-[300px] md:w-[500px] md:h-[500px] lg:w-[700px] lg:h-[700px] bg-cyan-500/10 mix-blend-screen blur-[80px] md:blur-[100px] rounded-full animate-pulse pointer-events-none" />

      <div className="relative z-10 w-full max-w-[1200px] mx-auto px-2 md:px-6 lg:px-12 grid grid-cols-1 lg:grid-cols-2 gap-6 lg:gap-12 items-center">
        {/* Typography & Bullets Column */}
        <motion.div
           variants={containerVariants}
           initial="hidden"
           whileInView="visible"
           viewport={{ once: true, amount: 0.3 }}
           className="flex flex-col justify-center order-2 lg:order-1"
           style={{ translateZ: 140 }}
        >
          <motion.div variants={itemVariants}>
            <BrainCircuit className="w-10 h-10 md:w-12 md:h-12 lg:w-14 lg:h-14 text-cyan-400 mb-4 md:mb-5 drop-shadow-[0_0_20px_rgba(6,182,212,0.5)]" />
          </motion.div>

          <motion.h2
            variants={itemVariants}
            className="text-2xl md:text-3xl lg:text-4xl xl:text-5xl font-black text-white leading-snug lg:leading-snug tracking-tight drop-shadow-md"
          >
            مساعد طبي بذكاء اصطناعي{" "}
            <span className="bg-gradient-to-l from-cyan-400 via-cyan-300 to-purple-500 bg-clip-text text-transparent">
              لا ينام أبداً.
            </span>
          </motion.h2>

          <motion.p
            variants={itemVariants}
            className="mt-4 md:mt-5 text-sm md:text-base lg:text-lg text-slate-300 leading-relaxed max-w-xl font-medium"
          >
            تكنولوجيا الذكاء الاصطناعي الأقوى لدعم أطبائك، لتقديم رعاية منزلية ترقى للمعايير العالمية، مدمجة في نظام متكامل.
          </motion.p>

          {/* Bullet Points */}
          <motion.ul variants={itemVariants} className="mt-5 md:mt-8 space-y-3 md:space-y-4">
            {BULLETS.map((bullet, i) => {
              const Icon = bullet.icon;
              return (
                <li key={i} className="group flex items-start gap-3 md:gap-4 cursor-default">
                  <div className="flex-shrink-0 w-9 h-9 md:w-10 md:h-10 rounded-xl md:rounded-[0.8rem] bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center transition-all duration-300 group-hover:bg-cyan-500/20 group-hover:shadow-[0_0_20px_rgba(6,182,212,0.3)] group-hover:border-cyan-400/50 group-hover:-translate-y-1">
                    <Icon className="w-4 h-4 md:w-5 md:h-5 text-cyan-400 transition-transform duration-300 group-hover:scale-110 group-hover:text-cyan-200" />
                  </div>
                  <div className="flex flex-col pt-0.5 md:pt-1">
                    <span className="text-sm md:text-base font-bold text-white group-hover:text-cyan-200 transition-colors duration-300">
                      {bullet.text}
                    </span>
                    <span className="text-[11px] md:text-sm font-medium text-slate-400 mt-0.5 md:mt-1 leading-relaxed">
                      {bullet.desc}
                    </span>
                  </div>
                </li>
              );
            })}
          </motion.ul>
        </motion.div>

          {/* Floating 3D Holographic AI Head — Hidden on mobile */}
          <motion.div
            className="hidden lg:flex relative h-[400px] md:h-[500px] lg:h-[480px] w-full order-1 lg:order-2 items-center justify-center perspective-[1500px]"
            initial={{ opacity: 0, y: 60 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.2 }}
            transition={{ duration: 1.2, ease: [0.22, 1, 0.36, 1], delay: 0.2 }}
            style={{ transformStyle: "preserve-3d", transform: "translateZ(100px)" }}
          >
            {/* Ambient Deep Glow */}
            <motion.div
              className="absolute w-[250px] h-[250px] lg:w-[350px] lg:h-[350px] rounded-full pointer-events-none"
              style={{ background: 'radial-gradient(circle, rgba(6,182,212,0.15) 0%, rgba(139,92,246,0.1) 50%, transparent 70%)', transform: "translateZ(-100px)" }}
              animate={{ scale: [1, 1.2, 1], opacity: [0.5, 0.8, 0.5] }}
              transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
            />

            {/* Neural Matrix Halos (Rotating in 3D Space) */}
            <motion.div
              className="absolute w-[200px] h-[200px] md:w-[280px] md:h-[280px] rounded-full border border-cyan-500/20"
              style={{ transformStyle: "preserve-3d", transform: "translateZ(50px)" }}
              animate={{ rotateX: [60, 60], rotateZ: [0, 360] }}
              transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
            >
              <div className="absolute top-0 left-1/2 w-4 h-4 bg-cyan-400 rounded-full shadow-[0_0_20px_#06b6d4] -translate-x-1/2 -translate-y-1/2" style={{ transform: "translateZ(20px)" }} />
              <div className="absolute bottom-0 left-1/2 w-2 h-2 bg-purple-400 rounded-full shadow-[0_0_15px_#a855f7] -translate-x-1/2 translate-y-1/2" style={{ transform: "translateZ(20px)" }} />
            </motion.div>

            <motion.div
              className="absolute w-[280px] h-[280px] md:w-[380px] md:h-[380px] rounded-full border border-purple-500/10"
              style={{ transformStyle: "preserve-3d", transform: "translateZ(80px)" }}
              animate={{ rotateY: [70, 70], rotateX: [20, 20], rotateZ: [360, 0] }}
              transition={{ duration: 25, repeat: Infinity, ease: "linear" }}
            >
              <div className="absolute top-1/2 right-0 w-3 h-3 bg-purple-400 rounded-full shadow-[0_0_20px_#a855f7] translate-x-1/2 -translate-y-1/2" style={{ transform: "translateZ(30px)" }} />
            </motion.div>

            {/* 3D Head Container */}
            <motion.div
              className="relative w-[180px] h-[240px] md:w-[240px] md:h-[320px] lg:w-[280px] lg:h-[380px]"
              style={{ transformStyle: "preserve-3d", transform: "translateZ(150px)" }}
              animate={{ y: [-15, 15, -15], rotateY: [-5, 5, -5], rotateX: [2, -2, 2] }}
              transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
            >
              {/* Core Head SVG - Glassmorphic Abstract Shape */}
              <svg viewBox="0 0 200 280" className="absolute inset-0 w-full h-full drop-shadow-[0_0_30px_rgba(6,182,212,0.3)]" style={{ transform: "translateZ(180px)", overflow: "visible" }}>
                <defs>
                  <linearGradient id="headGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.8" />
                    <stop offset="50%" stopColor="#3b82f6" stopOpacity="0.4" />
                    <stop offset="100%" stopColor="#a855f7" stopOpacity="0.8" />
                  </linearGradient>
                  <filter id="meshGlow" x="-20%" y="-20%" width="140%" height="140%">
                    <feGaussianBlur stdDeviation="8" result="blur" />
                    <feMerge>
                      <feMergeNode in="blur" />
                      <feMergeNode in="SourceGraphic" />
                    </feMerge>
                  </filter>
                </defs>
                {/* Abstract Tech Head Profile */}
                <path 
                  d="M100,5 C140,5 180,45 180,95 C180,120 165,145 155,165 C145,185 140,210 135,230 C130,250 115,270 95,275 C75,280 60,255 55,235 C50,210 45,185 30,165 C15,145 10,120 10,95 C10,45 50,5 100,5 Z" 
                  fill="none" 
                  stroke="url(#headGrad)" 
                  strokeWidth="2"
                  filter="url(#meshGlow)"
                  className="animate-[pulse_4s_cubic-bezier(0.4,0,0.6,1)_infinite]"
                />
                
                {/* Neural Mesh Grid (Internal) */}
                <path d="M50,95 Q100,40 150,95 T150,165 T100,230 T50,165 Z" fill="none" stroke="rgba(6,182,212,0.3)" strokeWidth="1" strokeDasharray="4 4" />
                <path d="M20,130 L180,130" stroke="rgba(168,85,247,0.3)" strokeWidth="1" />
                <path d="M100,20 L100,260" stroke="rgba(168,85,247,0.3)" strokeWidth="1" />
                
                {/* Visualizer Lines (Thinking Effect) */}
                <motion.path 
                  d="M70,110 C85,90 115,90 130,110" 
                  fill="none" 
                  stroke="#06b6d4" 
                  strokeWidth="3" 
                  strokeLinecap="round"
                  initial={{ pathLength: 0, opacity: 0 }}
                  animate={{ pathLength: 1, opacity: 1 }}
                  transition={{ duration: 2, repeat: Infinity, repeatType: "reverse", ease: "easeInOut" }}
                />
              </svg>

              {/* The "Eye" / Quantum Core */}
              <motion.div
                className="absolute top-[40%] left-1/2 w-12 h-12 md:w-16 md:h-16 rounded-full bg-cyan-400 flex items-center justify-center shadow-[0_0_60px_#06b6d4,inset_0_0_20px_#fff]"
                style={{ 
                  transform: "translate3d(-50%, -50%, 250px)"
                }}
                animate={{ scale: [1, 1.15, 1] }}
                transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
              >
                <div className="w-4 h-4 rounded-full bg-white shadow-[0_0_10px_#fff]" />
              </motion.div>

              {/* Floating Data Nodes around the Core */}
              {[...Array(6)].map((_, i) => (
                <motion.div
                  key={i}
                  className="absolute top-[40%] left-1/2 w-1.5 h-1.5 bg-purple-300 rounded-full shadow-[0_0_10px_#a855f7]"
                  style={{
                    transformOrigin: "center center",
                    marginTop: "-3px",
                    marginLeft: "-3px",
                    transform: `translateZ(${220 + (i * 10)}px)`
                  }}
                  animate={{
                    x: [Math.cos(i * (Math.PI / 3)) * 60, Math.cos((i * (Math.PI / 3)) + Math.PI) * 60, Math.cos(i * (Math.PI / 3)) * 60],
                    y: [Math.sin(i * (Math.PI / 3)) * 60, Math.sin((i * (Math.PI / 3)) + Math.PI) * 60, Math.sin(i * (Math.PI / 3)) * 60],
                    opacity: [0, 1, 0]
                  }}
                  transition={{
                    duration: 4 + (i * 0.5),
                    repeat: Infinity,
                    ease: "easeInOut",
                    delay: i * 0.2
                  }}
                />
              ))}

              {/* Cybernetic Inner Rings */}
              <motion.div 
                className="absolute top-[40%] left-1/2 w-[120px] h-[120px] border-2 border-dashed border-cyan-500/40 rounded-full"
                style={{ transformStyle: "preserve-3d", transform: "translate3d(-50%, -50%, 200px)" }}
                animate={{ rotateZ: 360, rotateX: [10, -10, 10] }}
                transition={{ rotateZ: { duration: 10, repeat: Infinity, ease: "linear" }, rotateX: { duration: 4, repeat: Infinity, ease: "easeInOut" } }}
              />

            </motion.div>

          {/* Label */}
          <motion.div
            className="absolute bottom-2 left-1/2 -translate-x-1/2 bg-slate-800/60 backdrop-blur-md px-4 py-1.5 rounded-full border border-white/5 shadow-lg z-20"
            animate={{ y: [-3, 3, -3] }}
            transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
          >
            <span className="text-cyan-300/80 text-xs font-medium tracking-wide">المساعد الذكي — يعمل على مدار الساعة</span>
          </motion.div>
        </motion.div>
      </div>
    </div>
  );
};

const ShieldContent = () => (
  <div className="flex flex-col items-center justify-center w-full h-full px-4 md:px-0" style={{ transformStyle: "preserve-3d" }}>
    <motion.div style={{ translateZ: 180 }} className="text-center mb-6 md:mb-16 z-10 relative">
      <ShieldCheck className="w-10 h-10 md:w-14 md:h-14 lg:w-16 lg:h-16 text-emerald-400 mx-auto mb-4 md:mb-5 drop-shadow-[0_0_30px_rgba(52,211,153,0.5)]" />
      <h2 className="text-2xl md:text-3xl lg:text-5xl font-bold text-white text-balance drop-shadow-xl leading-snug">حماية سيبرانية لا تُخترق</h2>
    </motion.div>
    
    <div className="relative w-full max-w-[1300px] flex flex-col lg:flex-row items-center justify-center lg:min-h-[400px]" style={{ transformStyle: "preserve-3d", transform: "translateZ(60px)" }}>
      {/* Central Shield Animation Box - Floating Radar */}
      <motion.div className="w-full max-w-4xl aspect-[16/9] md:aspect-[21/9] flex items-center justify-center overflow-visible z-10 relative" style={{ transformStyle: "preserve-3d" }}>
        
        <div className="absolute inset-0 flex items-center justify-center opacity-80" style={{ transformStyle: "preserve-3d", transform: "translateZ(20px) rotateX(60deg)", marginTop: "10vh" }}>
          <div className="absolute w-12 h-12 md:w-16 md:h-16 lg:w-20 lg:h-20 bg-emerald-500 rounded-full shadow-[0_0_80px_rgba(16,185,129,1)] z-20" style={{ transform: "translateZ(60px)" }} />
          {[1, 2, 3, 4, 5].map((i) => (
            <motion.div key={i} className={`absolute rounded-full border-[2px] md:border-[3px] border-emerald-500/30 ${i > 3 ? 'hidden md:block' : ''}`} style={{ width: i * (typeof window !== 'undefined' && window.innerWidth < 768 ? 80 : 140), height: i * (typeof window !== 'undefined' && window.innerWidth < 768 ? 80 : 140), translateZ: (6 - i) * 10 }}
              animate={{ rotateZ: [0, 360], scale: [0.95, 1.05, 0.95], opacity: [0.2, 0.6, 0.2] }}
              transition={{ rotateZ: { duration: 15 + i * 5, repeat: Infinity, ease: "linear" }, scale: { duration: 4, repeat: Infinity, ease: "easeInOut", delay: i * 0.4 }, opacity: { duration: 4, repeat: Infinity, ease: "easeInOut", delay: i * 0.4 } }}>
              <div className="w-1/2 h-full absolute top-0 right-0 origin-left border-r-4 border-emerald-400 bg-gradient-to-r from-transparent to-emerald-500/40 rounded-r-full backdrop-blur-sm" />
            </motion.div>
          ))}
          {Array.from({ length: 12 }).map((_, i) => (
             <motion.div key={i} className={`absolute w-2 h-2 md:w-3 md:h-3 lg:w-4 lg:h-4 bg-emerald-200 rounded-full shadow-[0_0_20px_white] ${i > 7 ? 'hidden md:block' : ''}`}
               style={{ transformOrigin: `0 ${100 + (i % 4) * 30}px`, left: '50%', top: '50%', marginTop: -(100 + (i % 4) * 30), marginLeft: -2, translateZ: 30 + i * 5, rotateZ: i * 30 }}
               animate={{ opacity: [0, 1, 0], scale: [0.5, 1.5, 0.5] }} transition={{ duration: 3, repeat: Infinity, delay: i * 0.25 }} />
          ))}
        </div>
      </motion.div>

      {/* Mobile: Grid of security cards below radar */}
      <div className="grid grid-cols-2 gap-2.5 mt-4 w-full lg:hidden">
        {[
          { icon: ShieldCheck, title: "تشفير طرف-إلى-طرف", desc: "بياناتك مشفرة ببروتوكولات عسكرية.", color: "emerald" },
          { icon: BrainCircuit, title: "هوية لا مركزية", desc: "تحقق ذكي عبر البلوكشين.", color: "cyan" },
          { icon: Database, title: "محفظة صحية آمنة", desc: "سجلاتك مخزنة في شبكة بلوكشين.", color: "rose" },
          { icon: ShieldAlert, title: "منع الاختراق", desc: "مراقبة حية لصد الهجمات.", color: "purple" },
        ].map((card, i) => {
          const Icon = card.icon;
          const colorMap: Record<string, { bg: string; border: string; text: string; iconBg: string; iconBorder: string }> = {
            emerald: { bg: "bg-emerald-500/5", border: "border-emerald-500/20", text: "text-emerald-400", iconBg: "bg-emerald-500/20", iconBorder: "border-emerald-500/30" },
            cyan: { bg: "bg-cyan-500/5", border: "border-cyan-500/20", text: "text-cyan-400", iconBg: "bg-cyan-500/20", iconBorder: "border-cyan-500/30" },
            rose: { bg: "bg-rose-500/5", border: "border-rose-500/20", text: "text-rose-400", iconBg: "bg-rose-500/20", iconBorder: "border-rose-500/30" },
            purple: { bg: "bg-purple-500/5", border: "border-purple-500/20", text: "text-purple-400", iconBg: "bg-purple-500/20", iconBorder: "border-purple-500/30" },
          };
          const c = colorMap[card.color];
          return (
            <motion.div
              key={i}
              className={`${c.bg} backdrop-blur-xl p-3 rounded-xl border ${c.border} select-none`}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 * i, duration: 0.5 }}
            >
              <div className="flex items-center gap-2 mb-1.5">
                <div className={`p-1.5 rounded-lg ${c.iconBg} border ${c.iconBorder}`}>
                  <Icon className={`w-3.5 h-3.5 ${c.text}`} />
                </div>
                <span className="text-white font-bold text-[11px] leading-tight">{card.title}</span>
              </div>
              <p className="text-slate-400 text-[10px] leading-relaxed font-medium">{card.desc}</p>
            </motion.div>
          );
        })}
      </div>

      {/* Desktop: E2E Encryption (Top Right) */}
      <motion.div 
        className="hidden lg:block absolute top-0 right-0 lg:-top-4 lg:-right-4 bg-slate-900/80 backdrop-blur-xl p-4 rounded-2xl border border-emerald-500/20 shadow-[0_20px_40px_-15px_rgba(16,185,129,0.2)] w-[240px] select-none z-20"
        style={{ translateZ: 180 }}
        animate={{ y: [-8, 8, -8] }}
        transition={{ duration: 4.5, repeat: Infinity, ease: "easeInOut", delay: 0 }}
      >
        <div className="flex items-center gap-3 mb-2 md:mb-3">
          <div className="p-2 rounded-lg bg-emerald-500/20 border border-emerald-500/30">
            <ShieldCheck className="w-4 h-4 md:w-5 md:h-5 text-emerald-400" />
          </div>
          <div className="text-white font-bold text-xs md:text-sm">تشفير طرف-إلى-طرف</div>
        </div>
        <p className="text-slate-300 text-xs md:text-sm leading-relaxed font-medium">
          جميع بياناتك الطبية والشخصية مشفرة ببروتوكولات عسكرية لا يمكن اختراقها.
        </p>
      </motion.div>

      <motion.div 
        className="hidden lg:block absolute bottom-0 right-0 lg:-bottom-4 lg:-right-4 bg-slate-900/80 backdrop-blur-xl p-4 rounded-2xl border border-cyan-500/20 shadow-[0_20px_40px_-15px_rgba(6,182,212,0.2)] w-[240px] select-none z-20"
        style={{ translateZ: 140 }}
        animate={{ y: [8, -8, 8] }}
        transition={{ duration: 5.5, repeat: Infinity, ease: "easeInOut", delay: 1 }}
      >
        <div className="flex items-center gap-3 mb-2 md:mb-3">
          <div className="p-2 rounded-lg bg-cyan-500/20 border border-cyan-500/30">
            <BrainCircuit className="w-4 h-4 md:w-5 md:h-5 text-cyan-400" />
          </div>
          <div className="text-white font-bold text-xs md:text-sm">هوية لا مركزية (KYC)</div>
        </div>
        <p className="text-slate-300 text-xs md:text-sm leading-relaxed font-medium">
          نظام تحقق ذكي عبر البلوكشين وتعرف على الوجه لمنع انتحال الشخصية.
        </p>
      </motion.div>

      <motion.div 
        className="hidden lg:block absolute top-0 left-0 lg:-top-4 lg:-left-4 bg-slate-900/80 backdrop-blur-xl p-4 rounded-2xl border border-rose-500/20 shadow-[0_20px_40px_-15px_rgba(225,29,72,0.2)] w-[240px] select-none z-20"
        style={{ translateZ: 190 }}
        animate={{ y: [10, -10, 10] }}
        transition={{ duration: 5, repeat: Infinity, ease: "easeInOut", delay: 0.5 }}
      >
        <div className="flex items-center gap-3 mb-2 md:mb-3">
          <div className="p-2 rounded-lg bg-rose-500/20 border border-rose-500/30">
            <Database className="w-4 h-4 md:w-5 md:h-5 text-rose-400" />
          </div>
          <div className="text-white font-bold text-xs md:text-sm">محفظة صحية لامركزية</div>
        </div>
        <p className="text-slate-300 text-xs md:text-sm leading-relaxed font-medium">
          سجلاتك الطبية مخزنة في شبكة بلوكشين، أنت فقط من يملك مفتاح الوصول إليها.
        </p>
      </motion.div>

      <motion.div 
        className="hidden lg:block absolute bottom-0 left-0 lg:-bottom-4 lg:-left-4 bg-slate-900/80 backdrop-blur-xl p-4 rounded-2xl border border-purple-500/20 shadow-[0_20px_40px_-15px_rgba(168,85,247,0.2)] w-[240px] select-none z-20"
        style={{ translateZ: 150 }}
        animate={{ y: [-6, 6, -6] }}
        transition={{ duration: 4.8, repeat: Infinity, ease: "easeInOut", delay: 1.5 }}
      >
        <div className="flex items-center gap-3 mb-2 md:mb-3">
          <div className="p-2 rounded-lg bg-purple-500/20 border border-purple-500/30">
            <ShieldAlert className="w-4 h-4 md:w-5 md:h-5 text-purple-400" />
          </div>
          <div className="text-white font-bold text-xs md:text-sm">نظام منع الاختراق (IPS)</div>
        </div>
        <p className="text-slate-300 text-xs md:text-sm leading-relaxed font-medium">
          مراقبة حية للشبكة لصد الهجمات وحماية خصوصية بيانات المرضى والمستشفيات.
        </p>
      </motion.div>
    </div>
  </div>
);

function TopNavbar() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 50);
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <motion.nav
      dir="rtl"
      className="fixed top-0 left-0 right-0 z-50 select-none"
      initial={{ opacity: 0, y: -30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
    >
      <div
        className="mx-auto flex items-center justify-between px-4 md:px-8 lg:px-10 py-3 md:py-4 transition-all duration-500"
        style={{
          background: scrolled
            ? "rgba(2, 4, 8, 0.75)"
            : "transparent",
          backdropFilter: scrolled ? "blur(24px) saturate(180%)" : "none",
          borderBottom: scrolled
            ? "1px solid rgba(255,255,255,0.06)"
            : "1px solid transparent",
        }}
      >
        {/* Right side — Logo */}
        <a href="#hero" className="flex items-center gap-2 md:gap-3 group">
          <motion.img
            src="/images/icon.svg"
            alt="Wateen"
            className="w-8 h-8 md:w-10 md:h-10 lg:w-12 lg:h-12 object-contain drop-shadow-lg"
            whileHover={{ scale: 1.1, rotate: -5 }}
            transition={{ type: "spring", stiffness: 300, damping: 15 }}
            draggable={false}
          />
          <span className="text-lg md:text-xl lg:text-2xl font-black bg-gradient-to-l from-white via-cyan-200 to-cyan-400 bg-clip-text text-transparent group-hover:opacity-90 transition-opacity">
            وَتِين
          </span>
        </a>

        {/* Left side — Auth buttons */}
        <div className="flex items-center gap-3">
          <motion.a
            href="/login"
            className="flex items-center gap-1.5 md:gap-2 px-3 py-2 md:px-5 md:py-2.5 rounded-xl text-xs md:text-sm lg:text-base font-bold text-white cursor-pointer"
            style={{
              background: "linear-gradient(135deg, #0088FF 0%, #6C3AED 100%)",
              boxShadow:
                "0 0 20px rgba(0,136,255,0.25), 0 4px 12px rgba(0,0,0,0.3)",
            }}
            whileHover={{
              scale: 1.04,
              boxShadow:
                "0 0 30px rgba(0,136,255,0.4), 0 8px 24px rgba(0,0,0,0.4)",
            }}
            whileTap={{ scale: 0.96 }}
            transition={{ type: "spring", stiffness: 400, damping: 25 }}
          >
            <UserPlus className="w-4 h-4 md:w-5 md:h-5" strokeWidth={2} />
            <span className="hidden md:inline">تسجيل الدخول / إنشاء حساب</span>
            <span className="md:hidden">دخول</span>
          </motion.a>
        </div>
      </div>
    </motion.nav>
  );
}
