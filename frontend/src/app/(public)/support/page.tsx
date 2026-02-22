"use client";

import React, { useRef } from "react";
import { motion } from "framer-motion";
import { Mail, ArrowLeft, HeadphonesIcon } from "lucide-react";
import { useLanguage } from "@/lib/i18n";

export default function SupportPage() {
  const { isRTL } = useLanguage();

  const content = {
    badge: isRTL ? "الدعم الفني" : "Technical Support",
    title: isRTL ? "نحن هنا لمساعدتك دائماً" : "We Are Always Here to Help",
    subtitle: isRTL 
      ? "تواصل مع فريق الدعم المخصص لمنصة واتين لحل أي مشكلة أو الإجابة على استفساراتك بأسرع وقت ممكن." 
      : "Contact the dedicated Wateen support team to resolve any issues or answer your inquiries as quickly as possible.",
    backBtn: isRTL ? "العودة للرئيسية" : "Back to Home",
    emailAction: isRTL ? "أرسل لنا رسالة" : "Send us a message",
    emailAddress: "support@wateen.live"
  };

  return (
    <main className="min-h-screen bg-[#020408] text-slate-50 selection:bg-cyan-500/30 overflow-hidden flex flex-col" dir={isRTL ? 'rtl' : 'ltr'}>
      {/* Background */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[80vw] h-[80vw] max-w-[800px] max-h-[800px] bg-blue-500/10 blur-[150px] rounded-full mix-blend-screen" />
        <div className="absolute inset-0 bg-[url('/noise.svg')] opacity-20 mix-blend-overlay" />
      </div>

      <div className="relative z-10 w-full max-w-4xl mx-auto px-6 lg:px-12 flex-1 flex flex-col justify-center py-10">
        
        {/* Navigation / Back Button */}
        <motion.div 
          className="absolute top-10 left-6 right-6 lg:left-12 lg:right-12"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <a 
            href="/"
            className="inline-flex items-center gap-2 text-slate-400 hover:text-cyan-400 transition-colors group cursor-pointer w-fit"
          >
            <ArrowLeft className={`w-5 h-5 transition-transform group-hover:${isRTL ? 'translate-x-1' : '-translate-x-1'} ${isRTL ? 'rotate-180' : ''}`} />
            <span className="font-medium">{content.backBtn}</span>
          </a>
        </motion.div>

        {/* Content Box */}
        <motion.div 
          className="w-full bg-slate-900/40 backdrop-blur-2xl border border-white/10 rounded-[2.5rem] p-8 md:p-16 text-center relative overflow-hidden"
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
        >
          {/* Inner ambient glow */}
          <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-blue-400/50 to-transparent" />
          
          <motion.div 
            className="w-20 h-20 md:w-24 md:h-24 mx-auto rounded-full bg-blue-500/10 border border-blue-500/20 flex items-center justify-center mb-8 relative"
            animate={{ y: [-5, 5, -5] }}
            transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
          >
            <div className="absolute inset-0 bg-blue-400/20 rounded-full blur-xl" />
            <HeadphonesIcon className="w-10 h-10 md:w-12 md:h-12 text-blue-400 relative z-10" />
          </motion.div>

          <h1 className="text-3xl md:text-4xl lg:text-5xl font-black mb-4 text-white">
            {content.title}
          </h1>
          
          <p className="text-lg md:text-xl text-slate-400 mb-12 max-w-xl mx-auto leading-relaxed">
            {content.subtitle}
          </p>

          {/* Email Action Button */}
          <motion.a 
            href={`mailto:${content.emailAddress}`}
            className="inline-flex items-center gap-4 px-8 py-4 rounded-2xl bg-gradient-to-r from-blue-600 to-cyan-600 text-white font-bold text-lg md:text-xl shadow-[0_10px_30px_-10px_rgba(37,99,235,0.5)] hover:shadow-[0_20px_40px_-10px_rgba(37,99,235,0.7)] transition-all duration-300 group"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Mail className="w-6 h-6 group-hover:animate-bounce" />
            <span>{content.emailAction}</span>
          </motion.a>
          
          <div className="mt-8 font-mono text-slate-500 text-sm md:text-base">
            {content.emailAddress}
          </div>
        </motion.div>

      </div>
    </main>
  );
}
