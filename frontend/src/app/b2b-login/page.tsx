"use client";
import React, { useState, Suspense } from "react";
import dynamic from "next/dynamic";
import { motion } from "framer-motion";
import { Mail, Lock, ArrowLeft, Eye, EyeOff } from "lucide-react";

// Vercel Best Practice: bundle-dynamic-imports (Lazy load heavy 3D WebGL components)
const NetworkGlobe = dynamic(() => import("@/components/ui/network-globe").then(mod => mod.NetworkGlobe), { 
  ssr: false, 
  loading: () => (
    <div className="w-full max-w-[600px] aspect-square flex items-center justify-center">
      <div className="w-24 h-24 rounded-full border-b-2 border-cyan-500 animate-spin blur-[1px]"></div>
    </div>
  )
});

export default function B2BKineticLogin() {
  const [emailFocus, setEmailFocus] = useState(false);
  const [passFocus, setPassFocus] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  // Staggered animation variants
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.15,
        delayChildren: 0.8, // Wait for the globe's sweeping entrance
      },
    },
  };

  const itemFadeUp = {
    hidden: { opacity: 0, y: 30, filter: "blur(8px)" },
    visible: { 
      opacity: 1, 
      y: 0, 
      filter: "blur(0px)",
      transition: { type: "spring", stiffness: 300, damping: 24 } 
    },
  };

  return (
    <div className="min-h-screen w-full bg-[#050505] text-slate-100 flex flex-col lg:grid lg:grid-cols-2 overflow-hidden selection:bg-cyan-500/30" dir="rtl">
      
      {/* ─── LEFT HALF: 3D KINETIC NETWORK GLOBE (RTL End) ─── */}
      <motion.div 
        className="relative flex items-center justify-center p-8 lg:p-12 order-first lg:order-last h-[40vh] lg:h-full bg-gradient-to-l from-[#050505] to-[#0A0A1A] lg:border-r border-white/5"
        initial={{ opacity: 0, scale: 0.9, x: -50 }}
        animate={{ opacity: 1, scale: 1, x: 0 }}
        transition={{ duration: 1.5, ease: [0.16, 1, 0.3, 1] }}
      >
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(0,102,255,0.08)_0%,transparent_60%)] pointer-events-none" />
        
        {/* The 3D Component */}
        <div className="w-full max-w-[600px] aspect-square z-10 relative">
            <NetworkGlobe />
        </div>

        {/* Branding Overlay on Globe Side */}
        <div className="absolute inset-0 z-20 pointer-events-none p-8 lg:p-14 flex flex-col justify-end items-end hidden lg:flex">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 2, duration: 1 }}
            className="text-left"
          >
            <h3 className="text-xl font-medium tracking-wide text-cyan-400 opacity-80" style={{ fontFamily: "'Outfit', sans-serif" }}>WATEEN SECURE NETWORK</h3>
            <p className="text-sm text-slate-500 mt-2 max-w-sm ml-auto opacity-70">
              Encrypted quantum routing protocols active. Establishing secure connection to the central agency mainframe...
            </p>
          </motion.div>
        </div>
      </motion.div>

      {/* ─── RIGHT HALF: PREMIUM GLASSMORPHIC FORM (RTL Start) ─── */}
      <div className="relative flex items-center justify-center p-6 sm:p-12 lg:p-16 h-full order-last lg:order-first z-10">
        
        {/* Subtle background mesh gradient for depth */}
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-[0.03] pointer-events-none" />
        <div className="absolute -top-[20%] -right-[10%] w-[500px] h-[500px] rounded-full bg-blue-600/10 blur-[120px] pointer-events-none animate-pulse" style={{ animationDuration: '8s' }} />

        {/* Back to Home Button */}
        <a href="/" className="absolute top-8 right-8 flex items-center gap-2 text-sm font-medium text-slate-400 hover:text-white transition-colors group z-20">
          <ArrowLeft className="w-4 h-4 transform group-hover:-translate-x-1 transition-transform rotate-180" />
          العودة للرئيسية
        </a>

        {/* Form Container */}
        <motion.div 
          className="w-full max-w-[440px] relative z-10"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          {/* Decorative Logo */}
          <motion.div variants={itemFadeUp} className="mb-10 inline-flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 p-[1px] shadow-[0_0_20px_rgba(0,102,255,0.3)]">
                <div className="w-full h-full bg-[#050505] rounded-xl flex items-center justify-center backdrop-blur-xl">
                  <img src="/images/icon.svg" alt="Wateen" className="w-7 h-7 object-contain drop-shadow-md" />
                </div>
              </div>
              <div className="flex flex-col">
                <span className="text-3xl font-black bg-gradient-to-l from-white to-cyan-400 bg-clip-text text-transparent leading-none" style={{ fontFamily: "'Amiri', 'Outfit', sans-serif" }}>وَتِين</span>
                <span className="text-[13px] font-bold tracking-widest text-[#FFB300] leading-none mt-1 uppercase" style={{ fontFamily: "'Outfit', sans-serif" }}>AGENCY COMMAND</span>
              </div>
          </motion.div>

          <motion.h1 variants={itemFadeUp} className="text-3xl font-bold text-white mb-2" style={{ fontFamily: "'Amiri', 'Outfit', sans-serif" }}>
            تسجيل الدخول إلى الشبكة
          </motion.h1>
          <motion.p variants={itemFadeUp} className="text-slate-400 text-sm mb-10">
            أدخل بيانات الاعتماد الخاصة بمكتبك للوصول إلى مركز العمليات المشفرة.
          </motion.p>

          <motion.form variants={itemFadeUp} className="space-y-6" onSubmit={(e) => { e.preventDefault(); window.location.href = '/b2b'; }}>
            
            {/* Email Field */}
            <div className={`relative rounded-xl transition-all duration-300 ${emailFocus ? 'ring-2 ring-cyan-500/50 bg-cyan-500/5 shadow-[0_0_15px_rgba(0,229,255,0.15)]' : 'bg-white/5 border border-white/10 hover:border-white/20'}`}>
              <label htmlFor="emailAddress" className="sr-only">البريد الإلكتروني</label>
              <div className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none">
                <Mail className={`w-5 h-5 transition-colors ${emailFocus ? 'text-cyan-400' : 'text-slate-500'}`} />
              </div>
              <input
                id="emailAddress"
                type="email"
                required
                placeholder="البريد الإلكتروني"
                className="w-full bg-transparent text-white placeholder:text-slate-500 text-[15px] outline-none py-4 pr-12 pl-4 rounded-xl"
                onFocus={() => setEmailFocus(true)}
                onBlur={() => setEmailFocus(false)}
              />
            </div>

            {/* Password Field */}
            <div className={`relative rounded-xl transition-all duration-300 ${passFocus ? 'ring-2 ring-cyan-500/50 bg-cyan-500/5 shadow-[0_0_15px_rgba(0,229,255,0.15)]' : 'bg-white/5 border border-white/10 hover:border-white/20'}`}>
              <label htmlFor="userPassword" className="sr-only">كلمة المرور المشفرة</label>
              <div className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none">
                <Lock className={`w-5 h-5 transition-colors ${passFocus ? 'text-cyan-400' : 'text-slate-500'}`} />
              </div>
              <input
                id="userPassword"
                type={showPassword ? "text" : "password"}
                required
                placeholder="كلمة المرور المشفرة"
                className="w-full bg-transparent text-white placeholder:text-slate-500 text-[15px] outline-none py-4 pr-12 pl-14 rounded-xl font-mono tracking-wider"
                onFocus={() => setPassFocus(true)}
                onBlur={() => setPassFocus(false)}
              />
              <button 
                type="button" 
                onClick={() => setShowPassword(!showPassword)}
                className="absolute left-16 top-1/2 -translate-y-1/2 text-slate-500 hover:text-cyan-400 transition-colors p-1"
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
              <button type="button" className="absolute left-4 top-1/2 -translate-y-1/2 text-xs font-semibold text-cyan-500 hover:text-cyan-400 transition-colors">
                نسيت؟
              </button>
            </div>

            {/* Submit Button */}
            <motion.button
              variants={itemFadeUp}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="w-full py-4 rounded-xl font-bold text-[15px] text-white overflow-hidden relative group"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-blue-600 via-cyan-500 to-blue-600 bg-[length:200%_auto] group-hover:bg-[100%_center] transition-all duration-500" />
              {/* Glow effect */}
              <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 blur-xl bg-cyan-500/50" />
              <div className="absolute inset-0 shadow-[inset_0_1px_rgba(255,255,255,0.3)] rounded-xl pointer-events-none" />
              <span className="relative z-10 flex items-center justify-center gap-2">
                تسجيل الدخول <ArrowLeft className="w-4 h-4 rotate-180" />
              </span>
            </motion.button>
            
            <div className="relative flex items-center justify-center mt-6">
                <div className="absolute inset-x-0 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />
                <span className="relative z-10 bg-[#050505] px-4 text-xs font-medium text-slate-500 uppercase tracking-widest">أو التوصيل عبر</span>
            </div>

            {/* Google OAuth */}
            <motion.button
              variants={itemFadeUp}
              type="button"
              className="w-full py-4 rounded-xl flex items-center justify-center gap-3 bg-white/5 hover:bg-white/10 border border-white/5 hover:border-white/10 transition-all font-medium text-sm text-slate-300"
            >
              <svg viewBox="0 0 24 24" className="w-5 h-5 bg-white rounded-full p-0.5" xmlns="http://www.w3.org/2000/svg">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
              </svg>
              Google Workspace
            </motion.button>
          </motion.form>
        </motion.div>

        {/* Footer info bounds */}
        <div className="absolute bottom-6 w-full text-center z-10 hidden sm:block">
            <p className="text-[11px] text-slate-600 font-medium tracking-wide">
                2026 © WATEEN HEALTHCARE PLATFORM. ALL SECURE ROUTES MONITORED.
            </p>
        </div>
      </div>
    </div>
  );
}
