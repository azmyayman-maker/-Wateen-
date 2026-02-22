"use client";

import React, { useRef } from "react";
import { motion, useScroll, useTransform } from "framer-motion";
import { 
  Activity, BrainCircuit, ShieldCheck, MapPin, Database, Award, ArrowLeft,
  Syringe, Cross, HeartPulse, HeartHandshake, UserCheck, Droplets, FlaskConical, Star
} from "lucide-react";
import { useLanguage } from "@/lib/i18n";

export default function ServicesPage() {
  const { isRTL } = useLanguage();
  const containerRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end end"]
  });

  const headerY = useTransform(scrollYProgress, [0, 0.2], [0, -100]);
  const headerOpacity = useTransform(scrollYProgress, [0, 0.2], [1, 0]);

  // Content derived exactly from the Master Implementation Plan (MIP v3.2)
  const content = {
    badge: isRTL ? "خدماتنا" : "Our Services",
    title: isRTL ? "منظومة الرعاية الصحية المتكاملة" : "Comprehensive Healthcare Ecosystem",
    subtitle: isRTL 
      ? "تتجاوز واتين مفهوم التمريض المنزلي التقليدي لتقدم منظومة صحية متكاملة مدعومة بإنترنت الأشياء، الذكاء الاصطناعي، وتقنية البلوك تشين." 
      : "Wateen goes beyond traditional home nursing to offer a comprehensive healthcare ecosystem powered by IoT, AI, and Blockchain.",
    backBtn: isRTL ? "العودة للرئيسية" : "Back to Home",
    services: [
      {
        icon: Activity,
        color: "text-rose-400",
        bg: "bg-rose-500/10",
        border: "border-rose-500/20",
        title: isRTL ? "مراقبة العلامات الحيوية (IoT)" : "Real-time Vitals Monitoring",
        desc: isRTL 
          ? "تكامل مباشر مع الأجهزة القابلة للارتداء لمراقبة مستمرة لمعدل ضربات القلب، ضغط الدم، ونسبة الأكسجين. يشمل نظام تنبيهات مبكر للتشوهات." 
          : "Direct integration with wearables for continuous monitoring of HR, BP, and SpO2. Includes an early warning system for anomalies."
      },
      {
        icon: BrainCircuit,
        color: "text-cyan-400",
        bg: "bg-cyan-500/10",
        border: "border-cyan-500/20",
        title: isRTL ? "المساعد الطبي الذكي (AI Copilot)" : "AI Clinical Decision Support",
        desc: isRTL 
          ? "مساعد ذكي مدرب لدعم الكوادر التمريضية بقرارات سريرية فورية، حسابات دقيقة للجرعات، والتحقق من التفاعلات الدوائية باللغة العربية." 
          : "A trained AI assistant supporting nursing staff with instant clinical decisions, precise dosage calculations, and drug interaction checks."
      },
      {
        icon: ShieldCheck,
        color: "text-purple-400",
        bg: "bg-purple-500/10",
        border: "border-purple-500/20",
        title: isRTL ? "سجلات مؤمنة (Blockchain)" : "Blockchain-Secured Records",
        desc: isRTL 
          ? "أول محفظة صحية في مصر بتقنية Hyperledger Fabric، تضمن تشفير السجلات الطبية بالكامل ومنح حق الوصول الحصري للمريض." 
          : "Egypt's first health wallet via Hyperledger Fabric, ensuring fully encrypted medical records and exclusive patient access control."
      },
      {
        icon: MapPin,
        color: "text-emerald-400",
        bg: "bg-emerald-500/10",
        border: "border-emerald-500/20",
        title: isRTL ? "ملاحة دقيقة (Hyper-local Navigation)" : "Hyper-Local Navigation",
        desc: isRTL 
          ? "تجاوز تحديات العناوين غير المنظمة باستخدام نظام توجيه ذكي يعتمد على المعالم، لتسريع وصول التمريض وتقليل זמן الاستجابة." 
          : "Overcoming unstructured addressing challenges using landmark-based smart routing to accelerate nurse arrival and reduce response time."
      },
      {
        icon: Database,
        color: "text-orange-400",
        bg: "bg-orange-500/10",
        border: "border-orange-500/20",
        title: isRTL ? "تسعير ديناميكي وخدمات تنبؤية" : "Dynamic Pricing & Prediction",
        desc: isRTL 
          ? "تسعير متكيف حسب المنطقة والطلب، وتنبؤ استباقي للحالات الصحية من خلال تحليل البيانات التاريخية بذكاء." 
          : "Adaptive pricing based on zone and demand, alongside proactive health state prediction through intelligent historical data analysis."
      },
      {
        icon: Award,
        color: "text-yellow-400",
        bg: "bg-yellow-500/10",
        border: "border-yellow-500/20",
        title: isRTL ? "تأكيد الهوية البيومتري (KYC)" : "Biometric Identity Verification",
        desc: isRTL 
          ? "عمليات تحقق صارمة لمقدمي الخدمة تشمل التعرف على الوجوه ومطابقة مستندات النقابة والبطاقة، لضمان أعلى معايير الأمان والثقة." 
          : "Rigorous provider checks including facial recognition and syndicate/ID document matching, ensuring the highest standards of safety and trust."
      }
    ]
  };

  const coreServices = isRTL ? [
    { title: "زيارة تمريضية شاملة", desc: "رعاية تمريضية متكاملة في راحة منزلك بواسطة نخبة من الممرضين المؤهلين.", icon: HeartHandshake, color: "from-blue-400 to-indigo-500", shadow: "shadow-blue-500/20", colSpan: "lg:col-span-2 lg:row-span-2" },
    { title: "الحقن الوريدي والعضلي", desc: "إعطاء الحقن بجميع أنواعها بأعلى معايير التعقيم.", icon: Syringe, color: "from-emerald-400 to-teal-500", shadow: "shadow-emerald-500/20", colSpan: "lg:col-span-2" },
    { title: "تركيب الكانيولا والمحاليل", desc: "تركيب الكانيولا الوريدية والمحاليل باحترافية وبدون ألم.", icon: Droplets, color: "from-cyan-400 to-blue-500", shadow: "shadow-cyan-500/20", colSpan: "lg:col-span-1" },
    { title: "العناية المتقدمة بالجروح", desc: "تغيير على الجروح الجراحية باستخدام أحدث الغيارات.", icon: Cross, color: "from-rose-400 to-red-500", shadow: "shadow-rose-500/20", colSpan: "lg:col-span-1" },
    { title: "القسطرة البولية والأنبوب المعدي", desc: "تركيب وتغيير القسطرة البولية وأنبوب التغذية بعناية.", icon: FlaskConical, color: "from-orange-400 to-amber-500", shadow: "shadow-orange-500/20", colSpan: "lg:col-span-2" },
    { title: "رعاية كبار السن", desc: "برامج رعاية مخصصة لكبار السن تشمل النظافة والمتابعة.", icon: UserCheck, color: "from-purple-400 to-fuchsia-500", shadow: "shadow-purple-500/20", colSpan: "lg:col-span-1" },
    { title: "قياس العلامات الحيوية", desc: "قياس دقيق لضغط الدم، السكر، النبض، ونسبة الأكسجين.", icon: HeartPulse, color: "from-red-400 to-rose-500", shadow: "shadow-red-500/20", colSpan: "lg:col-span-1" }
  ] : [
    { title: "Comprehensive Nursing Visit", desc: "Full nursing care in the comfort of your home by highly qualified nurses.", icon: HeartHandshake, color: "from-blue-400 to-indigo-500", shadow: "shadow-blue-500/20", colSpan: "lg:col-span-2 lg:row-span-2" },
    { title: "IV & IM Injections", desc: "Administration of all types of injections with strict sterilization.", icon: Syringe, color: "from-emerald-400 to-teal-500", shadow: "shadow-emerald-500/20", colSpan: "lg:col-span-2" },
    { title: "Cannula & IV Fluids", desc: "Professional and painless insertion of IV cannulas and therapeutic fluids.", icon: Droplets, color: "from-cyan-400 to-blue-500", shadow: "shadow-cyan-500/20", colSpan: "lg:col-span-1" },
    { title: "Advanced Wound Care", desc: "Dressing surgical wounds using the latest medical dressings.", icon: Cross, color: "from-rose-400 to-red-500", shadow: "shadow-rose-500/20", colSpan: "lg:col-span-1" },
    { title: "Catheter & Feeding", desc: "Insertion and changing of catheters and feeding tubes with utmost care.", icon: FlaskConical, color: "from-orange-400 to-amber-500", shadow: "shadow-orange-500/20", colSpan: "lg:col-span-2" },
    { title: "Elderly Care", desc: "Tailored care programs for the elderly including hygiene and monitoring.", icon: UserCheck, color: "from-purple-400 to-fuchsia-500", shadow: "shadow-purple-500/20", colSpan: "lg:col-span-1" },
    { title: "Vitals Monitoring", desc: "Accurate measurement of blood pressure, blood sugar, pulse, and SpO2.", icon: HeartPulse, color: "from-red-400 to-rose-500", shadow: "shadow-red-500/20", colSpan: "lg:col-span-1" }
  ];

  return (
    <main className="min-h-screen bg-[#020408] text-slate-50 selection:bg-cyan-500/30 overflow-hidden" dir={isRTL ? 'rtl' : 'ltr'}>
      {/* Dynamic Background */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute top-1/4 left-1/4 w-[40vw] h-[40vw] bg-rose-500/5 blur-[120px] rounded-full mix-blend-screen" />
        <div className="absolute bottom-1/4 right-1/4 w-[40vw] h-[40vw] bg-cyan-500/5 blur-[120px] rounded-full mix-blend-screen" />
        <div className="absolute inset-0 bg-[url('/noise.svg')] opacity-20 mix-blend-overlay" />
      </div>

      <div ref={containerRef} className="relative z-10 w-full max-w-7xl mx-auto px-6 lg:px-12 pt-10 lg:pt-20 pb-24">
        
        {/* Navigation / Back Button */}
        <motion.a 
          href="/"
          className="inline-flex items-center gap-2 text-slate-400 hover:text-cyan-400 transition-colors mb-12 group cursor-pointer"
          initial={{ opacity: 0, x: isRTL ? 20 : -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5 }}
        >
          <ArrowLeft className={`w-5 h-5 transition-transform group-hover:${isRTL ? 'translate-x-1' : '-translate-x-1'} ${isRTL ? 'rotate-180' : ''}`} />
          <span className="font-medium">{content.backBtn}</span>
        </motion.a>

        {/* Hero Section */}
        <motion.div 
          className="text-center max-w-4xl mx-auto mb-20"
          style={{ y: headerY, opacity: headerOpacity }}
        >
          <motion.div 
            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-slate-800/60 border border-slate-700/50 text-slate-300 text-sm font-semibold mb-6 shadow-lg select-none"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            {content.badge}
          </motion.div>
          
          <motion.h1 
            className="text-4xl md:text-5xl lg:text-6xl font-black mb-6 leading-tight tracking-tight bg-gradient-to-b from-white via-slate-100 to-slate-400 bg-clip-text text-transparent"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            {content.title}
          </motion.h1>
          
          <motion.p 
            className="text-lg md:text-xl text-slate-400 leading-relaxed max-w-2xl mx-auto font-medium"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            {content.subtitle}
          </motion.p>
        </motion.div>

        {/* Section 1: Core Nursing & Home Care (Bento Grid) */}
        <div className="mb-32">
          <div className="flex items-center gap-4 mb-10">
            <div className="h-[2px] w-12 bg-gradient-to-r from-cyan-500 to-transparent" />
            <h2 className="text-2xl md:text-3xl font-bold text-white">
              {isRTL ? "خدمات الرعاية المنزلية والتمريض" : "Home Care & Nursing Services"}
            </h2>
            <div className="h-[2px] flex-1 bg-gradient-to-r from-slate-800 to-transparent opacity-50" />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6 auto-rows-fr">
            {coreServices.map((service, idx) => {
              const Icon = service.icon;
              return (
                <motion.div
                  key={idx}
                  className={`group relative overflow-hidden rounded-[2rem] bg-slate-900/40 backdrop-blur-xl border border-white/5 hover:border-white/10 transition-all duration-500 flex flex-col justify-between p-6 md:p-8 ${service.colSpan}`}
                  initial={{ opacity: 0, scale: 0.95 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true, margin: "-50px" }}
                  transition={{ duration: 0.5, delay: idx * 0.05 }}
                  whileHover={{ y: -5 }}
                >
                  <div className={`absolute inset-0 bg-gradient-to-br ${service.color} opacity-0 group-hover:opacity-5 transition-opacity duration-500`} />
                  
                  <div className="flex justify-between items-start mb-6">
                    <div className={`w-14 h-14 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center relative overflow-hidden group-hover:shadow-[0_0_30px_rgba(0,0,0,0)] group-hover:${service.shadow} transition-shadow duration-500`}>
                      <div className={`absolute inset-0 bg-gradient-to-br ${service.color} opacity-20`} />
                      <Icon className="w-7 h-7 text-white relative z-10 drop-shadow-lg" />
                    </div>
                    {/* Tiny visual pulse for the first big tile */}
                    {idx === 0 && (
                      <span className="flex h-3 w-3 relative">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-3 w-3 bg-cyan-500"></span>
                      </span>
                    )}
                  </div>

                  <div>
                    <h3 className={`text-xl md:text-2xl font-bold text-white mb-3 group-hover:text-transparent group-hover:bg-clip-text group-hover:bg-gradient-to-r ${service.color} transition-all duration-300`}>
                      {service.title}
                    </h3>
                    <p className={`text-slate-400 font-medium leading-relaxed ${idx === 0 ? "text-lg max-w-md" : "text-sm md:text-base"}`}>
                      {service.desc}
                    </p>
                  </div>
                  
                  {/* Glass reflection */}
                  <div className="absolute -inset-full top-0 z-0 block h-full w-1/2 -skew-x-12 transform bg-gradient-to-r from-transparent via-white/5 to-transparent opacity-0 group-hover:animate-shine" />
                </motion.div>
              );
            })}
          </div>
        </div>

        {/* Section 2: Exclusive Features (Tech innovations based on MIP) */}
        <div className="mb-20">
          <div className="flex items-center gap-4 mb-10">
            <div className="h-[2px] w-12 bg-gradient-to-r from-purple-500 to-transparent" />
            <h2 className="text-2xl md:text-3xl font-bold text-white flex items-center gap-3">
              <Star className="w-6 h-6 text-purple-400 fill-purple-400/20" />
              {isRTL ? "الابتكارات التقنية الحصرية" : "Exclusive Technological Innovations"}
            </h2>
            <div className="h-[2px] flex-1 bg-gradient-to-r from-slate-800 to-transparent opacity-50" />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {content.services.map((service, idx) => {
            const Icon = service.icon;
            return (
              <motion.div 
                key={idx}
                className="group relative p-8 rounded-[2rem] bg-slate-900/40 backdrop-blur-xl border border-white/5 overflow-hidden hover:bg-slate-800/40 transition-colors duration-500"
                initial={{ opacity: 0, y: 40 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-50px" }}
                transition={{ duration: 0.6, delay: idx * 0.1 }}
                whileHover={{ y: -5 }}
              >
                {/* Glow Effect */}
                <div className={`absolute top-0 ${isRTL ? 'right-0' : 'left-0'} w-32 h-32 ${service.bg} blur-3xl rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none`} />
                
                <div className={`w-14 h-14 rounded-2xl ${service.bg} border ${service.border} flex items-center justify-center mb-6 relative z-10 group-hover:scale-110 transition-transform duration-500`}>
                  <Icon className={`w-7 h-7 ${service.color}`} />
                </div>
                
                <h3 className="text-xl md:text-2xl font-bold text-white mb-4 relative z-10">
                  {service.title}
                </h3>
                
                <p className="text-slate-400 font-medium leading-relaxed relative z-10">
                  {service.desc}
                </p>
                
                {/* Highlight edge line */}
                <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-white/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
              </motion.div>
            )
          })}
        </div>
        </div>

      </div>
    </main>
  );
}
