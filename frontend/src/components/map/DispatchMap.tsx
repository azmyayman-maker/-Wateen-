'use client';

import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { UserCircle2, Clock, AlertCircle } from 'lucide-react';

interface CoverageData {
  type: string;
  features: Array<{
    type: string;
    geometry: {
      type: string;
      coordinates: number[][][];
    };
  }>;
}

interface Nurse {
  id: string | number;
  name: string;
  lat: number;
  lng: number;
  status: 'available' | 'busy';
}

interface Visit {
  id: string;
  type: string;
  lat: number;
  lng: number;
  status: string;
}

interface DispatchMapProps {
  agencyId: string;
}

// Custom marker icons
const createNurseIcon = (status: 'available' | 'busy') => {
  const colorClass = status === 'available' ? 'border-emerald-500 text-emerald-400' : 'border-amber-500 text-amber-400';
  return L.divIcon({
    className: 'custom-nurse-marker',
    html: `<div class="p-1 rounded-full border-2 bg-slate-900 shadow-lg transition-transform hover:scale-125 cursor-pointer ${colorClass}">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-6 h-6">
        <path fill-rule="evenodd" d="M7.502 6h7.128A3.75 3.75 0 0118 9.75v9.75a3 3 0 003 3h.75v.572a1 1 0 01-.482.876l-3.599 1.24a.75.75 0 01-.636-.636V18.5h.75a.75.75 0 00.75-.75v-6.75a.75.75 0 00-.75-.75H14.5V9.75a3 3 0 00-3-3h-3.998z" clip-rule="evenodd" />
      </svg>
    </div>`,
    iconSize: [32, 32],
    iconAnchor: [16, 32],
  });
};

const visitIcon = L.divIcon({
  className: 'custom-visit-marker',
  html: `<div class="relative p-2 bg-blue-600 rounded-xl shadow-[0_0_20px_rgba(37,99,235,0.6)] cursor-pointer animate-bounce">
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-5 h-5 text-white">
      <path fill-rule="evenodd" d="M12 2.25c-5.385 0-9.75 4.365-9.75 9.75s4.365 9.75 9.75 9.75 9.75-4.365 9.75-9.75S17.385 2.25 12 2.25zM12.75 6a.75.75 0 00-1.5 0v6c0 .414.336.75.75.75h4.5a.75.75 0 000-1.5h-3.75V6z" clip-rule="evenodd" />
    </svg>
  </div>`,
  iconSize: [36, 36],
  iconAnchor: [18, 36],
});

export default function DispatchMap({ agencyId }: DispatchMapProps) {
  const [coverageData, setCoverageData] = useState<CoverageData | null>(null);
  const [nurses, setNurses] = useState<Nurse[]>([]);
  const [visits, setVisits] = useState<Visit[]>([]);
  const [selectedVisit, setSelectedVisit] = useState<Visit | null>(null);

  const center: [number, number] = [30.0444, 31.2357];

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
      <MapContainer
        center={center}
        zoom={11}
        scrollWheelZoom={true}
        className="w-full h-full z-0"
        attributionControl={true}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        />

        {/* Nurse Markers */}
        {nurses.map(n => (
          <Marker 
            key={n.id} 
            position={[n.lat, n.lng]} 
            icon={createNurseIcon(n.status)}
          />
        ))}

        {/* Visit Markers (Pending) */}
        {visits.map(v => (
          <Marker 
            key={v.id} 
            position={[v.lat, v.lng]} 
            icon={visitIcon}
            eventHandlers={{
              click: () => setSelectedVisit(v),
            }}
          />
        ))}

        {/* Selected Visit Popup */}
        {selectedVisit && (
          <Popup
            position={[selectedVisit.lat, selectedVisit.lng]}
            onClose={() => setSelectedVisit(null)}
          >
            <div className="p-3 min-w-[200px] bg-slate-900 text-white rounded-lg border border-white/10 shadow-2xl">
              <div className="flex items-center gap-2 mb-2">
                <AlertCircle className="w-4 h-4 text-blue-400" />
                <h4 className="font-bold text-sm tracking-tight">{selectedVisit.type}</h4>
              </div>
              <p className="text-xs text-slate-400 mb-3">Status: {selectedVisit.status}</p>
              <button 
                onClick={() => {
                  alert("Dispatching integration incoming. This will route to the dispatch API.");
                  setSelectedVisit(null);
                }}
                className="w-full py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-xs font-bold transition-all">
                Dispatch Nurse
              </button>
            </div>
          </Popup>
        )}
      </MapContainer>

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
