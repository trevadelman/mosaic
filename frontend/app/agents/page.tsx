"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useAgents } from "@/lib/hooks/use-agents"
import { AgentSelector } from "@/components/agents/agent-selector"
import { BrainCircuit, LayoutDashboard, MessageSquare } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Agent } from "@/lib/types"

export default function AgentsPage() {
  const router = useRouter()
  const { agents, loading, error } = useAgents()
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null)

  // Handle selecting an agent
  const handleSelectAgent = (agent: Agent) => {
    setSelectedAgent(agent)
  }

  // Handle opening the agent UI
  const handleOpenUI = (agent: Agent) => {
    router.push(`/agent-ui?agentId=${agent.id}`)
  }

  // Handle opening the chat
  const handleOpenChat = () => {
    if (selectedAgent) {
      router.push(`/chat?agentId=${selectedAgent.id}`)
    }
  }

  return (
    <div className="container mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Agents</h1>
        <p className="text-muted-foreground">
          View and manage available agents in the MOSAIC system
        </p>
      </div>

      {error && (
        <div className="mb-6 rounded-lg border border-destructive bg-destructive/10 p-4 text-destructive">
          <p className="font-medium">Error loading agents</p>
          <p className="text-sm">{error}</p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-1 border rounded-lg p-4">
          <h2 className="text-xl font-bold mb-4">Available Agents</h2>
          <AgentSelector
            agents={agents}
            selectedAgent={selectedAgent}
            onSelect={handleSelectAgent}
            onOpenUI={handleOpenUI}
            loading={loading}
          />
        </div>
        
        <div className="md:col-span-2">
          {selectedAgent ? (
            <div className="border rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-bold">{selectedAgent.name}</h2>
                <div className="flex items-center gap-2">
                  <span className="rounded-full bg-primary/10 px-2.5 py-0.5 text-xs font-medium text-primary">
                    {selectedAgent.type}
                  </span>
                </div>
              </div>
              
              <p className="text-muted-foreground mb-6">{selectedAgent.description}</p>
              
              {selectedAgent.capabilities && selectedAgent.capabilities.length > 0 && (
                <div className="mb-6">
                  <h3 className="font-semibold mb-2">Capabilities</h3>
                  <div className="flex flex-wrap gap-2">
                    {selectedAgent.capabilities.map((capability: string) => (
                      <span
                        key={capability}
                        className="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold"
                      >
                        {capability}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              
              {selectedAgent.tools && selectedAgent.tools.length > 0 && (
                <div className="mb-6">
                  <h3 className="font-semibold mb-2">Tools</h3>
                  <div className="flex flex-wrap gap-2">
                    {selectedAgent.tools.map((tool: any) => (
                      <span
                        key={tool.id}
                        className="inline-flex items-center rounded-full bg-secondary px-2.5 py-0.5 text-xs font-semibold"
                        title={tool.description}
                      >
                        {tool.name}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              
              <div className="flex justify-end gap-2">
                <Button
                  variant="outline"
                  onClick={() => handleOpenUI(selectedAgent)}
                  className="flex items-center gap-2"
                >
                  <LayoutDashboard className="h-4 w-4" />
                  Open UI
                </Button>
                <Button
                  onClick={handleOpenChat}
                  className="flex items-center gap-2"
                >
                  <MessageSquare className="h-4 w-4" />
                  Chat with Agent
                </Button>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center rounded-lg border p-12 text-center h-full">
              <BrainCircuit className="h-12 w-12 text-muted-foreground" />
              <h2 className="mt-4 text-xl font-semibold">No agent selected</h2>
              <p className="mt-2 text-muted-foreground">
                Select an agent from the list to view details and interact with it.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
