"use client";

import React, { useEffect, useState, useRef, useCallback } from "react";
import { motion, useMotionValue, useTransform, animate } from "framer-motion";
import { CardSpotlight } from "../../components/ui/card-spotlight";
import { CardStack, Card } from "../../components/ui/card-stack";
import {
  ActiveOrdersIcon,
  AvailableStaffIcon,
  CoverageAreasIcon,
  TodayRevenueIcon,
} from "../../components/icons/KineticIcons";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";

// ─── Types ──────────────────────────────────────────────────────
interface MetricCardProps {
  title: string;
  value: number;
  suffix?: string;
  prefix?: string;
  subtitle: string;
  icon: React.ComponentType<{ className?: string }>;
  accentColor: string;
  spotlightColors?: number[][];
  delay?: number;
}

// Helper: hex to RGB triplet for spotlight shader
function hexToRgb(hex: string): number[] {
  const h = hex.replace('#', '');
  return [parseInt(h.slice(0,2),16), parseInt(h.slice(2,4),16), parseInt(h.slice(4,6),16)];
}

// ─── Static Data (hoisted outside component — rendering-hoist-jsx) ─────
const REVENUE_DATA = [
  { name: "٨ ص",  value: 820,  target: 1000 },
  { name: "٩ ص",  value: 1200, target: 1200 },
  { name: "١٠ ص", value: 2100, target: 1800 },
  { name: "١١ ص", value: 1800, target: 2200 },
  { name: "١٢ م", value: 3200, target: 2800 },
  { name: "١ م",  value: 2800, target: 3200 },
  { name: "٢ م",  value: 4100, target: 3500 },
  { name: "٣ م",  value: 3600, target: 3800 },
  { name: "٤ م",  value: 5200, target: 4200 },
  { name: "٥ م",  value: 4800, target: 4600 },
  { name: "٦ م",  value: 6100, target: 5000 },
  { name: "٧ م",  value: 5500, target: 5400 },
  { name: "٨ م",  value: 7200, target: 5800 },
  { name: "٩ م",  value: 6800, target: 6200 },
];

const WEEK_DATA = [
  { name: "السبت", value: 12000, target: 11000 },
  { name: "الأحد", value: 15500, target: 14000 },
  { name: "الإثنين", value: 18200, target: 17500 },
  { name: "الثلاثاء", value: 16800, target: 17000 },
  { name: "الأربعاء", value: 21000, target: 19000 },
  { name: "الخميس", value: 24500, target: 22000 },
  { name: "الجمعة", value: 28000, target: 25000 },
];

const MONTH_DATA = Array.from({ length: 30 }, (_, i) => {
  const day = i + 1;
  const base = 8000 + (day * 800);
  const variance = Math.sin(day / 1.5) * 4000;
  return {
    name: `${day} مارس`,
    value: Math.round(base + variance),
    target: Math.round(base),
  };
});


const REVENUE_TOTAL = REVENUE_DATA.reduce((s, d) => s + d.value, 0);
const REVENUE_AVG = Math.round(REVENUE_TOTAL / REVENUE_DATA.length);
const REVENUE_MAX = REVENUE_DATA.reduce((max, d) => d.value > max.value ? d : max, REVENUE_DATA[0]);
const TIME_PERIODS = ["اليوم", "الأسبوع", "الشهر"] as const;

const CARDS: Card[] = [
  { 
    id: 1, 
    name: "طلب عاجل — تمريض مكثف في المعادي", 
    designation: "منذ ٣ دقائق",
    link: "visits",
    content: (
      <div className="flex flex-col gap-3 relative">
        <div className="flex items-center gap-2">
          <div className="w-2.5 h-2.5 rounded-full bg-[#FFB300] shadow-[0_0_8px_#FFB300] animate-pulse" />
          <span className="text-white font-bold bg-[#FFB300]/20 px-2 py-0.5 rounded text-sm">حالة طارئة حرجة</span>
        </div>
        <p>مريض يتطلب رعاية مكثفة بشكل عاجل. يرجى <span className="text-[#00E5FF] font-bold">توجيه أقرب ممرض متاح</span> في المنطقة فوراً.</p>
      </div>
    )
  },
  { 
    id: 2, 
    name: "تأكيد وصول الممرضة لموقع المريض", 
    designation: "منذ ٨ دقائق",
    link: "visits",
    content: (
      <div className="flex flex-col gap-3 relative">
        <div className="flex items-center gap-2">
          <div className="w-2.5 h-2.5 rounded-full bg-[#00C853] shadow-[0_0_8px_#00C853]" />
          <span className="text-white font-bold bg-[#00C853]/20 px-2 py-0.5 rounded text-sm">تأكيد ميداني</span>
        </div>
        <p>تم تأكيد وصول طاقم التمريض بنجاح إلى <span className="text-[#0066FF] font-bold">موقع المريض</span> وجاري بدء الرعاية المجدولة.</p>
      </div>
    )
  },
  { 
    id: 3, 
    name: "ممرض غير متاح في منطقة التجمع", 
    designation: "منذ ١٢ دقيقة",
    link: "nurses",
    content: (
      <div className="flex flex-col gap-3 relative">
        <div className="flex items-center gap-2">
          <div className="w-2.5 h-2.5 rounded-full bg-[#FF5252] shadow-[0_0_8px_#FF5252] animate-pulse" />
          <span className="text-white font-bold bg-[#FF5252]/20 px-2 py-0.5 rounded text-sm">تنبيه نظام</span>
        </div>
        <p>لا يتوفر طاقم تمريض في نطاق 5كم لطلب <span className="text-[#FFB300] font-bold">تغيير قسطرة</span>. يتطلب تدخلاً يدوياً.</p>
      </div>
    )
  },
];

const GLASSMORPHIC_CARD =
  "rounded-2xl bg-[#0A0A1A]/50 backdrop-blur-2xl border border-white/[0.08] shadow-[0_8px_32px_0_rgba(0,0,0,0.4),inset_0_1px_0_0_rgba(255,255,255,0.05)] transition-all duration-300 hover:-translate-y-1 hover:border-white/[0.15] hover:shadow-[0_0_25px_rgba(0,102,255,0.15)] cursor-pointer";

// Arabic number formatter for consistent RTL numerals
const arFormatter = new Intl.NumberFormat("ar-EG");
const formatAr = (v: number) => arFormatter.format(v);

// ─── Animated Counter Hook ──────────────────────────────────────
function useAnimatedCounter(target: number, duration: number = 2, delay: number = 0) {
  const motionVal = useMotionValue(0);
  const rounded = useTransform(motionVal, (v) => Math.round(v));
  const [display, setDisplay] = useState(0);

  useEffect(() => {
    const timeout = setTimeout(() => {
      const controls = animate(motionVal, target, {
        duration,
        ease: "easeOut",
      });
      return () => controls.stop();
    }, delay * 1000);
    return () => clearTimeout(timeout);
  }, [target, duration, delay, motionVal]);

  useEffect(() => {
    const unsubscribe = rounded.on("change", (v) => setDisplay(v));
    return unsubscribe;
  }, [rounded]);

  return display;
}

// ─── MetricCard Component — CardSpotlight Edition ───────────────
interface MetricCardProps {
  title: string;
  value: number;
  suffix?: string;
  prefix?: string;
  subtitle: string;
  icon: any;
  accentColor: string;
  spotlightColors?: [number, number, number][];
  delay?: number;
  link?: string;
}

const MetricCard = React.memo(function MetricCard({
  title,
  value,
  suffix,
  prefix,
  subtitle,
  icon: Icon,
  accentColor,
  spotlightColors,
  delay = 0,
  link,
}: MetricCardProps) {
  const count = useAnimatedCounter(value, 2, delay);
  const colors = spotlightColors ?? [hexToRgb(accentColor), [139, 92, 246]];

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay, ease: "easeOut" }}
      onClick={() => {
        if (link) window.location.hash = `/${link}`;
      }}
      className={link ? "cursor-pointer" : ""}
    >
      <CardSpotlight
        radius={280}
        color={`${accentColor}20`}
        spotlightColors={colors}
        className="rounded-2xl bg-[#0A0A1A]/50 backdrop-blur-2xl border border-white/[0.08] shadow-[0_8px_32px_0_rgba(0,0,0,0.4),inset_0_1px_0_0_rgba(255,255,255,0.05)] p-6 flex flex-col justify-between cursor-pointer transition-all duration-300 hover:-translate-y-1 hover:border-white/[0.15]"
      >
        <div className="flex items-center justify-between mb-4 relative z-20">
          <h3 className="text-base font-semibold text-slate-200 font-['Fira_Sans',_'Amiri',_sans-serif]">
            {title}
          </h3>
          <div
            className="w-12 h-12 rounded-xl flex items-center justify-center transition-transform duration-300 hover:scale-110"
            style={{ backgroundColor: `${accentColor}15` }}
          >
            <Icon className="w-7 h-7" />
          </div>
        </div>
        <div className="relative z-20">
          <p className="text-3xl font-bold text-white font-['Fira_Code',_monospace] tracking-tight">
            {prefix}{count.toLocaleString("ar-EG")}{suffix}
          </p>
          <p className="text-sm text-slate-400 mt-1 font-['Fira_Sans',_'Amiri',_sans-serif]">
            {subtitle}
          </p>
        </div>
      </CardSpotlight>
    </motion.div>
  );
});

// ─── Ultra-Premium Chart Tooltip ────────────────────────────────
const PremiumTooltip = React.memo(function PremiumTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  const actual = payload.find((p: any) => p.dataKey === "value");
  const target = payload.find((p: any) => p.dataKey === "target");
  const delta = actual && target ? actual.value - target.value : 0;
  const isPositive = delta >= 0;

  return (
    <div className="bg-[#0A0A1A]/90 backdrop-blur-2xl border border-white/10 rounded-2xl px-5 py-4 shadow-[0_8px_40px_rgba(0,0,0,0.5)] min-w-[180px]">
      {/* Time label */}
      <div className="flex items-center gap-2 mb-3 pb-2 border-b border-white/5">
        <div className="w-1.5 h-1.5 rounded-full bg-[#0066FF] shadow-[0_0_6px_#0066FF]" />
        <p className="text-slate-400 text-xs font-['Fira_Sans',_sans-serif]">{label}</p>
      </div>
      {/* Actual */}
      <div className="flex items-center justify-between mb-2">
        <span className="text-slate-500 text-xs font-['Fira_Sans',_'Amiri',_sans-serif]">الفعلي</span>
        <span className="text-white font-bold text-base font-['Fira_Code',_monospace]">
          {formatAr(actual?.value ?? 0)} <span className="text-slate-500 text-xs">ج.م</span>
        </span>
      </div>
      {/* Target */}
      {target && (
        <div className="flex items-center justify-between mb-2">
          <span className="text-slate-500 text-xs font-['Fira_Sans',_'Amiri',_sans-serif]">المستهدف</span>
          <span className="text-slate-400 text-sm font-['Fira_Code',_monospace]">
            {formatAr(target.value)} <span className="text-slate-600 text-xs">ج.م</span>
          </span>
        </div>
      )}
      {/* Delta */}
      <div className={`flex items-center justify-between pt-2 border-t border-white/5 mt-1`}>
        <span className="text-slate-500 text-xs font-['Fira_Sans',_'Amiri',_sans-serif]">الفارق</span>
        <span className={`text-sm font-bold font-['Fira_Code',_monospace] ${isPositive ? 'text-[#00C853]' : 'text-[#FF5252]'}`}>
          {isPositive ? '+' : ''}{formatAr(delta)} ج.م
        </span>
      </div>
    </div>
  );
});

// ─── Custom Active Dot with Glow ────────────────────────────────
const GlowDot = (props: any) => {
  const { cx, cy } = props;
  if (!cx || !cy) return null;
  return (
    <g>
      {/* Outer glow ring */}
      <circle cx={cx} cy={cy} r={14} fill="rgba(0,102,255,0.08)" />
      <circle cx={cx} cy={cy} r={10} fill="rgba(0,102,255,0.15)" />
      {/* Inner ring */}
      <circle cx={cx} cy={cy} r={5} fill="#0066FF" stroke="rgba(0,229,255,0.6)" strokeWidth={2} />
      {/* Center dot */}
      <circle cx={cx} cy={cy} r={2} fill="#ffffff" />
    </g>
  );
};


// ─── Main Command Center ─────────────────────────────────────────
export const CommandCenter = () => {
  const [selectedPeriod, setSelectedPeriod] = useState<"اليوم" | "الأسبوع" | "الشهر">("اليوم");
  const [chartData, setChartData] = useState<any[]>(REVENUE_DATA);
  const [isConnected, setIsConnected] = useState<boolean | null>(null);

  // Period mapping for backend key
  const periodKeyMap: Record<string, "today" | "week" | "month"> = {
    "اليوم": "today",
    "الأسبوع": "week",
    "الشهر": "month"
  };

  // Fetch real data from backend
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // We use Agency 1 for demo purposes
        const response = await fetch("http://localhost:8000/api/v1/agency/1/dashboard/overview");
        if (response.ok) {
          const data = await response.json();
          if (data.chart_data && data.chart_data[periodKeyMap[selectedPeriod]]) {
            setChartData(data.chart_data[periodKeyMap[selectedPeriod]]);
            setIsConnected(true);
            return;
          }
        }
        throw new Error("Invalid response or not configured");
      } catch (err) {
        console.warn("Could not connect to database for realtime data, using fallback.", err);
        setIsConnected(false);
        // If API fails, use appropriate static data to simulate period change
        if (selectedPeriod === "اليوم") setChartData(REVENUE_DATA);
        else if (selectedPeriod === "الأسبوع") setChartData(WEEK_DATA);
        else setChartData(MONTH_DATA);
      }
    };
    fetchDashboardData();
  }, [selectedPeriod]);

  // Derive dynamic stats from current chartData
  const dynamicTotal = chartData.reduce((s, d) => s + (d.value || 0), 0);
  const dynamicAvg = chartData.length > 0 ? Math.round(dynamicTotal / chartData.length) : 0;
  const dynamicMax = chartData.length > 0 ? chartData.reduce((max, d) => (d.value || 0) > (max.value || 0) ? d : max, chartData[0]) : { name: "-", value: 0 };


  return (
    <div className="max-w-[1600px] mx-auto w-full px-2">
        {/* ═══ Header ═══ */}
        <motion.div
          className="mb-8"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: "easeOut" }}
        >
          <div className="flex items-center gap-4">
            <h1 className="text-3xl md:text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-l from-[#0066FF] to-[#FFB300] font-['Fira_Code',_monospace] inline-block">
              مركز القيادة
            </h1>
          </div>
          <p className="text-slate-400 mt-2 text-base font-['Fira_Sans',_'Amiri',_sans-serif]">
            نظرة شاملة على أداء المكتب والعمليات الحالية
          </p>
        </motion.div>

        {/* ═══ Top Row — 4 Metric Cards ═══ */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
          <MetricCard
            title="الطلبات النشطة"
            icon={ActiveOrdersIcon}
            value={24}
            subtitle="+12% عن الأسبوع الماضي"
            accentColor="#0066FF"
            spotlightColors={[[0, 102, 255], [59, 130, 246]]}
            delay={0.1}
            link="visits"
          />
          <MetricCard
            title="الكوادر المتاحة"
            icon={AvailableStaffIcon}
            value={156}
            subtitle="8 جاهزون للتوجيه الفوري"
            accentColor="#00C853"
            spotlightColors={[[0, 200, 83], [16, 185, 129]]}
            delay={0.2}
            link="nurses"
          />
          <MetricCard
            title="المناطق المغطاة"
            icon={CoverageAreasIcon}
            value={12}
            subtitle="4 مناطق ذات كثافة عالية"
            accentColor="#00E5FF"
            spotlightColors={[[0, 229, 255], [56, 189, 248]]}
            delay={0.3}
            link="coverage"
          />
          <MetricCard
            title="إيرادات اليوم"
            icon={TodayRevenueIcon}
            value={12450}
            suffix=" ج.م"
            subtitle="+5% عن متوسط الأيام السابقة"
            accentColor="#FFB300"
            spotlightColors={[[255, 179, 0], [251, 146, 60]]}
            delay={0.4}
            link="financials"
          />
        </div>

        {/* ═══ Middle Row — Chart + Alerts ═══ */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
          {/* Revenue Chart — 8 cols (RTL start = right) */}
          <motion.div
            className={GLASSMORPHIC_CARD + " lg:col-span-8 p-6"}
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.5, ease: "easeOut" }}
          >
            {/* ═══ Chart Header — Title + Stats + Period Selector ═══ */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6 gap-4">
              <div>
                <h2 className="text-lg font-bold text-slate-100 font-['Fira_Sans',_'Amiri',_sans-serif] mb-1">
                  رادار العمليات الحية
                </h2>
                <div className="flex items-center gap-4 text-xs font-['Fira_Code',_monospace]">
                  <span className="text-slate-400">
                    الإجمالي: <span className="text-white font-semibold">{formatAr(dynamicTotal)} ج.م</span>
                  </span>
                  <span className="text-slate-600">|</span>
                  <span className="text-slate-400">
                    الذروة: <span className="text-[#00E5FF] font-semibold">{dynamicMax.name}</span>
                  </span>
                  <span className="text-slate-600">|</span>
                  <span className="text-slate-400">
                    المتوسط: <span className="text-[#FFB300] font-semibold">{formatAr(dynamicAvg)} ج.م</span>
                  </span>
                </div>
              </div>
              {/* Period Pills — Premium Sliding Selector */}
              <div className="flex items-center gap-1 bg-white/[0.02] rounded-xl p-1 border border-white/5 relative">
                {TIME_PERIODS.map((period) => {
                  const isActive = selectedPeriod === period;
                  return (
                    <button
                      key={period}
                      onClick={() => setSelectedPeriod(period)}
                      className={`relative px-5 py-2 rounded-lg text-xs font-bold transition-colors duration-300 font-['Fira_Sans',_sans-serif] cursor-pointer z-10 ${
                        isActive ? 'text-white' : 'text-slate-500 hover:text-slate-300'
                      }`}
                    >
                      {isActive && (
                        <motion.div
                          layoutId="active-period-pill"
                          className="absolute inset-0 bg-gradient-to-r from-[#0066FF] to-[#00E5FF] rounded-lg shadow-[0_0_20px_rgba(0,102,255,0.3)] z-[-1]"
                          transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                        />
                      )}
                      <span className="relative z-10">{period}</span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* ═══ Legend ═══ */}
            <div className="flex items-center gap-5 mb-4 text-xs font-['Fira_Sans',_'Amiri',_sans-serif]">
              <div className="flex items-center gap-2">
                <div className="w-3 h-0.5 rounded-full bg-gradient-to-r from-[#0066FF] to-[#00E5FF]" />
                <span className="text-slate-400">الإيرادات الفعلية</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-0.5 rounded-full bg-[#FFB300]/60" style={{ borderTop: '1px dashed #FFB300' }} />
                <span className="text-slate-500">المستهدف</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-px bg-[#FF5252]/40" style={{ borderTop: '1px dashed #FF5252' }} />
                <span className="text-slate-500">المتوسط</span>
              </div>
            </div>

            {/* ═══ Chart ═══ */}
            <div className="w-full" dir="ltr" style={{ height: 320 }}>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <defs>
                    {/* Primary area gradient — Wateen Blue */}
                    <linearGradient id="wateenGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#0066FF" stopOpacity={0.35} />
                      <stop offset="40%" stopColor="#0066FF" stopOpacity={0.12} />
                      <stop offset="100%" stopColor="#0066FF" stopOpacity={0} />
                    </linearGradient>
                    {/* Target area gradient — Amber */}
                    <linearGradient id="targetGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#FFB300" stopOpacity={0.08} />
                      <stop offset="100%" stopColor="#FFB300" stopOpacity={0} />
                    </linearGradient>
                    {/* Line gradient — Blue to Cyan */}
                    <linearGradient id="lineGradient" x1="0" y1="0" x2="1" y2="0">
                      <stop offset="0%" stopColor="#0066FF" />
                      <stop offset="50%" stopColor="#338FFF" />
                      <stop offset="100%" stopColor="#00E5FF" />
                    </linearGradient>
                    {/* Glow filter for main line */}
                    <filter id="lineGlow" x="-20%" y="-20%" width="140%" height="140%">
                      <feGaussianBlur in="SourceGraphic" stdDeviation="3" result="blur" />
                      <feColorMatrix in="blur" type="matrix" values="0 0 0 0 0 0 0 0 0 0.4 0 0 0 0 1 0 0 0 0.6 0" />
                      <feMerge>
                        <feMergeNode />
                        <feMergeNode in="SourceGraphic" />
                      </feMerge>
                    </filter>
                  </defs>

                  {/* Grid */}
                  <CartesianGrid
                    strokeDasharray="2 6"
                    stroke="rgba(255,255,255,0.03)"
                    vertical={false}
                  />

                  {/* X Axis */}
                  <XAxis
                    dataKey="name"
                    stroke="transparent"
                    tick={{ fill: "rgba(255,255,255,0.35)", fontSize: 11, fontFamily: "'Fira Sans', sans-serif" }}
                    axisLine={false}
                    tickLine={false}
                    tickMargin={12}
                  />

                  {/* Y Axis */}
                  <YAxis
                    stroke="transparent"
                    tick={{ fill: "rgba(255,255,255,0.25)", fontSize: 10, fontFamily: "'Fira Code', monospace" }}
                    tickFormatter={formatAr}
                    axisLine={false}
                    tickLine={false}
                    width={52}
                    tickMargin={8}
                  />

                  {/* Average Reference Line */}
                  {dynamicAvg > 0 && (
                    <ReferenceLine
                      y={dynamicAvg}
                      stroke="rgba(255,82,82,0.25)"
                      strokeDasharray="4 4"
                      label={{
                        value: `⌀ ${formatAr(dynamicAvg)}`,
                        position: 'insideTopRight',
                        fill: 'rgba(255,82,82,0.5)',
                        fontSize: 10,
                        fontFamily: "'Fira Code', monospace",
                      }}
                    />
                  )}

                  {/* Tooltip */}
                  <Tooltip
                    content={<PremiumTooltip />}
                    cursor={{
                      stroke: 'rgba(0,102,255,0.15)',
                      strokeWidth: 1,
                      strokeDasharray: '4 4',
                    }}
                  />

                  {/* Target Area — dashed amber line + faint fill */}
                  <Area
                    type="monotone"
                    dataKey="target"
                    stroke="rgba(255,179,0,0.35)"
                    strokeWidth={1.5}
                    strokeDasharray="6 4"
                    fill="url(#targetGradient)"
                    dot={false}
                    activeDot={false}
                    isAnimationActive={true}
                    animationDuration={600}
                  />

                  {/* Primary Revenue Area — glowing blue line */}
                  <Area
                    type="monotone"
                    dataKey="value"
                    stroke="url(#lineGradient)"
                    strokeWidth={2.5}
                    fill="url(#wateenGradient)"
                    dot={false}
                    activeDot={<GlowDot />}
                    filter="url(#lineGlow)"
                    isAnimationActive={true}
                    animationDuration={800}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </motion.div>

          {/* Alerts Panel — 4 cols (RTL end = left) */}
          <motion.div
            className="lg:col-span-4 p-5 flex flex-col items-center justify-center w-full"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6, delay: 0.6, ease: "easeOut" }}
          >
            <div className="w-full flex items-center justify-between mb-8 pb-3 border-b border-white/5">
              <h2 className="text-lg font-bold text-slate-100 font-['Fira_Sans',_sans-serif]">
                أحدث التنبيهات
              </h2>
              <motion.div
                className="w-2.5 h-2.5 rounded-full bg-[#FFB300] shadow-[0_0_10px_#FFB300]"
                animate={{ opacity: [1, 0.4, 1] }}
                transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
              />
            </div>
            
            <div className="flex-1 w-full flex justify-center mt-4">
              <CardStack items={CARDS} />
            </div>
          </motion.div>
        </div>
        
        {/* Bottom Padding for Full Scroll Clearance */}
        <div className="h-40 w-full flex items-end justify-center pb-8 opacity-50">
          <p className="text-xs text-slate-500 font-['Fira_Code',_monospace]">WATEEN B2B — COMMAND CENTER VERIFIED</p>
        </div>
    </div>
  );
};
