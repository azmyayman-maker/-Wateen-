'use client';

import React, { useEffect, useState } from 'react';
import { useMap } from 'react-leaflet';
import WateenMapInner from './WateenMapInner';
import { validateCoveragePolygon, sanitizeGeoJSON } from '../../lib/map/validators';
import type { Feature, Polygon, MultiPolygon } from 'geojson';

// Inner component requiring useMap() context
function GeomanIntegration({ onSave }: { onSave: (feature: Feature<Polygon | MultiPolygon>) => void }) {
  const map = useMap();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Configure Geoman strictly for Policy requirements
    map.pm.addControls({
      position: 'topleft',
      drawMarker: false,
      drawCircleMarker: false,
      drawPolyline: false,
      drawRectangle: false,
      drawCircle: false,
      drawText: false,
      drawPolygon: true,
      editControls: true,
    });

    // Enforce intersection prevention natively via Geoman
    map.pm.setGlobalOptions({ allowSelfIntersection: false });

    // Handle create event
    interface PmCreateEvent {
      layer: import('leaflet').Layer & {
        toGeoJSON: () => Feature<Polygon | MultiPolygon>;
      };
    }
    
    const handleCreate = (e: PmCreateEvent) => {
      const geojson = e.layer.toGeoJSON();
      
      const validation = validateCoveragePolygon(geojson);
      if (!validation.valid) {
        setError(validation.error || 'Invalid shape');
        // Delete invalid shape immediately
        map.removeLayer(e.layer);
        return;
      }
      
      setError(null);
      const sanitized = sanitizeGeoJSON(geojson);
      onSave(sanitized);
    };

    map.on('pm:create', handleCreate);

    return () => {
      map.pm.removeControls();
      map.off('pm:create', handleCreate);
    };
  }, [map, onSave]);

  return (
    <div className="absolute top-4 end-4 z-[1000] w-64 max-w-full">
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">خطأ! </strong>
          <span className="block sm:inline">{error}</span>
        </div>
      )}
    </div>
  );
}

// B2B Interface Component
interface CoveragePolygonEditorProps {
  center: [number, number];
  zoom: number;
  onSave: (feature: Feature<Polygon | MultiPolygon>) => void;
  className?: string;
}

export default function CoveragePolygonEditor({ center, zoom, onSave, className }: CoveragePolygonEditorProps) {
  return (
    <div className={`relative ${className || 'w-full h-[500px]'}`}>
      <WateenMapInner center={center} zoom={zoom}>
        <GeomanIntegration onSave={onSave} />
      </WateenMapInner>
    </div>
  );
}
