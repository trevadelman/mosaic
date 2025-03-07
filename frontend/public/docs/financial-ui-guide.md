# Financial UI Components Guide

## Overview

The Mosaic Financial UI demonstrates how agents can provide rich, interactive interfaces beyond simple text-based interactions. This guide explains the current implementation and provides a roadmap for creating your own custom agent UIs.

## Current Implementation

### Stock Chart Component

The Stock Chart component demonstrates a real-time financial data visualization tool that:

1. **Fetches Real Market Data**: Connects to Yahoo Finance API via the backend to retrieve actual stock data
2. **Provides Interactive Controls**: Allows users to:
   - Search for different stock symbols
   - Change time ranges (1D, 1W, 1M, 3M, 1Y, 5Y)
   - Switch between visualization types (Line, Bar, Candle)
3. **Handles Network Issues**: Implements robust error handling with fallbacks to mock data
4. **Maintains Responsive UI**: Uses loading states and timeouts to ensure the UI remains interactive

### Architecture

The implementation follows a layered architecture:

1. **Frontend Component (React/TypeScript)**
   - Renders the UI and handles user interactions
   - Manages local state (loading, data, symbol, timeRange)
   - Communicates with backend via WebSocket events

2. **WebSocket Communication**
   - Sends data requests and user actions to the backend
   - Receives data responses from the backend
   - Handles connection issues with timeouts and fallbacks

3. **Backend Integration**
   - Processes requests from the frontend
   - Fetches data from external APIs (Yahoo Finance)
   - Formats and returns data to the frontend

4. **Mock Data Generation**
   - Provides realistic fallback data when external APIs are unavailable
   - Adjusts mock data based on selected time ranges
   - Ensures UI remains functional in all scenarios

## Creating Your Own Agent UI Components

### Step 1: Define Your Component's Purpose

Start by clearly defining what your component will do:

- What data will it display?
- What interactions will it support?
- What backend services will it require?

For example, you might create:
- A real-time news feed for specific topics
- An interactive data visualization for scientific research
- A collaborative document editor with agent assistance

### Step 2: Create the Frontend Component

1. **Create a new directory** for your component:
   ```
   mkdir -p mosaic/frontend/components/agent-ui/your-domain
   ```

2. **Create your component file**:
   ```tsx
   // mosaic/frontend/components/agent-ui/your-domain/your-component.tsx
   
   "use client"
   
   import React, { useEffect, useState } from 'react';
   import { useAgentUI } from '../../../lib/contexts/agent-ui-context';
   
   interface YourComponentProps {
     componentId: string;
     agentId: string;
     // Add your custom props here
   }
   
   export const YourComponent: React.FC<YourComponentProps> = ({
     componentId,
     agentId,
     // Destructure your props
   }) => {
     const { sendUIEvent } = useAgentUI();
     const [data, setData] = useState([]);
     const [loading, setLoading] = useState(false);
     
     // Request data from the backend
     useEffect(() => {
       // Set up event listener for responses
       const handleUIEvent = (event: CustomEvent<any>) => {
         const eventData = event.detail;
         
         // Handle responses
         if (
           eventData.type === 'data_response' && 
           eventData.component === componentId && 
           eventData.action === 'your_action'
         ) {
           // Update state with received data
           setData(eventData.data.data);
           setLoading(false);
         }
       };
       
       // Add event listener
       window.addEventListener('ui_event', handleUIEvent as EventListener);
       
       // Send data request
       try {
         sendUIEvent({
           type: 'data_request',
           component: componentId,
           action: 'get_your_data',
           data: {
             // Your request parameters
           }
         });
         
         setLoading(true);
       } catch (error) {
         console.error('Error sending UI event:', error);
         setLoading(false);
       }
       
       // Clean up
       return () => {
         window.removeEventListener('ui_event', handleUIEvent as EventListener);
       };
     }, [componentId, agentId, sendUIEvent]);
     
     // Render your component
     return (
       <div className="flex flex-col h-full">
         {/* Your UI here */}
       </div>
     );
   };
   ```

3. **Create a registration file**:
   ```tsx
   // mosaic/frontend/components/agent-ui/your-domain/register-your-component.ts
   
   import { registerComponent } from '../../../lib/agent-ui/component-registry';
   import { YourComponent } from './your-component';
   
   export function registerYourComponent() {
     registerComponent('your-component', YourComponent);
   }
   ```

4. **Update the index file**:
   ```tsx
   // mosaic/frontend/components/agent-ui/your-domain/index.ts
   
   export * from './your-component';
   export * from './register-your-component';
   ```

### Step 3: Implement Backend Handler

1. **Create or update the WebSocket handler**:
   ```python
   # mosaic/backend/app/ui_websocket_handler.py
   
   async def handle_your_data_request(websocket, event_data, agent_id, user_id):
       """Handle request for your custom data."""
       try:
           # Extract parameters from the request
           params = event_data.get('data', {})
           
           # Fetch data from external API or process locally
           result_data = await fetch_your_data(params)
           
           # Send response back to the client
           await send_ui_event(
               websocket,
               {
                   'type': 'data_response',
                   'component': event_data.get('component'),
                   'action': 'your_action',
                   'data': {
                       'data': result_data,
                       # Additional metadata
                   }
               },
               agent_id
           )
           
           logger.info(f"Sent your data for {params}")
       except Exception as e:
           logger.error(f"Error getting your data: {str(e)}")
           # Send error response
   ```

2. **Register your handler in the WebSocket router**:
   ```python
   # Add to the existing handler mapping
   DATA_REQUEST_HANDLERS = {
       # ... existing handlers
       'get_your_data': handle_your_data_request,
   }
   ```

### Step 4: Register Your Component

1. **Update the component registry**:
   ```tsx
   // mosaic/frontend/lib/agent-ui/mock-registrations.ts
   
   import { registerYourComponent } from '../../components/agent-ui/your-domain';
   
   export function registerMockComponents() {
     // Existing registrations
     registerStockChart();
     
     // Your new component
     registerYourComponent();
   }
   ```

2. **Create a demo page** (optional):
   ```tsx
   // mosaic/frontend/app/demo/your-domain-ui/page.tsx
   
   "use client"
   
   import React from 'react';
   import { YourComponent } from '../../../components/agent-ui/your-domain';
   
   export default function YourDomainDemoPage() {
     return (
       <div className="container mx-auto p-4">
         <h1 className="text-2xl font-bold mb-4">Your Domain UI Demo</h1>
         
         <div className="grid grid-cols-1 gap-4">
           <div className="border rounded-lg overflow-hidden h-[600px]">
             <YourComponent
               componentId="your-component"
               agentId="your_domain_agent"
             />
           </div>
         </div>
       </div>
     );
   }
   ```

## Example: Creating a Research Assistant UI

Let's walk through an example of creating a Research Assistant UI with multiple components:

### 1. Define Components

For a Research Assistant, you might want:
- A search interface for academic papers
- A visualization of citation networks
- A note-taking component with AI suggestions

### 2. Implement the Search Component

```tsx
// mosaic/frontend/components/agent-ui/research/paper-search.tsx

"use client"

import React, { useState } from 'react';
import { useAgentUI } from '../../../lib/contexts/agent-ui-context';

export const PaperSearch = ({ componentId, agentId }) => {
  const { sendUIEvent } = useAgentUI();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  
  const handleSearch = () => {
    setLoading(true);
    
    sendUIEvent({
      type: 'user_action',
      component: componentId,
      action: 'search_papers',
      data: { query }
    });
    
    // Set up event listener for results...
  };
  
  return (
    <div className="flex flex-col h-full">
      <div className="p-4 border-b">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="w-full p-2 border rounded"
          placeholder="Search academic papers..."
        />
        <button 
          onClick={handleSearch}
          className="mt-2 px-4 py-2 bg-primary text-white rounded"
        >
          Search
        </button>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4">
        {loading ? (
          <div className="flex justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        ) : (
          <ul className="space-y-4">
            {results.map((paper, index) => (
              <li key={index} className="border p-4 rounded">
                <h3 className="font-semibold">{paper.title}</h3>
                <p className="text-sm text-gray-600">{paper.authors.join(', ')}</p>
                <p className="mt-2">{paper.abstract}</p>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};
```

### 3. Implement Backend Handler

```python
# In ui_websocket_handler.py

async def handle_paper_search(websocket, event_data, agent_id, user_id):
    """Handle academic paper search requests."""
    try:
        query = event_data.get('data', {}).get('query', '')
        
        # Use a research API or database to search for papers
        papers = await search_academic_papers(query)
        
        await send_ui_event(
            websocket,
            {
                'type': 'data_response',
                'component': event_data.get('component'),
                'action': 'paper_search_results',
                'data': {
                    'results': papers
                }
            },
            agent_id
        )
    except Exception as e:
        logger.error(f"Error searching papers: {str(e)}")
```

### 4. Connect to an Agent

The Research Assistant agent would need to:
1. Process search queries
2. Retrieve relevant papers
3. Analyze and summarize content
4. Generate insights and suggestions

This requires:
- Integration with academic APIs (e.g., Semantic Scholar, PubMed)
- Natural language processing for understanding research content
- Knowledge graph capabilities for connecting related concepts

## Best Practices

### 1. Component Design

- **Modular Components**: Break complex UIs into smaller, reusable components
- **Responsive Design**: Ensure components work well on different screen sizes
- **Loading States**: Always provide visual feedback during data fetching
- **Error Handling**: Gracefully handle and display errors
- **Fallbacks**: Provide fallback content when data is unavailable

### 2. State Management

- **Local vs. Shared State**: Decide what state belongs in the component vs. context
- **Refs for Async Operations**: Use refs to avoid stale state in async callbacks
- **Cleanup**: Always clean up event listeners and timeouts

### 3. Communication

- **Event Types**: Use consistent event types (data_request, user_action, data_response)
- **Timeouts**: Implement timeouts for all network requests
- **Logging**: Add detailed logging for troubleshooting

### 4. Performance

- **Debouncing**: Debounce frequent user inputs (e.g., search queries)
- **Pagination**: Implement pagination for large datasets
- **Memoization**: Use React.memo and useMemo for expensive calculations

## Conclusion

The Agent UI framework provides a powerful way to create rich, interactive interfaces that go beyond simple text-based interactions. By following this guide, you can create custom UI components that leverage the capabilities of specialized agents to provide unique and valuable user experiences.

Whether you're building financial tools, research assistants, creative writing aids, or any other specialized application, the combination of intelligent agents and custom UIs opens up new possibilities for human-AI collaboration.
