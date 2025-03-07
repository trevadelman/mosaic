/**
 * Hook for using agent UI components
 * 
 * This hook provides a simple API for opening and interacting with custom UI components.
 */

import { useCallback, useMemo } from 'react';
import { useAgentUI } from '../contexts/agent-ui-context';
import { ComponentRegistration, UIEvent } from '../types/agent-ui';
import { createComponentInstance, getAgentComponentRegistrations } from '../agent-ui/component-registry';

interface UseAgentUIComponentsOptions {
  agentId: string;
}

interface UseAgentUIComponentsResult {
  /**
   * Available component registrations for the agent
   */
  availableComponents: ComponentRegistration[];
  
  /**
   * Open a component in a modal
   * @param componentId The ID of the component to open
   * @param props Optional props to pass to the component
   */
  openComponent: (componentId: string, props?: Record<string, any>) => void;
  
  /**
   * Close the currently open component
   */
  closeComponent: () => void;
  
  /**
   * Send an event to the currently open component
   * @param action The action to perform
   * @param data The data to send with the event
   */
  sendComponentEvent: (action: string, data: any) => void;
  
  /**
   * Check if a component is currently open
   * @param componentId The ID of the component to check
   */
  isComponentOpen: (componentId: string) => boolean;
  
  /**
   * Currently active component ID
   */
  activeComponentId: string | null;
}

/**
 * Hook for using agent UI components
 * 
 * @param options Options for the hook
 * @returns Functions and data for working with agent UI components
 */
export function useAgentUIComponents(
  options: UseAgentUIComponentsOptions
): UseAgentUIComponentsResult {
  const { agentId } = options;
  const { 
    registerComponent, 
    unregisterComponent, 
    openComponentModal, 
    closeComponentModal, 
    sendUIEvent,
    activeComponentId,
    isComponentOpen
  } = useAgentUI();
  
  // Get available components for this agent
  const availableComponents = useMemo(() => {
    const components = getAgentComponentRegistrations(agentId);
    console.log(`Available components for agent ${agentId}:`, components);
    return components;
  }, [agentId]);
  
  // Open a component
  const openComponent = useCallback((
    componentId: string, 
    props?: Record<string, any>
  ) => {
    // Find the component registration
    const registration = availableComponents.find(reg => reg.id === componentId);
    
    if (!registration) {
      console.error(`Component not found: ${componentId}`);
      
      // Try to import the component directly
      if (componentId === 'stock-chart') {
        console.log('Trying to import StockChart component directly');
        
        // Import the StockChart component
        import('@/components/agent-ui/financial/stock-chart').then(module => {
          console.log('StockChart component imported directly');
          
          // Create a mock registration
          const mockRegistration: ComponentRegistration = {
            id: 'stock-chart',
            name: 'Stock Chart',
            description: 'Interactive stock chart with technical indicators',
            agentId: 'financial_supervisor',
            requiredFeatures: ['charts'],
            defaultModalConfig: {
              size: 'large',
              panels: ['chart', 'controls'],
              features: ['zoom', 'pan', 'export'],
              closable: true
            }
          };
          
          // Register the component implementation
          import('@/components/agent-ui/financial').then(() => {
            console.log('Financial components module imported');
            
            // Try again after a short delay
            setTimeout(() => {
              console.log('Retrying openComponent');
              openComponent(componentId, props);
            }, 100);
          });
        });
      }
      
      return;
    }
    
    // Create a component instance
    const instance = createComponentInstance(registration, props);
    
    if (!instance) {
      console.error(`Failed to create component instance: ${componentId}`);
      return;
    }
    
    // Register and open the component
    registerComponent(instance);
    openComponentModal(instance.id, props);
  }, [availableComponents, registerComponent, openComponentModal]);
  
  // Close the component
  const closeComponent = useCallback(() => {
    closeComponentModal();
  }, [closeComponentModal]);
  
  // Send an event to the component
  const sendComponentEvent = useCallback((
    action: string, 
    data: any
  ) => {
    if (!activeComponentId) {
      console.error('No active component to send event to');
      return;
    }
    
    const event: UIEvent = {
      type: 'user_action',
      component: activeComponentId,
      action,
      data
    };
    
    sendUIEvent(event);
  }, [activeComponentId, sendUIEvent]);
  
  return {
    availableComponents,
    openComponent,
    closeComponent,
    sendComponentEvent,
    isComponentOpen,
    activeComponentId
  };
}
