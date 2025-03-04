"""
Test script for the Agent Sandbox Environment

This script tests the functionality of the Agent Sandbox Environment, including:
1. Sandbox isolation
2. Agent loading in sandbox
3. Deployment pipeline from sandbox to production
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

class TestAgentSandboxEnvironment(unittest.TestCase):
    """Test cases for the Agent Sandbox Environment."""
    
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
        
        # Create a sandbox directory
        self.sandbox_dir = os.path.join(self.temp_dir, "sandbox")
        os.makedirs(self.sandbox_dir, exist_ok=True)
        
        # Create a production directory
        self.production_dir = os.path.join(self.temp_dir, "production")
        os.makedirs(self.production_dir, exist_ok=True)
    
    def tearDown(self):
        """Clean up the test environment."""
        # Remove the temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_sandbox_isolation(self):
        """Test that the sandbox environment is isolated from production."""
        # Write the agent to a file in the sandbox
        sandbox_file = self.generator.write_agent_to_file(
            self.example_definition, 
            self.sandbox_dir
        )
        
        # Check that the file exists in the sandbox
        self.assertTrue(os.path.exists(sandbox_file))
        
        # Check that the file does not exist in production
        production_file = os.path.join(
            self.production_dir, 
            os.path.basename(sandbox_file)
        )
        self.assertFalse(os.path.exists(production_file))
    
    def test_agent_loading_in_sandbox(self):
        """Test that agents can be loaded in the sandbox environment."""
        # Write the agent to a file in the sandbox
        sandbox_file = self.generator.write_agent_to_file(
            self.example_definition, 
            self.sandbox_dir
        )
        
        # Load the module dynamically
        spec = importlib.util.spec_from_file_location(
            "weather_agent_module",
            sandbox_file
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
    
    def test_deployment_pipeline(self):
        """Test the deployment pipeline from sandbox to production."""
        # Write the agent to a file in the sandbox
        sandbox_file = self.generator.write_agent_to_file(
            self.example_definition, 
            self.sandbox_dir
        )
        
        # Deploy the agent to production
        production_file = os.path.join(
            self.production_dir, 
            os.path.basename(sandbox_file)
        )
        shutil.copy(sandbox_file, production_file)
        
        # Check that the file exists in production
        self.assertTrue(os.path.exists(production_file))
        
        # Check that the file contents are the same
        with open(sandbox_file, "r") as f:
            sandbox_content = f.read()
        with open(production_file, "r") as f:
            production_content = f.read()
        self.assertEqual(sandbox_content, production_content)
    
    def test_sandbox_modification(self):
        """Test that modifications in the sandbox do not affect production."""
        # Write the agent to a file in the sandbox
        sandbox_file = self.generator.write_agent_to_file(
            self.example_definition, 
            self.sandbox_dir
        )
        
        # Deploy the agent to production
        production_file = os.path.join(
            self.production_dir, 
            os.path.basename(sandbox_file)
        )
        shutil.copy(sandbox_file, production_file)
        
        # Modify the agent in the sandbox
        with open(sandbox_file, "a") as f:
            f.write("\n# This is a modification in the sandbox")
        
        # Check that the modification exists in the sandbox
        with open(sandbox_file, "r") as f:
            sandbox_content = f.read()
        self.assertIn("# This is a modification in the sandbox", sandbox_content)
        
        # Check that the modification does not exist in production
        with open(production_file, "r") as f:
            production_content = f.read()
        self.assertNotIn("# This is a modification in the sandbox", production_content)

if __name__ == "__main__":
    unittest.main()
