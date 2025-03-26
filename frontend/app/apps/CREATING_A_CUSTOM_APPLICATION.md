# Creating a Custom Application in Mosaic

This guide walks you through creating a simple Hello World application in Mosaic. This will serve as a template for creating more complex applications.

## Prerequisites
- Node.js 18 or higher
- Python 3.11 or higher
- Working Mosaic installation

## Overview

When creating a custom application in Mosaic, you have two main approaches:

1. **Standalone Application**: Create a traditional web application that operates independently
2. **Agent-Powered Application**: Leverage Mosaic's agent system for AI-powered functionality

The choice between these approaches depends on your application's needs. Use agents when you need:
- Natural language processing
- Complex decision making
- Integration with multiple tools or data sources
- Dynamic, AI-driven responses

For simpler applications that don't require AI capabilities, prefer the standalone approach for better performance and simplicity.

## Step 1: Choose Your Approach

### Standalone Application
Best for:
- CRUD operations
- Data visualization
- Simple user interfaces
- Fixed business logic
- Real-time updates

### Agent-Powered Application
Best for:
- Natural language interactions
- Complex data analysis
- Dynamic content generation
- Multi-step workflows
- Integration with external services

Example: Our Database Visualizer is a standalone application because it focuses on visualization and data presentation, while our Financial Analysis app uses an agent because it needs complex market analysis and natural language processing.

## Step 2: Create the Frontend Route

Create a new file at `frontend/app/apps/hello-world/page.tsx`:

```typescript
"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

export default function HelloWorldApp() {
  const [name, setName] = useState("")
  const [greeting, setGreeting] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/apps/hello-world/greet`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ name })
      })
      
      if (!response.ok) {
        throw new Error(`Error: ${response.status} ${response.statusText}`)
      }
      
      const data = await response.json()
      setGreeting(data.greeting)
    } catch (error) {
      console.error("Error fetching greeting:", error)
      setError(error instanceof Error ? error.message : "An error occurred")
    } finally {
      setLoading(false)
    }
  }
  
  return (
    <div className="container py-10">
      <Card>
        <CardHeader>
          <CardTitle>Hello World Application</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Input
                type="text"
                placeholder="Enter your name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                disabled={loading}
              />
            </div>
            <Button type="submit" disabled={loading}>
              {loading ? "Getting Greeting..." : "Get Greeting"}
            </Button>
          </form>
          
          {error && (
            <div className="mt-4 p-4 bg-destructive/10 rounded-md text-destructive">
              <p>{error}</p>
            </div>
          )}
          
          {greeting && !error && (
            <div className="mt-4 p-4 bg-primary/10 rounded-md">
              <p className="text-lg">{greeting}</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
```

## Step 2: Add Backend Support

Create or update `backend/app/apps_api.py`:

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/apps", tags=["applications"])

class GreetingRequest(BaseModel):
    name: str

@router.post("/hello-world/greet")
async def get_greeting(request: GreetingRequest):
    """Get a greeting for the given name."""
    try:
        return {
            "greeting": f"Hello, {request.name}! Welcome to Mosaic."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

Add the router to `backend/app/main.py`:

```python
from backend.app.apps_api import router as apps_api_router
app.include_router(apps_api_router)
```

## Step 3: Add to Applications Index

Update `frontend/app/apps/page.tsx`:

```typescript
"use client"

import Link from "next/link"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

const applications = [
  {
    id: "hello-world",
    name: "Hello World",
    description: "A simple example application",
    icon: "👋",
    color: "bg-blue-500"
  }
]

export default function ApplicationsPage() {
  return (
    <div className="container py-10">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold">Applications</h1>
          <p className="text-muted-foreground mt-1">
            Custom applications built on the Mosaic platform
          </p>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {applications.map(app => (
          <Link href={`/apps/${app.id}`} key={app.id} className="block">
            <Card className="h-full hover:shadow-md transition-shadow">
              <CardHeader className={`${app.color} text-white rounded-t-lg`}>
                <div className="text-3xl mb-2">{app.icon}</div>
                <CardTitle>{app.name}</CardTitle>
              </CardHeader>
              <CardContent className="pt-4">
                <CardDescription className="text-base text-foreground/80">
                  {app.description}
                </CardDescription>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  )
}
```

## Step 4: Update Navigation

Update the sidebar navigation component to include the applications icon:

```typescript
import { Layout } from "lucide-react"

// Replace the community navigation item with applications
export const sidebarNavItems = [
  // ... other items ...
  {
    title: "Applications",
    href: "/apps",
    icon: <Layout className="h-5 w-5" />,
  },
  // ... other items ...
]
```

## Testing

1. Start the backend server:
```bash
cd mosaic/backend
uvicorn app.main:app --reload
```

2. Start the frontend development server:
```bash
cd mosaic/frontend
npm run dev
```

3. Visit http://localhost:3000/apps to see the applications index
4. Click on the Hello World application
5. Enter your name and click "Get Greeting"

Note: The backend API runs on port 8000 while the frontend runs on port 3000. Make sure to use the correct URL (http://localhost:8000) when making API calls from the frontend.

### Environment Configuration

The application uses environment variables to handle different deployment environments:

1. **Frontend Environment Variables**:
   - `NEXT_PUBLIC_API_URL`: Backend API URL (e.g., "http://localhost:8000/api")
   - Set in:
     - Development: `.env.local` file
     - Docker: `docker-compose.yml` under frontend service

2. **Backend Environment Variables**:
   - `CORS_ORIGINS`: Allowed frontend origins (e.g., "http://localhost:3000")
   - Set in:
     - Development: `.env` file or system environment (defaults to "http://localhost:3000")
     - Docker: `docker-compose.yml` under backend service

3. **Default Ports**:
   - Frontend: http://localhost:3000
   - Backend: http://localhost:8000

This configuration ensures the application works consistently across different environments without hardcoding URLs.

## Using Agents in Your Application

If you decide to use an agent, you can integrate it using the `useChat` and `useAgents` hooks:

```typescript
import { useChat } from "@/lib/hooks/use-chat"
import { useAgents } from "@/lib/hooks/use-agents"

export default function YourApp() {
  // Find the agent you want to use
  const { agents } = useAgents()
  const yourAgent = agents.find(a => a.id === "your_agent_id")
  
  // Set up chat functionality with the agent
  const { messages, sendMessage, isProcessing } = useChat(yourAgent?.id)
  
  // Use the agent's capabilities
  const handleAction = () => {
    sendMessage("Your instruction to the agent")
  }
  
  return (
    // Your UI components
  )
}
```

Key considerations when using agents:
1. Only use agents when their capabilities truly add value to your application
2. Handle loading and error states appropriately
3. Consider the response format and how to present it effectively
4. Use proper typing for agent responses
5. Consider rate limits and processing time

## Common Issues and Best Practices

1. **API Endpoint Not Found**
   - Check that the API router is properly included in main.py
   - Verify the API route matches your frontend fetch call
   - Ensure environment variables are properly set (NEXT_PUBLIC_API_URL)

2. **Component Not Rendering**
   - Verify the route structure is correct
   - Check for JavaScript errors in the console
   - Implement proper loading states
   - Handle and display errors appropriately

3. **Styling Issues**
   - Make sure all UI components are imported correctly
   - Check that tailwind classes are applied properly
   - Use appropriate UI feedback for loading and error states

4. **Error Handling**
   - Always implement proper error handling
   - Display user-friendly error messages
   - Use loading states to prevent multiple submissions
   - Disable form inputs during submission

## Next Steps

1. Add more features to your application
2. Implement more complex UI components
3. Add proper error handling
4. Add loading states
5. Implement proper testing

## Tips for Success

### General Tips

1. Follow the Mosaic coding standards
2. Use TypeScript for type safety
3. Implement proper error handling
4. Add loading states for better UX
5. Test thoroughly before deploying

### Agent Integration Tips
1. Check agent availability before using
2. Handle agent not found scenarios gracefully
3. Consider using a loading UI during agent processing
4. Format agent responses appropriately for your UI
5. Cache agent responses when possible
6. Use error boundaries for agent-related errors

## Complex Application Structure

For complex applications, organize your code into a structured layout. Here's an example using our Database Visualizer application that shows database structure and data in an interactive way:

### Project Structure

```
backend/
  app/
    apps/
      db_visualizer/           # Backend application code
        __init__.py
        models.py             # Pydantic models for API
        service.py           # Database interaction logic
        api.py              # FastAPI endpoints
frontend/
  app/
    apps/
      db-visualizer/          # Frontend application code
        components/          # React components
          ForceGraph.tsx    # D3 force-directed graph
          TableDetails.tsx  # Table structure view
          TableDataView.tsx # Table data grid
        hooks/             # React hooks
          useGraphData.ts    # Graph data fetching
          useTableDetails.ts # Table info fetching
          useTableData.ts    # Table data fetching
        page.tsx           # Main page component
```

### Key Components

1. **Backend Service** ([source](mosaic/backend/app/apps/db_visualizer/service.py)):
   - Uses SQLAlchemy to inspect database structure
   - Extracts table relationships and column information
   - Provides paginated table data access
   ```python
   class DatabaseVisualizerService:
       def get_database_structure(self) -> DatabaseStructure:
           """Extract database structure including tables and relationships."""
           
       def get_table_details(self, table_name: str) -> Dict:
           """Get detailed information about a specific table."""
           
       def get_table_data(self, table_name: str, page: int = 1) -> Dict:
           """Get paginated data from a specific table."""
   ```

2. **Frontend Components**:
   - Interactive Graph ([source](mosaic/frontend/app/apps/db-visualizer/components/ForceGraph.tsx)):
     ```typescript
     export function ForceGraph({ nodes, links, onNodeClick }) {
       // D3 force-directed graph implementation
       // Shows tables and their relationships
     }
     ```
   - Table Information ([source](mosaic/frontend/app/apps/db-visualizer/components/TableDetails.tsx)):
     ```typescript
     export function TableDetailsPanel({ details }) {
       // Displays table structure:
       // - Columns and their types
       // - Primary/Foreign keys
       // - Indexes
     }
     ```

3. **Data Hooks** ([source](mosaic/frontend/app/apps/db-visualizer/hooks)):
   ```typescript
   // Custom hooks for data fetching and state management
   export function useGraphData() {
     // Fetches and manages database structure
   }
   
   export function useTableData() {
     // Fetches and manages table content
   }
   ```

### Features Demonstrated
1. **Complex Data Visualization**: Using D3.js for interactive graphs
2. **Real-time Data Access**: Direct database structure inspection
3. **Modular Architecture**: Separated concerns between data, UI, and business logic
4. **Type Safety**: Strong typing with TypeScript and Pydantic
5. **Error Handling**: Comprehensive error states and loading indicators
6. **Responsive Design**: Adapts to different screen sizes

This example shows how to:
- Structure larger applications
- Handle complex data relationships
- Build interactive visualizations
- Manage state and data flow
- Implement proper error handling
- Create reusable components

For the complete implementation, see the [db_visualizer directory](mosaic/backend/app/apps/db_visualizer) in the backend and [db-visualizer directory](mosaic/frontend/app/apps/db-visualizer) in the frontend.
