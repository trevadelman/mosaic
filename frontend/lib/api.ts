import { Agent, ApiResponse, Message, Tool } from "./types"

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
  
  // Get all agents from the database
  getDbAgents: () => fetchApi<Agent[]>("/agent-creator/db/agents"),
  
  // Get a specific agent from the database by ID
  getDbAgent: (id: number) => fetchApi<Agent>(`/agent-creator/db/agents/${id}`),
  
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
  getMessages: (agentId: string) => 
    fetchApi<Message[]>(`/chat/${agentId}/messages`),

  // Send a message to an agent
  sendMessage: (agentId: string, content: string) =>
    fetchApi<Message>(`/chat/${agentId}/messages`, {
      method: "POST",
      body: JSON.stringify({ content }),
    }),
    
  // Clear chat history with a specific agent
  clearMessages: (agentId: string) =>
    fetchApi<{status: string, message: string}>(`/chat/${agentId}/messages`, {
      method: "DELETE",
    }),
}

/**
 * Agent Creator API functions
 */
export const agentCreatorApi = {
  // Get the agent schema
  getSchema: () => fetchApi<any>("/agent-creator/schema"),

  // Get all available templates
  getTemplates: () => fetchApi<any[]>("/agent-creator/templates"),

  // Get a specific template by ID
  getTemplate: (id: string) => fetchApi<any>(`/agent-creator/templates/${id}`),

  // Create a new agent template
  createTemplate: (template: any) => 
    fetchApi<any>("/agent-creator/template", {
      method: "POST",
      body: JSON.stringify(template),
    }),

  // Add a tool to a template
  addTool: (template: any, tool: any) => 
    fetchApi<any>("/agent-creator/add-tool", {
      method: "POST",
      body: JSON.stringify({ template, tool }),
    }),

  // Validate a template
  validateTemplate: (template: any) => 
    fetchApi<any>("/agent-creator/validate", {
      method: "POST",
      body: JSON.stringify(template),
    }),

  // Generate code for a template
  generateCode: (template: any) => 
    fetchApi<any>("/agent-creator/generate-code", {
      method: "POST",
      body: JSON.stringify(template),
    }),

  // Deploy an agent
  deployAgent: (template: any, options: any) => 
    fetchApi<any>("/agent-creator/deploy", {
      method: "POST",
      body: JSON.stringify({ template, options }),
    }),

  // Save a template
  saveTemplate: (id: string, template: any) => 
    fetchApi<any>(`/agent-creator/templates/${id}`, {
      method: "POST",
      body: JSON.stringify(template),
    }),
}
