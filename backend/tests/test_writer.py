"""
Test script for the writer agent.

This script demonstrates how to use the writer agent to perform file operations
with security boundaries.
"""

import os
import logging
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.agents.writer import register_writer_agent, read_file_tool, write_file_tool, list_files_tool
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.agents.writer import register_writer_agent, read_file_tool, write_file_tool, list_files_tool

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("mosaic.test_writer")

# Load environment variables
load_dotenv()

def main():
    """Run the writer agent test."""
    # Check if the OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("Please set your OPENAI_API_KEY in the .env file")
        return
    
    # Initialize the language model
    logger.info("Initializing language model")
    model = ChatOpenAI(model="gpt-4o-mini")
    
    # Create the writer agent
    logger.info("Creating writer agent")
    writer = register_writer_agent(model)
    
    # Create the agent
    agent = writer.create()
    
    # Initialize the conversation state
    state = {"messages": []}
    
    print("\nWriter Agent Test")
    print("----------------")
    print("This test demonstrates how to use the writer agent to perform file operations")
    print("with security boundaries.")
    print("\nExample queries:")
    print("- 'Read the file /tmp/test.txt'")
    print("- 'Write \"Hello, world!\" to /tmp/test.txt'")
    print("- 'List files in /tmp'")
    print("\nType 'exit' to quit.")
    print("----------------\n")
    
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

def test_file_operations():
    """Test the file operations functionality."""
    print("\nFile Operations Tests")
    print("--------------------")
    
    # Create a test directory
    test_dir = "/tmp/mosaic_test"
    os.makedirs(test_dir, exist_ok=True)
    
    # Test cases
    test_cases = [
        {
            "name": "List directory",
            "operation": "list",
            "path": test_dir
        },
        {
            "name": "Write file",
            "operation": "write",
            "path": f"{test_dir}/test.txt",
            "content": "Hello, world! This is a test file."
        },
        {
            "name": "Read file",
            "operation": "read",
            "path": f"{test_dir}/test.txt"
        },
        {
            "name": "Write sensitive content",
            "operation": "write",
            "path": f"{test_dir}/sensitive.txt",
            "content": "My credit card number is 4111 1111 1111 1111."
        },
        {
            "name": "Write to sensitive path",
            "operation": "write",
            "path": "/etc/test.txt",
            "content": "This should not be allowed."
        },
        {
            "name": "Read non-existent file",
            "operation": "read",
            "path": f"{test_dir}/nonexistent.txt"
        }
    ]
    
    # Create the writer agent directly
    writer_agent = register_writer_agent(None)
    
    for test_case in test_cases:
        print(f"\n[Test] {test_case['name']}")
        print(f"Operation: {test_case['operation']}")
        print(f"Path: {test_case['path']}")
        
        if test_case['operation'] == 'list':
            # Test list_files_tool
            result = list_files_tool(test_case['path'])
            print(f"Exists: {result['exists']}")
            if result['error']:
                print(f"Error: {result['error']}")
            else:
                print(f"Files: {result['files']}")
                print(f"Directories: {result['directories']}")
        
        elif test_case['operation'] == 'read':
            # Test read_file_tool
            result = read_file_tool(test_case['path'])
            print(f"Exists: {result['exists']}")
            if result['error']:
                print(f"Error: {result['error']}")
            else:
                print(f"Size: {result['size']} bytes")
                print(f"Content: {result['content']}")
        
        elif test_case['operation'] == 'write':
            # Test write_file_tool
            content_json = json.dumps({"content": test_case['content']})
            result = write_file_tool(f"{test_case['path']} {content_json}")
            print(f"Success: {result['success']}")
            if result['error']:
                print(f"Error: {result['error']}")
            else:
                print(f"Path: {result['path']}")
                print(f"Size: {result['size']} bytes")

def test_security_boundaries():
    """Test the security boundaries of the writer agent."""
    print("\nSecurity Boundaries Tests")
    print("-----------------------")
    
    # Test cases for allowed and disallowed paths
    test_paths = [
        {"path": "/tmp/test.txt", "operation": "write", "expected": True},
        {"path": os.path.expanduser("~/Documents/test.txt"), "operation": "write", "expected": True},
        {"path": os.path.expanduser("~/Downloads/test.txt"), "operation": "write", "expected": True},
        {"path": "/etc/passwd", "operation": "read", "expected": False},
        {"path": "/etc/shadow", "operation": "read", "expected": False},
        {"path": "/var/log/syslog", "operation": "read", "expected": False},
        {"path": os.path.expanduser("~/.ssh/id_rsa"), "operation": "read", "expected": False},
        {"path": os.path.expanduser("~/.aws/credentials"), "operation": "read", "expected": False},
        {"path": ".env", "operation": "write", "expected": False},
        {"path": "config.json", "operation": "write", "expected": False},
        {"path": "secrets.json", "operation": "write", "expected": False}
    ]
    
    for test_path in test_paths:
        print(f"\n[Test] Path: {test_path['path']}")
        print(f"Operation: {test_path['operation']}")
        print(f"Expected: {'Allowed' if test_path['expected'] else 'Disallowed'}")
        
        # Check if the path is allowed
        from mosaic.backend.agents.writer import _is_path_allowed
        result = _is_path_allowed(test_path['path'], test_path['operation'])
        print(f"Result: {'Allowed' if result else 'Disallowed'}")
        print(f"Correct: {'Yes' if result == test_path['expected'] else 'No'}")

if __name__ == "__main__":
    # Uncomment to run the interactive test
    # main()
    
    # Run the automated tests
    test_file_operations()
    test_security_boundaries()
