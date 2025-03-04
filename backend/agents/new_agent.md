# Creating New Agents in Mosaic

This guide provides a comprehensive overview of how to create new agents in the Mosaic system. It covers both specialized agents with their own tools and supervisor agents that orchestrate multiple specialized agents.

## Table of Contents

1. [Understanding the Agent Architecture](#understanding-the-agent-architecture)
2. [Creating a Specialized Agent](#creating-a-specialized-agent)
   - [Step 1: Define Tools](#step-1-define-tools)
   - [Step 2: Create the Agent Class](#step-2-create-the-agent-class)
   - [Step 3: Create a Registration Function](#step-3-create-a-registration-function)
   - [Step 4: Add the Agent to the Initialization Process](#step-4-add-the-agent-to-the-initialization-process)
   - [Step 5: Update the API Endpoints](#step-5-update-the-api-endpoints)
   - [Step 6: Implement Proper Logging](#step-6-implement-proper-logging)
3. [Creating a Supervisor Agent](#creating-a-supervisor-agent)
   - [Step 1: Define the Specialized Agents](#step-1-define-the-specialized-agents)
   - [Step 2: Create the Supervisor Function](#step-2-create-the-supervisor-function)
   - [Step 3: Add the Supervisor to the Initialization Process](#step-3-add-the-supervisor-to-the-initialization-process)
   - [Step 4: Update the API Endpoints](#step-4-update-the-api-endpoints-1)
   - [Step 5: Implement Proper Logging](#step-5-implement-proper-logging-1)
4. [Testing Your Agents](#testing-your-agents)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)

## Understanding the Agent Architecture

The Mosaic system is built on a modular agent architecture that consists of:

1. **Base Agent Framework**: Provides the foundation for all agents, including the `BaseAgent` class and the `AgentRegistry` for managing agents.

2. **Specialized Agents**: Agents that perform specific tasks using tools, such as the `WebSearchAgent` for searching the web or the `CalculatorAgent` for performing mathematical operations.

3. **Supervisor Agents**: Agents that orchestrate multiple specialized agents to solve complex problems, such as the `ResearchSupervisor` that coordinates web search, browser interaction, data processing, and literature agents.

4. **Tools**: Functions that agents can use to perform specific tasks, such as `search_web_tool` for searching the web or `add_tool` for adding numbers.

5. **API Layer**: FastAPI endpoints that expose the agents to the frontend, allowing users to interact with them.

## Creating a Specialized Agent

A specialized agent is an agent that performs a specific task using tools. Here's how to create one:

### Step 1: Define Tools

Tools are functions that agents can use to perform specific tasks. They should be defined as standalone functions with the `@tool` decorator from LangChain.

```python
import logging
from langchain_core.tools import tool

# Configure logging
logger = logging.getLogger("mosaic.agents.your_agent_name")

@tool
def your_tool_name(param1: str, param2: int) -> str:
    """
    Description of what your tool does.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of the return value
    """
    logger.info(f"Using your_tool_name with params: {param1}, {param2}")
    
    try:
        # Implement your tool's functionality here
        result = f"Processed {param1} {param2} times"
        
        logger.info(f"Tool result: {result}")
        return result
    
    except Exception as e:
        logger.error(f"Error in your_tool_name: {str(e)}")
        return f"Error: {str(e)}"
```

Important considerations for tools:

- Always define tools as standalone functions, not as instance methods of a class.
- Use the `@tool` decorator from LangChain to mark functions as tools.
- Include detailed docstrings that describe what the tool does, its parameters, and its return value.
- Implement proper logging to track the tool's execution and any errors.
- Handle exceptions gracefully and return informative error messages.

### Step 2: Create the Agent Class

Create a new Python file in the `mosaic/backend/agents` directory for your agent. The file should define a class that inherits from `BaseAgent` and implements the required methods.

```python
"""
Your Agent Module for MOSAIC

Description of what your agent does and its purpose in the MOSAIC system.
"""

import logging
from typing import List, Dict, Any, Optional

from langchain_core.language_models import LanguageModelLike
from langchain_core.tools import BaseTool

try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.agents.base import BaseAgent, agent_registry
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.agents.base import BaseAgent, agent_registry

# Configure logging
logger = logging.getLogger("mosaic.agents.your_agent_name")

# Import or define your tools here
# from .your_tools import your_tool_name

class YourAgentClass(BaseAgent):
    """
    Description of your agent and what it does.
    """
    
    def __init__(
        self,
        name: str = "your_agent_name",
        model: Optional[LanguageModelLike] = None,
        tools: List[BaseTool] = None,
        prompt: str = None,
        description: str = None,
    ):
        """
        Initialize a new instance of your agent.
        
        Args:
            name: The name of the agent (default: "your_agent_name")
            model: The language model to use for the agent
            tools: Optional list of additional tools
            prompt: Optional system prompt for the agent
            description: Optional description of the agent
        """
        # Define your agent's tools
        agent_tools = [
            your_tool_name,
            # Add more tools here
        ]
        
        # Combine with any additional tools
        all_tools = agent_tools + (tools or [])
        
        super().__init__(
            name=name,
            model=model,
            tools=all_tools,
            prompt=prompt,
            description=description or "Description of your agent"
        )
        
        logger.info(f"Initialized {name} agent with {len(all_tools)} tools")
    
    def _get_default_prompt(self) -> str:
        """
        Get the default system prompt for your agent.
        
        Returns:
            A string containing the default system prompt
        """
        return (
            "You are an agent that [describe what your agent does]. "
            "Your job is to [describe the agent's purpose and responsibilities]. "
            "\n\n"
            "You have the following tools at your disposal: "
            "- Use your_tool_name to [describe what the tool does]. "
            # Add descriptions for other tools
            "\n\n"
            "Always provide factual information based on your tools. "
            "If you cannot complete a task, clearly state that and explain why. "
            "Never make up information or hallucinate details."
        )
```

Important considerations for agent classes:

- Inherit from `BaseAgent` to get the common functionality for all agents.
- Implement the `_get_default_prompt` method to provide a default system prompt for the agent.
- Include detailed docstrings that describe what the agent does and how it works.
- Implement proper logging to track the agent's initialization and execution.

### Step 3: Create a Registration Function

Add a function to register your agent with the agent registry. This function will be called during the initialization process to create and register your agent.

```python
def register_your_agent(model: LanguageModelLike) -> YourAgentClass:
    """
    Create and register your agent.
    
    Args:
        model: The language model to use for the agent
        
    Returns:
        The created agent
    """
    try:
        # Try importing with the full package path (for local development)
        from mosaic.backend.agents.base import agent_registry
    except ImportError:
        # Fall back to relative import (for Docker environment)
        from backend.agents.base import agent_registry
    
    your_agent = YourAgentClass(model=model)
    agent_registry.register(your_agent)
    return your_agent
```

### Step 4: Automatic Discovery and API Endpoint Generation

The MOSAIC system now includes a dynamic agent discovery system that automatically scans the agents directory for Python files, extracts agent registration functions, and calls them automatically during startup. This means you don't need to manually modify the `initialize_agents` function in `main.py` or update the API endpoints.

When you create a new agent file in the `mosaic/backend/agents` directory with a registration function that starts with `register_`, the system will automatically:

1. Discover the agent during startup
2. Register the agent with the agent registry
3. Generate API endpoints for the agent
4. Extract metadata from the agent class (name, description, capabilities, icon, etc.)
5. Make the agent available through the API

For example, if you create a file `mosaic/backend/agents/your_agent.py` with a registration function `register_your_agent`, the system will automatically discover and register your agent during startup. You can then access your agent through the API at `/api/agents/your_agent_name`.

The system also automatically generates the following API endpoints for your agent:

- **GET /api/agents**: Lists all available agents, including your agent
- **GET /api/agents/your_agent_name**: Gets information about your agent
- **GET /api/agents/your_agent_name/capabilities**: Gets the capabilities of your agent
- **POST /api/agents/your_agent_name/messages**: Sends a message to your agent
- **GET /api/agents/your_agent_name/messages**: Gets all messages for your agent
- **POST /api/agents/your_agent_name/capabilities/{capability_name}**: Invokes a specific capability of your agent

To ensure your agent is properly discovered and registered, make sure:

1. Your agent file is in the `mosaic/backend/agents` directory
2. Your agent class inherits from `BaseAgent`
3. Your registration function starts with `register_` and takes a model parameter
4. Your agent class has appropriate metadata (name, description, capabilities, icon, etc.)

### Step 6: Implement Proper Logging

Ensure that your agent and its tools implement proper logging to track their execution and any errors. This is important for debugging and for providing feedback to users.

In the WebSocket endpoint in `mosaic/backend/app/main.py`, add a section to handle your agent's logs:

```python
# For your_agent_name, also add the handler to any specialized loggers it might use
if agent_id == "your_agent_name":
    # Add handler to your_agent_name logger
    your_agent_logger = logging.getLogger("mosaic.agents.your_agent_name")
    your_agent_logger.addHandler(ws_handler)
    
    # If your agent uses other loggers, add handlers for them too
    # other_logger = logging.getLogger("mosaic.agents.other_component")
    # other_logger.addHandler(ws_handler)
    
    logger.info("Added log handlers to all components for your_agent_name")
```

And in the cleanup section:

```python
# For your_agent_name, also remove the handler from any specialized loggers it might use
if agent_id == "your_agent_name":
    # Remove handler from your_agent_name logger
    your_agent_logger = logging.getLogger("mosaic.agents.your_agent_name")
    if ws_handler in your_agent_logger.handlers:
        your_agent_logger.removeHandler(ws_handler)
    
    # If your agent uses other loggers, remove handlers from them too
    # other_logger = logging.getLogger("mosaic.agents.other_component")
    # if ws_handler in other_logger.handlers:
    #     other_logger.removeHandler(ws_handler)
    
    logger.info("Removed log handlers from all components for your_agent_name")
```

## Creating a Supervisor Agent

A supervisor agent is an agent that orchestrates multiple specialized agents to solve complex problems. Here's how to create one:

### Step 1: Define the Specialized Agents

Before creating a supervisor agent, you need to define the specialized agents that it will orchestrate. Follow the steps in the previous section to create the specialized agents.

### Step 2: Create the Supervisor Function

Create a new function in `mosaic/backend/agents/supervisor.py` that creates a supervisor agent that orchestrates your specialized agents.

```python
def create_your_supervisor(
    model: LanguageModelLike,
    output_mode: str = "full_history"
) -> StateGraph:
    """
    Create a supervisor that orchestrates multiple agents for your task.
    
    This function creates a supervisor that can orchestrate agent1, agent2, agent3, etc.
    to perform your complex task.
    
    Args:
        model: The language model to use for the supervisor
        output_mode: How to handle agent outputs ("full_history" or "last_message")
        
    Returns:
        A StateGraph representing the supervisor workflow
    """
    # Make sure all required agents are registered
    try:
        # Try importing with the full package path (for local development)
        from mosaic.backend.agents.agent1 import register_agent1
        from mosaic.backend.agents.agent2 import register_agent2
        from mosaic.backend.agents.agent3 import register_agent3
    except ImportError:
        # Fall back to relative import (for Docker environment)
        from backend.agents.agent1 import register_agent1
        from backend.agents.agent2 import register_agent2
        from backend.agents.agent3 import register_agent3
    
    # Register agents if they don't exist
    agent1 = agent_registry.get("agent1")
    if agent1 is None:
        logger.info("Agent1 not found in registry, registering it now")
        agent1 = register_agent1(model)
    
    agent2 = agent_registry.get("agent2")
    if agent2 is None:
        logger.info("Agent2 not found in registry, registering it now")
        agent2 = register_agent2(model)
    
    agent3 = agent_registry.get("agent3")
    if agent3 is None:
        logger.info("Agent3 not found in registry, registering it now")
        agent3 = register_agent3(model)
    
    # Define the agent names to include
    agent_names = ["agent1", "agent2", "agent3"]
    
    # Create the supervisor prompt
    prompt = (
        "You are a supervisor managing a team of specialized agents:\n"
        "1. agent1: Use for [describe what agent1 does].\n"
        "2. agent2: Use for [describe what agent2 does].\n"
        "3. agent3: Use for [describe what agent3 does].\n"
        "\n"
        "Your job is to coordinate these agents to [describe the supervisor's purpose]. "
        "Break down tasks and delegate to the appropriate agent. "
        "Synthesize the information they provide into a coherent response.\n"
        "\n"
        "Important rules:\n"
        "- [Rule 1]\n"
        "- [Rule 2]\n"
        "- [Rule 3]\n"
        "- Only use factual information retrieved by the agents.\n"
        "- If information cannot be found, clearly state that and explain why.\n"
        "- Never make up information or hallucinate details.\n"
        "- Provide clear error reports when agents fail, but always try alternative approaches.\n"
        "- Always attribute information to its source."
    )
    
    # Create the supervisor
    logger.info(f"Creating your supervisor with agents: {', '.join(agent_names)}")
    supervisor = agent_registry.create_supervisor(
        model=model,
        agent_names=agent_names,
        prompt=prompt,
        name="your_supervisor",
        output_mode=output_mode
    )
    
    logger.info("Successfully created your supervisor")
    return supervisor.compile()
```

### Step 3: Create a Registration Function for the Supervisor

Add a function to register your supervisor with the agent registry. This function will be called during the initialization process to create and register your supervisor.

```python
def register_your_supervisor(model: LanguageModelLike) -> StateGraph:
    """
    Create and register your supervisor agent.
    
    Args:
        model: The language model to use for the supervisor
        
    Returns:
        The created supervisor agent
    """
    try:
        # Try importing with the full package path (for local development)
        from mosaic.backend.agents.base import agent_registry
    except ImportError:
        # Fall back to relative import (for Docker environment)
        from backend.agents.base import agent_registry
    
    # Create the supervisor
    supervisor = create_your_supervisor(model)
    
    # Register the supervisor with the agent registry
    agent_registry.register_supervisor("your_supervisor", supervisor)
    
    return supervisor
```

### Step 4: Automatic Discovery and API Endpoint Generation

Just like with specialized agents, the MOSAIC system's dynamic agent discovery system will automatically scan the agents directory for Python files, extract supervisor registration functions, and call them automatically during startup. This means you don't need to manually modify the `initialize_agents` function in `main.py` or update the API endpoints.

When you create a new supervisor file in the `mosaic/backend/agents` directory with a registration function that starts with `register_` and ends with `_supervisor`, the system will automatically:

1. Discover the supervisor during startup
2. Register the supervisor with the agent registry
3. Generate API endpoints for the supervisor
4. Extract metadata from the supervisor (name, description, capabilities, icon, etc.)
5. Make the supervisor available through the API

For example, if you create a file `mosaic/backend/agents/your_supervisor.py` with a registration function `register_your_supervisor`, the system will automatically discover and register your supervisor during startup. You can then access your supervisor through the API at `/api/agents/your_supervisor`.

The system also automatically generates the following API endpoints for your supervisor:

- **GET /api/agents**: Lists all available agents, including your supervisor
- **GET /api/agents/your_supervisor**: Gets information about your supervisor
- **GET /api/agents/your_supervisor/capabilities**: Gets the capabilities of your supervisor
- **POST /api/agents/your_supervisor/messages**: Sends a message to your supervisor
- **GET /api/agents/your_supervisor/messages**: Gets all messages for your supervisor

To ensure your supervisor is properly discovered and registered, make sure:

1. Your supervisor file is in the `mosaic/backend/agents` directory
2. Your registration function starts with `register_` and takes a model parameter
3. Your supervisor has appropriate metadata (name, description, capabilities, icon, etc.)

### Step 5: Implement Proper Logging

Ensure that your supervisor and its specialized agents implement proper logging to track their execution and any errors. This is important for debugging and for providing feedback to users.

In the WebSocket endpoint in `mosaic/backend/app/main.py`, add a section to handle your supervisor's logs:

```python
# For your_supervisor, also add the handler to the specialized agents' loggers
if agent_id == "your_supervisor":
    # Add handler to agent1 logger
    agent1_logger = logging.getLogger("mosaic.agents.agent1")
    agent1_logger.addHandler(ws_handler)
    
    # Add handler to agent2 logger
    agent2_logger = logging.getLogger("mosaic.agents.agent2")
    agent2_logger.addHandler(ws_handler)
    
    # Add handler to agent3 logger
    agent3_logger = logging.getLogger("mosaic.agents.agent3")
    agent3_logger.addHandler(ws_handler)
    
    logger.info("Added log handlers to all specialized agents for your_supervisor")
```

And in the cleanup section:

```python
# For your_supervisor, also remove the handler from the specialized agents' loggers
if agent_id == "your_supervisor":
    # Remove handler from agent1 logger
    agent1_logger = logging.getLogger("mosaic.agents.agent1")
    if ws_handler in agent1_logger.handlers:
        agent1_logger.removeHandler(ws_handler)
    
    # Remove handler from agent2 logger
    agent2_logger = logging.getLogger("mosaic.agents.agent2")
    if ws_handler in agent2_logger.handlers:
        agent2_logger.removeHandler(ws_handler)
    
    # Remove handler from agent3 logger
    agent3_logger = logging.getLogger("mosaic.agents.agent3")
    if ws_handler in agent3_logger.handlers:
        agent3_logger.removeHandler(ws_handler)
    
    logger.info("Removed log handlers from all specialized agents for your_supervisor")
```

## Testing Your Agents

Before deploying your agents, it's important to test them to ensure they work as expected. Here's how to create a test script for your agent:

```python
"""
Test script for your agent

This script demonstrates the capabilities of your agent.
"""

import os
import logging
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("mosaic.test_your_agent")

# Load environment variables from .env file
load_dotenv()

# Check if the OpenAI API key is set
if not os.getenv("OPENAI_API_KEY"):
    print("Please set your OPENAI_API_KEY in the .env file")
    exit(1)

def main():
    """Run the test for your agent."""
    print("Your Agent Test")
    print("-----------------------------")
    print("This test demonstrates the capabilities of your agent.")
    print("It can [describe what your agent can do].")
    print("\nExample queries:")
    print("- '[Example query 1]'")
    print("- '[Example query 2]'")
    print("- '[Example query 3]'")
    print("\nType 'exit' to quit.")
    print("-----------------------------\n")
    
    # Initialize the language model
    model = ChatOpenAI(model="gpt-4o-mini")
    
    # Import your agent
    try:
        # Try importing with the full package path (for local development)
        from mosaic.backend.agents.your_agent import register_your_agent
    except ImportError:
        # Fall back to relative import (for Docker environment)
        from backend.agents.your_agent import register_your_agent
    
    # Create your agent
    logger.info("Creating your agent...")
    your_agent = register_your_agent(model)
    logger.info("Your agent created successfully")
    
    # Initialize the conversation state
    state = {"messages": []}
    
    while True:
        # Get user input
        user_input = input("\nYou: ")
        if user_input.lower() == 'exit':
            break
        
        # Add the user message to the state
        user_message = {"role": "user", "content": user_input}
        state["messages"].append(user_message)
        
        print("\nProcessing... (this may take some time)")
        logger.info(f"Your Agent: Starting processing for query: '{user_input}'")
        
        try:
            # Invoke your agent
            logger.info(f"Invoking your agent...")
            result = your_agent.invoke(state)
            logger.info(f"Your agent completed processing")
            
            # Update the state with the result
            state = result
            
            # Print the agent responses
            for message in result["messages"]:
                # Skip user messages
                if (isinstance(message, dict) and message.get("role") == "user") or \
                   (hasattr(message, "type") and message.type == "human"):
                    continue
                
                # Log agent responses
                if hasattr(message, "name") and message.name:
                    logger.info(f"Response from {message.name}")
                    print(f"\n{message.name}: {message.content}")
                elif hasattr(message, "content"):
                    logger.info(f"Response from Assistant")
                    print(f"\nAssistant: {message.content}")
                elif isinstance(message, dict) and "content" in message:
                    logger.info(f"Response from Assistant")
                    print(f"\nAssistant: {message['content']}")
                    
            logger.info(f"Processing completed successfully")
            
        except Exception as e:
            logger.error(f"Error in processing: {str(e)}")
            print(f"\nError: An error occurred while processing your request: {str(e)}")

if __name__ == "__main__":
    main()
```

## Best Practices

When creating new agents, follow these best practices:

1. **Modular Design**: Keep your agent's code modular and focused on a specific task. If an agent is becoming too complex, consider breaking it down into multiple specialized agents orchestrated by a supervisor.

2. **Comprehensive Logging**: Implement detailed logging throughout your agent's code to track its execution and any errors. This is important for debugging and for providing feedback to users.

3. **Error Handling**: Handle exceptions gracefully and provide informative error messages. This helps users understand what went wrong and how to fix it.

4. **Clear Documentation**: Include detailed docstrings and comments in your code to explain what your agent does and how it works. This makes it easier for others to understand and maintain your code.

5. **Consistent Naming**: Use consistent naming conventions for your agents, tools, and functions. This makes your code more readable and easier to understand.

6. **Tool Design**: Design your tools to be focused on a single task and to handle edge cases gracefully. Include detailed docstrings that describe what the tool does, its parameters, and its return value.

7. **Prompt Engineering**: Craft your agent's system prompt carefully to ensure it understands its role and responsibilities. Include clear instructions on when and how to use its tools.

8. **Testing**: Test your agent thoroughly with a variety of inputs to ensure it works as expected. Create a test script that demonstrates its capabilities and catches any issues.

9. **UI Integration**: Consider how your agent will be displayed in the UI and provide appropriate metadata (name, description, capabilities, icon) to make it user-friendly.

10. **Performance Optimization**: Optimize your agent's performance by minimizing unnecessary API calls and computations. Use caching where appropriate to avoid redundant operations.

## Troubleshooting

Here are some common issues you might encounter when creating new agents and how to fix them:

### Agent Not Appearing in UI

If your agent is not appearing in the UI, check the following:

1. Make sure your agent is properly registered with the agent registry in the `register_your_agent` function.
2. Make sure your agent is added to the `initialized_agents` dictionary in the `initialize_agents` function.
3. Make sure the `get_agents` and `get_agent` API endpoints include your agent in their switch statements.
4. Check the server logs for any errors during agent initialization.

### Agent Not Responding to Messages

If your agent is not responding to messages, check the following:

1. Make sure your agent's tools are properly defined and registered.
2. Make sure your agent's system prompt is clear and instructs the agent to use its tools.
3. Check the server logs for any errors during agent invocation.
4. Make sure the language model is properly initialized and has access to the tools.

### Logs Not Appearing in UI

If your agent's logs are not appearing in the UI, check the following:

1. Make sure your agent and its tools are using the correct logger (`logging.getLogger("mosaic.agents.your_agent_name")`).
2. Make sure the WebSocket log handler is properly added to your agent's logger in the WebSocket endpoint.
3. Make sure the WebSocket log handler is properly removed from your agent's logger in the cleanup section.
4. Check the server logs for any errors during log handling.

### Supervisor Not Orchestrating Agents Correctly

If your supervisor is not orchestrating agents correctly, check the following:

1. Make sure all the specialized agents are properly registered with the agent registry.
2. Make sure the supervisor's prompt clearly describes each agent's role and when to use it.
3. Make sure the supervisor has access to all the specialized agents it needs.
4. Check the server logs for any errors during supervisor invocation.

### Tool Execution Errors

If your tools are encountering errors during execution, check the following:

1. Make sure your tools are properly defined and handle exceptions gracefully.
2. Make sure your tools have access to any external resources they need (APIs, databases, etc.).
3. Make sure your tools are properly documented so the agent knows how to use them.
4. Check the server logs for any errors during tool execution.

### Performance Issues

If your agent is slow or unresponsive, check the following:

1. Make sure your tools are optimized for performance and don't make unnecessary API calls or computations.
2. Consider using caching to avoid redundant operations.
3. Make sure your agent's prompt is clear and concise to minimize token usage.
4. Consider using a faster language model for simple tasks.
