import { Button, Input } from '@/components/shared'

export default function RegisterPage() {
  return (
    <div className="space-y-6">
      <div className="text-center">
        <h1 className="text-2xl font-bold text-text-primary">إنشاء حساب</h1>
        <p className="mt-2 text-sm text-text-secondary">انضم إلى منصة وتين</p>
      </div>
      
      <form className="space-y-4">
        <Input
          label="الاسم الكامل"
          type="text"
          required
          placeholder="أدخل اسمك"
        />
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
        <Input
          label="تأكيد كلمة المرور"
          type="password"
          required
          placeholder="••••••••"
        />
        <Button type="submit" className="w-full">
          إنشاء الحساب
        </Button>
      </form>
      
      <p className="text-center text-sm text-text-secondary">
        لديك حساب بالفعل؟{' '}
        <Link href="/login" className="text-primary font-medium hover:underline">
          سجل دخولك
        </a>
      </p>
    </div>
  )
}
