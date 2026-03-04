"use client";

import React from "react";
import { motion } from "framer-motion";

interface IconProps {
  className?: string;
}

/**
 * DashboardKineticIcon — Wateen Blue #0066FF
 * Animated 4-quadrant grid with staggered pulse for Command Center sidebar.
 */
export function DashboardKineticIcon({ className }: IconProps) {
  return (
    <div className={className}>
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill="none"
        className="w-full h-full"
      >
        {/* Top-left quadrant */}
        <motion.rect
          x="3" y="3" width="8" height="8" rx="2"
          stroke="#0066FF" strokeWidth="1.5" fill="rgba(0,102,255,0.06)"
          animate={{ scale: [1, 1.05, 1], opacity: [0.7, 1, 0.7] }}
          transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut" }}
          style={{ transformOrigin: "7px 7px" }}
        />
        {/* Top-right quadrant */}
        <motion.rect
          x="13" y="3" width="8" height="8" rx="2"
          stroke="#0066FF" strokeWidth="1.5" fill="rgba(0,102,255,0.06)"
          animate={{ scale: [1, 1.05, 1], opacity: [0.7, 1, 0.7] }}
          transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut", delay: 0.3 }}
          style={{ transformOrigin: "17px 7px" }}
        />
        {/* Bottom-left quadrant */}
        <motion.rect
          x="3" y="13" width="8" height="8" rx="2"
          stroke="#0066FF" strokeWidth="1.5" fill="rgba(0,102,255,0.06)"
          animate={{ scale: [1, 1.05, 1], opacity: [0.7, 1, 0.7] }}
          transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut", delay: 0.6 }}
          style={{ transformOrigin: "7px 17px" }}
        />
        {/* Bottom-right quadrant */}
        <motion.rect
          x="13" y="13" width="8" height="8" rx="2"
          stroke="#0066FF" strokeWidth="1.5" fill="rgba(0,102,255,0.06)"
          animate={{ scale: [1, 1.05, 1], opacity: [0.7, 1, 0.7] }}
          transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut", delay: 0.9 }}
          style={{ transformOrigin: "17px 17px" }}
        />
        {/* Center pulse dot */}
        <motion.circle
          cx="12" cy="12" r="2"
          fill="#0066FF"
          animate={{ scale: [0.8, 1.3, 0.8], opacity: [0.4, 1, 0.4] }}
          transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
          style={{ transformOrigin: "12px 12px" }}
        />
      </svg>
    </div>
  );
}

/**
 * ActiveOrdersIcon — Wateen Blue #0066FF
 * Multi-ring pulse radar with strokeDasharray draw animation.
 * Wrapped in a <div> for rendering performance (rendering-animate-svg-wrapper).
 */
export function ActiveOrdersIcon({ className }: IconProps) {
  return (
    <div className={className}>
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 48 48"
        fill="none"
        className="w-full h-full"
      >
        {/* Outer detection ring - slow pulse */}
        <motion.circle
          cx="24" cy="24" r="22"
          stroke="#0066FF"
          strokeWidth="1"
          strokeLinecap="round"
          fill="none"
          initial={{ strokeDasharray: "0 140", opacity: 0 }}
          animate={{
            strokeDasharray: ["0 140", "70 70", "140 0", "70 70", "0 140"],
            opacity: [0, 0.6, 0.3, 0.6, 0],
          }}
          transition={{ duration: 5, repeat: Infinity, ease: "easeInOut" }}
        />
        {/* Middle activity ring - medium speed */}
        <motion.circle
          cx="24" cy="24" r="16"
          stroke="#0066FF"
          strokeWidth="1.5"
          strokeLinecap="round"
          fill="none"
          initial={{ strokeDasharray: "0 100", opacity: 0.3 }}
          animate={{
            strokeDasharray: ["0 100", "50 50", "100 0", "50 50", "0 100"],
            opacity: [0.3, 1, 0.5, 1, 0.3],
          }}
          transition={{ duration: 3.5, repeat: Infinity, ease: "easeInOut" }}
        />
        {/* Inner core ring */}
        <motion.circle
          cx="24" cy="24" r="10"
          stroke="#0066FF"
          strokeWidth="2"
          strokeLinecap="round"
          fill="none"
          initial={{ pathLength: 0 }}
          animate={{
            pathLength: [0, 1, 0],
            opacity: [0.5, 1, 0.5],
          }}
          transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut" }}
        />
        {/* Activity pulse line — heartbeat EKG effect */}
        <motion.path
          d="M8 24 L16 24 L18 18 L21 30 L24 20 L27 28 L30 22 L32 24 L40 24"
          stroke="#0066FF"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          fill="none"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{
            pathLength: [0, 1, 1, 0],
            opacity: [0, 1, 1, 0],
          }}
          transition={{
            duration: 2.5,
            repeat: Infinity,
            repeatDelay: 0.5,
            ease: "easeInOut",
          }}
        />
        {/* Center dot - pulsing */}
        <motion.circle
          cx="24" cy="24" r="3"
          fill="#0066FF"
          animate={{
            opacity: [0.4, 1, 0.4],
            scale: [0.8, 1.2, 0.8],
          }}
          transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
          style={{ transformOrigin: "24px 24px" }}
        />
      </svg>
    </div>
  );
}

/**
 * AvailableStaffIcon — Trust Green #00C853
 * Multi-layer user figures with staggered sine-wave floating.
 */
export function AvailableStaffIcon({ className }: IconProps) {
  return (
    <div className={className}>
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 48 48"
        fill="none"
        className="w-full h-full"
      >
        {/* Back layer person (depth effect - more muted) */}
        <motion.g
          animate={{ y: [0, -3, 0, 3, 0] }}
          transition={{ duration: 4.5, repeat: Infinity, ease: "easeInOut", delay: 0.8 }}
        >
          <circle
            cx="38" cy="14" r="4"
            stroke="#00C853"
            strokeWidth="1.5"
            strokeOpacity="0.4"
            fill="none"
          />
          <path
            d="M44 34v-3a6 6 0 0 0-6-6"
            stroke="#00C853"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeOpacity="0.4"
            fill="none"
          />
        </motion.g>

        {/* Middle person */}
        <motion.g
          animate={{ y: [0, -4, 0, 2, 0] }}
          transition={{ duration: 3.5, repeat: Infinity, ease: "easeInOut", delay: 0.3 }}
        >
          <circle
            cx="30" cy="16" r="5"
            stroke="#00C853"
            strokeWidth="1.5"
            strokeOpacity="0.7"
            fill="none"
          />
          <path
            d="M38 38v-4a6 6 0 0 0-6-6h-4"
            stroke="#00C853"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeOpacity="0.7"
            fill="none"
          />
        </motion.g>

        {/* Front layer person (fully visible) */}
        <motion.g
          animate={{ y: [0, -5, 0, 3, 0] }}
          transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
        >
          <circle
            cx="18" cy="16" r="6"
            stroke="#00C853"
            strokeWidth="2"
            fill="none"
          />
          <path
            d="M30 38v-4a8 8 0 0 0-8-8H14a8 8 0 0 0-8 8v4"
            stroke="#00C853"
            strokeWidth="2"
            strokeLinecap="round"
            fill="none"
          />
        </motion.g>

        {/* Ready pulse - glowing availability indicator */}
        <motion.circle
          cx="18" cy="16" r="9"
          stroke="#00C853"
          strokeWidth="1"
          fill="none"
          animate={{
            scale: [1, 1.4, 1.8],
            opacity: [0.5, 0.2, 0],
          }}
          transition={{ duration: 2, repeat: Infinity, ease: "easeOut" }}
          style={{ transformOrigin: "18px 16px" }}
        />
      </svg>
    </div>
  );
}

/**
 * CoverageAreasIcon — Cyan #00E5FF
 * Animated map polygon with vertex-pulsing glow dots.
 * FIXED: Removed animated r/y1/y2 attributes — uses scale/opacity only.
 */
export function CoverageAreasIcon({ className }: IconProps) {
  return (
    <div className={className}>
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 48 48"
        fill="none"
        className="w-full h-full"
      >
        {/* Map fold lines */}
        <motion.path
          d="M6 10l12-6 12 6 12-6v28l-12 6-12-6-12 6z"
          stroke="#00E5FF"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          fill="none"
          initial={{ pathLength: 0 }}
          animate={{
            pathLength: [0, 1, 1, 0],
            opacity: [0.3, 1, 0.8, 0.3],
          }}
          transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
        />
        {/* Vertical fold crease left */}
        <motion.path
          d="M18 4v28"
          stroke="#00E5FF"
          strokeWidth="1"
          fill="none"
          animate={{
            pathLength: [0, 1],
            opacity: [0.2, 0.7, 0.2],
          }}
          transition={{ duration: 2.5, repeat: Infinity, repeatType: "reverse", ease: "easeInOut" }}
        />
        {/* Vertical fold crease right */}
        <motion.path
          d="M30 10v28"
          stroke="#00E5FF"
          strokeWidth="1"
          fill="none"
          animate={{
            pathLength: [0, 1],
            opacity: [0.2, 0.7, 0.2],
          }}
          transition={{ duration: 2.5, repeat: Infinity, repeatType: "reverse", ease: "easeInOut", delay: 0.5 }}
        />

        {/* Coverage zone polygon - glowing */}
        <motion.polygon
          points="14,16 24,12 34,18 30,28 18,30 12,22"
          stroke="#00E5FF"
          strokeWidth="1.5"
          fill="rgba(0,229,255,0.08)"
          strokeLinejoin="round"
          animate={{
            opacity: [0.5, 1, 0.5],
            scale: [0.95, 1.02, 0.95],
          }}
          transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
          style={{ transformOrigin: "center" }}
        />

        {/* Vertex dots - pulsing via scale instead of r */}
        {[
          { cx: 14, cy: 16, delay: 0 },
          { cx: 24, cy: 12, delay: 0.3 },
          { cx: 34, cy: 18, delay: 0.6 },
          { cx: 30, cy: 28, delay: 0.9 },
          { cx: 18, cy: 30, delay: 1.2 },
          { cx: 12, cy: 22, delay: 1.5 },
        ].map((dot, i) => (
          <motion.circle
            key={i}
            cx={dot.cx}
            cy={dot.cy}
            r="2.5"
            fill="#00E5FF"
            animate={{
              scale: [1, 1.6, 1],
              opacity: [0.5, 1, 0.5],
            }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              ease: "easeInOut",
              delay: dot.delay,
            }}
            style={{ transformOrigin: `${dot.cx}px ${dot.cy}px` }}
          />
        ))}

        {/* Scanning line sweep — uses transform instead of y1/y2 animation */}
        <motion.g
          animate={{
            y: [-14, 14, -14],
            opacity: [0, 0.4, 0],
          }}
          transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
        >
          <line
            x1="6" y1="24" x2="42" y2="24"
            stroke="#00E5FF"
            strokeWidth="0.5"
            strokeOpacity="0.6"
          />
        </motion.g>
      </svg>
    </div>
  );
}

/**
 * TodayRevenueIcon — Urgent Amber #FFB300
 * Coin stack with continuous upward light sweep and trending arrow.
 */
export function TodayRevenueIcon({ className }: IconProps) {
  return (
    <div className={className}>
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 48 48"
        fill="none"
        className="w-full h-full"
      >
        {/* Coin stack ellipses */}
        <motion.ellipse
          cx="24" cy="36" rx="14" ry="4"
          stroke="#FFB300" strokeWidth="1.5" fill="none"
          animate={{ opacity: [0.6, 1, 0.6] }}
          transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
        />
        <motion.ellipse
          cx="24" cy="30" rx="14" ry="4"
          stroke="#FFB300" strokeWidth="1.5" fill="none"
          animate={{ opacity: [0.5, 0.9, 0.5] }}
          transition={{ duration: 2, repeat: Infinity, ease: "easeInOut", delay: 0.2 }}
        />
        <motion.ellipse
          cx="24" cy="24" rx="14" ry="4"
          stroke="#FFB300" strokeWidth="1.5" fill="none"
          animate={{ opacity: [0.4, 0.8, 0.4] }}
          transition={{ duration: 2, repeat: Infinity, ease: "easeInOut", delay: 0.4 }}
        />
        <motion.ellipse
          cx="24" cy="18" rx="14" ry="4"
          stroke="#FFB300" strokeWidth="2"
          fill="rgba(255,179,0,0.08)"
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 2, repeat: Infinity, ease: "easeInOut", delay: 0.6 }}
        />
        {/* Side walls */}
        <motion.path
          d="M10 18v18c0 2.2 6.3 4 14 4s14-1.8 14-4V18"
          stroke="#FFB300"
          strokeWidth="1.5"
          strokeLinecap="round"
          fill="none"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: [0, 1, 1] }}
          transition={{ duration: 3, repeat: Infinity, repeatType: "reverse", ease: "easeInOut" }}
        />

        {/* Trending up arrow */}
        <motion.g
          animate={{ y: [0, -6, 0], opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 2, repeat: Infinity, ease: "easeOut" }}
        >
          <path
            d="M34 14l2-6"
            stroke="#FFB300"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            fill="none"
          />
          <path
            d="M36 8h-4"
            stroke="#FFB300"
            strokeWidth="2"
            strokeLinecap="round"
            fill="none"
          />
          <path
            d="M36 8v4"
            stroke="#FFB300"
            strokeWidth="2"
            strokeLinecap="round"
            fill="none"
          />
        </motion.g>

        {/* Light sweep effect moving upward */}
        <motion.rect
          x="10" y="40" width="28" height="4"
          fill="url(#sweepGrad)"
          rx="2"
          animate={{
            y: [40, 14, 40],
            opacity: [0, 0.6, 0],
          }}
          transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut" }}
        />
        <defs>
          <linearGradient id="sweepGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#FFB300" stopOpacity="0" />
            <stop offset="50%" stopColor="#FFB300" stopOpacity="0.4" />
            <stop offset="100%" stopColor="#FFB300" stopOpacity="0" />
          </linearGradient>
        </defs>
      </svg>
    </div>
  );
}

/**
 * AnimatedSettingsIcon — Rotating gear
 */
export function AnimatedSettingsIcon({ className, color = "currentColor" }: IconProps & { color?: string }) {
  return (
    <div className={className}>
      <motion.svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill="none"
        stroke={color}
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="w-full h-full"
        animate={{ rotate: 360 }}
        transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
      >
        <path
          d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"
        />
        <circle cx="12" cy="12" r="3" />
      </motion.svg>
    </div>
  );
}

/**
 * AnimatedZapIcon — Energy Blue
 */
export function AnimatedZapIcon({ className, color = "#3b82f6" }: IconProps & { color?: string }) {
  return (
    <div className={className}>
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill="none"
        stroke={color}
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="w-full h-full"
      >
        <motion.path
          d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"
          initial={{ pathLength: 0.8, opacity: 0.8 }}
          animate={{
            pathLength: [0.8, 1, 0.8],
            opacity: [0.8, 1, 0.8],
          }}
          transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
        />
      </svg>
    </div>
  );
}

/**
 * AnimatedClockIcon — Alerts
 */
export function AnimatedClockIcon({ className, color = "currentColor" }: IconProps & { color?: string }) {
  return (
    <div className={className}>
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill="none"
        stroke={color}
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="w-full h-full"
      >
        <circle cx="12" cy="12" r="10" />
        <motion.polyline
          points="12 6 12 12 16 14"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: [0, 1] }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
        />
      </svg>
    </div>
  );
}
