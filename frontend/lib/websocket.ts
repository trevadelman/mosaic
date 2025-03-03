import { Message, WebSocketEvent } from "./types"

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws"

export class WebSocketService {
  private socket: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectTimeout: NodeJS.Timeout | null = null
  private eventListeners: Map<string, ((event: WebSocketEvent) => void)[]> = new Map()

  constructor(private agentId?: string) {}

  connect() {
    if (this.socket?.readyState === WebSocket.OPEN) return

    const url = this.agentId ? `${WS_URL}/chat/${this.agentId}` : WS_URL
    
    this.socket = new WebSocket(url)
    
    this.socket.onopen = () => {
      console.log("WebSocket connected")
      this.reconnectAttempts = 0
      this.dispatchEvent({ type: "connect" })
    }
    
    this.socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        
        if (data.type === "message") {
          this.dispatchEvent({ 
            type: "message", 
            message: data.message 
          })
        } else if (data.type === "typing") {
          this.dispatchEvent({ 
            type: "typing", 
            agentId: data.agentId 
          })
        } else if (data.type === "log_update") {
          console.log("Log update received:", data)
          this.dispatchEvent({ 
            type: "log_update", 
            log: data.log,
            messageId: data.messageId
          })
        }
      } catch (error) {
        console.error("Error parsing WebSocket message:", error)
      }
    }
    
    this.socket.onclose = (event) => {
      console.log("WebSocket disconnected:", event.reason)
      this.dispatchEvent({ 
        type: "disconnect", 
        reason: event.reason 
      })
      
      this.socket = null
      
      // Attempt to reconnect if not closed intentionally
      if (!event.wasClean && this.reconnectAttempts < this.maxReconnectAttempts) {
        this.reconnectTimeout = setTimeout(() => {
          this.reconnectAttempts++
          this.connect()
        }, 1000 * Math.pow(2, this.reconnectAttempts)) // Exponential backoff
      }
    }
    
    this.socket.onerror = (error) => {
      console.error("WebSocket error:", error)
      this.dispatchEvent({ 
        type: "error", 
        error: "Connection error" 
      })
    }
  }

  disconnect() {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout)
      this.reconnectTimeout = null
    }
    
    if (this.socket) {
      this.socket.close()
      this.socket = null
    }
  }

  sendMessage(message: Omit<Message, "id" | "timestamp" | "status">) {
    if (this.socket?.readyState !== WebSocket.OPEN) {
      this.dispatchEvent({ 
        type: "error", 
        error: "WebSocket not connected" 
      })
      return false
    }
    
    try {
      this.socket.send(JSON.stringify({
        type: "message",
        message
      }))
      return true
    } catch (error) {
      console.error("Error sending message:", error)
      this.dispatchEvent({ 
        type: "error", 
        error: "Failed to send message" 
      })
      return false
    }
  }

  addEventListener(callback: (event: WebSocketEvent) => void): () => void {
    const id = Math.random().toString(36).substring(2, 9)
    
    if (!this.eventListeners.has("event")) {
      this.eventListeners.set("event", [])
    }
    
    this.eventListeners.get("event")?.push(callback)
    
    // Return unsubscribe function
    return () => {
      const listeners = this.eventListeners.get("event") || []
      this.eventListeners.set(
        "event",
        listeners.filter(cb => cb !== callback)
      )
    }
  }

  private dispatchEvent(event: WebSocketEvent) {
    const listeners = this.eventListeners.get("event") || []
    listeners.forEach(callback => callback(event))
  }
}

// Singleton instance for app-wide use
let wsService: WebSocketService | null = null

export function getWebSocketService(agentId?: string): WebSocketService {
  if (!wsService) {
    wsService = new WebSocketService(agentId)
  } else if (agentId && wsService) {
    // If agent ID changed, disconnect and create new connection
    wsService.disconnect()
    wsService = new WebSocketService(agentId)
  }
  
  return wsService
}
