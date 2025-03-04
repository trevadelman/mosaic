"""
Test script for the calculator agent and supervisor.

This script demonstrates how to use the calculator agent and supervisor
to perform basic mathematical operations.
"""

import os
import logging
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.agents.regular.calculator import register_calculator_agent
    from mosaic.backend.agents.supervisors.research_assistant import create_calculator_supervisor
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.agents.regular.calculator import register_calculator_agent
    from backend.agents.supervisors.research_assistant import create_calculator_supervisor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("mosaic.test_calculator")

# Load environment variables
load_dotenv()

def main():
    """Run the calculator agent test."""
    # Check if the OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("Please set your OPENAI_API_KEY in the .env file")
        return
    
    # Initialize the language model
    logger.info("Initializing language model")
    model = ChatOpenAI(model="gpt-4o-mini")
    
    # Create the calculator supervisor
    logger.info("Creating calculator supervisor")
    supervisor = create_calculator_supervisor(model)
    
    # Initialize the conversation state
    state = {"messages": []}
    
    print("\nCalculator Agent Test")
    print("--------------------")
    print("This test demonstrates how to use the calculator agent and supervisor")
    print("to perform basic mathematical operations.")
    print("\nExample queries:")
    print("- 'What is 123 + 456?'")
    print("- 'Calculate 15 * 7 - 3'")
    print("- 'What is the square root of 144?'")
    print("- 'Solve (10 + 5) * 3 / 2'")
    print("\nType 'exit' to quit.")
    print("--------------------\n")
    
    while True:
        # Get user input
        user_input = input("\nYou: ")
        if user_input.lower() == 'exit':
            break
        
        # Add the user message to the state
        user_message = {"role": "user", "content": user_input}
        state["messages"].append(user_message)
        
        # Invoke the supervisor
        logger.info(f"Processing query: {user_input}")
        result = supervisor.invoke(state)
        
        # Update the state with the result
        state = result
        
        # Print the agent responses
        for message in result["messages"]:
            # Skip user messages
            if hasattr(message, "type") and message.type == "human":
                continue
            
            # Print the message content
            if hasattr(message, "name") and message.name:
                print(f"\n{message.name}: {message.content}")
            else:
                print(f"\nAssistant: {message.content}")

if __name__ == "__main__":
    main()
