'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useVisitSocket } from '@/hooks/useVisitSocket';

/**
 * T045: ActiveVisitNurse — Post-acceptance nurse view for an active visit.
 * Shows patient details, navigation button, and status transition buttons.
 * Transitions: EN_ROUTE → ARRIVED → IN_PROGRESS → COMPLETED
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

interface ActiveVisitNurseProps {
  visitId: string;
  patientName: string;
  patientAddress: string;
  patientPhone?: string;
  serviceType: string;
  onCompleted?: () => void;
}

const STATUS_FLOW = [
  { key: 'EN_ROUTE', label: 'في الطريق', icon: '🚗', color: 'from-blue-500 to-cyan-500' },
  { key: 'ARRIVED', label: 'وصلت', icon: '📍', color: 'from-amber-500 to-orange-500' },
  { key: 'IN_PROGRESS', label: 'جاري التنفيذ', icon: '💉', color: 'from-purple-500 to-pink-500' },
  { key: 'COMPLETED', label: 'تم الإنتهاء', icon: '✅', color: 'from-emerald-500 to-green-500' },
];

export default function ActiveVisitNurse({
  visitId,
  patientName,
  patientAddress,
  patientPhone,
  serviceType,
  onCompleted,
}: ActiveVisitNurseProps) {
  const { status } = useVisitSocket(visitId);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const currentStep = STATUS_FLOW[currentStepIndex];
  const nextStep = STATUS_FLOW[currentStepIndex + 1];
  const isLastStep = currentStepIndex >= STATUS_FLOW.length - 1;

  const transitionToNext = async () => {
    if (isTransitioning || !nextStep) return;
    setIsTransitioning(true);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/v1/visits/${visitId}/transition/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ new_status: nextStep.key }),
      });

      if (response.ok) {
        setCurrentStepIndex((i) => i + 1);
        if (nextStep.key === 'COMPLETED') {
          onCompleted?.();
        }
      } else {
        const data = await response.json().catch(() => ({}));
        setError(data.detail || 'فشل تحديث الحالة');
      }
    } catch {
      setError('خطأ في الاتصال');
    } finally {
      setIsTransitioning(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#050505] text-white p-6" dir="rtl">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold mb-1">الزيارة النشطة</h1>
        <p className="text-sm text-slate-400">{serviceType}</p>
      </div>

      {/* Patient Info Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white/5 border border-white/10 rounded-2xl p-5 mb-6"
      >
        <h2 className="text-lg font-bold text-white mb-3">{patientName}</h2>
        <div className="space-y-2">
          <div className="flex items-start gap-3">
            <span className="text-slate-400 mt-0.5">📍</span>
            <p className="text-sm text-slate-300">{patientAddress}</p>
          </div>
          {patientPhone && (
            <div className="flex items-center gap-3">
              <span className="text-slate-400">📞</span>
              <a href={`tel:${patientPhone}`} className="text-sm text-cyan-400 hover:underline">
                {patientPhone}
              </a>
            </div>
          )}
        </div>

        {/* Navigate Button */}
        <motion.a
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(patientAddress)}`}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-4 w-full py-3 rounded-xl font-bold text-sm text-white flex items-center justify-center gap-2 bg-gradient-to-l from-blue-600 to-cyan-600"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          فتح الملاحة
        </motion.a>
      </motion.div>

      {/* Status Progress */}
      <div className="mb-8">
        <h3 className="text-sm font-semibold text-slate-400 mb-4">مراحل الزيارة</h3>
        <div className="space-y-3">
          {STATUS_FLOW.map((step, index) => {
            const isDone = index < currentStepIndex;
            const isCurrent = index === currentStepIndex;

            return (
              <motion.div
                key={step.key}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className={`flex items-center gap-3 p-3 rounded-xl transition-all ${
                  isCurrent
                    ? 'bg-white/10 border border-white/20'
                    : isDone
                    ? 'bg-emerald-500/10 border border-emerald-500/20'
                    : 'bg-white/[0.02] border border-white/5'
                }`}
              >
                <span className="text-xl">{isDone ? '✓' : step.icon}</span>
                <span className={`text-sm font-semibold ${
                  isCurrent ? 'text-white' : isDone ? 'text-emerald-400' : 'text-slate-500'
                }`}>
                  {step.label}
                </span>
                {isCurrent && (
                  <span className="mr-auto text-xs text-cyan-400 animate-pulse">● حالية</span>
                )}
              </motion.div>
            );
          })}
        </div>
      </div>

      {/* Transition Button */}
      {!isLastStep && nextStep && (
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={transitionToNext}
          disabled={isTransitioning}
          className="w-full py-4 rounded-xl font-bold text-white relative overflow-hidden disabled:opacity-50"
        >
          <div className={`absolute inset-0 bg-gradient-to-l ${nextStep.color}`} />
          <span className="relative z-10 flex items-center justify-center gap-2">
            {isTransitioning ? 'جاري التحديث...' : `الانتقال إلى: ${nextStep.label}`}
          </span>
        </motion.button>
      )}

      {isLastStep && (
        <div className="text-center py-8">
          <span className="text-4xl mb-4 block">🎉</span>
          <p className="text-lg font-bold text-emerald-400">تمت الزيارة بنجاح!</p>
        </div>
      )}

      {/* Error */}
      {error && (
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mt-4 text-sm text-red-400 text-center bg-red-500/10 px-4 py-2 rounded-lg border border-red-500/20"
        >
          {error}
        </motion.p>
      )}
    </div>
  );
}
