import React from 'react';
import { useDashboardSocket } from '../../hooks/useDashboardSocket';
import { motion } from 'framer-motion';

// Component enforcing Arabic RTL natively
export const LiveDashboard: React.FC<{ agencyId: string; token: string }> = ({ agencyId, token }) => {
  const { metrics, isPolling, error } = useDashboardSocket(agencyId, token);

  if (error) return <div dir="rtl" className="p-4 bg-red-100 text-red-700 rounded-lg">{error}</div>;
  if (!metrics) return <div dir="rtl" className="p-4 animate-pulse">جاري تحميل لوحة التحكم...</div>;

  return (
    <div dir="rtl" className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 p-6 bg-slate-50 rounded-xl">
      
      {/* Active Visits */}
      <motion.div 
        layout
        className="p-6 bg-white rounded-xl shadow-sm border-r-4 border-r-blue-500"
      >
        <h3 className="text-gray-500 text-sm font-medium mb-2">الزيارات النشطة</h3>
        <motion.span 
          key={metrics.active_visits}
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-3xl font-bold text-gray-900"
        >
          {metrics.active_visits}
        </motion.span>
      </motion.div>

      {/* Queue Depth (Pulsing Amber if > 5) */}
      <motion.div 
        layout
        className={`p-6 bg-white rounded-xl shadow-sm border-r-4 ${metrics.queue_depth > 5 ? 'border-r-amber-500 animate-pulse' : 'border-r-green-500'}`}
      >
        <h3 className="text-gray-500 text-sm font-medium mb-2">طابور التوزيع</h3>
        <motion.span 
          key={metrics.queue_depth}
          initial={{ scale: 0.8 }}
          animate={{ scale: 1 }}
          className="text-3xl font-bold text-gray-900"
        >
          {metrics.queue_depth}
        </motion.span>
      </motion.div>

      {/* Online Nurses */}
      <motion.div 
        layout
        className="p-6 bg-white rounded-xl shadow-sm border-r-4 border-r-emerald-500"
      >
        <h3 className="text-gray-500 text-sm font-medium mb-2">الممرضون المتاحون</h3>
        <motion.span 
          key={metrics.online_nurses}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-3xl font-bold text-gray-900"
        >
          {metrics.online_nurses}
        </motion.span>
      </motion.div>

      {/* Financials (Decimal precision enforced) */}
      <div className="p-6 bg-slate-900 rounded-xl shadow-sm border-r-4 border-r-purple-500 text-white">
        <h3 className="text-slate-400 text-sm font-medium mb-4">الإيرادات الحية (ج.م)</h3>
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm">معلق:</span>
          <span className="font-mono text-amber-400">{metrics.revenue.escrowed}</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-sm">مُسوى:</span>
          <span className="font-mono text-emerald-400">{metrics.revenue.settled}</span>
        </div>
      </div>

    </div>
  );
};
