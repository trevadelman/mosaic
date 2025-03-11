"use client";

import { ViewContainer } from "@/components/agents/view-container";
import { useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { 
  AgentView, 
  AgentWithView, 
  ToolAccess, 
  UpdateSystem,
  ViewMessage 
} from "@/lib/types/agent-view";
import { WebSocketEvent, Message } from "@/lib/types";
import { useWebSocket } from "@/lib/hooks/use-websocket";
import { agentApi, chatApi } from "@/lib/api";

interface AgentViewPageProps {
  params: {
    name: string;
  };
}

// Simple event emitter for component communication
class EventEmitter {
  private events: Record<string, Array<(data: any) => void>> = {};

  subscribe(channel: string, handler: (data: any) => void): () => void {
    if (!this.events[channel]) {
      this.events[channel] = [];
    }
    this.events[channel].push(handler);
    
    return () => {
      this.events[channel] = this.events[channel].filter(h => h !== handler);
    };
  }

  publish(channel: string, data: any): void {
    if (this.events[channel]) {
      this.events[channel].forEach(handler => {
        try {
          handler(data);
        } catch (err) {
          console.error(`Error in event handler for channel ${channel}:`, err);
        }
      });
    }
  }
}

export default function AgentViewPage({ params }: AgentViewPageProps) {
  const router = useRouter();
  const ws = useWebSocket();
  
  // State
  const [agent, setAgent] = useState<AgentWithView | null>(null);
  const [view, setView] = useState<AgentView | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  
  // Create a ref for the event emitter to ensure it persists across renders
  const eventEmitterRef = useRef<EventEmitter>(new EventEmitter());
  
  // Load agent data
  useEffect(() => {
    async function loadAgent() {
      try {
        // Use the agentApi instead of direct fetch
        const response = await agentApi.getAgent(params.name);
        
        if (response.error) {
          throw new Error(response.error);
        }
        
        if (!response.data) {
          throw new Error('Agent data not found');
        }
        
        console.log("Agent data:", response.data);
        
        // Add hasCustomView property if it doesn't exist
        const agentData = {
          ...response.data,
          hasCustomView: true, // Assume all agents have custom views for now
          custom_view: {
            name: `${response.data.name}View`,
            layout: 'split',
            capabilities: []
          }
        } as AgentWithView;
        
        setAgent(agentData);
      } catch (err) {
        console.error("Error loading agent:", err);
        setError(err instanceof Error ? err : new Error('Unknown error'));
      } finally {
        setLoading(false);
      }
    }
    
    loadAgent();
  }, [params.name]);
  
  // Load view component
  useEffect(() => {
    if (agent) {
      import(`@/components/agents/${params.name}/view/index`)
        .then(module => {
          console.log("Loaded view component:", module.default);
          setView(module.default);
        })
        .catch(err => {
          console.error('Error loading view:', err);
          setError(new Error('Failed to load view components'));
        });
    }
  }, [agent, params.name]);

  // Tool access setup - using chat API
  const tools: ToolAccess = {};
  
  // Dynamically add tool methods based on the view's tool requirements
  if (agent && view) {
    view.tools.forEach(toolName => {
      tools[toolName] = async (...args: any[]) => {
        console.log(`Invoking tool ${toolName} through chat with args:`, args);
        
        try {
          // Format the message to instruct the agent to use a specific tool
          let message = `Use the ${toolName} tool with the following parameters:\n\n`;
          
          // Format the parameters based on the tool
          if (toolName === 'search_location') {
            // For search_location, the first argument is the query
            const query = args[0];
            message += `query: "${query}"`;
          } else if (toolName === 'get_weather_forecast_by_coordinates') {
            // For get_weather_forecast_by_coordinates, we need latitude, longitude, and days
            // Handle both object and individual parameters
            let latitude, longitude, days;
            
            if (typeof args[0] === 'object' && args[0] !== null) {
              // If first argument is an object with parameters
              const params = args[0];
              latitude = params.latitude || params.lat;
              longitude = params.longitude || params.lon;
              days = params.days || 5;
            } else {
              // If parameters are passed individually
              latitude = args[0];
              longitude = args[1];
              days = args[2] || 5;
            }
            
            message += `latitude: ${latitude}\nlongitude: ${longitude}\ndays: ${days}`;
            console.log(`Formatted forecast parameters: lat=${latitude}, lon=${longitude}, days=${days}`);
          } else {
            // For other tools, just stringify the arguments
            message += `Arguments: ${JSON.stringify(args)}`;
          }
          
          // Send the message to the agent
          console.log(`Sending message to agent: ${message}`);
          const response = await chatApi.sendMessage(agent.id, message);
          
          if (response.error) {
            throw new Error(response.error);
          }
          
          if (!response.data) {
            throw new Error('No response from agent');
          }
          
          console.log(`Chat response for tool ${toolName}:`, response.data);
          
          // Get the agent's response
          const messages = await chatApi.getMessages(agent.id);
          
          if (messages.error) {
            throw new Error(messages.error);
          }
          
          if (!messages.data || messages.data.length === 0) {
            throw new Error('No messages found');
          }
          
          // Find the latest assistant message
          const assistantMessages = messages.data.filter(m => m.role === 'assistant');
          if (assistantMessages.length === 0) {
            throw new Error('No assistant messages found');
          }
          
          const latestMessage = assistantMessages[assistantMessages.length - 1];
          console.log(`Latest assistant message:`, latestMessage);
          
          // Return the content of the latest assistant message
          return latestMessage.content;
        } catch (err) {
          console.error(`Error executing tool ${toolName}:`, err);
          throw err;
        }
      };
    });
  }

  // Update system setup - using the event emitter
  const updates: UpdateSystem = {
    subscribe: (channel: string, handler: (data: any) => void) => {
      console.log(`Subscribing to channel: ${channel}`);
      return eventEmitterRef.current.subscribe(channel, handler);
    },
    publish: (channel: string, data: any) => {
      console.log(`Publishing to channel ${channel}:`, data);
      eventEmitterRef.current.publish(channel, data);
    }
  };

  // Handle loading and error states
  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (error || !agent) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-8">
        <h2 className="text-xl font-bold text-destructive">Error</h2>
        <p className="mt-2 text-muted-foreground">{error?.message || 'Agent not found'}</p>
        <button 
          className="mt-4 text-primary hover:underline"
          onClick={() => router.back()}
        >
          Go Back
        </button>
      </div>
    );
  }

  if (!view) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  // Render the view
  return (
    <ViewContainer
      agent={agent}
      layout={view.layout}
      config={view.layoutConfig}
      className="p-4"
    >
      {Object.entries(view.components).map(([key, Component]) => (
        Component && (
          <div key={key} className="h-full">
            <Component 
              agent={agent}
              tools={tools}
              updates={updates}
            />
          </div>
        )
      ))}
    </ViewContainer>
  );
}
