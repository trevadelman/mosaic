/**
 * Financial Components Registry
 * 
 * This file registers all financial components with the component registry.
 */

import { registerComponentImplementation } from '../../../lib/agent-ui/component-registry';
import { StockChart } from './stock-chart';
import { FinancialUIDemoButton } from './demo-button';

// Register the StockChart component
console.log('Registering StockChart component implementation');
registerComponentImplementation('stock-chart', StockChart);

// Export all components
export { StockChart, FinancialUIDemoButton };

// Export component IDs for easy reference
export const FINANCIAL_COMPONENTS = {
  STOCK_CHART: 'stock-chart'
};

// Log that the financial components module has been loaded
console.log('Financial components module loaded');
