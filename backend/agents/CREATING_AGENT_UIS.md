# Creating Custom UIs for Your Agents in MOSAIC

This guide will walk you through the process of creating custom user interfaces (UIs) for your agents in MOSAIC. We'll keep it simple and beginner-friendly, focusing on practical steps rather than complex technical details.

## What You'll Learn

- How the Agent UI Framework works
- How to create a backend UI component
- How to create a frontend UI component
- How to connect your UI to an agent
- How to test your custom UI

## Prerequisites

Before you start, make sure you have:

- MOSAIC up and running (see the [Quickstart Guide](../../QUICKSTART.md))
- A working agent (see [Creating Agents](CREATING_AGENTS.md))
- Basic knowledge of Python and React/TypeScript
- Your favorite code editor open

## Understanding the Agent UI Framework

In MOSAIC, agents can have specialized UIs beyond the standard chat interface. These UIs can:

- Visualize data (charts, graphs, tables)
- Provide interactive controls (buttons, sliders, forms)
- Display specialized content (maps, diagrams, documents)

The Agent UI Framework consists of two main parts:

1. **Backend UI Components**: Python classes that handle data and events
2. **Frontend UI Components**: React components that render the UI

These components communicate through WebSockets, allowing real-time updates and interactions.

## Creating a Simple Chart UI

Let's create a simple chart UI for an agent that can display bar charts. We'll build both the backend and frontend components.

### Step 1: Create the Backend UI Component

First, let's create the backend component that will handle data and events.

#### Create a New File

Create a new Python file in the `mosaic/backend/ui/components` directory. Let's call it `simple_chart.py`.

#### Import Required Modules

Add these imports at the top of your file:

```python
import logging
from typing import Dict, List, Any
from datetime import datetime

# Import the base visualization component
try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.ui.components.visualization import VisualizationComponent
    from mosaic.backend.ui.base import ui_component_registry
    from mosaic.backend.agents.base import agent_registry
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.ui.components.visualization import VisualizationComponent
    from backend.ui.base import ui_component_registry
    from backend.agents.base import agent_registry

# Configure logging
logger = logging.getLogger("mosaic.ui_components.simple_chart")
```

#### Create the Component Class

Now, let's create the UI component class:

```python
class SimpleChartComponent(VisualizationComponent):
    """
    A simple chart component that can display bar charts.
    """
    
    def __init__(self):
        """Initialize the simple chart component."""
        super().__init__(
            component_id="simple-chart",
            name="Simple Chart",
            description="A simple chart component for displaying bar charts",
            chart_types=["bar"]
        )
        
        # Register handlers
        self.register_handler("get_chart_data", self.handle_get_chart_data)
        
        logger.info(f"Initialized {self.name} component")
    
    async def handle_get_chart_data(self, websocket: Any, event_data: Dict[str, Any], agent_id: str, client_id: str) -> None:
        """
        Handle a request to get chart data.
        
        Args:
            websocket: The WebSocket connection
            event_data: The event data
            agent_id: The agent ID
            client_id: The client ID
        """
        try:
            # Get parameters from the event data
            params = event_data.get("data", {})
            
            # Get data from the agent
            chart_data = await self._get_data_from_agent(params, agent_id)
            
            # Send the data back to the client
            await self._send_response(websocket, event_data, {
                "success": True,
                "chart_data": chart_data
            })
        
        except Exception as e:
            logger.error(f"Error handling get_chart_data request: {str(e)}")
            
            # Send error response
            await self._send_response(websocket, event_data, {
                "success": False,
                "error": f"Error getting chart data: {str(e)}"
            })
    
    async def _get_data_from_agent(self, params: Dict[str, Any], agent_id: str) -> Dict[str, Any]:
        """
        Get data from the agent.
        
        Args:
            params: The parameters for the data request
            agent_id: The agent ID
            
        Returns:
            The chart data
        """
        try:
            # Get the agent
            try:
                # Try importing with the full package path (for local development)
                from mosaic.backend.app.agent_runner import get_initialized_agents
            except ImportError:
                # Fall back to relative import (for Docker environment)
                from backend.app.agent_runner import get_initialized_agents
            
            initialized_agents = get_initialized_agents()
            agent = initialized_agents.get(agent_id)
            
            if not agent:
                raise ValueError(f"Agent '{agent_id}' not found")
            
            # Find a tool that can generate chart data
            # This example assumes the agent has a tool named "generate_chart_data_tool"
            tool = None
            for t in agent.tools:
                if t.name == "generate_chart_data_tool":
                    tool = t
                    break
            
            if not tool:
                # If the agent doesn't have the specific tool, return sample data
                logger.warning(f"Tool 'generate_chart_data_tool' not found in agent '{agent_id}', using sample data")
                return self._get_sample_data()
            
            # Invoke the tool
            result = tool.invoke(params)
            
            # Process the result
            # This assumes the tool returns data in a format that can be used by the chart
            # You might need to transform the data depending on your specific tool
            
            return result
        
        except Exception as e:
            logger.error(f"Error getting data from agent: {str(e)}")
            return self._get_sample_data()
    
    def _get_sample_data(self) -> Dict[str, Any]:
        """
        Get sample data for testing.
        
        Returns:
            Sample chart data
        """
        return {
            "labels": ["January", "February", "March", "April", "May"],
            "datasets": [
                {
                    "label": "Sample Data",
                    "data": [65, 59, 80, 81, 56]
                }
            ]
        }
    
    async def _send_response(self, websocket: Any, event_data: Dict[str, Any], response_data: Dict[str, Any]) -> None:
        """
        Send a response back to the client.
        
        Args:
            websocket: The WebSocket connection
            event_data: The original event data
            response_data: The response data
        """
        # Create the response event
        response = {
            "type": "ui_event",
            "data": {
                "component": self.component_id,
                "action": event_data.get("action", "unknown"),
                "requestId": event_data.get("requestId", "unknown"),
                **response_data
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Send the response
        await websocket.send_json(response)
```

#### Register the Component

At the end of the file, add code to create and register the component:

```python
# Create and register the component
simple_chart_component = SimpleChartComponent()
ui_component_registry.register(simple_chart_component)

# You can register this component with any agent that has chart data
# For example, if you have a "data_analysis" agent:
if "data_analysis" in agent_registry.list_agents():
    agent_registry.register_ui_component("data_analysis", simple_chart_component.component_id)
    logger.info(f"Registered {simple_chart_component.name} with data_analysis agent")
```

### Step 2: Create the Frontend UI Component

Now, let's create the frontend React component that will render the chart.

#### Create the Directory Structure

First, create the necessary directories:

```
mosaic/frontend/components/agent-ui/data-analysis/
```

#### Create the Component File

Create a new TypeScript file in this directory called `simple-chart.tsx`:

```tsx
import React, { useState, useEffect } from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { useAgentUI } from '../../../lib/contexts/agent-ui-context';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

// Define props interface
interface SimpleChartProps {
  componentId: string;
  agentId: string;
}

// Define chart data interface
interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor?: string;
    borderColor?: string;
    borderWidth?: number;
  }[];
}

export const SimpleChart: React.FC<SimpleChartProps> = ({
  componentId,
  agentId,
}) => {
  // State for chart data
  const [chartData, setChartData] = useState<ChartData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  // Get the sendUIEvent function from the AgentUI context
  const { sendUIEvent } = useAgentUI();
  
  // Chart options
  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Simple Bar Chart',
      },
    },
  };
  
  // Effect to fetch data when the component mounts
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      
      try {
        // Request chart data from the backend
        sendUIEvent({
          type: 'data_request',
          component: componentId,
          action: 'get_chart_data',
          data: {}
        });
      } catch (err) {
        setError('Failed to send data request');
        setLoading(false);
      }
    };
    
    // Set up event listener for responses
    const handleUIEvent = (event: CustomEvent<any>) => {
      const data = event.detail;
      
      // Check if this event is for our component
      if (data.component === componentId && data.action === 'get_chart_data') {
        if (data.success) {
          setChartData(data.chart_data);
        } else {
          setError(data.error || 'Failed to get chart data');
        }
        setLoading(false);
      }
    };
    
    // Add event listener
    window.addEventListener('ui_event', handleUIEvent as EventListener);
    
    // Fetch data
    fetchData();
    
    // Clean up
    return () => {
      window.removeEventListener('ui_event', handleUIEvent as EventListener);
    };
  }, [componentId, agentId, sendUIEvent]);
  
  // Render loading state
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg font-medium">Loading chart data...</div>
      </div>
    );
  }
  
  // Render error state
  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg font-medium text-red-500">Error: {error}</div>
      </div>
    );
  }
  
  // Render chart
  if (!chartData) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg font-medium">No data available</div>
      </div>
    );
  }
  
  // Add default colors if not provided
  const dataWithColors = {
    ...chartData,
    datasets: chartData.datasets.map((dataset, index) => ({
      ...dataset,
      backgroundColor: dataset.backgroundColor || `rgba(${75 + index * 40}, ${192 - index * 20}, ${192 - index * 30}, 0.6)`,
      borderColor: dataset.borderColor || `rgba(${75 + index * 40}, ${192 - index * 20}, ${192 - index * 30}, 1)`,
      borderWidth: dataset.borderWidth || 1,
    })),
  };
  
  return (
    <div className="p-4 bg-white rounded-lg shadow">
      <Bar options={options} data={dataWithColors} />
    </div>
  );
};
```

#### Create the Index File

Create an `index.ts` file in the same directory to register the component:

```typescript
import { registerComponentImplementation } from '../../../lib/agent-ui/component-registry';
import { SimpleChart } from './simple-chart';

// Register the component
registerComponentImplementation('simple-chart', SimpleChart);

// Export the component
export { SimpleChart };

// Export component ID
export const DATA_ANALYSIS_COMPONENTS = {
  SIMPLE_CHART: 'simple-chart'
};

// Log that the module has been loaded
console.log('Data analysis components module loaded');
```

### Step 3: Add a Tool to Your Agent

For your UI to display meaningful data, your agent needs a tool that can generate chart data. Let's add a simple tool to an existing agent.

#### Create a Chart Data Tool

Open your agent file (e.g., `data_analysis.py`) and add a tool for generating chart data:

```python
@tool
def generate_chart_data_tool(categories: List[str] = None, values: List[float] = None) -> Dict[str, Any]:
    """
    Generate data for a bar chart.
    
    Args:
        categories: Optional list of categories (x-axis labels)
        values: Optional list of values (y-axis values)
        
    Returns:
        Chart data in the format expected by Chart.js
    """
    # If categories and values are provided, use them
    if categories and values:
        if len(categories) != len(values):
            return {
                "error": "Categories and values must have the same length"
            }
        
        return {
            "labels": categories,
            "datasets": [
                {
                    "label": "Data",
                    "data": values
                }
            ]
        }
    
    # Otherwise, generate some sample data
    sample_categories = ["Category A", "Category B", "Category C", "Category D", "Category E"]
    sample_values = [42, 58, 35, 70, 48]
    
    return {
        "labels": sample_categories,
        "datasets": [
            {
                "label": "Sample Data",
                "data": sample_values
            }
        ]
    }
```

Add this tool to your agent's tools list:

```python
def register_data_analysis_agent(model):
    """Register the data analysis agent."""
    tools = [
        # ... existing tools ...
        generate_chart_data_tool
    ]
    
    agent = DataAnalysisAgent("data_analysis", model, tools)
    return agent
```

### Step 4: Connect Everything Together

Now that we have both the backend and frontend components, and a tool in our agent, let's make sure everything is connected.

#### Update the Backend Component Registration

Make sure your backend component is registered with the correct agent:

```python
# Register the component with the data_analysis agent
if "data_analysis" in agent_registry.list_agents():
    agent_registry.register_ui_component("data_analysis", simple_chart_component.component_id)
    logger.info(f"Registered {simple_chart_component.name} with data_analysis agent")
```

#### Update the Frontend Component Registration

Make sure your frontend component is registered in the component registry. In `mosaic/frontend/lib/agent-ui/component-registry.ts`, import your component:

```typescript
// Import component modules
import '../../../components/agent-ui/data-analysis';
```

### Step 5: Test Your UI

Now it's time to test your custom UI!

1. Restart the MOSAIC backend:
   ```
   python -m uvicorn mosaic.backend.app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. Restart the frontend:
   ```
   cd mosaic/frontend
   npm run dev
   ```

3. Open your browser and go to http://localhost:3000
4. Find your agent in the sidebar (e.g., "data_analysis")
5. Look for the UI button next to your agent
6. Click the UI button to open your custom UI
7. You should see your bar chart with the sample data!

## Creating More Advanced UIs

Once you're comfortable with the basics, you can create more advanced UIs:

### Interactive Controls

Add interactive controls to your UI to allow users to customize the data:

```tsx
// Add a dropdown to select different datasets
const [selectedDataset, setSelectedDataset] = useState<string>('default');

// Add to your component JSX
<div className="mb-4">
  <label className="mr-2">Select dataset:</label>
  <select 
    value={selectedDataset} 
    onChange={(e) => {
      setSelectedDataset(e.target.value);
      // Request new data with the selected dataset
      sendUIEvent({
        type: 'data_request',
        component: componentId,
        action: 'get_chart_data',
        data: { dataset: e.target.value }
      });
    }}
    className="p-2 border rounded"
  >
    <option value="default">Default</option>
    <option value="monthly">Monthly</option>
    <option value="quarterly">Quarterly</option>
  </select>
</div>
```

### Multiple Chart Types

Support multiple chart types in your UI:

```tsx
// Add state for chart type
const [chartType, setChartType] = useState<'bar' | 'line' | 'pie'>('bar');

// Add imports for other chart types
import { Bar, Line, Pie } from 'react-chartjs-2';

// Add to your component JSX
<div className="mb-4">
  <label className="mr-2">Chart type:</label>
  <select 
    value={chartType} 
    onChange={(e) => setChartType(e.target.value as 'bar' | 'line' | 'pie')}
    className="p-2 border rounded"
  >
    <option value="bar">Bar</option>
    <option value="line">Line</option>
    <option value="pie">Pie</option>
  </select>
</div>

// Render the selected chart type
{chartType === 'bar' && <Bar options={options} data={dataWithColors} />}
{chartType === 'line' && <Line options={options} data={dataWithColors} />}
{chartType === 'pie' && <Pie options={options} data={dataWithColors} />}
```

### Real-Time Updates

Add real-time updates to your UI:

```tsx
// Add a refresh interval
useEffect(() => {
  // Set up a refresh interval
  const intervalId = setInterval(() => {
    // Request updated data
    sendUIEvent({
      type: 'data_request',
      component: componentId,
      action: 'get_chart_data',
      data: { refresh: true }
    });
  }, 30000); // Refresh every 30 seconds
  
  // Clean up
  return () => clearInterval(intervalId);
}, [componentId, sendUIEvent]);
```

## Best Practices

1. **Keep Components Focused**: Each UI component should have a single responsibility
2. **Handle Errors Gracefully**: Always include error handling in your components
3. **Provide Loading States**: Show loading indicators while data is being fetched
4. **Use Responsive Design**: Make sure your UI works well on different screen sizes
5. **Document Your Components**: Add good comments and documentation to your code

## Common Pitfalls

1. **Forgetting to Register Components**: Make sure both backend and frontend components are registered
2. **Mismatched Component IDs**: The component ID must match between backend and frontend
3. **Not Handling WebSocket Errors**: Always handle WebSocket connection errors
4. **Overcomplicating the UI**: Start simple and add complexity gradually

## Troubleshooting Common Issues

When creating custom UIs, you might encounter some issues. Here are some common problems and their solutions:

### 1. Component Not Showing Up in the UI

If your component is not showing up in the UI, check the following:

- Make sure the component is registered in both the backend and frontend
- Check that the component ID matches between backend and frontend
- Verify that the agent has the UI component registered

### 2. WebSocket Connection Issues

WebSocket connection issues are common when working with agent UIs. Here's how to fix them:

- Make sure the WebSocket URL is correct (check the `NEXT_PUBLIC_WS_URL` environment variable)
- Add proper error handling for WebSocket connections
- Consider implementing a fallback mechanism for when WebSockets fail

### 3. React Hooks and Next.js Server Components

When using React hooks in Next.js, you might encounter errors about hooks being used in server components. To fix this:

- Add the `"use client"` directive at the top of any component file that uses React hooks:
  ```tsx
  "use client"
  
  import React, { useState, useEffect } from 'react';
  ```
- This is required for components that use hooks like `useState`, `useEffect`, etc.

### 4. Component Registration in Frontend

To properly register your frontend component, you need to:

1. Create an `index.ts` file in your component directory:
   ```typescript
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

2. Import this module in the root layout file (`mosaic/frontend/app/layout.tsx`):
   ```typescript
   // Import component registries
   import '@/components/agent-ui/your-agent';
   ```

3. Add your component to the component registry in `agent-ui-container.tsx`:
   ```typescript
   // Import UI component implementations
   import { YourComponent } from './your-agent/your-component';
   
   // Component registry mapping component IDs to their React implementations
   const componentRegistry: Record<string, React.ComponentType<any>> = {
     // ... existing components ...
     'your-component-id': YourComponent,
   };
   ```

### 5. Handling Backend Tool Execution

When executing tools from your UI component, you might encounter issues with how tools are accessed. Here's a robust approach:

```python
async def _get_agent_runner(self):
    """
    Get the agent runner.
    
    Returns:
        The agent runner
    """
    try:
        # Try importing with the full package path (for local development)
        from mosaic.backend.app.agent_runner import get_initialized_agents
    except ImportError:
        # Fall back to relative import (for Docker environment)
        from backend.app.agent_runner import get_initialized_agents
    
    # Get the initialized agents
    agents = get_initialized_agents()
    
    # Return the specific agent
    return agents.get("your_agent_id")

async def handle_tool_execution(self, websocket: Any, event: Dict[str, Any], agent_id: str, client_id: str) -> None:
    try:
        # Get parameters from the event data
        params = event.get("data", {})
        
        # Get the agent
        agent = await self._get_agent_runner()
        
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")
        
        # Find the tool
        tool = None
        for t in agent.tools:
            if t.name == "your_tool_name":
                tool = t
                break
        
        if not tool:
            raise ValueError("Tool not found")
        
        # Call the tool directly
        result = tool.func(**params)
        
        # Send the data back to the client
        await self._send_response(websocket, event, {
            "success": True,
            "data": result
        })
    
    except Exception as e:
        logger.error(f"Error handling tool execution: {str(e)}")
        
        # Send error response
        await self._send_response(websocket, event, {
            "success": False,
            "error": f"Error executing tool: {str(e)}"
        })
```

### 6. Fallback to Client-Side Data Generation

If you're having persistent issues with WebSocket connections or backend tool execution, consider implementing a client-side fallback:

```tsx
// Generate random data on the client side
const generateRandomData = () => {
  // Generate random data based on parameters
  // ...
  return { /* your data structure */ };
};

// Try to fetch from backend, fall back to client-side generation
useEffect(() => {
  const fetchData = async () => {
    setLoading(true);
    
    try {
      // Try to request data from backend
      sendUIEvent({
        type: 'data_request',
        component: componentId,
        action: 'get_data',
        data: params
      });
      
      // Set a timeout for fallback
      const timeoutId = setTimeout(() => {
        if (loading) {
          console.log('Backend request timed out, using client-side data generation');
          setChartData(generateRandomData());
          setLoading(false);
        }
      }, 5000); // 5 second timeout
      
      return () => clearTimeout(timeoutId);
    } catch (err) {
      console.error('Error requesting data from backend:', err);
      setChartData(generateRandomData());
      setLoading(false);
    }
  };
  
  fetchData();
}, [params]);
```

## Advanced Debugging Techniques

When developing agent UIs, you may encounter complex issues that require more advanced debugging techniques. Here are some strategies that can help:

### 1. Comprehensive WebSocket Event Logging

Add detailed logging for all WebSocket events to help diagnose communication issues:

```tsx
// Set up event listener for responses
const handleUIEvent = (event: CustomEvent<any>) => {
  const data = event.detail;
  
  // Log all UI events for debugging
  console.log('UI event received:', data);
  
  // Check if this event is for our component
  if (data.component === componentId && data.action === 'get_data') {
    console.log('Received data response for our component:', data);
    
    if (data.success) {
      console.log('Data received successfully:', data.data);
      setData(data.data);
    } else {
      console.error('Error getting data:', data.error);
      setError(data.error || 'Failed to get data');
      // Fallback to client-side data generation
      setData(generateRandomData());
    }
    
    setLoading(false);
  }
};

// Add event listener
window.addEventListener('ui_event', handleUIEvent as EventListener);
```

### 2. Data Format Validation

Always validate the format of data received from the backend before using it:

```tsx
// Render the appropriate visualization based on the data
const renderVisualization = () => {
  // Log the data for debugging
  console.log('Rendering visualization with data:', data);
  
  try {
    // Validate data format
    if (!data || typeof data !== 'object') {
      throw new Error('Invalid data format: data is not an object');
    }
    
    if (data.type === 'bar') {
      // Validate bar chart data
      if (!Array.isArray(data.categories) || !Array.isArray(data.values) || !Array.isArray(data.colors)) {
        throw new Error('Invalid bar chart data: missing required arrays');
      }
      
      if (data.categories.length !== data.values.length || data.categories.length !== data.colors.length) {
        throw new Error('Invalid bar chart data: arrays have different lengths');
      }
      
      // Render bar chart
      return (
        <BarChart 
          width={chartWidth} 
          height={chartHeight} 
          data={data.categories.map((cat, i) => ({
            name: cat,
            value: data.values[i],
            color: data.colors[i]
          }))} 
        >
          {/* Chart components */}
        </BarChart>
      );
    } else {
      throw new Error(`Unknown data type: ${data.type}`);
    }
  } catch (error) {
    console.error('Error rendering visualization:', error);
    return (
      <div className="error-message">
        Error rendering visualization. Check console for details.
      </div>
    );
  }
};
```

### 3. Debugging WebSocket Connection Issues

If you're experiencing WebSocket connection issues, add these debugging steps:

1. Check if the WebSocket connection is established:

```tsx
useEffect(() => {
  // Log WebSocket connection status
  console.log('WebSocket connection status:', websocket ? 'Connected' : 'Disconnected');
  
  if (!websocket) {
    console.error('WebSocket connection not established');
    setError('WebSocket connection not established');
    return;
  }
  
  // Rest of your code...
}, [websocket]);
```

2. Add a ping/pong mechanism to test WebSocket connectivity:

```tsx
// Add a ping function to test WebSocket connectivity
const pingWebSocket = () => {
  console.log('Sending ping to WebSocket');
  sendUIEvent({
    type: 'ping',
    component: componentId,
    action: 'ping',
    data: { timestamp: Date.now() }
  });
};

// Add a button to test WebSocket connectivity
<button onClick={pingWebSocket}>Test WebSocket Connection</button>
```

3. In your backend component, add a handler for ping events:

```python
async def handle_ping(self, websocket: Any, event: Dict[str, Any], agent_id: str, client_id: str) -> None:
    """Handle ping events for testing WebSocket connectivity."""
    logger.info(f"Received ping from client {client_id}")
    
    # Send pong response
    await self._send_response(websocket, event, {
        "success": True,
        "message": "pong",
        "timestamp": datetime.now().isoformat()
    })
```

### 4. Handling Data Format Mismatches

When the backend and frontend expect different data formats, implement a data transformation layer:

```tsx
// Transform backend data to frontend format
const transformData = (backendData: any): ChartData => {
  console.log('Transforming backend data:', backendData);
  
  try {
    // Handle different backend data formats
    if (backendData.type === 'bar') {
      return {
        type: 'bar',
        categories: backendData.categories || [],
        values: backendData.values || [],
        colors: backendData.colors || []
      };
    } else if (Array.isArray(backendData)) {
      // Handle array format (legacy or alternative format)
      return {
        type: 'bar',
        categories: backendData.map(item => item.name || ''),
        values: backendData.map(item => item.value || 0),
        colors: backendData.map(item => item.color || '#000000')
      };
    } else {
      throw new Error(`Unknown data format: ${JSON.stringify(backendData)}`);
    }
  } catch (error) {
    console.error('Error transforming data:', error);
    // Return default data
    return generateDefaultData();
  }
};

// Use the transformed data
useEffect(() => {
  if (data.success) {
    const transformedData = transformData(data.chart_data);
    setChartData(transformedData);
  }
}, [data]);
```

### 5. Implementing Robust Error Boundaries

Use React Error Boundaries to prevent the entire UI from crashing when a component fails:

```tsx
// ErrorBoundary.tsx
import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    console.error('Error caught by ErrorBoundary:', error, errorInfo);
  }

  render(): ReactNode {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }
      
      return (
        <div className="error-boundary">
          <h2>Something went wrong.</h2>
          <details>
            <summary>Error details</summary>
            <pre>{this.state.error?.toString()}</pre>
          </details>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
```

Then wrap your component with the ErrorBoundary:

```tsx
// In your parent component
import ErrorBoundary from './ErrorBoundary';

// ...

return (
  <ErrorBoundary>
    <YourComponent />
  </ErrorBoundary>
);
```

### 6. Debugging Backend Tool Execution

If your agent tools aren't executing correctly, add detailed logging in the backend:

```python
async def handle_get_data(self, websocket: Any, event: Dict[str, Any], agent_id: str, client_id: str) -> None:
    """Handle a request to get data."""
    try:
        # Log the request
        logger.info(f"Handling get_data request from client {client_id} for agent {agent_id}")
        logger.info(f"Event data: {event}")
        
        # Get parameters from the event data
        params = event.get("data", {})
        logger.info(f"Request parameters: {params}")
        
        # Get the agent
        agent = await self._get_agent_runner()
        
        if not agent:
            logger.error(f"Agent {agent_id} not found")
            raise ValueError(f"Agent {agent_id} not found")
        
        logger.info(f"Agent found: {agent.name}")
        logger.info(f"Available tools: {[t.name for t in agent.tools]}")
        
        # Find the tool
        tool = None
        for t in agent.tools:
            if t.name == "get_data_tool":
                tool = t
                break
        
        if not tool:
            logger.error("get_data_tool not found in agent tools")
            raise ValueError("get_data_tool not found")
        
        logger.info(f"Tool found: {tool.name}")
        
        # Call the tool directly
        logger.info(f"Calling tool with parameters: {params}")
        result = tool.func(**params)
        logger.info(f"Tool result: {result}")
        
        # Send the data back to the client
        await self._send_response(websocket, event, {
            "success": True,
            "data": result
        })
        logger.info("Response sent successfully")
    
    except Exception as e:
        logger.error(f"Error handling get_data request: {str(e)}", exc_info=True)
        
        # Send error response
        await self._send_response(websocket, event, {
            "success": False,
            "error": f"Error getting data: {str(e)}"
        })
```

By implementing these advanced debugging techniques, you'll be better equipped to diagnose and fix issues in your agent UI components.

## Next Steps

- Study the existing UI components in the `mosaic/backend/ui/components` directory
- Explore the frontend components in `mosaic/frontend/components/agent-ui`
- Try creating more complex UIs with multiple components
- Experiment with different chart libraries and visualization techniques

Happy UI building!
