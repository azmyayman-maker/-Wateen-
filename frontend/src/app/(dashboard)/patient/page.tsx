import { Card } from '@/components/shared'

export default function PatientDashboard() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-text-primary">لوحة تحكم المريض</h1>
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <h2 className="text-lg font-semibold text-text-primary">المواعيد القادمة</h2>
          <p className="mt-2 text-3xl font-bold text-primary">3</p>
        </Card>
        
        <Card>
          <h2 className="text-lg font-semibold text-text-primary">الوصفات الطبية</h2>
          <p className="mt-2 text-3xl font-bold text-secondary">5</p>
        </Card>
        
        <Card>
          <h2 className="text-lg font-semibold text-text-primary">النتائج الطبية</h2>
          <p className="mt-2 text-3xl font-bold text-success">2</p>
        </Card>
      </div>
      
      <Card>
        <h2 className="text-lg font-semibold text-text-primary mb-4">النشاط الأخير</h2>
        <p className="text-text-secondary">لا يوجد نشاط حديث</p>
      </Card>
    </div>
  )
}
