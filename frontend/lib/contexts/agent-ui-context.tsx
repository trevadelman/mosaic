"use client"

/**
 * Agent UI Context
 * 
 * This context provides a registry for custom UI components that can be
 * used by agents to provide rich, interactive interfaces.
 */

import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import { AgentUIComponent, ComponentRegistration, UIEvent } from '../types/agent-ui';
import { useWebSocket, ConnectionState } from './websocket-context';
import { WebSocketEvent } from '../types';

// Agent ID for UI events
const UI_AGENT_ID = 'agent-ui';

interface AgentUIContextType {
  /** Register a component with the registry */
  registerComponent: (component: AgentUIComponent) => void;
  /** Unregister a component from the registry */
  unregisterComponent: (id: string) => void;
  /** Get a component from the registry by ID */
  getComponent: (id: string) => AgentUIComponent | undefined;
  /** Get all registered components */
  getAllComponents: () => AgentUIComponent[];
  /** Get all component registrations */
  getComponentRegistrations: () => ComponentRegistration[];
  /** Open a component in a modal */
  openComponentModal: (id: string, props?: Record<string, any>) => void;
  /** Close the currently open modal */
  closeComponentModal: () => void;
  /** Currently active component ID */
  activeComponentId: string | null;
  /** Send a UI event to the backend */
  sendUIEvent: (event: UIEvent) => void;
  /** Check if a component is currently open */
  isComponentOpen: (id: string) => boolean;
}

const AgentUIContext = createContext<AgentUIContextType | undefined>(undefined);

export const AgentUIProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [components, setComponents] = useState<Record<string, AgentUIComponent>>({});
  const [registrations, setRegistrations] = useState<ComponentRegistration[]>([]);
  const [activeComponentId, setActiveComponentId] = useState<string | null>(null);
  const websocket = useWebSocket();

  // Check if WebSocket is connected
  const isConnected = useCallback(() => {
    return websocket.connectionState === ConnectionState.CONNECTED;
  }, [websocket.connectionState]);

  // UI WebSocket connection
  const [uiSocket, setUiSocket] = useState<WebSocket | null>(null);
  
  // Connect to the UI WebSocket endpoint
  useEffect(() => {
    // Only create a new connection if one doesn't exist
    if (uiSocket !== null) {
      return;
    }
    
    // Create a WebSocket connection to the UI endpoint
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws';
    const agentId = UI_AGENT_ID;
    console.log(`Connecting to UI WebSocket at ${wsUrl}/ui/${agentId}`);
    
    // Use the agent ID for the UI WebSocket
    const socket = new WebSocket(`${wsUrl}/ui/${agentId}`);
    
    // Store the socket in state
    setUiSocket(socket);
    
    socket.onopen = () => {
      console.log('UI WebSocket connected');
      
      // Request component registrations from the backend
      socket.send(JSON.stringify({ type: 'get_component_registrations' }));
      console.log('Sent request for component registrations');
    };
    
    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('UI WebSocket message received:', data);
        
        // Handle component registrations
        if (data.type === 'component_registrations') {
          setRegistrations(data.data?.registrations || []);
          console.log('Component registrations updated:', data.data?.registrations);
        }
        
        // Handle UI events
        if (data.type === 'ui_event') {
          const uiEvent = data.data;
          console.log('UI event received:', uiEvent);
          
          // Process UI event based on type
          if (uiEvent.type === 'data_response') {
            console.log('Dispatching data_response event:', uiEvent);
            
            // Dispatch a custom event for UI components to listen to
            try {
              const customEvent = new CustomEvent('ui_event', { detail: uiEvent });
              window.dispatchEvent(customEvent);
              console.log('Custom event dispatched successfully');
            } catch (error) {
              console.error('Error dispatching custom event:', error);
            }
          } else if (uiEvent.type === 'ui_update') {
            // Update component props
            setComponents(prev => {
              const component = prev[uiEvent.component];
              if (!component) return prev;
              
              return {
                ...prev,
                [uiEvent.component]: {
                  ...component,
                  props: {
                    ...component.props,
                    ...uiEvent.data
                  }
                }
              };
            });
          }
        }
      } catch (error) {
        console.error('Error processing UI WebSocket message:', error);
      }
    };
    
    socket.onclose = () => {
      console.log('UI WebSocket disconnected');
      // Reset the socket state when closed
      setUiSocket(null);
    };
    
    socket.onerror = (error) => {
      console.error('UI WebSocket error:', error);
    };
    
    // Clean up on unmount
    return () => {
      socket.close();
      setUiSocket(null);
    };
  }, [uiSocket]);

  // Handle incoming messages from the WebSocket
  useEffect(() => {
    const handleWebSocketEvent = (event: WebSocketEvent) => {
      if (event.type !== 'message' || !event.message) return;
      
      try {
        // Parse custom data from message content if it's JSON
        try {
          const customData = JSON.parse(event.message.content);
          
          // Handle component registrations
          if (customData.type === 'component_registrations') {
            setRegistrations(customData.registrations || []);
          }
          
          // Handle UI events
          if (customData.type === 'ui_event') {
            const uiEvent = customData.data as UIEvent;
            // Process UI event based on type
            if (uiEvent.type === 'ui_update') {
              // Update component props
              setComponents(prev => {
                const component = prev[uiEvent.component];
                if (!component) return prev;
                
                return {
                  ...prev,
                  [uiEvent.component]: {
                    ...component,
                    props: {
                      ...component.props,
                      ...uiEvent.data
                    }
                  }
                };
              });
            }
          }
        } catch (jsonError) {
          // Not JSON data, ignore
        }
      } catch (error) {
        console.error('Error processing WebSocket message:', error);
      }
    };

    // Subscribe to WebSocket events
    const unsubscribe = websocket.addEventListener(handleWebSocketEvent);
    
    return () => {
      unsubscribe();
    };
  }, [websocket]);

  // Register a component with the registry
  const registerComponent = (component: AgentUIComponent) => {
    setComponents(prev => ({
      ...prev,
      [component.id]: component
    }));
  };

  // Unregister a component from the registry
  const unregisterComponent = (id: string) => {
    setComponents(prev => {
      const newComponents = { ...prev };
      delete newComponents[id];
      return newComponents;
    });
    
    // Close the modal if the unregistered component is active
    if (activeComponentId === id) {
      setActiveComponentId(null);
    }
  };

  // Get a component from the registry by ID
  const getComponent = (id: string) => components[id];

  // Get all registered components
  const getAllComponents = () => Object.values(components);

  // Get all component registrations
  const getComponentRegistrations = () => registrations;

  // Open a component in a modal
  const openComponentModal = (id: string, props?: Record<string, any>) => {
    const component = components[id];
    if (!component) {
      console.error(`Component with ID "${id}" not found in registry`);
      return;
    }
    
    // Update component props if provided
    if (props) {
      setComponents(prev => ({
        ...prev,
        [id]: {
          ...prev[id],
          props: {
            ...prev[id].props,
            ...props
          }
        }
      }));
    }
    
    setActiveComponentId(id);
    
    // Notify the backend that a component was opened
    sendUIEvent({
      type: 'user_action',
      component: id,
      action: 'open',
      data: props || {}
    });
  };

  // Close the currently open modal
  const closeComponentModal = () => {
    if (activeComponentId) {
      // Notify the backend that a component was closed
      sendUIEvent({
        type: 'user_action',
        component: activeComponentId,
        action: 'close',
        data: {}
      });
    }
    
    setActiveComponentId(null);
  };

  // Send a UI event to the backend
  const sendUIEvent = (event: UIEvent) => {
    if (!uiSocket || uiSocket.readyState !== WebSocket.OPEN) {
      console.error('Cannot send UI event: UI WebSocket not connected');
      return;
    }
    
    // Add timestamp and event ID if not provided
    const completeEvent: UIEvent = {
      ...event,
      eventId: event.eventId || `ui-event-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      timestamp: event.timestamp || Date.now()
    };
    
    // Send the event through the UI WebSocket
    try {
      uiSocket.send(JSON.stringify({
        type: 'ui_event',
        data: completeEvent
      }));
      console.log('UI event sent:', completeEvent);
    } catch (error) {
      console.error('Error sending UI event:', error);
    }
  };

  // Check if a component is currently open
  const isComponentOpen = (id: string) => activeComponentId === id;

  const value: AgentUIContextType = {
    registerComponent,
    unregisterComponent,
    getComponent,
    getAllComponents,
    getComponentRegistrations,
    openComponentModal,
    closeComponentModal,
    activeComponentId,
    sendUIEvent,
    isComponentOpen
  };

  return (
    <AgentUIContext.Provider value={value}>
      {children}
    </AgentUIContext.Provider>
  );
};

export const useAgentUI = () => {
  const context = useContext(AgentUIContext);
  if (context === undefined) {
    throw new Error('useAgentUI must be used within an AgentUIProvider');
  }
  return context;
};
