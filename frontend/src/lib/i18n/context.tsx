'use client';

import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import type { Locale, Translations } from './types';
import { ar } from './ar';
import { en } from './en';

const translations: Record<Locale, Translations> = { ar, en };

interface LanguageContextValue {
  locale: Locale;
  dir: 'rtl' | 'ltr';
  isRTL: boolean;
  t: Translations;
  setLocale: (locale: Locale) => void;
  toggleLocale: () => void;
}

const LanguageContext = createContext<LanguageContextValue | null>(null);

const STORAGE_KEY = 'wateen-locale';

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>('ar');
  const [mounted, setMounted] = useState(false);

  // Hydrate from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY) as Locale | null;
    if (stored && (stored === 'ar' || stored === 'en')) {
      setLocaleState(stored);
    }
    setMounted(true);
  }, []);

  // Update document attributes when locale changes
  useEffect(() => {
    if (!mounted) return;
    const dir = locale === 'ar' ? 'rtl' : 'ltr';
    document.documentElement.setAttribute('lang', locale);
    document.documentElement.setAttribute('dir', dir);
  }, [locale, mounted]);

  const setLocale = useCallback((newLocale: Locale) => {
    setLocaleState(newLocale);
    localStorage.setItem(STORAGE_KEY, newLocale);
  }, []);

  const toggleLocale = useCallback(() => {
    setLocale(locale === 'ar' ? 'en' : 'ar');
  }, [locale, setLocale]);

  const dir = locale === 'ar' ? 'rtl' : 'ltr';

  const value: LanguageContextValue = {
    locale,
    dir,
    isRTL: locale === 'ar',
    t: translations[locale],
    setLocale,
    toggleLocale,
  };

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage(): LanguageContextValue {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
}
