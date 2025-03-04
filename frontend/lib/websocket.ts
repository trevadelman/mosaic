import { Message, WebSocketEvent } from "./types"

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws"

export class WebSocketService {
  private socket: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectTimeout: NodeJS.Timeout | null = null
  private eventListeners: Map<string, ((event: WebSocketEvent) => void)[]> = new Map()
  private keepAliveInterval: NodeJS.Timeout | null = null
  private isReconnecting = false
  private lastSentMessageId: string | null = null
  private sentMessages = new Set<string>()

  constructor(private agentId?: string) {}

  connect() {
    if (this.socket?.readyState === WebSocket.OPEN) return
    if (this.isReconnecting) return

    this.isReconnecting = true
    const url = this.agentId ? `${WS_URL}/chat/${this.agentId}` : WS_URL
    
    console.log(`Connecting to WebSocket: ${url}`)
    this.socket = new WebSocket(url)
    
    this.socket.onopen = () => {
      console.log("WebSocket connected")
      this.reconnectAttempts = 0
      this.isReconnecting = false
      this.dispatchEvent({ type: "connect" })
      
      // Set up keep-alive ping every 30 seconds
      if (this.keepAliveInterval) {
        clearInterval(this.keepAliveInterval)
      }
      
      this.keepAliveInterval = setInterval(() => {
        if (this.isConnected()) {
          console.log("Sending keep-alive ping")
          try {
            this.socket!.send(JSON.stringify({ type: "ping" }))
          } catch (error) {
            console.error("Error sending keep-alive ping:", error)
            this.reconnect()
          }
        } else {
          this.reconnect()
        }
      }, 30000) // 30 seconds
    }
    
    this.socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        
        if (data.type === "message") {
          // Check if this is a response to a message we sent
          const clientMessageId = data.message?.clientMessageId
          
          if (clientMessageId) {
            // If we've already processed this message, ignore it
            if (this.sentMessages.has(clientMessageId)) {
              console.log("Ignoring duplicate message with ID:", clientMessageId)
              return
            }
            
            // Mark this message as processed
            this.sentMessages.add(clientMessageId)
          }
          
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
    
    if (this.keepAliveInterval) {
      clearInterval(this.keepAliveInterval)
      this.keepAliveInterval = null
    }
    
    if (this.socket) {
      this.socket.close()
      this.socket = null
    }
  }
  
  reconnect() {
    console.log("Reconnecting WebSocket...")
    this.disconnect()
    this.connect()
  }
  
  isConnected(): boolean {
    return this.socket !== null && this.socket.readyState === WebSocket.OPEN
  }

  async sendMessage(message: Omit<Message, "id" | "timestamp" | "status">): Promise<boolean> {
    // If socket is not connected, try to connect
    if (!this.isConnected()) {
      console.log("WebSocket not connected, attempting to connect...")
      this.connect()
      
      // Wait for connection to establish
      let attempts = 0
      const maxAttempts = 5
      
      while (!this.isConnected() && attempts < maxAttempts) {
        console.log(`Waiting for WebSocket connection... Attempt ${attempts + 1}/${maxAttempts}`)
        await new Promise(resolve => setTimeout(resolve, 500))
        attempts++
      }
      
      if (!this.isConnected()) {
        console.error("Failed to establish WebSocket connection after multiple attempts")
        this.dispatchEvent({ 
          type: "error", 
          error: "WebSocket connection failed" 
        })
        return false
      }
    }
    
    try {
      // Generate a client-side message ID to track this message
      const clientMessageId = `client-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`
      
      // Store the message ID to prevent duplication
      this.lastSentMessageId = clientMessageId
      
      this.socket!.send(JSON.stringify({
        type: "message",
        message: {
          ...message,
          clientMessageId
        }
      }))
      console.log("Message sent successfully via WebSocket with ID:", clientMessageId)
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
