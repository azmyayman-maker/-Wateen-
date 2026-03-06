'use client';

import React from 'react';
import dynamic from 'next/dynamic';
import type L from 'leaflet';

const WateenMapInner = dynamic<WateenMapProps>(
  () => import('./WateenMapInner'),
  { 
    ssr: false, 
    loading: () => (
      <div className="w-full h-full min-h-[400px] flex items-center justify-center bg-[#0A0A1A] animate-pulse rounded-lg border border-gray-800">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-4 border-[#0066FF] border-t-transparent rounded-full animate-spin"></div>
          <span className="text-[#0066FF] font-medium font-sans">Loading Wateen GIS Map...</span>
        </div>
      </div>
    )
  }
);

export interface WateenMapProps {
  center: [number, number];
  zoom: number;
  className?: string;
  children?: React.ReactNode;
  onLoad?: (mapInstance: L.Map) => void;
}

export default function WateenMap(props: WateenMapProps) {
  return <WateenMapInner {...props} />;
}
