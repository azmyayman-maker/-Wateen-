'use client';

import React, { useState, useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Polygon, FeatureGroup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import '@geoman-io/leaflet-geoman-free';
import '@geoman-io/leaflet-geoman-free/dist/leaflet-geoman.css';

interface CoverageMapProps {
  initialPolygon?: any; // GeoJSON Polygon geometry
  onCoverageChange: (polygon: any) => void;
  isSaving?: boolean;
}

export default function CoverageMap({ initialPolygon, onCoverageChange, isSaving = false }: CoverageMapProps) {
  const mapRef = useRef<any>(null);
  const geoGroupRef = useRef<any>(null);

  // Default to Cairo, Egypt
  const center: [number, number] = [30.0444, 31.2357];

  useEffect(() => {
    if (mapRef.current) {
        const map = mapRef.current;
        
        // Setup Geoman
        map.pm.addControls({
          position: 'topleft',
          drawMarker: false,
          drawCircleMarker: false,
          drawPolyline: false,
          drawRectangle: false,
          drawCircle: false,
          drawText: false,
          cutPolygon: false,
          rotateMode: false,
          drawPolygon: true,
          editMode: true,
          dragMode: true,
          removalMode: true,
        });

        map.pm.setLang('ar');

        // Global draw style - Wateen Cyan/Amber
        map.pm.setPathOptions({
          color: '#22d3ee',
          fillColor: '#22d3ee',
          fillOpacity: 0.2,
          weight: 3,
        });

        // Event listeners
        map.on('pm:create', (e: any) => {
          const layer = e.layer;
          onCoverageChange(layer.toGeoJSON().geometry);
          layer.on('pm:edit', (editEvent: any) => {
             onCoverageChange(editEvent.layer.toGeoJSON().geometry);
          });
        });

        map.on('pm:remove', () => {
          onCoverageChange(null);
        });

        // Fix map size issues on initial load
        setTimeout(() => {
          map.invalidateSize();
        }, 500);
    }
  }, [mapRef.current]);

  // Convert GeoJSON geometry to Leaflet LatLngs
  const getInitialCoords = () => {
    if (initialPolygon && initialPolygon.type === 'Polygon') {
      return initialPolygon.coordinates[0].map((coord: any) => [coord[1], coord[0]]);
    }
    return null;
  };

  const initialCoords = getInitialCoords();

  return (
    <div className="w-full h-full relative rounded-xl overflow-hidden shadow-lg border border-neutral-700 bg-slate-900">
      <MapContainer
        center={center}
        zoom={11}
        className="w-full h-full z-10"
        ref={mapRef}
        attributionControl={false}
      >
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          subdomains="abcd"
        />
        
        <FeatureGroup ref={geoGroupRef}>
          {initialCoords && (
            <Polygon 
              positions={initialCoords} 
              pathOptions={{ 
                color: '#f59e0b', 
                fillColor: '#f59e0b', 
                fillOpacity: 0.2,
                weight: 3
              }} 
            />
          )}
        </FeatureGroup>
      </MapContainer>

      {/* Saving Overlay */}
      {isSaving && (
        <div className="absolute inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-[1000]">
           <div className="bg-neutral-800 border border-neutral-700 px-6 py-4 rounded-2xl flex flex-col items-center gap-4 text-white shadow-2xl animate-in fade-in zoom-in duration-300">
               <div className="w-12 h-12 border-4 border-cyan-500/30 border-t-cyan-400 rounded-full animate-spin"></div>
               <span className="font-medium text-lg">جاري حفظ النطاق الجغرافي...</span>
           </div>
        </div>
      )}
      
      {/* Custom Tooltip */}
      <div className="absolute bottom-4 left-4 right-4 z-[1000] pointer-events-none">
          <div className="bg-slate-900/80 backdrop-blur-md border border-slate-700 p-3 rounded-xl text-xs text-slate-300 text-center shadow-lg">
             <span className="text-cyan-400 font-bold">تلميح:</span> استخدم أيقونة المضلع في اليسار لرسم منطقة تغطية جديدة.
          </div>
      </div>
    </div>
  );
}
