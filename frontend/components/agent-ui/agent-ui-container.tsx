/**
 * Agent UI Container Component
 * 
 * This component serves as the main container for agent-specific UI components.
 * It handles the loading, rendering, and communication with UI components
 * registered for a specific agent.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useWebSocket } from '../../lib/contexts/websocket-context';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Loader2, MessageSquare, LayoutDashboard } from 'lucide-react';

// Import UI component implementations
import { StockChart as StockChartComponent } from './financial/stock-chart';
// No other components needed for now

// Define the props for the AgentUIContainer component
interface AgentUIContainerProps {
  agentId: string;
  agentName: string;
  onSwitchToChat: () => void;
  clientId: string;
}

// Define the UI component type
interface UIComponent {
  id: string;
  name: string;
  description: string;
  features: string[];
}

// Component registry mapping component IDs to their React implementations
const componentRegistry: Record<string, React.ComponentType<any>> = {
  'stock-chart': StockChartComponent,
};

const AgentUIContainer: React.FC<AgentUIContainerProps> = ({
  agentId,
  agentName,
  onSwitchToChat,
  clientId,
}) => {
  // State for available UI components
  const [components, setComponents] = useState<UIComponent[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [activeComponent, setActiveComponent] = useState<string | null>(null);
  
  // Get the WebSocket connection
  const websocket = useWebSocket();
  const isConnected = websocket.connectionState === 'connected';
  
  // Agent-specific UI WebSocket connection
  const [uiSocket, setUiSocket] = useState<WebSocket | null>(null);
  
  // Connect to the agent-specific UI WebSocket
  useEffect(() => {
    if (!agentId) return;
    
    // Create a WebSocket connection to the UI endpoint for this agent
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws';
    console.log(`Connecting to agent-specific UI WebSocket at ${wsUrl}/ui/${agentId}`);
    
    const socket = new WebSocket(`${wsUrl}/ui/${agentId}`);
    
    socket.onopen = () => {
      console.log(`Agent-specific UI WebSocket connected for ${agentId}`);
      
      // Request component registrations from the backend
      socket.send(JSON.stringify({ type: 'get_component_registrations' }));
    };
    
    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('Agent-specific UI WebSocket message received:', data);
        
        // Handle component registrations
        if (data.type === 'component_registrations') {
          const components = data.data?.registrations || [];
          setComponents(components);
          
          // Set the first component as active if there are any
          if (components.length > 0) {
            setActiveComponent(components[0].id);
          }
        }
      } catch (error) {
        console.error('Error processing agent-specific UI WebSocket message:', error);
      }
    };
    
    socket.onclose = () => {
      console.log(`Agent-specific UI WebSocket disconnected for ${agentId}`);
    };
    
    socket.onerror = (error) => {
      console.error(`Agent-specific UI WebSocket error for ${agentId}:`, error);
    };
    
    // Store the socket in state
    setUiSocket(socket);
    
    // Clean up on unmount or when agentId changes
    return () => {
      socket.close();
    };
  }, [agentId]);
  
  // Fetch available UI components for the agent
  const fetchComponents = useCallback(async () => {
    try {
      setLoading(true);
      
      // Send a request to get the UI components for the agent
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";
      const response = await fetch(`${API_BASE_URL}/agents/${agentId}/ui-components`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch UI components: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      // Filter out components that don't have an implementation
      const availableComponents = data.components.filter(
        (component: UIComponent) => componentRegistry[component.id]
      );
      
      setComponents(availableComponents);
      
      // Set the first component as active if there are any
      if (availableComponents.length > 0) {
        setActiveComponent(availableComponents[0].id);
      }
      
      setError(null);
    } catch (err) {
      console.error('Error fetching UI components:', err);
      setError('Failed to load UI components. Please try again later.');
    } finally {
      setLoading(false);
    }
  }, [agentId]);
  
  // Fetch components when the component mounts or the agent changes
  useEffect(() => {
    if (agentId) {
      fetchComponents();
    }
  }, [agentId, fetchComponents]);
  
  // Render the active component
  const renderActiveComponent = () => {
    if (!activeComponent) {
      return (
        <div className="flex flex-col items-center justify-center p-8 text-center">
          <p className="text-gray-500 dark:text-gray-400">
            No UI components available for this agent.
          </p>
          <Button onClick={onSwitchToChat} className="mt-4">
            <MessageSquare className="mr-2 h-4 w-4" />
            Switch to Chat
          </Button>
        </div>
      );
    }
    
    const ComponentToRender = componentRegistry[activeComponent];
    
    if (!ComponentToRender) {
      return (
        <div className="flex flex-col items-center justify-center p-8 text-center">
          <p className="text-gray-500 dark:text-gray-400">
            Component implementation not found.
          </p>
        </div>
      );
    }
    
    // Create a function to send UI events through the agent-specific WebSocket
    const sendUIEvent = (event: any) => {
      if (!uiSocket || uiSocket.readyState !== WebSocket.OPEN) {
        console.error('Cannot send UI event: Agent-specific UI WebSocket not connected');
        return;
      }
      
      try {
        uiSocket.send(JSON.stringify({
          type: 'ui_event',
          data: {
            ...event,
            component: activeComponent,
            timestamp: Date.now()
          }
        }));
        console.log('UI event sent:', event);
      } catch (error) {
        console.error('Error sending UI event:', error);
      }
    };
    
    return (
      <ComponentToRender
        agentId={agentId}
        clientId={clientId}
        componentId={activeComponent}
        sendMessage={websocket.sendMessage}
        sendUIEvent={sendUIEvent}
      />
    );
  };
  
  // Render the component
  return (
    <Card className="w-full h-full flex flex-col">
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle>{agentName} UI</CardTitle>
          <div className="flex flex-row gap-2 mt-2">
            {components.map((component) => (
              <Badge key={component.id} variant="outline">
                {component.name}
              </Badge>
            ))}
          </div>
        </div>
        <div className="flex flex-row gap-2">
          <Button variant="outline" onClick={onSwitchToChat}>
            <MessageSquare className="mr-2 h-4 w-4" />
            Chat
          </Button>
        </div>
      </CardHeader>
      <CardContent className="flex-grow overflow-hidden">
        {loading ? (
          <div className="flex flex-col items-center justify-center h-full">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
              Loading UI components...
            </p>
          </div>
        ) : error ? (
          <div className="flex flex-col items-center justify-center h-full">
            <p className="text-red-500">{error}</p>
            <Button onClick={fetchComponents} className="mt-4">
              Retry
            </Button>
          </div>
        ) : components.length > 0 ? (
          <Tabs
            value={activeComponent || ''}
            onValueChange={setActiveComponent}
            className="h-full flex flex-col"
          >
            <TabsList className="grid" style={{ gridTemplateColumns: `repeat(${components.length}, 1fr)` }}>
              {components.map((component) => (
                <TabsTrigger key={component.id} value={component.id}>
                  {component.name}
                </TabsTrigger>
              ))}
            </TabsList>
            <div className="flex-grow overflow-auto p-4">
              {components.map((component) => (
                <TabsContent
                  key={component.id}
                  value={component.id}
                  className="h-full"
                >
                  {activeComponent === component.id && renderActiveComponent()}
                </TabsContent>
              ))}
            </div>
          </Tabs>
        ) : (
          <div className="flex flex-col items-center justify-center h-full">
            <LayoutDashboard className="h-12 w-12 text-gray-300 dark:text-gray-600" />
            <p className="mt-4 text-gray-500 dark:text-gray-400">
              No UI components available for this agent.
            </p>
            <Button onClick={onSwitchToChat} className="mt-4">
              <MessageSquare className="mr-2 h-4 w-4" />
              Switch to Chat
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default AgentUIContainer;
