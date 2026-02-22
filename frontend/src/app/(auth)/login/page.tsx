"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import Image from "next/image";
import { useRouter } from "next/navigation";

// ─── SVG Icons (Lucide-style inlined for zero-dep) ────────────────────────────
const PhoneIcon = ({ className = "w-5 h-5" }: { className?: string }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.8"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
  >
    <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" />
  </svg>
);

const LockIcon = ({ className = "w-4 h-4" }: { className?: string }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
  >
    <rect width="18" height="11" x="3" y="11" rx="2" ry="2" />
    <path d="M7 11V7a5 5 0 0 1 10 0v4" />
  </svg>
);

const ArrowLeftIcon = ({ className = "w-5 h-5" }: { className?: string }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
  >
    <path d="m12 19-7-7 7-7" />
    <path d="M19 12H5" />
  </svg>
);

const ShieldCheckIcon = ({ className = "w-4 h-4" }: { className?: string }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
  >
    <path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z" />
    <path d="m9 12 2 2 4-4" />
  </svg>
);

// ─── CSS Animations ───────────────────────────────────────────────────────────
const animationStyles = `
  @keyframes loginFadeInUp {
    0% {
      opacity: 0;
      transform: translateY(28px) scale(0.97);
      filter: blur(6px);
    }
    100% {
      opacity: 1;
      transform: translateY(0) scale(1);
      filter: blur(0);
    }
  }
  @keyframes loginShimmer {
    0% { background-position: -200% center; }
    100% { background-position: 200% center; }
  }
  @keyframes loginGlow {
    0%, 100% { box-shadow: 0 0 20px rgba(6, 182, 212, 0.15), 0 0 60px rgba(6, 182, 212, 0.05); }
    50% { box-shadow: 0 0 30px rgba(6, 182, 212, 0.25), 0 0 80px rgba(6, 182, 212, 0.1); }
  }
  @keyframes loginFloatBreathing {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-3px); }
  }
  .login-entrance {
    animation: loginFadeInUp 1s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    opacity: 0;
  }
  .login-entrance-delay-1 { animation-delay: 0.15s; }
  .login-entrance-delay-2 { animation-delay: 0.3s; }
  .login-entrance-delay-3 { animation-delay: 0.45s; }
  .login-entrance-delay-4 { animation-delay: 0.6s; }
  .login-entrance-delay-5 { animation-delay: 0.75s; }
`;

// ─── Component ────────────────────────────────────────────────────────────────
export default function LoginPage() {
  const router = useRouter();
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [step, setStep] = useState<1 | 2>(1);
  const [isFocused, setIsFocused] = useState(false);
  const [mounted, setMounted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const handleIdentifierChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    // If it looks like a phone number (mostly digits), strip non-digits.
    // If it has letters or '@', treat as email/username.
    const val = e.target.value;
    if (/^[0-9+]*$/.test(val)) {
      setIdentifier(val.replace(/\D/g, "").slice(0, 11));
    } else {
      setIdentifier(val);
    }
  };

  const isEmail = identifier.includes("@") && identifier.includes(".");
  const isPhone = /^\d{10,11}$/.test(identifier);
  const isValidIdentifier = isEmail || isPhone;

  const handleIdentifierSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!isValidIdentifier || isLoading) return;

    setIsLoading(true);
    // Mock API Check
    setTimeout(() => {
      setIsLoading(false);
      // IF identifier starts with 11 or 10 or 011 or 010 or has admin -> mock EXISTS
      const userExists =
        identifier.startsWith("11") ||
        identifier.startsWith("10") ||
        identifier.startsWith("011") ||
        identifier.startsWith("010") ||
        identifier.includes("admin");

      if (userExists) {
        setStep(2); // Ask for password
      } else {
        // Redirect to register with identifier
        router.push(`/register?identifier=${encodeURIComponent(identifier)}`);
      }
    }, 800);
  };

  const handleLoginSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!password || isLoading) return;

    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      // Mock successful login
      router.push("/dashboard");
    }, 1000);
  };

  return (
    <>
      <style dangerouslySetInnerHTML={{ __html: animationStyles }} />

      <div className="w-full max-w-md mx-auto">
        {/* ─── THE FLOATING GLASSMORPHIC AUTH PANEL ─── */}
        <div
          className={`
            relative overflow-hidden
            bg-white/[0.07] backdrop-blur-2xl
            border border-white/[0.15]
            rounded-[2.5rem] 
            p-8 sm:p-10
            transition-all duration-700
            ${mounted ? "login-entrance" : "opacity-0"}
          `}
          style={{
            boxShadow: `
              0 25px 50px -12px rgba(0, 0, 0, 0.5),
              inset 0 1px 1px rgba(255, 255, 255, 0.15),
              0 0 0 1px rgba(255, 255, 255, 0.05)
            `,
          }}
        >
          {/* ── Subtle panel edge highlight ── */}
          <div
            className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/30 to-transparent"
            aria-hidden="true"
          />

          {/* ─── HEADER: Logo + Greeting ─── */}
          <div className="text-center mb-8 login-entrance login-entrance-delay-1">
            <div
              className={`mx-auto transition-all duration-500 relative ${step === 2 ? 'w-16 h-16 mb-4' : 'w-20 h-20 mb-5'}`}
              style={{ animation: "loginFloatBreathing 5s ease-in-out infinite 1.5s" }}
            >
              <div className="absolute inset-0 rounded-full bg-cyan-500/20 blur-xl" aria-hidden="true" />
              <Image
                src="/images/icon.svg"
                alt="شعار وتين"
                fill
                className="relative z-10 drop-shadow-2xl object-contain"
                priority
              />
            </div>

            <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-wide leading-relaxed transition-all">
              {step === 1 ? (
                <>مرحباً بك في{" "}
                <span className="text-transparent bg-clip-text bg-gradient-to-l from-cyan-400 to-purple-400">
                  وَتِين
                </span></>
              ) : 'مرحباً بعودتك!'}
            </h1>
            <p className="mt-2 text-sm text-white/50 font-light transition-all">
              {step === 1 ? 'منصة الرعاية الصحية المنزلية' : identifier}
            </p>
          </div>

          {/* ─── AUTH FORM ─── */}
          <form
            onSubmit={step === 1 ? handleIdentifierSubmit : handleLoginSubmit}
            className="space-y-6 relative"
          >
            {/* Step 1: Identifier Input */}
            <div className={`transition-all duration-500 transform ${step === 1 ? 'opacity-100 translate-x-0 relative z-10' : 'opacity-0 -translate-x-10 absolute inset-0 pointer-events-none'}`}>
              <div className="login-entrance login-entrance-delay-2">
                <label
                  htmlFor="identifier-input"
                  className="block text-sm font-medium text-white/70 mb-2.5"
                >
                  <span className="flex items-center gap-2">
                    <PhoneIcon className="w-4 h-4 text-cyan-400" />
                    رقم الهاتف المحمول أو البريد الإلكتروني
                  </span>
                </label>

                <div
                  className={`
                    relative flex items-center
                    bg-slate-900/50 
                    border rounded-xl h-14
                    transition-all duration-300 ease-out
                    ${
                      isFocused && step === 1
                        ? "border-cyan-400/80 ring-2 ring-cyan-500/20 shadow-[0_0_25px_rgba(6,182,212,0.15),inset_0_0_10px_rgba(6,182,212,0.05)] scale-[1.01]"
                        : "border-white/10 hover:border-white/20"
                    }
                  `}
                >
                    <input
                    id="identifier-input"
                    type="text"
                    dir={identifier ? "ltr" : "rtl"}
                    autoComplete="username"
                    placeholder="مثال: 01xxxxxxxxx أو البريد الإلكتروني"
                    value={identifier}
                    onChange={handleIdentifierChange}
                    onFocus={() => setIsFocused(true)}
                    onBlur={() => setIsFocused(false)}
                    className={`
                      w-full h-full pl-14 pr-4
                      bg-transparent text-white text-base
                      placeholder:text-white/20
                      focus:outline-none
                      tracking-wide font-medium
                      rounded-xl
                    `}
                    aria-label="أدخل المُعرّف الخاص بك"
                  />

                  {/* Validation Indicator */}
                  {identifier.length > 0 && (
                    <div className="absolute left-5 top-1/2 -translate-y-1/2">
                      <div
                        className={`
                          w-2.5 h-2.5 rounded-full transition-all duration-500
                          ${isValidIdentifier ? "bg-emerald-400 shadow-[0_0_12px_rgba(52,211,153,0.6)]" : "bg-white/10"}
                        `}
                      />
                    </div>
                  )}
                </div>
              </div>

              {/* ─── CTA BUTTON STEP 1 ─── */}
              <div className="login-entrance login-entrance-delay-3 mt-6">
                <button
                  type="submit"
                  disabled={!isValidIdentifier || isLoading}
                  className={`
                    group relative w-full h-14 
                    rounded-xl overflow-hidden
                    text-white font-bold text-base tracking-wide
                    transition-all duration-300 ease-out
                    cursor-pointer
                    focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-500
                    ${
                      isValidIdentifier && !isLoading
                        ? "bg-gradient-to-l from-cyan-500 to-purple-600 shadow-lg shadow-cyan-500/25 hover:shadow-xl hover:shadow-cyan-500/30 hover:scale-[1.02] active:scale-[0.98]"
                        : "bg-slate-700/50 cursor-not-allowed opacity-60"
                    }
                  `}
                  style={
                    isValidIdentifier && !isLoading
                      ? { animation: "loginGlow 3s ease-in-out infinite 2s" }
                      : undefined
                  }
                >
                  {isValidIdentifier && !isLoading && (
                    <div
                      className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                      style={{
                        background:
                          "linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.1) 50%, transparent 100%)",
                        backgroundSize: "200% 100%",
                        animation: "loginShimmer 2s linear infinite",
                      }}
                      aria-hidden="true"
                    />
                  )}
                  <span className="relative z-10 flex items-center justify-center gap-3">
                    {isLoading ? "جاري التحقق..." : "المتابعة"}
                    {!isLoading && <ArrowLeftIcon className="w-5 h-5 transition-transform duration-300 group-hover:-translate-x-1" />}
                  </span>
                </button>
              </div>

              {/* ─── SOCIAL SEPARATOR ─── */}
              <div className="login-entrance login-entrance-delay-4 flex items-center gap-4 my-6">
                <div className="flex-1 h-px bg-gradient-to-l from-white/15 to-transparent" />
                <span className="text-xs text-white/25 font-light">أو</span>
                <div className="flex-1 h-px bg-gradient-to-r from-white/15 to-transparent" />
              </div>

              {/* ─── GOOGLE SIGN IN ─── */}
              <div className="login-entrance login-entrance-delay-4">
                <button
                  type="button"
                  className="
                    w-full h-12 rounded-xl
                    bg-white/[0.06] hover:bg-white/[0.1]
                    border border-white/10 hover:border-white/20
                    text-white/70 hover:text-white
                    text-sm font-medium
                    transition-all duration-300
                    flex items-center justify-center gap-3
                    cursor-pointer
                  "
                >
                  <svg viewBox="0 0 24 24" className="w-5 h-5" aria-hidden="true">
                    <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4" />
                    <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
                    <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05" />
                    <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335" />
                  </svg>
                  المتابعة مع Google
                </button>
              </div>
            </div>

            {/* Step 2: Password Input */}
            <div className={`transition-all duration-500 transform ${step === 2 ? 'opacity-100 translate-x-0 relative z-10' : 'opacity-0 translate-x-10 absolute inset-0 pointer-events-none'}`}>
              <div>
                <label
                  htmlFor="password-input"
                  className="block text-sm font-medium text-white/70 mb-2.5"
                >
                  <span className="flex items-center gap-2">
                    <LockIcon className="w-4 h-4 text-purple-400" />
                    كلمة المرور
                  </span>
                </label>

                <div
                  className={`
                    relative flex items-center
                    bg-slate-900/50 
                    border rounded-xl h-14
                    transition-all duration-300 ease-out
                    ${
                      isFocused && step === 2
                        ? "border-purple-500 ring-1 ring-purple-500/50 shadow-[0_0_20px_rgba(168,85,247,0.15)]"
                        : "border-white/10 hover:border-white/20"
                    }
                  `}
                >
                  <input
                    id="password-input"
                    type="password"
                    dir="ltr"
                    autoComplete="current-password"
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    onFocus={() => setIsFocused(true)}
                    onBlur={() => setIsFocused(false)}
                    className={`
                      w-full h-full px-4
                      bg-transparent text-white text-base
                      placeholder:text-white/20
                      focus:outline-none
                      tracking-widest font-medium
                      rounded-xl
                    `}
                    aria-label="أدخل كلمة المرور"
                  />
                </div>
              </div>

              <div className="flex items-center justify-between mt-4 mb-6 px-1">
                <button
                   type="button"
                   onClick={() => setStep(1)}
                   className="text-xs text-white/50 hover:text-white transition-colors flex items-center gap-1"
                >
                  <ArrowLeftIcon className="w-3 h-3 rotate-180" />
                  تعديل المُعرّف
                </button>
                <Link
                  href="/forgot-password"
                  className="text-xs text-purple-400/80 hover:text-purple-400 underline underline-offset-2 transition-colors"
                >
                  نسيت كلمة المرور؟
                </Link>
              </div>

              {/* ─── CTA BUTTON STEP 2 ─── */}
              <div>
                <button
                  type="submit"
                  disabled={!password || isLoading}
                  className={`
                    group relative w-full h-14 
                    rounded-xl overflow-hidden
                    text-white font-bold text-base tracking-wide
                    transition-all duration-300 ease-out
                    cursor-pointer
                    focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-purple-500
                    ${
                      password && !isLoading
                        ? "bg-gradient-to-l from-purple-500 to-indigo-600 shadow-lg shadow-purple-500/25 hover:shadow-xl hover:shadow-purple-500/30 hover:scale-[1.02] active:scale-[0.98]"
                        : "bg-slate-700/50 cursor-not-allowed opacity-60"
                    }
                  `}
                >
                  <span className="relative z-10 flex items-center justify-center gap-3">
                    {isLoading ? "جاري الدخول..." : "تسجيل الدخول"}
                    {!isLoading && <ArrowLeftIcon className="w-5 h-5 transition-transform duration-300 group-hover:-translate-x-1" />}
                  </span>
                </button>
              </div>
            </div>
          </form>

          {/* ─── FOOTER ─── */}
          <div className="mt-8 login-entrance login-entrance-delay-5">
            {/* Security Badge */}
            <div className="flex items-center justify-center gap-2 text-white/25 text-xs">
              <ShieldCheckIcon className="w-3.5 h-3.5 text-emerald-400/60" />
              <span>اتصال مشفّر وآمن بالكامل</span>
              <LockIcon className="w-3 h-3 text-white/20" />
            </div>

            {/* Terms */}
            <p className="mt-3 text-center text-[11px] text-white/20 leading-relaxed">
              بالمتابعة، أنت توافق على{" "}
              <Link
                href="/terms"
                className="text-cyan-400/50 hover:text-cyan-400/80 underline underline-offset-2 transition-colors"
              >
                شروط الاستخدام
              </Link>{" "}
              و{" "}
              <Link
                href="/privacy"
                className="text-cyan-400/50 hover:text-cyan-400/80 underline underline-offset-2 transition-colors"
              >
                سياسة الخصوصية
              </Link>
            </p>
          </div>
        </div>

        {/* ─── BRAND WATERMARK (below panel) ─── */}
        <div className="mt-6 text-center login-entrance login-entrance-delay-5">
          <p className="text-xs text-white/15 tracking-widest font-light">
            WATEEN HEALTHCARE © {new Date().getFullYear()}
          </p>
        </div>
      </div>
    </>
  );
}
