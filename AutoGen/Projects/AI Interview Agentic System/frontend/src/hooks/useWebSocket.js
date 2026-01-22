import { useState, useEffect, useCallback, useRef } from 'react';

const WS_BASE = 'ws://127.0.0.1:8000';

export function useWebSocket(sessionId) {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState(null);
  const [error, setError] = useState(null);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  const connect = useCallback(() => {
    if (!sessionId) {
      console.log('WebSocket: No sessionId provided');
      return;
    }

    // Prevent double connections
    if (wsRef.current && (wsRef.current.readyState === WebSocket.OPEN || wsRef.current.readyState === WebSocket.CONNECTING)) {
      console.log('WebSocket: Already connected or connecting, skipping');
      return;
    }

    console.log(`WebSocket: Attempting to connect to session ${sessionId}`);

    try {
      const ws = new WebSocket(`${WS_BASE}/ws/interview/${sessionId}`);

      ws.onopen = () => {
        console.log(`WebSocket: Connection opened for session ${sessionId}`);
        setIsConnected(true);
        setError(null);
      };

      ws.onmessage = (event) => {
        console.log('WebSocket: Message received:', event.data);
        try {
          const data = JSON.parse(event.data);
          setLastMessage(data);
        } catch (e) {
          console.error('Failed to parse WebSocket message:', e);
        }
      };

      ws.onerror = (event) => {
        console.error('WebSocket error event:', event);
        setError('WebSocket connection error');
      };

      ws.onclose = (event) => {
        console.log(`WebSocket: Connection closed. Code: ${event.code}, Reason: ${event.reason}`);
        setIsConnected(false);
        if (event.code !== 1000) {
          // Abnormal closure - try to reconnect
          console.log('WebSocket: Abnormal closure detected, will reconnect in 3s...');
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, 3000);
        } else {
          console.log('WebSocket: Normal closure, not reconnecting');
        }
      };

      wsRef.current = ws;
    } catch (e) {
      setError('Failed to connect to WebSocket');
      console.error('WebSocket connection failed:', e);
    }
  }, [sessionId]);

  const disconnect = useCallback(() => {
    console.log('WebSocket: Disconnecting...');
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (wsRef.current) {
      if (wsRef.current.readyState === WebSocket.OPEN || wsRef.current.readyState === WebSocket.CONNECTING) {
        wsRef.current.close(1000, 'Client disconnect');
      }
      wsRef.current = null;
    }
    setIsConnected(false);
  }, []);

  const sendMessage = useCallback((message) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.error('WebSocket not connected');
    }
  }, []);

  const startInterview = useCallback(() => {
    sendMessage({ type: 'start' });
  }, [sendMessage]);

  const submitAnswer = useCallback((text) => {
    sendMessage({ type: 'answer', data: { text } });
  }, [sendMessage]);

  const ready = useCallback(() => {
    sendMessage({ type: 'ready' });
  }, [sendMessage]);

  const toggleVoice = useCallback((enabled) => {
    sendMessage({ type: 'voice_toggle', data: { enabled } });
  }, [sendMessage]);

  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);

  return {
    isConnected,
    lastMessage,
    error,
    sendMessage,
    startInterview,
    submitAnswer,
    ready,
    toggleVoice,
    reconnect: connect
  };
}
