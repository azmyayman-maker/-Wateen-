"use client";

import dynamic from "next/dynamic";

// Next.js App Router needs to load the React Admin SPA entirely on the client side.
// We use dynamic import with ssr: false to guarantee this.
const AdminApp = dynamic(() => import("../../../../admin/App"), {
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center min-h-screen bg-slate-50">
      <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-[#0066FF]"></div>
    </div>
  ),
});

export default function AdminPage() {
  return <AdminApp />;
}
