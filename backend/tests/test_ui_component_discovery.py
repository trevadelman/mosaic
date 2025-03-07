"""
Simple Test for UI Component System

This module provides a simple test for the UI component system using a real component.
"""

import unittest
import sys
import os
from unittest.mock import MagicMock

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import the test component
from backend.ui.components.test_component import TestComponent
from backend.ui.base import ui_component_registry
from backend.agents.base import agent_registry, BaseAgent
from backend.app.ui_websocket_handler import get_component_registrations

class TestUIComponentSystem(unittest.TestCase):
    """Test the UI component system with a real component."""
    
    def setUp(self):
        """Set up the test case."""
        # Create a mock agent for testing
        self.mock_agent = MagicMock(spec=BaseAgent)
        self.mock_agent.name = "test_agent"
        
        # Register the mock agent
        agent_registry.agents["test_agent"] = self.mock_agent
        
        # Get the test component
        self.test_component = ui_component_registry.get("test-component")
        
        # Manually register the component with the agent
        if "test_agent" not in agent_registry.ui_components:
            agent_registry.ui_components["test_agent"] = []
        
        if "test-component" not in agent_registry.ui_components["test_agent"]:
            agent_registry.ui_components["test_agent"].append("test-component")
    
    def tearDown(self):
        """Tear down the test case."""
        # Remove the mock agent
        if "test_agent" in agent_registry.agents:
            del agent_registry.agents["test_agent"]
    
    def test_component_registration(self):
        """Test that the test component is registered correctly."""
        # Get the test component from the registry
        component = ui_component_registry.get("test-component")
        
        # Check that the component exists
        self.assertIsNotNone(component)
        
        # Check that it's the right type
        self.assertIsInstance(component, TestComponent)
        
        # Check that the component properties are correct
        self.assertEqual(component.component_id, "test-component")
        self.assertEqual(component.name, "Test Component")
        self.assertEqual(component.description, "A simple component for testing the UI component system")
        self.assertEqual(component.required_features, ["test"])
        self.assertEqual(component.default_modal_config["size"], "medium")
        self.assertEqual(component.default_modal_config["closable"], True)
    
    def test_component_handlers(self):
        """Test that the component handlers are registered correctly."""
        # Get the test component from the registry
        component = ui_component_registry.get("test-component")
        
        # Check that the handlers exist
        self.assertIsNotNone(component.get_handler("test_action"))
        self.assertIsNotNone(component.get_handler("get_data"))
        
        # Check that non-existent handlers return None
        self.assertIsNone(component.get_handler("non_existent_action"))
    
    def test_agent_component_association(self):
        """Test that the component is associated with the test agent."""
        # Get the components for the test agent
        components = agent_registry.get_ui_components("test_agent")
        
        # Check that the test component is in the list
        self.assertIn("test-component", components)
    
    def test_component_registrations(self):
        """Test that the component registrations are correct."""
        # Patch the get_component_registrations function to use our mock agent
        from unittest.mock import patch
        
        with patch('backend.app.ui_websocket_handler.agent_registry.get') as mock_get:
            # Set up the mock to return our mock agent
            mock_get.return_value = self.mock_agent
            
            # Get the component registrations for the test agent
            registrations = get_component_registrations("test_agent")
            
            # Check that there is one registration
            self.assertEqual(len(registrations), 1)
            
            # Check that the registration is correct
            registration = registrations[0]
            self.assertEqual(registration["id"], "test-component")
            self.assertEqual(registration["name"], "Test Component")
            self.assertEqual(registration["description"], "A simple component for testing the UI component system")
            self.assertEqual(registration["agentId"], "test_agent")
            self.assertEqual(registration["requiredFeatures"], ["test"])
            self.assertEqual(registration["defaultModalConfig"]["size"], "medium")
            self.assertEqual(registration["defaultModalConfig"]["closable"], True)

if __name__ == '__main__':
    unittest.main()
