"use client"

import { useRef, useEffect } from "react"
import { Message as MessageType, Agent } from "@/lib/types"
import { Message } from "./message"
import { ChatInput } from "./chat-input"
import { AlertCircle, Loader2, Wifi, WifiOff, Trash2 } from "lucide-react"
import { ConnectionState } from "@/lib/contexts/websocket-context"
import { Button } from "@/components/ui/button"

interface ChatInterfaceProps {
  messages: MessageType[]
  onSendMessage: (message: string) => void
  onClearChat?: () => void
  isProcessing?: boolean
  selectedAgent: Agent | null
  error?: string | null
  connectionState?: ConnectionState
}

export function ChatInterface({
  messages,
  onSendMessage,
  onClearChat,
  isProcessing = false,
  selectedAgent,
  error,
  connectionState = ConnectionState.DISCONNECTED
}: ChatInterfaceProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Scroll to bottom when messages change
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" })
    }
    
    // Debug messages
    console.log("Messages updated:", messages)
  }, [messages])

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="border-b p-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold">
            {selectedAgent ? selectedAgent.name : "Chat"}
          </h2>
          
          <div className="flex items-center gap-3">
            {/* Clear chat button */}
            {messages.length > 0 && onClearChat && (
              <Button
                variant="ghost"
                size="sm"
                className="h-8 px-2 text-muted-foreground hover:text-foreground"
                onClick={onClearChat}
                disabled={isProcessing}
                title="Clear conversation"
              >
                <Trash2 className="h-4 w-4 mr-1" />
                <span className="text-xs">Clear</span>
              </Button>
            )}
            
            {/* Connection status indicator */}
            {connectionState && (
              <div className="flex items-center gap-1 text-xs">
                {connectionState === ConnectionState.CONNECTED ? (
                  <>
                    <Wifi className="h-3 w-3 text-green-500" />
                    <span className="text-green-500">Connected</span>
                  </>
                ) : connectionState === ConnectionState.CONNECTING ? (
                  <>
                    <Loader2 className="h-3 w-3 animate-spin text-yellow-500" />
                    <span className="text-yellow-500">Connecting</span>
                  </>
                ) : connectionState === ConnectionState.RECONNECTING ? (
                  <>
                    <Loader2 className="h-3 w-3 animate-spin text-yellow-500" />
                    <span className="text-yellow-500">Reconnecting</span>
                  </>
                ) : (
                  <>
                    <WifiOff className="h-3 w-3 text-destructive" />
                    <span className="text-destructive">Disconnected</span>
                  </>
                )}
              </div>
            )}
          </div>
        </div>
        
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
