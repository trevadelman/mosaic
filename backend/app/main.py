from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
import os
import uuid
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

# Import database modules
try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.database import init_db, ChatService, AttachmentService
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.database import init_db, ChatService, AttachmentService

# Import the agent API router
try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.app.agent_api import get_agent_api_router
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.app.agent_api import get_agent_api_router

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

# Include the agent API router
app.include_router(get_agent_api_router())

# Configure CORS
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://frontend:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
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

class Message(BaseModel):
    id: str
    role: str
    content: str
    timestamp: int
    agentId: Optional[str] = None
    status: Optional[str] = None
    error: Optional[str] = None

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

# Import the agent API for metadata extraction
try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.app.agent_api import agent_api
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.app.agent_api import agent_api

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
async def get_messages(agent_id: str):
    """Get all messages for a specific agent."""
    try:
        # Get messages from the database
        messages = ChatService.get_conversation_messages(agent_id)
        return messages
    except Exception as e:
        logger.error(f"Error getting messages for agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting messages: {str(e)}")

@app.delete("/api/chat/{agent_id}/messages")
async def clear_messages(agent_id: str):
    """Clear all messages for a specific agent."""
    try:
        # Clear the conversation in the database
        success = ChatService.clear_conversation(agent_id)
        if success:
            return {"status": "success", "message": f"Conversation with agent {agent_id} cleared"}
        else:
            return {"status": "warning", "message": f"No active conversation found for agent {agent_id}"}
    except Exception as e:
        logger.error(f"Error clearing messages for agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error clearing messages: {str(e)}")

@app.post("/api/chat/{agent_id}/messages")
async def send_message(agent_id: str, message: MessageContent):
    """Send a message to an agent and get a response."""
    try:
        # Create user message in the database
        user_message_id = str(uuid.uuid4())
        user_message = ChatService.add_message(
            agent_id=agent_id,
            role="user",
            content=message.content,
            timestamp=int(datetime.now().timestamp() * 1000),
            status="sent",
            message_id=user_message_id
        )
        
        # Get the agent from the initialized agents
        initialized_agents = get_initialized_agents()
        agent = initialized_agents.get(agent_id)
        
        if agent:
            try:
                # Initialize the conversation state
                state = {"messages": []}
                
                # Get all previous messages for context
                previous_messages = ChatService.get_messages_for_agent_state(agent_id)
                
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
                    timestamp=int(datetime.now().timestamp() * 1000)
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
                    error=str(e)
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
                error=f"Agent '{agent_id}' not found"
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
                    # Create user message in the database
                    user_message_id = str(uuid.uuid4())
                    user_message = ChatService.add_message(
                        agent_id=agent_id,
                        role="user",
                        content=message_data.get("content", ""),
                        timestamp=int(datetime.now().timestamp() * 1000),
                        status="sent",
                        message_id=user_message_id,
                        client_message_id=message_data.get("clientMessageId")
                    )
                    
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
                            previous_messages = ChatService.get_messages_for_agent_state(agent_id)
                            
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
                                message_id=agent_message_id
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
                                message_id=agent_message_id
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
                            message_id=agent_message_id
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
                    # Clear the conversation in the database
                    success = ChatService.clear_conversation(agent_id)
                    
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
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.app.agent_runner import initialize_agents, get_initialized_agents

# Initialize the agents on startup
@app.on_event("startup")
async def startup_event():
    """Initialize the agents and database on startup."""
    # Initialize the database
    logger.info("Initializing database")
    init_db()
    logger.info("Database initialized")
    
    # Initialize the agents
    initialize_agents()

# Close database connection on shutdown
@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown."""
    from mosaic.backend.database import close_db_connection
    logger.info("Closing database connection")
    close_db_connection()
    logger.info("Database connection closed")

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
