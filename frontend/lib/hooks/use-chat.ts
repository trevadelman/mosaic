"use client"

import { useState, useEffect, useCallback } from "react"
import { v4 as uuidv4 } from "uuid"
import { Message } from "../types"
import { chatApi } from "../api"
import { mockMessages } from "../mock-data"
import { useWebSocket, ConnectionState } from "../contexts/websocket-context"

// Always use the actual API in Docker environment
const USE_MOCK_DATA = false

export function useChat(agentId?: string) {
  const [messages, setMessages] = useState<Message[]>([])
  const [isProcessing, setIsProcessing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isInitialized, setIsInitialized] = useState(false)
  const [sentMessageContents, setSentMessageContents] = useState<Set<string>>(new Set())
  
  // Get WebSocket context
  const { 
    connectionState, 
    sendMessage: wsSendMessage, 
    addEventListener, 
    connect,
    disconnect
  } = useWebSocket()

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
      const fetchMessages = async () => {
        if (!agentId) return
        
        const response = await chatApi.getMessages(agentId)
        
        if (response.error) {
          setError(response.error)
        } else if (response.data) {
          setMessages(response.data)
        }
        
        setIsInitialized(true)
      }

      fetchMessages()

      // Disconnect existing WebSocket connection
      console.log("Disconnecting existing WebSocket connection")
      disconnect()
      
      // Connect to WebSocket for this agent
      console.log("Connecting to WebSocket for agent:", agentId)
      connect(agentId)
    }
  }, [agentId, connect, disconnect])

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

  // Send a message
  const sendMessage = useCallback(
    async (content: string) => {
      if (!agentId || !content.trim()) return

      setError(null)
      setIsProcessing(true)

      // Create a temporary message
      const tempMessage: Message = {
        id: uuidv4(),
        role: "user",
        content,
        timestamp: Date.now(),
        agentId,
        status: "sending"
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
          console.log("Sending message via WebSocket:", content)
          const sent = await wsSendMessage(agentId, content)
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
              const response = await chatApi.sendMessage(agentId, content)
              
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
    [agentId, connectionState, wsSendMessage, messages, sentMessageContents]
  )

  // Clear chat history
  const clearChat = useCallback(async () => {
    if (!agentId) return
    
    try {
      // Try to clear via WebSocket first
      if (connectionState === ConnectionState.CONNECTED) {
        console.log("Clearing chat via WebSocket")
        const cleared = await wsSendMessage(agentId, "", "clear_conversation")
        
        if (cleared) {
          // Reset messages
          setMessages([])
          setError(null)
          return
        }
      }
      
      // Fallback to API
      console.log("Clearing chat via API")
      const response = await chatApi.clearMessages(agentId)
      
      if (response.error) {
        setError(response.error)
      } else {
        // Reset messages
        setMessages([])
        setError(null)
      }
    } catch (error) {
      console.error("Error clearing chat:", error)
      setError("Failed to clear chat")
    }
  }, [agentId, connectionState, wsSendMessage])

  return {
    messages,
    sendMessage,
    clearChat,
    isProcessing,
    error,
    connectionState
  }
}
