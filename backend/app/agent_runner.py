"""
Agent Runner Module for MOSAIC

This module runs the agent system in a separate process from the main API server.
It initializes the agents and makes them available to the API server.
"""

import os
import logging
import time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("mosaic.agent_runner")

# Import the agent discovery module
from app.agent_discovery import discover_and_register_agents

# Import specific agents that need special handling
from backend.agents import create_calculator_supervisor

# Load environment variables
load_dotenv()

# Global variable to store initialized agents
initialized_agents = {}

def initialize_agents():
    """Initialize all agents and make them available globally."""
    global initialized_agents
    
    # Check if the OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("Please set your OPENAI_API_KEY in the .env file")
        return {}
    
    # Initialize the language model
    logger.info("Initializing language model")
    model = ChatOpenAI(model="gpt-4o-mini")
    
    # Discover and register all agents
    logger.info("Discovering and registering agents")
    discovered_agents = discover_and_register_agents(model)
    initialized_agents.update(discovered_agents)
    
    # Create the calculator supervisor (special case)
    logger.info("Creating calculator supervisor")
    supervisor = create_calculator_supervisor(model)
    initialized_agents["research_supervisor"] = supervisor
    
    logger.info(f"Initialized {len(initialized_agents)} agents: {', '.join(initialized_agents.keys())}")
    
    return initialized_agents

def get_initialized_agents():
    """Get the dictionary of initialized agents."""
    return initialized_agents

def main():
    """Run the agent system."""
    logger.info("Starting MOSAIC Agent Runner")
    
    # Initialize all agents
    initialize_agents()
    
    logger.info("Agent system initialized and ready")
    
    # Keep the process running
    try:
        while True:
            time.sleep(60)
            logger.info("Agent system is running")
    except KeyboardInterrupt:
        logger.info("Agent system shutting down")

if __name__ == "__main__":
    main()
