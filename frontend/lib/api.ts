import { Agent, ApiResponse, Message } from "./types"

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
}

/**
 * Chat API functions
 */
export const chatApi = {
  // Get chat history with a specific agent
  getMessages: (agentId: string) => 
    fetchApi<Message[]>(`/chat/${agentId}/messages`),

  // Send a message to an agent
  sendMessage: (agentId: string, content: string) =>
    fetchApi<Message>(`/chat/${agentId}/messages`, {
      method: "POST",
      body: JSON.stringify({ content }),
    }),
}
