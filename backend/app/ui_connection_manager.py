"""
UI Connection Manager Module for MOSAIC

This module provides a more robust WebSocket connection manager for UI components.
It tracks connections by agent, component, and client, and provides methods for
sending events to specific clients or broadcasting to all clients.
"""

import logging
import json
import asyncio
from typing import Dict, List, Set, Any, Optional, Tuple
from fastapi import WebSocket
from datetime import datetime
import uuid

# Import the UI component registry
try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.ui.base import ui_component_registry
    from mosaic.backend.agents.base import agent_registry
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.ui.base import ui_component_registry
    from backend.agents.base import agent_registry

# Configure logging
logger = logging.getLogger("mosaic.ui_connection_manager")

class UIConnectionManager:
    """
    Enhanced WebSocket connection manager for UI components.
    
    This class manages WebSocket connections for UI components, tracking them by
    agent, component, and client. It provides methods for sending events to specific
    clients or broadcasting to all clients.
    """
    
    def __init__(self):
        """Initialize the UI connection manager."""
        # Track connections by agent
        self.agent_connections: Dict[str, List[WebSocket]] = {}
        
        # Track connections by agent and client
        self.client_connections: Dict[str, Dict[str, WebSocket]] = {}
        
        # Track connections by agent, component, and client
        self.component_connections: Dict[str, Dict[str, Dict[str, WebSocket]]] = {}
        
        # Track active components by client
        self.active_components: Dict[str, Dict[str, Set[str]]] = {}
        
        # Track disconnected clients for potential reconnection
        self.disconnected_clients: Dict[str, Dict[str, datetime]] = {}
        
        # Track message queues for disconnected clients
        self.message_queues: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
        
        # Track connection status
        self.connection_status: Dict[str, Dict[str, bool]] = {}
        
        logger.info("Initialized enhanced UI connection manager")
    
    async def connect(self, websocket: WebSocket, client_id: str, agent_id: str) -> None:
        """
        Connect a client to the UI WebSocket.
        
        Args:
            websocket: The WebSocket connection
            client_id: The client ID
            agent_id: The agent ID
        """
        await websocket.accept()
        
        # Add to agent connections
        if agent_id not in self.agent_connections:
            self.agent_connections[agent_id] = []
        self.agent_connections[agent_id].append(websocket)
        
        # Add to client connections
        if agent_id not in self.client_connections:
            self.client_connections[agent_id] = {}
        self.client_connections[agent_id][client_id] = websocket
        
        # Initialize component connections for this agent and client
        if agent_id not in self.component_connections:
            self.component_connections[agent_id] = {}
        if client_id not in self.component_connections[agent_id]:
            self.component_connections[agent_id][client_id] = {}
        
        # Initialize active components for this agent and client
        if agent_id not in self.active_components:
            self.active_components[agent_id] = {}
        if client_id not in self.active_components[agent_id]:
            self.active_components[agent_id][client_id] = set()
        
        # Update connection status
        if agent_id not in self.connection_status:
            self.connection_status[agent_id] = {}
        self.connection_status[agent_id][client_id] = True
        
        # Check if this client was previously disconnected
        if agent_id in self.disconnected_clients and client_id in self.disconnected_clients[agent_id]:
            # Remove from disconnected clients
            del self.disconnected_clients[agent_id][client_id]
            
            # Send any queued messages
            if agent_id in self.message_queues and client_id in self.message_queues[agent_id]:
                for message in self.message_queues[agent_id][client_id]:
                    await websocket.send_json(message)
                
                # Clear the queue
                self.message_queues[agent_id][client_id] = []
                
                logger.info(f"Sent queued messages to reconnected client {client_id} for agent {agent_id}")
        
        logger.info(f"Client {client_id} connected to UI WebSocket for agent {agent_id}")
    
    def disconnect(self, websocket: WebSocket, client_id: str, agent_id: str) -> None:
        """
        Disconnect a client from the UI WebSocket.
        
        Args:
            websocket: The WebSocket connection
            client_id: The client ID
            agent_id: The agent ID
        """
        # Remove from agent connections
        if agent_id in self.agent_connections:
            if websocket in self.agent_connections[agent_id]:
                self.agent_connections[agent_id].remove(websocket)
        
        # Remove from client connections
        if agent_id in self.client_connections:
            if client_id in self.client_connections[agent_id]:
                del self.client_connections[agent_id][client_id]
        
        # Don't remove from component connections yet, in case the client reconnects
        
        # Update connection status
        if agent_id in self.connection_status:
            if client_id in self.connection_status[agent_id]:
                self.connection_status[agent_id][client_id] = False
        
        # Add to disconnected clients
        if agent_id not in self.disconnected_clients:
            self.disconnected_clients[agent_id] = {}
        self.disconnected_clients[agent_id][client_id] = datetime.now()
        
        # Initialize message queue if needed
        if agent_id not in self.message_queues:
            self.message_queues[agent_id] = {}
        if client_id not in self.message_queues[agent_id]:
            self.message_queues[agent_id][client_id] = []
        
        logger.info(f"Client {client_id} disconnected from UI WebSocket for agent {agent_id}")
    
    def register_component(self, component_id: str, client_id: str, agent_id: str, websocket: WebSocket) -> None:
        """
        Register a component for a client.
        
        Args:
            component_id: The component ID
            client_id: The client ID
            agent_id: The agent ID
            websocket: The WebSocket connection
        """
        # Add to component connections
        if agent_id not in self.component_connections:
            self.component_connections[agent_id] = {}
        if client_id not in self.component_connections[agent_id]:
            self.component_connections[agent_id][client_id] = {}
        self.component_connections[agent_id][client_id][component_id] = websocket
        
        # Add to active components
        if agent_id not in self.active_components:
            self.active_components[agent_id] = {}
        if client_id not in self.active_components[agent_id]:
            self.active_components[agent_id][client_id] = set()
        self.active_components[agent_id][client_id].add(component_id)
        
        logger.info(f"Registered component {component_id} for client {client_id} and agent {agent_id}")
    
    def unregister_component(self, component_id: str, client_id: str, agent_id: str) -> None:
        """
        Unregister a component for a client.
        
        Args:
            component_id: The component ID
            client_id: The client ID
            agent_id: The agent ID
        """
        # Remove from component connections
        if agent_id in self.component_connections:
            if client_id in self.component_connections[agent_id]:
                if component_id in self.component_connections[agent_id][client_id]:
                    del self.component_connections[agent_id][client_id][component_id]
        
        # Remove from active components
        if agent_id in self.active_components:
            if client_id in self.active_components[agent_id]:
                if component_id in self.active_components[agent_id][client_id]:
                    self.active_components[agent_id][client_id].remove(component_id)
        
        logger.info(f"Unregistered component {component_id} for client {client_id} and agent {agent_id}")
    
    def is_component_active(self, component_id: str, client_id: str, agent_id: str) -> bool:
        """
        Check if a component is active for a client.
        
        Args:
            component_id: The component ID
            client_id: The client ID
            agent_id: The agent ID
            
        Returns:
            True if the component is active, False otherwise
        """
        if agent_id in self.active_components:
            if client_id in self.active_components[agent_id]:
                return component_id in self.active_components[agent_id][client_id]
        return False
    
    def is_client_connected(self, client_id: str, agent_id: str) -> bool:
        """
        Check if a client is connected.
        
        Args:
            client_id: The client ID
            agent_id: The agent ID
            
        Returns:
            True if the client is connected, False otherwise
        """
        if agent_id in self.connection_status:
            if client_id in self.connection_status[agent_id]:
                return self.connection_status[agent_id][client_id]
        return False
    
    def get_active_components(self, client_id: str, agent_id: str) -> Set[str]:
        """
        Get the active components for a client.
        
        Args:
            client_id: The client ID
            agent_id: The agent ID
            
        Returns:
            A set of active component IDs
        """
        if agent_id in self.active_components:
            if client_id in self.active_components[agent_id]:
                return self.active_components[agent_id][client_id]
        return set()
    
    def get_active_clients(self, agent_id: str) -> List[str]:
        """
        Get the active clients for an agent.
        
        Args:
            agent_id: The agent ID
            
        Returns:
            A list of active client IDs
        """
        active_clients = []
        if agent_id in self.connection_status:
            for client_id, connected in self.connection_status[agent_id].items():
                if connected:
                    active_clients.append(client_id)
        return active_clients
    
    def get_clients_for_component(self, component_id: str, agent_id: str) -> List[str]:
        """
        Get the clients that have a component active.
        
        Args:
            component_id: The component ID
            agent_id: The agent ID
            
        Returns:
            A list of client IDs
        """
        clients = []
        if agent_id in self.active_components:
            for client_id, components in self.active_components[agent_id].items():
                if component_id in components:
                    clients.append(client_id)
        return clients
    
    def clean_up_disconnected_clients(self, max_age_seconds: int = 3600) -> None:
        """
        Clean up disconnected clients that have been disconnected for too long.
        
        Args:
            max_age_seconds: The maximum age in seconds before a disconnected client is cleaned up
        """
        now = datetime.now()
        for agent_id in list(self.disconnected_clients.keys()):
            for client_id in list(self.disconnected_clients[agent_id].keys()):
                disconnect_time = self.disconnected_clients[agent_id][client_id]
                age = (now - disconnect_time).total_seconds()
                if age > max_age_seconds:
                    # Remove from disconnected clients
                    del self.disconnected_clients[agent_id][client_id]
                    
                    # Remove from message queues
                    if agent_id in self.message_queues and client_id in self.message_queues[agent_id]:
                        del self.message_queues[agent_id][client_id]
                    
                    # Remove from component connections
                    if agent_id in self.component_connections and client_id in self.component_connections[agent_id]:
                        del self.component_connections[agent_id][client_id]
                    
                    # Remove from active components
                    if agent_id in self.active_components and client_id in self.active_components[agent_id]:
                        del self.active_components[agent_id][client_id]
                    
                    # Remove from connection status
                    if agent_id in self.connection_status and client_id in self.connection_status[agent_id]:
                        del self.connection_status[agent_id][client_id]
                    
                    logger.info(f"Cleaned up disconnected client {client_id} for agent {agent_id} after {age} seconds")
    
    async def send_ui_event(self, event: Dict[str, Any], agent_id: str, client_id: Optional[str] = None, component_id: Optional[str] = None) -> None:
        """
        Send a UI event to a client or all clients for an agent.
        
        Args:
            event: The UI event to send
            agent_id: The agent ID
            client_id: Optional client ID to send to a specific client
            component_id: Optional component ID to send to clients with this component active
        """
        # Create the message to send
        message = {
            "type": "ui_event",
            "data": event,
            "timestamp": datetime.now().isoformat()
        }
        
        # Determine the clients to send to
        clients_to_send: List[Tuple[str, WebSocket]] = []
        
        if client_id and component_id:
            # Send to a specific client and component
            if agent_id in self.component_connections:
                if client_id in self.component_connections[agent_id]:
                    if component_id in self.component_connections[agent_id][client_id]:
                        websocket = self.component_connections[agent_id][client_id][component_id]
                        clients_to_send.append((client_id, websocket))
        
        elif client_id:
            # Send to a specific client
            if agent_id in self.client_connections:
                if client_id in self.client_connections[agent_id]:
                    websocket = self.client_connections[agent_id][client_id]
                    clients_to_send.append((client_id, websocket))
        
        elif component_id:
            # Send to all clients with this component active
            if agent_id in self.component_connections:
                for client_id, components in self.component_connections[agent_id].items():
                    if component_id in components:
                        websocket = components[component_id]
                        clients_to_send.append((client_id, websocket))
        
        else:
            # Send to all clients for this agent
            if agent_id in self.client_connections:
                for client_id, websocket in self.client_connections[agent_id].items():
                    clients_to_send.append((client_id, websocket))
        
        # Send the message to each client
        for client_id, websocket in clients_to_send:
            if self.is_client_connected(client_id, agent_id):
                try:
                    await websocket.send_json(message)
                    logger.info(f"Sent UI event to client {client_id} for agent {agent_id}")
                except Exception as e:
                    logger.error(f"Error sending UI event to client {client_id} for agent {agent_id}: {str(e)}")
                    
                    # Mark the client as disconnected
                    self.connection_status[agent_id][client_id] = False
                    
                    # Add to disconnected clients
                    if agent_id not in self.disconnected_clients:
                        self.disconnected_clients[agent_id] = {}
                    self.disconnected_clients[agent_id][client_id] = datetime.now()
                    
                    # Queue the message
                    if agent_id not in self.message_queues:
                        self.message_queues[agent_id] = {}
                    if client_id not in self.message_queues[agent_id]:
                        self.message_queues[agent_id][client_id] = []
                    self.message_queues[agent_id][client_id].append(message)
            else:
                # Queue the message for disconnected clients
                if agent_id not in self.message_queues:
                    self.message_queues[agent_id] = {}
                if client_id not in self.message_queues[agent_id]:
                    self.message_queues[agent_id][client_id] = []
                self.message_queues[agent_id][client_id].append(message)
                
                logger.info(f"Queued UI event for disconnected client {client_id} for agent {agent_id}")
    
    async def broadcast_ui_event(self, event: Dict[str, Any]) -> None:
        """
        Broadcast a UI event to all connected clients.
        
        Args:
            event: The UI event to broadcast
        """
        # Create the message to send
        message = {
            "type": "ui_event",
            "data": event,
            "timestamp": datetime.now().isoformat()
        }
        
        # Send to all connected clients
        for agent_id, clients in self.client_connections.items():
            for client_id, websocket in clients.items():
                if self.is_client_connected(client_id, agent_id):
                    try:
                        await websocket.send_json(message)
                        logger.info(f"Broadcast UI event to client {client_id} for agent {agent_id}")
                    except Exception as e:
                        logger.error(f"Error broadcasting UI event to client {client_id} for agent {agent_id}: {str(e)}")
                        
                        # Mark the client as disconnected
                        self.connection_status[agent_id][client_id] = False
                        
                        # Add to disconnected clients
                        if agent_id not in self.disconnected_clients:
                            self.disconnected_clients[agent_id] = {}
                        self.disconnected_clients[agent_id][client_id] = datetime.now()
                        
                        # Queue the message
                        if agent_id not in self.message_queues:
                            self.message_queues[agent_id] = {}
                        if client_id not in self.message_queues[agent_id]:
                            self.message_queues[agent_id][client_id] = []
                        self.message_queues[agent_id][client_id].append(message)
    
    async def send_component_registrations(self, registrations: List[Dict[str, Any]], agent_id: str, client_id: Optional[str] = None) -> None:
        """
        Send component registrations to a client or all clients for an agent.
        
        Args:
            registrations: The component registrations to send
            agent_id: The agent ID
            client_id: Optional client ID to send to a specific client
        """
        # Create the message to send
        message = {
            "type": "component_registrations",
            "data": {
                "registrations": registrations
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Determine the clients to send to
        clients_to_send: List[Tuple[str, WebSocket]] = []
        
        if client_id:
            # Send to a specific client
            if agent_id in self.client_connections:
                if client_id in self.client_connections[agent_id]:
                    websocket = self.client_connections[agent_id][client_id]
                    clients_to_send.append((client_id, websocket))
        else:
            # Send to all clients for this agent
            if agent_id in self.client_connections:
                for client_id, websocket in self.client_connections[agent_id].items():
                    clients_to_send.append((client_id, websocket))
        
        # Send the message to each client
        for client_id, websocket in clients_to_send:
            if self.is_client_connected(client_id, agent_id):
                try:
                    await websocket.send_json(message)
                    logger.info(f"Sent component registrations to client {client_id} for agent {agent_id}")
                except Exception as e:
                    logger.error(f"Error sending component registrations to client {client_id} for agent {agent_id}: {str(e)}")
                    
                    # Mark the client as disconnected
                    self.connection_status[agent_id][client_id] = False
                    
                    # Add to disconnected clients
                    if agent_id not in self.disconnected_clients:
                        self.disconnected_clients[agent_id] = {}
                    self.disconnected_clients[agent_id][client_id] = datetime.now()
                    
                    # Queue the message
                    if agent_id not in self.message_queues:
                        self.message_queues[agent_id] = {}
                    if client_id not in self.message_queues[agent_id]:
                        self.message_queues[agent_id][client_id] = []
                    self.message_queues[agent_id][client_id].append(message)
            else:
                # Queue the message for disconnected clients
                if agent_id not in self.message_queues:
                    self.message_queues[agent_id] = {}
                if client_id not in self.message_queues[agent_id]:
                    self.message_queues[agent_id][client_id] = []
                self.message_queues[agent_id][client_id].append(message)
                
                logger.info(f"Queued component registrations for disconnected client {client_id} for agent {agent_id}")

# Create a global UI connection manager
ui_manager = UIConnectionManager()
