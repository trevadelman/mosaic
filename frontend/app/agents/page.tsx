"use client"

import { useState } from "react"
import { useAgents } from "@/lib/hooks/use-agents"
import { BrainCircuit, Info, Settings } from "lucide-react"

export default function AgentsPage() {
  const { agents, loading, error } = useAgents()
  const [selectedAgentId, setSelectedAgentId] = useState<string | null>(null)

  const selectedAgent = agents.find(agent => agent.id === selectedAgentId)

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

      {loading ? (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <div
              key={i}
              className="rounded-lg border bg-card p-6 shadow-sm animate-pulse"
            >
              <div className="flex items-center gap-4">
                <div className="h-12 w-12 rounded-full bg-muted"></div>
                <div className="space-y-2">
                  <div className="h-4 w-24 rounded bg-muted"></div>
                  <div className="h-3 w-32 rounded bg-muted"></div>
                </div>
              </div>
              <div className="mt-4 space-y-2">
                <div className="h-3 w-full rounded bg-muted"></div>
                <div className="h-3 w-4/5 rounded bg-muted"></div>
              </div>
            </div>
          ))}
        </div>
      ) : agents.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-lg border bg-card p-12 text-center shadow-sm">
          <BrainCircuit className="h-12 w-12 text-muted-foreground" />
          <h2 className="mt-4 text-xl font-semibold">No agents available</h2>
          <p className="mt-2 text-muted-foreground">
            There are no agents registered in the system.
          </p>
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {agents.map((agent) => (
            <div
              key={agent.id}
              className={`rounded-lg border bg-card p-6 shadow-sm transition-colors hover:border-primary/50 ${
                selectedAgentId === agent.id ? "border-primary" : ""
              }`}
              onClick={() => setSelectedAgentId(agent.id)}
            >
              <div className="flex items-center gap-4">
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary text-primary-foreground">
                  {agent.icon ? (
                    <span className="text-lg">{agent.icon}</span>
                  ) : (
                    <BrainCircuit className="h-6 w-6" />
                  )}
                </div>
                <div>
                  <h3 className="font-semibold">{agent.name}</h3>
                  <p className="text-sm text-muted-foreground">{agent.type}</p>
                </div>
              </div>
              <p className="mt-4 text-sm text-muted-foreground">
                {agent.description}
              </p>
              {agent.capabilities && agent.capabilities.length > 0 && (
                <div className="mt-4 flex flex-wrap gap-2">
                  {agent.capabilities.map((capability) => (
                    <span
                      key={capability}
                      className="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold"
                    >
                      {capability}
                    </span>
                  ))}
                </div>
              )}
              <div className="mt-6 flex justify-end gap-2">
                <button
                  className="inline-flex h-8 w-8 items-center justify-center rounded-md text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                  aria-label="Agent information"
                >
                  <Info className="h-4 w-4" />
                </button>
                <button
                  className="inline-flex h-8 w-8 items-center justify-center rounded-md text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                  aria-label="Agent settings"
                >
                  <Settings className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {selectedAgent && (
        <div className="mt-8 rounded-lg border bg-card p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold">{selectedAgent.name}</h2>
            <div className="flex items-center gap-2">
              <span className="rounded-full bg-primary/10 px-2.5 py-0.5 text-xs font-medium text-primary">
                {selectedAgent.type}
              </span>
            </div>
          </div>
          <p className="mt-2 text-muted-foreground">{selectedAgent.description}</p>
          
          <div className="mt-6">
            <h3 className="font-semibold">Capabilities</h3>
            <div className="mt-2 flex flex-wrap gap-2">
              {selectedAgent.capabilities.map((capability) => (
                <span
                  key={capability}
                  className="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold"
                >
                  {capability}
                </span>
              ))}
            </div>
          </div>
          
          <div className="mt-6 flex justify-end gap-2">
            <button
              className="inline-flex h-9 items-center justify-center rounded-md border bg-background px-4 text-sm font-medium shadow-sm transition-colors hover:bg-accent hover:text-accent-foreground"
              onClick={() => window.location.href = `/chat?agent=${selectedAgent.id}`}
            >
              Chat with Agent
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
