'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

/**
 * T044: DispatchOfferCard — Full-screen overlay for incoming nurse dispatch offers.
 * Shows service type, patient district, distance/ETA, earnings.
 * Accept/Decline buttons with 60s countdown timer.
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

interface DispatchOffer {
  offerId: string;
  visitId: string;
  serviceType: string;
  patientDistrict: string;
  distanceKm: number;
  etaMinutes: number;
  earnings: string;
  expiresAt: string;
}

interface DispatchOfferCardProps {
  offer: DispatchOffer | null;
  onAccepted?: () => void;
  onDeclined?: () => void;
}

export default function DispatchOfferCard({ offer, onAccepted, onDeclined }: DispatchOfferCardProps) {
  const [timeLeft, setTimeLeft] = useState(60);
  const [isResponding, setIsResponding] = useState(false);
  const [responseStatus, setResponseStatus] = useState<'idle' | 'accepted' | 'declined' | 'expired'>('idle');

  // Countdown timer
  useEffect(() => {
    if (!offer || responseStatus !== 'idle') return;

    const expiresAt = new Date(offer.expiresAt).getTime();
    const updateTimer = () => {
      const remaining = Math.max(0, Math.ceil((expiresAt - Date.now()) / 1000));
      setTimeLeft(remaining);
      if (remaining <= 0) {
        setResponseStatus('expired');
      }
    };

    updateTimer();
    const interval = setInterval(updateTimer, 1000);
    return () => clearInterval(interval);
  }, [offer, responseStatus]);

  // Reset state when new offer arrives
  useEffect(() => {
    if (offer) {
      setResponseStatus('idle');
      setTimeLeft(60);
    }
  }, [offer?.offerId]);

  const respond = useCallback(async (action: 'accept' | 'reject') => {
    if (!offer || isResponding) return;
    setIsResponding(true);

    try {
      const response = await fetch(`${API_URL}/v1/visits/nurse/respond-offer/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ offer_id: offer.offerId, action }),
      });

      if (response.ok) {
        setResponseStatus(action === 'accept' ? 'accepted' : 'declined');
        if (action === 'accept') onAccepted?.();
        else onDeclined?.();
      } else {
        const err = await response.json().catch(() => ({}));
        console.error('Respond offer failed:', err);
      }
    } catch (err) {
      console.error('Respond offer error:', err);
    } finally {
      setIsResponding(false);
    }
  }, [offer, isResponding, onAccepted, onDeclined]);

  if (!offer) return null;

  const urgencyColor = timeLeft <= 10 ? 'from-red-500 to-orange-500' 
    : timeLeft <= 30 ? 'from-amber-500 to-yellow-500' 
    : 'from-cyan-500 to-blue-500';

  const progressPercent = (timeLeft / 60) * 100;

  return (
    <AnimatePresence>
      {responseStatus === 'idle' && (
        <motion.div
          initial={{ opacity: 0, scale: 0.9, y: 100 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.9, y: 100 }}
          transition={{ type: 'spring', damping: 25, stiffness: 300 }}
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm"
          dir="rtl"
        >
          <motion.div 
            className="w-full max-w-md bg-[#0A0A1A] border border-white/10 rounded-2xl overflow-hidden shadow-2xl"
            layoutId="offer-card"
          >
            {/* Countdown Progress Bar */}
            <div className="h-1.5 bg-white/5 relative overflow-hidden">
              <motion.div
                className={`h-full bg-gradient-to-l ${urgencyColor}`}
                initial={{ width: '100%' }}
                animate={{ width: `${progressPercent}%` }}
                transition={{ duration: 1, ease: 'linear' }}
              />
            </div>

            {/* Header */}
            <div className="p-6 pb-4">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${urgencyColor} flex items-center justify-center`}>
                    <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-white">طلب زيارة جديد</h3>
                    <p className="text-sm text-slate-400">{offer.serviceType}</p>
                  </div>
                </div>
                <div className={`text-2xl font-bold bg-gradient-to-l ${urgencyColor} bg-clip-text text-transparent font-mono`}>
                  {timeLeft}s
                </div>
              </div>

              {/* Details Grid */}
              <div className="grid grid-cols-2 gap-3 mb-6">
                <div className="bg-white/5 rounded-xl p-3 border border-white/5">
                  <p className="text-xs text-slate-400 mb-1">المنطقة</p>
                  <p className="text-sm font-semibold text-white">{offer.patientDistrict}</p>
                </div>
                <div className="bg-white/5 rounded-xl p-3 border border-white/5">
                  <p className="text-xs text-slate-400 mb-1">المسافة</p>
                  <p className="text-sm font-semibold text-white">{offer.distanceKm.toFixed(1)} كم</p>
                </div>
                <div className="bg-white/5 rounded-xl p-3 border border-white/5">
                  <p className="text-xs text-slate-400 mb-1">الوقت المتوقع</p>
                  <p className="text-sm font-semibold text-white">{offer.etaMinutes} دقيقة</p>
                </div>
                <div className="bg-white/5 rounded-xl p-3 border border-white/5">
                  <p className="text-xs text-slate-400 mb-1">الأرباح</p>
                  <p className="text-sm font-semibold text-emerald-400">{offer.earnings} ج.م</p>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3">
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => respond('reject')}
                  disabled={isResponding}
                  className="flex-1 py-3.5 rounded-xl font-bold text-sm bg-white/5 border border-white/10 text-slate-300 hover:bg-white/10 transition-colors disabled:opacity-50"
                >
                  رفض
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => respond('accept')}
                  disabled={isResponding}
                  className="flex-1 py-3.5 rounded-xl font-bold text-sm text-white relative overflow-hidden disabled:opacity-50"
                >
                  <div className="absolute inset-0 bg-gradient-to-l from-emerald-500 to-cyan-500" />
                  <span className="relative z-10">قبول الطلب</span>
                </motion.button>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
