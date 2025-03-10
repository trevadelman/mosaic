# Creating a New Agent in Mosaic

This comprehensive guide walks you through the process of creating a new agent in the Mosaic framework. It covers everything from understanding the basic concepts to implementing, testing, and deploying your agent.

## Table of Contents

1. [Introduction to Agents in Mosaic](#introduction-to-agents-in-mosaic)
2. [Agent Architecture Overview](#agent-architecture-overview)
3. [Prerequisites](#prerequisites)
4. [Step-by-Step Guide to Creating a New Agent](#step-by-step-guide-to-creating-a-new-agent)
5. [Testing Your Agent](#testing-your-agent)
6. [Registering Your Agent](#registering-your-agent)
7. [Advanced Agent Features](#advanced-agent-features)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)
10. [Examples](#examples)

## Introduction to Agents in Mosaic

Agents in Mosaic are specialized AI assistants designed to perform specific tasks. Each agent has a defined purpose, capabilities, and tools it can use. The Mosaic framework provides a structured way to create, manage, and deploy these agents.

### Types of Agents

Mosaic supports several types of agents:

1. **Regular Agents**: Standalone agents that perform specific tasks (e.g., calculator, file processing)
2. **Supervisor Agents**: Agents that coordinate other agents to solve complex problems
3. **Specialized Agents**: Agents with domain-specific knowledge and capabilities

### Agent Components

Each agent consists of:

- **Name**: A unique identifier for the agent
- **Description**: A clear explanation of what the agent does
- **Tools**: Functions the agent can use to perform tasks
- **Prompt**: Instructions that guide the agent's behavior
- **Model**: The underlying language model that powers the agent
- **Capabilities**: A list of what the agent can do
- **Icon**: A visual representation of the agent (emoji)

## Agent Architecture Overview

Before creating an agent, it's important to understand how agents fit into the Mosaic architecture:

1. **Agent Registry**: Central system that keeps track of all available agents
2. **Agent Discovery**: Mechanism that finds and registers agents at startup
3. **Agent Runner**: System that initializes and runs agents
4. **Agent API**: Interface for interacting with agents from the frontend

Agents are built on top of LangChain and LangGraph, which provide the foundation for creating AI agents with tools and workflows.

## Prerequisites

Before creating a new agent, ensure you have:

1. **Mosaic Framework**: A working installation of the Mosaic framework
2. **Python Knowledge**: Basic understanding of Python programming
3. **LangChain Familiarity**: Basic understanding of LangChain concepts (optional but helpful)
4. **API Keys**: Access to necessary API keys (e.g., OpenAI API key)
5. **Development Environment**: A code editor and terminal

## Step-by-Step Guide to Creating a New Agent

### 1. Plan Your Agent

Before writing any code, define:

- **Purpose**: What specific problem will your agent solve?
- **Capabilities**: What tasks will your agent be able to perform?
- **Tools**: What functions will your agent need to accomplish its tasks?
- **Interactions**: How will users interact with your agent?

### 2. Create a New Agent File

1. Navigate to the appropriate directory:
   - For regular agents: `mosaic/backend/agents/regular/`
   - For supervisor agents: `mosaic/backend/agents/supervisors/`

2. Create a new Python file with a descriptive name:
   ```
   my_new_agent.py
   ```

3. Add a descriptive docstring at the top of the file:
   ```python
   """
   My New Agent Module for MOSAIC

   This module defines an agent that [describe what your agent does].
   It provides [list key capabilities].
   """
   ```

### 3. Install Required Dependencies

If your agent requires external libraries, make sure to install them:

```bash
pip install package1 package2 package3
```

For example, the financial analysis agent requires:

```bash
pip install yfinance pandas numpy
```

### 4. Import Required Modules

Add the necessary imports to your agent file:

```python
import logging
import json
from typing import List, Dict, Any, Optional
# Import any external libraries your agent needs
# For example, for a financial analysis agent:
# import yfinance as yf
# import pandas as pd
# import numpy as np
# from datetime import datetime, timedelta

from langchain_core.language_models import LanguageModelLike
from langchain_core.tools import BaseTool, tool

try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.agents.base import BaseAgent, agent_registry
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.agents.base import BaseAgent, agent_registry

# Configure logging
logger = logging.getLogger("mosaic.agents.my_new_agent")
```

### 4. Define Agent Tools and Helper Functions

Tools are functions that your agent can use to perform tasks. Define them using the `@tool` decorator. You can also create helper functions that aren't directly exposed as tools but support your agent's functionality:

```python
@tool
def my_tool_function(param1: str, param2: int) -> str:
    """
    Description of what this tool does.
    
    Args:
        param1: Description of parameter 1
        param2: Description of parameter 2
        
    Returns:
        A string containing the result
    """
    logger.info(f"Tool function called with params: {param1}, {param2}")
    
    try:
        # Implement your tool logic here
        result = f"Processed {param1} {param2} times"
        
        logger.info(f"Successfully processed: {result}")
        return result
    
    except Exception as e:
        # Log the error
        logger.error(f"Error processing request: {str(e)}")
        
        # Create a detailed error report
        error_report = {
            "task": "My Tool Function",
            "status": "Failed",
            "params": {
                "param1": param1,
                "param2": param2
            },
            "error": str(e),
            "error_type": type(e).__name__
        }
        
        # Return a user-friendly error message
        return f"Error processing request: {json.dumps(error_report, indent=2)}"
```

You can define multiple tools for your agent. Each tool should:
- Have a clear purpose
- Include detailed docstrings
- Handle errors gracefully
- Log important information

#### Helper Functions

You can also create helper functions that aren't directly exposed as tools:

```python
# Helper function not decorated with @tool
def _convert_range_to_period(range_value: str) -> str:
    """
    Convert a range value to a period string.
    
    Args:
        range_value: The range value (1D, 1W, 1M, 3M, 6M, 1Y, 5Y)
        
    Returns:
        A period string
    """
    if range_value == "1D":
        return "1d"
    elif range_value == "1W":
        return "1wk"
    elif range_value == "1M":
        return "1mo"
    # Add more mappings as needed
    else:
        logger.warning(f"Unknown range value: {range_value}, defaulting to 1 month")
        return "1mo"  # Default value
```

#### Different Return Types

Tools can return different types of data:

1. **String Return Type**: Most common, returns formatted text results
   ```python
   @tool
   def get_text_data(param: str) -> str:
       """Return text data."""
       return f"Processed: {param}"
   ```

2. **Dictionary Return Type**: For structured data or visualization
   ```python
   @tool
   def get_chart_data(symbol: str) -> Dict[str, Any]:
       """Return data for chart visualization."""
       return {
           "symbol": symbol,
           "data": [{"date": "2023-01-01", "value": 100}, {"date": "2023-01-02", "value": 105}],
           "type": "line_chart"
       }
   ```

3. **List Return Type**: For collections of items
   ```python
   @tool
   def get_items(count: int) -> List[str]:
       """Return a list of items."""
       return [f"Item {i}" for i in range(count)]
   ```

### 5. Create the Agent Class

Define your agent class by inheriting from `BaseAgent`:

```python
class MyNewAgent(BaseAgent):
    """
    Detailed description of what your agent does.
    
    This agent provides [list capabilities] and can [describe key functions].
    """
    
    def __init__(
        self,
        name: str = "my_new_agent",
        model: Optional[LanguageModelLike] = None,
        tools: List[BaseTool] = None,
        prompt: str = None,
        description: str = None,
        type: str = "Specialized",
        capabilities: List[str] = None,
        icon: str = "🔧",
    ):
        """
        Initialize a new instance of your agent.
        
        Args:
            name: The name of the agent (default: "my_new_agent")
            model: The language model to use for the agent
            tools: Optional list of additional tools
            prompt: Optional system prompt for the agent
            description: Optional description of the agent
            type: The type of agent (default: "Specialized")
            capabilities: List of agent capabilities
            icon: Emoji icon for the agent (default: "🔧")
        """
        # Create the agent tools
        agent_tools = [
            my_tool_function,
            # Add more tools here
        ]
        
        # Combine with any additional tools
        all_tools = agent_tools + (tools or [])
        
        # Default capabilities if none provided
        if capabilities is None:
            capabilities = ["Capability 1", "Capability 2"]
        
        super().__init__(
            name=name,
            model=model,
            tools=all_tools,
            prompt=prompt,
            description=description or "Description of what your agent does",
            type=type,
            capabilities=capabilities,
            icon=icon
        )
        
        logger.debug(f"Initialized agent with {len(all_tools)} tools")
    
    def _get_default_prompt(self) -> str:
        """
        Get the default system prompt for the agent.
        
        Returns:
            A string containing the default system prompt
        """
        return (
            "You are a specialized agent that can [describe what your agent does]. "
            "Your job is to [explain the agent's primary task]. "
            "\n\n"
            "You have tools for [describe tool categories]: "
            "- Use my_tool_function to [describe what this tool does]. "
            # Add more tool descriptions here
            "\n\n"
            "Always work with the actual data provided to you. "
            "If you cannot complete a task, clearly explain why. "
            "Never make up information or hallucinate details. "
            "Always provide clear explanations of your actions and results."
        )
```

### 6. Create the Registration Function

Add a function to register your agent with the agent registry:

```python
def register_my_new_agent(model: LanguageModelLike) -> MyNewAgent:
    """
    Create and register your new agent.
    
    Args:
        model: The language model to use for the agent
        
    Returns:
        The created agent instance
    """
    try:
        # Try importing with the full package path (for local development)
        from mosaic.backend.agents.base import agent_registry
    except ImportError:
        # Fall back to relative import (for Docker environment)
        from backend.agents.base import agent_registry
    
    my_agent = MyNewAgent(model=model)
    agent_registry.register(my_agent)
    return my_agent
```

### 7. (Optional) Create a Supervisor Agent

If you're creating a supervisor agent that coordinates other agents, use this template instead:

```python
def create_my_supervisor(
    model: LanguageModelLike,
    output_mode: str = "full_history"
) -> StateGraph:
    """
    Create a supervisor that coordinates other agents.
    
    Args:
        model: The language model to use for the supervisor
        output_mode: How to handle agent outputs ("full_history" or "last_message")
        
    Returns:
        A StateGraph representing the supervisor workflow
    """
    # Define the agent names to include
    agent_names = ["agent1", "agent2"]
    
    # Create the supervisor prompt
    prompt = (
        "You are a coordinator managing specialized agents:\n"
        "1. agent1: Use for [describe what agent1 does].\n"
        "2. agent2: Use for [describe what agent2 does].\n"
        "\n"
        "Your job is to coordinate these agents to [describe the overall task].\n"
        # Add more detailed instructions here
    )
    
    # Create the supervisor
    logger.info(f"Creating supervisor with agents: {', '.join(agent_names)}")
    
    supervisor = agent_registry.create_supervisor(
        model=model,
        agent_names=agent_names,
        prompt=prompt,
        name="my_supervisor",
        output_mode=output_mode
    )
    
    logger.info("Successfully created supervisor")
    return supervisor.compile()
```

## Testing Your Agent

### 1. Create a Test File

Create a test file in the `mosaic/backend/tests/` directory:

```python
"""
Test module for the new agent.
"""

import unittest
from unittest.mock import MagicMock, patch
import os
import sys

# Import the agent
try:
    from mosaic.backend.agents.regular.my_new_agent import MyNewAgent, my_tool_function
except ImportError:
    from backend.agents.regular.my_new_agent import MyNewAgent, my_tool_function

class TestMyNewAgent(unittest.TestCase):
    """Test cases for the new agent."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock model
        self.mock_model = MagicMock()
        
        # Create an instance of the agent
        self.agent = MyNewAgent(model=self.mock_model)
    
    def test_tool_function(self):
        """Test the tool function."""
        result = my_tool_function("test", 3)
        self.assertEqual(result, "Processed test 3 times")
    
    def test_agent_initialization(self):
        """Test that the agent initializes correctly."""
        self.assertEqual(self.agent.name, "my_new_agent")
        self.assertIsNotNone(self.agent.tools)
        self.assertGreaterEqual(len(self.agent.tools), 1)
    
    def test_agent_invoke(self):
        """Test that the agent can be invoked."""
        # Mock the model's response
        self.mock_model.invoke.return_value = {"content": "Test response"}
        
        # Create a test state
        state = {
            "messages": [
                {"role": "user", "content": "Test message"}
            ]
        }
        
        # Invoke the agent
        result = self.agent.invoke(state)
        
        # Check that the result contains messages
        self.assertIn("messages", result)

if __name__ == "__main__":
    unittest.main()
```

### 2. Run the Tests

Run your tests to ensure your agent works correctly:

```bash
cd mosaic
python -m unittest backend/tests/test_my_new_agent.py
```

## Registering Your Agent

Your agent will be automatically discovered and registered at startup thanks to the agent discovery system. However, you can also manually register it for testing:

```python
from langchain_openai import ChatOpenAI
from mosaic.backend.agents.regular.my_new_agent import register_my_new_agent

# Initialize the model
model = ChatOpenAI(model="gpt-4o-mini")

# Register the agent
my_agent = register_my_new_agent(model)

# Test the agent
result = my_agent.invoke({"messages": [{"role": "user", "content": "Test message"}]})
print(result)
```

## Advanced Agent Features

### 1. Custom Invoke Method

You can override the `invoke` method to add custom logic:

```python
def invoke(self, state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a request and return a response.
    
    This method overrides the default invoke method to add custom logic.
    
    Args:
        state: The current state of the conversation
        
    Returns:
        The updated state with the agent's response
    """
    logger.info("Custom invoke method called")
    
    # Add custom pre-processing logic here
    
    # Call the parent invoke method
    result = super().invoke(state)
    
    # Add custom post-processing logic here
    
    return result
```

### 2. Adding State Management

For agents that need to maintain state between invocations:

```python
def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.state = {}  # Initialize state dictionary

def invoke(self, state: Dict[str, Any]) -> Dict[str, Any]:
    # Update agent state based on input
    user_message = self._get_last_user_message(state)
    if user_message and "reset" in user_message.lower():
        self.state = {}  # Reset state
    
    # Add state to the result
    result = super().invoke(state)
    
    # Store information in state for next invocation
    self.state["last_invocation"] = datetime.now().isoformat()
    
    return result
```

### 3. Handling File Attachments

For agents that process files:

```python
def invoke(self, state: Dict[str, Any]) -> Dict[str, Any]:
    """Process a request with possible file attachments."""
    logger.info("File processing invoke method called")
    
    # Check for attachments in the messages
    messages = state.get("messages", [])
    
    for message in reversed(messages):
        if isinstance(message, dict) and message.get("role") == "user":
            attachments = message.get("attachments", [])
            
            if attachments:
                logger.info(f"Found {len(attachments)} attachments")
                
                # Process the first attachment
                attachment = attachments[0]
                attachment_data = attachment.get("data")
                attachment_filename = attachment.get("filename", "unknown_file")
                attachment_content_type = attachment.get("contentType", "application/octet-stream")
                
                # Process the attachment based on its type
                if attachment_content_type.startswith("image/"):
                    # Process image
                    pass
                elif attachment_content_type == "application/pdf":
                    # Process PDF
                    pass
                # Add more file type handlers as needed
                
                break
    
    # Continue with normal processing
    return super().invoke(state)
```

## Troubleshooting

### Common Issues and Solutions

1. **Agent Not Found**: If your agent isn't being discovered, check:
   - File location (should be in `regular/` or `supervisors/` directory)
   - Registration function name (should start with `register_`)
   - Import paths (should handle both direct and relative imports)

2. **Tool Execution Errors**: If your tools are failing:
   - Check parameter types and validation
   - Add more error handling
   - Improve logging to identify the issue

3. **Model Errors**: If you're getting model-related errors:
   - Verify your API key is set correctly
   - Check model name and parameters
   - Ensure your prompt isn't too long

4. **Integration Issues**: If your agent doesn't work with the rest of the system:
   - Check that your agent inherits from `BaseAgent`
   - Ensure your agent is properly registered
   - Verify that your agent follows the expected interface

## Best Practices

### Code Organization

1. **Modular Design**: Keep tools and agent logic separate
2. **Clear Documentation**: Document all functions, classes, and parameters
3. **Error Handling**: Handle errors gracefully at all levels
4. **Logging**: Use logging to track agent behavior and debug issues

### Agent Design

1. **Single Responsibility**: Each agent should have a clear, focused purpose
2. **Clear Instructions**: Provide detailed instructions in the agent prompt
3. **Robust Tools**: Design tools that handle edge cases and invalid inputs
4. **User-Friendly Responses**: Format responses to be clear and helpful

### Performance

1. **Efficient Processing**: Minimize unnecessary computation
2. **Caching**: Cache results when appropriate
3. **Asynchronous Operations**: Use async for I/O-bound operations
4. **Resource Management**: Close connections and free resources

## Examples

### Example 1: Simple Calculator Agent

```python
"""
Calculator Agent Module for MOSAIC

This module defines a calculator agent that can perform mathematical calculations.
It provides tools for basic arithmetic, algebra, and unit conversion.
"""

import logging
import math
from typing import List, Dict, Any, Optional

from langchain_core.language_models import LanguageModelLike
from langchain_core.tools import BaseTool, tool

try:
    from mosaic.backend.agents.base import BaseAgent, agent_registry
except ImportError:
    from backend.agents.base import BaseAgent, agent_registry

# Configure logging
logger = logging.getLogger("mosaic.agents.calculator")

@tool
def calculate_expression(expression: str) -> str:
    """
    Calculate the result of a mathematical expression.
    
    Args:
        expression: The mathematical expression to evaluate
        
    Returns:
        A string containing the result
    """
    logger.info(f"Calculating expression: {expression}")
    
    try:
        # Create a safe environment for eval
        safe_dict = {
            'abs': abs, 'round': round, 'min': min, 'max': max,
            'sum': sum, 'pow': pow, 'math': math
        }
        
        # Add all math module functions
        for name in dir(math):
            if not name.startswith('_'):
                safe_dict[name] = getattr(math, name)
        
        # Evaluate the expression
        result = eval(expression, {"__builtins__": {}}, safe_dict)
        
        # Format the result
        if isinstance(result, (int, float)):
            if result.is_integer():
                formatted_result = str(int(result))
            else:
                formatted_result = str(result)
        else:
            formatted_result = str(result)
        
        logger.info(f"Calculation result: {formatted_result}")
        return formatted_result
    
    except Exception as e:
        logger.error(f"Error calculating expression: {str(e)}")
        return f"Error: {str(e)}"

class CalculatorAgent(BaseAgent):
    """
    Calculator agent that can perform mathematical calculations.
    
    This agent provides tools for evaluating mathematical expressions,
    solving equations, and performing unit conversions.
    """
    
    def __init__(
        self,
        name: str = "calculator",
        model: Optional[LanguageModelLike] = None,
        tools: List[BaseTool] = None,
        prompt: str = None,
        description: str = None,
        type: str = "Utility",
        capabilities: List[str] = None,
        icon: str = "🧮",
    ):
        """
        Initialize a new calculator agent.
        
        Args:
            name: The name of the agent (default: "calculator")
            model: The language model to use for the agent
            tools: Optional list of additional tools
            prompt: Optional system prompt for the agent
            description: Optional description of the agent
            type: The type of agent (default: "Utility")
            capabilities: List of agent capabilities
            icon: Emoji icon for the agent (default: "🧮")
        """
        # Create the calculator tools
        calculator_tools = [
            calculate_expression
        ]
        
        # Combine with any additional tools
        all_tools = calculator_tools + (tools or [])
        
        # Default capabilities if none provided
        if capabilities is None:
            capabilities = ["Mathematical Calculations", "Expression Evaluation"]
        
        super().__init__(
            name=name,
            model=model,
            tools=all_tools,
            prompt=prompt,
            description=description or "Calculator Agent for performing mathematical calculations",
            type=type,
            capabilities=capabilities,
            icon=icon
        )
        
        logger.debug(f"Initialized calculator agent with {len(all_tools)} tools")
    
    def _get_default_prompt(self) -> str:
        """
        Get the default system prompt for the calculator agent.
        
        Returns:
            A string containing the default system prompt
        """
        return (
            "You are a calculator assistant that can perform mathematical calculations. "
            "Your job is to solve mathematical problems and evaluate expressions. "
            "\n\n"
            "You have tools for calculations: "
            "- Use calculate_expression to evaluate mathematical expressions. "
            "\n\n"
            "Always show your work and explain your calculations. "
            "If you cannot solve a problem, clearly explain why. "
            "Never make up information or hallucinate details. "
            "Always provide clear explanations of your calculations and results."
        )

def register_calculator_agent(model: LanguageModelLike) -> CalculatorAgent:
    """
    Create and register a calculator agent.
    
    Args:
        model: The language model to use for the agent
        
    Returns:
        The created calculator agent
    """
    try:
        from mosaic.backend.agents.base import agent_registry
    except ImportError:
        from backend.agents.base import agent_registry
    
    calculator = CalculatorAgent(model=model)
    agent_registry.register(calculator)
    return calculator
```

### Example 2: File Processing Supervisor

```python
"""
File Processing Supervisor Agent Module for MOSAIC

This module defines a file processing supervisor agent that orchestrates file processing.
It determines the file type and routes processing to specialized agents.
"""

import logging
from typing import List, Dict, Any, Optional

from langchain_core.language_models import LanguageModelLike
from langgraph.graph import StateGraph

try:
    from mosaic.backend.agents.base import agent_registry
except ImportError:
    from backend.agents.base import agent_registry

# Configure logging
logger = logging.getLogger("mosaic.agents.file_processing_supervisor")

def create_file_processing_supervisor(
    model: LanguageModelLike,
    output_mode: str = "full_history"
) -> StateGraph:
    """
    Create a file processing supervisor that orchestrates file processing agents.
    
    This function creates a supervisor that can determine file types and route
    processing to specialized agents like the Excel processing agent.
    
    Args:
        model: The language model to use for the supervisor
        output_mode: How to handle agent outputs ("full_history" or "last_message")
        
    Returns:
        A StateGraph representing the supervisor workflow
    """
    # Make sure all required agents are registered
    try:
        from mosaic.backend.agents.regular.file_processing import register_file_processing_agent
    except ImportError:
        from backend.agents.regular.file_processing import register_file_processing_agent
    
    # Register file processing agent if it doesn't exist
    file_processing = agent_registry.get("file_processing")
    if file_processing is None:
        logger.info("File processing agent not found in registry, registering it now")
        file_processing = register_file_processing_agent(model)
    
    # Define the agent names to include
    agent_names = ["file_processing"]
    
    # Create the file processing supervisor prompt
    prompt = (
        "You are a file processing coordinator managing specialized file processing agents:\n"
        "1. file_processing: Use for processing Excel (XLSX) files, extracting data, and performing analysis.\n"
        "\n"
        "Your job is to coordinate file processing based on the file type. When a user uploads a file, "
        "you should determine the file type and route it to the appropriate agent for processing. "
        "Currently, you can process Excel files, but more file types will be added in the future.\n"
        "\n"
        "IMPORTANT: When a user uploads a file or mentions a file, you should IMMEDIATELY use the transfer_to_file_processing tool "
        "to hand off the request to the file_processing agent.\n"
        "\n"
        "Important rules:\n"
        "- Always check the file type before processing\n"
        "- For Excel files, use the file_processing agent by calling transfer_to_file_processing\n"
        "- For unsupported file types, clearly explain that the file type is not yet supported\n"
        "- Never make up information or hallucinate details\n"
        "- Provide clear explanations of the data and analysis results\n"
    )
    
    # Create the supervisor
    logger.info(f"Creating file processing supervisor with agents: {', '.join(agent_names)}")
    
    supervisor = agent_registry.create_supervisor(
        model=model,
        agent_names=agent_names,
        prompt=prompt,
        name="file_processing_supervisor",
        output_mode=output_mode
    )
    
    logger.info("Successfully created file processing supervisor")
    return supervisor.compile()
```

## Conclusion

Creating a new agent in Mosaic involves defining tools, creating an agent class, and registering the agent with the system. By following this guide, you can create powerful, specialized agents that extend the capabilities of the Mosaic framework.

Remember to:
- Define a clear purpose for your agent
- Create robust tools with good error handling
- Write comprehensive tests
- Document your code thoroughly
- Follow best practices for agent design

With these principles in mind, you can create agents that provide valuable functionality to users of the Mosaic system.
