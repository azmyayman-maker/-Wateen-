'use client';

import { useState, useEffect, useCallback, useRef } from 'react';

/**
 * T029: WebSocket hook for tracking a specific visit in real-time.
 * 
 * Returns live status, nurse location, ETA, and connection state.
 * Includes auto-reconnect with exponential backoff (max 30s).
 * Falls back to REST polling if WebSocket fails repeatedly.
 * 
 * Usage:
 *   const { status, nurseLocation, eta, isConnected } = useVisitSocket(visitId);
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
const WS_BASE = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';

interface NurseLocation {
  latitude: number | null;
  longitude: number | null;
  name: string;
  id: string;
}

interface VisitSocketState {
  status: string | null;
  nurseLocation: NurseLocation | null;
  eta: number | null;
  isConnected: boolean;
  error: string | null;
}

export function useVisitSocket(visitId: string | null) {
  const [state, setState] = useState<VisitSocketState>({
    status: null,
    nurseLocation: null,
    eta: null,
    isConnected: false,
    error: null,
  });

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptRef = useRef(0);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const pollingTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const maxReconnectAttempts = 5;

  // REST polling fallback
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
    } catch {
      // Silently ignore polling errors
    }
  }, [visitId]);

  // Start REST polling as fallback
  const startPolling = useCallback(() => {
    if (pollingTimerRef.current) return;
    pollingTimerRef.current = setInterval(pollStatus, 5000);
    pollStatus(); // immediate first poll
  }, [pollStatus]);

  const stopPolling = useCallback(() => {
    if (pollingTimerRef.current) {
      clearInterval(pollingTimerRef.current);
      pollingTimerRef.current = null;
    }
  }, []);

  // WebSocket connection
  const connect = useCallback(() => {
    if (!visitId || typeof window === 'undefined') return;

    const token = localStorage.getItem('wateen_access_token');
    if (!token) {
      startPolling();
      return;
    }

    try {
      const ws = new WebSocket(`${WS_BASE}/ws/patient/?token=${token}`);
      wsRef.current = ws;

      ws.onopen = () => {
        setState((prev) => ({ ...prev, isConnected: true, error: null }));
        reconnectAttemptRef.current = 0;
        stopPolling();
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'visit_update' && data.data) {
            const update = data.data;
            if (update.visit_id === visitId || !update.visit_id) {
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
          }
        } catch {
          // Ignore malformed messages
        }
      };

      ws.onerror = () => {
        setState((prev) => ({ ...prev, error: 'WebSocket error' }));
      };

      ws.onclose = () => {
        setState((prev) => ({ ...prev, isConnected: false }));
        wsRef.current = null;

        // Exponential backoff reconnect
        if (reconnectAttemptRef.current < maxReconnectAttempts) {
          const delay = Math.min(
            1000 * Math.pow(2, reconnectAttemptRef.current),
            30000
          );
          reconnectAttemptRef.current++;
          reconnectTimerRef.current = setTimeout(connect, delay);
        } else {
          // Max retries exceeded — fall back to REST polling
          startPolling();
        }
      };
    } catch {
      startPolling();
    }
  }, [visitId, startPolling, stopPolling]);

  // Disconnect
  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }
    stopPolling();
  }, [stopPolling]);

  useEffect(() => {
    if (visitId) {
      connect();
    }
    return () => disconnect();
  }, [visitId, connect, disconnect]);

  return {
    ...state,
    reconnect: connect,
    disconnect,
  };
}
