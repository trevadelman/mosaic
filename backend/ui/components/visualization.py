"""
Visualization Component Module for MOSAIC

This module defines the base visualization component interface for the MOSAIC system.
It provides a foundation for creating specialized visualization components that can
be used by agents to provide rich, interactive data visualizations.
"""

import logging
from abc import abstractmethod
from typing import List, Dict, Any, Optional, Callable, Union

from ..base import UIComponent

# Configure logging
logger = logging.getLogger("mosaic.ui_components.visualization")

class VisualizationComponent(UIComponent):
    """
    Base class for all MOSAIC visualization components.
    
    This class provides the foundation for creating specialized visualization components
    in the MOSAIC system. It extends the base UIComponent with visualization-specific
    functionality.
    """
    
    def __init__(
        self,
        component_id: str,
        name: str,
        description: str = None,
        required_features: List[str] = None,
        default_modal_config: Dict[str, Any] = None,
        chart_types: List[str] = None,
    ):
        """
        Initialize a new visualization component.
        
        Args:
            component_id: The unique identifier for the component
            name: The display name of the component
            description: Optional description of the component
            required_features: Optional list of required features
            default_modal_config: Optional default modal configuration
            chart_types: Optional list of supported chart types
        """
        # Set default modal config for visualization components
        if default_modal_config is None:
            default_modal_config = {
                "size": "large",
                "panels": ["chart", "controls"],
                "features": ["zoom", "pan", "export"],
                "closable": True
            }
        
        # Add visualization-specific required features
        if required_features is None:
            required_features = []
        if "charts" not in required_features:
            required_features.append("charts")
        
        # Initialize the base component
        super().__init__(
            component_id=component_id,
            name=name,
            description=description,
            required_features=required_features,
            default_modal_config=default_modal_config
        )
        
        # Set visualization-specific properties
        self.chart_types = chart_types or ["line", "bar", "pie"]
        
        # Register standard visualization handlers
        self.register_standard_handlers()
        
        logger.info(f"Initialized visualization component {self.name} with {len(self.chart_types)} chart types")
    
    def register_standard_handlers(self) -> None:
        """
        Register standard handlers for visualization components.
        
        This method registers the standard handlers that all visualization components
        should support. Subclasses can override this method to add additional handlers.
        """
        self.register_handler("get_data", self.handle_get_data)
        self.register_handler("change_chart_type", self.handle_change_chart_type)
        self.register_handler("export_data", self.handle_export_data)
    
    @abstractmethod
    async def handle_get_data(self, websocket: Any, event_data: Dict[str, Any], agent_id: str, client_id: str) -> Any:
        """
        Handle a request to get data for the visualization.
        
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
    async def handle_change_chart_type(self, websocket: Any, event_data: Dict[str, Any], agent_id: str, client_id: str) -> Any:
        """
        Handle a request to change the chart type.
        
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
    async def handle_export_data(self, websocket: Any, event_data: Dict[str, Any], agent_id: str, client_id: str) -> Any:
        """
        Handle a request to export data.
        
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
    async def _send_data_response(self, websocket: Any, event_data: Dict[str, Any], data: Dict[str, Any], agent_id: str, client_id: str) -> None:
        """
        Send a data response to the client.
        
        Args:
            websocket: The WebSocket connection
            event_data: The original event data
            data: The data to send
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
