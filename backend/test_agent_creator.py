"""
Test script for the Agent Creator Agent

This script tests the functionality of the Agent Creator Agent, including:
1. Template generation
2. Tool addition
3. Template validation
4. Code generation
5. Deployment
"""

import os
import json
import unittest
import tempfile
import shutil
import importlib.util
from pathlib import Path

try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.agents.agent_creator import AgentCreatorAgent
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.agents.agent_creator import AgentCreatorAgent

# Import the tool functions directly
try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.agents.agent_creator import (
        create_agent_template,
        add_tool_to_template,
        validate_agent_template,
        generate_agent_code,
        deploy_agent,
    )
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.agents.agent_creator import (
        create_agent_template,
        add_tool_to_template,
        validate_agent_template,
        generate_agent_code,
        deploy_agent,
    )

# Create a mock agent creator that can invoke the tools directly
class MockAgentCreator:
    def create_agent_template(self, spec):
        return create_agent_template(spec)
    
    def add_tool_to_template(self, template_json, tool_spec):
        return add_tool_to_template(template_json, tool_spec)
    
    def validate_agent_template(self, template_json):
        return validate_agent_template(template_json)
    
    def generate_agent_code(self, template_json):
        return generate_agent_code(template_json)
    
    def deploy_agent(self, template_json, sandbox=True):
        return deploy_agent(template_json, sandbox=sandbox)

class TestAgentCreatorAgent(unittest.TestCase):
    """Test cases for the Agent Creator Agent."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create a temporary directory for test outputs
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a mock agent creator
        self.agent_creator = MockAgentCreator()
        
        # Create a basic agent specification
        self.agent_spec = """
        name: test_agent
        type: Specialized
        description: A test agent for testing the agent creator
        capabilities: Testing, Validation, Verification
        icon: 🧪
        prompt: You are a test agent that helps with testing and validation.
        """
        
        # Create a basic tool specification
        self.tool_spec = """
        name: test_tool
        description: A test tool for testing the agent creator
        parameters:
        - input: string: The input to test
        - count: integer: The number of times to test
        returns: string: The test result
        implementation:
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
    
    def tearDown(self):
        """Clean up the test environment."""
        # Remove the temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_template_generation(self):
        """Test that the agent creator can generate templates."""
        # Generate a template
        template_json = self.agent_creator.create_agent_template(self.agent_spec)
        
        # Parse the template
        template = json.loads(template_json)
        
        # Check that the template contains the expected elements
        self.assertEqual(template["agent"]["name"], "test_agent")
        self.assertEqual(template["agent"]["type"], "Specialized")
        self.assertEqual(template["agent"]["description"], "A test agent for testing the agent creator")
        self.assertEqual(template["agent"]["capabilities"], ["Testing", "Validation", "Verification"])
        self.assertEqual(template["agent"]["icon"], "🧪")
        self.assertEqual(template["agent"]["systemPrompt"], "You are a test agent that helps with testing and validation.")
        self.assertEqual(template["agent"]["tools"], [])
    
    def test_tool_addition(self):
        """Test that the agent creator can add tools to templates."""
        # Generate a template
        template_json = self.agent_creator.create_agent_template(self.agent_spec)
        
        # Add a tool to the template
        updated_template_json = self.agent_creator.add_tool_to_template(template_json, self.tool_spec)
        
        # Parse the updated template
        updated_template = json.loads(updated_template_json)
        
        # Check that the template contains the expected elements
        self.assertEqual(len(updated_template["agent"]["tools"]), 1)
        self.assertEqual(updated_template["agent"]["tools"][0]["name"], "test_tool")
        self.assertEqual(updated_template["agent"]["tools"][0]["description"], "A test tool for testing the agent creator")
        self.assertEqual(len(updated_template["agent"]["tools"][0]["parameters"]), 2)
        self.assertEqual(updated_template["agent"]["tools"][0]["parameters"][0]["name"], "input")
        self.assertEqual(updated_template["agent"]["tools"][0]["parameters"][0]["type"], "string")
        self.assertEqual(updated_template["agent"]["tools"][0]["parameters"][1]["name"], "count")
        self.assertEqual(updated_template["agent"]["tools"][0]["parameters"][1]["type"], "integer")
        self.assertEqual(updated_template["agent"]["tools"][0]["returns"]["type"], "string")
        self.assertEqual(updated_template["agent"]["tools"][0]["returns"]["description"], "The test result")
        self.assertIn("@tool", updated_template["agent"]["tools"][0]["implementation"]["code"])
    
    def test_template_validation(self):
        """Test that the agent creator can validate templates."""
        # Generate a template
        template_json = self.agent_creator.create_agent_template(self.agent_spec)
        
        # Add a tool to the template
        updated_template_json = self.agent_creator.add_tool_to_template(template_json, self.tool_spec)
        
        # Validate the template
        validation_result = self.agent_creator.validate_agent_template(updated_template_json)
        
        # Check that the validation passed
        self.assertEqual(validation_result, "Agent template is valid")
        
        # Create an invalid template
        invalid_template = json.loads(updated_template_json)
        del invalid_template["agent"]["type"]  # Remove required field
        invalid_template_json = json.dumps(invalid_template)
        
        # Validate the invalid template
        with self.assertRaises(Exception):
            self.agent_creator.validate_agent_template(invalid_template_json)
    
    def test_code_generation(self):
        """Test that the agent creator can generate code."""
        # Generate a template
        template_json = self.agent_creator.create_agent_template(self.agent_spec)
        
        # Add a tool to the template
        updated_template_json = self.agent_creator.add_tool_to_template(template_json, self.tool_spec)
        
        # Generate code
        code = self.agent_creator.generate_agent_code(updated_template_json)
        
        # Check that the code contains the expected elements
        self.assertIn("class TestagentAgent(BaseAgent):", code)
        self.assertIn("def test_tool(", code)
        self.assertIn("def register_test_agent_agent(", code)
    
    def test_deployment(self):
        """Test that the agent creator can deploy agents."""
        # Generate a template
        template_json = self.agent_creator.create_agent_template(self.agent_spec)
        
        # Add a tool to the template
        updated_template_json = self.agent_creator.add_tool_to_template(template_json, self.tool_spec)
        
        # Deploy the agent to the sandbox
        deployment_result = self.agent_creator.deploy_agent(updated_template_json, sandbox=True)
        
        # Check that the deployment was successful
        self.assertIn("Agent 'test_agent' deployed to sandbox", deployment_result)

if __name__ == "__main__":
    unittest.main()
