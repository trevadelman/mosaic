// Agent types
export interface Agent {
  id: string
  name: string
  description: string
  type: string
  capabilities: string[]
  icon?: string
}

// Message types
export interface Message {
  id: string
  role: "user" | "assistant" | "system"
  content: string
  timestamp: number
  agentId?: string
  status?: "sending" | "sent" | "error"
  error?: string
  logs?: string[]  // Array of log messages for this message
}

// Response types
export interface ApiResponse<T> {
  data?: T
  error?: string
}

// WebSocket event types
export type WebSocketEvent = 
  | { type: "connect" }
  | { type: "disconnect", reason?: string }
  | { type: "message", message: Message }
  | { type: "typing", agentId: string }
  | { type: "log_update", log: string, messageId: string }
  | { type: "error", error: string }
