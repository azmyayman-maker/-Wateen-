'use client';

import Link from 'next/link'
import { useLanguage } from '@/lib/i18n'

export default function NotFound() {
  const { t } = useLanguage();

  return (
    <main id="main-content" className="min-h-screen flex flex-col items-center justify-center p-8">
      <h1 className="text-6xl font-bold text-primary">404</h1>
      <h2 className="mt-4 text-2xl font-semibold text-text-primary">{t.notFound.title}</h2>
      <p className="mt-2 text-text-secondary text-center max-w-md">
        {t.notFound.description}
      </p>
      <Link
        href="/"
        className="mt-6 inline-flex items-center justify-center font-semibold rounded-md bg-primary text-white px-4 h-10 hover:bg-primary-light transition-colors"
      >
        {t.notFound.goHome}
      </Link>
    </main>
  )
}
