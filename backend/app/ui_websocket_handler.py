"""
UI WebSocket Handler Module for MOSAIC

This module handles WebSocket connections for custom UI components.
It provides a way for the frontend to communicate with the backend for custom UI events.
"""

import logging
import json
import asyncio
from typing import Dict, List, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime
import uuid

# Import the UI component registry, connection manager, and request tracker
try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.ui.base import ui_component_registry
    from mosaic.backend.agents.base import agent_registry
    from mosaic.backend.app.ui_connection_manager import ui_manager
    from mosaic.backend.app.request_tracker import request_tracker
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.ui.base import ui_component_registry
    from backend.agents.base import agent_registry
    from backend.app.ui_connection_manager import ui_manager
    from backend.app.request_tracker import request_tracker

# Configure logging
logger = logging.getLogger("mosaic.ui_websocket_handler")

# Function to get component registrations for an agent
def get_component_registrations(agent_id: str) -> List[Dict[str, Any]]:
    """
    Get component registrations for an agent.
    
    Args:
        agent_id: The agent ID
        
    Returns:
        A list of component registrations
    """
    # Get all components from the registry
    components = ui_component_registry.list_components()
    
    # Get the agent from the registry
    agent = agent_registry.get(agent_id)
    
    if not agent:
        logger.warning(f"Agent {agent_id} not found in registry")
        return []
    
    # Get the components associated with this agent
    agent_components = agent_registry.get_ui_components(agent_id)
    
    if not agent_components:
        logger.info(f"No UI components found for agent {agent_id}")
        return []
    
    # Format the component registrations
    registrations = []
    for component_id in agent_components:
        component = ui_component_registry.get(component_id)
        if component:
            registrations.append({
                "id": component.component_id,
                "name": component.name,
                "description": component.description,
                "agentId": agent_id,
                "requiredFeatures": component.required_features,
                "defaultModalConfig": component.default_modal_config
            })
    
    return registrations

# WebSocket handler for UI events
async def handle_ui_websocket(websocket: WebSocket, agent_id: str):
    """
    Handle WebSocket connections for UI events.
    
    Args:
        websocket: The WebSocket connection
        agent_id: The agent ID
    """
    client_id = str(uuid.uuid4())
    
    try:
        await ui_manager.connect(websocket, client_id, agent_id)
        
        # Get component registrations for this agent from the registry
        registrations = get_component_registrations(agent_id)
        
        # Send component registrations to the client
        await ui_manager.send_component_registrations(registrations, agent_id, client_id)
        
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "ping":
                # Respond to ping with a pong to keep the connection alive
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                })
                continue
            
            elif data.get("type") == "ui_event":
                # Process UI event
                event_data = data.get("data", {})
                
                # Log the event
                logger.info(f"Received UI event from client {client_id} for agent {agent_id}: {event_data.get('type')} - {event_data.get('action')}")
                
                # Get the component ID and action
                component_id = event_data.get("component")
                action = event_data.get("action")
                
                # Generate a request ID for tracking
                request_id = str(uuid.uuid4())
                
                # Add request ID to the event data
                event_data["request_id"] = request_id
                
                # Try to get the component from the registry
                component = ui_component_registry.get(component_id)
                
                if component:
                    # Register the component for this client if not already registered
                    if not ui_manager.is_component_active(component_id, client_id, agent_id):
                        ui_manager.register_component(component_id, client_id, agent_id, websocket)
                    
                    # Get the handler for this action
                    handler = component.get_handler(action)
                    
                    if handler:
                        # Register the handler with the request tracker if not already registered
                        if not request_tracker.get_handler(component_id, action):
                            # Create a wrapper handler that adapts the component handler to the request tracker
                            async def wrapped_handler(data: Dict[str, Any]) -> Dict[str, Any]:
                                try:
                                    # Extract the necessary parameters from the data
                                    ws = data.get("websocket")
                                    event = data.get("event")
                                    agent = data.get("agent_id")
                                    client = data.get("client_id")
                                    
                                    # Call the original handler
                                    await handler(ws, event, agent, client)
                                    
                                    # Return a success response
                                    return {
                                        "success": True,
                                        "timestamp": datetime.now().isoformat()
                                    }
                                except Exception as e:
                                    # Return an error response
                                    return {
                                        "success": False,
                                        "error": str(e),
                                        "timestamp": datetime.now().isoformat()
                                    }
                            
                            # Register the wrapped handler
                            request_tracker.register_handler(component_id, action, wrapped_handler)
                            logger.info(f"Registered handler for component {component_id}, action {action} with request tracker")
                        
                        try:
                            # Track the request with the request tracker
                            logger.info(f"Tracking request {request_id} for component {component_id}, action {action}")
                            
                            # Prepare the data for the handler
                            handler_data = {
                                "websocket": websocket,
                                "event": event_data,
                                "agent_id": agent_id,
                                "client_id": client_id
                            }
                            
                            # Track the request and get the response
                            _, response = await request_tracker.track_request(component_id, action, handler_data)
                            
                            # Check if the response indicates an error
                            if not response.get("success", False):
                                error_message = response.get("error", "Unknown error")
                                logger.error(f"Error in request {request_id} for component {component_id}, action {action}: {error_message}")
                                
                                # Send error response
                                await ui_manager.send_ui_event({
                                    "type": "error",
                                    "component": component_id,
                                    "action": action,
                                    "error": error_message,
                                    "request_id": request_id
                                }, agent_id, client_id, component_id)
                        except Exception as e:
                            logger.error(f"Error tracking request {request_id} for component {component_id}, action {action}: {str(e)}")
                            
                            # Send error response
                            await ui_manager.send_ui_event({
                                "type": "error",
                                "component": component_id,
                                "action": action,
                                "error": str(e),
                                "request_id": request_id
                            }, agent_id, client_id, component_id)
                    else:
                        logger.warning(f"No handler found for component {component_id}, action {action}")
                        
                        # Send error response
                        await ui_manager.send_ui_event({
                            "type": "error",
                            "component": component_id,
                            "action": action,
                            "error": f"No handler found for action {action}",
                            "request_id": request_id
                        }, agent_id, client_id, component_id)
                else:
                    logger.warning(f"Component {component_id} not found in registry")
                    
                    # Send error response
                    await ui_manager.send_ui_event({
                        "type": "error",
                        "component": component_id,
                        "action": action,
                        "error": f"Component {component_id} not found"
                    }, agent_id, client_id)
                
                # Echo the event back to the client for testing
                await websocket.send_json({
                    "type": "ui_event_received",
                    "data": event_data,
                    "timestamp": datetime.now().isoformat()
                })
            
            elif data.get("type") == "get_component_registrations":
                # Get component registrations for this agent from the registry
                registrations = get_component_registrations(agent_id)
                
                # Send component registrations to the client
                await ui_manager.send_component_registrations(registrations, agent_id, client_id)
    
    except WebSocketDisconnect:
        ui_manager.disconnect(websocket, client_id, agent_id)
        logger.info(f"Client {client_id} disconnected from UI WebSocket for agent {agent_id}")
    
    except Exception as e:
        logger.error(f"Error in UI WebSocket handler: {str(e)}")
        ui_manager.disconnect(websocket, client_id, agent_id)

# Note: The helper functions for stock data have been moved to the StockDataProvider
# and are now used by the StockChartComponent

# Start a background task to clean up disconnected clients
async def cleanup_disconnected_clients():
    """
    Periodically clean up disconnected clients.
    """
    while True:
        try:
            # Clean up disconnected clients that have been disconnected for more than 1 hour
            ui_manager.clean_up_disconnected_clients(max_age_seconds=3600)
            
            # Wait for 10 minutes before cleaning up again
            await asyncio.sleep(600)
        except Exception as e:
            logger.error(f"Error cleaning up disconnected clients: {str(e)}")
            
            # Wait for 1 minute before trying again
            await asyncio.sleep(60)

# Function to start the cleanup task
def start_cleanup_task():
    """
    Start the cleanup task in the background.
    """
    asyncio.create_task(cleanup_disconnected_clients())
