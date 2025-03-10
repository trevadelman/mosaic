"use client"

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { Agent, Message } from '../types';
import { useRouter, usePathname, useSearchParams } from 'next/navigation';

interface AgentContextType {
  currentAgentId: string | null;
  setCurrentAgentId: (agentId: string | null) => void;
  conversationContext: Record<string, {
    messages: Message[];
    lastActive: number;
  }>;
  updateConversationContext: (agentId: string, messages: Message[]) => void;
  clearConversationContext: (agentId: string) => void;
}

const AgentContext = createContext<AgentContextType | undefined>(undefined);

export function AgentProvider({ children }: { children: ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  
  // Get agentId from URL if available
  const agentIdFromUrl = searchParams.get('agentId');
  
  // State for current agent ID
  const [currentAgentId, setCurrentAgentId] = useState<string | null>(agentIdFromUrl);
  
  // State for conversation context
  const [conversationContext, setConversationContext] = useState<Record<string, {
    messages: Message[];
    lastActive: number;
  }>>({});
  
  // Update current agent ID when URL changes
  useEffect(() => {
    if (agentIdFromUrl && agentIdFromUrl !== currentAgentId) {
      setCurrentAgentId(agentIdFromUrl);
    }
  }, [agentIdFromUrl, currentAgentId]);
  
  // Update conversation context for an agent
  const updateConversationContext = (agentId: string, messages: Message[]) => {
    setConversationContext(prev => ({
      ...prev,
      [agentId]: {
        messages,
        lastActive: Date.now()
      }
    }));
  };
  
  // Clear conversation context for an agent
  const clearConversationContext = (agentId: string) => {
    setConversationContext(prev => {
      const newContext = { ...prev };
      delete newContext[agentId];
      return newContext;
    });
  };
  
  // Clean up old conversation contexts (older than 1 hour)
  useEffect(() => {
    const cleanupInterval = setInterval(() => {
      const oneHourAgo = Date.now() - 60 * 60 * 1000;
      
      setConversationContext(prev => {
        const newContext = { ...prev };
        
        Object.keys(newContext).forEach(agentId => {
          if (newContext[agentId].lastActive < oneHourAgo) {
            delete newContext[agentId];
          }
        });
        
        return newContext;
      });
    }, 15 * 60 * 1000); // Run every 15 minutes
    
    return () => clearInterval(cleanupInterval);
  }, []);
  
  return (
    <AgentContext.Provider
      value={{
        currentAgentId,
        setCurrentAgentId,
        conversationContext,
        updateConversationContext,
        clearConversationContext
      }}
    >
      {children}
    </AgentContext.Provider>
  );
}

export function useAgentContext() {
  const context = useContext(AgentContext);
  
  if (context === undefined) {
    throw new Error('useAgentContext must be used within an AgentProvider');
  }
  
  return context;
}
