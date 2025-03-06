"use client"

import { useState, useEffect } from "react"
import { useUser } from "@clerk/nextjs"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { chatApi } from "@/lib/api"
import { Conversation } from "@/lib/types"
import { formatDistanceToNow } from "date-fns"
import { 
  Sheet, 
  SheetContent, 
  SheetHeader, 
  SheetTitle, 
  SheetTrigger,
  SheetClose
} from "@/components/ui/sheet"
import { 
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"
import { 
  Clock, 
  MessageSquare, 
  MoreVertical, 
  Trash2,
  RotateCw
} from "lucide-react"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

interface ConversationHistoryProps {
  agentId: string
  onConversationSelect: () => void
}

export function ConversationHistory({ agentId, onConversationSelect }: ConversationHistoryProps) {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isOpen, setIsOpen] = useState(false)
  const { user } = useUser()
  
  // Fetch conversations when the component mounts or when agentId changes
  useEffect(() => {
    if (isOpen && agentId) {
      fetchConversations()
    }
  }, [agentId, isOpen])
  
  // Fetch conversations from the API
  const fetchConversations = async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      const userId = user?.id
      const response = await chatApi.getConversations(agentId, userId)
      
      if (response.error) {
        setError(response.error)
      } else if (response.data) {
        setConversations(response.data)
      }
    } catch (err) {
      setError("Failed to fetch conversation history")
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }
  
  // Activate a conversation
  const activateConversation = async (conversationId: number) => {
    setIsLoading(true)
    setError(null)
    
    try {
      const userId = user?.id
      const response = await chatApi.activateConversation(agentId, conversationId, userId)
      
      if (response.error) {
        setError(response.error)
      } else {
        // Close the panel and notify parent
        setIsOpen(false)
        onConversationSelect()
      }
    } catch (err) {
      setError("Failed to activate conversation")
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }
  
  // Delete a conversation
  const deleteConversation = async (conversationId: number) => {
    setIsLoading(true)
    setError(null)
    
    try {
      const response = await chatApi.deleteConversation(agentId, conversationId)
      
      if (response.error) {
        setError(response.error)
      } else {
        // Refresh the conversation list
        fetchConversations()
      }
    } catch (err) {
      setError("Failed to delete conversation")
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }
  
  // Format the date for display
  const formatDate = (dateString: string) => {
    try {
      return formatDistanceToNow(new Date(dateString), { addSuffix: true })
    } catch (err) {
      return "Unknown date"
    }
  }
  
  // Get a preview of the conversation content
  const getConversationPreview = (conversation: Conversation) => {
    if (conversation.messages && conversation.messages.length > 0) {
      // Get the last message
      const lastMessage = conversation.messages[conversation.messages.length - 1]
      // Truncate the content if it's too long
      return lastMessage.content.length > 50
        ? `${lastMessage.content.substring(0, 50)}...`
        : lastMessage.content
    }
    return "No messages"
  }
  
  return (
    <Sheet open={isOpen} onOpenChange={setIsOpen}>
      <SheetTrigger asChild>
        <Button 
          variant="outline" 
          size="sm" 
          className="flex items-center gap-2 hover:bg-blue-50 hover:text-blue-600 hover:border-blue-200 transition-colors"
          title="View conversation history"
          onClick={() => {
            // Fetch conversations when the button is clicked
            if (!isOpen) {
              fetchConversations()
            }
          }}
        >
          <MessageSquare className="h-4 w-4" />
          <span>History</span>
          {conversations.length > 0 && (
            <span className="ml-1 bg-blue-100 text-blue-800 text-xs px-1.5 py-0.5 rounded-full">
              {conversations.length}
            </span>
          )}
        </Button>
      </SheetTrigger>
      <SheetContent side="right" className="w-[350px] sm:w-[450px]">
        <SheetHeader>
          <SheetTitle className="flex items-center">
            <MessageSquare className="h-5 w-5 mr-2 text-blue-500" />
            <span>Conversation History</span>
          </SheetTitle>
          <p className="text-sm text-muted-foreground">
            Select a previous conversation to continue
          </p>
        </SheetHeader>
        
        {error && (
          <div className="bg-red-50 text-red-800 p-3 rounded-md mt-4 flex items-center">
            <div className="bg-red-100 rounded-full p-1 mr-2">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-red-600" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div>
              <p className="text-sm font-medium">Error loading conversations</p>
              <p className="text-xs">{error}</p>
            </div>
          </div>
        )}
        
        {isLoading ? (
          <div className="flex flex-col justify-center items-center h-40">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mb-2"></div>
            <p className="text-sm text-gray-500">Loading conversations...</p>
          </div>
        ) : conversations.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-40 text-center p-4">
            <div className="bg-gray-100 rounded-full p-3 mb-3">
              <MessageSquare className="h-6 w-6 text-gray-400" />
            </div>
            <p className="text-gray-500 font-medium mb-1">No conversation history</p>
            <p className="text-xs text-gray-400">
              Start a new chat to create conversation history
            </p>
          </div>
        ) : (
          <div className="mt-4 space-y-2">
            {conversations.map((conversation) => (
              <div 
                key={conversation.id} 
                className={`p-3 rounded-md border cursor-pointer transition-colors ${
                  conversation.isActive 
                    ? "bg-blue-50 border-blue-200" 
                    : "bg-white hover:bg-blue-50 hover:border-blue-100 border-gray-200"
                }`}
                onClick={() => activateConversation(conversation.id)}
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center">
                      {conversation.isActive ? (
                        <>
                          <div className="w-2 h-2 bg-blue-600 rounded-full mr-2 animate-pulse" title="Active conversation" />
                          <h3 className="font-medium text-sm truncate text-blue-800">
                            {conversation.title || `Conversation ${conversation.id}`}
                          </h3>
                        </>
                      ) : (
                        <h3 className="font-medium text-sm truncate text-gray-800">
                          {conversation.title || `Conversation ${conversation.id}`}
                        </h3>
                      )}
                    </div>
                    <div className="flex items-center text-gray-500 text-xs mt-1">
                      <span className="mr-2">{formatDate(conversation.updatedAt)}</span>
                      <span className="bg-gray-100 px-1.5 py-0.5 rounded">#{conversation.id}</span>
                    </div>
                  </div>
                  
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                      <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                        <MoreVertical className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem 
                        onClick={(e) => {
                          e.stopPropagation();
                          activateConversation(conversation.id);
                        }}
                        disabled={conversation.isActive}
                      >
                        <MessageSquare className="mr-2 h-4 w-4" />
                        <span>Switch to this conversation</span>
                      </DropdownMenuItem>
                      
                      <AlertDialog>
                        <AlertDialogTrigger asChild>
                          <DropdownMenuItem onSelect={(e: Event) => e.preventDefault()}>
                            <Trash2 className="mr-2 h-4 w-4" />
                            <span>Delete conversation</span>
                          </DropdownMenuItem>
                        </AlertDialogTrigger>
                        <AlertDialogContent>
                          <AlertDialogHeader>
                            <AlertDialogTitle>Delete conversation?</AlertDialogTitle>
                            <AlertDialogDescription>
                              This action cannot be undone. This will permanently delete this
                              conversation and all its messages.
                            </AlertDialogDescription>
                          </AlertDialogHeader>
                          <AlertDialogFooter>
                            <AlertDialogCancel>Cancel</AlertDialogCancel>
                            <AlertDialogAction 
                              onClick={(e) => {
                                e.stopPropagation();
                                deleteConversation(conversation.id);
                              }}
                              className="bg-red-600 hover:bg-red-700"
                            >
                              Delete
                            </AlertDialogAction>
                          </AlertDialogFooter>
                        </AlertDialogContent>
                      </AlertDialog>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
                
                {conversation.isActive ? (
                  <div className="mt-2 p-2 bg-blue-100 rounded-md border border-blue-200 text-blue-800 flex items-center justify-center">
                    <div className="h-3 w-3 bg-blue-600 rounded-full mr-1.5 animate-pulse" />
                    <p className="text-xs font-medium">
                      Currently active
                    </p>
                  </div>
                ) : (
                  <div className="mt-2 p-2 bg-gray-100 rounded-md border border-gray-200 text-gray-700 flex items-center justify-center hover:bg-blue-50 hover:text-blue-700 hover:border-blue-200 transition-colors">
                    <MessageSquare className="h-3 w-3 mr-1.5" />
                    <p className="text-xs font-medium">
                      Click to activate
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </SheetContent>
    </Sheet>
  )
}
