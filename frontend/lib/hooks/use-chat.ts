"use client"

import { useState, useEffect, useCallback } from "react"
import { v4 as uuidv4 } from "uuid"
import { useUser } from "@clerk/nextjs"
import { Message, Attachment } from "../types"
import { chatApi } from "../api"
import { mockMessages } from "../mock-data"
import { useWebSocket, ConnectionState } from "../contexts/websocket-context"
import { useAgentContext } from "../contexts/agent-context"

// Always use the actual API in Docker environment
const USE_MOCK_DATA = false

export function useChat(agentId?: string) {
  // Get agent context for preserving conversation state
  const { 
    conversationContext, 
    updateConversationContext, 
    clearConversationContext
  } = useAgentContext();
  
  // Initialize messages from context if available
  const initialMessages = agentId && conversationContext[agentId] 
    ? conversationContext[agentId].messages 
    : [];
  
  const [messages, setMessages] = useState<Message[]>(initialMessages)
  const [isProcessing, setIsProcessing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isInitialized, setIsInitialized] = useState(false)
  const [sentMessageContents, setSentMessageContents] = useState<Set<string>>(new Set())
  const { user } = useUser()
  
  // Get WebSocket context
  const { 
    connectionState, 
    sendMessage: wsSendMessage, 
    addEventListener, 
    connect,
    disconnect
  } = useWebSocket()
  
  // Update context when messages change
  useEffect(() => {
    if (agentId && messages.length > 0 && isInitialized) {
      // Get current messages from context
      const currentMessages = conversationContext[agentId]?.messages || [];
      
      // Only update if messages have actually changed
      if (JSON.stringify(currentMessages) !== JSON.stringify(messages)) {
        updateConversationContext(agentId, messages);
      }
    }
  }, [agentId, messages, updateConversationContext, isInitialized, conversationContext]);

  // Function to fetch messages from the API
  const fetchMessages = useCallback(async () => {
    if (!agentId) return
    
    // Get the user ID if available
    const userId = user?.id
    
    const response = await chatApi.getMessages(agentId, userId)
    
    if (response.error) {
      setError(response.error)
    } else if (response.data) {
      setMessages(response.data)
    }
    
    setIsInitialized(true)
  }, [agentId, user])

  // Initialize WebSocket connection and fetch messages when agentId changes
  useEffect(() => {
    if (!agentId) return

    // Reset messages when agent changes
    setMessages([])
    setIsProcessing(false)
    setError(null)
    
    console.log("Agent changed to:", agentId)

    if (USE_MOCK_DATA) {
      // Use mock data
      setTimeout(() => {
        if (mockMessages[agentId]) {
          setMessages(mockMessages[agentId])
        } else {
          setMessages([])
        }
        setIsInitialized(true)
      }, 500) // Simulate network delay
    } else {
      // Fetch message history from API
      fetchMessages()

      // Disconnect existing WebSocket connection
      console.log("Disconnecting existing WebSocket connection")
      disconnect()
      
      // Connect to WebSocket for this agent
      console.log("Connecting to WebSocket for agent:", agentId)
      connect(agentId)
    }
  }, [agentId, connect, disconnect, fetchMessages])

  // Set up WebSocket event listeners
  useEffect(() => {
    if (!agentId || USE_MOCK_DATA) return

    // Set up event listener
    const unsubscribe = addEventListener((event) => {
      if (event.type === "message" && event.message) {
        console.log("Received message event:", event.message)
        
        // For user messages, check if we've already sent this content
        if (event.message.role === "user") {
          const content = event.message.content
          
          // If we've already sent this message content, update the existing message
          if (sentMessageContents.has(content)) {
            setMessages(prev => 
              prev.map(msg => 
                (msg.role === "user" && msg.content === content)
                  ? { ...event.message, id: msg.id } // Keep our ID but update other fields
                  : msg
              )
            )
            return
          }
        }
        
        // Only add the message if it's not already in the list
        setMessages(prev => {
          const exists = prev.some(msg => msg.id === event.message.id)
          return exists ? prev : [...prev, event.message]
        })
        
        setIsProcessing(false)
      } else if (event.type === "log_update" && event.messageId) {
        console.log("Received log update:", event.log, "for message:", event.messageId)
        
        // Add log to the appropriate message
        setMessages(prev => 
          prev.map(msg => 
            msg.id === event.messageId
              ? { 
                  ...msg, 
                  logs: [...(msg.logs || []), event.log] 
                }
              : msg
          )
        )
      } else if (event.type === "error") {
        console.error("Received error event:", event.error)
        setError(event.error)
        setIsProcessing(false)
      } else if (event.type === "connect") {
        console.log("WebSocket connected")
        setError(null)
      }
    })

    // Clean up
    return () => {
      unsubscribe()
    }
  }, [agentId, addEventListener, sentMessageContents])

  // Update UI based on connection state
  useEffect(() => {
    if (connectionState === ConnectionState.DISCONNECTED) {
      // Only show error if we've already initialized
      if (isInitialized) {
        setError("Connection lost. Reconnecting...")
      }
    } else if (connectionState === ConnectionState.CONNECTED) {
      // Clear connection error when connected
      if (error === "Connection lost. Reconnecting...") {
        setError(null)
      }
    }
  }, [connectionState, error, isInitialized])

  // Process files and convert to base64
  const processFiles = async (files: File[]): Promise<Attachment[]> => {
    const attachments: Attachment[] = []
    
    for (const file of files) {
      // Create a new attachment
      const attachment: Attachment = {
        id: Date.now() + Math.floor(Math.random() * 1000), // Temporary ID
        type: file.type,
        filename: file.name,
        contentType: file.type,
        size: file.size,
      }
      
      // Convert file to base64 for all file types
      try {
        const base64 = await readFileAsBase64(file)
        attachment.data = base64
      } catch (error) {
        console.error("Error converting file to base64:", error)
      }
      
      attachments.push(attachment)
    }
    
    return attachments
  }
  
  // Helper function to read file as base64
  const readFileAsBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = () => {
        if (typeof reader.result === 'string') {
          // Remove the data URL prefix (e.g., "data:image/jpeg;base64,")
          const base64 = reader.result.split(',')[1]
          resolve(base64)
        } else {
          reject(new Error('FileReader result is not a string'))
        }
      }
      reader.onerror = reject
      reader.readAsDataURL(file)
    })
  }

  // Send a message with optional attachments
  const sendMessage = useCallback(
    async (content: string, attachments?: File[]) => {
      if (!agentId || (!content.trim() && !attachments?.length)) return

      setError(null)
      setIsProcessing(true)

      // Process attachments if any
      let processedAttachments: Attachment[] | undefined
      if (attachments && attachments.length > 0) {
        console.log("Processing attachments:", attachments)
        processedAttachments = await processFiles(attachments)
        console.log("Processed attachments:", processedAttachments)
      }

      // Create a temporary message
      const tempMessage: Message = {
        id: uuidv4(),
        role: "user",
        content,
        timestamp: Date.now(),
        agentId,
        status: "sending",
        attachments: processedAttachments
      }

      // Check if a similar message was recently added
      const recentDuplicate = messages.some(msg => 
        msg.content === content && 
        msg.role === "user" &&
        Date.now() - msg.timestamp < 5000 // Within last 5 seconds
      )
      
      // Only add the message if it's not a duplicate
      if (!recentDuplicate) {
        // Add to messages immediately for UI feedback
        setMessages(prev => [...prev, tempMessage])
        
        // Track this message content as sent
        setSentMessageContents(prev => {
          const newSet = new Set(prev)
          newSet.add(content)
          return newSet
        })
      }

      if (USE_MOCK_DATA) {
        // Simulate API delay
        setTimeout(() => {
          // Update message status to sent
          setMessages(prev => 
            prev.map(msg => 
              msg.id === tempMessage.id 
                ? { ...msg, status: "sent" } 
                : msg
            )
          )
          
          // Simulate agent response after a delay
          setTimeout(() => {
            const responseMessage: Message = {
              id: uuidv4(),
              role: "assistant",
              content: `This is a mock response to: "${content}"`,
              timestamp: Date.now(),
              agentId
            }
            
            setMessages(prev => [...prev, responseMessage])
            setIsProcessing(false)
          }, 1500)
        }, 500)
      } else {
        try {
          // Try to send via WebSocket
          console.log("Sending message via WebSocket:", content, processedAttachments ? `with ${processedAttachments.length} attachments` : "")
          
          // Send message with attachments
          const sent = await wsSendMessage(agentId, content, "message", processedAttachments)
          console.log("Message sent successfully:", sent)
          
          // Update message status to sent
          setMessages(prev => 
            prev.map(msg => 
              msg.id === tempMessage.id 
                ? { ...msg, status: "sent" } 
                : msg
            )
          )
          
          if (!sent) {
            // If WebSocket send failed but we're still trying to connect,
            // don't fall back to API yet
            if (connectionState === ConnectionState.CONNECTING || 
                connectionState === ConnectionState.RECONNECTING) {
              console.log("Message queued, waiting for connection...")
            } else {
              // Fallback to API if WebSocket fails and we're not connecting
              console.log("Falling back to API")
              const userId = user?.id
              const response = await chatApi.sendMessage(agentId, content, userId)
              
              if (response.error) {
                setError(response.error)
                setIsProcessing(false)
                
                // Update message status to error
                setMessages(prev => 
                  prev.map(msg => 
                    msg.id === tempMessage.id 
                      ? { ...msg, status: "error", error: response.error } 
                      : msg
                  )
                )
              }
            }
          }
        } catch (error) {
          console.error("Error sending message:", error)
          setError("Failed to send message")
          setIsProcessing(false)
          
          // Update message status to error
          setMessages(prev => 
            prev.map(msg => 
              msg.id === tempMessage.id 
                ? { ...msg, status: "error", error: "Failed to send message" } 
                : msg
            )
          )
        }
      }
    },
    [agentId, connectionState, wsSendMessage, messages, sentMessageContents, user]
  )

  // Clear chat history
  const clearChat = useCallback(async () => {
    if (!agentId) return
    
    try {
      // Get the user ID if available
      const userId = user?.id
      
      // Try to clear via WebSocket first
      if (connectionState === ConnectionState.CONNECTED) {
        console.log("Clearing chat via WebSocket")
        const cleared = await wsSendMessage(agentId, "", "clear_conversation")
        
        if (cleared) {
          // Reset messages
          setMessages([])
          setError(null)
          
          // Clear conversation context
          clearConversationContext(agentId)
          return
        }
      }
      
      // Fallback to API
      console.log("Clearing chat via API")
      const response = await chatApi.clearMessages(agentId, userId)
      
      if (response.error) {
        setError(response.error)
      } else {
        // Reset messages
        setMessages([])
        setError(null)
        
        // Clear conversation context
        clearConversationContext(agentId)
      }
    } catch (error) {
      console.error("Error clearing chat:", error)
      setError("Failed to clear chat")
    }
  }, [agentId, connectionState, wsSendMessage, user, clearConversationContext])

  return {
    messages,
    sendMessage,
    clearChat,
    refreshMessages: fetchMessages,
    isProcessing,
    error,
    connectionState
  }
}
