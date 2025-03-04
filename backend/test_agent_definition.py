"""
Test script for the Agent Definition System

This script tests the functionality of the Agent Definition System, including:
1. Schema validation
2. Code generation
3. Agent registration
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
    from mosaic.backend.agents.agent_generator import AgentGenerator
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.agents.agent_generator import AgentGenerator

class TestAgentDefinitionSystem(unittest.TestCase):
    """Test cases for the Agent Definition System."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create a temporary directory for test outputs
        self.temp_dir = tempfile.mkdtemp()
        
        # Initialize the agent generator
        self.generator = AgentGenerator()
        
        # Load the example agent definition
        example_path = os.path.join(
            os.path.dirname(__file__), 
            "agents", 
            "example_agent.json"
        )
        with open(example_path, "r") as f:
            self.example_definition = json.load(f)
    
    def tearDown(self):
        """Clean up the test environment."""
        # Remove the temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_schema_validation(self):
        """Test that the schema validation works correctly."""
        # Valid definition should pass validation
        self.assertTrue(
            self.generator.validate_definition(self.example_definition)
        )
        
        # Invalid definition should fail validation
        invalid_definition = {
            "agent": {
                "name": "invalid_agent",
                # Missing required fields
            }
        }
        
        with self.assertRaises(Exception):
            self.generator.validate_definition(invalid_definition)
    
    def test_code_generation(self):
        """Test that the code generation works correctly."""
        # Generate code for the example agent
        code = self.generator.generate_agent_class(self.example_definition)
        
        # Check that the code contains expected elements
        self.assertIn("class WeatheragentAgent(BaseAgent):", code)
        self.assertIn("def get_current_weather(", code)
        self.assertIn("def get_weather_forecast(", code)
        self.assertIn("def register_weather_agent_agent(", code)
    
    def test_agent_file_generation(self):
        """Test that the agent file generation works correctly."""
        # Write the agent to a file
        output_file = self.generator.write_agent_to_file(
            self.example_definition, 
            self.temp_dir
        )
        
        # Check that the file exists
        self.assertTrue(os.path.exists(output_file))
        
        # Check that the file contains the expected code
        with open(output_file, "r") as f:
            code = f.read()
        
        self.assertIn("class WeatheragentAgent(BaseAgent):", code)
        self.assertIn("def get_current_weather(", code)
        self.assertIn("def get_weather_forecast(", code)
        self.assertIn("def register_weather_agent_agent(", code)
    
    def test_dynamic_loading(self):
        """Test that the generated agent can be dynamically loaded."""
        # Write the agent to a file
        output_file = self.generator.write_agent_to_file(
            self.example_definition, 
            self.temp_dir
        )
        
        # Load the module dynamically
        spec = importlib.util.spec_from_file_location(
            "weather_agent_module",
            output_file
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Check that the module contains the expected classes and functions
        self.assertTrue(hasattr(module, "WeatheragentAgent"))
        self.assertTrue(hasattr(module, "register_weather_agent_agent"))
        
        # Check that the agent class has the expected methods
        agent_class = getattr(module, "WeatheragentAgent")
        agent = agent_class()
        self.assertTrue(hasattr(agent, "_get_default_prompt"))
        self.assertEqual(agent.name, "weather_agent")

if __name__ == "__main__":
    unittest.main()
