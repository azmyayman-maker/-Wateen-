import { useState, useEffect } from 'react';

interface DashboardMetrics {
  active_visits: number;
  queue_depth: number;
  online_nurses: number;
  revenue: { escrowed: string; settled: string };
}

export function useDashboardSocket(agencyId: string, token: string) {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [isPolling, setIsPolling] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let ws: WebSocket;

    const connectWebSocket = () => {
      // Sec-WebSocket-Protocol routing auth prevents URL query leaks
      ws = new WebSocket(`ws://localhost:8000/ws/dashboard/agency/`, [token]);

      ws.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          if (payload.type === 'dashboard.heartbeat') {
            setMetrics(payload.data.metrics);
            setIsPolling(false);
          }
        } catch (e) {
          console.error("Invalid heartbeat payload", e);
        }
      };

      ws.onclose = (event) => {
        // Fallback to HTTP Polling if connection drops
        setIsPolling(true);
        if (event.code === 1008) {
          setError("Connection limit exceeded (max 5 active sessions).");
        }
      };
    };

    connectWebSocket();

    return () => {
      if (ws) ws.close();
    };
  }, [agencyId, token]);

  // Isolate Polling to prevent memory leaks from unnecessary interval GC
  useEffect(() => {
    let fallbackInterval: NodeJS.Timeout;

    if (isPolling && !error) {
      // Graceful 30s Degradation 
      fallbackInterval = setInterval(() => {
        fetch('/api/v1/dashboard/metrics/', {
          headers: { Authorization: `Bearer ${token}` }
        })
        .then(res => res.json())
        .then(data => setMetrics(data.metrics))
        .catch(err => console.error("Polling failed", err));
      }, 30000);
    }

    return () => {
      if (fallbackInterval) clearInterval(fallbackInterval);
    };
  }, [isPolling, error, token]);

  return { metrics, isPolling, error };
}
