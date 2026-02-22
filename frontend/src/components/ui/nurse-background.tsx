'use client';

import { useEffect, useState } from 'react';
import { DotOrbit } from '@paper-design/shaders-react';

interface NurseBackgroundProps {
  isOnline: boolean;
  height?: number;
}

/**
 * Nurse Dashboard Background using DotOrbit shader.
 * - Online:  Teal/green tactical pulse — shows the nurse is active
 * - Offline: Dark muted dots — standby mode
 */
export function NurseBackground({ isOnline, height = 600 }: NurseBackgroundProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => setMounted(true), []);

  if (!mounted) {
    return (
      <div
        className="absolute inset-0 bg-gradient-to-br from-slate-950 via-slate-900 to-[#16615F]/10"
        style={{ height }}
      />
    );
  }

  return (
    <div className="absolute inset-0 overflow-hidden" style={{ height }}>
      {/* DotOrbit — correct API: colorBack (string), colors (string[]) */}
      <DotOrbit
        className="w-full h-full absolute inset-0"
        colorBack={isOnline ? '#020617' : '#080f1c'}
        colors={
          isOnline
            ? ['#16615F', '#79B253', '#FD8839', '#F32D17', '#16615F', '#79B253']
            : ['#1e293b', '#0f172a', '#162530', '#1e293b']
        }
        size={isOnline ? 0.32 : 0.16}
        sizeRange={0.25}
        spreading={isOnline ? 0.5 : 0.2}
        speed={isOnline ? 0.8 : 0.12}
        stepsPerColor={isOnline ? 2 : 1}
      />

      {/* Tactical vignette */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background: isOnline
            ? 'radial-gradient(ellipse 90% 70% at 50% 30%, transparent 25%, rgba(2,6,23,0.55) 100%)'
            : 'radial-gradient(ellipse 90% 70% at 50% 30%, transparent 15%, rgba(2,6,23,0.75) 100%)',
        }}
      />

      {/* Always-on readability veil */}
      <div className="absolute inset-0 pointer-events-none bg-slate-950/30" />

      {/* Bottom gradient fade — seamless transition to content */}
      <div
        className="absolute bottom-0 left-0 right-0 pointer-events-none z-10"
        style={{
          height: '48%',
          background:
            'linear-gradient(to bottom, transparent 0%, rgba(2,6,23,0.5) 35%, rgba(2,6,23,0.92) 70%, rgb(2,6,23) 100%)',
        }}
      />

      {/* Top fade */}
      <div
        className="absolute top-0 left-0 right-0 pointer-events-none"
        style={{
          height: 60,
          background: 'linear-gradient(to bottom, rgba(2,6,23,0.6) 0%, transparent 100%)',
        }}
      />
    </div>
  );
}
