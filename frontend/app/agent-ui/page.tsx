"use client"

/**
 * Agent UI Page
 * 
 * This page displays the agent UI for a specific agent.
 * It allows users to interact with the agent through specialized UI components.
 */

import React, { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAgents } from '@/lib/hooks/use-agents';
import { useAgentContext } from '@/lib/contexts/agent-context';
import AgentUIContainer from '@/components/agent-ui/agent-ui-container';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Loader2 } from 'lucide-react';

export default function AgentUIPage() {
  // Get the agent ID from the query parameters
  const searchParams = useSearchParams();
  const router = useRouter();
  const agentId = searchParams.get('agentId');
  
  // Get the agent data
  const { agents, loading: agentsLoading } = useAgents();
  const { setCurrentAgentId } = useAgentContext();
  const [agent, setAgent] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  // Generate a client ID for the UI components
  const [clientId] = useState<string>(`client-${Math.random().toString(36).substring(2, 9)}`);
  
  // Update current agent ID in context
  useEffect(() => {
    if (agentId) {
      setCurrentAgentId(agentId);
    }
  }, [agentId, setCurrentAgentId]);
  
  // Find the agent in the list of agents
  useEffect(() => {
    if (!agentId) {
      setError('No agent ID provided');
      setLoading(false);
      return;
    }
    
    if (!agentsLoading && agents) {
      const foundAgent = agents.find((a) => a.id === agentId);
      
      if (foundAgent) {
        setAgent(foundAgent);
        setError(null);
      } else {
        setError(`Agent with ID ${agentId} not found`);
      }
      
      setLoading(false);
    }
  }, [agentId, agents, agentsLoading]);
  
  // Handle switching to chat
  const handleSwitchToChat = () => {
    router.push(`/chat?agentId=${agentId}`);
  };
  
  // Handle going back to the agents list
  const handleBackToAgents = () => {
    router.push('/agents');
  };
  
  // Render the page
  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b">
        <div className="flex items-center">
          <Button variant="ghost" onClick={handleBackToAgents} className="mr-2">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Agents
          </Button>
        </div>
      </div>
      
      {/* Content */}
      <div className="flex-grow overflow-hidden p-4">
        {loading || agentsLoading ? (
          <div className="flex flex-col items-center justify-center h-full">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
              Loading agent UI...
            </p>
          </div>
        ) : error ? (
          <div className="flex flex-col items-center justify-center h-full">
            <p className="text-red-500">{error}</p>
            <Button onClick={handleBackToAgents} className="mt-4">
              Back to Agents
            </Button>
          </div>
        ) : agent ? (
          <AgentUIContainer
            agentId={agent.id}
            agentName={agent.name}
            onSwitchToChat={handleSwitchToChat}
            clientId={clientId}
          />
        ) : (
          <div className="flex flex-col items-center justify-center h-full">
            <p className="text-gray-500 dark:text-gray-400">
              No agent selected
            </p>
            <Button onClick={handleBackToAgents} className="mt-4">
              Back to Agents
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
