/**
 * Agent UI Component Registry
 * 
 * This utility provides functions for registering and retrieving custom UI components.
 */

import { AgentUIComponent, ComponentRegistration } from '../types/agent-ui';

// In-memory storage for component registrations
let componentRegistrations: ComponentRegistration[] = [
  // Default mock registration for the stock chart component
  {
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
  }
];

// In-memory storage for component implementations
const componentImplementations: Record<string, React.ComponentType<any>> = {};

/**
 * Register a component implementation
 * 
 * @param id The unique identifier for the component
 * @param component The React component implementation
 */
export function registerComponentImplementation(
  id: string,
  component: React.ComponentType<any>
): void {
  componentImplementations[id] = component;
  console.log(`Registered component implementation: ${id}`);
}

/**
 * Get a component implementation by ID
 * 
 * @param id The unique identifier for the component
 * @returns The React component implementation or undefined if not found
 */
export function getComponentImplementation(
  id: string
): React.ComponentType<any> | undefined {
  return componentImplementations[id];
}

/**
 * Set the component registrations
 * 
 * @param registrations The component registrations from the backend
 */
export function setComponentRegistrations(
  registrations: ComponentRegistration[]
): void {
  componentRegistrations = registrations;
  console.log(`Updated component registrations: ${registrations.length} components`);
}

/**
 * Get all component registrations
 * 
 * @returns The component registrations
 */
export function getComponentRegistrations(): ComponentRegistration[] {
  return componentRegistrations;
}

/**
 * Create a component instance from a registration and props
 * 
 * @param registration The component registration
 * @param props The props to pass to the component
 * @returns The component instance or null if the implementation is not found
 */
export function createComponentInstance(
  registration: ComponentRegistration,
  props: Record<string, any> = {}
): AgentUIComponent | null {
  console.log(`Creating component instance for ${registration.id}`);
  console.log(`Component implementations:`, Object.keys(componentImplementations));
  
  const implementation = getComponentImplementation(registration.id);
  
  if (!implementation) {
    console.error(`Component implementation not found: ${registration.id}`);
    
    // Try to dynamically import the component
    if (registration.id === 'stock-chart') {
      console.log('Trying to dynamically register StockChart component');
      
      // Force register the component
      console.log('Forcing registration of StockChart component');
      
      // Import the financial components module
      import('@/components/agent-ui/financial')
        .then(() => {
          console.log('Financial components module imported successfully');
        })
        .catch(error => {
          console.error('Error importing financial components module:', error);
        });
    }
    
    return null;
  }
  
  console.log(`Component implementation found for ${registration.id}`);
  
  return {
    id: registration.id,
    component: implementation,
    props: {
      ...props,
      agentId: registration.agentId,
      componentId: registration.id
    },
    modalConfig: registration.defaultModalConfig
  };
}

/**
 * Get all available component registrations for an agent
 * 
 * @param agentId The agent ID to filter by
 * @returns The component registrations for the agent
 */
export function getAgentComponentRegistrations(
  agentId: string
): ComponentRegistration[] {
  console.log(`Getting component registrations for agent ${agentId}`);
  console.log(`All component registrations:`, componentRegistrations);
  
  const filteredRegistrations = componentRegistrations.filter(reg => reg.agentId === agentId);
  console.log(`Filtered component registrations for agent ${agentId}:`, filteredRegistrations);
  
  return filteredRegistrations;
}

/**
 * Check if a component is available for an agent
 * 
 * @param agentId The agent ID to check
 * @param componentId The component ID to check
 * @returns True if the component is available for the agent
 */
export function isComponentAvailableForAgent(
  agentId: string,
  componentId: string
): boolean {
  return componentRegistrations.some(
    reg => reg.agentId === agentId && reg.id === componentId
  );
}
