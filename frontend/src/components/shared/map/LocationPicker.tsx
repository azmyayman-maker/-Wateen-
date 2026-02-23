"use client";

import React, { useMemo } from 'react';
import dynamic from 'next/dynamic';
import { MapPin, Navigation, Crosshair } from 'lucide-react';
import { cn } from '@/lib/utils';

interface LocationPickerProps {
  initialLocation?: [number, number]; // [lat, lng]
  onLocationSelect?: (lat: number, lng: number) => void;
  readOnly?: boolean;
  className?: string;
}

export default function LocationPicker({ 
  initialLocation = [30.0444, 31.2357], // Default to Cairo
  onLocationSelect,
  readOnly = false,
  className
}: LocationPickerProps) {
  
  // Dynamically import the map to avoid SSR issues with Leaflet
  const Map = useMemo(() => dynamic(
    () => import('./MapCore'),
    { 
      loading: () => (
        <div className="w-full h-full flex flex-col items-center justify-center bg-slate-900/50 backdrop-blur-sm rounded-2xl border border-white/10">
          <div className="relative flex items-center justify-center mb-4">
            <div className="absolute w-12 h-12 bg-indigo-500/20 rounded-full animate-ping" />
            <MapPin className="w-8 h-8 text-indigo-400 relative z-10" />
          </div>
          <p className="text-slate-400 text-sm font-medium tracking-wide animate-pulse">Initializing Secure Map...</p>
        </div>
      ),
      ssr: false 
    }
  ), []);

  return (
    <div className={cn("relative w-full h-[400px] rounded-2xl overflow-hidden border border-white/10 shadow-2xl group", className)}>
      
      {/* 
        Map styling wrapper:
        into a sleek, dark-mode aesthetic that matches Wateen's premium UI.
      */}
      <div className="absolute inset-0 w-full h-full [&_.leaflet-tile-pane]:filter [&_.leaflet-tile-pane]:invert [&_.leaflet-tile-pane]:hue-rotate-180 [&_.leaflet-tile-pane]:brightness-[0.7] [&_.leaflet-tile-pane]:contrast-[1.3] [&_.leaflet-tile-pane]:sepia-[0.3] [&_.leaflet-container]:bg-slate-950">
        <Map 
          center={initialLocation} 
          onLocationSelect={onLocationSelect} 
          readOnly={readOnly} 
        />
      </div>

      {/* Floating UI Overlay for Interactive Mode */}
      {!readOnly && (
        <div className="absolute top-4 left-4 right-4 z-[400] flex items-center justify-between pointer-events-none gap-4">
          
          {/* Status Panel */}
          <div className="bg-slate-950/80 backdrop-blur-md border border-white/10 rounded-xl px-4 py-3 flex items-center gap-3 flex-1 max-w-sm pointer-events-auto transform transition-all duration-300 group-hover:bg-slate-900/90 shadow-[0_8px_32px_rgba(0,0,0,0.5)]">
            <div className="w-8 h-8 rounded-full bg-cyan-500/20 border border-cyan-500/30 flex items-center justify-center shrink-0">
              <Crosshair className="w-4 h-4 text-cyan-400" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-[11px] text-cyan-400/80 font-bold tracking-wider uppercase mb-0.5">Location Target</p>
              <p className="text-sm text-slate-200 font-medium truncate">Click map to adjust pin position</p>
            </div>
          </div>

          {/* Action Buttons */}
          <button 
            type="button"
            className="shrink-0 bg-indigo-500/20 hover:bg-indigo-500/40 text-indigo-400 border border-indigo-500/30 rounded-xl p-3 backdrop-blur-md pointer-events-auto transition-all shadow-lg hover:shadow-indigo-500/20 hover:scale-105 active:scale-95"
            onClick={() => {
              // Geolocation feature could be integrated here
              if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                  (pos) => {
                    if (onLocationSelect) {
                      onLocationSelect(pos.coords.latitude, pos.coords.longitude);
                    }
                  },
                  (err) => console.error(err)
                );
              }
            }}
          >
            <Navigation className="w-5 h-5" />
          </button>
        </div>
      )}

      {/* Readonly Marker / Visual Flourish */}
      {readOnly && (
        <div className="absolute bottom-4 left-4 z-[400] pointer-events-none">
          <div className="bg-slate-950/80 backdrop-blur-md border border-white/10 rounded-full px-4 py-2 flex items-center gap-2 shadow-xl">
             <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
             <span className="text-xs font-medium text-slate-300">Live Tracking Active</span>
          </div>
        </div>
      )}
    </div>
  );
}
