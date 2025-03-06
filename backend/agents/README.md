# MOSAIC Agent System

This directory contains the agent system for the MOSAIC platform. The agent system is built on top of LangChain and LangGraph, providing a flexible and extensible framework for creating and orchestrating intelligent agents.

## Directory Structure

The agent system is organized into the following directories:

- **base.py**: Contains the base agent framework and agent registry
- **regular/**: Contains regular (specialized) agents
- **supervisors/**: Contains supervisor agents that orchestrate regular agents
- **internal/**: Contains internal utilities for agent management

## Architecture

The agent system follows a modular architecture with the following components:

### Base Agent Framework

The base agent framework provides the foundation for creating specialized agents. It includes:

- **BaseAgent**: An abstract base class that all agents inherit from
- **AgentRegistry**: A singleton registry for managing agents
- **Tool Utilities**: Utilities for creating and managing agent tools
- **Dynamic Discovery**: Automatic discovery and registration of agents and supervisors
- **API Endpoint Generation**: Dynamic generation of API endpoints for agents

### Regular Agents

Regular agents (in the `regular/` directory) are built on top of the base agent framework and provide specific capabilities:

- **CalculatorAgent**: Performs basic mathematical operations
- **WebSearchAgent**: Searches the web and retrieves webpage content
- **BrowserInteractionAgent**: Handles JavaScript-heavy websites
- **DataProcessingAgent**: Extracts and normalizes information
- **LiteratureAgent**: Searches for academic papers and articles
- **SafetyAgent**: Validates agent actions for safety
- **WriterAgent**: Handles file operations
- **StoryWriterAgent**: Generates creative stories based on prompts
- **FileProcessingAgent**: Processes and analyzes Excel files

### Supervisor Agents

Supervisor agents (in the `supervisors/` directory) orchestrate multiple regular agents to solve complex problems:

- **Calculator Supervisor**: Orchestrates the calculator agent to solve mathematical problems
- **Research Supervisor**: Orchestrates web search, browser interaction, data processing, and literature agents for comprehensive research tasks
- **Multi-Agent Supervisor**: Generic supervisor that can orchestrate any combination of regular agents

### Internal Utilities

Internal utilities (in the `internal/` directory) provide functionality for agent management:

- **AgentGenerator**: Validates agent definitions and handles agent registration
- **agent_schema.json**: JSON schema for validating agent definitions

## Usage

### Using Existing Agents

To use an existing agent, you can import it and invoke it directly:

```python
from mosaic.backend.agents import agent_registry

# Get an agent from the registry
calculator_agent = agent_registry.get("calculator")

# Invoke the agent
result = calculator_agent.invoke({"messages": [{"role": "user", "content": "Calculate 2 + 2"}]})
```

### Creating a New Agent

To create a new agent, inherit from the `BaseAgent` class and implement the required methods:

```python
from mosaic.backend.agents import BaseAgent

class MyAgent(BaseAgent):
    def _get_default_prompt(self) -> str:
        return "You are a specialized agent that..."
    
    # Add agent-specific tools and methods
```

### Registering an Agent

Register your agent with the agent registry to make it available to supervisors:

```python
from mosaic.backend.agents import agent_registry

# Create and register the agent
my_agent = MyAgent(model=model)
agent_registry.register(my_agent)
```

### Creating a Supervisor

Create a supervisor to orchestrate multiple agents:

```python
from mosaic.backend.agents import create_multi_agent_supervisor

# Create a supervisor with specific agents
supervisor = create_multi_agent_supervisor(
    model=model,
    agent_names=["calculator", "my_agent"]
)

# Invoke the supervisor
result = supervisor.invoke({"messages": [{"role": "user", "content": "..."}]})
```

## Testing

Each agent includes a test script that demonstrates its capabilities:

```bash
# Test the calculator agent
python -m mosaic.backend.tests.test_calculator

# Test the research supervisor (orchestrates multiple agents)
python -m mosaic.backend.tests.test_research_supervisor
```

## Adding New Tools

When creating tools for agents, it's important to define them as standalone functions rather than instance methods. This avoids the `TypeError("StructuredTool._run() got multiple values for argument 'self'")` error that occurs when using instance methods as tools.

### ✅ Correct Way: Define Tools as Standalone Functions

```python
from langchain_core.tools import tool

@tool
def add_tool(a: float, b: float) -> float:
    """
    Add two numbers.
    
    Args:
        a: The first number
        b: The second number
        
    Returns:
        The sum of a and b
    """
    return a + b

class MyAgent(BaseAgent):
    def __init__(self, name, model, tools=None, prompt=None):
        # Use the standalone function as a tool
        agent_tools = [add_tool]
        
        super().__init__(name, model, agent_tools + (tools or []), prompt)
```

### ❌ Incorrect Way: Define Tools as Instance Methods

```python
class MyAgent(BaseAgent):
    @tool  # This will cause errors!
    def add(self, a: float, b: float) -> float:
        """Add two numbers."""
        return a + b
        
    def __init__(self, name, model, tools=None, prompt=None):
        # This approach will cause TypeError when the tool is used
        agent_tools = [self.add]
        
        super().__init__(name, model, agent_tools + (tools or []), prompt)
```

### Important Notes

1. Always define tools as standalone functions with the `@tool` decorator
2. Make sure tool names are unique across the system
3. Include detailed docstrings for each tool, as they are used by the LLM to understand the tool's purpose
4. When updating tool names, make sure to update any references in supervisor prompts
5. When handling message objects in test scripts or UI code, always check the object type before accessing properties:
   ```python
   # Correct way to handle different message types
   if isinstance(message, dict) and message.get("role") == "user":
       # Handle dictionary-style messages
       content = message.get("content", "")
   elif hasattr(message, "content"):
       # Handle object-style messages (like HumanMessage, AIMessage)
       content = message.content
   ```

## Logging Best Practices

Proper logging is essential for debugging and monitoring agent behavior, especially for supervisor agents that orchestrate multiple specialized agents. The MOSAIC platform includes a WebSocket-based logging system that captures logs from agents and displays them in the UI.

### Logging in Tools

When creating tools for agents, use the logger to log important information:

```python
import logging

# Configure logging
logger = logging.getLogger("mosaic.agents.my_agent")

@tool
def my_tool(param: str) -> str:
    """
    A tool that does something.
    
    Args:
        param: The parameter
        
    Returns:
        The result
    """
    logger.info(f"Processing parameter: {param}")
    
    # Do something with the parameter
    result = process_param(param)
    
    logger.info(f"Result: {result}")
    return result
```

### Logging in Supervisor Agents

For supervisor agents that orchestrate multiple specialized agents, it's important to ensure that logs from all specialized agents are captured and displayed in the UI. The WebSocket log handler in the main.py file is set up to capture logs from the supervisor agent and all its specialized agents.

When creating a new supervisor agent, make sure to follow this pattern in the main.py file:

```python
# Add the handler to the agent's logger
agent_logger = logging.getLogger(f"mosaic.agents.{agent_id}")
agent_logger.addHandler(ws_handler)

# For supervisor agents, also add the handler to the specialized agents' loggers
if agent_id == "my_supervisor":
    # Add handler to each specialized agent's logger
    for specialized_agent_name in ["agent1", "agent2", "agent3"]:
        specialized_agent_logger = logging.getLogger(f"mosaic.agents.{specialized_agent_name}")
        specialized_agent_logger.addHandler(ws_handler)
    
    logger.info(f"Added log handlers to all specialized agents for {agent_id}")
```

And in the cleanup code:

```python
# Remove the custom log handler from the agent's logger
if ws_handler in agent_logger.handlers:
    agent_logger.removeHandler(ws_handler)

# For supervisor agents, also remove the handler from the specialized agents' loggers
if agent_id == "my_supervisor":
    # Remove handler from each specialized agent's logger
    for specialized_agent_name in ["agent1", "agent2", "agent3"]:
        specialized_agent_logger = logging.getLogger(f"mosaic.agents.{specialized_agent_name}")
        if ws_handler in specialized_agent_logger.handlers:
            specialized_agent_logger.removeHandler(ws_handler)
    
    logger.info(f"Removed log handlers from all specialized agents for {agent_id}")
```

This ensures that logs from all specialized agents are captured and displayed in the UI, providing a comprehensive view of the supervisor agent's behavior.

## Dynamic Agent Discovery and API Endpoint Generation

The MOSAIC platform includes a dynamic agent discovery system and automatic API endpoint generation for agents. This makes it easier to use new agents without modifying the core application code.

### Dynamic Agent Discovery

The agent discovery system automatically scans the agents directory for Python files, extracts agent registration functions, and calls them automatically during startup. This means you can create a new agent by simply adding a new file to the agents directory.

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

### Agent Metadata Extraction

The agent discovery system also extracts metadata from agent classes, including:

- **Name**: The name of the agent
- **Description**: The description of the agent (from the docstring)
- **Type**: The type of agent (Utility, Specialized, Supervisor)
- **Capabilities**: The capabilities of the agent (from tools or docstring)
- **Icon**: An icon for the agent (emoji)

This metadata is used to generate API endpoints and UI components for the agent.

### Dynamic API Endpoint Generation

The agent API system automatically generates API endpoints for each agent, including:

- **GET /api/agents**: Get a list of all available agents
- **GET /api/agents/{agent_id}**: Get information about a specific agent
- **GET /api/agents/{agent_id}/capabilities**: Get the capabilities of a specific agent
- **POST /api/agents/{agent_id}/messages**: Send a message to an agent
- **GET /api/agents/{agent_id}/messages**: Get all messages for a specific agent
- **POST /api/agents/{agent_id}/capabilities/{capability_name}**: Invoke a specific capability of an agent

This means you can create a new agent and immediately use it through the API without modifying the core application code.

## File Processing System

The MOSAIC platform includes a file processing system that allows users to upload files and have them processed by specialized agents. The system is built around two main components:

### FileProcessingAgent

The `FileProcessingAgent` is a specialized agent that processes uploaded files. It currently focuses on Excel (XLSX) files, extracting and analyzing tabular data. The agent provides the following tools:

- **process_excel_file_tool**: Extracts basic information and preview data from Excel files
- **analyze_excel_data_tool**: Performs specific analyses like correlation, summary statistics, or groupby

The `FileProcessingAgent` is designed to handle file attachments directly, retrieving the file data from the database if necessary. It includes robust error handling and logging to help diagnose issues with file processing.

### FileProcessingSupervisor

The `FileProcessingSupervisor` is a supervisor agent that orchestrates file processing. It determines the file type and routes processing to specialized agents like the `FileProcessingAgent`. The supervisor provides the following tools:

- **transfer_to_file_processing**: Transfers control to the `FileProcessingAgent` for processing Excel files
- **transfer_back_to_file_processing_supervisor**: Transfers control back to the supervisor after processing

The supervisor is designed to handle file attachments in messages, automatically detecting when a file has been uploaded and transferring control to the appropriate specialized agent.

### File Processing Flow

The file processing flow works as follows:

1. The user uploads a file through the chat interface
2. The file is stored in the database as an attachment
3. The message with the attachment is sent to the `file_processing_supervisor` agent
4. The supervisor detects the file attachment and transfers control to the `file_processing` agent
5. The `file_processing` agent retrieves the file data from the database
6. The agent processes the file and returns the results
7. The supervisor includes the full results in its response to the user

This architecture allows for easy extension to support additional file types in the future by adding new specialized agents and updating the supervisor to route to them based on file type.

### Adding Support for New File Types

To add support for a new file type:

1. Create a new specialized agent that handles the file type (e.g., `PDFProcessingAgent`)
2. Implement tools for processing the file type (e.g., `process_pdf_file_tool`)
3. Update the `file_processing_supervisor` to detect the file type and transfer control to the new agent
4. Register the new agent with the agent registry

The modular design of the file processing system makes it easy to extend with support for additional file types while maintaining a consistent user experience.

## References

- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
