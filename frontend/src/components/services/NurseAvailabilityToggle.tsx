'use client';

import React, { useState, useCallback } from 'react';
import { motion } from 'framer-motion';

/**
 * T047: NurseAvailabilityToggle — Prominent toggle for nurse online/offline status.
 * Starts/stops GPS streaming when toggled on/off.
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

interface NurseAvailabilityToggleProps {
  initialOnline?: boolean;
  onStatusChange?: (isOnline: boolean) => void;
}

export default function NurseAvailabilityToggle({ 
  initialOnline = false, 
  onStatusChange 
}: NurseAvailabilityToggleProps) {
  const [isOnline, setIsOnline] = useState(initialOnline);
  const [isToggling, setIsToggling] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const toggle = useCallback(async () => {
    if (isToggling) return;
    setIsToggling(true);
    setError(null);

    const newState = !isOnline;

    try {
      let lat: number | null = null;
      let lng: number | null = null;

      // Get GPS coordinates when going online
      if (newState) {
        try {
          const position = await new Promise<GeolocationPosition>((resolve, reject) => {
            navigator.geolocation.getCurrentPosition(resolve, reject, {
              enableHighAccuracy: true,
              timeout: 10000,
            });
          });
          lat = position.coords.latitude;
          lng = position.coords.longitude;
        } catch {
          setError('يرجى تفعيل خدمات الموقع للعمل كممرضه متاحة');
          setIsToggling(false);
          return;
        }
      }

      const response = await fetch(`${API_URL}/v1/visits/nurse/toggle/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          is_online: newState,
          latitude: lat,
          longitude: lng,
        }),
      });

      if (response.ok) {
        setIsOnline(newState);
        onStatusChange?.(newState);
      } else {
        const data = await response.json().catch(() => ({}));
        setError(data.detail || 'فشل تغيير الحالة');
      }
    } catch {
      setError('خطأ في الاتصال');
    } finally {
      setIsToggling(false);
    }
  }, [isOnline, isToggling, onStatusChange]);

  return (
    <div className="flex flex-col items-center gap-4" dir="rtl">
      {/* Toggle Button */}
      <motion.button
        whileTap={{ scale: 0.95 }}
        onClick={toggle}
        disabled={isToggling}
        className={`
          relative w-32 h-32 rounded-full border-4 transition-all duration-500
          ${isOnline
            ? 'border-emerald-500/50 shadow-[0_0_40px_rgba(16,185,129,0.3)]'
            : 'border-white/10 shadow-none'
          }
          ${isToggling ? 'opacity-60 cursor-wait' : 'cursor-pointer'}
        `}
      >
        {/* Glow ring */}
        {isOnline && (
          <motion.div
            className="absolute inset-0 rounded-full border-2 border-emerald-400/30"
            animate={{ scale: [1, 1.15, 1], opacity: [0.5, 0, 0.5] }}
            transition={{ duration: 2, repeat: Infinity }}
          />
        )}

        {/* Inner circle */}
        <div className={`
          absolute inset-2 rounded-full flex items-center justify-center transition-all duration-500
          ${isOnline
            ? 'bg-gradient-to-br from-emerald-500 to-cyan-500'
            : 'bg-white/5'
          }
        `}>
          {/* Power icon */}
          <svg 
            className={`w-10 h-10 transition-colors duration-300 ${isOnline ? 'text-white' : 'text-slate-500'}`} 
            fill="none" 
            viewBox="0 0 24 24" 
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 2v6m0 0a6 6 0 110 12 6 6 0 010-12z" />
          </svg>
        </div>
      </motion.button>

      {/* Status Label */}
      <div className="text-center">
        <p className={`text-lg font-bold transition-colors ${isOnline ? 'text-emerald-400' : 'text-slate-400'}`}>
          {isToggling ? 'جاري التحويل...' : isOnline ? 'متصلة — متاحة للزيارات' : 'غير متصلة'}
        </p>
        <p className="text-xs text-slate-500 mt-1">
          {isOnline ? 'موقعك الجغرافي يُرسل تلقائياً' : 'اضغطي للبدء في استقبال الطلبات'}
        </p>
      </div>

      {/* Error message */}
      {error && (
        <motion.p
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-sm text-red-400 text-center bg-red-500/10 px-4 py-2 rounded-lg border border-red-500/20"
        >
          {error}
        </motion.p>
      )}
    </div>
  );
}
