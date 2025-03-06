# MOSAIC Backend

This directory contains the backend components of the MOSAIC system, including the FastAPI application, agent system, and database models.

## System Architecture

The MOSAIC backend consists of several key components:

1. **FastAPI Application**: Provides REST API endpoints and WebSocket connections for the frontend
2. **Agent System**: Implements the agent framework, regular agents, and supervisor agents
   - **Dynamic Agent Discovery**: Automatically discovers and registers both regular agents and supervisors
   - **API Endpoint Generation**: Dynamically generates API endpoints for agents
3. **Database Models**: Defines the data models for storing queries, responses, and agent configurations

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
