"""
Data Input Component Module for MOSAIC

This module defines the base data input component interface for the MOSAIC system.
It provides a foundation for creating specialized data input components that can
be used by agents to collect structured data from users.
"""

import logging
from abc import abstractmethod
from typing import List, Dict, Any, Optional, Callable, Union

from ..base import UIComponent

# Configure logging
logger = logging.getLogger("mosaic.ui_components.data_input")

class DataInputComponent(UIComponent):
    """
    Base class for all MOSAIC data input components.
    
    This class provides the foundation for creating specialized data input components
    in the MOSAIC system. It extends the base UIComponent with data input-specific
    functionality.
    """
    
    def __init__(
        self,
        component_id: str,
        name: str,
        description: str = None,
        required_features: List[str] = None,
        default_modal_config: Dict[str, Any] = None,
        data_schema: Dict[str, Any] = None,
    ):
        """
        Initialize a new data input component.
        
        Args:
            component_id: The unique identifier for the component
            name: The display name of the component
            description: Optional description of the component
            required_features: Optional list of required features
            default_modal_config: Optional default modal configuration
            data_schema: Optional schema for the data to be collected
        """
        # Set default modal config for data input components
        if default_modal_config is None:
            default_modal_config = {
                "size": "medium",
                "panels": ["input", "preview"],
                "features": ["submit", "validate", "clear"],
                "closable": True
            }
        
        # Add data input-specific required features
        if required_features is None:
            required_features = []
        if "data_input" not in required_features:
            required_features.append("data_input")
        
        # Initialize the base component
        super().__init__(
            component_id=component_id,
            name=name,
            description=description,
            required_features=required_features,
            default_modal_config=default_modal_config
        )
        
        # Set data input-specific properties
        self.data_schema = data_schema or {}
        
        # Register standard data input handlers
        self.register_standard_handlers()
        
        logger.info(f"Initialized data input component {self.name}")
    
    def register_standard_handlers(self) -> None:
        """
        Register standard handlers for data input components.
        
        This method registers the standard handlers that all data input components
        should support. Subclasses can override this method to add additional handlers.
        """
        self.register_handler("submit", self.handle_submit)
        self.register_handler("validate", self.handle_validate)
        self.register_handler("clear", self.handle_clear)
        self.register_handler("get_schema", self.handle_get_schema)
    
    @abstractmethod
    async def handle_submit(self, websocket: Any, event_data: Dict[str, Any], agent_id: str, client_id: str) -> Any:
        """
        Handle a data submission.
        
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
    async def handle_clear(self, websocket: Any, event_data: Dict[str, Any], agent_id: str, client_id: str) -> Any:
        """
        Handle a clear request.
        
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
    async def handle_get_schema(self, websocket: Any, event_data: Dict[str, Any], agent_id: str, client_id: str) -> Any:
        """
        Handle a request to get the data schema.
        
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
    async def _send_data_response(self, websocket: Any, event_data: Dict[str, Any], response_data: Dict[str, Any], agent_id: str, client_id: str) -> None:
        """
        Send a data response to the client.
        
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
    async def _send_schema_response(self, websocket: Any, event_data: Dict[str, Any], schema: Dict[str, Any], agent_id: str, client_id: str) -> None:
        """
        Send a schema response to the client.
        
        Args:
            websocket: The WebSocket connection
            event_data: The original event data
            schema: The schema to send
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
