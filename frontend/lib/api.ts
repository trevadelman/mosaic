import { Agent, ApiResponse, Conversation, Message, Tool } from "./types"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

/**
 * Generic fetch function with error handling
 */
async function fetchApi<T>(
  endpoint: string,
  options?: RequestInit
): Promise<ApiResponse<T>> {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
    })

    const data = await response.json()

    if (!response.ok) {
      return { error: data.detail || "An error occurred" }
    }

    return { data }
  } catch (error) {
    console.error("API error:", error)
    return { error: "Failed to connect to the server" }
  }
}

/**
 * Agent API functions
 */
export const agentApi = {
  // Get all available agents
  getAgents: () => fetchApi<Agent[]>("/agents"),

  // Get a specific agent by ID
  getAgent: (id: string) => fetchApi<Agent>(`/agents/${id}`),
  
  // Get tools for a specific agent
  getAgentTools: (id: string) => fetchApi<Tool[]>(`/agents/${id}/tools`),
  
  // Get relationships for a specific agent
  getAgentRelationships: (id: string) => fetchApi<Agent['relationships']>(`/agents/${id}/relationships`),
}

/**
 * Chat API functions
 */
export const chatApi = {
  // Get chat history with a specific agent
  getMessages: (agentId: string, userId?: string) => 
    fetchApi<Message[]>(`/chat/${agentId}/messages${userId ? `?user_id=${userId}` : ''}`),

  // Send a message to an agent
  sendMessage: (agentId: string, content: string, userId?: string) =>
    fetchApi<Message>(`/chat/${agentId}/messages${userId ? `?user_id=${userId}` : ''}`, {
      method: "POST",
      body: JSON.stringify({ content }),
    }),
    
  // Clear chat history with a specific agent
  clearMessages: (agentId: string, userId?: string) =>
    fetchApi<{status: string, message: string}>(`/chat/${agentId}/messages${userId ? `?user_id=${userId}` : ''}`, {
      method: "DELETE",
    }),
    
  // Get conversation history for a specific agent
  getConversations: (agentId: string, userId?: string) =>
    fetchApi<Conversation[]>(`/chat/${agentId}/conversations${userId ? `?user_id=${userId}` : ''}`),
    
  // Activate a specific conversation
  activateConversation: (agentId: string, conversationId: number, userId?: string) =>
    fetchApi<Conversation>(`/chat/${agentId}/conversations/${conversationId}/activate${userId ? `?user_id=${userId}` : ''}`, {
      method: "POST",
    }),
    
  // Delete a specific conversation
  deleteConversation: (agentId: string, conversationId: number) =>
    fetchApi<{status: string, message: string}>(`/chat/${agentId}/conversations/${conversationId}`, {
      method: "DELETE",
    }),
}

/**
 * User Data API functions
 */
export const userDataApi = {
  // Export user data
  exportUserData: (userId: string) => {
    window.location.href = `${API_BASE_URL}/user-data/export?user_id=${userId}`;
    return Promise.resolve({ data: { status: "success" } });
  },
  
  // Delete user data
  deleteUserData: (userId: string) =>
    fetchApi<{status: string, message: string}>(`/user-data/delete?user_id=${userId}`, {
      method: "DELETE",
    }),
    
  // Clear user conversations
  clearUserConversations: (userId: string) =>
    fetchApi<{status: string, message: string}>(`/user-data/clear-conversations?user_id=${userId}`, {
      method: "DELETE",
    }),
}
