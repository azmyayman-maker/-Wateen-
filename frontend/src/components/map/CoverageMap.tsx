'use client';

import React, { useState, useCallback, useRef } from 'react';
import Map, { NavigationControl } from 'react-map-gl';
import DrawControl from './DrawControl';
import 'mapbox-gl/dist/mapbox-gl.css';
import '@mapbox/mapbox-gl-draw/dist/mapbox-gl-draw.css';

interface CoverageMapProps {
  initialPolygon?: any; // GeoJSON Polygon
  onCoverageChange: (polygon: any) => void;
  isSaving?: boolean;
}

export default function CoverageMap({ initialPolygon, onCoverageChange, isSaving = false }: CoverageMapProps) {
  const [features, setFeatures] = useState<any>({});
  
  // Default to Cairo, Egypt
  const [viewState, setViewState] = useState({
    longitude: 31.2357,
    latitude: 30.0444,
    zoom: 11
  });

  const onUpdate = useCallback((e: any) => {
    setFeatures((currFeatures: any) => {
      const newFeatures = { ...currFeatures };
      for (const f of e.features) {
        newFeatures[f.id] = f;
      }
      return newFeatures;
    });

    // We only care about the single polygon for the coverage area
    // Just pass the last modified feature
    if (e.features.length > 0) {
        onCoverageChange(e.features[0].geometry);
    }
  }, [onCoverageChange]);

  const onDelete = useCallback((e: any) => {
    setFeatures((currFeatures: any) => {
      const newFeatures = { ...currFeatures };
      for (const f of e.features) {
        delete newFeatures[f.id];
      }
      return newFeatures;
    });
    // If they delete everything, pass null
    onCoverageChange(null);
  }, [onCoverageChange]);

  return (
    <div className="w-full h-full relative rounded-xl overflow-hidden shadow-lg border border-neutral-700">
      {/* We use the public MAPBOX token. Real apps should secure this. */}
      {/* For MVP we might hardcode or use NEXT_PUBLIC_MAPBOX_TOKEN if available */}
      <Map
        {...viewState}
        onMove={evt => setViewState(evt.viewState)}
        mapStyle="mapbox://styles/mapbox/dark-v11"
        mapboxAccessToken={process.env.NEXT_PUBLIC_MAPBOX_TOKEN || "pk.eyJ1IjoiYWxpYXNnZXIxMjMiLCJhIjoiY2tyNzhlN2FzMHBveTJwczNtaTI4MTE2YSJ9.WJ2o5X5P4-aYF9z9U8tYwQ"}
      >
        <NavigationControl position="top-left" />
        
        <DrawControl
          position="top-right"
          displayControlsDefault={false}
          controls={{
            polygon: true,
            trash: true
          }}
          defaultMode="draw_polygon"
          onCreate={onUpdate}
          onUpdate={onUpdate}
          onDelete={onDelete}
        />
      </Map>

      {/* Saving Overlay */}
      {isSaving && (
        <div className="absolute inset-0 bg-neutral-900/50 backdrop-blur-sm flex items-center justify-center z-50">
           <div className="bg-neutral-800 border border-neutral-700 px-6 py-3 rounded-lg flex items-center gap-3 text-amber-500 font-medium shadow-xl">
               <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-amber-500"></div>
               جاري حفظ النطاق...
           </div>
        </div>
      )}
    </div>
  );
}
