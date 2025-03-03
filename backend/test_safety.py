"""
Test script for the safety agent.

This script demonstrates how to use the safety agent to validate content
and approve operations based on safety rules.
"""

import os
import logging
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.agents import register_safety_agent
    from mosaic.backend.agents.safety import validate_content_tool, approve_operation_tool
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.agents import register_safety_agent
    from backend.agents.safety import validate_content_tool, approve_operation_tool

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("mosaic.test_safety")

# Load environment variables
load_dotenv()

def main():
    """Run the safety agent test."""
    # Check if the OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("Please set your OPENAI_API_KEY in the .env file")
        return
    
    # Initialize the language model
    logger.info("Initializing language model")
    model = ChatOpenAI(model="gpt-4o-mini")
    
    # Create the safety agent
    logger.info("Creating safety agent")
    safety = register_safety_agent(model)
    
    # Create the agent
    agent = safety.create()
    
    # Initialize the conversation state
    state = {"messages": []}
    
    print("\nSafety Agent Test")
    print("----------------")
    print("This test demonstrates how to use the safety agent to validate content")
    print("and approve operations based on safety rules.")
    print("\nExample queries:")
    print("- 'Validate this content: Here is my phone number 555-123-4567'")
    print("- 'Approve this file write operation to /etc/passwd'")
    print("- 'Is it safe to run the command: rm -rf /tmp/test'")
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

def test_content_validation():
    """Test the content validation functionality."""
    print("\nContent Validation Tests")
    print("----------------------")
    
    test_cases = [
        {
            "name": "Safe content",
            "content": "This is a safe message with no personal information."
        },
        {
            "name": "Email detection",
            "content": "Please contact me at john.doe@example.com for more information."
        },
        {
            "name": "Credit card detection",
            "content": "My credit card number is 4111 1111 1111 1111."
        },
        {
            "name": "Phone number detection",
            "content": "Call me at (555) 123-4567 or +1 555-987-6543."
        },
        {
            "name": "Dangerous command",
            "content": "To fix the issue, run rm -rf / on your system."
        }
    ]
    
    # Create the safety agent directly
    safety_agent = register_safety_agent(None)
    
    for test_case in test_cases:
        print(f"\n[Test] {test_case['name']}")
        print(f"Content: {test_case['content']}")
        
        # Call the validation tool directly
        result = validate_content_tool(test_case['content'])
        
        # Print the result
        print(f"Is safe: {result['is_safe']}")
        if result['issues']:
            print(f"Issues: {result['issues']}")
        print(f"Severity: {result['severity']}")
        print(f"Recommendation: {result['recommendation']}")

def test_operation_approval():
    """Test the operation approval functionality."""
    print("\nOperation Approval Tests")
    print("----------------------")
    
    test_cases = [
        {
            "name": "Safe file write",
            "operation": "file_write",
            "context": {
                "path": "/tmp/test.txt",
                "content": "This is a test file."
            }
        },
        {
            "name": "Sensitive file write",
            "operation": "file_write",
            "context": {
                "path": "/etc/passwd",
                "content": "new:x:1001:1001::/home/new:/bin/bash"
            }
        },
        {
            "name": "Safe API call",
            "operation": "api_call",
            "context": {
                "url": "https://api.openai.com/v1/chat/completions",
                "method": "POST"
            }
        },
        {
            "name": "Unauthorized API call",
            "operation": "api_call",
            "context": {
                "url": "https://malicious-site.com/api",
                "method": "POST"
            }
        },
        {
            "name": "Safe command",
            "operation": "execute_command",
            "context": {
                "command": "ls -la /tmp"
            }
        },
        {
            "name": "Dangerous command",
            "operation": "execute_command",
            "context": {
                "command": "sudo rm -rf /var/log"
            }
        }
    ]
    
    # Create the safety agent directly
    safety_agent = register_safety_agent(None)
    
    for test_case in test_cases:
        print(f"\n[Test] {test_case['name']}")
        print(f"Operation: {test_case['operation']}")
        print(f"Context: {json.dumps(test_case['context'], indent=2)}")
        
        # Call the approval tool directly
        # Create a string representation of the operation and context
        operation = test_case['operation']
        context = test_case['context']
        result = approve_operation_tool(f"{operation} {json.dumps(context)}")
        
        # Print the result
        print(f"Approved: {result['approved']}")
        print(f"Reason: {result['reason']}")
        if result['restrictions']:
            print(f"Restrictions: {result['restrictions']}")

def test_package_installation():
    """Test the package installation security checks."""
    print("\nPackage Installation Security Tests")
    print("--------------------------------")
    
    test_cases = [
        {
            "name": "Simple pip install",
            "command": "pip install requests",
            "expected_approved": True,
            "expected_restrictions": True
        },
        {
            "name": "Pip install with version pinning",
            "command": "pip install requests==2.28.1",
            "expected_approved": True,
            "expected_restrictions": True
        },
        {
            "name": "Pip install from git",
            "command": "pip install git+https://github.com/example/package.git",
            "expected_approved": True,
            "expected_restrictions": True
        },
        {
            "name": "Pip install with sudo",
            "command": "sudo pip install requests",
            "expected_approved": False,
            "expected_restrictions": False
        },
        {
            "name": "Npm install",
            "command": "npm install express",
            "expected_approved": True,
            "expected_restrictions": True
        },
        {
            "name": "Npm install with version",
            "command": "npm install express@4.18.2",
            "expected_approved": True,
            "expected_restrictions": True
        },
        {
            "name": "Apt install",
            "command": "apt-get install nginx",
            "expected_approved": True,
            "expected_restrictions": True
        },
        {
            "name": "Brew install",
            "command": "brew install node",
            "expected_approved": True,
            "expected_restrictions": True
        },
        {
            "name": "Pip install with suspicious flag",
            "command": "pip install --pre tensorflow",
            "expected_approved": True,
            "expected_restrictions": True
        },
        {
            "name": "Pip install in virtual environment",
            "command": "venv/bin/pip install requests",
            "expected_approved": True,
            "expected_restrictions": True
        }
    ]
    
    # Import the package installation check function
    from mosaic.backend.agents.safety import _check_package_installation
    
    for test_case in test_cases:
        print(f"\n[Test] {test_case['name']}")
        print(f"Command: {test_case['command']}")
        
        # Call the package installation check function
        result = _check_package_installation(test_case['command'])
        
        # Print the result
        print(f"Approved: {result['approved']} (Expected: {test_case['expected_approved']})")
        print(f"Reason: {result['reason']}")
        if result['restrictions']:
            print(f"Restrictions: {result['restrictions']}")
            has_restrictions = True
        else:
            has_restrictions = False
        
        print(f"Has Restrictions: {has_restrictions} (Expected: {test_case['expected_restrictions']})")
        print(f"Correct Approval: {'Yes' if result['approved'] == test_case['expected_approved'] else 'No'}")
        print(f"Correct Restrictions: {'Yes' if has_restrictions == test_case['expected_restrictions'] else 'No'}")

if __name__ == "__main__":
    # Uncomment to run the interactive test
    # main()
    
    # Run the automated tests
    test_content_validation()
    test_operation_approval()
    test_package_installation()
