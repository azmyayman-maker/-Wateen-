'use client';

import React, { useState, useEffect } from 'react';
import { useMap, Marker } from 'react-leaflet';
import WateenMapInner from './WateenMapInner';
import { searchAddress, NominatimResponse } from '../../lib/map/nominatim';
import type { Feature, Point } from 'geojson';

function LocationController({ 
  position, 
  onPositionChange,
  source
}: { 
  position: [number, number], 
  onPositionChange: (pos: [number, number], src: 'drag' | 'external') => void,
  source: 'drag' | 'external'
}) {
  const map = useMap();
  
  useEffect(() => {
    // Only animate flyTo if the position change came from an external source (Search/Locate Me)
    // Avoids micro-jitter rendering when dragging
    if (source === 'external') {
      map.flyTo(position, map.getZoom(), { animate: true });
    }
  }, [position, map, source]);

  return (
    <Marker 
      position={position} 
      draggable={true}
      eventHandlers={{
        dragend: (e) => {
          const marker = e.target;
          const newPos = marker.getLatLng();
          onPositionChange([newPos.lat, newPos.lng], 'drag');
        }
      }}
    />
  );
}

interface PatientLocationPickerProps {
  defaultCenter: [number, number];
  defaultZoom?: number;
  onConfirm: (feature: Feature<Point>) => void;
}

export default function PatientLocationPicker({ defaultCenter, defaultZoom = 15, onConfirm }: PatientLocationPickerProps) {
  const [position, setPosition] = useState<[number, number]>(defaultCenter);
  const [positionSource, setPositionSource] = useState<'drag' | 'external'>('external');
  const [addressLabel, setAddressLabel] = useState<string>('');
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<NominatimResponse[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isWaiting, setIsWaiting] = useState(false); // Throttle pending state
  const [gpsError, setGpsError] = useState<string | null>(null);

  // Debounce logic
  useEffect(() => {
    if (query.trim().length > 2) {
      setIsWaiting(true); // User is typing, we are waiting for debounce
    } else {
      setIsWaiting(false);
      setResults([]);
    }

    const timerId = setTimeout(() => {
      if (query.trim().length > 2) {
        setIsWaiting(false);
        setIsSearching(true);
        searchAddress(query).then(data => {
          setResults(data);
          setIsSearching(false);
        });
      }
    }, 1000); // 1-second debounce strictly mandated by OSM

    return () => clearTimeout(timerId);
  }, [query]);

  const handlePositionChange = (pos: [number, number], src: 'drag' | 'external') => {
    setPosition(pos);
    setPositionSource(src);
  };

  const handleLocateMe = () => {
    if (!navigator.geolocation) {
      setGpsError('متصفحك لا يدعم تحديد الموقع'); // Browser doesn't support geolocation
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        handlePositionChange([pos.coords.latitude, pos.coords.longitude], 'external');
        setGpsError(null);
        setAddressLabel('موقعك الحالي (GPS)');
      },
      (err) => {
        setGpsError('تم رفض الإذن أوالتحديد غير متوفر'); // Permission denied / unavailable
      }
    );
  };

  const handleSelectResult = (r: NominatimResponse) => {
    handlePositionChange([parseFloat(r.lat), parseFloat(r.lon)], 'external');
    setAddressLabel(r.display_name);
    setResults([]);
    setQuery('');
  };

  const submitLocation = () => {
    const feature: Feature<Point> = {
      type: 'Feature',
      geometry: {
        type: 'Point',
        // GeoJSON expects [longitude, latitude]
        coordinates: [position[1], position[0]] 
      },
      properties: {
        addressLabel: addressLabel || 'موقع مخصص (Custom Location)'
      }
    };
    onConfirm(feature);
  };

  return (
    <div className="relative w-full h-full flex flex-col gap-2" dir="rtl">
      
      <div className="absolute top-4 left-0 right-0 z-[1000] px-12 flex flex-col gap-2">
        <div className="flex gap-2 bg-white p-2 rounded-lg shadow-md border border-gray-200">
          <input 
            type="text" 
            className="flex-1 px-3 py-2 text-sm outline-none w-full"
            placeholder="ابحث عن عنوان..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button 
            type="button" 
            className="bg-[#0066FF] hover:bg-blue-700 text-white px-4 py-2 rounded-md transition-colors"
            onClick={handleLocateMe}
          >
            تحديد موقعي
          </button>
        </div>
        
        {isWaiting && !isSearching && (
          <div className="bg-white p-2 text-center text-sm shadow-md rounded-md text-gray-500">انتظار...</div>
        )}
        
        {isSearching && (
          <div className="bg-white p-2 text-center text-sm shadow-md rounded-md text-[#0066FF]">جاري البحث...</div>
        )}
        
        {results.length > 0 && (
          <div className="bg-white shadow-lg rounded-md border border-gray-200 mt-1 max-h-60 overflow-y-auto">
            {results.map((r) => (
              <div 
                key={r.place_id} 
                className="p-3 border-b hover:bg-gray-50 cursor-pointer text-sm"
                onClick={() => handleSelectResult(r)}
              >
                {r.display_name}
              </div>
            ))}
          </div>
        )}

        {gpsError && (
          <div className="bg-red-100 text-red-700 p-2 text-sm rounded shadow-sm">
            {gpsError}
          </div>
        )}
      </div>

      <div className="flex-1 w-full relative min-h-[400px] border border-gray-200 rounded-lg overflow-hidden">
        <WateenMapInner center={position} zoom={defaultZoom}>
          <LocationController position={position} onPositionChange={handlePositionChange} source={positionSource} />
        </WateenMapInner>
      </div>

      <div className="absolute bottom-6 left-1/2 transform -translate-x-1/2 z-[1000]">
         <button 
           className="bg-[#0A0A1A] text-white px-8 py-3 rounded-full shadow-lg font-bold text-lg hover:bg-gray-900 transition-colors"
           onClick={submitLocation}
         >
           تأكيد الموقع
         </button>
      </div>
    </div>
  );
}
