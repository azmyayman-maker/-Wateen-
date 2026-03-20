'use client';

import { useState, useEffect, useCallback, useRef } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
const WS_BASE = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';

interface NurseLocation {
  latitude: number | null;
  longitude: number | null;
  name: string;
  id: string;
}

type ConnectionMode = 'live' | 'reconnecting' | 'polling' | 'disconnected';

interface VisitSocketState {
  status: string | null;
  nurseLocation: NurseLocation | null;
  eta: number | null;
  connectionMode: ConnectionMode;
  gpsStale: boolean;
  error: string | null;
}

export function useVisitSocket(visitId: string | null) {
  const [state, setState] = useState<VisitSocketState>({
    status: null,
    nurseLocation: null,
    eta: null,
    connectionMode: 'disconnected',
    gpsStale: false,
    error: null,
  });

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptRef = useRef(0);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const pollingTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const pollingReconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const gpsStaleTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const maxReconnectAttempts = 6;

  const resetGpsStaleTimer = useCallback(() => {
    if (gpsStaleTimerRef.current) {
      clearTimeout(gpsStaleTimerRef.current);
    }
    gpsStaleTimerRef.current = setTimeout(() => {
      setState(prev => ({ ...prev, gpsStale: true }));
    }, 45000);
  }, []);

  const pollStatus = useCallback(async () => {
    if (!visitId) return;
    try {
      const response = await fetch(`${API_URL}/v1/visits/${visitId}/status/`, {
        credentials: 'include',
      });
      if (response.ok) {
        const data = await response.json();
        setState((prev) => ({
          ...prev,
          status: data.status,
          nurseLocation: data.nurse
            ? {
                latitude: data.nurse.latitude,
                longitude: data.nurse.longitude,
                name: data.nurse.name,
                id: data.nurse.id,
              }
            : prev.nurseLocation,
          eta: data.nurse?.eta_minutes ?? prev.eta,
        }));
      }
    } catch (err) {
      console.warn('Polling failed:', err);
      // Silently ignore polling errors but could track failure count here
    }
  }, [visitId]);

  const startPolling = useCallback(() => {
    if (pollingTimerRef.current) return;
    pollingTimerRef.current = setInterval(pollStatus, 10000);
    pollStatus();
  }, [pollStatus]);

  const stopPolling = useCallback(() => {
    if (pollingTimerRef.current) {
      clearInterval(pollingTimerRef.current);
      pollingTimerRef.current = null;
    }
    if (pollingReconnectTimerRef.current) {
      clearTimeout(pollingReconnectTimerRef.current);
      pollingReconnectTimerRef.current = null;
    }
  }, []);

  const connect = useCallback(() => {
    if (!visitId || typeof window === 'undefined') return;

    const token = localStorage.getItem('wateen_access_token');
    if (!token) {
      startPolling();
      setState(prev => ({ ...prev, connectionMode: 'polling' }));
      return;
    }

    try {
      const wsUrl = `${WS_BASE}/ws/visits/${visitId}/`;
      const ws = new WebSocket(wsUrl, ['access_token', token]);
      wsRef.current = ws;

      ws.onopen = () => {
        setState((prev) => ({ 
          ...prev, 
          connectionMode: 'live', 
          error: null 
        }));
        reconnectAttemptRef.current = 0;
        stopPolling();
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.type === 'gps_update' && data.data) {
            const gpsData = data.data;
            
            // Issue #4: Bounds validation before state update
            if (
              typeof gpsData.latitude !== 'number' || 
              typeof gpsData.longitude !== 'number' ||
              gpsData.latitude < -90 || gpsData.latitude > 90 ||
              gpsData.longitude < -180 || gpsData.longitude > 180
            ) {
              console.warn('Received invalid GPS coordinates:', gpsData);
              return;
            }

            setState((prev) => ({
              ...prev,
              nurseLocation: {
                latitude: gpsData.latitude,
                longitude: gpsData.longitude,
                name: prev.nurseLocation?.name ?? '',
                id: gpsData.nurse_id ?? prev.nurseLocation?.id ?? '',
              },
              gpsStale: false,
            }));
            resetGpsStaleTimer();
            return;
          }
          
          if (data.type === 'visit_update' && data.data) {
            const update = data.data;
            setState((prev) => ({
              ...prev,
              status: update.status ?? prev.status,
              nurseLocation: update.nurse_location
                ? {
                    latitude: update.nurse_location.latitude,
                    longitude: update.nurse_location.longitude,
                    name: update.nurse_name ?? prev.nurseLocation?.name ?? '',
                    id: update.nurse_id ?? prev.nurseLocation?.id ?? '',
                  }
                : prev.nurseLocation,
              eta: update.eta_minutes ?? prev.eta,
            }));
          }
        } catch (err) {
          console.warn('Malformed WebSocket message received:', err);
        }
      };

      ws.onerror = () => {
        setState((prev) => ({ ...prev, error: 'WebSocket error' }));
      };

      ws.onclose = () => {
        setState((prev) => ({ 
          ...prev, 
          connectionMode: 'reconnecting',
        }));
        wsRef.current = null;

        if (reconnectAttemptRef.current < maxReconnectAttempts) {
          const delays = [1000, 2000, 4000, 8000, 16000, 30000];
          const delay = delays[Math.min(reconnectAttemptRef.current, delays.length - 1)];
          reconnectAttemptRef.current++;
          reconnectTimerRef.current = setTimeout(connect, delay);
        } else {
          setState(prev => ({ ...prev, connectionMode: 'polling' }));
          startPolling();
          
          pollingReconnectTimerRef.current = setTimeout(() => {
            reconnectAttemptRef.current = 0;
            connect();
          }, 30000);
        }
      };
    } catch {
      startPolling();
      setState(prev => ({ ...prev, connectionMode: 'polling' }));
    }
  }, [visitId, startPolling, stopPolling, resetGpsStaleTimer]);

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }
    if (pollingReconnectTimerRef.current) {
      clearTimeout(pollingReconnectTimerRef.current);
      pollingReconnectTimerRef.current = null;
    }
    if (gpsStaleTimerRef.current) {
      clearTimeout(gpsStaleTimerRef.current);
      gpsStaleTimerRef.current = null;
    }
    stopPolling();
    setState(prev => ({ ...prev, connectionMode: 'disconnected' }));
  }, [stopPolling]);

  useEffect(() => {
    if (visitId) {
      connect();
    }
    return () => disconnect();
  }, [visitId, connect, disconnect]);

  return {
    status: state.status,
    nurseLocation: state.nurseLocation,
    eta: state.eta,
    connectionMode: state.connectionMode,
    gpsStale: state.gpsStale,
    error: state.error,
    reconnect: connect,
    disconnect,
  };
}
