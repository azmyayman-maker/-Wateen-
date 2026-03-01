'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  ArrowLeft, 
  Search, 
  Filter, 
  Clock, 
  User, 
  CheckCircle2, 
  ChevronRight,
  MapPin,
  AlertTriangle
} from 'lucide-react';
import Link from 'next/link';
import { useLanguage } from '@/lib/i18n';

// Mock data for the dispatching queue
const MOCK_PENDING = [
  { id: 'v1', type: 'IV Drip', patient: 'Ahmed Ali', location: 'Maadi, Cairo', time: '2 mins ago', price: 250, urgency: 'high' },
  { id: 'v2', type: 'Wound Care', patient: 'Sara Mahmoud', location: 'Nasr City', time: '5 mins ago', price: 180, urgency: 'normal' },
  { id: 'v3', type: 'Blood Test', patient: 'Omar Hassan', location: 'Zamalek', time: '12 mins ago', price: 120, urgency: 'normal' },
];

const MOCK_AVAILABLE_NURSES = [
  { id: 'n1', name: 'Amira S.', rating: 4.9, distance: '0.8 km', specialty: 'General Nursing' },
  { id: 'n2', name: 'Khaled M.', rating: 4.7, distance: '1.5 km', specialty: 'ER Specialist' },
  { id: 'n3', name: 'Mona Y.', rating: 5.0, distance: '2.1 km', specialty: 'Home Care Expert' },
];

export default function AgencyDispatchPage() {
  const { isRTL } = useLanguage();
  const [selectedVisit, setSelectedVisit] = useState<any>(null);
  const [isDispatching, setIsDispatching] = useState(false);

  const handleDispatch = (nurse: any) => {
    setIsDispatching(true);
    // Real API call to /api/v1/agency/{id}/dispatch/manual/
    setTimeout(() => {
      setIsDispatching(false);
      setSelectedVisit(null);
      alert(`${isRTL ? 'تم توزيع الزيارة بنجاح!' : 'Visit dispatched successfully!'}`);
    }, 1500);
  };

  return (
    <div className="space-y-8 pb-20">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link 
          href="/agency" 
          className="p-2.5 rounded-xl bg-slate-900 border border-white/5 hover:border-white/20 transition-all text-slate-400 hover:text-white"
        >
          <ArrowLeft className={`w-5 h-5 ${isRTL ? 'rotate-180' : ''}`} />
        </Link>
        <div>
          <h1 className="text-2xl font-black text-white">{isRTL ? 'قائمة التوزيع' : 'Dispatch Queue'}</h1>
          <p className="text-sm text-slate-400 font-medium">Manage pending requests waiting for nurse assignment</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
        
        {/* Left Column: Visit List */}
        <div className="space-y-4">
          <div className="flex items-center justify-between px-2">
            <h3 className="text-xs font-black text-slate-500 uppercase tracking-widest">{isRTL ? 'الطلبات المعلقة' : 'Pending Requests'}</h3>
            <span className="text-xs font-bold text-blue-400 bg-blue-400/10 px-2 py-1 rounded-md">{MOCK_PENDING.length} Total</span>
          </div>

          <div className="space-y-3">
             {MOCK_PENDING.map((visit) => (
               <button
                 key={visit.id}
                 onClick={() => setSelectedVisit(visit)}
                 className={`w-full p-5 rounded-3xl border transition-all text-start group relative overflow-hidden ${
                   selectedVisit?.id === visit.id 
                    ? 'bg-blue-600 border-blue-500 shadow-2xl shadow-blue-600/20' 
                    : 'bg-slate-900/40 border-white/5 hover:border-white/20'
                 }`}
               >
                 <div className="flex items-start justify-between relative z-10">
                   <div className="flex items-center gap-4">
                      <div className={`p-3 rounded-2xl ${selectedVisit?.id === visit.id ? 'bg-white/20' : 'bg-slate-800'}`}>
                        <Clock className={`w-6 h-6 ${selectedVisit?.id === visit.id ? 'text-white' : 'text-blue-400'}`} />
                      </div>
                      <div>
                        <h4 className="font-bold text-white text-lg">{visit.type}</h4>
                        <p className={`text-xs ${selectedVisit?.id === visit.id ? 'text-blue-100' : 'text-slate-400'}`}>
                          {visit.patient} • {visit.location}
                        </p>
                      </div>
                   </div>
                   <div className="text-end">
                      <p className="font-black text-white">{visit.price} EGP</p>
                      <p className={`text-[10px] font-bold ${selectedVisit?.id === visit.id ? 'text-blue-200' : 'text-slate-500'}`}>{visit.time}</p>
                   </div>
                 </div>
                 
                 {visit.urgency === 'high' && (
                   <div className="absolute top-0 right-0 p-1 bg-red-500 rounded-bl-xl">
                      <AlertTriangle className="w-3 h-3 text-white" />
                   </div>
                 )}
               </button>
             ))}
          </div>
        </div>

        {/* Right Column: Nurse Selection (Conditional) */}
        <div className="space-y-6">
           <h3 className="text-xs font-black text-slate-500 uppercase tracking-widest px-2">
             {selectedVisit ? (isRTL ? 'اختر ممرض للتوزيع' : 'Assign a Nurse') : (isRTL ? 'تفاصيل المهمة' : 'Task Details')}
           </h3>

           {selectedVisit ? (
             <motion.div 
               initial={{ opacity: 0, y: 20 }}
               animate={{ opacity: 1, y: 0 }}
               className="bg-slate-900/60 backdrop-blur-2xl border border-white/10 rounded-[2.5rem] p-8 space-y-8 shadow-2xl"
             >
                <div className="flex items-center gap-4 pb-6 border-b border-white/5">
                   <div className="w-14 h-14 rounded-full bg-blue-500 flex items-center justify-center text-white ring-8 ring-blue-500/10">
                      <User className="w-8 h-8" />
                   </div>
                   <div>
                      <h2 className="text-xl font-black text-white line-clamp-1">{selectedVisit.patient}</h2>
                      <div className="flex items-center gap-2 text-slate-400 text-xs">
                        <MapPin className="w-3 h-3" />
                        {selectedVisit.location}
                      </div>
                   </div>
                </div>

                <div className="space-y-4">
                  <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest">{isRTL ? 'الممرضين المتاحين في المنطقة' : 'Available Nurses Nearby'}</h4>
                  <div className="space-y-3">
                    {MOCK_AVAILABLE_NURSES.map((nurse) => (
                      <div 
                        key={nurse.id} 
                        className="flex items-center justify-between p-4 rounded-2xl bg-white/5 border border-white/5 hover:bg-white/10 transition-all group"
                      >
                        <div className="flex items-center gap-3">
                           <div className="w-10 h-10 rounded-full bg-slate-800 border border-white/10 flex items-center justify-center">
                              <span className="text-xs font-bold text-slate-300">{nurse.name.split(' ')[0][0]}</span>
                           </div>
                           <div>
                             <p className="text-sm font-bold text-white">{nurse.name}</p>
                             <div className="flex items-center gap-2 text-[10px] text-slate-500">
                               <span className="text-emerald-400 font-bold">★ {nurse.rating}</span>
                               <span>• {nurse.distance}</span>
                             </div>
                           </div>
                        </div>
                        <button 
                          disabled={isDispatching}
                          onClick={() => handleDispatch(nurse)}
                          className="p-2 rounded-lg bg-blue-500 text-white opacity-0 group-hover:opacity-100 transition-all hover:scale-110 active:scale-90"
                        >
                          <ChevronRight className="w-4 h-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="p-4 rounded-2xl bg-blue-500/10 border border-blue-500/20">
                   <p className="text-[10px] font-bold text-blue-400 uppercase tracking-widest mb-1">{isRTL ? 'إجمالي الربح المتوقع' : 'Estimated Revenue'}</p>
                   <p className="text-xl font-black text-white">{(selectedVisit.price * 0.85).toFixed(2)} EGP <span className="text-xs text-slate-500 font-medium">(Net)</span></p>
                </div>
             </motion.div>
           ) : (
             <div className="h-[400px] flex flex-col items-center justify-center bg-slate-900/20 border-2 border-dashed border-white/5 rounded-[2.5rem] text-center p-8">
                <div className="w-20 h-20 rounded-full bg-slate-900 flex items-center justify-center mb-4">
                   <Clock className="w-10 h-10 text-slate-600" />
                </div>
                <h4 className="text-lg font-bold text-slate-300 mb-2">{isRTL ? 'اختر طلباً' : 'Select a request'}</h4>
                <p className="text-sm text-slate-500 max-w-xs">{isRTL ? 'اختر طلباً من القائمة اليسرى لعرض الممرضين المتاحين وتوزيع المهمة' : 'Select a request from the list to see available nurses and dispatch the visit.'}</p>
             </div>
           )}
        </div>
      </div>
    </div>
  );
}
