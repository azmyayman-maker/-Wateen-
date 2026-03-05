'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { useVisitSocket } from '@/hooks/useVisitSocket';

/**
 * T043: ActiveVisitTracker — Real-time status badge, nurse profile card,
 * live map placeholder, and ETA countdown for patients.
 */

interface ActiveVisitTrackerProps {
  visitId: string;
}

const STATUS_LABELS: Record<string, { label: string; color: string; emoji: string }> = {
  PENDING_AGENCY: { label: 'بانتظار الوكالة', color: 'text-amber-400', emoji: '⏳' },
  PENDING_NURSE: { label: 'بانتظار الممرضة', color: 'text-amber-400', emoji: '🔍' },
  ACCEPTED: { label: 'تم القبول', color: 'text-blue-400', emoji: '✅' },
  EN_ROUTE: { label: 'في الطريق إليك', color: 'text-cyan-400', emoji: '🚗' },
  ARRIVED: { label: 'وصلت', color: 'text-emerald-400', emoji: '📍' },
  IN_PROGRESS: { label: 'جاري التنفيذ', color: 'text-purple-400', emoji: '💉' },
  COMPLETED: { label: 'تمت الزيارة', color: 'text-emerald-400', emoji: '✅' },
  CANCELLED: { label: 'ملغاة', color: 'text-red-400', emoji: '❌' },
};

export default function ActiveVisitTracker({ visitId }: ActiveVisitTrackerProps) {
  const { status, nurseLocation, eta, isConnected } = useVisitSocket(visitId);

  const statusInfo = STATUS_LABELS[status || 'PENDING_AGENCY'] || STATUS_LABELS.PENDING_AGENCY;

  return (
    <div className="bg-white/5 border border-white/10 rounded-2xl overflow-hidden" dir="rtl">
      {/* Status Header */}
      <div className="p-5 border-b border-white/5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">{statusInfo.emoji}</span>
            <div>
              <p className={`text-sm font-bold ${statusInfo.color}`}>{statusInfo.label}</p>
              <p className="text-xs text-slate-500">رقم الزيارة: {visitId.slice(0, 8)}...</p>
            </div>
          </div>

          {/* Connection indicator */}
          <div className={`flex items-center gap-1.5 text-xs ${isConnected ? 'text-emerald-400' : 'text-amber-400'}`}>
            <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-400' : 'bg-amber-400'} animate-pulse`} />
            {isConnected ? 'مباشر' : 'استعلام'}
          </div>
        </div>
      </div>

      {/* Nurse Info */}
      {nurseLocation && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="p-5 border-b border-white/5"
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-cyan-500 to-blue-500 flex items-center justify-center text-white font-bold text-sm">
              {nurseLocation.name?.charAt(0) || '?'}
            </div>
            <div className="flex-1">
              <p className="text-sm font-semibold text-white">{nurseLocation.name}</p>
              {eta && (
                <p className="text-xs text-cyan-400">الوصول خلال {eta} دقيقة تقريباً</p>
              )}
            </div>
          </div>
        </motion.div>
      )}

      {/* ETA Countdown */}
      {eta && status === 'EN_ROUTE' && (
        <div className="p-5">
          <div className="flex items-center justify-center gap-2">
            <motion.div
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 1.5, repeat: Infinity }}
              className="text-3xl font-bold text-cyan-400 font-mono"
            >
              {eta}
            </motion.div>
            <span className="text-sm text-slate-400">دقيقة للوصول</span>
          </div>
        </div>
      )}
    </div>
  );
}
