'use client';

import React, { useState } from 'react';
import CoverageMap from '@/components/map/CoverageMap';
import { Save, Map } from 'lucide-react';
import { getCookie } from '@/lib/api/cookies';
import { authAPI } from '@/lib/api/auth';

export default function AgencySettingsPage() {
  const [coveragePolygon, setCoveragePolygon] = useState<any>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState({ text: '', type: '' });

  // Get agencyId from authenticated user's JWT token
  const getAgencyId = () => {
    const accessToken = getCookie('access_token');
    if (!accessToken) return null;
    const userInfo = authAPI.getUserFromToken(accessToken);
    // For agency admins, we need the agency ID from the user profile
    // This is a placeholder - in production would fetch from user profile API
    return userInfo?.id || null;
  };

  const agencyId = getAgencyId();

  const handleCoverageChange = (polygon: any) => {
    setCoveragePolygon(polygon);
  };

  const saveCoverage = async () => {
    if (!coveragePolygon) {
        setMessage({ text: 'يرجى رسم نطاق التغطية أولاً', type: 'error' });
        return;
    }

    if (!agencyId) {
        setMessage({ text: 'غير مصرح لك بالوصول', type: 'error' });
        return;
    }

    setIsSaving(true);
    setMessage({ text: '', type: '' });

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || '/api/v1';
      const accessToken = getCookie('access_token');
      const response = await fetch(`${apiUrl}/agency/${agencyId}/coverage/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
        },
        body: JSON.stringify({ coverage_polygon: coveragePolygon }),
      });

      if (!response.ok) throw new Error('فشل حفظ نطاق التغطية');
      
      setMessage({ text: 'تم حفظ نطاق التغطية بنجاح', type: 'success' });
    } catch (error: any) {
      setMessage({ text: error.message, type: 'error' });
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-6" dir="rtl">
      <div>
        <h1 className="text-2xl font-bold font-inter text-white">إعدادات النطاق الجغرافي</h1>
        <p className="text-neutral-400 mt-1">قم بتحديد أو تعديل المنطقة الجغرافية التي تغطيها خدمات التمريض الخاصة بك</p>
      </div>

      {message.text && (
        <div className={`p-4 rounded-lg border ${message.type === 'error' ? 'bg-red-500/10 border-red-500/50 text-red-500' : 'bg-green-500/10 border-green-500/50 text-green-500'}`}>
          {message.text}
        </div>
      )}

      <div className="bg-neutral-800/50 border border-neutral-700 rounded-2xl overflow-hidden flex flex-col h-[600px]">
        <div className="p-4 border-b border-neutral-700 flex justify-between items-center bg-neutral-800/80">
          <h2 className="text-lg font-semibold text-white flex items-center gap-2">
            <Map className="w-5 h-5 text-amber-500" />
            الخريطة التفاعلية
          </h2>
          <button
            onClick={saveCoverage}
            disabled={isSaving}
            className="flex items-center gap-2 text-white bg-gradient-to-r from-amber-600 to-amber-500 hover:from-amber-500 hover:to-amber-400 font-medium rounded-lg text-sm px-4 py-2 transition-all disabled:opacity-50"
          >
            <Save className="w-4 h-4" />
            {isSaving ? 'جاري الحفظ...' : 'حفظ النطاق'}
          </button>
        </div>
        
        <div className="flex-1 p-4">
            <CoverageMap
               onCoverageChange={handleCoverageChange}
               isSaving={isSaving}
            />
        </div>
        
        <div className="p-4 bg-neutral-900/50 border-t border-neutral-700 text-sm text-neutral-400 flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-amber-500 inline-block animate-pulse"></span>
            استخدم أدوات الرسم على يمين الخريطة لتحديد منطقة التغطية بدقة. يمكنك مسح التحديد ورسمه مرة أخرى.
        </div>
      </div>
    </div>
  );
}
