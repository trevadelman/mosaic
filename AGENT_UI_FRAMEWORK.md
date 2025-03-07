# MOSAIC Agent UI Framework

## Overview

The MOSAIC Agent UI Framework provides a flexible system for creating rich, interactive user interfaces for agents beyond the traditional chat interface. This framework allows agents to offer specialized visualizations, data processing tools, and interactive components tailored to their specific capabilities.

## Architecture

The Agent UI Framework follows a modular architecture with clear separation between backend and frontend components:

### Backend Components

1. **UI Component Base Classes**
   - Located in `mosaic/backend/ui/base.py`
   - Provides abstract base classes for UI components
   - Handles component registration and discovery

2. **UI Component Implementations**
   - Located in `mosaic/backend/ui/components/`
   - Specialized implementations for different types of UI components
   - Examples include `stock_chart.py`, etc.

3. **UI WebSocket Handler**
   - Located in `mosaic/backend/app/ui_websocket_handler.py`
   - Manages WebSocket connections for real-time communication
   - Routes events between UI components and frontend

4. **UI Component Discovery**
   - Located in `mosaic/backend/app/ui_component_discovery.py`
   - Discovers and registers UI components for agents
   - Maps components to agents based on capabilities

### Frontend Components

1. **Component Registry**
   - Located in `mosaic/frontend/lib/agent-ui/component-registry.ts`
   - Registers React component implementations for UI components
   - Maps component IDs to their React implementations

2. **Agent UI Container**
   - Located in `mosaic/frontend/components/agent-ui/agent-ui-container.tsx`
   - Main container for agent-specific UI components
   - Handles loading, rendering, and communication with UI components

3. **UI Component Implementations**
   - Located in `mosaic/frontend/components/agent-ui/`
   - React implementations of UI components
   - Organized by agent type (e.g., `financial/`, `research/`, etc.)

4. **WebSocket Context**
   - Located in `mosaic/frontend/lib/contexts/websocket-context.tsx`
   - Provides WebSocket connection for real-time communication
   - Handles message routing and event dispatching

## Communication Flow

1. **Component Registration**
   - Backend UI components register with the UI component registry
   - Frontend React components register with the component registry
   - Components are mapped to agents based on capabilities

2. **WebSocket Connection**
   - When a user opens an agent UI, a WebSocket connection is established
   - The connection is specific to the agent and client
   - Events are routed through this connection

3. **Event Flow**
   - Frontend components send events to the backend through the WebSocket
   - Backend components process events and send responses
   - Events can include data requests, user actions, and UI updates

4. **Data Flow**
   - Backend components fetch data directly from agent tools
   - UI components should use agent tools exclusively for data retrieval
   - Data is processed and formatted for the frontend
   - Frontend components render the data in the UI

## Using Agent Tools for Data Retrieval

The recommended approach for data retrieval in UI components is to use agent tools directly:

1. **Access the Agent**
   - Get the initialized agent using `get_initialized_agents()`
   - Retrieve the specific agent by ID

2. **Find the Appropriate Tool**
   - Iterate through the agent's tools to find the one you need
   - Tools are identified by their name (e.g., `get_stock_history_tool`)

3. **Invoke the Tool**
   - Call the tool's `invoke()` method with the appropriate parameters
   - Process the response as needed

Example:
```python
async def _get_data_from_agent(self, params):
    try:
        # Get the agent
        from mosaic.backend.app.agent_runner import get_initialized_agents
        initialized_agents = get_initialized_agents()
        agent = initialized_agents.get("my_agent")
        
        if not agent:
            raise ValueError(f"Agent 'my_agent' not found")
        
        # Find the tool
        tool = None
        for t in agent.tools:
            if t.name == "my_data_tool":
                tool = t
                break
        
        if not tool:
            raise ValueError(f"Tool 'my_data_tool' not found in agent 'my_agent'")
        
        # Invoke the tool
        response = tool.invoke({
            "param1": params.get("param1"),
            "param2": params.get("param2")
        })
        
        # Process the response
        # ...
        
        return processed_data
    
    except Exception as e:
        logger.error(f"Error getting data from agent: {str(e)}")
        return {"error": str(e)}
```

## Creating a New UI Component

### Backend Component

1. **Create a new Python file** in `mosaic/backend/ui/components/`
2. **Inherit from an appropriate base class**:
   - `VisualizationComponent` for data visualizations
   - `InteractiveComponent` for interactive components
   - `DataInputComponent` for data input components
3. **Implement required methods**:
   - `__init__`: Initialize the component with ID, name, and description
   - `handle_*`: Event handlers for different actions
4. **Register the component** with the UI component registry

Example:
```python
from mosaic.backend.ui.components.visualization import VisualizationComponent
from mosaic.backend.ui.base import ui_component_registry

class MyVisualizationComponent(VisualizationComponent):
    def __init__(self):
        super().__init__(
            component_id="my-visualization",
            name="My Visualization",
            description="A custom visualization component"
        )
        
        # Register event handlers
        self.register_handler("get_data", self.handle_get_data)
        
    async def handle_get_data(self, websocket, event_data, agent_id, client_id):
        # Get data from agent tool
        data = await self._get_data_from_agent(event_data.get("data", {}))
        
        # Send response
        await self._send_data_response(websocket, event_data, data, agent_id, client_id)
    
    async def _get_data_from_agent(self, params):
        # Implementation of agent tool data retrieval
        # ...

# Create and register the component
my_visualization_component = MyVisualizationComponent()
ui_component_registry.register(my_visualization_component)
```

### Frontend Component

1. **Create a new TypeScript/React file** in `mosaic/frontend/components/agent-ui/`
2. **Implement the React component** with appropriate props and state
3. **Register the component** in an index.ts file

Example:
```tsx
// mosaic/frontend/components/agent-ui/my-agent/my-visualization.tsx
import React, { useState, useEffect } from 'react';
import { useAgentUI } from '../../../lib/contexts/agent-ui-context';

interface MyVisualizationProps {
  componentId: string;
  agentId: string;
}

export const MyVisualization: React.FC<MyVisualizationProps> = ({
  componentId,
  agentId,
}) => {
  const { sendUIEvent } = useAgentUI();
  const [data, setData] = useState<any[]>([]);
  
  useEffect(() => {
    // Set up event listener
    const handleUIEvent = (event: CustomEvent<any>) => {
      // Handle events
    };
    
    window.addEventListener('ui_event', handleUIEvent as EventListener);
    
    // Request data
    sendUIEvent({
      type: 'data_request',
      component: componentId,
      action: 'get_data',
      data: {}
    });
    
    return () => {
      window.removeEventListener('ui_event', handleUIEvent as EventListener);
    };
  }, [componentId, agentId, sendUIEvent]);
  
  return (
    <div>
      {/* Render visualization */}
    </div>
  );
};
```

```typescript
// mosaic/frontend/components/agent-ui/my-agent/index.ts
import { registerComponentImplementation } from '../../../lib/agent-ui/component-registry';
import { MyVisualization } from './my-visualization';

// Register the component
console.log('Registering MyVisualization component implementation');
registerComponentImplementation('my-visualization', MyVisualization);

// Export components
export { MyVisualization };

// Export component IDs
export const MY_AGENT_COMPONENTS = {
  MY_VISUALIZATION: 'my-visualization'
};

// Log that the module has been loaded
console.log('My agent components module loaded');
```

## Registering Components with Agents

To associate a UI component with an agent:

1. **In the agent's module**, import the UI component registry
2. **Register the component with the agent** using the agent's ID

Example:
```python
from mosaic.backend.ui.base import ui_component_registry
from mosaic.backend.agents.base import agent_registry

# Register the component with the agent
if "my_agent" in agent_registry.list_agents():
    agent_registry.register_ui_component("my_agent", "my-visualization")
```

## Best Practices

1. **Component Naming**
   - Use kebab-case for component IDs (e.g., `stock-chart`)
   - Use PascalCase for React component names (e.g., `StockChart`)
   - Use snake_case for Python class names (e.g., `StockChartComponent`)

2. **Event Handling**
   - Use descriptive event names (e.g., `get_stock_data`, `change_symbol`)
   - Include all necessary data in event payloads
   - Handle errors gracefully and provide meaningful error messages

3. **Data Flow**
   - Always use agent tools for data retrieval
   - Keep data transformations in the backend when possible
   - Send only the necessary data to the frontend
   - Use appropriate data structures for different types of visualizations

4. **Component Organization**
   - Group related components in directories
   - Use index.ts files to export and register components
   - Keep component implementations focused and single-purpose

## Troubleshooting

### Common Issues

1. **Component Not Appearing**
   - Check that the component is registered in both backend and frontend
   - Verify that the component ID matches in both places
   - Check the browser console for errors

2. **WebSocket Connection Issues**
   - Verify that the WebSocket server is running
   - Check for CORS issues if running in development
   - Ensure the WebSocket URL is correct

3. **Data Not Loading**
   - Check that the agent is properly initialized
   - Verify that the agent has the necessary tools
   - Check for errors in the backend logs

### Debugging Tips

1. **Backend Debugging**
   - Use logging to track event flow and data processing
   - Check the terminal output for errors
   - Use the Python debugger if necessary

2. **Frontend Debugging**
   - Use browser developer tools to inspect network requests
   - Add console.log statements to track component lifecycle
   - Use React DevTools to inspect component state

## Example: Financial Analysis UI

The Financial Analysis UI provides a good example of the Agent UI Framework in action:

1. **Backend Components**
   - `stock_chart.py`: Provides stock chart visualization using the financial_analysis agent's tools

2. **Frontend Components**
   - `stock-chart.tsx`: Renders stock charts using Recharts

3. **Data Flow**
   - The stock chart component uses the financial_analysis agent's `get_stock_history_tool` to fetch stock data
   - The tool returns formatted stock history data
   - The component parses the response and sends it to the frontend
   - The frontend renders the data as an interactive chart

This example demonstrates how to create specialized UI components that use agent tools directly for data retrieval, providing a clean and efficient architecture for agent UIs.
