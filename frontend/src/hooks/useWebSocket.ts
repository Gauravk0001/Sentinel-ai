import { useEffect, useRef, useState } from 'react';

/**
 * WebSocket hook for real-time SentinelAI updates.
 * - Connects to `/ws` endpoint
 * - Handles `ai_alert` and `risk_update` message types
 * - Auto-reconnects on disconnect
 */
export function useWebSocket(onMessage?: (message: any) => void) {
  const [connected, setConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<any>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const connect = () => {
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const ws = new WebSocket(`${protocol}://${window.location.host}/ws`);

    ws.onopen = () => {
      setConnected(true);
      console.log('[SentinelAI WS] connected');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setLastMessage(data);
        if (onMessage) onMessage(data);
      } catch (err) {
        console.error('[SentinelAI WS] parse error', err);
      }
    };

    ws.onclose = () => {
      setConnected(false);
      // Auto-reconnect after 3 seconds
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
      reconnectTimer.current = setTimeout(connect, 3000);
    };

    ws.onerror = (err) => {
      console.error('[SentinelAI WS] error', err);
      ws.close();
    };

    wsRef.current = ws;
  };

  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  return { connected, lastMessage };
}

