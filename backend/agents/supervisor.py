"""
Supervisor Agent Module for MOSAIC

This module defines a supervisor agent that can orchestrate other agents.
It serves as an example of how to create a supervisor that can leverage specialized agents.
"""

import logging
from typing import List, Dict, Any, Optional

from langchain_core.language_models import LanguageModelLike
from langgraph.graph import StateGraph

try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.agents.base import agent_registry
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.agents.base import agent_registry

# Configure logging
logger = logging.getLogger("mosaic.agents.supervisor")

def create_calculator_supervisor(
    model: LanguageModelLike,
    output_mode: str = "last_message"
) -> StateGraph:
    """
    Create a supervisor agent that can use the calculator agent.
    
    This function creates a supervisor that can orchestrate the calculator agent
    to solve mathematical problems.
    
    Args:
        model: The language model to use for the supervisor
        output_mode: How to handle agent outputs ("full_history" or "last_message")
        
    Returns:
        A StateGraph representing the supervisor workflow
    """
    # Make sure the calculator agent is registered
    try:
        # Try importing with the full package path (for local development)
        from mosaic.backend.agents.calculator import register_calculator_agent
    except ImportError:
        # Fall back to relative import (for Docker environment)
        from backend.agents.calculator import register_calculator_agent
    
    calculator = agent_registry.get("calculator")
    if calculator is None:
        logger.info("Calculator agent not found in registry, registering it now")
        calculator = register_calculator_agent(model)
    
    # Create the supervisor
    logger.info("Creating calculator supervisor")
    supervisor = agent_registry.create_supervisor(
        model=model,
        agent_names=["calculator"],
        prompt=(
            "You are a helpful assistant that can solve mathematical problems. "
            "You have access to a calculator agent that can perform basic mathematical operations. "
            "When a user asks a mathematical question, delegate the calculation to the calculator agent. "
            "\n\n"
            "IMPORTANT: Always use the calculator agent's tools for calculations. "
            "For simple calculations like addition, subtraction, multiplication, and division, "
            "use the calculator agent's specific tools (add_tool, subtract_tool, multiply_tool, divide_tool). "
            "For example, to calculate 5 + 5, transfer to the calculator agent and use the add_tool with arguments a=5 and b=5. "
            "For more complex expressions, use the parse_expression_tool. "
            "\n\n"
            "Always explain the steps and reasoning behind the calculations. "
            "If the calculator agent encounters an error, explain the issue to the user in simple terms."
        ),
        name="calculator_supervisor",
        output_mode=output_mode
    )
    
    logger.info("Successfully created calculator supervisor")
    return supervisor.compile()

def create_multi_agent_supervisor(
    model: LanguageModelLike,
    agent_names: List[str] = None,
    prompt: str = None,
    name: str = "supervisor",
    output_mode: str = "last_message"
) -> StateGraph:
    """
    Create a supervisor agent that can orchestrate multiple agents.
    
    This function creates a supervisor that can orchestrate multiple specialized agents
    to solve complex problems.
    
    Args:
        model: The language model to use for the supervisor
        agent_names: List of agent names to include (defaults to all registered agents)
        prompt: System prompt for the supervisor
        name: The name of the supervisor (default: "supervisor")
        output_mode: How to handle agent outputs ("full_history" or "last_message")
        
    Returns:
        A StateGraph representing the supervisor workflow
    """
    # Use all registered agents if none specified
    if agent_names is None:
        agent_names = agent_registry.list_agents()
    
    # Create a default prompt if none provided
    if prompt is None:
        agent_descriptions = []
        for agent_name in agent_names:
            agent = agent_registry.get(agent_name)
            if agent is not None:
                agent_descriptions.append(f"- {agent_name}: {agent.description}")
        
        agents_text = "\n".join(agent_descriptions)
        prompt = (
            f"You are a supervisor agent that coordinates multiple specialized agents:\n"
            f"{agents_text}\n\n"
            f"Your job is to understand user requests and delegate tasks to the appropriate agent. "
            f"Break down complex problems into smaller tasks that can be handled by individual agents. "
            f"Synthesize the information from different agents to provide a comprehensive response. "
            f"If an agent fails to complete a task, try a different approach or agent. "
            f"Always provide clear explanations and reasoning for your decisions."
        )
    
    # Create the supervisor
    logger.info(f"Creating multi-agent supervisor with agents: {', '.join(agent_names)}")
    supervisor = agent_registry.create_supervisor(
        model=model,
        agent_names=agent_names,
        prompt=prompt,
        name=name,
        output_mode=output_mode
    )
    
    logger.info(f"Successfully created multi-agent supervisor '{name}'")
    return supervisor.compile()
