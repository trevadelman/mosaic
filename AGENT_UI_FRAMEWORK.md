# MOSAIC Agent UI Framework

This document explains how the hasUI framework works in MOSAIC, allowing agents to have custom UI components that provide rich, interactive interfaces beyond simple text chat.

## Overview

The MOSAIC Agent UI Framework connects backend agents with frontend UI components through a WebSocket-based communication system. This enables agents to have custom interfaces that can visualize data, accept user input, and provide interactive experiences.

## Architecture

The framework consists of several key components:

### Backend Components

1. **UI Component Registry**: Manages UI component registrations
   - Located in `backend/ui/base.py`
   - Provides methods to register and retrieve UI components

2. **Agent Registry**: Manages agent registrations and their associated UI components
   - Located in `backend/agents/base.py`
   - Provides methods to register agents and associate UI components with them

3. **WebSocket Handlers**: Handle communication between frontend and backend
   - Located in `backend/app/ui_websocket_handler.py`
   - Manages WebSocket connections and routes messages to the appropriate handlers

4. **UI Connection Manager**: Manages WebSocket connections for UI components
   - Located in `backend/app/ui_connection_manager.py`
   - Tracks connections by agent, component, and client

### Frontend Components

1. **Component Registry**: Maps component IDs to React components
   - Located in `frontend/lib/agent-ui/component-registry.ts`
   - Provides methods to register and retrieve UI component implementations

2. **WebSocket Context**: Manages WebSocket connections
   - Located in `frontend/lib/contexts/websocket-context.tsx`
   - Provides methods to send and receive messages

3. **Agent UI Context**: Manages UI component state and communication
   - Located in `frontend/lib/contexts/agent-ui-context.tsx`
   - Provides methods to register components and send UI events

4. **Agent UI Container**: Renders the appropriate UI component
   - Located in `frontend/components/agent-ui/agent-ui-container.tsx`
   - Manages the lifecycle of UI components

### Communication Flow

1. Frontend connects to backend via WebSockets
2. Backend sends component registrations to frontend
3. Frontend renders the appropriate component
4. Components communicate with backend via WebSocket events
5. Backend processes events and sends responses back to frontend

## Implementation Guide

### 1. Create a Backend UI Component

```python
# In mosaic/backend/ui/components/your_component.py
from mosaic.backend.ui.base import UIComponent, ui_component_registry
from mosaic.backend.agents.base import agent_registry

class YourComponent(UIComponent):
    def __init__(self):
        super().__init__(
            component_id="your-component-id",  # Must match frontend component ID
            name="Your Component Name",
            description="Description of your component",
            required_features=["feature1", "feature2"],
            default_modal_config={
                "title": "Your Component",
                "width": "80%",
                "height": "80%",
                "resizable": True
            }
        )
        
        # Register handlers for actions
        self.register_handler("action1", self.handle_action1)
        
    async def handle_action1(self, websocket, event, agent_id, client_id):
        # Handle the action
        # Get the agent
        agent = await self._get_agent_runner()
        
        # Process the request
        result = await agent.run_tool(...)
        
        # Send response
        await self._send_response(websocket, event, {
            "success": True,
            "data": result
        })
    
    async def _get_agent_runner(self):
        """
        Get the agent instance.
        """
        try:
            from mosaic.backend.app.agent_runner import get_initialized_agents
        except ImportError:
            from backend.app.agent_runner import get_initialized_agents
        
        # Get the initialized agents
        agents = get_initialized_agents()
        
        # Return the specific agent
        return agents.get("your_agent_id")

# Create and register the component
your_component = YourComponent()
ui_component_registry.register(your_component)

# Register the component with the agent if it exists
if "your_agent_id" in agent_registry.list_agents():
    agent_registry.register_ui_component("your_agent_id", your_component.component_id)
    logger.info(f"Registered {your_component.name} component with your_agent_id agent")
```

### 2. Create a Frontend UI Component

```tsx
// In mosaic/frontend/components/agent-ui/your-agent/your-component.tsx
"use client"

import React, { useState, useEffect } from 'react';

interface YourComponentProps {
  componentId: string;
  agentId: string;
  sendUIEvent: (event: any) => void;
}

export const YourComponent: React.FC<YourComponentProps> = ({
  componentId,
  agentId,
  sendUIEvent,
}) => {
  // State
  const [data, setData] = useState<any>(null);
  
  // Effect to set up event listener for responses
  useEffect(() => {
    const handleUIEvent = (event: CustomEvent<any>) => {
      const data = event.detail;
      
      // Check if this event is for our component
      if (data.component === componentId && data.action === 'action1') {
        if (data.success) {
          setData(data.data);
        }
      }
    };
    
    // Add event listener
    window.addEventListener('ui_event', handleUIEvent as EventListener);
    
    // Request initial data
    sendUIEvent({
      type: 'data_request',
      component: componentId,
      action: 'action1',
      data: {}
    });
    
    // Clean up
    return () => {
      window.removeEventListener('ui_event', handleUIEvent as EventListener);
    };
  }, [componentId, sendUIEvent]);
  
  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold mb-4">Your Component</h2>
      {/* Render your component UI */}
    </div>
  );
};
```

### 3. Register the Frontend Component

```ts
// In mosaic/frontend/components/agent-ui/your-agent/index.ts
"use client"

import { registerComponentImplementation } from '../../../lib/agent-ui/component-registry';
import { YourComponent } from './your-component';

// Register the component
registerComponentImplementation('your-component-id', YourComponent);

// Export the component
export { YourComponent };

// Export component ID
export const YOUR_AGENT_COMPONENTS = {
  YOUR_COMPONENT: 'your-component-id'
};

// Log that the module has been loaded
console.log('Your agent components module loaded');
```

### 4. Import the Component in the Root Layout

```tsx
// In mosaic/frontend/app/layout.tsx
// Import component registries
import '@/components/agent-ui/financial'
import '@/components/agent-ui/chart-data-generator'
import '@/components/agent-ui/your-agent'
```

### 5. Register the UI Component in the Agent Registration Function

```python
# In mosaic/backend/agents/regular/your_agent.py
def register_your_agent(model):
    agent = YourAgent("your_agent", model)
    agent_registry.register(agent)
    
    # Explicitly register the UI component with the agent
    agent_registry.register_ui_component("your_agent", "your-component-id")
    
    return agent
```

## Key Points for Successful Implementation

1. **Component ID Matching**: Ensure the component ID in the backend matches the one in the frontend.

2. **Explicit Registration**: Always explicitly register the UI component with the agent in the agent registration function.

3. **Error Handling**: Implement proper error handling in both backend and frontend components.

4. **WebSocket Connection**: Be aware of WebSocket connection timing issues and implement appropriate retry mechanisms.

5. **Agent Runner Access**: Use the correct method to access the agent runner:
   ```python
   async def _get_agent_runner(self):
       try:
           from mosaic.backend.app.agent_runner import get_initialized_agents
       except ImportError:
           from backend.app.agent_runner import get_initialized_agents
       
       agents = get_initialized_agents()
       return agents.get("your_agent_id")
   ```

6. **Event Handling**: Properly handle events in the frontend component by checking the component ID and action.

7. **Client Directive**: Always include the "use client" directive at the top of frontend component files.

## Debugging Tips

1. **Check Backend Logs**: Look for registration messages and WebSocket connection issues.

2. **Check Frontend Console**: Look for WebSocket connection issues and event handling errors.

3. **Verify Component Registration**: Ensure the component is registered with the agent in the agent registration function.

4. **Check WebSocket Connection**: Ensure the WebSocket connection is established before sending events.

5. **Inspect Network Traffic**: Use browser developer tools to inspect WebSocket traffic.

## Example: Chart Data Generator

The chart data generator agent and its UI component provide a good example of a working implementation:

### Backend Component

```python
# Register UI component for this agent
agent_registry.register_ui_component("chart_data_generator", "chart-visualizer")
```

### Frontend Component

```tsx
// Register the component
registerComponentImplementation('chart-visualizer', ChartVisualizer);
```

This ensures that the chart data generator agent has a UI component that can be displayed in the frontend.

## Troubleshooting

### Common Issues

1. **UI Button Not Showing**: Ensure the agent has a UI component registered and the hasUI property is set.

2. **WebSocket Connection Issues**: Check for WebSocket connection errors in the browser console.

3. **Component Not Rendering**: Ensure the component is registered in the frontend and imported in the root layout.

4. **Agent Not Found**: Ensure the agent is registered and initialized before accessing it.

5. **Event Handling Issues**: Ensure the event listener is properly set up and the event data is correctly formatted.

### Solutions

1. **Explicitly Register UI Component**: Always explicitly register the UI component with the agent in the agent registration function.

2. **Use Correct Agent Runner Access**: Use the correct method to access the agent runner.

3. **Implement Retry Mechanisms**: Implement retry mechanisms for WebSocket connections and event handling.

4. **Check Component ID Matching**: Ensure the component ID in the backend matches the one in the frontend.

5. **Debug with Logging**: Add logging statements to track the flow of events and identify issues.

## Conclusion

The MOSAIC Agent UI Framework provides a powerful way to create rich, interactive interfaces for agents. By following the implementation guide and best practices, you can create custom UI components that enhance the user experience and provide advanced functionality beyond simple text chat.
