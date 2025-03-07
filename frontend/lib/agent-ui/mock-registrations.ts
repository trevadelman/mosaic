/**
 * Mock Component Registrations
 * 
 * This file provides mock component registrations for testing purposes.
 * In a production environment, these registrations would come from the backend.
 */

import { ComponentRegistration } from '../types/agent-ui';
import { setComponentRegistrations } from './component-registry';

/**
 * Register mock component registrations
 */
export function registerMockComponentRegistrations(): void {
  const mockRegistrations: ComponentRegistration[] = [
    {
      id: 'stock-chart',
      name: 'Stock Chart',
      description: 'Interactive stock chart with technical indicators',
      agentId: 'financial-analysis',
      requiredFeatures: ['charts'],
      defaultModalConfig: {
        size: 'large',
        panels: ['chart', 'controls'],
        features: ['zoom', 'pan', 'export'],
        closable: true
      }
    }
  ];
  
  // Set the mock registrations
  setComponentRegistrations(mockRegistrations);
  
  console.log('Registered mock component registrations:', mockRegistrations);
}
