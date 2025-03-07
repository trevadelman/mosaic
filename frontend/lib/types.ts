// Agent types
export interface Tool {
  id: number
  name: string
  description: string
  parameters: any[]
  returns: any
}

export interface Agent {
  id: string
  name: string
  description: string
  type: string
  capabilities: string[]
  icon?: string
  tools?: Tool[]
  relationships?: {
    supervisor?: string
    subAgents?: string[]
  }
  hasUI?: boolean
}

// Attachment types
export interface Attachment {
  id: number
  type: string // "image", "file", etc.
  filename: string
  contentType: string
  size: number
  url?: string
  data?: string // Base64 encoded data for small attachments
}

// Conversation types
export interface Conversation {
  id: number
  agentId: string
  title: string
  createdAt: string
  updatedAt: string
  isActive: boolean
  userId?: string
  messages?: Message[]
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
  attachments?: Attachment[] // Array of attachments for this message
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
  | { type: "ui_event", data: any }
  | { type: "component_registrations", data: any }
