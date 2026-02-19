import Link from 'next/link'

export default function NotFound() {
  return (
    <main id="main-content" className="min-h-screen flex flex-col items-center justify-center p-8">
      <h1 className="text-6xl font-bold text-primary">404</h1>
      <h2 className="mt-4 text-2xl font-semibold text-text-primary">الصفحة غير موجودة</h2>
      <p className="mt-2 text-text-secondary text-center max-w-md">
        عذراً، الصفحة التي تبحث عنها غير موجودة أو تم نقلها.
      </p>
      <Link
        href="/"
        className="mt-6 inline-flex items-center justify-center font-semibold rounded-md bg-primary text-white px-4 h-10 hover:bg-primary-light transition-colors"
      >
        العودة للصفحة الرئيسية
      </Link>
    </main>
  )
}
