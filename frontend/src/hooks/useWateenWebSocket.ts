import { useEffect, useState, useCallback, useRef } from 'react';

type WebSocketMessage = {
  type: string;
  [key: string]: any;
};

export function useWateenWebSocket(wsPath: string, onMessage?: (data: WebSocketMessage) => void) {
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  const connect = useCallback(() => {
    if (typeof window === 'undefined') return;
    
    // Auto-reconnect prevention
    if (wsRef.current && (wsRef.current.readyState === WebSocket.OPEN || wsRef.current.readyState === WebSocket.CONNECTING)) {
      return;
    }

    const token = localStorage.getItem('wateen_access_token');
    if (!token) {
      console.warn('Cannot connect to WebSocket: No access token found');
      return;
    }

    const wsUrl = `ws://localhost:8000/${wsPath}?token=${token}`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log(`WebSocket Connected to ${wsPath}`);
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (onMessage) onMessage(data);
      } catch (err) {
        console.error('Failed to parse WebSocket message', err);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket Error:', error);
    };

    ws.onclose = () => {
      console.log(`WebSocket Disconnected from ${wsPath}`);
      setIsConnected(false);
      wsRef.current = null;
    };
  }, [wsPath, onMessage]);

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsConnected(false);
  }, []);

  useEffect(() => {
    // Only connect if path is defined
    if (wsPath) {
      connect();
    }
    return () => disconnect();
  }, [connect, disconnect, wsPath]);

  return { isConnected, connect, disconnect };
}
