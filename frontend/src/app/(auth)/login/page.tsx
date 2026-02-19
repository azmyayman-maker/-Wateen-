import Link from 'next/link'
import { Button, Input } from '@/components/shared'

export default function LoginPage() {
  return (
    <div className="space-y-6">
      <div className="text-center">
        <h1 className="text-2xl font-bold text-text-primary">تسجيل الدخول</h1>
        <p className="mt-2 text-sm text-text-secondary">مرحباً بعودتك</p>
      </div>
      
      <form action="#" method="post" className="space-y-4">
        <Input
          label="البريد الإلكتروني"
          type="email"
          required
          placeholder="example@email.com"
        />
        <Input
          label="كلمة المرور"
          type="password"
          required
          placeholder="••••••••"
        />
        <Button type="submit" className="w-full">
          تسجيل الدخول
        </Button>
      </form>
      
      <p className="text-center text-sm text-text-secondary">
        ليس لديك حساب؟{' '}
        <Link href="/register" className="text-primary font-medium hover:underline">
          سجل الآن
        </Link>
      </p>
    </div>
  )
}
