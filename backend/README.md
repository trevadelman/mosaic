# MOSAIC Backend

This directory contains the backend components of the MOSAIC system, including the FastAPI application, agent system, and database models.

## System Architecture

The MOSAIC backend consists of several key components:

1. **FastAPI Application**: Provides REST API endpoints and WebSocket connections for the frontend
2. **Agent System**: Implements the agent framework, regular agents, and supervisor agents
   - **Dynamic Agent Discovery**: Automatically discovers and registers both regular agents and supervisors
   - **API Endpoint Generation**: Dynamically generates API endpoints for agents
3. **UI Component System**: Implements the backend components of the Agent UI framework
   - **UI Component Registry**: Manages UI components and their association with agents
   - **WebSocket Handler**: Handles real-time communication with UI components
   - **Component Discovery**: Automatically discovers and registers UI components
4. **Database Models**: Defines the data models for storing queries, responses, and agent configurations

### Agent System Directory Structure

The agent system is organized into the following directories:

- **agents/base.py**: Contains the base agent framework and agent registry
- **agents/regular/**: Contains regular (specialized) agents
- **agents/supervisors/**: Contains supervisor agents that orchestrate regular agents
- **agents/sandbox/**: Contains sandbox environment for testing new agents
- **agents/templates/**: Contains templates for creating new agents

## How to Test the System

### Prerequisites

1. Python 3.11 or higher
2. OpenAI API key (set in .env file)

### Setting Up the Environment

1. Create a virtual environment:
   ```bash
   cd /Users/trevoradelman/Documents/devStuff/langChainDev/swarms
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install the package in development mode:
   ```bash
   cd /Users/trevoradelman/Documents/devStuff/langChainDev/swarms
   pip install -e mosaic
   ```

   This installs the mosaic package in development mode, which means any changes you make to the code will be immediately reflected without needing to reinstall the package.

3. Create a .env file in the mosaic directory:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

### Testing the Calculator Agent

The simplest way to test the system is to run the calculator agent test script:

```bash
cd /Users/trevoradelman/Documents/devStuff/langChainDev/swarms
python -m mosaic.backend.tests.test_calculator
```

This will start an interactive session where you can test the calculator agent's capabilities by entering mathematical expressions.

### Running the FastAPI Backend

To run the full backend server:

```bash
cd /Users/trevoradelman/Documents/devStuff/langChainDev/swarms
python -m uvicorn mosaic.backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

This will start the FastAPI server on http://localhost:8000. You can access the API documentation at http://localhost:8000/docs.

## Integration with Frontend

The frontend communicates with the backend through:

1. **REST API Endpoints**:
   - `/api/agents`: Get a list of all available agents
   - `/api/agents/{agent_id}`: Get information about a specific agent
   - `/api/agents/{agent_id}/messages`: Send a message to an agent or get all messages for a specific agent
   - `/api/chat/{agent_id}/conversations`: Get conversation history for a specific agent
   - `/api/chat/{agent_id}/conversations/{conversation_id}/activate`: Activate a specific conversation

2. **WebSocket Connection**:
   - `/ws/chat/{agent_id}`: Real-time communication for agent responses and logs

## User Authentication and Data Management

The backend supports user authentication through Clerk. This integration enables:

1. **User-Specific Data**: 
   - Each user has their own conversation history
   - Messages are associated with specific users
   - User preferences are stored in the database

2. **Database Schema**:
   - The database includes `user_id` columns in relevant tables (conversations, messages, attachments)
   - User preferences are stored in a dedicated table

3. **API Authentication**:
   - API endpoints accept a `user_id` parameter to filter data by user
   - WebSocket connections can be associated with specific users

4. **Migration Support**:
   - Database migrations are provided to add user-related columns to existing tables
   - The `add_user_id_columns.py` migration script adds the necessary columns for user data

## Testing the Full System

To test the full system (frontend + backend):

1. Start the backend server:
   ```bash
   cd /Users/trevoradelman/Documents/devStuff/langChainDev/swarms
   python -m uvicorn mosaic.backend.app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. In a separate terminal, start the frontend development server:
   ```bash
   cd /Users/trevoradelman/Documents/devStuff/langChainDev/swarms/mosaic/frontend
   npm install  # Only needed the first time
   npm run dev
   ```

3. Open your browser to http://localhost:3000 to access the MOSAIC interface.

## Dynamic Agent Discovery and API Endpoint Generation

The MOSAIC backend now includes a dynamic agent discovery system and automatic API endpoint generation for agents. This makes it easier to create and use new agents without modifying the core application code.

### Creating a New Agent

To create a new agent that will be automatically discovered:

1. Create a new Python file in the `mosaic/backend/agents` directory (e.g., `my_agent.py`)
2. Implement a registration function that starts with `register_` and takes a model parameter:

```python
from mosaic.backend.agents import BaseAgent

class MyAgent(BaseAgent):
    def __init__(self, name, model, tools=None, prompt=None):
        super().__init__(name, model, tools or [], prompt)
    
    def _get_default_prompt(self) -> str:
        return "You are a specialized agent that..."

def register_my_agent(model):
    """Register the my_agent agent."""
    agent = MyAgent("my_agent", model)
    return agent
```

The agent discovery system will automatically find this registration function and call it during startup, registering the agent with the agent registry.

### Using the Agent API

The agent API system automatically generates API endpoints for each agent:

- **GET /api/agents**: Get a list of all available agents
  ```bash
  curl http://localhost:8000/api/agents
  ```

- **GET /api/agents/{agent_id}**: Get information about a specific agent
  ```bash
  curl http://localhost:8000/api/agents/calculator
  ```

- **GET /api/agents/{agent_id}/capabilities**: Get the capabilities of a specific agent
  ```bash
  curl http://localhost:8000/api/agents/calculator/capabilities
  ```

- **POST /api/agents/{agent_id}/messages**: Send a message to an agent
  ```bash
  curl -X POST http://localhost:8000/api/agents/calculator/messages \
    -H "Content-Type: application/json" \
    -d '{"content": "What is 2 + 2?"}'
  ```

- **GET /api/agents/{agent_id}/messages**: Get all messages for a specific agent
  ```bash
  curl http://localhost:8000/api/agents/calculator/messages
  ```

- **POST /api/agents/{agent_id}/capabilities/{capability_name}**: Invoke a specific capability of an agent
  ```bash
  curl -X POST http://localhost:8000/api/agents/calculator/capabilities/add \
    -H "Content-Type: application/json" \
    -d '{"a": 2, "b": 2}'
  ```

## Troubleshooting

### Module Not Found Errors

If you encounter "Module not found" errors, make sure you're running the commands from the root directory (/Users/trevoradelman/Documents/devStuff/langChainDev/swarms) and that the Python module structure is correctly set up.

### OpenAI API Key Issues

If you encounter authentication errors with the OpenAI API, check that your API key is correctly set in the .env file and that it has the necessary permissions.

### WebSocket Connection Issues

If the WebSocket connection fails, make sure both the frontend and backend are running and that there are no network restrictions blocking WebSocket connections.

### Agent Discovery Issues

If your agent is not being discovered automatically, check the following:

1. Make sure the agent file is in the `mosaic/backend/agents` directory
2. Make sure the registration function starts with `register_` and takes a model parameter
3. Check the logs for any errors during agent discovery
4. Make sure the agent is properly registered with the agent registry

## Agent UI Framework

The MOSAIC backend includes a powerful Agent UI Framework that enables rich, interactive user interfaces for specialized agents beyond the traditional chat interface. This framework allows agents to offer visualizations, data processing tools, and interactive components tailored to their specific capabilities.

### UI Component System Directory Structure

The UI component system is organized into the following directories:

- **ui/base.py**: Contains the base UI component classes and component registry
- **ui/components/**: Contains specialized UI component implementations
- **app/ui_websocket_handler.py**: Handles WebSocket connections for UI components
- **app/ui_component_discovery.py**: Discovers and registers UI components

### Key Components

1. **UI Component Base Classes**
   - Located in `mosaic/backend/ui/base.py`
   - Provides abstract base classes for UI components
   - Handles component registration and discovery

2. **UI Component Registry**
   - Located in `mosaic/backend/ui/base.py`
   - Manages UI components and their association with agents
   - Provides methods for registering and retrieving components

3. **UI WebSocket Handler**
   - Located in `mosaic/backend/app/ui_websocket_handler.py`
   - Manages WebSocket connections for real-time communication
   - Routes events between UI components and frontend

4. **UI Component Discovery**
   - Located in `mosaic/backend/app/ui_component_discovery.py`
   - Discovers and registers UI components for agents
   - Maps components to agents based on capabilities

### Component Types

The framework includes several types of UI components:

1. **VisualizationComponent**: For data visualizations like charts and graphs
2. **InteractiveComponent**: For interactive components like forms and controls
3. **DataInputComponent**: For data input components like file uploads

### Using Agent Tools for Data Retrieval

A key feature of the Agent UI Framework is the direct use of agent tools for data retrieval. This approach replaces the previous DataProvider abstraction layer, allowing UI components to directly leverage the full capabilities of agents, including their reasoning abilities and error handling.

Example of using agent tools in a UI component:

```python
async def _get_data_from_agent(self, params):
    try:
        # Get the agent
        from mosaic.backend.app.agent_runner import get_initialized_agents
        initialized_agents = get_initialized_agents()
        agent = initialized_agents.get("financial_analysis")
        
        if not agent:
            raise ValueError(f"Agent 'financial_analysis' not found")
        
        # Find the tool
        tool = None
        for t in agent.tools:
            if t.name == "get_stock_history_tool":
                tool = t
                break
        
        if not tool:
            raise ValueError(f"Tool 'get_stock_history_tool' not found in agent 'financial_analysis'")
        
        # Invoke the tool
        response = tool.invoke({
            "symbol": params.get("symbol"),
            "period": params.get("period", "1mo"),
            "interval": params.get("interval", "1d")
        })
        
        # Process the response
        processed_data = self._parse_stock_history_response(response)
        
        return processed_data
    
    except Exception as e:
        logger.error(f"Error getting stock data from agent: {str(e)}")
        return {"error": str(e)}
```

### Creating a New UI Component

To create a new UI component:

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

### Registering Components with Agents

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

### WebSocket Communication

The UI component system uses WebSocket connections for real-time communication with the frontend. The WebSocket handler routes events to the appropriate component based on the event data.

Example of a WebSocket event:
```json
{
  "type": "data_request",
  "component": "stock-chart",
  "action": "get_stock_data",
  "data": {
    "symbol": "AAPL",
    "period": "1mo",
    "interval": "1d"
  }
}
```

The WebSocket handler routes this event to the `handle_get_stock_data` method of the `stock-chart` component, which then retrieves the data from the appropriate agent tool and sends a response.

### Testing UI Components

The framework includes comprehensive testing support for UI components:

1. **Unit Tests**: Test component registration, event handling, and data retrieval
2. **Integration Tests**: Test WebSocket communication and agent integration
3. **Mock Components**: Test components with mock data for development

Example test:
```python
def test_stock_chart_component():
    # Create the component
    component = StockChartComponent()
    
    # Test registration
    assert component.component_id == "stock-chart"
    assert component.name == "Stock Chart"
    
    # Test handler registration
    assert "get_stock_data" in component.handlers
    
    # Test data retrieval
    data = asyncio.run(component._get_data_from_agent({
        "symbol": "AAPL",
        "period": "1mo",
        "interval": "1d"
    }))
    
    assert "dates" in data
    assert "prices" in data
    assert len(data["dates"]) > 0
    assert len(data["prices"]) > 0
```
