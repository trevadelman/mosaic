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
    return {
        "initialized_agents": list(initialized_agents.keys()),
        "registry_agents": agent_registry.list_agents(),
        "openai_api_key_set": bool(os.getenv("OPENAI_API_KEY")),
        "environment": os.getenv("ENVIRONMENT", "unknown"),
        "cors_origins": os.getenv("CORS_ORIGINS", "").split(",")
    }

# Agent routes
@app.get("/api/agents")
async def get_agents():
    """Get a list of all available agents."""
    try:
        agents = []
        for agent_id, agent in initialized_agents.items():
            if agent_id == "calculator":
                agents.append({
                    "id": agent.name,
                    "name": agent.name.capitalize(),
                    "description": agent.description,
                    "type": "Utility",
                    "capabilities": ["Basic Math", "Equations", "Unit Conversion"],
                    "icon": "🧮"
                })
            elif agent_id == "research_supervisor":
                agents.append({
                    "id": agent_id,
                    "name": "Research Assistant",
                    "description": "Research assistant that can search the web, browse websites, process data, and find academic papers",
                    "type": "Supervisor",
                    "capabilities": ["Web Search", "Content Retrieval", "Data Processing", "Academic Research"],
                    "icon": "🔍"
                })
            else:
                agents.append({
                    "id": agent.name,
                    "name": agent.name.capitalize(),
                    "description": agent.description,
                    "type": "Utility",
                    "capabilities": [],
                    "icon": "🤖"
                })
        return agents
    except Exception as e:
        logger.error(f"Error getting agents: {str(e)}")
        return []

@app.get("/api/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get information about a specific agent."""
    agent = initialized_agents.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    if agent_id == "calculator":
        return {
            "id": agent.name,
            "name": agent.name.capitalize(),
            "description": agent.description,
            "type": "Utility",
            "capabilities": ["Basic Math", "Equations", "Unit Conversion"],
            "icon": "🧮"
        }
    elif agent_id == "research_supervisor":
        return {
            "id": agent_id,
            "name": "Research Assistant",
            "description": "Research assistant that can search the web, browse websites, process data, and find academic papers",
            "type": "Supervisor",
            "capabilities": ["Web Search", "Content Retrieval", "Data Processing", "Academic Research"],
            "icon": "🔍"
        }
    else:
        return {
            "id": agent.name,
            "name": agent.name.capitalize(),
            "description": agent.description,
            "type": "Utility",
            "capabilities": [],
            "icon": "🤖"
        }

# Chat routes
@app.get("/api/chat/{agent_id}/messages")
async def get_messages(agent_id: str):
    """Get all messages for a specific agent."""
    if agent_id not in MESSAGE_STORE:
        MESSAGE_STORE[agent_id] = []
    return MESSAGE_STORE[agent_id]

@app.post("/api/chat/{agent_id}/messages")
async def send_message(agent_id: str, message: MessageContent):
    """Send a message to an agent and get a response."""
    if agent_id not in MESSAGE_STORE:
        MESSAGE_STORE[agent_id] = []
    
    # Create user message
    user_message = {
        "id": str(uuid.uuid4()),
        "role": "user",
        "content": message.content,
        "timestamp": int(datetime.now().timestamp() * 1000),
        "agentId": agent_id,
        "status": "sent"
    }
    
    # Add user message to history
    MESSAGE_STORE[agent_id].append(user_message)
    
    # Get the agent from the initialized agents
    agent = initialized_agents.get(agent_id)
    
    if agent:
        try:
            # Initialize the conversation state
            state = {"messages": []}
            
            # Add the user message to the state
            state["messages"].append({
                "role": "user",
                "content": message.content
            })
            
            # Invoke the agent
            logger.info(f"Invoking {agent_id} agent")
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
            
            # Create the agent message
            agent_message = {
                "id": str(uuid.uuid4()),
                "role": "assistant",
                "content": agent_response,
                "timestamp": int(datetime.now().timestamp() * 1000),
                "agentId": agent_id
            }
            
        except Exception as e:
            logger.error(f"Error invoking {agent_id} agent: {str(e)}")
            
            # Create error message
            agent_message = {
                "id": str(uuid.uuid4()),
                "role": "assistant",
                "content": f"Error: {str(e)}",
                "timestamp": int(datetime.now().timestamp() * 1000),
                "agentId": agent_id,
                "status": "error",
                "error": str(e)
            }
    else:
        # Agent not found
        logger.warning(f"Agent {agent_id} not found in registry")
        
        # Create error message
        agent_message = {
            "id": str(uuid.uuid4()),
            "role": "assistant",
            "content": f"Error: Agent '{agent_id}' not found",
            "timestamp": int(datetime.now().timestamp() * 1000),
            "agentId": agent_id,
            "status": "error",
            "error": f"Agent '{agent_id}' not found"
        }
    
    # Add agent message to history
    MESSAGE_STORE[agent_id].append(agent_message)
    
    # Return the user message
    return user_message

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
        
        # Store log in message store directly (synchronously)
        for agent_id, messages in MESSAGE_STORE.items():
            for message in messages:
                if message.get("id") == self.message_id:
                    if "logs" not in message:
                        message["logs"] = []
                    message["logs"].append(log_entry)
                    break
        
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
                
                # Create user message
                user_message = {
                    "id": str(uuid.uuid4()),
                    "role": "user",
                    "content": message_data.get("content", ""),
                    "timestamp": int(datetime.now().timestamp() * 1000),
                    "agentId": agent_id,
                    "status": "sent",
                    "clientMessageId": message_data.get("clientMessageId")  # Pass through client message ID
                }
                
                # Add user message to history
                if agent_id not in MESSAGE_STORE:
                    MESSAGE_STORE[agent_id] = []
                MESSAGE_STORE[agent_id].append(user_message)
                
                # Send confirmation back to client
                await websocket.send_json({
                    "type": "message",
                    "message": user_message
                })
                
                # Create agent response with a unique ID
                agent_message_id = str(uuid.uuid4())
                
                # Create initial log message
                initial_log = f"{datetime.now().strftime('%H:%M:%S')} - Starting processing with {agent_id} agent"
                
                # Send initial log message
                await websocket.send_json({
                    "type": "log_update",
                    "log": initial_log,
                    "messageId": agent_message_id
                })
                
                # Get the agent from the initialized agents
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
                        
                        # Add the user message to the state
                        state["messages"].append({
                            "role": "user",
                            "content": message_data.get("content", "")
                        })
                        
                        # Invoke the agent
                        logger.info(f"Invoking {agent_id} agent")
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
                        
                        # Get all logs from the message store
                        logs = [initial_log]
                        for agent_id_key, messages in MESSAGE_STORE.items():
                            for message in messages:
                                if message.get("id") == agent_message_id and "logs" in message:
                                    logs = message.get("logs", [])
                                    break
                        
                        # Create the agent message with logs
                        agent_message = {
                            "id": agent_message_id,
                            "role": "assistant",
                            "content": agent_response,
                            "timestamp": int(datetime.now().timestamp() * 1000),
                            "agentId": agent_id,
                            "logs": ws_handler.get_logs()  # Include all logs from the handler
                        }
                        
                        # Add agent message to history
                        MESSAGE_STORE[agent_id].append(agent_message)
                        
                        # Send agent response back to client with a small delay
                        # This ensures the logs have time to be processed
                        await asyncio.sleep(0.5)
                        
                        # Log that we're sending the response
                        logger.info(f"Sending agent response back to client: {agent_message['id']}")
                        
                        await websocket.send_json({
                            "type": "message",
                            "message": agent_message
                        })
                    
                    except Exception as e:
                        logger.error(f"Error invoking {agent_id} agent: {str(e)}")
                        
                        # Send error message
                        error_message = {
                            "id": agent_message_id,
                            "role": "assistant",
                            "content": f"Error: {str(e)}",
                            "timestamp": int(datetime.now().timestamp() * 1000),
                            "agentId": agent_id,
                            "status": "error",
                            "error": str(e)
                        }
                        
                        # Add error message to history
                        MESSAGE_STORE[agent_id].append(error_message)
                        
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
                    
                    # Create error message
                    agent_message = {
                        "id": agent_message_id,
                        "role": "assistant",
                        "content": f"Error: Agent '{agent_id}' not found",
                        "timestamp": int(datetime.now().timestamp() * 1000),
                        "agentId": agent_id,
                        "status": "error",
                        "error": f"Agent '{agent_id}' not found"
                    }
                    
                    # Add agent message to history
                    MESSAGE_STORE[agent_id].append(agent_message)
                    
                    # Send agent response back to client
                    await websocket.send_json({
                        "type": "message",
                        "message": agent_message
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

# Global variable to store the initialized agents
initialized_agents = {}

# Initialize the agents
def initialize_agents():
    """Initialize the agents and register them with the agent registry."""
    global initialized_agents
    
    try:
        # Try importing with the full package path (for local development)
        from mosaic.backend.agents import register_calculator_agent
        from mosaic.backend.agents.web_search import register_web_search_agent
        from mosaic.backend.agents.browser_interaction import register_browser_interaction_agent
        from mosaic.backend.agents.data_processing import register_data_processing_agent
        from mosaic.backend.agents.literature import register_literature_agent
        from mosaic.backend.agents.supervisor import create_research_supervisor
        from langchain_openai import ChatOpenAI
    except ImportError:
        try:
            # Fall back to relative import (for Docker environment)
            from backend.agents import register_calculator_agent
            from backend.agents.web_search import register_web_search_agent
            from backend.agents.browser_interaction import register_browser_interaction_agent
            from backend.agents.data_processing import register_data_processing_agent
            from backend.agents.literature import register_literature_agent
            from backend.agents.supervisor import create_research_supervisor
            from langchain_openai import ChatOpenAI
        except ImportError:
            logger.error("Failed to import agent modules. Agents will not be available.")
            return
    
    try:
        # Check if the OpenAI API key is set
        if not os.getenv("OPENAI_API_KEY"):
            logger.warning("OPENAI_API_KEY not set. Agents will not be available.")
            return
        
        # Initialize the language model
        logger.info("Initializing language model")
        model = ChatOpenAI(model="gpt-4o-mini")
        
        # Register the calculator agent
        logger.info("Registering calculator agent")
        calculator = register_calculator_agent(model)
        initialized_agents["calculator"] = calculator
        
        # Register specialized agents for the research supervisor
        logger.info("Registering specialized agents for research supervisor")
        web_search = register_web_search_agent(model)
        browser_interaction = register_browser_interaction_agent(model)
        data_processing = register_data_processing_agent(model)
        literature = register_literature_agent(model)
        
        # Create the research supervisor
        logger.info("Creating research supervisor")
        research_supervisor = create_research_supervisor(model)
        initialized_agents["research_supervisor"] = research_supervisor
        
        # Log the registered agents
        logger.info(f"Registered agents: {agent_registry.list_agents()}")
        logger.info(f"Initialized agents: {list(initialized_agents.keys())}")
        
        logger.info("Agents initialized and registered successfully")
    except Exception as e:
        logger.error(f"Error initializing agents: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

# Initialize the agents on startup
@app.on_event("startup")
async def startup_event():
    """Initialize the agents on startup."""
    initialize_agents()

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
