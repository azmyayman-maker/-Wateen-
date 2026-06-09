import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

export const CommandCenterHeatmap: React.FC<{ token: string }> = ({ token }) => {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    // SuperAdmin specialized WebSocket stream
    const ws = new WebSocket(`ws://localhost:8000/ws/dashboard/superadmin/`, [token]);
    ws.onmessage = (event) => {
      const payload = JSON.parse(event.data);
      if (payload.type === 'dashboard.superadmin') {
        setData(payload.data);
      }
    };
    return () => ws.close();
  }, [token]);

  if (!data) return <div dir="rtl" className="p-4 text-center animate-pulse">جاري تحميل الخريطة المجمعة للجمهورية...</div>;

  return (
    <div dir="rtl" className="bg-slate-900 text-white rounded-xl p-6 shadow-xl glassmorphism-dark">
      <h2 className="text-xl font-bold mb-4">عين النسر (Eagle&apos;s Eye) - خريطة التوزيع</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-slate-800 p-4 rounded-lg">
          <span className="block text-slate-400 text-sm">البنية التحتية (Redis)</span>
          <span className="text-2xl font-mono text-emerald-400">{data.infrastructure.redis_used_memory}</span>
        </div>
        <div className="bg-slate-800 p-4 rounded-lg">
          <span className="block text-slate-400 text-sm">توقيت البث</span>
          <span className="text-sm font-mono text-slate-300">{new Date(data.timestamp).toLocaleTimeString('ar-EG')}</span>
        </div>
      </div>

      <div className="h-96 w-full bg-slate-800 rounded-lg flex items-center justify-center relative overflow-hidden border border-slate-700">
        {/* Geographic representation clustering heatpoints logically */}
        {data.heatmap.map((point: any, idx: number) => (
          <motion.div
            key={idx}
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 0.8 }}
            className="absolute rounded-full bg-rose-500 flex items-center justify-center text-xs font-bold"
            style={{
              width: `${point.count * 10}px`, 
              height: `${point.count * 10}px`,
              left: `${Math.random() * 80 + 10}%`, // Prototype placement logic overlay
              top: `${Math.random() * 80 + 10}%`,
            }}
          >
            {point.count}
          </motion.div>
        ))}
        <span className="absolute bottom-4 left-4 text-xs text-slate-500 bg-black/50 px-2 py-1 rounded">
          * الإحداثيات مموهة قانونياً بموجب ST_SnapToGrid 
        </span>
      </div>
    </div>
  );
};
