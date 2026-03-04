'use client';

import { DashboardSidebar } from '@/components/dashboard/DashboardSidebar';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="min-h-screen bg-surface flex w-full">
      <DashboardSidebar>
        <main id="main-content" className="w-full flex-grow relative">
          {children}
        </main>
      </DashboardSidebar>
    </div>
  )
}
