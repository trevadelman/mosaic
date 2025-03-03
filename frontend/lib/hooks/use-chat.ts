"use client"

import { useState, useEffect, useCallback } from "react"
import { v4 as uuidv4 } from "uuid"
import { Message } from "../types"
import { chatApi } from "../api"
import { getWebSocketService } from "../websocket"
import { mockMessages } from "../mock-data"

// Always use the actual API in Docker environment
const USE_MOCK_DATA = false

export function useChat(agentId?: string) {
  const [messages, setMessages] = useState<Message[]>([])
  const [isProcessing, setIsProcessing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Initialize WebSocket connection when agentId changes
  useEffect(() => {
    if (!agentId) return

    if (USE_MOCK_DATA) {
      // Use mock data
      setTimeout(() => {
        if (mockMessages[agentId]) {
          setMessages(mockMessages[agentId])
        } else {
          setMessages([])
        }
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
      }

      fetchMessages()

      // Set up WebSocket connection
      const ws = getWebSocketService(agentId)
      ws.connect()

      // Set up event listener
      const unsubscribe = ws.addEventListener((event) => {
        if (event.type === "message" && event.message) {
          setMessages(prev => [...prev, event.message])
          setIsProcessing(false)
        } else if (event.type === "log_update" && event.messageId) {
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
          setError(event.error)
          setIsProcessing(false)
        }
      })

      // Clean up
      return () => {
        unsubscribe()
        ws.disconnect()
      }
    }
  }, [agentId])

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

      // Add to messages immediately for UI feedback
      setMessages(prev => [...prev, tempMessage])

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
          // Try to send via WebSocket first
          const ws = getWebSocketService(agentId)
          const sent = ws.sendMessage({
            role: "user",
            content,
            agentId
          })
          
          if (!sent) {
            // Fallback to API if WebSocket fails
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
            } else if (response.data) {
              // Update message status to sent
              setMessages(prev => 
                prev.map(msg => 
                  msg.id === tempMessage.id 
                    ? { ...msg, status: "sent" } 
                    : msg
                )
              )
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
    [agentId]
  )

  return {
    messages,
    sendMessage,
    isProcessing,
    error
  }
}
