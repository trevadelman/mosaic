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

from backend.agents import (
    register_calculator_agent,
    create_calculator_supervisor
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("mosaic.agent_runner")

# Load environment variables
load_dotenv()

def main():
    """Run the agent system."""
    logger.info("Starting MOSAIC Agent Runner")
    
    # Check if the OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("Please set your OPENAI_API_KEY in the .env file")
        return
    
    # Initialize the language model
    logger.info("Initializing language model")
    model = ChatOpenAI(model="gpt-4o-mini")
    
    # Create the calculator agent
    logger.info("Creating calculator agent")
    calculator = register_calculator_agent(model)
    
    # Create the calculator supervisor
    logger.info("Creating calculator supervisor")
    supervisor = create_calculator_supervisor(model)
    
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
