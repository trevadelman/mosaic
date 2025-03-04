"use client"

import { useAgentDetails } from "@/lib/hooks/use-agent-details"
import { Agent } from "@/lib/types"
import { Loader2, Wrench, Link } from "lucide-react"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"

interface AgentDetailsProps {
  agent: Agent | null
}

export function AgentDetails({ agent }: AgentDetailsProps) {
  const { tools, relationships, loading, error } = useAgentDetails({
    agentId: agent?.id || null,
  })

  if (!agent) {
    return null
  }

  return (
    <div className="space-y-4">
      <Accordion type="multiple" className="w-full">
        {/* Tools Section */}
        <AccordionItem value="tools">
          <AccordionTrigger className="text-sm font-medium">
            <div className="flex items-center gap-2">
              <Wrench className="h-4 w-4" />
              <span>Tools ({loading ? "..." : tools.length})</span>
            </div>
          </AccordionTrigger>
          <AccordionContent>
            {loading ? (
              <div className="flex items-center justify-center py-4">
                <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                <span className="ml-2 text-sm text-muted-foreground">Loading tools...</span>
              </div>
            ) : error ? (
              <div className="py-2 text-sm text-destructive">{error}</div>
            ) : tools.length === 0 ? (
              <div className="py-2 text-sm text-muted-foreground">No tools available</div>
            ) : (
              <div className="space-y-2">
                {tools.map((tool) => (
                  <div key={tool.id} className="rounded-md border p-3">
                    <h4 className="font-medium">{tool.name}</h4>
                    <p className="text-sm text-muted-foreground">{tool.description}</p>
                    
                    {tool.parameters.length > 0 && (
                      <div className="mt-2">
                        <h5 className="text-xs font-medium text-muted-foreground">Parameters:</h5>
                        <ul className="mt-1 space-y-1">
                          {tool.parameters.map((param, index) => (
                            <li key={index} className="text-xs">
                              <span className="font-mono">{param.name}</span>
                              {param.required && <span className="text-destructive">*</span>}
                              {param.description && (
                                <span className="text-muted-foreground"> - {param.description}</span>
                              )}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </AccordionContent>
        </AccordionItem>

        {/* Relationships Section */}
        <AccordionItem value="relationships">
          <AccordionTrigger className="text-sm font-medium">
            <div className="flex items-center gap-2">
              <Link className="h-4 w-4" />
              <span>Relationships</span>
            </div>
          </AccordionTrigger>
          <AccordionContent>
            {loading ? (
              <div className="flex items-center justify-center py-4">
                <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                <span className="ml-2 text-sm text-muted-foreground">Loading relationships...</span>
              </div>
            ) : error ? (
              <div className="py-2 text-sm text-destructive">{error}</div>
            ) : (
              <div className="space-y-2">
                {relationships?.supervisor ? (
                  <div className="rounded-md border p-3">
                    <h4 className="text-sm font-medium">Supervisor</h4>
                    <p className="text-sm">{relationships.supervisor}</p>
                  </div>
                ) : (
                  <div className="py-2 text-sm text-muted-foreground">No supervisor</div>
                )}

                {relationships?.subAgents && relationships.subAgents.length > 0 ? (
                  <div className="rounded-md border p-3">
                    <h4 className="text-sm font-medium">Sub-Agents</h4>
                    <ul className="mt-1">
                      {relationships.subAgents.map((subAgent, index) => (
                        <li key={index} className="text-sm">{subAgent}</li>
                      ))}
                    </ul>
                  </div>
                ) : (
                  <div className="py-2 text-sm text-muted-foreground">No sub-agents</div>
                )}
              </div>
            )}
          </AccordionContent>
        </AccordionItem>
      </Accordion>
    </div>
  )
}
