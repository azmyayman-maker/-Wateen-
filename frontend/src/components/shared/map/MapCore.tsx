"use client";

import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

interface MapCoreProps {
  center: [number, number];
  zoom?: number;
  onLocationSelect?: (lat: number, lng: number) => void;
  readOnly?: boolean;
}

// Custom glowing pulse icon to match Wateen's premium aesthetic
const customIcon = new L.DivIcon({
  className: 'custom-map-marker',
  html: `<div class="relative flex items-center justify-center w-6 h-6">
          <div class="absolute w-full h-full bg-cyan-500 rounded-full opacity-40 animate-ping"></div>
          <div class="relative w-3.5 h-3.5 bg-cyan-400 border-[2.5px] border-slate-900 rounded-full shadow-[0_0_15px_rgba(34,211,238,0.8)]"></div>
        </div>`,
  iconSize: [24, 24],
  iconAnchor: [12, 12],
});

// Internal component to handle map clicks
const LocationMarker = ({ position, setPosition, readOnly }: any) => {
  const map = useMapEvents({
    click(e) {
      if (!readOnly) {
        setPosition(e.latlng);
        map.flyTo(e.latlng, map.getZoom(), {
          animate: true,
          duration: 0.8,
        });
      }
    },
  });

  return position === null ? null : (
    <Marker position={position} icon={customIcon} />
  );
};

export default function MapCore({ center, zoom = 14, onLocationSelect, readOnly = false }: MapCoreProps) {
  const [position, setPosition] = React.useState<L.LatLngExpression>(center);

  // Update parent when position changes
  useEffect(() => {
    if (position && onLocationSelect) {
      const p = position as any;
      if (p.lat && p.lng) {
        onLocationSelect(p.lat, p.lng);
      }
    }
  }, [position, onLocationSelect]);

  return (
    <MapContainer 
      center={center} 
      zoom={zoom} 
      scrollWheelZoom={!readOnly}
      className="w-full h-full z-0 font-sans"
      attributionControl={false}
      zoomControl={!readOnly}
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <LocationMarker position={position} setPosition={setPosition} readOnly={readOnly} />
    </MapContainer>
  );
}
