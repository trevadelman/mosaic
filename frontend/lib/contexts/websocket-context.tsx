"use client"

import React, { createContext, useContext, useEffect, useState, useCallback, useRef } from "react"
import { Message, WebSocketEvent } from "../types"

// WebSocket connection states
export enum ConnectionState {
  CONNECTING = "connecting",
  CONNECTED = "connected",
  DISCONNECTED = "disconnected",
  RECONNECTING = "reconnecting",
}

// Message queue item
interface QueuedMessage {
  agentId: string
  content: string
  retries: number
  id: string
  timestamp: number
}

// WebSocket context type
interface WebSocketContextType {
  connectionState: ConnectionState
  sendMessage: (agentId: string, content: string) => Promise<boolean>
  addEventListener: (callback: (event: WebSocketEvent) => void) => () => void
  connect: (agentId?: string) => void
  disconnect: () => void
}

// Default context value
const defaultContext: WebSocketContextType = {
  connectionState: ConnectionState.DISCONNECTED,
  sendMessage: async () => false,
  addEventListener: () => () => {},
  connect: () => {},
  disconnect: () => {},
}

// Create context
const WebSocketContext = createContext<WebSocketContextType>(defaultContext)

// WebSocket URL
const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws"

// WebSocket Provider props
interface WebSocketProviderProps {
  children: React.ReactNode
}

export function WebSocketProvider({ children }: WebSocketProviderProps) {
  // State
  const [connectionState, setConnectionState] = useState<ConnectionState>(ConnectionState.DISCONNECTED)
  const [messageQueue, setMessageQueue] = useState<QueuedMessage[]>([])
  
  // Refs
  const socketRef = useRef<WebSocket | null>(null)
  const reconnectAttemptsRef = useRef<number>(0)
  const maxReconnectAttemptsRef = useRef<number>(10)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const keepAliveIntervalRef = useRef<NodeJS.Timeout | null>(null)
  const isReconnectingRef = useRef<boolean>(false)
  const currentAgentIdRef = useRef<string | undefined>(undefined)
  const eventListenersRef = useRef<((event: WebSocketEvent) => void)[]>([])

  // Connect to WebSocket
  const connect = useCallback((agentId?: string) => {
    // If already connected or reconnecting, return
    if (
      socketRef.current?.readyState === WebSocket.OPEN ||
      isReconnectingRef.current
    ) {
      return
    }

    // Update state
    isReconnectingRef.current = true
    setConnectionState(ConnectionState.CONNECTING)
    currentAgentIdRef.current = agentId

    // Create WebSocket URL
    const url = agentId ? `${WS_URL}/chat/${agentId}` : WS_URL
    console.log(`Connecting to WebSocket: ${url}`)

    // Create WebSocket
    socketRef.current = new WebSocket(url)

    // WebSocket event handlers
    socketRef.current.onopen = () => {
      console.log("WebSocket connected")
      reconnectAttemptsRef.current = 0
      isReconnectingRef.current = false
      setConnectionState(ConnectionState.CONNECTED)
      dispatchEvent({ type: "connect" })

      // Process any queued messages
      processMessageQueue()

      // Set up keep-alive ping
      if (keepAliveIntervalRef.current) {
        clearInterval(keepAliveIntervalRef.current)
      }

      keepAliveIntervalRef.current = setInterval(() => {
        if (isConnected()) {
          console.log("Sending keep-alive ping")
          try {
            socketRef.current!.send(JSON.stringify({ type: "ping" }))
          } catch (error) {
            console.error("Error sending keep-alive ping:", error)
            reconnect()
          }
        } else {
          reconnect()
        }
      }, 30000) // 30 seconds
    }

    socketRef.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        
        if (data.type === "message") {
          dispatchEvent({ 
            type: "message", 
            message: data.message 
          })
        } else if (data.type === "typing") {
          dispatchEvent({ 
            type: "typing", 
            agentId: data.agentId 
          })
        } else if (data.type === "log_update") {
          console.log("Log update received:", data)
          dispatchEvent({ 
            type: "log_update", 
            log: data.log,
            messageId: data.messageId
          })
        } else if (data.type === "pong") {
          // Received pong from server (keep-alive response)
          console.log("Received pong from server")
        }
      } catch (error) {
        console.error("Error parsing WebSocket message:", error)
      }
    }

    socketRef.current.onclose = (event) => {
      console.log("WebSocket disconnected:", event.reason)
      setConnectionState(ConnectionState.DISCONNECTED)
      dispatchEvent({ 
        type: "disconnect", 
        reason: event.reason 
      })
      
      socketRef.current = null
      
      // Attempt to reconnect if not closed intentionally
      if (!event.wasClean && reconnectAttemptsRef.current < maxReconnectAttemptsRef.current) {
        setConnectionState(ConnectionState.RECONNECTING)
        reconnectTimeoutRef.current = setTimeout(() => {
          reconnectAttemptsRef.current++
          connect(currentAgentIdRef.current)
        }, 1000 * Math.pow(2, reconnectAttemptsRef.current)) // Exponential backoff
      }
    }

    socketRef.current.onerror = (error) => {
      console.error("WebSocket error:", error)
      dispatchEvent({ 
        type: "error", 
        error: "Connection error" 
      })
    }
  }, [])

  // Disconnect from WebSocket
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }
    
    if (keepAliveIntervalRef.current) {
      clearInterval(keepAliveIntervalRef.current)
      keepAliveIntervalRef.current = null
    }
    
    if (socketRef.current) {
      socketRef.current.close()
      socketRef.current = null
    }

    setConnectionState(ConnectionState.DISCONNECTED)
  }, [])

  // Reconnect to WebSocket
  const reconnect = useCallback(() => {
    console.log("Reconnecting WebSocket...")
    disconnect()
    connect(currentAgentIdRef.current)
  }, [connect, disconnect])

  // Check if WebSocket is connected
  const isConnected = useCallback(() => {
    return socketRef.current !== null && socketRef.current.readyState === WebSocket.OPEN
  }, [])

  // Process message queue
  const processMessageQueue = useCallback(() => {
    if (!isConnected() || messageQueue.length === 0) return

    // Process each message in the queue
    const processQueue = async () => {
      const newQueue = [...messageQueue]
      
      for (let i = 0; i < newQueue.length; i++) {
        const queuedMessage = newQueue[i]
        
        try {
          const sent = await sendMessageInternal(
            queuedMessage.agentId,
            queuedMessage.content,
            queuedMessage.id,
            queuedMessage.timestamp
          )
          
          if (sent) {
            // Remove from queue if sent successfully
            newQueue.splice(i, 1)
            i--
          } else {
            // Increment retry count
            queuedMessage.retries++
            
            // Remove from queue if max retries reached
            if (queuedMessage.retries >= 3) {
              newQueue.splice(i, 1)
              i--
              
              // Dispatch error event
              dispatchEvent({
                type: "error",
                error: `Failed to send message after ${queuedMessage.retries} attempts`
              })
            }
          }
        } catch (error) {
          console.error("Error processing queued message:", error)
        }
      }
      
      setMessageQueue(newQueue)
    }
    
    processQueue()
  }, [messageQueue])

  // Send message internal implementation
  const sendMessageInternal = useCallback(
    async (
      agentId: string,
      content: string,
      id?: string,
      timestamp?: number
    ): Promise<boolean> => {
      if (!isConnected()) {
        console.log("WebSocket not connected, cannot send message")
        return false
      }
      
      try {
        socketRef.current!.send(JSON.stringify({
          type: "message",
          message: {
            role: "user",
            content,
            agentId,
            id,
            timestamp
          }
        }))
        console.log("Message sent successfully via WebSocket")
        return true
      } catch (error) {
        console.error("Error sending message:", error)
        return false
      }
    },
    []
  )

  // Send message (public API)
  const sendMessage = useCallback(
    async (agentId: string, content: string): Promise<boolean> => {
      // If not connected, add to queue and try to connect
      if (!isConnected()) {
        console.log("WebSocket not connected, queueing message")
        
        // Add to queue
        const queuedMessage: QueuedMessage = {
          agentId,
          content,
          retries: 0,
          id: Math.random().toString(36).substring(2, 9),
          timestamp: Date.now()
        }
        
        setMessageQueue(prev => [...prev, queuedMessage])
        
        // Try to connect
        connect(agentId)
        
        return false
      }
      
      // Send message directly
      return sendMessageInternal(agentId, content)
    },
    [connect, isConnected, sendMessageInternal]
  )

  // Add event listener
  const addEventListener = useCallback(
    (callback: (event: WebSocketEvent) => void): (() => void) => {
      eventListenersRef.current.push(callback)
      
      // Return unsubscribe function
      return () => {
        eventListenersRef.current = eventListenersRef.current.filter(cb => cb !== callback)
      }
    },
    []
  )

  // Dispatch event to all listeners
  const dispatchEvent = useCallback((event: WebSocketEvent) => {
    eventListenersRef.current.forEach(callback => callback(event))
  }, [])

  // Process message queue when connection state changes
  useEffect(() => {
    if (connectionState === ConnectionState.CONNECTED) {
      processMessageQueue()
    }
  }, [connectionState, processMessageQueue])

  // Clean up on unmount
  useEffect(() => {
    return () => {
      disconnect()
    }
  }, [disconnect])

  // Context value
  const contextValue: WebSocketContextType = {
    connectionState,
    sendMessage,
    addEventListener,
    connect,
    disconnect
  }

  return (
    <WebSocketContext.Provider value={contextValue}>
      {children}
    </WebSocketContext.Provider>
  )
}

// Hook to use WebSocket context
export function useWebSocket() {
  const context = useContext(WebSocketContext)
  
  if (context === undefined) {
    throw new Error("useWebSocket must be used within a WebSocketProvider")
  }
  
  return context
}
