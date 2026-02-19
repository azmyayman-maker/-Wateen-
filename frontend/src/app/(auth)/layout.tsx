import { Card } from '@/components/shared'

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-surface p-4">
      <Card variant="elevated" padding="lg" className="w-full max-w-md">
        {children}
      </Card>
    </div>
  )
}
