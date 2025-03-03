"use client"

import { useState, useEffect } from "react"
import { ChatInterface } from "@/components/chat/chat-interface"
import { AgentSelector } from "@/components/agents/agent-selector"
import { useAgents } from "@/lib/hooks/use-agents"
import { useChat } from "@/lib/hooks/use-chat"

export default function ChatPage() {
  const { agents, selectedAgent, selectAgent, loading: agentsLoading } = useAgents()
  const { 
    messages, 
    sendMessage, 
    isProcessing, 
    error 
  } = useChat(selectedAgent?.id)

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
              loading={agentsLoading}
            />
          </div>
        </div>
      </div>

      {/* Chat interface */}
      <div className="flex-1">
        <ChatInterface
          messages={messages}
          onSendMessage={sendMessage}
          isProcessing={isProcessing}
          selectedAgent={selectedAgent}
          error={error}
        />
      </div>
    </div>
  )
}
