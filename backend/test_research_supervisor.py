"""
Test script for the Research Supervisor Agent

This script demonstrates the capabilities of the research supervisor agent,
which orchestrates multiple specialized agents to perform comprehensive research tasks.
"""

import os
import logging
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("mosaic.test_research_supervisor")

# Load environment variables from .env file
load_dotenv()

# Check if the OpenAI API key is set
if not os.getenv("OPENAI_API_KEY"):
    print("Please set your OPENAI_API_KEY in the .env file")
    exit(1)

def main():
    """Run the research supervisor test."""
    print("Research Supervisor Agent Test")
    print("-----------------------------")
    print("This test demonstrates the capabilities of the research supervisor agent,")
    print("which orchestrates multiple specialized agents:")
    print("1. Web Search Agent - Searches the web and retrieves webpage content")
    print("2. Browser Interaction Agent - Handles JavaScript-heavy websites")
    print("3. Data Processing Agent - Extracts and normalizes product information")
    print("4. Literature Agent - Searches for academic papers and articles")
    print("\nExample queries:")
    print("- 'Research the latest iPhone model and its features'")
    print("- 'Find information about Tesla's newest electric vehicle'")
    print("- 'Research academic papers on machine learning for image recognition'")
    print("- 'Compare features of top gaming laptops'")
    print("\nType 'exit' to quit.")
    print("-----------------------------\n")
    
    # Initialize the language model
    model = ChatOpenAI(model="gpt-4o-mini")
    
    # Import the research supervisor
    try:
        # Try importing with the full package path (for local development)
        from mosaic.backend.agents.supervisor import create_research_supervisor
    except ImportError:
        # Fall back to relative import (for Docker environment)
        from backend.agents.supervisor import create_research_supervisor
    
    # Create the research supervisor
    logger.info("Creating research supervisor...")
    research_supervisor = create_research_supervisor(model)
    logger.info("Research supervisor created successfully")
    
    # Initialize the conversation state
    state = {"messages": []}
    
    while True:
        # Get user input
        user_input = input("\nYou: ")
        if user_input.lower() == 'exit':
            break
        
        # Add the user message to the state
        user_message = {"role": "user", "content": user_input}
        state["messages"].append(user_message)
        
        print("\nResearching... (this may take some time depending on the complexity of the query)")
        logger.info(f"Research Supervisor: Starting research for query: '{user_input}'")
        
        try:
            # Invoke the research supervisor
            logger.info(f"Invoking research supervisor...")
            result = research_supervisor.invoke(state)
            logger.info(f"Research supervisor completed processing")
            
            # Update the state with the result
            state = result
            
            # Print the agent responses
            for message in result["messages"]:
                # Skip user messages
                if (isinstance(message, dict) and message.get("role") == "user") or \
                   (hasattr(message, "type") and message.type == "human"):
                    continue
                
                # Log agent responses
                if hasattr(message, "name") and message.name:
                    logger.info(f"Response from {message.name}")
                    print(f"\n{message.name}: {message.content}")
                elif hasattr(message, "content"):
                    logger.info(f"Response from Assistant")
                    print(f"\nAssistant: {message.content}")
                elif isinstance(message, dict) and "content" in message:
                    logger.info(f"Response from Assistant")
                    print(f"\nAssistant: {message['content']}")
                    
            logger.info(f"Research completed successfully")
            
        except Exception as e:
            logger.error(f"Error in research process: {str(e)}")
            print(f"\nError: An error occurred while processing your request: {str(e)}")

if __name__ == "__main__":
    main()
