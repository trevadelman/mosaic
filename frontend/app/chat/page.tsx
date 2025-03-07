"use client"

import { useState, useEffect } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { ChatInterface } from "@/components/chat/chat-interface"
import { AgentSelector } from "@/components/agents/agent-selector"
import { useAgents } from "@/lib/hooks/use-agents"
import { useChat } from "@/lib/hooks/use-chat"
import { useAgentContext } from "@/lib/contexts/agent-context"
import { Button } from "@/components/ui/button"
import { LayoutDashboard } from "lucide-react"

export default function ChatPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const agentIdFromUrl = searchParams.get('agentId')
  
  const { agents, selectedAgent, selectAgent, loading: agentsLoading } = useAgents()
  const { setCurrentAgentId } = useAgentContext()
  const { 
    messages, 
    sendMessage, 
    clearChat,
    refreshMessages,
    isProcessing, 
    error,
    connectionState
  } = useChat(selectedAgent?.id)
  
  // Set the current agent ID in context when it changes
  useEffect(() => {
    if (selectedAgent) {
      setCurrentAgentId(selectedAgent.id)
    }
  }, [selectedAgent, setCurrentAgentId])
  
  // Handle agent ID from URL
  useEffect(() => {
    if (agentIdFromUrl && agents.length > 0) {
      const agent = agents.find(a => a.id === agentIdFromUrl)
      if (agent) {
        selectAgent(agent)
      }
    }
  }, [agentIdFromUrl, agents, selectAgent])

  // Handle sending messages with attachments
  const handleSendMessage = (message: string, attachments?: File[]) => {
    sendMessage(message, attachments)
  }

  // Handle switching to agent UI
  const handleOpenUI = () => {
    if (selectedAgent) {
      router.push(`/agent-ui?agentId=${selectedAgent.id}`)
    }
  }

  return (
    <div className="flex h-full flex-col md:flex-row">
      {/* Agent selection sidebar */}
      <div className="w-full border-r md:w-80">
        <div className="flex h-full flex-col">
          <div className="border-b p-4">
            <h2 className="text-xl font-semibold">Agents</h2>
            <p className="text-sm text-muted-foreground">
              Select an agent to chat with
            </p>
          </div>
          <div className="flex-1 overflow-auto p-4">
            <AgentSelector 
              agents={agents} 
              selectedAgent={selectedAgent} 
              onSelect={selectAgent} 
              onOpenUI={handleOpenUI}
              loading={agentsLoading}
            />
          </div>
        </div>
      </div>

      {/* Chat interface */}
      <div className="flex-1">
        <ChatInterface
          messages={messages}
          onSendMessage={handleSendMessage}
          onClearChat={clearChat}
          refreshMessages={refreshMessages}
          isProcessing={isProcessing}
          selectedAgent={selectedAgent}
          error={error}
          connectionState={connectionState}
          onOpenUI={handleOpenUI}
        />
      </div>
    </div>
  )
}
