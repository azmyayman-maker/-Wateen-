"use client";

import React, { useRef } from "react";
import { motion, useScroll, useTransform } from "framer-motion";
import { Shield, Award, HeartPulse, GraduationCap, Users, ArrowLeft } from "lucide-react";
import { useLanguage } from "@/lib/i18n";

export default function AboutPage() {
  const { isRTL, t } = useLanguage();
  const containerRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end end"]
  });

  const headerY = useTransform(scrollYProgress, [0, 0.2], [0, -100]);
  const headerOpacity = useTransform(scrollYProgress, [0, 0.2], [1, 0]);

  // We are hardcoding some Arabic/English content here for optimal creative control 
  // without cluttering the main i18n file for this specific static marketing page.
  const content = {
    badge: isRTL ? "من نحن" : "About Us",
    title: isRTL ? "نخبة الرعاية الطبية في مكان واحد" : "The Elite of Medical Care in One Place",
    subtitle: isRTL 
      ? "نحن لا نقدم مجرد خدمة، نحن نرسخ معياراً جديداً للرعاية المنزلية في مصر عبر فريق من أمهر المهندسين وأفضل الكوادر الطبية وكوادر التمريض." 
      : "We don't just provide a service; we establish a new standard for home care in Egypt through a team of the most skilled engineers, top medical professionals, and nursing staff.",
    visionTitle: isRTL ? "رؤيتنا" : "Our Vision",
    visionText: isRTL 
      ? "أن نصبح المرجعية الأولى للرعاية الصحية المنزلية الموثوقة والآمنة."
      : "To become the premier reference for reliable and secure home healthcare.",
    stats: [
      { num: "+500", label: isRTL ? "ممرض معتمد" : "Certified Nurses", icon: Users },
      { num: "99%", label: isRTL ? "رضا المرضى" : "Patient Satisfaction", icon: HeartPulse },
      { num: "24/7", label: isRTL ? "دعم طبي ذكي" : "Smart Medical Support", icon: Shield },
    ],
    teamIntro: isRTL 
      ? "وراء كل ابتكار في واتين يقف فريق هندسي مبدع من أكفأ العقول في مجال التكنولوجيا وأفضل الكوادر الطبية من طواقم التمريض والرعاية المنزلية، يعملون بتناغم لضمان أعلى مستويات الأمان والجودة."
      : "Behind every innovation at Wateen stands a creative engineering team of the brightest minds in technology and top medical staff from nursing and home care teams, working in harmony to ensure the highest levels of safety and quality.",
    backBtn: isRTL ? "العودة للرئيسية" : "Back to Home"
  };

  return (
    <main className="min-h-screen bg-[#020408] text-slate-50 selection:bg-cyan-500/30 overflow-hidden" dir={isRTL ? 'rtl' : 'ltr'}>
      {/* Dynamic Background */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute top-0 right-1/4 w-[50vw] h-[50vw] bg-cyan-500/10 blur-[120px] rounded-full mix-blend-screen" />
        <div className="absolute bottom-0 left-1/4 w-[60vw] h-[60vw] bg-purple-500/10 blur-[150px] rounded-full mix-blend-screen" />
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
          className="text-center max-w-4xl mx-auto mb-24"
          style={{ y: headerY, opacity: headerOpacity }}
        >
          <motion.div 
            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-sm font-semibold mb-6 shadow-lg shadow-cyan-500/5 select-none"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Shield className="w-4 h-4" />
            {content.badge}
          </motion.div>
          
          <motion.h1 
            className="text-4xl md:text-5xl lg:text-7xl font-black mb-8 leading-tight tracking-tight bg-gradient-to-b from-white via-slate-200 to-slate-500 bg-clip-text text-transparent"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            {content.title}
          </motion.h1>
          
          <motion.p 
            className="text-lg md:text-xl lg:text-2xl text-slate-400 leading-relaxed max-w-3xl mx-auto font-medium"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            {content.subtitle}
          </motion.p>
        </motion.div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-32">
          {content.stats.map((stat, idx) => {
            const Icon = stat.icon;
            return (
              <motion.div 
                key={idx}
                className="relative p-8 rounded-3xl bg-slate-900/40 backdrop-blur-xl border border-white/5 overflow-hidden group"
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-100px" }}
                transition={{ duration: 0.5, delay: idx * 0.1 }}
                whileHover={{ y: -5, borderColor: "rgba(34,211,238,0.3)" }}
              >
                <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                <Icon className="w-10 h-10 text-cyan-400/50 mb-6 group-hover:text-cyan-400 group-hover:scale-110 transition-all duration-300" />
                <h3 className="text-4xl lg:text-5xl font-black text-white mb-2">{stat.num}</h3>
                <p className="text-slate-400 font-medium text-lg">{stat.label}</p>
              </motion.div>
            )
          })}
        </div>

        {/* The Team / Philosophy Section */}
        <motion.div 
          className="relative w-full rounded-[2.5rem] bg-gradient-to-br from-slate-900/80 to-[#020408] border border-white/5 p-8 md:p-16 lg:p-24 overflow-hidden"
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
        >
          {/* Abstract background elements inside the card */}
          <div className="absolute top-0 right-0 w-96 h-96 bg-cyan-500/10 blur-[100px] rounded-full pointer-events-none" />
          <div className="absolute bottom-0 left-0 w-96 h-96 bg-purple-500/10 blur-[100px] rounded-full pointer-events-none" />

          <div className="relative z-10 grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            <div>
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-cyan-400 to-emerald-400 p-0.5 mb-8 shadow-[0_0_30px_rgba(6,182,212,0.3)]">
                <div className="w-full h-full bg-slate-900 rounded-[15px] flex items-center justify-center">
                  <Award className="w-8 h-8 text-cyan-400" />
                </div>
              </div>
              <h2 className="text-3xl lg:text-5xl font-bold text-white mb-6 leading-tight">
                {isRTL ? "هندسة برمجية وطب يداً بيد" : "Software Engineering and Medicine, Hand in Hand"}
              </h2>
              <p className="text-lg text-slate-300 leading-relaxed font-medium">
                {content.teamIntro}
              </p>
              <div className="mt-10 flex flex-col gap-4">
                 {[
                  { title: isRTL ? "أكفاء المهندسين" : "Top-tier Engineers", desc: isRTL ? "بناء أنظمة مستقرة، مشفرة، وتعمل بذكاء لتلبية احتياجاتك اللحظية." : "Building stable, encrypted systems operating intelligently for your instant needs.", icon: GraduationCap },
                  { title: isRTL ? "أفضل الكوادر الطبية" : "Best Medical Staff", desc: isRTL ? "تمريض منزلي مدرب ومؤهل بأعلى المعايير، يخضع لتدقيق شامل (KYC)." : "Trained and highly qualified home care nurses, subject to rigorous KYC.", icon: Shield },
                 ].map((item, i) => (
                    <div key={i} className="flex gap-4 p-4 rounded-2xl bg-white/5 border border-white/5 hover:bg-white/10 transition-colors">
                      <div className="shrink-0 w-12 h-12 rounded-xl bg-cyan-500/20 flex items-center justify-center text-cyan-400">
                        <item.icon className="w-6 h-6" />
                      </div>
                      <div>
                        <h4 className="text-white font-bold text-lg mb-1">{item.title}</h4>
                        <p className="text-sm text-slate-400">{item.desc}</p>
                      </div>
                    </div>
                 ))}
              </div>
            </div>
            
            {/* Abstract visualizer acting as a placeholder for a team photo/graphic */}
            <div className="relative h-[400px] lg:h-[600px] rounded-3xl bg-slate-900/50 border border-white/5 overflow-hidden flex items-center justify-center">
                <motion.div 
                  className="w-64 h-64 border-[4px] border-cyan-500/20 rounded-full flex items-center justify-center"
                  animate={{ rotate: 360, scale: [1, 1.05, 1] }}
                  transition={{ rotate: { duration: 20, repeat: Infinity, ease: "linear" }, scale: { duration: 5, repeat: Infinity, ease: "easeInOut" } }}
                >
                  <motion.div 
                    className="w-48 h-48 border-[2px] border-purple-500/30 rounded-full border-dashed"
                    animate={{ rotate: -360 }}
                    transition={{ duration: 15, repeat: Infinity, ease: "linear" }}
                  />
                </motion.div>
                <div className="absolute inset-0 bg-gradient-to-t from-slate-900 via-transparent to-transparent opacity-80" />
                <div className="absolute bottom-8 left-8 right-8 text-center text-slate-400 font-medium tracking-wide">
                  WATEEN &copy; {new Date().getFullYear()}
                </div>
            </div>
          </div>
        </motion.div>
      </div>
    </main>
  );
}
