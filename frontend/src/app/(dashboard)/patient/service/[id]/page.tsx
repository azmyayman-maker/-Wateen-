'use client';

import { useLanguage } from '@/lib/i18n';
import { motion, AnimatePresence } from 'framer-motion';
import { useState } from 'react';
import { notFound } from 'next/navigation';
import { servicesData, ServiceId } from '@/lib/data/services';
import { ArrowRight, ArrowLeft, CheckCircle2, User, FileText, MapPin, Activity, ShieldCheck, Loader2 } from 'lucide-react';
import Link from 'next/link';
import { ServiceHeroFactory } from '@/components/services/ServiceHeroFactory';
import LocationPicker from '@/components/shared/map/LocationPicker';

// Booking steps
type BookingStep = 'customization' | 'location' | 'consent' | 'checkout' | 'processing' | 'success';

export default function ServiceBookingPage({ params }: { params: { id: string } }) {
  const { isRTL } = useLanguage();
  const [currentStep, setCurrentStep] = useState<BookingStep>('customization');
  const [patientType, setPatientType] = useState<'me' | 'other'>('me');
  const [notes, setNotes] = useState('');
  const [isConsentChecked, setIsConsentChecked] = useState(false);
  const [location, setLocation] = useState<[number, number] | null>(null);

  const serviceId = params.id as ServiceId;
  const service = servicesData[serviceId];

  if (!service) {
    notFound();
  }

  // Choose the native name based on the direction
  const title = isRTL ? service.nameAr : service.nameEn;
  const description = isRTL ? service.descriptionAr : service.descriptionEn;
  const tags = isRTL ? service.tagsAr : service.tagsEn;
  const SvgIcon = service.svg;

  return (
    <div className="min-h-[100dvh] w-full bg-[#030712] text-slate-50 overflow-x-hidden flex flex-col pt-20 pb-24">
      
      {/* ── Dynamic Hero Section ── */}
      <section className="relative w-full overflow-hidden shrink-0 px-4 md:px-8 py-10 min-h-[40vh] flex flex-col items-center justify-center text-center">
        
        {/* Ambient Glows */}
        <div 
          className="absolute inset-0 opacity-20 pointer-events-none" 
          style={{ 
            background: `radial-gradient(circle at top center, rgba(${service.colorRgb}, 0.5) 0%, transparent 70%)` 
          }} 
        />
        
        {/* Back Button */}
        <div className="absolute top-4 w-full px-4 max-w-4xl left-1/2 -translate-x-1/2 flex justify-start z-20">
          <Link href="/patient" className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors text-sm font-medium bg-slate-900/50 px-4 py-2 rounded-full border border-white/5 backdrop-blur-md">
            {isRTL ? <ArrowRight className="w-4 h-4" /> : <ArrowLeft className="w-4 h-4" />}
            {isRTL ? 'العودة للرئيسية' : 'Back to Home'}
          </Link>
        </div>

        {/* Hero Content */}
        <motion.div 
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
          className="relative z-10 max-w-2xl mx-auto flex flex-col items-center gap-6"
        >
          <div 
            className="w-24 h-24 sm:w-28 sm:h-28 rounded-3xl flex items-center justify-center border shadow-2xl relative"
            style={{ 
              borderColor: `rgba(${service.colorRgb}, 0.3)`, 
              background: `linear-gradient(135deg, rgba(${service.colorRgb}, 0.2) 0%, rgba(11,17,32,0.8) 100%)`,
              boxShadow: `0 20px 50px rgba(${service.colorRgb}, 0.15), inset 0 0 20px rgba(${service.colorRgb}, 0.1)` 
            }}
          >
             <div className="w-14 h-14 sm:w-16 sm:h-16 relative z-10 p-1">
               <SvgIcon />
             </div>
             <ServiceHeroFactory heroType={service.heroType} colorRgb={service.colorRgb} />
          </div>

          <div>
            <h1 className="text-3xl sm:text-4xl md:text-5xl font-extrabold tracking-tight text-white mb-4 drop-shadow-lg">
              {title}
            </h1>
            <p className="text-slate-300 text-sm sm:text-base leading-relaxed max-w-xl mx-auto">
              {description}
            </p>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-2 mt-2">
             {tags.map((tag, i) => (
                <span 
                  key={i} 
                  className="px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider border backdrop-blur-md"
                  style={{ 
                    borderColor: `rgba(${service.colorRgb}, 0.3)`, 
                    color: `rgb(${service.colorRgb})`,
                    background: `rgba(${service.colorRgb}, 0.1)`
                  }}
                >
                  {tag}
                </span>
             ))}
          </div>
        </motion.div>
      </section>

      {/* ── Unified Booking Flow Container ── */}
      <section className="relative z-20 flex-1 px-4 md:px-8 max-w-3xl mx-auto w-full -mt-6 pb-20">
         <div className="bg-slate-900/60 backdrop-blur-2xl border border-white/10 rounded-3xl overflow-hidden shadow-2xl min-h-[500px] flex flex-col">
             
             {/* Progress Bar */}
             {currentStep !== 'processing' && currentStep !== 'success' && (
               <div className="h-1.5 w-full bg-slate-800 flex">
                 <motion.div 
                   className="h-full" 
                   style={{ background: `rgb(${service.colorRgb})` }}
                   initial={{ width: '25%' }}
                   animate={{ 
                     width: currentStep === 'customization' ? '25%' : 
                            currentStep === 'location' ? '50%' : 
                            currentStep === 'consent' ? '75%' : '100%' 
                   }}
                   transition={{ type: 'spring', stiffness: 100, damping: 20 }}
                 />
               </div>
             )}

             <div className="p-6 sm:p-8 flex-1 flex flex-col">
                <AnimatePresence mode="wait">
                  
                  {/* STEP 1: Customization */}
                  {currentStep === 'customization' && (
                    <motion.div 
                      key="customization"
                      initial={{ opacity: 0, x: isRTL ? -20 : 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: isRTL ? 20 : -20 }}
                      className="flex-1 flex flex-col"
                    >
                      <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-slate-800 text-slate-300 border border-white/5"><User className="w-5 h-5" /></div>
                        {isRTL ? 'تفاصيل المريض' : 'Patient Details'}
                      </h2>
                      
                      <div className="space-y-6 flex-1">
                        <div>
                          <label className="block text-sm font-medium text-slate-400 mb-3">
                            {isRTL ? 'من يتلقى هذه الخدمة؟' : 'Who is receiving this service?'}
                          </label>
                          <div className="grid grid-cols-2 gap-3">
                            <button
                              onClick={() => setPatientType('me')}
                              className={`p-4 rounded-xl text-sm font-semibold border transition-all ${patientType === 'me' ? 'bg-slate-800 border-white/20 text-white shadow-lg' : 'bg-transparent border-white/5 text-slate-500 hover:text-slate-300'}`}
                            >
                              {isRTL ? 'لنفسي' : 'For Myself'}
                            </button>
                            <button
                              onClick={() => setPatientType('other')}
                              className={`p-4 rounded-xl text-sm font-semibold border transition-all ${patientType === 'other' ? 'bg-slate-800 border-white/20 text-white shadow-lg' : 'bg-transparent border-white/5 text-slate-500 hover:text-slate-300'}`}
                            >
                              {isRTL ? 'لشخص آخر' : 'For Someone Else'}
                            </button>
                          </div>
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-slate-400 mb-2 flex items-center gap-2">
                            <FileText className="w-4 h-4" />
                            {isRTL ? 'ملاحظات للممرض (اختياري)' : 'Notes for the Nurse (Optional)'}
                          </label>
                          <textarea 
                            value={notes}
                            onChange={(e) => setNotes(e.target.value)}
                            placeholder={isRTL ? 'أي حساسية، أعراض، أو توجيهات خاصة...' : 'Any allergies, symptoms, or special directions...'}
                            className="w-full bg-slate-950/50 border border-white/10 rounded-xl p-4 text-white placeholder-slate-600 focus:outline-none focus:border-white/30 transition-colors resize-none min-h-[120px]"
                          />
                        </div>
                      </div>

                      <button 
                        onClick={() => setCurrentStep('location')}
                        className="w-full mt-6 py-4 rounded-xl font-bold text-white flex items-center justify-center gap-2 transition-all shadow-lg active:scale-95"
                        style={{ background: `linear-gradient(90deg, rgb(${service.colorRgb}), rgba(${service.colorRgb}, 0.7))` }}
                      >
                        {isRTL ? 'التالي: تحديد الموقع' : 'Next: Set Location'}
                        {isRTL ? <ArrowLeft className="w-5 h-5" /> : <ArrowRight className="w-5 h-5" />}
                      </button>
                    </motion.div>
                  )}

                  {/* STEP 2: Location */}
                  {currentStep === 'location' && (
                    <motion.div 
                      key="location"
                      initial={{ opacity: 0, x: isRTL ? -20 : 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: isRTL ? 20 : -20 }}
                      className="flex-1 flex flex-col"
                    >
                      <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-slate-800 text-slate-300 border border-white/5"><MapPin className="w-5 h-5" /></div>
                        {isRTL ? 'موقع الزيارة' : 'Visit Location'}
                      </h2>
                      
                      <div className="flex-1 rounded-xl overflow-hidden border border-white/10 min-h-[300px] mb-6">
                        <LocationPicker onLocationSelect={(lat, lng) => setLocation([lat, lng])} />
                      </div>

                      <div className="flex gap-3 mt-auto">
                        <button 
                          onClick={() => setCurrentStep('customization')}
                          className="px-6 py-4 rounded-xl font-semibold text-slate-400 border border-white/10 hover:bg-white/5 transition-all"
                        >
                          {isRTL ? 'رجوع' : 'Back'}
                        </button>
                        <button 
                          onClick={() => setCurrentStep('consent')}
                          className="flex-1 py-4 rounded-xl font-bold text-white flex items-center justify-center gap-2 transition-all shadow-lg active:scale-95"
                          style={{ background: `linear-gradient(90deg, rgb(${service.colorRgb}), rgba(${service.colorRgb}, 0.7))` }}
                        >
                          {isRTL ? 'التالي: الموافقات' : 'Next: Consents'}
                          {isRTL ? <ArrowLeft className="w-5 h-5" /> : <ArrowRight className="w-5 h-5" />}
                        </button>
                      </div>
                    </motion.div>
                  )}

                  {/* STEP 3: Consent */}
                  {currentStep === 'consent' && (
                    <motion.div 
                      key="consent"
                      initial={{ opacity: 0, x: isRTL ? -20 : 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: isRTL ? 20 : -20 }}
                      className="flex-1 flex flex-col"
                    >
                      <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-slate-800 text-slate-300 border border-white/5"><ShieldCheck className="w-5 h-5" /></div>
                        {isRTL ? 'الموافقات الطبية' : 'Medical Consents'}
                      </h2>
                      
                      <div className="flex-1 space-y-4">
                        <div className="p-5 rounded-2xl border border-[#79B253]/20 bg-[#79B253]/5 flex gap-4 items-start">
                          <div className="w-10 h-10 rounded-full bg-[#79B253]/20 flex items-center justify-center shrink-0">
                             <Activity className="w-5 h-5 text-[#79B253]" />
                          </div>
                          <div>
                            <h3 className="text-white font-bold mb-1">{isRTL ? 'مشاركة المؤشرات الحيوية' : 'Share Vitals Data'}</h3>
                            <p className="text-sm text-slate-400 mb-4 line-clamp-2">
                              {isRTL 
                                ? 'أوافق على السماح لتطبيق وتين بجمع ومشاركة مؤشراتي الحيوية من جهازي الذكي (Apple Health / Google Fit) مع الممرض لضمان أفضل رعاية طبية.'
                                : 'I agree to allow Wateen to collect and share my real-time vitals from my smart device with the assigned nurse for optimal care.'}
                            </p>
                            <label className="flex items-center gap-3 cursor-pointer group">
                              <div className={`w-6 h-6 rounded border flex items-center justify-center transition-colors ${isConsentChecked ? 'bg-[#79B253] border-[#79B253]' : 'bg-transparent border-slate-600 group-hover:border-slate-400'}`}>
                                {isConsentChecked && <CheckCircle2 className="w-4 h-4 text-slate-900" />}
                              </div>
                              <span className="text-sm font-semibold text-white select-none">{isRTL ? 'أوافق على الشروط' : 'I accept the terms'}</span>
                              {/* Hidden checkbox for accessibility */}
                              <input type="checkbox" className="hidden" checked={isConsentChecked} onChange={(e) => setIsConsentChecked(e.target.checked)} />
                            </label>
                          </div>
                        </div>
                      </div>

                      <div className="flex gap-3 mt-auto pt-6">
                        <button 
                          onClick={() => setCurrentStep('location')}
                          className="px-6 py-4 rounded-xl font-semibold text-slate-400 border border-white/10 hover:bg-white/5 transition-all"
                        >
                          {isRTL ? 'رجوع' : 'Back'}
                        </button>
                        <button 
                          disabled={!isConsentChecked}
                          onClick={() => setCurrentStep('checkout')}
                          className={`flex-1 py-4 rounded-xl font-bold text-white flex items-center justify-center gap-2 transition-all active:scale-95 ${!isConsentChecked ? 'opacity-50 cursor-not-allowed grayscale' : 'shadow-lg'}`}
                          style={{ background: isConsentChecked ? `linear-gradient(90deg, rgb(${service.colorRgb}), rgba(${service.colorRgb}, 0.7))` : 'rgba(255,255,255,0.1)' }}
                        >
                          {isRTL ? 'متابعة للدفع' : 'Proceed to Checkout'}
                          {isRTL ? <ArrowLeft className="w-5 h-5" /> : <ArrowRight className="w-5 h-5" />}
                        </button>
                      </div>
                    </motion.div>
                  )}

                  {/* STEP 4: Checkout */}
                  {currentStep === 'checkout' && (
                    <motion.div 
                      key="checkout"
                      initial={{ opacity: 0, x: isRTL ? -20 : 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: isRTL ? 20 : -20 }}
                      className="flex-1 flex flex-col"
                    >
                      <h2 className="text-2xl font-bold text-white mb-2 text-center">
                        {isRTL ? 'ملخص الحجز' : 'Booking Summary'}
                      </h2>
                      <p className="text-sm text-slate-400 text-center mb-8">
                        {isRTL ? 'راجع تفاصيل طلبك قبل التأكيد' : 'Review your request before confirming'}
                      </p>
                      
                      <div className="flex-1 flex flex-col gap-4">
                        <div className="p-4 rounded-xl bg-slate-950/50 border border-white/5 flex justify-between items-center">
                          <span className="text-slate-400 font-medium">{isRTL ? 'الخدمة' : 'Service'}</span>
                          <span className="text-white font-bold">{title}</span>
                        </div>
                        <div className="p-4 rounded-xl bg-slate-950/50 border border-white/5 flex justify-between items-center">
                          <span className="text-slate-400 font-medium">{isRTL ? 'المريض' : 'Patient'}</span>
                          <span className="text-white font-bold capitalize">{patientType === 'me' ? (isRTL ? 'نفسي' : 'Myself') : (isRTL ? 'شخص آخر' : 'Someone Else')}</span>
                        </div>
                        <div className="p-4 rounded-xl bg-slate-950/50 border border-white/5 flex flex-col gap-2">
                          <div className="flex justify-between items-center border-b border-white/5 pb-3">
                            <span className="text-slate-400 font-medium">{isRTL ? 'تكلفة الخدمة' : 'Service Cost'}</span>
                            <span className="text-white font-bold">{service.basePrice} EGP</span>
                          </div>
                          <div className="flex justify-between items-center pt-1 border-b border-white/5 pb-3">
                            <span className="text-slate-400 font-medium">{isRTL ? 'رسوم التوصيل' : 'Dispatch Fee'}</span>
                            <span className="text-white font-bold">50 EGP</span>
                          </div>
                          <div className="flex justify-between items-center pt-1">
                            <span className="text-slate-300 font-bold">{isRTL ? 'الإجمالي' : 'Total'}</span>
                            <span className="text-2xl font-black" style={{ color: `rgb(${service.colorRgb})` }}>{service.basePrice + 50} EGP</span>
                          </div>
                        </div>
                      </div>

                      <div className="flex gap-3 mt-8">
                        <button 
                          onClick={() => setCurrentStep('consent')}
                          className="px-6 py-4 rounded-xl font-semibold text-slate-400 border border-white/10 hover:bg-white/5 transition-all"
                        >
                          {isRTL ? 'رجوع' : 'Back'}
                        </button>
                        <button 
                          onClick={() => {
                            setCurrentStep('processing');
                            setTimeout(() => {
                              setCurrentStep('success'); // In reality, this directs to simulator
                            }, 3000);
                          }}
                          className="flex-1 py-4 rounded-xl font-bold text-white flex items-center justify-center gap-2 transition-all shadow-[0_0_30px_rgba(255,255,255,0.1)] hover:shadow-[0_0_40px_rgba(255,255,255,0.2)] active:scale-95 text-lg"
                          style={{ background: `linear-gradient(90deg, rgb(${service.colorRgb}), rgba(${service.colorRgb}, 0.7))` }}
                        >
                          {isRTL ? 'تأكيد الطلب' : 'Confirm Request'}
                        </button>
                      </div>
                    </motion.div>
                  )}

                  {/* STEP 5: Processing Overlay (Simulator Transition) */}
                  {currentStep === 'processing' && (
                    <motion.div 
                      key="processing"
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      className="flex-1 flex flex-col items-center justify-center text-center gap-6"
                    >
                      <div className="relative w-24 h-24">
                        <div className="absolute inset-0 rounded-full border-4 border-slate-800" />
                        <motion.div 
                          className="absolute inset-0 rounded-full border-4 border-transparent border-t-white"
                          animate={{ rotate: 360 }}
                          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                        />
                        <div className="absolute inset-0 flex items-center justify-center">
                          <Activity className="w-8 h-8 text-white animate-pulse" />
                        </div>
                      </div>
                      <div>
                        <h2 className="text-2xl font-bold text-white mb-2">{isRTL ? 'جاري تأكيد حجزك...' : 'Confirming Booking...'}</h2>
                        <p className="text-slate-400">{isRTL ? 'نقوم بتأمين بياناتك بتشفير بلوكتشين' : 'Securing your data with blockchain encryption'}</p>
                      </div>
                    </motion.div>
                  )}

                  {/* STEP 6: Success (Temporary before simulator link) */}
                  {currentStep === 'success' && (
                    <motion.div 
                      key="success"
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      className="flex-1 flex flex-col items-center justify-center text-center gap-6"
                    >
                      <motion.div 
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{ type: 'spring', delay: 0.2 }}
                        className="w-24 h-24 rounded-full bg-green-500/20 flex items-center justify-center border border-green-500/50"
                      >
                         <CheckCircle2 className="w-12 h-12 text-green-400" />
                      </motion.div>
                      <div>
                        <h2 className="text-2xl font-bold text-white mb-2">{isRTL ? 'تم تأكيد الطلب بنجاح!' : 'Request Confirmed!'}</h2>
                        <p className="text-slate-400 mb-8">{isRTL ? 'جاري تحويلك إلى شاشة التتبع والرادار...' : 'Redirecting you to the tracking radar...'}</p>
                        
                        <Link href="/patient/simulator">
                           <button className="px-8 py-4 rounded-xl font-bold text-white bg-green-500 hover:bg-green-600 transition-colors shadow-lg shadow-green-500/20 active:scale-95">
                             {isRTL ? 'الدخول للرادار (محاكاة)' : 'Enter Radar (Simulator)'}
                           </button>
                        </Link>
                      </div>
                    </motion.div>
                  )}

                </AnimatePresence>
             </div>
         </div>
      </section>

    </div>
  );
}
