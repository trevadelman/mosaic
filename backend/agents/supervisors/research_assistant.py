"""
Research Assistant Agent Module for MOSAIC

This module defines research assistant agents that can orchestrate other specialized agents.
It provides examples of how to create research assistants that can leverage specialized agents
for tasks like web search, browser interaction, data processing, and literature research.
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
logger = logging.getLogger("mosaic.agents.research_assistant")


def create_research_supervisor(
    model: LanguageModelLike,
    output_mode: str = "full_history"
) -> StateGraph:
    """
    Create a research supervisor that orchestrates multiple agents for research tasks.
    
    This function creates a supervisor that can orchestrate web search, browser interaction,
    data processing, and literature agents to perform comprehensive research tasks.
    
    Args:
        model: The language model to use for the supervisor
        output_mode: How to handle agent outputs ("full_history" or "last_message")
        
    Returns:
        A StateGraph representing the supervisor workflow
    """
    # Make sure all required agents are registered
    try:
        # Try importing with the full package path (for local development)
        from mosaic.backend.agents.regular.web_search import register_web_search_agent
        from mosaic.backend.agents.regular.browser_interaction import register_browser_interaction_agent
        from mosaic.backend.agents.regular.literature import register_literature_agent
    except ImportError:
        # Fall back to relative import (for Docker environment)
        from backend.agents.regular.web_search import register_web_search_agent
        from backend.agents.regular.browser_interaction import register_browser_interaction_agent
        from backend.agents.regular.literature import register_literature_agent
    
    # Register agents if they don't exist
    web_search = agent_registry.get("web_search")
    if web_search is None:
        logger.info("Web search agent not found in registry, registering it now")
        web_search = register_web_search_agent(model)
    
    browser_interaction = agent_registry.get("browser_interaction")
    if browser_interaction is None:
        logger.info("Browser interaction agent not found in registry, registering it now")
        browser_interaction = register_browser_interaction_agent(model)
    

    
    literature = agent_registry.get("literature")
    if literature is None:
        logger.info("Literature agent not found in registry, registering it now")
        literature = register_literature_agent(model)
    
    # Define the agent names to include
    agent_names = ["web_search", "browser_interaction", "data_processing", "literature"]
    
    # Create the research supervisor prompt
    prompt = (
        "You are a research coordinator managing a team of specialized agents:\n"
        "1. web_search: Use for general web searches and simple webpage content retrieval.\n"
        "2. browser_interaction: Use for JavaScript-heavy websites that require browser rendering.\n"
        "3. data_processing: Use to extract and normalize product information from raw content.\n"
        "4. literature: Use to find academic papers and articles related to products or technologies.\n"
        "\n"
        "Your job is to coordinate these agents to gather comprehensive information about products, "
        "technologies, or companies. Break down research tasks and delegate to the appropriate agent. "
        "Synthesize the information they provide into a coherent response.\n"
        "\n"
        "Important rules:\n"
        "- When searching for current or latest information, avoid using specific years or dates in search queries. "
        "  Instead, use terms like 'latest', 'newest', or 'current' to ensure you get the most up-to-date information.\n"
        "- Exhaust all available tools and agents before giving up on a task. If one agent fails, try another approach. "
        "  For example, if browser_interaction fails to access a website directly, use web_search to search for "
        "  information about the same topic from other sources. Always try multiple approaches to solve a problem.\n"
        "- Only use factual information retrieved by the agents.\n"
        "- If information cannot be found after trying all possible approaches, clearly state that and explain why.\n"
        "- Never make up information or hallucinate details.\n"
        "- Provide clear error reports when agents fail, but always try alternative approaches.\n"
        "- Always attribute information to its source."
    )
    
    # Create the supervisor
    logger.info(f"Creating research supervisor with agents: {', '.join(agent_names)}")
    supervisor = agent_registry.create_supervisor(
        model=model,
        agent_names=agent_names,
        prompt=prompt,
        name="research_supervisor",
        output_mode=output_mode
    )
    
    logger.info("Successfully created research supervisor")
    return supervisor.compile()

