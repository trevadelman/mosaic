"use client"

import { registerComponentImplementation } from '../../../lib/agent-ui/component-registry';
import { ChartVisualizer } from './chart-visualizer';

// Register the component
registerComponentImplementation('chart-visualizer', ChartVisualizer);

// Export the component
export { ChartVisualizer };

// Export component ID
export const CHART_DATA_GENERATOR_COMPONENTS = {
  CHART_VISUALIZER: 'chart-visualizer'
};

// Log that the module has been loaded
console.log('Chart data generator components module loaded');
