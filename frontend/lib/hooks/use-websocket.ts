import { WebSocketEvent, Message } from "@/lib/types";
import { useCallback, useEffect, useRef } from "react";

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws";

export function useWebSocket() {
  const socket = useRef<WebSocket | null>(null);
  const eventListeners = useRef<Set<(event: WebSocketEvent) => void>>(new Set());
  const reconnectTimeout = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;

  const connect = useCallback(() => {
    if (socket.current?.readyState === WebSocket.OPEN) return;

    socket.current = new WebSocket(WS_URL);

    socket.current.onopen = () => {
      console.log("WebSocket connected");
      reconnectAttempts.current = 0;
      dispatchEvent({ type: "connect" });
    };

    socket.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === "message") {
          dispatchEvent({ 
            type: "message", 
            message: data.message 
          });
        }
      } catch (error) {
        console.error("Error parsing WebSocket message:", error);
      }
    };

    socket.current.onclose = () => {
      console.log("WebSocket disconnected");
      dispatchEvent({ type: "disconnect" });
      
      if (reconnectAttempts.current < maxReconnectAttempts) {
        reconnectTimeout.current = setTimeout(() => {
          reconnectAttempts.current++;
          connect();
        }, 1000 * Math.pow(2, reconnectAttempts.current));
      }
    };

    socket.current.onerror = (error) => {
      console.error("WebSocket error:", error);
      dispatchEvent({ 
        type: "error", 
        error: "Connection error" 
      });
    };
  }, []);

  const disconnect = useCallback(() => {
    if (reconnectTimeout.current) {
      clearTimeout(reconnectTimeout.current);
      reconnectTimeout.current = null;
    }
    
    if (socket.current) {
      socket.current.close();
      socket.current = null;
    }
  }, []);

  const addEventListener = useCallback((handler: (event: WebSocketEvent) => void) => {
    eventListeners.current.add(handler);
    return () => {
      eventListeners.current.delete(handler);
    };
  }, []);

  const sendMessage = useCallback((message: Omit<Message, "id" | "timestamp" | "status">) => {
    if (!socket.current || socket.current.readyState !== WebSocket.OPEN) {
      console.error("WebSocket not connected");
      return false;
    }

    try {
      socket.current.send(JSON.stringify({
        type: "message",
        message: {
          ...message,
          timestamp: Date.now()
        }
      }));
      return true;
    } catch (error) {
      console.error("Error sending message:", error);
      return false;
    }
  }, []);

  const dispatchEvent = useCallback((event: WebSocketEvent) => {
    eventListeners.current.forEach(handler => handler(event));
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    connect,
    disconnect,
    addEventListener,
    sendMessage,
    isConnected: () => socket.current?.readyState === WebSocket.OPEN
  };
}
