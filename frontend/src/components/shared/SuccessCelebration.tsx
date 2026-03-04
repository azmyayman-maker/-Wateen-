"use client";

import React, { useEffect, useState, useCallback } from "react";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import { useLanguage } from "@/lib/i18n";

// ─── CSS Confetti Animation ──────────────────────────────────────────────────
const confettiStyles = `
  @keyframes confettiFall {
    0% {
      transform: translateY(-100vh) rotate(0deg) scale(1);
      opacity: 1;
    }
    70% {
      opacity: 1;
    }
    100% {
      transform: translateY(100vh) rotate(720deg) scale(0.3);
      opacity: 0;
    }
  }
  @keyframes countdownRing {
    from { stroke-dashoffset: 0; }
    to { stroke-dashoffset: 157; }
  }
  .confetti-piece {
    position: fixed;
    top: -20px;
    z-index: 100;
    pointer-events: none;
  }
`;

const CONFETTI_COLORS = [
  "#06B6D4", "#8B5CF6", "#10B981", "#F59E0B", "#EF4444",
  "#EC4899", "#3B82F6", "#14B8A6", "#F97316", "#6366F1",
];

interface SuccessCelebrationProps {
  role: "patient" | "nurse";
  userName?: string;
  redirectTo?: string;
  redirectDelay?: number;
}

export default function SuccessCelebration({
  role,
  userName,
  redirectTo,
  redirectDelay = 3500,
}: SuccessCelebrationProps) {
  const router = useRouter();
  const { t } = useLanguage();
  const [showContent, setShowContent] = useState(false);

  const isPatient = role === "patient";
  const accentGradient = isPatient
    ? "from-cyan-500 to-emerald-400"
    : "from-purple-500 to-indigo-400";
  const accentShadow = isPatient
    ? "shadow-cyan-500/30"
    : "shadow-purple-500/30";
  const accentText = isPatient ? "text-cyan-400" : "text-purple-400";

  useEffect(() => {
    const timer = setTimeout(() => setShowContent(true), 200);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    if (redirectTo) {
      const timer = setTimeout(() => {
        router.push(redirectTo);
      }, redirectDelay);
      return () => clearTimeout(timer);
    }
  }, [redirectTo, redirectDelay, router]);

  // Generate confetti pieces
  const confettiPieces = Array.from({ length: 35 }, (_, i) => ({
    id: i,
    left: `${Math.random() * 100}%`,
    delay: `${Math.random() * 2}s`,
    duration: `${2.5 + Math.random() * 2}s`,
    color: CONFETTI_COLORS[i % CONFETTI_COLORS.length],
    size: 6 + Math.random() * 8,
    rotation: Math.random() * 360,
  }));

  return (
    <>
      <style dangerouslySetInnerHTML={{ __html: confettiStyles }} />

      {/* Confetti Layer */}
      {confettiPieces.map((piece) => (
        <div
          key={piece.id}
          className="confetti-piece"
          style={{
            left: piece.left,
            width: `${piece.size}px`,
            height: `${piece.size * 0.6}px`,
            backgroundColor: piece.color,
            borderRadius: piece.id % 3 === 0 ? "50%" : "2px",
            animation: `confettiFall ${piece.duration} ease-in ${piece.delay} forwards`,
            transform: `rotate(${piece.rotation}deg)`,
          }}
        />
      ))}

      {/* Main Content */}
      <div className="w-full max-w-md mx-auto text-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.8, y: 30 }}
          animate={showContent ? { opacity: 1, scale: 1, y: 0 } : {}}
          transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
          className={`
            relative overflow-hidden
            bg-slate-900/50 backdrop-blur-2xl
            border border-slate-700/50
            rounded-[2.5rem] 
            p-10 sm:p-12
          `}
          style={{
            boxShadow: `
              0 25px 50px -12px rgba(0, 0, 0, 0.5),
              inset 0 1px 1px rgba(255, 255, 255, 0.1),
              0 0 0 1px rgba(255, 255, 255, 0.05)
            `,
          }}
        >
          {/* Top edge highlight */}
          <div
            className={`absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-${isPatient ? 'cyan' : 'purple'}-500/40 to-transparent`}
            aria-hidden="true"
          />

          {/* Ambient Glows */}
          <div className={`absolute top-0 right-0 -mr-20 -mt-20 w-64 h-64 rounded-full ${isPatient ? 'bg-cyan-500/15' : 'bg-purple-500/15'} blur-[80px] pointer-events-none`} />
          <div className={`absolute bottom-0 left-0 -ml-20 -mb-20 w-64 h-64 rounded-full ${isPatient ? 'bg-emerald-500/10' : 'bg-indigo-500/10'} blur-[80px] pointer-events-none`} />

          {/* Checkmark Circle */}
          <motion.div
            initial={{ scale: 0, rotate: -180 }}
            animate={showContent ? { scale: 1, rotate: 0 } : {}}
            transition={{ delay: 0.3, duration: 0.6, type: "spring", stiffness: 200, damping: 15 }}
            className={`
              mx-auto w-24 h-24 rounded-full 
              bg-gradient-to-br ${accentGradient}
              flex items-center justify-center
              shadow-2xl ${accentShadow}
              mb-6
            `}
          >
            <motion.svg
              viewBox="0 0 24 24"
              className="w-12 h-12 text-white"
              initial={{ pathLength: 0 }}
              animate={showContent ? { pathLength: 1 } : {}}
              transition={{ delay: 0.7, duration: 0.5, ease: "easeOut" }}
            >
              <motion.path
                d="M5 13l4 4L19 7"
                fill="none"
                stroke="currentColor"
                strokeWidth="3"
                strokeLinecap="round"
                strokeLinejoin="round"
                initial={{ pathLength: 0 }}
                animate={{ pathLength: 1 }}
                transition={{ delay: 0.7, duration: 0.5, ease: "easeOut" }}
              />
            </motion.svg>
          </motion.div>

          {/* Welcome Text */}
          <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={showContent ? { opacity: 1, y: 0 } : {}}
            transition={{ delay: 0.6, duration: 0.5 }}
            className="space-y-3 relative z-10"
          >
            <h2 className="text-2xl sm:text-3xl font-bold text-white">
              {t.register.successTitle}
            </h2>
            {userName && (
              <p className={`text-lg font-medium ${accentText}`}>
                {userName} 👋
              </p>
            )}
            <p className="text-slate-400 text-sm leading-relaxed">
              {t.register.successDesc}
            </p>
          </motion.div>

          {/* Countdown Ring */}
          {redirectTo && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={showContent ? { opacity: 1 } : {}}
              transition={{ delay: 1, duration: 0.4 }}
              className="mt-8 flex flex-col items-center gap-2"
            >
              <div className="relative w-10 h-10">
                <svg className="w-full h-full -rotate-90" viewBox="0 0 56 56">
                  <circle
                    cx="28"
                    cy="28"
                    r="25"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="3"
                    className="text-slate-700"
                  />
                  <circle
                    cx="28"
                    cy="28"
                    r="25"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="3"
                    strokeDasharray="157"
                    className={accentText}
                    style={{
                      animation: `countdownRing ${redirectDelay}ms linear forwards`,
                    }}
                  />
                </svg>
              </div>
              <p className="text-xs text-slate-500">{t.register.redirecting}</p>
            </motion.div>
          )}
        </motion.div>
      </div>
    </>
  );
}
