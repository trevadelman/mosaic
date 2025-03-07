"""
Interactive Component Module for MOSAIC

This module defines the base interactive component interface for the MOSAIC system.
It provides a foundation for creating specialized interactive components that can
be used by agents to provide rich, interactive user interfaces.
"""

import logging
from abc import abstractmethod
from typing import List, Dict, Any, Optional, Callable, Union

from ..base import UIComponent

# Configure logging
logger = logging.getLogger("mosaic.ui_components.interactive")

class InteractiveComponent(UIComponent):
    """
    Base class for all MOSAIC interactive components.
    
    This class provides the foundation for creating specialized interactive components
    in the MOSAIC system. It extends the base UIComponent with interactive-specific
    functionality.
    """
    
    def __init__(
        self,
        component_id: str,
        name: str,
        description: str = None,
        required_features: List[str] = None,
        default_modal_config: Dict[str, Any] = None,
        input_types: List[str] = None,
    ):
        """
        Initialize a new interactive component.
        
        Args:
            component_id: The unique identifier for the component
            name: The display name of the component
            description: Optional description of the component
            required_features: Optional list of required features
            default_modal_config: Optional default modal configuration
            input_types: Optional list of supported input types
        """
        # Set default modal config for interactive components
        if default_modal_config is None:
            default_modal_config = {
                "size": "medium",
                "panels": ["form", "controls"],
                "features": ["submit", "reset", "validate"],
                "closable": True
            }
        
        # Add interactive-specific required features
        if required_features is None:
            required_features = []
        if "forms" not in required_features:
            required_features.append("forms")
        
        # Initialize the base component
        super().__init__(
            component_id=component_id,
            name=name,
            description=description,
            required_features=required_features,
            default_modal_config=default_modal_config
        )
        
        # Set interactive-specific properties
        self.input_types = input_types or ["text", "number", "select", "checkbox", "radio"]
        
        # Register standard interactive handlers
        self.register_standard_handlers()
        
        logger.info(f"Initialized interactive component {self.name} with {len(self.input_types)} input types")
    
    def register_standard_handlers(self) -> None:
        """
        Register standard handlers for interactive components.
        
        This method registers the standard handlers that all interactive components
        should support. Subclasses can override this method to add additional handlers.
        """
        self.register_handler("submit", self.handle_submit)
        self.register_handler("validate", self.handle_validate)
        self.register_handler("reset", self.handle_reset)
    
    @abstractmethod
    async def handle_submit(self, websocket: Any, event_data: Dict[str, Any], agent_id: str, client_id: str) -> Any:
        """
        Handle a form submission.
        
        Args:
            websocket: The WebSocket connection
            event_data: The event data
            agent_id: The ID of the agent
            client_id: The ID of the client
            
        Returns:
            The result of the handler
        """
        pass
    
    @abstractmethod
    async def handle_validate(self, websocket: Any, event_data: Dict[str, Any], agent_id: str, client_id: str) -> Any:
        """
        Handle a validation request.
        
        Args:
            websocket: The WebSocket connection
            event_data: The event data
            agent_id: The ID of the agent
            client_id: The ID of the client
            
        Returns:
            The result of the handler
        """
        pass
    
    @abstractmethod
    async def handle_reset(self, websocket: Any, event_data: Dict[str, Any], agent_id: str, client_id: str) -> Any:
        """
        Handle a form reset.
        
        Args:
            websocket: The WebSocket connection
            event_data: The event data
            agent_id: The ID of the agent
            client_id: The ID of the client
            
        Returns:
            The result of the handler
        """
        pass
    
    @abstractmethod
    async def _send_form_response(self, websocket: Any, event_data: Dict[str, Any], response_data: Dict[str, Any], agent_id: str, client_id: str) -> None:
        """
        Send a form response to the client.
        
        Args:
            websocket: The WebSocket connection
            event_data: The original event data
            response_data: The response data to send
            agent_id: The ID of the agent
            client_id: The ID of the client
        """
        pass
    
    @abstractmethod
    async def _send_validation_response(self, websocket: Any, event_data: Dict[str, Any], validation_results: Dict[str, Any], agent_id: str, client_id: str) -> None:
        """
        Send a validation response to the client.
        
        Args:
            websocket: The WebSocket connection
            event_data: The original event data
            validation_results: The validation results to send
            agent_id: The ID of the agent
            client_id: The ID of the client
        """
        pass
    
    @abstractmethod
    async def _send_ui_update(self, websocket: Any, event_data: Dict[str, Any], update_data: Dict[str, Any], agent_id: str, client_id: str) -> None:
        """
        Send a UI update to the client.
        
        Args:
            websocket: The WebSocket connection
            event_data: The original event data
            update_data: The update data to send
            agent_id: The ID of the agent
            client_id: The ID of the client
        """
        pass
