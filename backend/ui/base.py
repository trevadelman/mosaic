"""
Base UI Component Module for MOSAIC

This module defines the base UI component class and related utilities for the MOSAIC system.
It provides a foundation for creating specialized UI components that can be used by agents
to provide rich, interactive interfaces.
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Callable, Type, Union

# Configure logging
logger = logging.getLogger("mosaic.ui_components")

class UIComponent(ABC):
    """
    Base class for all MOSAIC UI components.
    
    This class provides the foundation for creating specialized UI components in the MOSAIC system.
    It handles common functionality such as initialization, handler registration, and event handling.
    """
    
    def __init__(
        self,
        component_id: str,
        name: str,
        description: str = None,
        required_features: List[str] = None,
        default_modal_config: Dict[str, Any] = None,
    ):
        """
        Initialize a new UI component.
        
        Args:
            component_id: The unique identifier for the component
            name: The display name of the component
            description: Optional description of the component
            required_features: Optional list of required features
            default_modal_config: Optional default modal configuration
        """
        self.component_id = component_id
        self.name = name
        self.description = description or f"{name} Component"
        self.required_features = required_features or []
        self.default_modal_config = default_modal_config or {
            "size": "medium",
            "panels": [],
            "features": [],
            "closable": True
        }
        self.handlers = {}
        
        logger.info(f"Initialized {self.name} component with ID {self.component_id}")
    
    def register_handler(self, action: str, handler: Callable) -> None:
        """
        Register a handler for a specific action.
        
        Args:
            action: The action to handle
            handler: The handler function
        """
        if action in self.handlers:
            logger.warning(f"Handler for action '{action}' already registered for component '{self.component_id}'. Overwriting.")
        
        self.handlers[action] = handler
        logger.info(f"Registered handler for action '{action}' in component '{self.component_id}'")
    
    def get_handler(self, action: str) -> Optional[Callable]:
        """
        Get a handler for a specific action.
        
        Args:
            action: The action to get the handler for
            
        Returns:
            The handler function if found, None otherwise
        """
        handler = self.handlers.get(action)
        if handler is None:
            logger.warning(f"Handler for action '{action}' not found in component '{self.component_id}'")
        return handler
    
    def get_registration(self, agent_id: str) -> Dict[str, Any]:
        """
        Get the registration data for this component.
        
        Args:
            agent_id: The ID of the agent that will use this component
            
        Returns:
            A dictionary containing the registration data
        """
        return {
            "id": self.component_id,
            "name": self.name,
            "description": self.description,
            "agentId": agent_id,
            "requiredFeatures": self.required_features,
            "defaultModalConfig": self.default_modal_config
        }
    
    async def handle_event(self, event_data: Dict[str, Any], websocket: Any, agent_id: str, client_id: str) -> Any:
        """
        Handle an event for this component.
        
        Args:
            event_data: The event data
            websocket: The WebSocket connection
            agent_id: The ID of the agent
            client_id: The ID of the client
            
        Returns:
            The result of the handler, or None if no handler found
        """
        action = event_data.get("action")
        if not action:
            logger.warning(f"No action specified in event for component '{self.component_id}'")
            return None
        
        handler = self.get_handler(action)
        if not handler:
            return None
        
        try:
            return await handler(websocket, event_data, agent_id, client_id)
        except Exception as e:
            logger.error(f"Error handling event for component '{self.component_id}', action '{action}': {str(e)}")
            return None


class UIComponentRegistry:
    """
    Registry for managing UI components in the MOSAIC system.
    
    This class provides a centralized registry for creating, retrieving, and
    managing UI components in the MOSAIC system.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UIComponentRegistry, cls).__new__(cls)
            cls._instance.components = {}  # component_id -> component
            cls._instance.agent_components = {}  # agent_id -> [component_id]
            cls._instance.logger = logging.getLogger("mosaic.ui_component_registry")
        return cls._instance
    
    def register(self, component: UIComponent) -> None:
        """
        Register a component with the registry.
        
        Args:
            component: The component to register
        """
        if component.component_id in self.components:
            # Component already registered, don't overwrite
            self.logger.debug(f"Component '{component.component_id}' already registered. Skipping.")
            return
        
        self.components[component.component_id] = component
        self.logger.debug(f"Registered component '{component.component_id}'")
    
    def register_for_agent(self, agent_id: str, component_id: str) -> None:
        """
        Register a component for an agent.
        
        Args:
            agent_id: The ID of the agent
            component_id: The ID of the component
        """
        if component_id not in self.components:
            self.logger.warning(f"Component '{component_id}' not found in registry")
            return
        
        if agent_id not in self.agent_components:
            self.agent_components[agent_id] = []
        
        if component_id not in self.agent_components[agent_id]:
            self.agent_components[agent_id].append(component_id)
            self.logger.debug(f"Registered component '{component_id}' for agent '{agent_id}'")
    
    def get(self, component_id: str) -> Optional[UIComponent]:
        """
        Get a component by ID.
        
        Args:
            component_id: The ID of the component to retrieve
            
        Returns:
            The component if found, None otherwise
        """
        component = self.components.get(component_id)
        if component is None:
            self.logger.warning(f"Component '{component_id}' not found in registry")
        return component
    
    def get_components_for_agent(self, agent_id: str) -> List[UIComponent]:
        """
        Get all components registered for an agent.
        
        Args:
            agent_id: The ID of the agent
            
        Returns:
            A list of components
        """
        component_ids = self.agent_components.get(agent_id, [])
        return [self.get(component_id) for component_id in component_ids if self.get(component_id) is not None]
    
    def get_registrations_for_agent(self, agent_id: str) -> List[Dict[str, Any]]:
        """
        Get all component registrations for an agent.
        
        Args:
            agent_id: The ID of the agent
            
        Returns:
            A list of component registrations
        """
        components = self.get_components_for_agent(agent_id)
        return [component.get_registration(agent_id) for component in components]
    
    def list_components(self) -> List[str]:
        """
        Get a list of all registered component IDs.
        
        Returns:
            A list of component IDs
        """
        return list(self.components.keys())
    
    async def handle_event(self, component_id: str, event_data: Dict[str, Any], websocket: Any, agent_id: str, client_id: str) -> Any:
        """
        Handle an event for a component.
        
        Args:
            component_id: The ID of the component
            event_data: The event data
            websocket: The WebSocket connection
            agent_id: The ID of the agent
            client_id: The ID of the client
            
        Returns:
            The result of the handler, or None if no handler found
        """
        component = self.get(component_id)
        if not component:
            return None
        
        return await component.handle_event(event_data, websocket, agent_id, client_id)


# Create a global UI component registry instance
ui_component_registry = UIComponentRegistry()
