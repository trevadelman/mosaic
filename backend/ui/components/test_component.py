"""
Test Component for MOSAIC UI

This module provides a simple test component for testing the UI component system.
"""

from typing import Dict, List, Any, Optional, Callable, Awaitable
from fastapi import WebSocket

# Import the UI component base class
try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.ui.base import UIComponent, ui_component_registry
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.ui.base import UIComponent, ui_component_registry

class TestComponent(UIComponent):
    """A simple test component for testing the UI component system."""
    
    def __init__(self):
        """Initialize the test component."""
        super().__init__(
            component_id="test-component",
            name="Test Component",
            description="A simple component for testing the UI component system",
            required_features=["test"],
            default_modal_config={
                "size": "medium",
                "closable": True
            }
        )
        
        # Register handlers
        self.register_handler("test_action", self.handle_test_action)
        self.register_handler("get_data", self.handle_get_data)
    
    def register_handler(self, action: str, handler: Callable[[WebSocket, Dict[str, Any], str, str], Awaitable[None]]):
        """
        Register a handler for a specific action.
        
        Args:
            action: The action to handle
            handler: The handler function
        """
        self.handlers[action] = handler
    
    def get_handler(self, action: str) -> Optional[Callable[[WebSocket, Dict[str, Any], str, str], Awaitable[None]]]:
        """
        Get the handler for a specific action.
        
        Args:
            action: The action to get the handler for
            
        Returns:
            The handler function, or None if no handler is registered for the action
        """
        return self.handlers.get(action)
    
    async def handle_test_action(self, websocket: WebSocket, event_data: Dict[str, Any], agent_id: str, client_id: str):
        """
        Handle a test action.
        
        Args:
            websocket: The WebSocket connection
            event_data: The event data
            agent_id: The agent ID
            client_id: The client ID
        """
        # Send a response
        await websocket.send_json({
            "type": "ui_event",
            "data": {
                "type": "test_response",
                "component": self.component_id,
                "action": "test_action",
                "data": {
                    "message": "Test action handled successfully",
                    "received_data": event_data.get("data", {})
                }
            }
        })
    
    async def handle_get_data(self, websocket: WebSocket, event_data: Dict[str, Any], agent_id: str, client_id: str):
        """
        Handle a get data action.
        
        Args:
            websocket: The WebSocket connection
            event_data: The event data
            agent_id: The agent ID
            client_id: The client ID
        """
        # Send a response with some test data
        await websocket.send_json({
            "type": "ui_event",
            "data": {
                "type": "data_response",
                "component": self.component_id,
                "action": "get_data",
                "data": {
                    "items": [
                        {"id": 1, "name": "Item 1", "value": 100},
                        {"id": 2, "name": "Item 2", "value": 200},
                        {"id": 3, "name": "Item 3", "value": 300}
                    ],
                    "total": 3
                }
            }
        })

# Register the component with the registry
test_component = TestComponent()
ui_component_registry.register(test_component)

# Register the component with the agent registry
try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.agents.base import agent_registry
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.agents.base import agent_registry

# Register the component with the test agent
agent_registry.register_ui_component("test_agent", test_component.component_id)
