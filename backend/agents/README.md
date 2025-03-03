# MOSAIC Agent System

This directory contains the agent system for the MOSAIC platform. The agent system is built on top of LangChain and LangGraph, providing a flexible and extensible framework for creating and orchestrating intelligent agents.

## Architecture

The agent system follows a modular architecture with the following components:

### Base Agent Framework

The base agent framework provides the foundation for creating specialized agents. It includes:

- **BaseAgent**: An abstract base class that all agents inherit from
- **AgentRegistry**: A singleton registry for managing agents
- **Tool Utilities**: Utilities for creating and managing agent tools

### Specialized Agents

Specialized agents are built on top of the base agent framework and provide specific capabilities:

- **CalculatorAgent**: Performs basic mathematical operations
- **SafetyAgent**: Validates agent actions for safety (coming soon)
- **WriterAgent**: Handles file operations (coming soon)
- **DeveloperAgent**: Creates and modifies code (coming soon)

### Supervisor System

The supervisor system orchestrates multiple agents to solve complex problems:

- **Calculator Supervisor**: Orchestrates the calculator agent
- **Multi-Agent Supervisor**: Orchestrates multiple specialized agents

## Usage

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

Each agent includes a test script that demonstrates its capabilities. For example, to test the calculator agent:

```bash
python -m mosaic.backend.test_calculator
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

## References

- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
