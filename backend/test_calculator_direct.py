"""
Direct test script for the calculator agent.

This script tests the calculator agent directly without using the supervisor.
"""

import os
import logging
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from mosaic.backend.agents import register_calculator_agent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("mosaic.test_calculator_direct")

# Load environment variables
load_dotenv()

def main():
    """Run the direct calculator agent test."""
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
    
    # Create the agent
    agent = calculator.create()
    
    # Initialize the conversation state
    state = {"messages": []}
    
    print("\nDirect Calculator Agent Test")
    print("---------------------------")
    print("This test directly uses the calculator agent without a supervisor.")
    print("\nExample queries:")
    print("- 'What is 5 + 5?'")
    print("- 'Calculate 15 * 7'")
    print("\nType 'exit' to quit.")
    print("---------------------------\n")
    
    while True:
        # Get user input
        user_input = input("\nYou: ")
        if user_input.lower() == 'exit':
            break
        
        # Add the user message to the state
        user_message = {"role": "user", "content": user_input}
        state["messages"].append(user_message)
        
        # Invoke the agent
        logger.info(f"Processing query: {user_input}")
        result = agent.invoke(state)
        
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
