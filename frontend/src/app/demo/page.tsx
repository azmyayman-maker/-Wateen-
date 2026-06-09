"use client";

import { useState } from 'react';
import dynamic from 'next/dynamic';
import { WateenCanvasLogo } from '../../components/WateenCanvasLogo';

const PatientLocationPicker = dynamic(() => import('../../components/maps/PatientLocationPicker'), { ssr: false });
const NurseLiveTracker = dynamic(() => import('../../components/NurseLiveTracker').then(mod => mod.NurseLiveTracker), { ssr: false });

export default function DemoHub() {
  const [activeTab, setActiveTab] = useState<'logo' | 'location' | 'tracker'>('logo');

  return (
    <div className="w-full min-h-screen bg-slate-50 flex flex-col font-sans" dir="rtl">
      {/* Navigation Bar */}
      <nav className="p-4 bg-white shadow-sm border-b border-slate-200 flex flex-wrap justify-center gap-4 sticky top-0 z-50">
        <button 
          onClick={() => setActiveTab('logo')}
          className={`px-4 py-2 rounded-lg font-bold transition-colors ${activeTab === 'logo' ? 'bg-[#0088FF] text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}`}
        >
          عارض الشعار
        </button>
        <button 
          onClick={() => setActiveTab('location')}
          className={`px-4 py-2 rounded-lg font-bold transition-colors ${activeTab === 'location' ? 'bg-[#0088FF] text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}`}
        >
          محدد الموقع 
        </button>
        <button 
          onClick={() => setActiveTab('tracker')}
          className={`px-4 py-2 rounded-lg font-bold transition-colors ${activeTab === 'tracker' ? 'bg-[#0088FF] text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}`}
        >
          التتبع الحي للممرض
        </button>
      </nav>

      {/* Main Content Area */}
      <div className="flex-1 w-full relative">
        {activeTab === 'logo' && (
          <div className="flex flex-col items-center justify-center min-h-[80vh]">
             <WateenCanvasLogo width={500} height={500} />
          </div>
        )}

        {activeTab === 'location' && (
          <div className="absolute inset-0 w-full h-full overflow-hidden">
            <PatientLocationPicker defaultCenter={[30.0444, 31.2357]} onConfirm={(f) => console.log(f)} />
          </div>
        )}
        
        {activeTab === 'tracker' && (
          <div className="absolute inset-0 w-full h-full overflow-hidden">
            <NurseLiveTracker />
          </div>
        )}
      </div>
    </div>
  );
}
