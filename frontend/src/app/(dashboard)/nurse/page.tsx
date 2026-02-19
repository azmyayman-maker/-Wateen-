import { Card } from '@/components/shared'

export default function NurseDashboard() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-text-primary">لوحة تحكم الممرض</h1>
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <h2 className="text-lg font-semibold text-text-primary">المرضى اليوم</h2>
          <p className="mt-2 text-3xl font-bold text-primary">12</p>
        </Card>
        
        <Card>
          <h2 className="text-lg font-semibold text-text-primary">المهام المعلقة</h2>
          <p className="mt-2 text-3xl font-bold text-warning">4</p>
        </Card>
        
        <Card>
          <h2 className="text-lg font-semibold text-text-primary">المواعيد</h2>
          <p className="mt-2 text-3xl font-bold text-secondary">8</p>
        </Card>
      </div>
      
      <Card>
        <h2 className="text-lg font-semibold text-text-primary mb-4">قائمة المرضى</h2>
        <p className="text-text-secondary">لا يوجد مرضى حالياً</p>
      </Card>
    </div>
  )
}
