'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { ShieldCheck, Building2, MapPin, Building, Phone } from 'lucide-react';

export default function AgencyRegisterPage() {
  const router = useRouter();
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError('');
    setIsLoading(true);

    const formData = new FormData(event.currentTarget);
    const data = {
      manager_name: formData.get('manager_name'),
      commercial_registry: formData.get('commercial_registry'),
      moh_license_number: formData.get('moh_license_number'),
      tax_id: formData.get('tax_id'),
      admin_national_id: formData.get('admin_national_id'),
      admin_phone_number: formData.get('admin_phone_number'),
      admin_password: formData.get('admin_password'),
    };

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || '/api/v1';
      const response = await fetch(`${apiUrl}/agency/register/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'Registration failed. Please check the inputs.');
      }

      // Onboarding success. Redirect to pending approval state or login
      router.push('/login?registered=agency');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="flex h-screen bg-neutral-900 text-white overflow-hidden">
      {/* Left panel */}
      <div className="hidden lg:flex w-1/2 bg-neutral-800 flex-col justify-center items-center p-12 relative overflow-hidden">
        {/* Dynamic Background */}
        <div className="absolute top-0 right-0 w-full h-full bg-gradient-to-bl from-amber-500/20 to-transparent"></div>
        <div className="relative z-10 text-center max-w-md">
          <Building2 className="w-20 h-20 mx-auto text-amber-500 mb-6" />
          <h2 className="text-4xl font-bold mb-4 font-outfit text-transparent bg-clip-text bg-gradient-to-r from-amber-200 to-amber-500">
            أهلاً بك في شبكة خدمات وتين
          </h2>
          <p className="text-neutral-400 text-lg">
            سجل شركتك أو وكالتك الطبية للانضمام إلى منصة الموردين وإدارة كادرك التمريضي بسهولة واحترافية.
          </p>
        </div>
      </div>

      {/* Right panel */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-neutral-900 overflow-y-auto">
        <div className="max-w-md w-full my-auto">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold font-inter mb-2">تسجيل شركة جديدة</h1>
            <p className="text-neutral-400 text-sm">أدخل بيانات الشركة لإنشاء حساب الإدارة الخاص بك</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4" dir="rtl">
            {error && (
              <div className="p-3 rounded-md bg-red-500/10 border border-red-500/50 text-red-500 text-sm">
                {error}
              </div>
            )}

            <div className="space-y-4">
              <h3 className="text-sm font-semibold text-neutral-400 border-b border-neutral-800 pb-2">بيانات الشركة</h3>
              <div>
                <label className="block text-sm font-medium text-neutral-300 mb-1">اسم المسؤول / المدير *</label>
                <div className="relative">
                  <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none text-neutral-500">
                    <ShieldCheck className="w-5 h-5" />
                  </div>
                  <input
                    type="text"
                    name="manager_name"
                    required
                    className="w-full bg-neutral-800 border border-neutral-700 text-white rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500 block p-2.5 pr-10"
                    placeholder="الاسم الكامل"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-neutral-300 mb-1">رقم السجل التجاري *</label>
                  <input
                    type="text"
                    name="commercial_registry"
                    required
                    className="w-full bg-neutral-800 border border-neutral-700 text-white rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500 block p-2.5"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-neutral-300 mb-1">ترخيص وزارة الصحة *</label>
                  <input
                    type="text"
                    name="moh_license_number"
                    required
                    className="w-full bg-neutral-800 border border-neutral-700 text-white rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500 block p-2.5"
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-neutral-300 mb-1">البطاقة الضريبية *</label>
                  <input
                    type="text"
                    name="tax_id"
                    required
                    className="w-full bg-neutral-800 border border-neutral-700 text-white rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500 block p-2.5"
                    placeholder="000-000-000"
                  />
              </div>

              <h3 className="text-sm font-semibold text-neutral-400 border-b border-neutral-800 pb-2 mt-6">بيانات الدخول (مدير النظام)</h3>
              
              <div>
                <label className="block text-sm font-medium text-neutral-300 mb-1">الرقم القومي لمدير الحساب *</label>
                <input
                  type="text"
                  name="admin_national_id"
                  required
                  maxLength={14}
                  className="w-full bg-neutral-800 border border-neutral-700 text-white rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500 block p-2.5 text-left"
                  placeholder="14 digits"
                  dir="ltr"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-neutral-300 mb-1">رقم الهاتف *</label>
                <input
                  type="tel"
                  name="admin_phone_number"
                  required
                  className="w-full bg-neutral-800 border border-neutral-700 text-white rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500 block p-2.5 text-left"
                  placeholder="01xxxxxxxxx"
                  dir="ltr"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-neutral-300 mb-1">كلمة المرور *</label>
                <input
                  type="password"
                  name="admin_password"
                  required
                  className="w-full bg-neutral-800 border border-neutral-700 text-white rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500 block p-2.5 text-left"
                  dir="ltr"
                />
              </div>

            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full text-white bg-gradient-to-r from-amber-600 to-amber-500 hover:from-amber-500 hover:to-amber-400 focus:ring-4 focus:outline-none focus:ring-amber-800 font-medium rounded-lg text-sm px-5 py-3 text-center transition-all duration-300 shadow-lg shadow-amber-900/20 disabled:opacity-50 mt-6"
            >
              {isLoading ? 'جاري إرسال الطلب...' : 'تسجيل الشركة والمتابعة'}
            </button>
            <div className="text-sm font-light text-neutral-400 text-center mt-4">
              لديك حساب بالفعل؟{' '}
              <Link href="/login" className="font-medium text-amber-500 hover:underline">
                تسجيل الدخول
              </Link>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
