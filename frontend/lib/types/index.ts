// Agent types
export interface Tool {
  id: number;
  name: string;
  description: string;
  parameters: any[];
  returns: any;
}

export interface Agent {
  id: string;
  name: string;
  description: string;
  type: string;
  capabilities: string[];
  icon?: string;
  tools?: Tool[];
  relationships?: {
    supervisor?: string;
    subAgents?: string[];
  };
}

// Attachment types
export interface Attachment {
  id: number;
  type: string; // "image", "file", etc.
  filename: string;
  contentType: string;
  size: number;
  url?: string;
  data?: string; // Base64 encoded data for small attachments
}

// Conversation types
export interface Conversation {
  id: number;
  agentId: string;
  title: string;
  createdAt: string;
  updatedAt: string;
  isActive: boolean;
  userId?: string;
  messages?: Message[];
}

// Message types
export interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: number;
  agentId?: string;
  status?: "sending" | "sent" | "error";
  error?: string;
  logs?: string[];  // Array of log messages for this message
  attachments?: Attachment[]; // Array of attachments for this message
  channel?: string; // Channel for view-specific messages
  data?: any; // Additional data for view-specific messages
}

// Response types
export interface ApiResponse<T> {
  data?: T;
  error?: string;
}

// WebSocket event types
export type WebSocketEvent = 
  | { type: "connect" }
  | { type: "disconnect"; reason?: string }
  | { type: "message"; message: Message }
  | { type: "typing"; agentId: string }
  | { type: "log_update"; log: string; messageId: string }
  | { type: "error"; error: string };

// View-specific event types
export interface ViewEvent {
  type: string;
  data: any;
  channel?: string;
  timestamp: number;
}

// View-specific message types
export interface ViewMessage extends Omit<Message, "id" | "timestamp" | "status"> {
  channel?: string;
  data?: any;
}
