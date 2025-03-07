# Creating Your Own Agents in MOSAIC

This guide will walk you through the process of creating your own agents in MOSAIC. We'll keep it simple and beginner-friendly, focusing on the practical steps rather than complex technical details.

## What You'll Learn

- How to create a basic agent
- How to add tools to your agent
- How to register your agent with MOSAIC
- How to test your agent

## Prerequisites

Before you start, make sure you have:

- MOSAIC up and running (see the [Quickstart Guide](../../QUICKSTART.md))
- Basic knowledge of Python
- Your favorite code editor open

## Understanding Agents

In MOSAIC, an agent is a specialized AI assistant that can perform specific tasks. Agents can:

- Chat with users
- Use tools to perform actions
- Process and analyze data
- Work together with other agents

## Creating a Basic Agent

Let's create a simple "Hello World" agent that responds to greetings.

### Step 1: Create a New File

Create a new Python file in the `mosaic/backend/agents/regular` directory. Let's call it `hello_agent.py`.

### Step 2: Import Required Modules

Add these imports at the top of your file:

```python
from mosaic.backend.agents.base import BaseAgent
from langchain_core.tools import tool
import logging

# Configure logging
logger = logging.getLogger("mosaic.agents.hello_agent")
```

### Step 3: Create a Tool

Tools are functions that your agent can use to perform actions. Let's create a simple greeting tool:

```python
@tool
def greeting_tool(name: str = "World") -> str:
    """
    Returns a friendly greeting.
    
    Args:
        name: The name to greet (default: "World")
        
    Returns:
        A greeting message
    """
    return f"Hello, {name}! Nice to meet you!"
```

### Step 4: Create the Agent Class

Now, let's create the agent class:

```python
class HelloAgent(BaseAgent):
    """
    A simple agent that greets users.
    """
    
    def __init__(self, name, model, tools=None, prompt=None):
        # Add our greeting tool to any tools passed in
        agent_tools = [greeting_tool]
        if tools:
            agent_tools.extend(tools)
            
        # Initialize the base agent
        super().__init__(name, model, agent_tools, prompt)
    
    def _get_default_prompt(self) -> str:
        """
        Returns the default prompt for the agent.
        """
        return """You are a friendly greeting agent. Your job is to welcome users and make them feel comfortable.
        
When a user greets you, respond warmly and ask how you can help them today.

You have access to the following tools:
- greeting_tool: Use this to generate a personalized greeting for the user.

Always be polite, friendly, and helpful!
"""
```

### Step 5: Create the Registration Function

MOSAIC uses a registration function to discover and initialize your agent:

```python
def register_hello_agent(model):
    """
    Register the hello agent.
    
    Args:
        model: The language model to use
        
    Returns:
        The initialized agent
    """
    logger.info("Registering hello agent")
    agent = HelloAgent("hello_agent", model)
    return agent
```

### Step 6: Put It All Together

Your complete `hello_agent.py` file should look like this:

```python
from mosaic.backend.agents.base import BaseAgent
from langchain_core.tools import tool
import logging

# Configure logging
logger = logging.getLogger("mosaic.agents.hello_agent")

@tool
def greeting_tool(name: str = "World") -> str:
    """
    Returns a friendly greeting.
    
    Args:
        name: The name to greet (default: "World")
        
    Returns:
        A greeting message
    """
    return f"Hello, {name}! Nice to meet you!"

class HelloAgent(BaseAgent):
    """
    A simple agent that greets users.
    """
    
    def __init__(self, name, model, tools=None, prompt=None):
        # Add our greeting tool to any tools passed in
        agent_tools = [greeting_tool]
        if tools:
            agent_tools.extend(tools)
            
        # Initialize the base agent
        super().__init__(name, model, agent_tools, prompt)
    
    def _get_default_prompt(self) -> str:
        """
        Returns the default prompt for the agent.
        """
        return """You are a friendly greeting agent. Your job is to welcome users and make them feel comfortable.
        
When a user greets you, respond warmly and ask how you can help them today.

You have access to the following tools:
- greeting_tool: Use this to generate a personalized greeting for the user.

Always be polite, friendly, and helpful!
"""

def register_hello_agent(model):
    """
    Register the hello agent.
    
    Args:
        model: The language model to use
        
    Returns:
        The initialized agent
    """
    logger.info("Registering hello agent")
    agent = HelloAgent("hello_agent", model)
    return agent
```

## Testing Your Agent

### Restart MOSAIC

After creating your agent, restart the MOSAIC backend to discover and register your new agent:

1. Stop the running backend server (press Ctrl+C in the terminal)
2. Start it again:
   ```
   python -m uvicorn mosaic.backend.app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Use Your Agent

1. Open your browser and go to http://localhost:3000
2. You should see your new "hello_agent" in the sidebar
3. Click on it to start a conversation
4. Try saying "Hello" or "Hi, my name is [your name]"

## Creating More Advanced Agents

Once you're comfortable with the basics, you can create more advanced agents:

### Adding More Tools

Tools are the key to making your agent useful. Here's an example of a more complex tool:

```python
@tool
def weather_tool(city: str) -> str:
    """
    Get the current weather for a city.
    
    Args:
        city: The city to get weather for
        
    Returns:
        A weather report
    """
    # In a real implementation, you would call a weather API here
    # For this example, we'll just return a mock response
    return f"The weather in {city} is currently sunny and 72°F (22°C)."
```

### Using External APIs

Many tools will need to call external APIs. Here's a simple example using the `requests` library:

```python
import requests

@tool
def get_joke_tool() -> str:
    """
    Get a random joke from an API.
    
    Returns:
        A joke
    """
    try:
        response = requests.get("https://official-joke-api.appspot.com/random_joke")
        data = response.json()
        return f"{data['setup']} {data['punchline']}"
    except Exception as e:
        return f"Sorry, I couldn't get a joke right now: {str(e)}"
```

### Creating a Supervisor Agent

Supervisor agents can coordinate multiple specialized agents. Here's a simplified example:

```python
from mosaic.backend.agents.base import create_multi_agent_supervisor

def register_greeting_supervisor(model):
    """
    Register a supervisor that coordinates the hello agent and joke agent.
    """
    supervisor = create_multi_agent_supervisor(
        model=model,
        name="greeting_supervisor",
        agent_names=["hello_agent", "joke_agent"],
        prompt="""You are a supervisor that coordinates between a greeting agent and a joke agent.
        
If the user wants a greeting, delegate to the hello_agent.
If the user wants a joke, delegate to the joke_agent.
If you're not sure, ask clarifying questions.
"""
    )
    return supervisor
```

## Best Practices

1. **Keep Tools Simple**: Each tool should do one thing well
2. **Handle Errors Gracefully**: Always include error handling in your tools
3. **Use Descriptive Names**: Make your agent and tool names clear and descriptive
4. **Document Everything**: Add good docstrings to your classes and functions
5. **Test Thoroughly**: Test your agent with different inputs before deploying

## Common Pitfalls

1. **Using Instance Methods as Tools**: Always define tools as standalone functions with the `@tool` decorator
2. **Missing Error Handling**: Tools should handle errors gracefully and return meaningful messages
3. **Overly Complex Prompts**: Keep your agent prompts clear and focused
4. **Forgetting to Register**: Make sure your registration function starts with `register_`

## Next Steps

- Study the existing agents in the `mosaic/backend/agents/regular` directory
- Try modifying your agent to add more capabilities
- Experiment with different prompts to see how they affect your agent's behavior
- Create a supervisor agent that coordinates multiple agents
- Create a [custom UI for your agent](CREATING_AGENT_UIS.md) to visualize data

Happy agent building!
