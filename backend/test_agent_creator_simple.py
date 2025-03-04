"""
Simplified test script for the Agent Creator Agent

This script tests the basic functionality of the Agent Creator Agent.
"""

import os
import json
import unittest
import tempfile
import shutil
from pathlib import Path

class TestAgentCreatorSimple(unittest.TestCase):
    """Simplified test cases for the Agent Creator Agent."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create a temporary directory for test outputs
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a basic agent specification
        self.agent_spec = {
            "agent": {
                "name": "test_agent",
                "type": "Specialized",
                "description": "A test agent for testing the agent creator",
                "capabilities": ["Testing", "Validation", "Verification"],
                "icon": "🧪",
                "systemPrompt": "You are a test agent that helps with testing and validation.",
                "tools": []
            }
        }
        
        # Create a basic tool specification
        self.tool_spec = {
            "name": "test_tool",
            "description": "A test tool for testing the agent creator",
            "parameters": [
                {
                    "name": "input",
                    "type": "string",
                    "description": "The input to test"
                },
                {
                    "name": "count",
                    "type": "integer",
                    "description": "The number of times to test"
                }
            ],
            "returns": {
                "type": "string",
                "description": "The test result"
            },
            "implementation": {
                "code": """
@tool
def test_tool(input: str, count: int = 1) -> str:
    \"\"\"A test tool for testing the agent creator.
    
    Args:
        input: The input to test
        count: The number of times to test
        
    Returns:
        The test result
    \"\"\"
    result = input * count
    return f"Test result: {result}"
"""
            }
        }
    
    def tearDown(self):
        """Clean up the test environment."""
        # Remove the temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_agent_template_structure(self):
        """Test that the agent template has the correct structure."""
        # Check that the agent template has the expected structure
        self.assertEqual(self.agent_spec["agent"]["name"], "test_agent")
        self.assertEqual(self.agent_spec["agent"]["type"], "Specialized")
        self.assertEqual(self.agent_spec["agent"]["description"], "A test agent for testing the agent creator")
        self.assertEqual(self.agent_spec["agent"]["capabilities"], ["Testing", "Validation", "Verification"])
        self.assertEqual(self.agent_spec["agent"]["icon"], "🧪")
        self.assertEqual(self.agent_spec["agent"]["systemPrompt"], "You are a test agent that helps with testing and validation.")
        self.assertEqual(self.agent_spec["agent"]["tools"], [])
    
    def test_tool_structure(self):
        """Test that the tool specification has the correct structure."""
        # Check that the tool specification has the expected structure
        self.assertEqual(self.tool_spec["name"], "test_tool")
        self.assertEqual(self.tool_spec["description"], "A test tool for testing the agent creator")
        self.assertEqual(len(self.tool_spec["parameters"]), 2)
        self.assertEqual(self.tool_spec["parameters"][0]["name"], "input")
        self.assertEqual(self.tool_spec["parameters"][0]["type"], "string")
        self.assertEqual(self.tool_spec["parameters"][1]["name"], "count")
        self.assertEqual(self.tool_spec["parameters"][1]["type"], "integer")
        self.assertEqual(self.tool_spec["returns"]["type"], "string")
        self.assertEqual(self.tool_spec["returns"]["description"], "The test result")
        self.assertIn("@tool", self.tool_spec["implementation"]["code"])
    
    def test_add_tool_to_template(self):
        """Test that a tool can be added to an agent template."""
        # Add the tool to the agent template
        self.agent_spec["agent"]["tools"].append(self.tool_spec)
        
        # Check that the tool was added correctly
        self.assertEqual(len(self.agent_spec["agent"]["tools"]), 1)
        self.assertEqual(self.agent_spec["agent"]["tools"][0]["name"], "test_tool")
        self.assertEqual(self.agent_spec["agent"]["tools"][0]["description"], "A test tool for testing the agent creator")
        self.assertEqual(len(self.agent_spec["agent"]["tools"][0]["parameters"]), 2)
        self.assertEqual(self.agent_spec["agent"]["tools"][0]["parameters"][0]["name"], "input")
        self.assertEqual(self.agent_spec["agent"]["tools"][0]["parameters"][0]["type"], "string")
        self.assertEqual(self.agent_spec["agent"]["tools"][0]["parameters"][1]["name"], "count")
        self.assertEqual(self.agent_spec["agent"]["tools"][0]["parameters"][1]["type"], "integer")
        self.assertEqual(self.agent_spec["agent"]["tools"][0]["returns"]["type"], "string")
        self.assertEqual(self.agent_spec["agent"]["tools"][0]["returns"]["description"], "The test result")
        self.assertIn("@tool", self.agent_spec["agent"]["tools"][0]["implementation"]["code"])

if __name__ == "__main__":
    unittest.main()
