"use client"

import { Agent } from "@/lib/types"
import { BrainCircuit } from "lucide-react"

interface AgentSelectorProps {
  agents: Agent[]
  selectedAgent: Agent | null
  onSelect: (agent: Agent) => void
  loading?: boolean
}

export function AgentSelector({
  agents,
  selectedAgent,
  onSelect,
  loading = false
}: AgentSelectorProps) {
  if (loading) {
    return (
      <div className="space-y-2">
        {[...Array(3)].map((_, i) => (
          <div
            key={i}
            className="flex items-center gap-3 rounded-lg p-3 animate-pulse"
          >
            <div className="h-10 w-10 rounded-full bg-muted"></div>
            <div className="space-y-2 flex-1">
              <div className="h-4 w-24 rounded bg-muted"></div>
              <div className="h-3 w-full rounded bg-muted"></div>
            </div>
          </div>
        ))}
      </div>
    )
  }

  if (agents.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-10 text-center">
        <BrainCircuit className="h-10 w-10 text-muted-foreground" />
        <h3 className="mt-4 text-lg font-medium">No agents available</h3>
        <p className="mt-2 text-sm text-muted-foreground">
          There are no agents available at the moment.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-2">
      {agents.map((agent) => (
        <button
          key={agent.id}
          onClick={() => onSelect(agent)}
          className={`flex w-full items-start gap-3 rounded-lg p-3 text-left transition-colors hover:bg-accent ${
            selectedAgent?.id === agent.id ? "bg-accent" : ""
          }`}
        >
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground">
            {agent.icon ? (
              <span className="text-lg">{agent.icon}</span>
            ) : (
              <BrainCircuit className="h-5 w-5" />
            )}
          </div>
          <div className="flex-1 space-y-1">
            <div className="flex items-center justify-between">
              <p className="font-medium leading-none">{agent.name}</p>
              <p className="text-xs text-muted-foreground">{agent.type}</p>
            </div>
            <p className="text-sm text-muted-foreground line-clamp-2">
              {agent.description}
            </p>
            {agent.capabilities && agent.capabilities.length > 0 && (
              <div className="flex flex-wrap gap-1 pt-1">
                {agent.capabilities.slice(0, 3).map((capability) => (
                  <span
                    key={capability}
                    className="inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-semibold"
                  >
                    {capability}
                  </span>
                ))}
                {agent.capabilities.length > 3 && (
                  <span className="inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-semibold">
                    +{agent.capabilities.length - 3}
                  </span>
                )}
              </div>
            )}
          </div>
        </button>
      ))}
    </div>
  )
}
