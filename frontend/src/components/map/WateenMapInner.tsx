'use client';

import React, { useEffect } from 'react';
import { MapContainer, TileLayer } from 'react-leaflet';
import L from 'leaflet';

// Import CSS
import 'leaflet/dist/leaflet.css';
import '@geoman-io/leaflet-geoman-free/dist/leaflet-geoman.css';

interface WateenMapInnerProps {
  center: [number, number];
  zoom: number;
  className?: string; // e.g., tailwind classes for height/width
  children?: React.ReactNode;
  onLoad?: (mapInstance: L.Map) => void;
}

export default function WateenMapInner({
  center,
  zoom,
  className = 'w-full h-full',
  children,
  onLoad
}: WateenMapInnerProps) {
  const mapRef = React.useCallback((map: L.Map | null) => {
    if (map && onLoad) {
      onLoad(map);
    }
  }, [onLoad]);
  useEffect(() => {
    // Fix Leaflet's default icon missing issue in Webpack/Next.js
    // By default, Leaflet tries to load marker icons via CSS url() which Next.js can mangle or fail to resolve.
    delete (L.Icon.Default.prototype as any)._getIconUrl;
    L.Icon.Default.mergeOptions({
      iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
      iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
      shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
    });
  }, []);

  return (
    <div className={`wateen-map-container ${className}`}>
      <MapContainer
        center={center}
        zoom={zoom}
        style={{ height: '100%', width: '100%', zIndex: 0 }}
        ref={mapRef}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {children}
      </MapContainer>
    </div>
  );
}
