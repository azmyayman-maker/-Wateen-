'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useVisitSocket } from '@/hooks/useVisitSocket';

/**
 * T039+T043: BookingFlow — Multi-step booking form + ActiveVisitTracker.
 * Steps: 1) Service + Urgency → 2) Location → 3) Review → 4) Confirm → Track
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

interface ServiceOption {
  id: string;
  name: string;
  base_price: number;
  description?: string;
}

interface BookingFlowProps {
  services: ServiceOption[];
  onComplete?: (visitId: string) => void;
}

type Step = 'SERVICE' | 'LOCATION' | 'REVIEW' | 'CONFIRM' | 'TRACKING';

interface EstimateResult {
  service_type?: { name: string };
  is_night_hours?: boolean;
  breakdown?: {
    base_price: number;
    distance_fee: number;
    night_surcharge?: number;
    final_price: number;
  };
}

export default function BookingFlow({ services, onComplete }: BookingFlowProps) {
  const [step, setStep] = useState<Step>('SERVICE');
  const [selectedService, setSelectedService] = useState<ServiceOption | null>(null);
  const [urgency, setUrgency] = useState<'NORMAL' | 'URGENT'>('NORMAL');
  const [location, setLocation] = useState<{ lat: number; lng: number } | null>(null);
  const [address, setAddress] = useState('');
  const [estimate, setEstimate] = useState<EstimateResult | null>(null);
  const [visitId, setVisitId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const visitSocket = useVisitSocket(step === 'TRACKING' ? visitId : null);

  // Step animations
  const slideVariants = {
    enter: { x: 50, opacity: 0 },
    center: { x: 0, opacity: 1 },
    exit: { x: -50, opacity: 0 },
  };

  const getEstimate = async () => {
    if (!selectedService || !location) return;
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/v1/visits/estimate/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          service_type_id: selectedService.id,
          latitude: location.lat,
          longitude: location.lng,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setEstimate(data);
        setStep('REVIEW');
      } else {
        setError('فشل في حساب التكلفة');
      }
    } catch {
      setError('خطأ في الاتصال');
    } finally {
      setIsLoading(false);
    }
  };

  const confirmBooking = async () => {
    if (!selectedService || !location) return;
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/v1/visits/request/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          service_type_id: selectedService.id,
          latitude: location.lat,
          longitude: location.lng,
          urgency,
          address,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setVisitId(data.visit_id || data.id);
        setStep('TRACKING');
        onComplete?.(data.visit_id || data.id);
      } else {
        const data = await response.json().catch(() => ({}));
        setError(data.detail || 'فشل في إنشاء الطلب');
      }
    } catch {
      setError('خطأ في الاتصال');
    } finally {
      setIsLoading(false);
    }
  };

  const getCurrentLocation = () => {
    if (typeof navigator !== 'undefined' && navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setLocation({ lat: pos.coords.latitude, lng: pos.coords.longitude });
        },
        () => setError('يرجى السماح بتحديد الموقع'),
        { enableHighAccuracy: true }
      );
    }
  };

  return (
    <div className="min-h-screen bg-[#050505] text-white" dir="rtl">
      {/* Progress Bar */}
      <div className="sticky top-0 z-40 bg-[#050505]/80 backdrop-blur-xl border-b border-white/5 px-6 py-4">
        <div className="flex items-center gap-2 mb-2 max-w-md mx-auto">
          {['SERVICE', 'LOCATION', 'REVIEW', 'CONFIRM'].map((s, i) => (
            <div key={s} className="flex-1 flex items-center gap-2">
              <div className={`h-1 flex-1 rounded-full transition-all ${
                ['SERVICE', 'LOCATION', 'REVIEW', 'CONFIRM'].indexOf(step) >= i
                  ? 'bg-gradient-to-l from-cyan-500 to-blue-500'
                  : 'bg-white/10'
              }`} />
            </div>
          ))}
        </div>
        <p className="text-xs text-slate-400 text-center">
          {step === 'SERVICE' && 'اختر الخدمة'}
          {step === 'LOCATION' && 'حدد الموقع'}
          {step === 'REVIEW' && 'مراجعة التكلفة'}
          {step === 'CONFIRM' && 'تأكيد الحجز'}
          {step === 'TRACKING' && 'تتبع الزيارة'}
        </p>
      </div>

      {/* Content */}
      <div className="max-w-md mx-auto p-6">
        <AnimatePresence mode="wait">
          {/* Step 1: Service Selection */}
          {step === 'SERVICE' && (
            <motion.div key="service" variants={slideVariants} initial="enter" animate="center" exit="exit">
              <h2 className="text-xl font-bold mb-6">اختر نوع الخدمة</h2>
              <div className="space-y-3 mb-6">
                {services.map((service) => (
                  <motion.button
                    key={service.id}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => setSelectedService(service)}
                    className={`w-full p-4 rounded-xl text-right transition-all ${
                      selectedService?.id === service.id
                        ? 'bg-cyan-500/10 border-2 border-cyan-500/50'
                        : 'bg-white/5 border border-white/10 hover:bg-white/10'
                    }`}
                  >
                    <div className="flex justify-between items-center">
                      <span className="font-semibold">{service.name}</span>
                      <span className="text-sm text-cyan-400">{service.base_price} ج.م</span>
                    </div>
                    {service.description && (
                      <p className="text-xs text-slate-400 mt-1">{service.description}</p>
                    )}
                  </motion.button>
                ))}
              </div>

              {/* Urgency Selector */}
              <div className="flex gap-3 mb-6">
                {(['NORMAL', 'URGENT'] as const).map((u) => (
                  <button
                    key={u}
                    onClick={() => setUrgency(u)}
                    className={`flex-1 py-3 rounded-xl text-sm font-semibold transition-all ${
                      urgency === u
                        ? u === 'URGENT'
                          ? 'bg-red-500/20 border border-red-500/50 text-red-400'
                          : 'bg-cyan-500/20 border border-cyan-500/50 text-cyan-400'
                        : 'bg-white/5 border border-white/10 text-slate-400'
                    }`}
                  >
                    {u === 'NORMAL' ? 'عادي' : '🚨 عاجل'}
                  </button>
                ))}
              </div>

              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => selectedService && setStep('LOCATION')}
                disabled={!selectedService}
                className="w-full py-3.5 rounded-xl font-bold text-white bg-gradient-to-l from-cyan-500 to-blue-600 disabled:opacity-30"
              >
                التالي — تحديد الموقع
              </motion.button>
            </motion.div>
          )}

          {/* Step 2: Location */}
          {step === 'LOCATION' && (
            <motion.div key="location" variants={slideVariants} initial="enter" animate="center" exit="exit">
              <h2 className="text-xl font-bold mb-6">حدد موقعك</h2>
              
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={getCurrentLocation}
                className="w-full py-4 rounded-xl bg-white/5 border border-white/10 text-white font-semibold mb-4 flex items-center justify-center gap-2"
              >
                📍 استخدم موقعي الحالي
              </motion.button>

              {location && (
                <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-xl p-4 mb-4">
                  <p className="text-sm text-emerald-400">✓ تم تحديد الموقع</p>
                  <p className="text-xs text-slate-400 mt-1">{location.lat.toFixed(4)}, {location.lng.toFixed(4)}</p>
                </div>
              )}

              <input
                type="text"
                placeholder="العنوان التفصيلي (اختياري)"
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                className="w-full bg-white/5 border border-white/10 rounded-xl py-3 px-4 text-white text-sm placeholder:text-slate-500 mb-6 outline-none focus:border-cyan-500/50"
              />

              <div className="flex gap-3">
                <button onClick={() => setStep('SERVICE')} className="flex-1 py-3 rounded-xl bg-white/5 border border-white/10 text-slate-300 font-semibold">
                  رجوع
                </button>
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  onClick={getEstimate}
                  disabled={!location || isLoading}
                  className="flex-1 py-3 rounded-xl font-bold text-white bg-gradient-to-l from-cyan-500 to-blue-600 disabled:opacity-30"
                >
                  {isLoading ? '...' : 'حساب التكلفة'}
                </motion.button>
              </div>
            </motion.div>
          )}

          {/* Step 3: Review */}
          {step === 'REVIEW' && estimate && (
            <motion.div key="review" variants={slideVariants} initial="enter" animate="center" exit="exit">
              <h2 className="text-xl font-bold mb-6">مراجعة التكلفة</h2>

              <div className="bg-white/5 border border-white/10 rounded-2xl p-5 mb-6 space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-slate-400">الخدمة</span>
                  <span className="text-white">{estimate.service_type?.name}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-400">السعر الأساسي</span>
                  <span className="text-white">{estimate.breakdown?.base_price} ج.م</span>
                </div>
                {estimate.breakdown?.distance_fee > 0 && (
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-400">رسوم المسافة</span>
                    <span className="text-white">{estimate.breakdown?.distance_fee} ج.م</span>
                  </div>
                )}
                {estimate.is_night_hours && (
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-400">رسوم الفترة الليلية</span>
                    <span className="text-amber-400">+{estimate.breakdown?.night_surcharge} ج.م</span>
                  </div>
                )}
                <div className="border-t border-white/10 pt-3 flex justify-between">
                  <span className="font-bold text-white">الإجمالي</span>
                  <span className="font-bold text-lg text-emerald-400">{estimate.breakdown?.final_price} ج.م</span>
                </div>
              </div>

              <div className="flex gap-3">
                <button onClick={() => setStep('LOCATION')} className="flex-1 py-3 rounded-xl bg-white/5 border border-white/10 text-slate-300 font-semibold">
                  رجوع
                </button>
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  onClick={confirmBooking}
                  disabled={isLoading}
                  className="flex-1 py-3 rounded-xl font-bold text-white bg-gradient-to-l from-emerald-500 to-cyan-500 disabled:opacity-30"
                >
                  {isLoading ? '...' : 'تأكيد الحجز'}
                </motion.button>
              </div>
            </motion.div>
          )}

          {/* Step 4: Tracking */}
          {step === 'TRACKING' && visitId && (
            <motion.div key="tracking" variants={slideVariants} initial="enter" animate="center" exit="exit">
              <div className="text-center py-8">
                <motion.div
                  animate={{ scale: [1, 1.1, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                  className="text-5xl mb-4"
                >
                  🏥
                </motion.div>
                <h2 className="text-xl font-bold mb-2">تم تأكيد الحجز!</h2>
                <p className="text-sm text-slate-400 mb-6">جاري البحث عن ممرضه قريبة منك...</p>

                {/* Live status */}
                <div className="bg-white/5 border border-white/10 rounded-2xl p-5 text-right mb-4">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-xs text-slate-400">حالة الطلب</span>
                    <span className={`text-sm font-semibold px-3 py-1 rounded-full ${
                      visitSocket.status === 'ACCEPTED' ? 'bg-emerald-500/20 text-emerald-400'
                      : visitSocket.status === 'EN_ROUTE' ? 'bg-blue-500/20 text-blue-400'
                      : 'bg-amber-500/20 text-amber-400'
                    }`}>
                      {visitSocket.status || 'PENDING'}
                    </span>
                  </div>

                  {visitSocket.nurseLocation && (
                    <div>
                      <p className="text-sm text-white font-semibold">{visitSocket.nurseLocation.name}</p>
                      {visitSocket.eta && (
                        <p className="text-xs text-cyan-400 mt-1">الوصول خلال {visitSocket.eta} دقيقة</p>
                      )}
                    </div>
                  )}
                </div>

                <div className={`flex items-center justify-center gap-2 text-xs ${
                  visitSocket.isConnected ? 'text-emerald-400' : 'text-amber-400'
                }`}>
                  <span className={`w-2 h-2 rounded-full ${visitSocket.isConnected ? 'bg-emerald-400' : 'bg-amber-400'} animate-pulse`} />
                  {visitSocket.isConnected ? 'متصل — تحديثات مباشرة' : 'وضع الاستعلام'}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

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
    </div>
  );
}
