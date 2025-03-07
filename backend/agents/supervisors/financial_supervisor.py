"""
Financial Supervisor Agent Module for MOSAIC

This module defines a financial supervisor agent that can orchestrate the financial analysis agent
and provide a comprehensive financial analysis experience.
"""

import logging
from typing import List, Dict, Any, Optional

from langchain_core.language_models import LanguageModelLike
from langgraph.graph import StateGraph

try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.agents.base import agent_registry
    from mosaic.backend.agents.regular.financial_analysis import register_financial_analysis_agent
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.agents.base import agent_registry
    from backend.agents.regular.financial_analysis import register_financial_analysis_agent

# Configure logging
logger = logging.getLogger("mosaic.agents.financial_supervisor")


def create_financial_supervisor(
    model: LanguageModelLike,
    output_mode: str = "full_history"
) -> StateGraph:
    """
    Create a financial supervisor that orchestrates the financial analysis agent.
    
    This function creates a supervisor that can orchestrate the financial analysis agent
    to perform comprehensive financial analysis tasks.
    
    Args:
        model: The language model to use for the supervisor
        output_mode: How to handle agent outputs ("full_history" or "last_message")
        
    Returns:
        A StateGraph representing the supervisor workflow
    """
    # Make sure the financial analysis agent is registered
    financial_analysis = agent_registry.get("financial_analysis")
    if financial_analysis is None:
        logger.info("Financial analysis agent not found in registry, registering it now")
        financial_analysis = register_financial_analysis_agent(model)
    
    # Define the agent names to include
    agent_names = ["financial_analysis"]
    
    # Create the financial supervisor prompt
    prompt = (
        "You are a financial advisor managing a specialized financial analysis agent:\n"
        "1. financial_analysis: Use for stock price analysis, technical indicators, company information, and stock comparison.\n"
        "\n"
        "Your job is to coordinate this agent to provide comprehensive financial analysis and insights. "
        "Break down financial analysis tasks and delegate to the financial analysis agent. "
        "Synthesize the information it provides into a coherent response.\n"
        "\n"
        "Important rules:\n"
        "- When analyzing stocks, use the financial analysis agent to get both technical and fundamental data.\n"
        "- For technical analysis, make sure to get multiple indicators (SMA, EMA, MACD, RSI, Bollinger Bands).\n"
        "- For fundamental analysis, get company information, financial metrics, and compare with similar companies.\n"
        "- When comparing stocks, use the stock comparison tool to get a side-by-side comparison of key metrics.\n"
        "- Only use factual information retrieved by the agent.\n"
        "- If information cannot be found after trying all possible approaches, clearly state that and explain why.\n"
        "- Never make up information or hallucinate details.\n"
        "- Provide clear error reports when the agent fails, but always try alternative approaches.\n"
        "- Always attribute information to its source.\n"
        "- Remember that past performance is not indicative of future results, and include appropriate disclaimers.\n"
        "- Do not provide specific investment advice or recommendations.\n"
        "\n"
        "You also have access to a custom UI component for visualizing stock data. "
        "When a user asks about a specific stock or wants to compare multiple stocks, "
        "you can suggest opening the stock chart UI component to visualize the data. "
        "The UI component is available through a button that will be displayed in the chat interface."
    )
    
    # Create the supervisor
    logger.info(f"Creating financial supervisor with agents: {', '.join(agent_names)}")
    supervisor = agent_registry.create_supervisor(
        model=model,
        agent_names=agent_names,
        prompt=prompt,
        name="financial_supervisor",
        output_mode=output_mode
    )
    
    logger.info("Successfully created financial supervisor")
    return supervisor.compile()
