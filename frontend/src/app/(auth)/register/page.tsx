"use client";

import React, { useState, useEffect, useMemo, Suspense } from "react";
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { Button, Input } from '@/components/shared';
import { 
  User, 
  Stethoscope, 
  Mail, 
  Lock, 
  Phone, 
  IdCard, 
  BriefcaseMedical, 
  UploadCloud, 
  CheckCircle2, 
  ChevronRight,
  ChevronLeft,
  Calendar,
  Eye,
  EyeOff,
  ShieldCheck,
  Check,
  X,
  Plus,
  Minus,
  CalendarDays
} from 'lucide-react';

import { DatePickerWheel } from '@/components/shared/DatePickerWheel';

const animationStyles = `
  @keyframes registerFadeInUp {
    0% { opacity: 0; transform: translateY(28px) scale(0.97); filter: blur(6px); }
    100% { opacity: 1; transform: translateY(0) scale(1); filter: blur(0); }
  }
  .register-entrance {
    animation: registerFadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  }
  
  /* Hide scrollbar for clean look */
  .no-scrollbar::-webkit-scrollbar {
    display: none;
  }
  .no-scrollbar {
    -ms-overflow-style: none;  /* IE and Edge */
    scrollbar-width: none;  /* Firefox */
  }
`;

type Role = 'patient' | 'nurse';

// Reusable animated input wrapper
const AnimatedInput = ({ children, delay = 0 }: { children: React.ReactNode, delay?: number }) => (
  <motion.div
    initial={{ opacity: 0, y: 10 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0, scale: 0.95, filter: 'blur(4px)' }}
    transition={{ duration: 0.3, delay }}
  >
    {children}
  </motion.div>
);

function RegisterContent() {
  const searchParams = useSearchParams();
  const initialIdentifier = searchParams.get("identifier") || "";
  
  const [phone, setPhone] = useState(initialIdentifier && !initialIdentifier.includes('@') ? initialIdentifier : "");
  const [email, setEmail] = useState(initialIdentifier && initialIdentifier.includes('@') ? initialIdentifier : "");
  const [mounted, setMounted] = useState(false);
  const [role, setRole] = useState<Role>('patient');
  const [dob, setDob] = useState<Date>(new Date(2000, 0, 1));
  const [step, setStep] = useState<1 | 2 | 3>(1);
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [nationalIdFile, setNationalIdFile] = useState<File | null>(null);
  const [nationalIdBackFile, setNationalIdBackFile] = useState<File | null>(null);
  const [syndicateFile, setSyndicateFile] = useState<File | null>(null);

  // --- Secondary Contact States ---
  const [secondaryPhones, setSecondaryPhones] = useState<{id: string, phone: string, owner: string, relation: string}[]>([]);

  const [showSecondaryEmail, setShowSecondaryEmail] = useState(false);
  const [secondaryEmail, setSecondaryEmail] = useState('');
  const [secondaryEmailOwner, setSecondaryEmailOwner] = useState('');
  const [secondaryEmailRelation, setSecondaryEmailRelation] = useState('');

  // Password validation rules
  const passwordRules = useMemo(() => [
    { id: 'length', label: 'لا يقل عن 8 أحرف', test: (p: string) => p.length >= 8 },
    { id: 'uppercase', label: 'يحتوي على حرف كبير (A-Z)', test: (p: string) => /[A-Z]/.test(p) },
    { id: 'lowercase', label: 'يحتوي على حرف صغير (a-z)', test: (p: string) => /[a-z]/.test(p) },
    { id: 'number', label: 'يحتوي على رقم (0-9)', test: (p: string) => /[0-9]/.test(p) },
    { id: 'special', label: 'يحتوي على رمز خاص (!@#$...)', test: (p: string) => /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(p) },
  ], []);

  const allRulesPassed = useMemo(() => 
    passwordRules.every(rule => rule.test(password)) && password === confirmPassword && confirmPassword.length > 0,
    [password, confirmPassword, passwordRules]
  );

  const passwordStrength = useMemo(() => {
    const passed = passwordRules.filter(rule => rule.test(password)).length;
    if (passed <= 1) return { label: 'ضعيفة', color: 'bg-red-500', width: '20%' };
    if (passed <= 2) return { label: 'مقبولة', color: 'bg-orange-500', width: '40%' };
    if (passed <= 3) return { label: 'متوسطة', color: 'bg-yellow-500', width: '60%' };
    if (passed <= 4) return { label: 'جيدة', color: 'bg-cyan-500', width: '80%' };
    return { label: 'ممتازة', color: 'bg-emerald-500', width: '100%' };
  }, [password, passwordRules]);

  useEffect(() => {
    setMounted(true);
  }, []);

  // Handle file selection (mock placeholder)
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>, setter: React.Dispatch<React.SetStateAction<File | null>>) => {
    if (e.target.files && e.target.files[0]) {
      setter(e.target.files[0]);
    }
  };

  return (
    <>
      <style dangerouslySetInnerHTML={{ __html: animationStyles }} />
      <div className="w-full max-w-lg mx-auto py-8">
        <div
          className={`
            relative overflow-hidden
            bg-slate-900/40 backdrop-blur-2xl
            border border-slate-700/50
            rounded-[2.5rem] 
            p-8 sm:p-10
            transition-all duration-700
            ${mounted ? "register-entrance" : "opacity-0"}
          `}
          style={{
            boxShadow: `
              0 25px 50px -12px rgba(0, 0, 0, 0.5),
              inset 0 1px 1px rgba(255, 255, 255, 0.1),
              0 0 0 1px rgba(255, 255, 255, 0.05)
            `,
          }}
        >
          {/* Subtle panel edge highlight */}
          <div
            className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-cyan-500/30 to-transparent"
            aria-hidden="true"
          />
          
          {/* Ambient Glows */}
          <div className="absolute top-0 right-0 -mr-20 -mt-20 w-64 h-64 rounded-full bg-cyan-500/10 blur-[80px] pointer-events-none" />
          <div className="absolute bottom-0 left-0 -ml-20 -mb-20 w-64 h-64 rounded-full bg-purple-500/10 blur-[80px] pointer-events-none" />

          <div className="text-center mb-8 relative z-10">
            <h1 className="text-2xl sm:text-3xl font-bold text-white mb-2">
              {step === 1 ? 'إنشاء حساب جديد' : step === 2 ? 'تأمين حسابك' : 'البيانات المهنية (مقدم الخدمة)'}
            </h1>
            <p className="text-slate-400 text-sm">
              {step === 1 ? 'انضم إلى واتين — الرعاية الصحية في خدمتك' : step === 2 ? 'الخطوة الأخيرة — اختر كلمة مرور قوية' : 'توثيق الهوية لضمان جودة الخدمة والبدء في تلقي الطلبات'}
            </p>
          </div>

          {/* Role Selector - only on step 1 */}
          {step === 1 && (
          <div className="relative z-10 p-1 bg-slate-800/50 rounded-2xl flex mb-8 border border-white/5 shadow-inner">
            <button
              type="button"
              onClick={() => setRole('patient')}
              className={`relative flex-1 py-3 text-sm font-medium rounded-xl transition-colors duration-200 z-10 flex items-center justify-center gap-2 ${role === 'patient' ? 'text-white' : 'text-slate-400 hover:text-white'}`}
            >
              <User className="w-4 h-4" />
              <span>طالب خدمة</span>
              {role === 'patient' && (
                <motion.div
                  layoutId="active-role-pill"
                  className="absolute inset-0 bg-gradient-to-r from-cyan-600 to-cyan-500 rounded-xl -z-10 shadow-lg shadow-cyan-500/20"
                  transition={{ type: "spring", stiffness: 300, damping: 25 }}
                />
              )}
            </button>
            <button
              type="button"
              onClick={() => setRole('nurse')}
              className={`relative flex-1 py-3 text-sm font-medium rounded-xl transition-colors duration-200 z-10 flex items-center justify-center gap-2 ${role === 'nurse' ? 'text-white' : 'text-slate-400 hover:text-white'}`}
            >
              <Stethoscope className="w-4 h-4" />
              <span>مقدم خدمة</span>
              {role === 'nurse' && (
                <motion.div
                  layoutId="active-role-pill"
                  className="absolute inset-0 bg-gradient-to-r from-purple-600 to-purple-500 rounded-xl -z-10 shadow-lg shadow-purple-500/20"
                  transition={{ type: "spring", stiffness: 300, damping: 25 }}
                />
              )}
            </button>
          </div>
          )}
          
          {step === 1 && (
          <>
          {/* Form Container */}
          <div className="relative z-10 max-h-[70vh] overflow-y-auto overflow-x-hidden no-scrollbar pb-4 -mx-4 px-4 sm:-mx-6 sm:px-6">
            <form 
              onSubmit={(e) => {
                e.preventDefault();
                // TODO: Add actual submission logic here later
              }}
              className="space-y-5 [&_label]:text-slate-300 [&_label]:font-medium [&_label]:text-sm"
            >
              <AnimatePresence mode="wait">
                <motion.div 
                  key={role}
                  initial={{ opacity: 0, x: role === 'patient' ? -20 : 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: role === 'patient' ? 20 : -20 }}
                  transition={{ duration: 0.3, ease: "easeInOut" }}
                  className="space-y-5"
                >
                  {/* Shared Fields */}
                  <AnimatedInput delay={0.05}>
                    <div className="relative group">
                      <Input
                        label="الاسم بالكامل (كما في الهوية الرسمية)"
                        type="text"
                        required
                        placeholder="أدخل اسمك"
                        className="pl-12 bg-slate-900/50 border-slate-700/50 focus:border-cyan-400/80 focus:ring-2 focus:ring-cyan-500/10 transition-all text-white placeholder:text-slate-500 shadow-inner focus:scale-[1.01]"
                      />
                      <User className="absolute left-3 top-9 w-4 h-4 text-slate-500 group-focus-within:text-cyan-400 transition-colors" />
                    </div>
                  </AnimatedInput>
                  
                  <AnimatedInput delay={0.1}>
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <label className="text-slate-300 font-medium text-sm px-1">رقم الهاتف المحمول (أساسي للتواصل)*</label>
                        {secondaryPhones.length < 9 && (
                          <button type="button" onClick={() => setSecondaryPhones([...secondaryPhones, { id: Date.now().toString() + Math.random(), phone: '', owner: '', relation: '' }])} className="flex items-center gap-1 text-xs text-cyan-400 hover:text-cyan-300 transition-colors px-2 py-1 rounded-lg bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/20">
                            <Plus className="w-3 h-3" /> أضف رقم إضافي
                          </button>
                        )}
                      </div>
                      <div className="relative group">
                        <input
                          type="tel"
                          required
                          value={phone}
                          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setPhone(e.target.value)}
                          placeholder="+20 1XX XXX XXXX"
                          className="w-full h-10 px-3 pl-12 rounded-md bg-slate-900/50 border border-slate-700/50 focus:border-cyan-400/80 focus:ring-2 focus:ring-cyan-500/10 transition-all text-white placeholder:text-slate-500 shadow-inner focus:scale-[1.01] focus:outline-none"
                          dir="ltr"
                        />
                        <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 group-focus-within:text-cyan-400 transition-colors" />
                      </div>
                    </div>
                  </AnimatedInput>

                  <AnimatePresence>
                    {secondaryPhones.map((contact, index) => (
                      <motion.div
                        key={contact.id}
                        initial={{ opacity: 0, height: 0, overflow: 'hidden' }}
                        animate={{ opacity: 1, height: 'auto', overflow: 'visible' }}
                        exit={{ opacity: 0, height: 0, overflow: 'hidden' }}
                        className="space-y-4 pt-1"
                      >
                        <div className="p-4 rounded-xl bg-slate-800/30 border border-slate-700/50 space-y-4 relative">
                          <div className="flex items-center justify-between mb-1">
                            <label className="text-slate-300 font-medium text-sm">رقم إضافي {index + 1}</label>
                            <button type="button" onClick={() => {
                              setSecondaryPhones(secondaryPhones.filter(c => c.id !== contact.id));
                            }} className="flex items-center gap-1 text-xs text-rose-400 hover:text-rose-300 transition-colors px-2 py-1 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/20">
                              <Minus className="w-3 h-3" /> إزالة
                            </button>
                          </div>
                          
                          <div className="relative group">
                            <input
                              type="tel"
                              required
                              value={contact.phone}
                              onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                                const newPhones = [...secondaryPhones];
                                newPhones[index].phone = e.target.value;
                                setSecondaryPhones(newPhones);
                              }}
                              placeholder="+20 1XX XXX XXXX (رقم إضافي)"
                              className="w-full h-10 px-3 pl-12 rounded-md bg-slate-900/50 border border-slate-700/50 focus:border-cyan-400/80 focus:ring-2 focus:ring-cyan-500/10 transition-all text-white placeholder:text-slate-500 shadow-inner focus:scale-[1.01] focus:outline-none"
                              dir="ltr"
                            />
                            <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 group-focus-within:text-cyan-400 transition-colors" />
                          </div>

                          {role === 'patient' && (
                            <div className="grid grid-cols-2 gap-3 pt-2">
                              <div>
                                <label className="text-slate-300 text-xs mb-1.5 block text-cyan-50">لمن هذا الرقم؟*</label>
                                <input
                                  type="text"
                                  required
                                  value={contact.owner}
                                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                                    const newPhones = [...secondaryPhones];
                                    newPhones[index].owner = e.target.value;
                                    setSecondaryPhones(newPhones);
                                  }}
                                  placeholder="الاسم"
                                  className="w-full h-9 px-3 rounded-md bg-slate-900/50 border border-slate-700/50 focus:border-cyan-400/80 focus:ring-1 focus:ring-cyan-500/10 transition-all text-white placeholder:text-slate-500 text-sm focus:outline-none"
                                />
                              </div>
                              <div>
                                <label className="text-slate-300 text-xs mb-1.5 block text-cyan-50">صلة القرابة*</label>
                                <input
                                  type="text"
                                  required
                                  value={contact.relation}
                                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                                    const newPhones = [...secondaryPhones];
                                    newPhones[index].relation = e.target.value;
                                    setSecondaryPhones(newPhones);
                                  }}
                                  placeholder="أب، أخت..."
                                  className="w-full h-9 px-3 rounded-md bg-slate-900/50 border border-slate-700/50 focus:border-cyan-400/80 focus:ring-1 focus:ring-cyan-500/10 transition-all text-white placeholder:text-slate-500 text-sm focus:outline-none"
                                />
                              </div>
                            </div>
                          )}
                        </div>
                      </motion.div>
                    ))}
                  </AnimatePresence>

                  <AnimatedInput delay={0.15}>
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <label className="text-slate-300 font-medium text-sm px-1">البريد الإلكتروني (لإرسال التقارير والإشعارات)*</label>
                        {!showSecondaryEmail && (
                          <button type="button" onClick={() => setShowSecondaryEmail(true)} className="flex items-center gap-1 text-xs text-cyan-400 hover:text-cyan-300 transition-colors px-2 py-1 rounded-lg bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/20">
                            <Plus className="w-3 h-3" /> أضف بريد إضافي
                          </button>
                        )}
                      </div>
                      <div className="relative group">
                        <input
                          type="email"
                          required
                          value={email}
                          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setEmail(e.target.value)}
                          placeholder="example@wateen.live"
                          className="w-full h-10 px-3 pl-12 rounded-md bg-slate-900/50 border border-slate-700/50 focus:border-cyan-400/80 focus:ring-2 focus:ring-cyan-500/10 transition-all text-white placeholder:text-slate-500 shadow-inner focus:scale-[1.01] focus:outline-none"
                          dir="ltr"
                        />
                        <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 group-focus-within:text-cyan-400 transition-colors" />
                      </div>
                    </div>
                  </AnimatedInput>

                  <AnimatePresence>
                    {showSecondaryEmail && (
                      <motion.div
                        initial={{ opacity: 0, height: 0, overflow: 'hidden' }}
                        animate={{ opacity: 1, height: 'auto', overflow: 'visible' }}
                        exit={{ opacity: 0, height: 0, overflow: 'hidden' }}
                        className="space-y-4 pt-1"
                      >
                        <div className="p-4 rounded-xl bg-slate-800/30 border border-slate-700/50 space-y-4">
                          <div className="flex items-center justify-between mb-1">
                            <label className="text-slate-300 font-medium text-sm">بريد إضافي (اختياري)</label>
                            <button type="button" onClick={() => {setShowSecondaryEmail(false); setSecondaryEmail(''); setSecondaryEmailOwner(''); setSecondaryEmailRelation('');}} className="flex items-center gap-1 text-xs text-rose-400 hover:text-rose-300 transition-colors px-2 py-1 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/20">
                              <Minus className="w-3 h-3" /> إزالة
                            </button>
                          </div>
                          
                          <div className="relative group">
                            <input
                              type="email"
                              value={secondaryEmail}
                              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSecondaryEmail(e.target.value)}
                              placeholder="extra@wateen.live"
                              className="w-full h-10 px-3 pl-12 rounded-md bg-slate-900/50 border border-slate-700/50 focus:border-cyan-400/80 focus:ring-2 focus:ring-cyan-500/10 transition-all text-white placeholder:text-slate-500 shadow-inner focus:scale-[1.01] focus:outline-none"
                              dir="ltr"
                            />
                            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 group-focus-within:text-cyan-400 transition-colors" />
                          </div>

                          {role === 'patient' && (
                            <div className="grid grid-cols-2 gap-3 pt-2">
                              <div>
                                <label className="text-slate-300 text-xs mb-1.5 block">لمن هذا البريد؟</label>
                                <input
                                  type="text"
                                  value={secondaryEmailOwner}
                                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSecondaryEmailOwner(e.target.value)}
                                  placeholder="اسم الشخص"
                                  className="w-full h-9 px-3 rounded-md bg-slate-900/50 border border-slate-700/50 focus:border-cyan-400/80 focus:ring-1 focus:ring-cyan-500/10 transition-all text-white placeholder:text-slate-500 text-sm focus:outline-none"
                                />
                              </div>
                              <div>
                                <label className="text-slate-300 text-xs mb-1.5 block">صلة القرابة</label>
                                <input
                                  type="text"
                                  value={secondaryEmailRelation}
                                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSecondaryEmailRelation(e.target.value)}
                                  placeholder="مثال: أب، زوجة..."
                                  className="w-full h-9 px-3 rounded-md bg-slate-900/50 border border-slate-700/50 focus:border-cyan-400/80 focus:ring-1 focus:ring-cyan-500/10 transition-all text-white placeholder:text-slate-500 text-sm focus:outline-none"
                                />
                              </div>
                            </div>
                          )}
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>

                  {/* Birth Date Picker */}
                  <AnimatedInput delay={0.15}>
                    <div className="relative group flex flex-col items-start w-full">
                      <label className="text-slate-300 font-medium text-sm mb-2 px-1 flex items-center gap-2">
                        <CalendarDays className="w-4 h-4 text-cyan-400" />
                        تاريخ الميلاد*
                      </label>
                      <DatePickerWheel 
                        date={dob} 
                        onChange={setDob} 
                        className="w-full"
                        minYear={1920}
                        maxYear={new Date().getFullYear() - 18}
                      />
                    </div>
                  </AnimatedInput>



                </motion.div>
              </AnimatePresence>

              <div className="pt-6 relative z-10 bg-transparent">
                <Button 
                  type="button" 
                  onClick={() => setStep(2)}
                  className={`
                    w-full h-14 text-base font-bold text-white border-0 
                    transition-all duration-300 hover:scale-[1.02] active:scale-[0.98]
                    flex items-center justify-center gap-2 group
                    ${role === 'patient' 
                      ? 'bg-gradient-to-l from-cyan-600 to-emerald-500 shadow-lg shadow-cyan-500/25 hover:shadow-cyan-500/40 hover:from-cyan-500 hover:to-emerald-400' 
                      : 'bg-gradient-to-l from-purple-600 to-indigo-500 shadow-lg shadow-purple-500/25 hover:shadow-purple-500/40 hover:from-purple-500 hover:to-indigo-400'}
                  `}
                >
                  <span>التالي — إنشاء كلمة المرور</span>
                  <ChevronRight className="w-5 h-5 rtl:rotate-180 transition-transform group-hover:-translate-x-1" />
                </Button>
              </div>
            </form>
          </div>
          </>
          )}

        {/* ════════════════════ Step 2: Password Creation ════════════════════ */}
        {step === 2 && (
          <motion.div
            key="step-2"
            initial={{ opacity: 0, x: 40 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -40 }}
            transition={{ duration: 0.35, ease: 'easeInOut' }}
            className="relative z-10 space-y-6"
          >
            {/* Header */}
            <div className="text-center space-y-2">
              <div className="mx-auto w-14 h-14 rounded-2xl bg-gradient-to-br from-cyan-500/20 to-emerald-500/20 border border-cyan-500/30 flex items-center justify-center mb-3">
                <ShieldCheck className="w-7 h-7 text-cyan-400" />
              </div>
              <h3 className="text-xl font-bold text-white">إنشاء كلمة مرور آمنة</h3>
              <p className="text-sm text-slate-400">اختر كلمة مرور قوية لحماية حسابك على المنصة</p>
            </div>

            {/* Password Input */}
            <div className="space-y-4">
              <div className="relative group">
                <label className="text-slate-300 font-medium text-sm mb-2 block px-1">كلمة المرور الجديدة*</label>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="أدخل كلمة المرور"
                    dir="ltr"
                    className="w-full h-14 pl-12 pr-12 rounded-2xl bg-slate-900/50 border border-slate-700/50 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/20 outline-none transition-all text-white placeholder:text-slate-500 text-base"
                  />
                  <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500 group-focus-within:text-cyan-400 transition-colors" />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500 hover:text-cyan-400 transition-colors"
                    tabIndex={-1}
                  >
                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
              </div>

              {/* Strength Bar */}
              {password.length > 0 && (
                <motion.div
                  initial={{ opacity: 0, y: -5 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="space-y-1.5"
                >
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-slate-400">قوة كلمة المرور</span>
                    <span className={`text-xs font-semibold ${passwordStrength.color.replace('bg-', 'text-')}`}>{passwordStrength.label}</span>
                  </div>
                  <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                    <motion.div
                      className={`h-full rounded-full ${passwordStrength.color}`}
                      initial={{ width: 0 }}
                      animate={{ width: passwordStrength.width }}
                      transition={{ duration: 0.4, ease: 'easeOut' }}
                    />
                  </div>
                </motion.div>
              )}

              {/* Validation Rules Checklist */}
              <div className="bg-slate-800/30 rounded-2xl p-4 border border-slate-700/30 space-y-2">
                <p className="text-xs text-slate-400 font-medium mb-2">يجب أن تتحقق كلمة المرور من الشروط التالية:</p>
                {passwordRules.map((rule) => {
                  const passed = rule.test(password);
                  return (
                    <motion.div
                      key={rule.id}
                      className="flex items-center gap-2.5"
                      animate={{ opacity: 1 }}
                    >
                      <div className={`w-5 h-5 rounded-full flex items-center justify-center shrink-0 transition-all duration-300 ${
                        passed 
                          ? 'bg-emerald-500/20 border border-emerald-500/50' 
                          : 'bg-slate-700/50 border border-slate-600/50'
                      }`}>
                        {passed 
                          ? <Check className="w-3 h-3 text-emerald-400" /> 
                          : <X className="w-3 h-3 text-slate-500" />
                        }
                      </div>
                      <span className={`text-sm transition-colors duration-300 ${
                        passed ? 'text-emerald-300' : 'text-slate-400'
                      }`}>
                        {rule.label}
                      </span>
                    </motion.div>
                  );
                })}
              </div>

              {/* Confirm Password */}
              <div className="relative group">
                <label className="text-slate-300 font-medium text-sm mb-2 block px-1">تأكيد كلمة المرور*</label>
                <div className="relative">
                  <input
                    type={showConfirmPassword ? 'text' : 'password'}
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="أعد إدخال كلمة المرور"
                    dir="ltr"
                    className={`w-full h-14 pl-12 pr-12 rounded-2xl bg-slate-900/50 border outline-none transition-all text-white placeholder:text-slate-500 text-base ${
                      confirmPassword.length > 0
                        ? password === confirmPassword
                          ? 'border-emerald-500/50 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500/20'
                          : 'border-red-500/50 focus:border-red-500 focus:ring-1 focus:ring-red-500/20'
                        : 'border-slate-700/50 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/20'
                    }`}
                  />
                  <CheckCircle2 className={`absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 transition-colors ${
                    confirmPassword.length > 0 && password === confirmPassword
                      ? 'text-emerald-400'
                      : 'text-slate-500 group-focus-within:text-cyan-400'
                  }`} />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500 hover:text-cyan-400 transition-colors"
                    tabIndex={-1}
                  >
                    {showConfirmPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
                {confirmPassword.length > 0 && password !== confirmPassword && (
                  <motion.p 
                    initial={{ opacity: 0, y: -5 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-xs text-red-400 mt-1.5 px-1"
                  >
                    كلمتا المرور غير متطابقتين
                  </motion.p>
                )}
                {confirmPassword.length > 0 && password === confirmPassword && (
                  <motion.p 
                    initial={{ opacity: 0, y: -5 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-xs text-emerald-400 mt-1.5 px-1"
                  >
                    ✓ كلمتا المرور متطابقتان
                  </motion.p>
                )}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3 pt-2">
              <button
                type="button"
                onClick={() => setStep(1)}
                className="flex items-center justify-center gap-1.5 px-5 h-14 rounded-2xl bg-slate-800/50 border border-slate-700/50 text-slate-300 hover:text-white hover:border-slate-600 transition-all text-sm font-medium"
              >
                <ChevronLeft className="w-4 h-4" />
                <span>رجوع</span>
              </button>
              <Button 
                type={role === 'patient' ? "submit" : "button"}
                onClick={() => {
                  if (role === 'nurse') setStep(3);
                }}
                disabled={!allRulesPassed}
                className={`
                  flex-1 h-14 text-base font-bold text-white border-0 
                  transition-all duration-300 
                  flex items-center justify-center gap-2 group
                  ${!allRulesPassed 
                    ? 'opacity-40 cursor-not-allowed bg-slate-700' 
                    : role === 'patient'
                      ? 'hover:scale-[1.02] active:scale-[0.98] bg-gradient-to-l from-cyan-600 to-emerald-500 shadow-lg shadow-cyan-500/25 hover:shadow-cyan-500/40'
                      : 'hover:scale-[1.02] active:scale-[0.98] bg-gradient-to-l from-purple-600 to-indigo-500 shadow-lg shadow-purple-500/25 hover:shadow-purple-500/40'
                  }
                `}
              >
                <span>{role === 'patient' ? 'إنشاء حساب مستخدم' : 'التالي — استكمال البيانات'}</span>
                {role === 'patient' ? (
                  <ShieldCheck className="w-5 h-5 transition-transform group-hover:scale-110" />
                ) : (
                  <ChevronRight className="w-5 h-5 rtl:rotate-180 transition-transform group-hover:-translate-x-1" />
                )}
              </Button>
            </div>
          </motion.div>
        )}

        {/* ════════════════════ Step 3: Nurse Professional Data ════════════════════ */}
        {step === 3 && role === 'nurse' && (
          <motion.div
            key="step-3"
            initial={{ opacity: 0, x: 40 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -40 }}
            transition={{ duration: 0.35, ease: 'easeInOut' }}
            className="relative z-10 space-y-6"
          >
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
              <AnimatedInput delay={0.1}>
                <div className="relative group">
                  <Input
                    label="الرقم القومي (المدون بالبطاقة الشخصية)"
                    type="text"
                    required
                    placeholder="14 رقم"
                    className="pl-10 bg-slate-900/50 border-slate-700/50 focus:border-purple-500 focus:ring-purple-500/20 transition-all text-white placeholder:text-slate-500"
                    dir="ltr"
                  />
                  <IdCard className="absolute left-3 top-9 w-4 h-4 text-slate-500 group-focus-within:text-purple-400 transition-colors" />
                </div>
              </AnimatedInput>

              <AnimatedInput delay={0.15}>
                <div className="relative group">
                  <Input
                    label="رقم القيد النقابي / ترخيص مزاولة المهنة"
                    type="text"
                    required
                    placeholder="أدخل رقم النقابة"
                    className="pl-10 bg-slate-900/50 border-slate-700/50 focus:border-purple-500 focus:ring-purple-500/20 transition-all text-white placeholder:text-slate-500"
                    dir="ltr"
                  />
                  <IdCard className="absolute left-3 top-9 w-4 h-4 text-slate-500 group-focus-within:text-purple-400 transition-colors" />
                </div>
              </AnimatedInput>
            </div>

            {/* Optional KYC Uploads */}
            <AnimatedInput delay={0.2}>
              <div className="bg-slate-800/30 rounded-2xl p-5 border border-slate-700/50">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h4 className="text-sm font-medium text-white mb-1">توثيق الهوية والمؤهلات (KYC)</h4>
                    <p className="text-xs text-slate-400">يمكنك تخطي هذه الخطوة حالياً، ولكنها إلزامية لاعتماد حسابك وبدء تقديم خدماتك الطبية.</p>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  {/* National ID Front Upload */}
                  <label className="relative flex flex-col items-center justify-center p-4 border-2 border-dashed border-slate-600 rounded-xl hover:border-purple-400 hover:bg-slate-800/50 transition-all cursor-pointer group">
                    <input type="file" className="hidden" accept="image/*,.pdf" onChange={(e) => handleFileChange(e, setNationalIdFile)} />
                    <UploadCloud className="w-8 h-8 text-slate-400 group-hover:text-purple-400 transition-colors mb-2" />
                    <span className="text-xs text-slate-300 font-medium text-center">
                      {nationalIdFile ? nationalIdFile.name : 'صورة البطاقة القومية (الوجه الأمامي)'}
                    </span>
                    {!nationalIdFile && <span className="text-[10px] text-slate-500 mt-1">PNG, JPG or PDF</span>}
                  </label>

                  {/* National ID Back Upload */}
                  <label className="relative flex flex-col items-center justify-center p-4 border-2 border-dashed border-slate-600 rounded-xl hover:border-purple-400 hover:bg-slate-800/50 transition-all cursor-pointer group">
                    <input type="file" className="hidden" accept="image/*,.pdf" onChange={(e) => handleFileChange(e, setNationalIdBackFile)} />
                    <UploadCloud className="w-8 h-8 text-slate-400 group-hover:text-purple-400 transition-colors mb-2" />
                    <span className="text-xs text-slate-300 font-medium text-center">
                      {nationalIdBackFile ? nationalIdBackFile.name : 'صورة البطاقة القومية (الوجه الخلفي)'}
                    </span>
                    {!nationalIdBackFile && <span className="text-[10px] text-slate-500 mt-1">PNG, JPG or PDF</span>}
                  </label>

                  {/* Syndicate Card Upload */}
                  <label className="relative flex flex-col items-center justify-center p-4 border-2 border-dashed border-slate-600 rounded-xl hover:border-purple-400 hover:bg-slate-800/50 transition-all cursor-pointer group">
                    <input type="file" className="hidden" accept="image/*,.pdf" onChange={(e) => handleFileChange(e, setSyndicateFile)} />
                    <UploadCloud className="w-8 h-8 text-slate-400 group-hover:text-purple-400 transition-colors mb-2" />
                    <span className="text-xs text-slate-300 font-medium text-center">
                      {syndicateFile ? syndicateFile.name : 'صورة بطاقة القيد بالنقابة المهنية'}
                    </span>
                    {!syndicateFile && <span className="text-[10px] text-slate-500 mt-1">PNG, JPG or PDF</span>}
                  </label>
                </div>
              </div>
            </AnimatedInput>

            {/* Action Buttons */}
            <div className="flex gap-3 pt-2">
              <button
                type="button"
                onClick={() => setStep(2)}
                className="flex items-center justify-center gap-1.5 px-5 h-14 rounded-2xl bg-slate-800/50 border border-slate-700/50 text-slate-300 hover:text-white hover:border-slate-600 transition-all text-sm font-medium"
              >
                <ChevronLeft className="w-4 h-4" />
                <span>رجوع</span>
              </button>
              
              <button
                type="submit"
                onClick={(e) => {
                  e.preventDefault(); // In a real app, this would submit without KYC
                  console.log("Skipping KYC...");
                }}
                className="flex items-center justify-center gap-1.5 px-5 h-14 rounded-2xl bg-slate-800/50 border border-slate-700/50 text-slate-300 hover:text-white hover:border-slate-600 transition-all text-sm font-medium"
              >
                <span>تخطي</span>
              </button>

              <Button 
                type="submit"
                className={`
                  flex-1 h-14 text-base font-bold text-white border-0 
                  transition-all duration-300 hover:scale-[1.02] active:scale-[0.98]
                  flex items-center justify-center gap-2 group
                  bg-gradient-to-l from-purple-600 to-indigo-500 shadow-lg shadow-purple-500/25 hover:shadow-purple-500/40
                `}
              >
                <span>تقديم طلب الانضمام</span>
                <CheckCircle2 className="w-5 h-5 transition-transform group-hover:scale-110" />
              </Button>
            </div>
          </motion.div>
        )}

        {/* Step Indicator Dots */}
        <div className="flex items-center justify-center gap-2 pt-4">
          {(role === 'nurse' ? [1, 2, 3] : [1, 2]).map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => setStep(s as 1 | 2 | 3)}
              className={`rounded-full transition-all duration-300 ${
                step === s
                  ? `w-8 h-2.5 ${role === 'patient' ? 'bg-cyan-500' : 'bg-purple-500'}`
                  : 'w-2.5 h-2.5 bg-slate-600 hover:bg-slate-500'
              }`}
              aria-label={`الخطوة ${s}`}
            />
          ))}
        </div>

          <div className="mt-8 text-center relative z-10 pt-4 border-t border-slate-700/50">
            <p className="text-sm text-slate-400 flex items-center justify-center gap-1.5">
              <span>لديك حساب بالفعل؟</span>
              <Link 
                href="/login" 
                className={`font-medium transition-colors hover:underline underline-offset-4 flex items-center ${role === 'patient' ? 'text-cyan-400 hover:text-cyan-300' : 'text-purple-400 hover:text-purple-300'}`}
              >
                سجل دخولك من هنا
              </Link>
            </p>
          </div>
        </div>
      </div>
    </>
  );
}

export default function RegisterPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center"><div className="w-12 h-12 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin" /></div>}>
      <RegisterContent />
    </Suspense>
  );
}
