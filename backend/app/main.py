from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
import os
import uuid
import asyncio
import base64
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import json

# Import database modules
try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.database import init_db, ChatService, AttachmentService, UserPreferenceService
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.database import init_db, ChatService, AttachmentService, UserPreferenceService

# Import the API routers
try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.app.agent_api import get_agent_api_router
    from mosaic.backend.app.user_api import get_user_api_router
    from mosaic.backend.app.webhook_api import get_webhook_api_router
    from mosaic.backend.app.user_data_api import get_user_data_api_router
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.app.agent_api import get_agent_api_router
    from backend.app.user_api import get_user_api_router
    from backend.app.webhook_api import get_webhook_api_router
    from backend.app.user_data_api import get_user_data_api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("mosaic_api")

# Initialize FastAPI app
app = FastAPI(
    title="MOSAIC API",
    description="API for Multi-agent Orchestration System for Adaptive Intelligent Collaboration",
    version="0.1.0",
)

# Include the API routers
app.include_router(get_agent_api_router())
app.include_router(get_user_api_router())
app.include_router(get_webhook_api_router())
app.include_router(get_user_data_api_router())

# Import settings
try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.app.config import settings
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.app.config import settings

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, client_id: str, query_id: Optional[str] = None):
        await websocket.accept()
        if query_id:
            if query_id not in self.active_connections:
                self.active_connections[query_id] = []
            self.active_connections[query_id].append(websocket)
            logger.info(f"Client {client_id} joined room {query_id}")
        else:
            if "broadcast" not in self.active_connections:
                self.active_connections["broadcast"] = []
            self.active_connections["broadcast"].append(websocket)
            logger.info(f"Client {client_id} connected to broadcast")

    def disconnect(self, websocket: WebSocket, query_id: Optional[str] = None):
        if query_id and query_id in self.active_connections:
            self.active_connections[query_id].remove(websocket)
            logger.info(f"Client disconnected from room {query_id}")
        elif "broadcast" in self.active_connections:
            self.active_connections["broadcast"].remove(websocket)
            logger.info("Client disconnected from broadcast")

    async def send_log(self, log: str, query_id: str):
        if query_id in self.active_connections:
            for connection in self.active_connections[query_id]:
                await connection.send_json({
                    "type": "log_update",
                    "log": log,
                    "timestamp": datetime.now().isoformat()
                })

    async def send_agent_response(self, agent: str, content: str, query_id: str):
        if query_id in self.active_connections:
            for connection in self.active_connections[query_id]:
                await connection.send_json({
                    "type": "agent_response",
                    "agent": agent,
                    "content": content,
                    "timestamp": datetime.now().isoformat()
                })

    async def send_status_update(self, status: str, message: str, query_id: str):
        if query_id in self.active_connections:
            for connection in self.active_connections[query_id]:
                await connection.send_json({
                    "type": "status_update",
                    "status": status,
                    "message": message,
                    "timestamp": datetime.now().isoformat()
                })

manager = ConnectionManager()

# Models
class Query(BaseModel):
    query: str

class QueryResponse(BaseModel):
    query_id: str
    status: str
    message: str

# Models for agents and messages
class Agent(BaseModel):
    id: str
    name: str
    description: str
    type: str
    capabilities: List[str]
    icon: Optional[str] = None

class MessageContent(BaseModel):
    content: str

class Attachment(BaseModel):
    id: int
    type: str
    filename: str
    contentType: str
    size: int
    url: Optional[str] = None
    data: Optional[str] = None  # Base64 encoded data

class Message(BaseModel):
    id: str
    role: str
    content: str
    timestamp: int
    agentId: Optional[str] = None
    status: Optional[str] = None
    error: Optional[str] = None
    attachments: Optional[List[Attachment]] = None

# Import the agent registry
try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.agents.base import agent_registry
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.agents.base import agent_registry

# Log the agent registry
logger.info(f"Agent registry at import: {agent_registry.list_agents()}")

# Message storage
MESSAGE_STORE = {}

# Routes
@app.get("/")
async def root():
    return {"message": "Welcome to MOSAIC API"}

@app.get("/api/debug/agents")
async def debug_agents():
    """Debug endpoint to check the initialized agents."""
    initialized_agents = get_initialized_agents()
    return {
        "initialized_agents": list(initialized_agents.keys()),
        "registry_agents": agent_registry.list_agents(),
        "openai_api_key_set": bool(os.getenv("OPENAI_API_KEY")),
        "environment": os.getenv("ENVIRONMENT", "unknown"),
        "cors_origins": os.getenv("CORS_ORIGINS", "").split(",")
    }

# Import the agent API for metadata extraction and UI WebSocket handler
try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.app.agent_api import agent_api
    from mosaic.backend.app.ui_websocket_handler import handle_ui_websocket
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.app.agent_api import agent_api
    from backend.app.ui_websocket_handler import handle_ui_websocket

# Agent routes
@app.get("/api/agents")
async def get_agents():
    """Get a list of all available agents."""
    try:
        initialized_agents = get_initialized_agents()
        agents = []
        
        for agent_id, agent in initialized_agents.items():
            # Extract agent metadata using the agent_api's method
            metadata = agent_api._extract_agent_metadata(agent_id, agent)
            agents.append(metadata)
            
        return agents
    except Exception as e:
        logger.error(f"Error getting agents: {str(e)}")
        return []

@app.get("/api/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get information about a specific agent."""
    initialized_agents = get_initialized_agents()
    agent = initialized_agents.get(agent_id)
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Extract agent metadata using the agent_api's method
    return agent_api._extract_agent_metadata(agent_id, agent)

# Chat routes
@app.get("/api/chat/{agent_id}/messages")
async def get_messages(agent_id: str, user_id: Optional[str] = None):
    """
    Get all messages for a specific agent.
    
    Args:
        agent_id: The ID of the agent
        user_id: Optional user ID to filter by
        
    Returns:
        A list of messages
    """
    try:
        # Get messages from the database, filtered by user_id if provided
        messages = ChatService.get_conversation_messages(agent_id, user_id)
        return messages
    except Exception as e:
        logger.error(f"Error getting messages for agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting messages: {str(e)}")

@app.get("/api/chat/{agent_id}/conversations")
async def get_conversations(agent_id: str, user_id: Optional[str] = None):
    """
    Get conversation history for a specific agent.
    
    Args:
        agent_id: The ID of the agent
        user_id: Optional user ID to filter by
        
    Returns:
        A list of conversations
    """
    try:
        # Get conversation history from the database, filtered by user_id if provided
        conversations = ChatService.get_conversation_history(agent_id, user_id)
        return conversations
    except Exception as e:
        logger.error(f"Error getting conversation history for agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting conversation history: {str(e)}")

@app.post("/api/chat/{agent_id}/conversations/{conversation_id}/activate")
async def activate_conversation(agent_id: str, conversation_id: int, user_id: Optional[str] = None):
    """
    Activate a specific conversation for an agent.
    
    Args:
        agent_id: The ID of the agent
        conversation_id: The ID of the conversation to activate
        user_id: Optional user ID to filter by
        
    Returns:
        The activated conversation
    """
    try:
        # Activate the conversation in the database
        conversation = ChatService.activate_conversation(conversation_id, agent_id, user_id)
        if conversation:
            return conversation
        else:
            raise HTTPException(status_code=404, detail=f"Conversation {conversation_id} not found")
    except Exception as e:
        logger.error(f"Error activating conversation {conversation_id} for agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error activating conversation: {str(e)}")

@app.delete("/api/chat/{agent_id}/conversations/{conversation_id}")
async def delete_conversation(agent_id: str, conversation_id: int):
    """
    Delete a specific conversation for an agent.
    
    Args:
        agent_id: The ID of the agent
        conversation_id: The ID of the conversation to delete
        
    Returns:
        A status message
    """
    try:
        # Delete the conversation in the database
        success = ChatService.delete_conversation(conversation_id)
        if success:
            return {"status": "success", "message": f"Conversation {conversation_id} deleted"}
        else:
            return {"status": "warning", "message": f"Conversation {conversation_id} not found"}
    except Exception as e:
        logger.error(f"Error deleting conversation {conversation_id} for agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting conversation: {str(e)}")

@app.delete("/api/chat/{agent_id}/messages")
async def clear_messages(agent_id: str, user_id: Optional[str] = None):
    """
    Clear all messages for a specific agent.
    
    Args:
        agent_id: The ID of the agent
        user_id: Optional user ID to filter by
        
    Returns:
        A status message
    """
    try:
        # Clear the conversation in the database
        success = ChatService.clear_conversation(agent_id, user_id)
        if success:
            return {"status": "success", "message": f"Conversation with agent {agent_id} cleared"}
        else:
            return {"status": "warning", "message": f"No active conversation found for agent {agent_id}"}
    except Exception as e:
        logger.error(f"Error clearing messages for agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error clearing messages: {str(e)}")

@app.post("/api/chat/{agent_id}/messages")
async def send_message(agent_id: str, message: MessageContent, user_id: Optional[str] = None):
    """
    Send a message to an agent and get a response.
    
    Args:
        agent_id: The ID of the agent
        message: The message content
        user_id: Optional user ID to filter by
        
    Returns:
        The created user message
    """
    try:
        # Create user message in the database
        user_message_id = str(uuid.uuid4())
        user_message = ChatService.add_message(
            agent_id=agent_id,
            role="user",
            content=message.content,
            timestamp=int(datetime.now().timestamp() * 1000),
            status="sent",
            message_id=user_message_id,
            user_id=user_id
        )
        
        # Get the agent from the initialized agents
        initialized_agents = get_initialized_agents()
        agent = initialized_agents.get(agent_id)
        
        if agent:
            try:
                # Initialize the conversation state
                state = {"messages": []}
                
                # Get all previous messages for context
                previous_messages = ChatService.get_messages_for_agent_state(agent_id, user_id)
                
                # Add all messages to the state
                state["messages"] = previous_messages
                
                # Invoke the agent
                logger.info(f"Invoking {agent_id} agent with {len(previous_messages)} previous messages")
                result = agent.invoke(state)
                logger.info(f"{agent_id} agent completed processing")
                
                # Extract the agent response
                agent_response = "No response from agent"
                messages = result.get("messages", [])
                
                # Log the message types for debugging
                logger.info(f"Result messages types: {[type(msg).__name__ for msg in messages]}")
                
                # Log all messages for debugging
                for i, msg in enumerate(messages):
                    if isinstance(msg, dict):
                        logger.info(f"Message {i} (dict): {msg}")
                    else:
                        msg_type = getattr(msg, "type", "N/A")
                        msg_content = getattr(msg, "content", "N/A")
                        
                        # Log tool usage more explicitly
                        if msg_type == "tool":
                            tool_name = getattr(msg, "name", "unknown_tool")
                            logger.info(f"Message {i} (ToolMessage): TOOL USED: {tool_name}, result={msg_content}")
                        else:
                            logger.info(f"Message {i} ({type(msg).__name__}): content={msg_content}, type={msg_type}, role={getattr(msg, 'role', 'N/A')}")
                
                # First try to find the last AIMessage
                for message_item in reversed(messages):
                    # Check if it's a LangChain message object
                    if hasattr(message_item, "content"):
                        # Check for AIMessage
                        if hasattr(message_item, "type") and message_item.type == "ai":
                            agent_response = message_item.content
                            logger.info(f"Found AI response in object (reversed): {agent_response[:50]}...")
                            break
                
                # If no AIMessage found, try other message types
                if agent_response == "No response from agent":
                    for message_item in messages:
                        # Check if the message is a dictionary
                        if isinstance(message_item, dict):
                            if message_item.get("role") == "assistant":
                                agent_response = message_item.get("content", "")
                                logger.info(f"Found assistant response in dict: {agent_response[:50]}...")
                                break
                        # Check if it's a LangChain message object
                        elif hasattr(message_item, "content"):
                            # Check for AIMessage, HumanMessage, etc.
                            msg_type = getattr(message_item, "type", None)
                            msg_role = getattr(message_item, "role", None)
                            
                            if msg_type == "assistant" or msg_role == "assistant":
                                agent_response = message_item.content
                                logger.info(f"Found assistant response in object: {agent_response[:50]}...")
                                break
                            elif msg_type == "ai" or msg_role == "ai":
                                agent_response = message_item.content
                                logger.info(f"Found AI response in object: {agent_response[:50]}...")
                                break
                
                # Create the agent message in the database
                agent_message = ChatService.add_message(
                    agent_id=agent_id,
                    role="assistant",
                    content=agent_response,
                    timestamp=int(datetime.now().timestamp() * 1000),
                    user_id=user_id
                )
                
            except Exception as e:
                logger.error(f"Error invoking {agent_id} agent: {str(e)}")
                
                # Create error message in the database
                agent_message = ChatService.add_message(
                    agent_id=agent_id,
                    role="assistant",
                    content=f"Error: {str(e)}",
                    timestamp=int(datetime.now().timestamp() * 1000),
                    status="error",
                    error=str(e),
                    user_id=user_id
                )
        else:
            # Agent not found
            logger.warning(f"Agent {agent_id} not found in registry")
            
            # Create error message in the database
            agent_message = ChatService.add_message(
                agent_id=agent_id,
                role="assistant",
                content=f"Error: Agent '{agent_id}' not found",
                timestamp=int(datetime.now().timestamp() * 1000),
                status="error",
                error=f"Agent '{agent_id}' not found",
                user_id=user_id
            )
        
        # Return the user message
        return user_message
    except Exception as e:
        logger.error(f"Error sending message to agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error sending message: {str(e)}")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    client_id = str(uuid.uuid4())
    await manager.connect(websocket, client_id)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data.get("action") == "join":
                query_id = data.get("query_id")
                if query_id:
                    await manager.connect(websocket, client_id, query_id)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"Client {client_id} disconnected")

# Import the agent registry
try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.agents.base import agent_registry
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.agents.base import agent_registry

# Custom log handler for WebSocket
class WebSocketLogHandler(logging.Handler):
    """Custom log handler to capture logs and send them to the client via WebSocket."""
    
    def __init__(self, websocket: WebSocket, message_id: str, loop=None):
        super().__init__()
        self.websocket = websocket
        self.message_id = message_id
        self.loop = loop or asyncio.get_event_loop()
        self.log_queue = []
        
    def emit(self, record):
        log_entry = self.format(record)
        
        # Store log in database
        try:
            ChatService.add_log_to_message(self.message_id, log_entry)
        except Exception as e:
            print(f"Error storing log in database: {e}")
        
        # Add to queue
        self.log_queue.append(log_entry)
        
        # Send log to client asynchronously
        try:
            # Use run_coroutine_threadsafe to properly handle the coroutine
            asyncio.run_coroutine_threadsafe(self._send_log(log_entry), self.loop)
        except Exception as e:
            # Don't raise exceptions from the log handler
            print(f"Error sending log: {e}")
    
    async def _send_log(self, log_entry: str):
        try:
            # Send log to client
            await self.websocket.send_json({
                "type": "log_update",
                "log": log_entry,
                "messageId": self.message_id
            })
        except Exception as e:
            # Don't raise exceptions from the log handler
            print(f"Error in _send_log: {e}")
    
    def get_logs(self):
        """Get all logs collected by this handler."""
        return self.log_queue

# Helper function to process attachments
async def process_attachments(attachments, temp_message_id=None):
    """Process attachments from the WebSocket message."""
    processed_attachments = []
    
    if not attachments:
        return processed_attachments
    
    # Generate a temporary message ID if not provided
    if temp_message_id is None:
        temp_message_id = f"temp_{str(uuid.uuid4())}"
    
    logger.info(f"Processing attachments with temporary message ID: {temp_message_id}")
    
    for attachment in attachments:
        # Create a database attachment
        db_attachment = None
        
        # If attachment has base64 data, store it
        if attachment.get('data'):
            try:
                # Decode base64 data
                file_data = base64.b64decode(attachment['data'])
                
                # Store in database with temporary message ID
                db_attachment = AttachmentService.add_attachment(
                    message_id=temp_message_id,  # Use temporary ID to satisfy NOT NULL constraint
                    attachment_type=attachment['type'],
                    filename=attachment['filename'],
                    content_type=attachment['contentType'],
                    size=attachment['size'],
                    data=file_data
                )
                
                # Add to processed attachments
                if db_attachment:
                    processed_attachments.append(db_attachment)
                
                logger.info(f"Stored attachment: {attachment['filename']} ({len(file_data)} bytes)")
            except Exception as e:
                logger.error(f"Error processing attachment: {str(e)}")
    
    return processed_attachments

# Helper function to format messages for LLM with image support
def format_messages_for_llm(messages):
    """Format messages for the LLM, including image attachments."""
    formatted_messages = []
    
    for msg in messages:
        # Basic message format
        formatted_msg = {
            "role": msg["role"],
            "content": []
        }
        
        # Add text content
        formatted_msg["content"].append({
            "type": "text",
            "text": msg["content"]
        })
        
        # Add image attachments if any
        if msg.get("attachments"):
            for attachment in msg["attachments"]:
                if attachment["type"].startswith("image/"):
                    # Get the image data
                    image_data = attachment.get("data")
                    
                    # If we don't have the data directly, try to get it from the attachment service
                    if not image_data and attachment.get("id"):
                        try:
                            attachment_details = AttachmentService.get_attachment(attachment["id"])
                            if attachment_details and attachment_details.get("data"):
                                image_data = attachment_details["data"]
                                logger.info(f"Retrieved image data from attachment service for ID: {attachment['id']}")
                        except Exception as e:
                            logger.error(f"Error retrieving attachment data: {str(e)}")
                    
                    if image_data:
                        # Add image content
                        image_url = f"data:{attachment['type']};base64,{image_data}"
                        formatted_msg["content"].append({
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        })
                        logger.info(f"Added image to message: {attachment['filename']} (base64 data redacted)")
                    else:
                        logger.warning(f"No image data found for attachment: {attachment['filename']}")
        
        formatted_messages.append(formatted_msg)
    
    return formatted_messages

@app.websocket("/ws/ui/{agent_id}")
async def ui_websocket_endpoint(websocket: WebSocket, agent_id: str):
    """
    WebSocket endpoint for UI events.
    
    This endpoint handles WebSocket connections for custom UI components.
    It allows the frontend to communicate with the backend for UI events.
    
    Args:
        websocket: The WebSocket connection
        agent_id: The agent ID
    """
    await handle_ui_websocket(websocket, agent_id)

@app.get("/api/agents/{agent_id}/ui-components")
async def get_agent_ui_components(agent_id: str):
    """Get the UI components for a specific agent."""
    try:
        # Import the UI component registry
        try:
            # Try importing with the full package path (for local development)
            from mosaic.backend.ui.base import ui_component_registry
            from mosaic.backend.agents.base import agent_registry
        except ImportError:
            # Fall back to relative import (for Docker environment)
            from backend.ui.base import ui_component_registry
            from backend.agents.base import agent_registry
        
        # Get the agent from the registry
        agent = agent_registry.get(agent_id)
        
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Get the components associated with this agent
        agent_components = agent_registry.get_ui_components(agent_id)
        
        if not agent_components:
            return {"components": []}
        
        # Format the component registrations
        registrations = []
        for component_id in agent_components:
            component = ui_component_registry.get(component_id)
            if component:
                registrations.append({
                    "id": component.component_id,
                    "name": component.name,
                    "description": component.description,
                    "features": component.required_features
                })
        
        return {"components": registrations}
    except Exception as e:
        logger.error(f"Error getting UI components for agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agents/{agent_id}/has-ui")
async def agent_has_ui(agent_id: str):
    """Check if an agent has UI components."""
    try:
        # Import the agent registry
        try:
            # Try importing with the full package path (for local development)
            from mosaic.backend.agents.base import agent_registry
        except ImportError:
            # Fall back to relative import (for Docker environment)
            from backend.agents.base import agent_registry
        
        # Get the agent from the registry
        agent = agent_registry.get(agent_id)
        
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Get the components associated with this agent
        agent_components = agent_registry.get_ui_components(agent_id)
        
        # Return whether the agent has UI components
        return {"hasUI": len(agent_components) > 0}
    except Exception as e:
        logger.error(f"Error checking if agent {agent_id} has UI components: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/chat/{agent_id}")
async def chat_websocket_endpoint(websocket: WebSocket, agent_id: str):
    client_id = str(uuid.uuid4())
    
    try:
        await websocket.accept()
        logger.info(f"Client {client_id} connected to chat with agent {agent_id}")
        
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "ping":
                # Respond to ping with a pong to keep the connection alive
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                })
                continue
            
            elif data.get("type") == "message":
                message_data = data.get("message", {})
                
                try:
                    # Generate a user message ID in advance
                    user_message_id = str(uuid.uuid4())
                    
                    # Process attachments if any
                    attachments = []
                    if message_data.get("attachments"):
                        logger.info(f"Processing {len(message_data['attachments'])} attachments for message {user_message_id}")
                        attachments = await process_attachments(message_data["attachments"], user_message_id)
                        logger.info(f"Processed {len(attachments)} attachments")
                    
                    # Create user message in the database
                    content = message_data.get("content", "")
                    
                    # Only add the special flag for the file_processing_supervisor agent
                    # and only for the internal state, not for display to the user
                    internal_content = content
                    if agent_id == "file_processing_supervisor" and message_data.get("attachments"):
                        # Get the first attachment
                        attachment = message_data["attachments"][0]
                        
                        # Get the attachment filename and type
                        filename = attachment.get("filename", "unknown_file")
                        content_type = attachment.get("contentType", "application/octet-stream")
                        
                        # Create a special flag based on the file type
                        if content_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" or content_type == "application/vnd.ms-excel" or filename.endswith(".xlsx") or filename.endswith(".xls"):
                            file_type = "Excel"
                        elif content_type.startswith("image/"):
                            file_type = "image"
                        elif content_type == "application/pdf":
                            file_type = "PDF"
                        elif content_type == "text/csv" or filename.endswith(".csv"):
                            file_type = "CSV"
                        elif content_type == "application/json" or filename.endswith(".json"):
                            file_type = "JSON"
                        elif content_type.startswith("text/"):
                            file_type = "text"
                        else:
                            file_type = "file"
                        
                        # Add the special flag to the internal content
                        if internal_content:
                            internal_content = f"{internal_content}\n\n[Attached {file_type} file: {filename}] Please use the transfer_to_file_processing tool to process this file."
                        else:
                            internal_content = f"[Attached {file_type} file: {filename}] Please use the transfer_to_file_processing tool to process this file."
                        
                        logger.info(f"Added special flag to internal message content for file_processing_supervisor: {internal_content}")
                    
                    # Get user_id from the message data if provided
                    user_id = message_data.get("userId")
                    
                    user_message = ChatService.add_message(
                        agent_id=agent_id,
                        role="user",
                        content=content,
                        timestamp=int(datetime.now().timestamp() * 1000),
                        status="sent",
                        message_id=user_message_id,
                        client_message_id=message_data.get("clientMessageId"),
                        user_id=user_id
                    )
                    
                    # Add attachments to the message
                    for attachment in attachments:
                        # Update the message_id for the attachment
                        AttachmentService.update_attachment_message(
                            attachment_id=attachment["id"],
                            message_id=user_message_id
                        )
                        
                        # Add attachment to the user message
                        if "attachments" not in user_message:
                            user_message["attachments"] = []
                        user_message["attachments"].append(attachment)
                    
                    # Send confirmation back to client
                    await websocket.send_json({
                        "type": "message",
                        "message": user_message
                    })
                    
                    # Create agent response with a unique ID
                    agent_message_id = str(uuid.uuid4())
                    
                    # Create initial log message
                    initial_log = f"{datetime.now().strftime('%H:%M:%S')} - Starting processing with {agent_id} agent"
                    
                    # Add initial log to the database
                    ChatService.add_log_to_message(agent_message_id, initial_log)
                    
                    # Send initial log message
                    await websocket.send_json({
                        "type": "log_update",
                        "log": initial_log,
                        "messageId": agent_message_id
                    })
                    
                    # Get the agent from the initialized agents
                    initialized_agents = get_initialized_agents()
                    agent = initialized_agents.get(agent_id)
                    
                    if agent:
                        # Set up a custom log handler to capture logs
                        ws_handler = WebSocketLogHandler(websocket, agent_message_id)
                        ws_handler.setLevel(logging.INFO)
                        ws_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', '%H:%M:%S'))
                        
                        # Add the handler to the agent's logger
                        agent_logger = logging.getLogger(f"mosaic.agents.{agent_id}")
                        agent_logger.addHandler(ws_handler)
                        
                        # For research_supervisor, also add the handler to the specialized agents' loggers
                        if agent_id == "research_supervisor":
                            # Add handler to web_search logger
                            web_search_logger = logging.getLogger("mosaic.agents.web_search")
                            web_search_logger.addHandler(ws_handler)
                            
                            # Add handler to browser_interaction logger
                            browser_interaction_logger = logging.getLogger("mosaic.agents.browser_interaction")
                            browser_interaction_logger.addHandler(ws_handler)
                            
                            # Add handler to data_processing logger
                            data_processing_logger = logging.getLogger("mosaic.agents.data_processing")
                            data_processing_logger.addHandler(ws_handler)
                            
                            # Add handler to literature logger
                            literature_logger = logging.getLogger("mosaic.agents.literature")
                            literature_logger.addHandler(ws_handler)
                            
                            logger.info("Added log handlers to all specialized agents for research_supervisor")
                        
                        try:
                            # Initialize the conversation state
                            state = {"messages": []}
                            
                            # Get all previous messages for context
                            previous_messages = ChatService.get_messages_for_agent_state(agent_id, user_id)
                            
                            # If this is the file_processing_supervisor agent, modify the last message to include the special flag
                            if agent_id == "file_processing_supervisor" and previous_messages:
                                # Find the last user message
                                for i in range(len(previous_messages) - 1, -1, -1):
                                    if isinstance(previous_messages[i], dict) and previous_messages[i].get("role") == "user":
                                        # Check if this message has attachments
                                        if previous_messages[i].get("attachments"):
                                            # Get the original content
                                            content = previous_messages[i].get("content", "")
                                            
                                            # Get the first attachment
                                            attachment = previous_messages[i]["attachments"][0]
                                            
                                            # Get the attachment filename and type
                                            filename = attachment.get("filename", "unknown_file")
                                            content_type = attachment.get("contentType", "application/octet-stream")
                                            
                                            # Create a special flag based on the file type
                                            if content_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" or content_type == "application/vnd.ms-excel" or filename.endswith(".xlsx") or filename.endswith(".xls"):
                                                file_type = "Excel"
                                            elif content_type.startswith("image/"):
                                                file_type = "image"
                                            elif content_type == "application/pdf":
                                                file_type = "PDF"
                                            elif content_type == "text/csv" or filename.endswith(".csv"):
                                                file_type = "CSV"
                                            elif content_type == "application/json" or filename.endswith(".json"):
                                                file_type = "JSON"
                                            elif content_type.startswith("text/"):
                                                file_type = "text"
                                            else:
                                                file_type = "file"
                                            
                                            # Add the special flag to the content
                                            if content:
                                                previous_messages[i]["content"] = f"{content}\n\n[Attached {file_type} file: {filename}] Please use the transfer_to_file_processing tool to process this file."
                                            else:
                                                previous_messages[i]["content"] = f"[Attached {file_type} file: {filename}] Please use the transfer_to_file_processing tool to process this file."
                                            
                                            logger.info(f"Added special flag to message content for file_processing_supervisor in state: {previous_messages[i]['content']}")
                                        break
                            
                            # Check if we have any image attachments
                            has_images = False
                            for msg in previous_messages:
                                if msg.get("attachments"):
                                    for attachment in msg.get("attachments", []):
                                        if attachment.get("type", "").startswith("image/"):
                                            has_images = True
                                            break
                            
                            # If we have images, format messages for vision model
                            if has_images:
                                logger.info("Detected image attachments, formatting for vision model")
                                formatted_messages = format_messages_for_llm(previous_messages)
                                state["messages"] = formatted_messages
                                state["use_vision"] = True
                                
                                # Log the formatted messages (without the actual base64 data)
                                log_formatted_messages = []
                                for msg in formatted_messages:
                                    log_msg = msg.copy()
                                    if "content" in log_msg and isinstance(log_msg["content"], list):
                                        log_content = []
                                        for content_item in log_msg["content"]:
                                            if content_item.get("type") == "image_url":
                                                log_content.append({
                                                    "type": "image_url",
                                                    "image_url": {"url": "[IMAGE DATA]"}
                                                })
                                            else:
                                                log_content.append(content_item)
                                        log_msg["content"] = log_content
                                    log_formatted_messages.append(log_msg)
                                
                                logger.info(f"Formatted messages for vision model (with image data redacted)")
                            else:
                                # Add all messages to the state in standard format
                                state["messages"] = previous_messages
                            
                            # Invoke the agent
                            logger.info(f"Invoking {agent_id} agent with {len(previous_messages)} previous messages")
                            result = agent.invoke(state)
                            logger.info(f"{agent_id} agent completed processing")
                            
                            # Extract the agent response
                            agent_response = "No response from agent"
                            messages = result.get("messages", [])
                            
                            # Log the message types for debugging
                            logger.info(f"Result messages types: {[type(msg).__name__ for msg in messages]}")
                            
                            # Log all messages for debugging (with image data redacted)
                            for i, msg in enumerate(messages):
                                if isinstance(msg, dict):
                                    # Create a redacted copy of the message for logging
                                    log_msg = msg.copy()
                                    if "content" in log_msg and isinstance(log_msg["content"], list):
                                        # Redact image data in content array
                                        for j, content_item in enumerate(log_msg["content"]):
                                            if isinstance(content_item, dict) and content_item.get("type") == "image_url":
                                                log_msg["content"][j] = {"type": "image_url", "image_url": {"url": "[IMAGE DATA REDACTED]"}}
                                    logger.info(f"Message {i} (dict): {log_msg}")
                                else:
                                    msg_type = getattr(msg, "type", "N/A")
                                    
                                    # Log tool usage more explicitly
                                    if msg_type == "tool":
                                        tool_name = getattr(msg, "name", "unknown_tool")
                                        logger.info(f"Message {i} (ToolMessage): TOOL USED: {tool_name}")
                                    else:
                                        # Don't log the actual content which might contain base64 data
                                        logger.info(f"Message {i} ({type(msg).__name__}): type={msg_type}, role={getattr(msg, 'role', 'N/A')}")
                            
                            # First try to find the last AIMessage
                            for message_item in reversed(messages):
                                # Check if it's a LangChain message object
                                if hasattr(message_item, "content"):
                                    # Check for AIMessage
                                    if hasattr(message_item, "type") and message_item.type == "ai":
                                        agent_response = message_item.content
                                        logger.info(f"Found AI response in object (reversed): {agent_response[:50]}...")
                                        break
                            
                            # If no AIMessage found, try other message types
                            if agent_response == "No response from agent":
                                for message_item in messages:
                                    # Check if the message is a dictionary
                                    if isinstance(message_item, dict):
                                        if message_item.get("role") == "assistant":
                                            agent_response = message_item.get("content", "")
                                            logger.info(f"Found assistant response in dict: {agent_response[:50]}...")
                                            break
                                    # Check if it's a LangChain message object
                                    elif hasattr(message_item, "content"):
                                        # Check for AIMessage, HumanMessage, etc.
                                        msg_type = getattr(message_item, "type", None)
                                        msg_role = getattr(message_item, "role", None)
                                        
                                        if msg_type == "assistant" or msg_role == "assistant":
                                            agent_response = message_item.content
                                            logger.info(f"Found assistant response in object: {agent_response[:50]}...")
                                            break
                                        elif msg_type == "ai" or msg_role == "ai":
                                            agent_response = message_item.content
                                            logger.info(f"Found AI response in object: {agent_response[:50]}...")
                                            break
                            
                            # Create the agent message in the database
                            agent_message = ChatService.add_message(
                                agent_id=agent_id,
                                role="assistant",
                                content=agent_response,
                                timestamp=int(datetime.now().timestamp() * 1000),
                                message_id=agent_message_id,
                                user_id=user_id
                            )
                            
                            # Send agent response back to client with a small delay
                            # This ensures the logs have time to be processed
                            await asyncio.sleep(0.5)
                            
                            # Log that we're sending the response
                            logger.info(f"Sending agent response back to client: {agent_message['id']}")
                            
                            # Add logs to the message for the response
                            agent_message["logs"] = ws_handler.get_logs()
                            
                            await websocket.send_json({
                                "type": "message",
                                "message": agent_message
                            })
                        
                        except Exception as e:
                            logger.error(f"Error invoking {agent_id} agent: {str(e)}")
                            
                            # Create error message in the database
                            error_message = ChatService.add_message(
                                agent_id=agent_id,
                                role="assistant",
                                content=f"Error: {str(e)}",
                                timestamp=int(datetime.now().timestamp() * 1000),
                                status="error",
                                error=str(e),
                                message_id=agent_message_id,
                                user_id=user_id
                            )
                            
                            # Add logs to the message for the response
                            error_message["logs"] = ws_handler.get_logs()
                            
                            # Send error message back to client
                            await websocket.send_json({
                                "type": "message",
                                "message": error_message
                            })
                        
                        finally:
                            # Remove the custom log handler from the agent's logger
                            if ws_handler in agent_logger.handlers:
                                agent_logger.removeHandler(ws_handler)
                            
                            # For research_supervisor, also remove the handler from the specialized agents' loggers
                            if agent_id == "research_supervisor":
                                # Remove handler from web_search logger
                                web_search_logger = logging.getLogger("mosaic.agents.web_search")
                                if ws_handler in web_search_logger.handlers:
                                    web_search_logger.removeHandler(ws_handler)
                                
                                # Remove handler from browser_interaction logger
                                browser_interaction_logger = logging.getLogger("mosaic.agents.browser_interaction")
                                if ws_handler in browser_interaction_logger.handlers:
                                    browser_interaction_logger.removeHandler(ws_handler)
                                
                                # Remove handler from data_processing logger
                                data_processing_logger = logging.getLogger("mosaic.agents.data_processing")
                                if ws_handler in data_processing_logger.handlers:
                                    data_processing_logger.removeHandler(ws_handler)
                                
                                # Remove handler from literature logger
                                literature_logger = logging.getLogger("mosaic.agents.literature")
                                if ws_handler in literature_logger.handlers:
                                    literature_logger.removeHandler(ws_handler)
                                
                                logger.info("Removed log handlers from all specialized agents for research_supervisor")
                    
                    else:
                        # Agent not found
                        logger.warning(f"Agent {agent_id} not found in registry")
                        
                        # Create error message in the database
                        agent_message = ChatService.add_message(
                            agent_id=agent_id,
                            role="assistant",
                            content=f"Error: Agent '{agent_id}' not found",
                            timestamp=int(datetime.now().timestamp() * 1000),
                            status="error",
                            error=f"Agent '{agent_id}' not found",
                            message_id=agent_message_id,
                            user_id=user_id
                        )
                        
                        # Send agent response back to client
                        await websocket.send_json({
                            "type": "message",
                            "message": agent_message
                        })
                
                except Exception as e:
                    logger.error(f"Error processing message: {str(e)}")
                    
                    # Send error message back to client
                    await websocket.send_json({
                        "type": "error",
                        "error": f"Error processing message: {str(e)}"
                    })
            
            elif data.get("type") == "clear_conversation":
                try:
                    # Get user_id from the data if provided
                    user_id = data.get("userId")
                    
                    # Clear the conversation in the database
                    success = ChatService.clear_conversation(agent_id, user_id)
                    
                    # Send confirmation back to client
                    await websocket.send_json({
                        "type": "conversation_cleared",
                        "success": success,
                        "timestamp": datetime.now().isoformat()
                    })
                
                except Exception as e:
                    logger.error(f"Error clearing conversation: {str(e)}")
                    
                    # Send error message back to client
                    await websocket.send_json({
                        "type": "error",
                        "error": f"Error clearing conversation: {str(e)}"
                    })
            
    except WebSocketDisconnect:
        logger.info(f"Client {client_id} disconnected from chat with agent {agent_id}")

async def simulate_agent_processing(websocket: WebSocket, agent_id: str, content: str, message_id: str):
    """Simulate agent processing with log messages."""
    # Initial planning phase
    await websocket.send_json({
        "type": "log_update",
        "log": f"{datetime.now().strftime('%H:%M:%S')} - {agent_id}: Planning response strategy",
        "messageId": message_id
    })
    await asyncio.sleep(0.5)
    
    # Agent-specific processing logs
    if agent_id == "calculator":
        await websocket.send_json({
            "type": "log_update",
            "log": f"{datetime.now().strftime('%H:%M:%S')} - {agent_id}: Parsing mathematical expression",
            "messageId": message_id
        })
        await asyncio.sleep(0.3)
        
        await websocket.send_json({
            "type": "log_update",
            "log": f"{datetime.now().strftime('%H:%M:%S')} - {agent_id}: Evaluating expression",
            "messageId": message_id
        })
        await asyncio.sleep(0.3)
        
    elif agent_id == "safety":
        await websocket.send_json({
            "type": "log_update",
            "log": f"{datetime.now().strftime('%H:%M:%S')} - {agent_id}: Analyzing content for safety concerns",
            "messageId": message_id
        })
        await asyncio.sleep(0.3)
        
        await websocket.send_json({
            "type": "log_update",
            "log": f"{datetime.now().strftime('%H:%M:%S')} - {agent_id}: Checking against security rules",
            "messageId": message_id
        })
        await asyncio.sleep(0.3)
        
    elif agent_id == "writer":
        await websocket.send_json({
            "type": "log_update",
            "log": f"{datetime.now().strftime('%H:%M:%S')} - {agent_id}: Analyzing file operation request",
            "messageId": message_id
        })
        await asyncio.sleep(0.3)
        
        await websocket.send_json({
            "type": "log_update",
            "log": f"{datetime.now().strftime('%H:%M:%S')} - {agent_id}: Validating file paths and permissions",
            "messageId": message_id
        })
        await asyncio.sleep(0.3)
        
    elif agent_id == "developer":
        await websocket.send_json({
            "type": "log_update",
            "log": f"{datetime.now().strftime('%H:%M:%S')} - {agent_id}: Analyzing code requirements",
            "messageId": message_id
        })
        await asyncio.sleep(0.3)
        
        await websocket.send_json({
            "type": "log_update",
            "log": f"{datetime.now().strftime('%H:%M:%S')} - {agent_id}: Generating code solution",
            "messageId": message_id
        })
        await asyncio.sleep(0.3)
    
    elif agent_id == "research_supervisor":
        await websocket.send_json({
            "type": "log_update",
            "log": f"{datetime.now().strftime('%H:%M:%S')} - {agent_id}: Analyzing research query",
            "messageId": message_id
        })
        await asyncio.sleep(0.3)
        
        await websocket.send_json({
            "type": "log_update",
            "log": f"{datetime.now().strftime('%H:%M:%S')} - {agent_id}: Delegating to specialized agents",
            "messageId": message_id
        })
        await asyncio.sleep(0.3)
        
        await websocket.send_json({
            "type": "log_update",
            "log": f"{datetime.now().strftime('%H:%M:%S')} - {agent_id}: Gathering information from multiple sources",
            "messageId": message_id
        })
        await asyncio.sleep(0.3)
    
    # Final processing phase
    await websocket.send_json({
        "type": "log_update",
        "log": f"{datetime.now().strftime('%H:%M:%S')} - {agent_id}: Formulating response",
        "messageId": message_id
    })
    await asyncio.sleep(0.3)
    
    await websocket.send_json({
        "type": "log_update",
        "log": f"{datetime.now().strftime('%H:%M:%S')} - {agent_id}: Response ready",
        "messageId": message_id
    })

# Import the agent runner module to get initialized agents
try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.app.agent_runner import initialize_agents, get_initialized_agents
    from mosaic.backend.app.ui_component_discovery import discover_and_register_components
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.app.agent_runner import initialize_agents, get_initialized_agents
    from backend.app.ui_component_discovery import discover_and_register_components

# Import the UI WebSocket handler, connection manager, and request tracker
try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.app.agent_api import agent_api
    from mosaic.backend.app.ui_websocket_handler import handle_ui_websocket, start_cleanup_task
    from mosaic.backend.app.request_tracker import request_tracker
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.app.agent_api import agent_api
    from backend.app.ui_websocket_handler import handle_ui_websocket, start_cleanup_task
    from backend.app.request_tracker import request_tracker

# Initialize the agents on startup
@app.on_event("startup")
async def startup_event():
    """Initialize the agents, UI components, and database on startup."""
    # Initialize the database
    logger.info("Initializing database")
    init_db()
    logger.info("Database initialized")
    
    # Discover and register UI components first
    logger.info("Discovering and registering UI components")
    ui_components = discover_and_register_components()
    logger.info(f"Registered {len(ui_components)} UI components")
    
    # Initialize the agents after UI components are registered
    logger.info("Initializing agents")
    initialize_agents()
    logger.info("Agents initialized")
    
    # Start the UI connection manager cleanup task
    logger.info("Starting UI connection manager cleanup task")
    start_cleanup_task()
    logger.info("UI connection manager cleanup task started")

# Close database connection and request tracker on shutdown
@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection and request tracker on shutdown."""
    try:
        # Try importing with the full package path (for local development)
        from mosaic.backend.database import close_db_connection
    except ImportError:
        # Fall back to relative import (for Docker environment)
        from backend.database import close_db_connection
    
    logger.info("Closing database connection")
    close_db_connection()
    logger.info("Database connection closed")
    
    # Close the request tracker
    logger.info("Closing request tracker")
    request_tracker.close()
    logger.info("Request tracker closed")

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
