'use client';

import React, { useEffect, useState, useRef } from 'react';
import Map, { Source, Layer, Marker, Popup, NavigationControl } from 'react-map-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import { UserCircle2, Clock, MapPin, AlertCircle } from 'lucide-react';

const MAPBOX_TOKEN = process.env.NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN;

interface DispatchMapProps {
  agencyId: string;
}

export default function DispatchMap({ agencyId }: DispatchMapProps) {
  const [viewState, setViewState] = useState({
    longitude: 31.2357,
    latitude: 30.0444,
    zoom: 11
  });
  
  const [coverageData, setCoverageData] = useState<any>(null);
  const [nurses, setNurses] = useState<any[]>([]);
  const [visits, setVisits] = useState<any[]>([]);
  const [selectedVisit, setSelectedVisit] = useState<any>(null);

  // Fetch initial state
  useEffect(() => {
    // 1. Fetch Coverage Polygon
    fetch(`/api/v1/agency/${agencyId}/coverage/`)
      .then(res => res.json())
      .then(data => {
         if (data.coverage_polygon) setCoverageData(data.coverage_polygon);
      });

    // 2. Fetch Active Nurses & Pending Visits
    // Mocking for now, would be real API calls + WebSocket updates
    setNurses([
      { id: 1, name: 'Amira S.', lat: 30.05, lng: 31.24, status: 'available' },
      { id: 2, name: 'Khaled M.', lat: 30.04, lng: 31.22, status: 'busy' },
    ]);
    
    setVisits([
      { id: 'v1', type: 'IV Drip', lat: 30.06, lng: 31.25, status: 'pending' },
    ]);
  }, [agencyId]);

  return (
    <div className="w-full h-full relative rounded-3xl overflow-hidden border border-white/10 shadow-2xl">
      <Map
        {...viewState}
        onMove={(evt: any) => setViewState(evt.viewState)}
        style={{ width: '100%', height: '100%' }}
        mapStyle="mapbox://styles/mapbox/dark-v11"
        mapboxAccessToken={MAPBOX_TOKEN}
      >
        <NavigationControl position="top-right" />

        {/* Coverage Polygon Layer */}
        {coverageData && (
          <Source id="coverage" type="geojson" data={coverageData}>
            <Layer
              id="coverage-fill"
              type="fill"
              paint={{
                'fill-color': '#4f46e5',
                'fill-opacity': 0.15
              }}
            />
            <Layer
              id="coverage-outline"
              type="line"
              paint={{
                'line-color': '#6366f1',
                'line-width': 2,
                'line-dasharray': [2, 1]
              }}
            />
          </Source>
        )}

        {/* Nurse Markers */}
        {nurses.map(n => (
          <Marker key={n.id} latitude={n.lat} longitude={n.lng} anchor="bottom">
            <div className={`p-1 rounded-full border-2 bg-slate-900 shadow-lg transition-transform hover:scale-125 cursor-pointer ${
              n.status === 'available' ? 'border-emerald-500' : 'border-amber-500'
            }`}>
              <UserCircle2 className={`w-6 h-6 ${n.status === 'available' ? 'text-emerald-400' : 'text-amber-400'}`} />
            </div>
          </Marker>
        ))}

        {/* Visit Markers (Pending) */}
        {visits.map(v => (
          <Marker key={v.id} latitude={v.lat} longitude={v.lng} anchor="bottom" onClick={(e: any) => {
            e.originalEvent.stopPropagation();
            setSelectedVisit(v);
          }}>
            <div className="relative p-2 bg-blue-600 rounded-xl shadow-[0_0_20px_rgba(37,99,235,0.6)] cursor-pointer animate-bounce">
              <Clock className="w-5 h-5 text-white" />
              <div className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full border-2 border-white animate-ping" />
            </div>
          </Marker>
        ))}

        {/* Selected Visit Popup */}
        {selectedVisit && (
          <Popup
            latitude={selectedVisit.lat}
            longitude={selectedVisit.lng}
            anchor="top"
            onClose={() => setSelectedVisit(null)}
            className="z-50"
          >
            <div className="p-3 min-w-[200px] bg-slate-900 text-white rounded-lg border border-white/10 shadow-2xl">
              <div className="flex items-center gap-2 mb-2">
                <AlertCircle className="w-4 h-4 text-blue-400" />
                <h4 className="font-bold text-sm tracking-tight">{selectedVisit.type}</h4>
              </div>
              <p className="text-xs text-slate-400 mb-3">Status: {selectedVisit.status}</p>
              <button className="w-full py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-xs font-bold transition-all">
                Dispatch Nurse
              </button>
            </div>
          </Popup>
        )}
      </Map>

      {/* Floating Info Overlays */}
      <div className="absolute bottom-6 left-6 p-4 rounded-2xl bg-slate-900/80 backdrop-blur-xl border border-white/10 shadow-2xl flex items-center gap-5">
         <div className="flex items-center gap-2">
           <div className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
           <span className="text-[10px] font-bold text-slate-300 uppercase">15 Online</span>
         </div>
         <div className="flex items-center gap-2">
           <div className="w-2.5 h-2.5 rounded-full bg-blue-500 animate-pulse" />
           <span className="text-[10px] font-bold text-slate-300 uppercase">5 Pending Requests</span>
         </div>
      </div>
    </div>
  );
}
