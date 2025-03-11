"use client"

import { Agent } from "@/lib/types"
import { BrainCircuit, Layout } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import Link from "next/link"
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion"

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

  // Group agents by type
  const groupedAgents = agents.reduce<Record<string, Agent[]>>((groups, agent) => {
    const type = agent.type || 'Other';
    if (!groups[type]) {
      groups[type] = [];
    }
    groups[type].push(agent);
    return groups;
  }, {});

  // Sort group names
  const sortedGroupNames = Object.keys(groupedAgents).sort((a, b) => {
    // Put "Supervisor" groups first
    if (a.includes('Supervisor') && !b.includes('Supervisor')) return -1;
    if (!a.includes('Supervisor') && b.includes('Supervisor')) return 1;
    // Then sort alphabetically
    return a.localeCompare(b);
  });

  return (
    <Accordion type="multiple" className="space-y-2" defaultValue={[]}>
      {sortedGroupNames.map((type) => (
        <AccordionItem key={type} value={type} className="border-none">
          <AccordionTrigger className="py-2 px-3 text-sm font-medium text-muted-foreground hover:no-underline">
            {type}
          </AccordionTrigger>
          <AccordionContent className="pb-1 pt-0">
            <div className="space-y-1">
              {groupedAgents[type].map((agent) => (
                <div
                  key={agent.id}
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
                    <div className="flex justify-between items-center">
                      <p className="font-medium leading-none">{agent.name}</p>
                      {agent.hasCustomView && (
                        <Link href={`/agents/${agent.id}/view`} onClick={(e) => e.stopPropagation()}>
                          <Badge 
                            variant="outline" 
                            className="ml-2 bg-blue-100 text-blue-800 hover:bg-blue-200 cursor-pointer"
                          >
                            <Layout className="h-3 w-3 mr-1" />
                            UI
                          </Badge>
                        </Link>
                      )}
                    </div>
                    <button
                      onClick={() => onSelect(agent)}
                      className="w-full text-left"
                    >
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
                      {agent.tools && agent.tools.length > 0 && (
                        <div className="flex flex-wrap gap-1 pt-1">
                          <span className="text-xs text-muted-foreground">Tools:</span>
                          {agent.tools.slice(0, 2).map((tool) => (
                            <span
                              key={tool.id}
                              className="inline-flex items-center rounded-full bg-secondary px-2 py-0.5 text-xs font-semibold"
                              title={tool.description}
                            >
                              {tool.name}
                            </span>
                          ))}
                          {agent.tools.length > 2 && (
                            <span className="inline-flex items-center rounded-full bg-secondary px-2 py-0.5 text-xs font-semibold">
                              +{agent.tools.length - 2}
                            </span>
                          )}
                        </div>
                      )}
                      {agent.relationships && (agent.relationships.supervisor || (agent.relationships.subAgents && agent.relationships.subAgents.length > 0)) && (
                        <div className="flex flex-wrap gap-1 pt-1">
                          {agent.relationships.supervisor && (
                            <span className="text-xs text-muted-foreground">
                              Supervisor: {agent.relationships.supervisor}
                            </span>
                          )}
                          {agent.relationships.subAgents && agent.relationships.subAgents.length > 0 && (
                            <span className="text-xs text-muted-foreground">
                              Sub-agents: {agent.relationships.subAgents.length}
                            </span>
                          )}
                        </div>
                      )}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </AccordionContent>
        </AccordionItem>
      ))}
    </Accordion>
  )
}
