'use client';

import React, { useState, useEffect } from 'react';
import { ShieldCheck, CheckCircle2, XCircle, Search, Clock, Building2 } from 'lucide-react';

interface Agency {
  id: string;
  manager_name: string;
  commercial_registry: string;
  moh_license_number: string;
  tax_id: string;
  status: 'pending' | 'verified' | 'suspended' | 'rejected';
  created_at: string;
}

export default function AgencyReviewQueue() {
  const [agencies, setAgencies] = useState<Agency[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchAgencies();
  }, []);

  const fetchAgencies = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || '/api/v1';
      // In a real app we would have an endpoint specifically for the admin to list agencies.
      // E.g., GET /api/v1/admin/agencies/
      // For this MVP frontend mock, we will show a placeholder if endpoint isn't wired.
      // We will pretend we fetched this data.
      setTimeout(() => {
        setAgencies([
          {
            id: 'mock-uuid-1',
            manager_name: 'أحمد محمود',
            commercial_registry: 'CR-10293847',
            moh_license_number: 'MOH-998877',
            tax_id: '123-456-789',
            status: 'pending',
            created_at: new Date().toISOString()
          },
        ]);
        setIsLoading(false);
      }, 1000);
      
    } catch (err: any) {
      setError(err.message);
      setIsLoading(false);
    }
  };

  const handleStatusUpdate = async (id: string, newStatus: 'verified' | 'rejected') => {
    try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || '/api/v1';
        // Note: Requires JWT access token in real app
        // await fetch(`${apiUrl}/admin/agencies/${id}/approve/`, { ... })
        
        // Mock UI Update for MVP demonstration
        setAgencies(prev => 
            prev.map(a => a.id === id ? { ...a, status: newStatus } : a)
        );
    } catch (err) {
        alert('Failed to update status');
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-12 text-amber-500">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6" dir="rtl">
      <div>
        <h1 className="text-2xl font-bold font-inter text-white">إدارة طلبات انضمام الشركات</h1>
        <p className="text-neutral-400 mt-1">مراجعة والتحقق من التراخيص الطبية والسجلات التجارية للوكالات الجديدة</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-neutral-800/50 border border-neutral-700 p-6 rounded-2xl flex items-center justify-between">
            <div>
                <p className="text-neutral-400 text-sm">بانتظار المراجعة</p>
                <p className="text-3xl font-bold text-amber-500 mt-1">
                    {agencies.filter(a => a.status === 'pending').length}
                </p>
            </div>
            <div className="bg-amber-500/10 p-3 rounded-full">
                <Clock className="w-8 h-8 text-amber-500" />
            </div>
        </div>
        
        <div className="bg-neutral-800/50 border border-neutral-700 p-6 rounded-2xl flex items-center justify-between">
            <div>
                <p className="text-neutral-400 text-sm">الشركات المعتمدة</p>
                <p className="text-3xl font-bold text-green-500 mt-1">
                    {agencies.filter(a => a.status === 'verified').length}
                </p>
            </div>
            <div className="bg-green-500/10 p-3 rounded-full">
                <ShieldCheck className="w-8 h-8 text-green-500" />
            </div>
        </div>
      </div>

      <div className="bg-neutral-800/50 border border-neutral-700 rounded-2xl overflow-hidden">
        <div className="p-4 border-b border-neutral-700 flex justify-between items-center bg-neutral-800/80">
          <h2 className="text-lg font-semibold text-white flex items-center gap-2">
            <Building2 className="w-5 h-5 text-amber-500" />
            سجل الشركات
          </h2>
          <div className="relative">
            <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none text-neutral-500">
              <Search className="w-4 h-4" />
            </div>
            <input
              type="text"
              className="bg-neutral-900 border border-neutral-700 text-white text-sm rounded-lg focus:ring-amber-500 focus:border-amber-500 block w-64 pr-10 p-2.5"
              placeholder="البحث برقم السجل التجاري..."
            />
          </div>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full text-right text-sm text-neutral-400">
            <thead className="text-xs text-neutral-300 uppercase bg-neutral-900/50 border-b border-neutral-700">
              <tr>
                <th scope="col" className="px-6 py-4">اسم الشركة / المدير</th>
                <th scope="col" className="px-6 py-4">السجل التجاري</th>
                <th scope="col" className="px-6 py-4">التصريح الطبي (MOH)</th>
                <th scope="col" className="px-6 py-4">الحالة</th>
                <th scope="col" className="px-6 py-4">الإجراء</th>
              </tr>
            </thead>
            <tbody>
              {agencies.map((agency) => (
                <tr key={agency.id} className="bg-neutral-800/30 border-b border-neutral-700 hover:bg-neutral-800/50 transition-colors">
                  <td className="px-6 py-4 font-medium text-white">
                    {agency.manager_name}
                  </td>
                  <td className="px-6 py-4 font-mono text-neutral-300">
                    {agency.commercial_registry}
                  </td>
                  <td className="px-6 py-4 font-mono text-neutral-300">
                    {agency.moh_license_number}
                  </td>
                  <td className="px-6 py-4">
                    {agency.status === 'pending' && (
                      <span className="bg-amber-500/10 text-amber-500 text-xs font-medium px-2.5 py-1 rounded-full border border-amber-500/20">قيد المراجعة</span>
                    )}
                    {agency.status === 'verified' && (
                      <span className="bg-green-500/10 text-green-500 text-xs font-medium px-2.5 py-1 rounded-full border border-green-500/20">معتمد</span>
                    )}
                    {agency.status === 'rejected' && (
                      <span className="bg-red-500/10 text-red-500 text-xs font-medium px-2.5 py-1 rounded-full border border-red-500/20">مرفوض</span>
                    )}
                  </td>
                  <td className="px-6 py-4">
                    {agency.status === 'pending' ? (
                        <div className="flex gap-2">
                           <button 
                             onClick={() => handleStatusUpdate(agency.id, 'verified')}
                             className="flex items-center gap-1 px-3 py-1.5 bg-green-500/10 hover:bg-green-500/20 text-green-500 rounded-lg border border-green-500/50 transition-colors">
                               <CheckCircle2 className="w-4 h-4" />
                               قبول
                           </button>
                           <button 
                             onClick={() => handleStatusUpdate(agency.id, 'rejected')}
                             className="flex items-center gap-1 px-3 py-1.5 bg-red-500/10 hover:bg-red-500/20 text-red-500 rounded-lg border border-red-500/50 transition-colors">
                               <XCircle className="w-4 h-4" />
                               رفض
                           </button>
                        </div>
                    ) : (
                        <span className="text-neutral-500 text-xs">تم الإجراء</span>
                    )}
                  </td>
                </tr>
              ))}
              {agencies.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-neutral-500">
                    لا توجد طلبات شركات مسجلة.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
