/**
 * Register Stock Chart Component
 * 
 * This file registers the stock chart component with the component registry.
 * It's imported directly by the demo page to ensure the component is registered.
 */

import { registerComponentImplementation } from '../../../lib/agent-ui/component-registry';
import { setComponentRegistrations } from '../../../lib/agent-ui/component-registry';
import { ComponentRegistration } from '../../../lib/types/agent-ui';
import { StockChart } from './stock-chart';

// Register the component implementation
registerComponentImplementation('stock-chart', StockChart);

// Register the component registration
const stockChartRegistration: ComponentRegistration = {
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
};

// Set the component registrations
export function registerStockChart() {
  setComponentRegistrations([stockChartRegistration]);
  console.log('Registered stock chart component registration');
}
