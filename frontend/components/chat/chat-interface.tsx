"use client"

import { useRef, useEffect } from "react"
import { Message as MessageType, Agent } from "@/lib/types"
import { Message } from "./message"
import { ChatInput } from "./chat-input"
import { AlertCircle, Loader2 } from "lucide-react"

interface ChatInterfaceProps {
  messages: MessageType[]
  onSendMessage: (message: string) => void
  isProcessing?: boolean
  selectedAgent: Agent | null
  error?: string | null
}

export function ChatInterface({
  messages,
  onSendMessage,
  isProcessing = false,
  selectedAgent,
  error
}: ChatInterfaceProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Scroll to bottom when messages change
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" })
    }
  }, [messages])

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="border-b p-4">
        <h2 className="text-xl font-semibold">
          {selectedAgent ? selectedAgent.name : "Chat"}
        </h2>
        {selectedAgent && (
          <p className="text-sm text-muted-foreground">
            {selectedAgent.description}
          </p>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto">
        {messages.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center p-8 text-center">
            <div className="rounded-full bg-primary/10 p-3">
              <div className="rounded-full bg-primary/20 p-2">
                {selectedAgent ? (
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary text-primary-foreground">
                    {selectedAgent.icon || selectedAgent.name.charAt(0)}
                  </div>
                ) : (
                  <div className="h-10 w-10 rounded-full bg-muted" />
                )}
              </div>
            </div>
            <h3 className="mt-6 text-xl font-semibold">
              {selectedAgent
                ? `Chat with ${selectedAgent.name}`
                : "Select an agent to start chatting"}
            </h3>
            <p className="mt-2 text-sm text-muted-foreground max-w-md">
              {selectedAgent
                ? `${selectedAgent.description}`
                : "Choose an agent from the sidebar to begin a conversation."}
            </p>
          </div>
        ) : (
          <div className="divide-y">
            {messages.map((message, i) => (
              <Message
                key={message.id}
                message={message}
                isLastMessage={i === messages.length - 1}
              />
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Error message */}
      {error && (
        <div className="mx-4 my-2 flex items-center gap-2 rounded-lg border border-destructive bg-destructive/10 p-3 text-sm text-destructive">
          <AlertCircle className="h-4 w-4" />
          <p>{error}</p>
        </div>
      )}

      {/* Processing indicator */}
      {isProcessing && (
        <div className="mx-4 my-2 flex items-center gap-2 rounded-lg border bg-muted p-3 text-sm">
          <Loader2 className="h-4 w-4 animate-spin" />
          <p>{selectedAgent ? `${selectedAgent.name} is thinking...` : "Processing..."}</p>
        </div>
      )}

      {/* Input */}
      <div className="border-t p-4">
        <ChatInput
          onSendMessage={onSendMessage}
          isDisabled={isProcessing || !selectedAgent}
          placeholder={
            selectedAgent
              ? `Message ${selectedAgent.name}...`
              : "Select an agent to start chatting"
          }
        />
      </div>
    </div>
  )
}
