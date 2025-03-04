"""
Test_db_agent Agent Module for MOSAIC

A test agent for database-driven metadata
"""

import logging
from typing import List, Dict, Any, Optional

from langchain_core.language_models import LanguageModelLike
from langchain_core.tools import BaseTool, tool

try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.agents.base import BaseAgent, agent_registry
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.agents.base import BaseAgent, agent_registry

# Import tool dependencies


# Configure logging
logger = logging.getLogger("mosaic.agents.test_db_agent")



@tool
def test_tool(param1: str) -> str:
    """
    A test tool.
    
    Args:
        param1: A test parameter
        
    Returns:
        A test return value
    """
    return f"Test tool called with param1={param1}"



class TestdbagentAgent(BaseAgent):
    """
    A test agent for database-driven metadata
    """
    
    def __init__(
        self,
        name: str = "test_db_agent",
        model: Optional[LanguageModelLike] = None,
        tools: List[BaseTool] = None,
        prompt: str = None,
        description: str = None,
    ):
        """
        Initialize a new Test_db_agent agent.
        
        Args:
            name: The name of the agent (default: "test_db_agent")
            model: The language model to use for the agent
            tools: Optional list of additional tools
            prompt: Optional system prompt for the agent
            description: Optional description of the agent
        """
        # Define the agent's tools
        agent_tools = [
            test_tool
        ]
        
        # Combine with any additional tools
        all_tools = agent_tools + (tools or [])
        
        super().__init__(
            name=name,
            model=model,
            tools=all_tools,
            prompt=prompt,
            description=description or "A test agent for database-driven metadata"
        )
        
        logger.info(f"Initialized test_db_agent agent with {len(all_tools)} tools")
    
    def _get_default_prompt(self) -> str:
        """
        Get the default system prompt for the test_db_agent agent.
        
        Returns:
            A string containing the default system prompt
        """
        return """You are a test agent for database-driven metadata."""


def register_test_db_agent_agent(model: LanguageModelLike) -> TestdbagentAgent:
    """
    Create and register a test_db_agent agent.
    
    Args:
        model: The language model to use for the agent
        
    Returns:
        The created test_db_agent agent
    """
    try:
        # Try importing with the full package path (for local development)
        from mosaic.backend.agents.base import agent_registry
    except ImportError:
        # Fall back to relative import (for Docker environment)
        from backend.agents.base import agent_registry
    
    test_db_agent_agent = TestdbagentAgent(model=model)
    agent_registry.register(test_db_agent_agent)
    return test_db_agent_agent
