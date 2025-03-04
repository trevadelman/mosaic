"""
Agent API Module for MOSAIC

This module provides dynamic API endpoint generation for agents.
It extracts agent routes from main.py and creates agent-specific API modules.
"""

import logging
import os
import uuid
import asyncio
from typing import List, Dict, Any, Optional, Type, Callable
from datetime import datetime
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("mosaic.agent_api")

# Import the agent registry
try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.agents.base import BaseAgent, agent_registry
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.agents.base import BaseAgent, agent_registry

# Import the agent runner module to get initialized agents
from app.agent_runner import get_initialized_agents

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

# Message storage
MESSAGE_STORE = {}

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

class AgentAPI:
    """
    Class for generating dynamic API endpoints for agents.
    """
    
    def __init__(self):
        """Initialize the agent API."""
        self.router = APIRouter(prefix="/api/agents", tags=["agents"])
        self.agent_routers = {}
        self.message_store = MESSAGE_STORE
        
        # Set up the base routes
        self._setup_base_routes()
    
    def _setup_base_routes(self):
        """Set up the base routes for the agent API."""
        
        @self.router.get("")
        async def get_agents():
            """Get a list of all available agents."""
            try:
                initialized_agents = get_initialized_agents()
                agents = []
                
                for agent_id, agent in initialized_agents.items():
                    # Extract agent metadata
                    metadata = self._extract_agent_metadata(agent_id, agent)
                    agents.append(metadata)
                
                return agents
            except Exception as e:
                logger.error(f"Error getting agents: {str(e)}")
                return []
        
        @self.router.get("/{agent_id}")
        async def get_agent(agent_id: str):
            """Get information about a specific agent."""
            initialized_agents = get_initialized_agents()
            agent = initialized_agents.get(agent_id)
            
            if not agent:
                raise HTTPException(status_code=404, detail="Agent not found")
            
            # Extract agent metadata
            metadata = self._extract_agent_metadata(agent_id, agent)
            return metadata
        
        @self.router.get("/{agent_id}/capabilities")
        async def get_agent_capabilities(agent_id: str):
            """Get the capabilities of a specific agent."""
            initialized_agents = get_initialized_agents()
            agent = initialized_agents.get(agent_id)
            
            if not agent:
                raise HTTPException(status_code=404, detail="Agent not found")
            
            # Extract agent capabilities
            capabilities = self._extract_agent_capabilities(agent)
            return {"capabilities": capabilities}
    
    def _extract_agent_metadata(self, agent_id: str, agent: Any) -> Dict[str, Any]:
        """
        Extract metadata from an agent.
        
        Args:
            agent_id: The ID of the agent
            agent: The agent object
            
        Returns:
            A dictionary containing agent metadata
        """
        # Check if the agent is a CompiledStateGraph (supervisor)
        is_supervisor = not hasattr(agent, 'description')
        
        # Default metadata
        if is_supervisor:
            # For supervisor agents, use agent_id as the name
            metadata = {
                "id": agent_id,
                "name": agent_id.capitalize(),
                "description": "A supervisor agent that orchestrates multiple specialized agents",
                "type": "Supervisor",
                "capabilities": [],
                "icon": "👨‍💼"
            }
        else:
            # For regular agents, use agent attributes
            metadata = {
                "id": agent.name,
                "name": agent.name.capitalize(),
                "description": agent.description,
                "type": "Utility",
                "capabilities": [],
                "icon": "🤖"
            }
        
        # Special cases for known agent types
        if agent_id == "calculator":
            metadata.update({
                "capabilities": ["Basic Math", "Equations", "Unit Conversion"],
                "icon": "🧮"
            })
        elif agent_id == "research_supervisor":
            metadata.update({
                "name": "Research Assistant",
                "description": "Research assistant that can search the web, browse websites, process data, and find academic papers",
                "type": "Supervisor",
                "capabilities": ["Web Search", "Content Retrieval", "Data Processing", "Academic Research"],
                "icon": "🔍"
            })
        elif agent_id == "web_search":
            metadata.update({
                "name": "Web Search",
                "type": "Specialized",
                "capabilities": ["Web Search", "Content Retrieval"],
                "icon": "🌐"
            })
        elif agent_id == "browser_interaction":
            metadata.update({
                "name": "Browser Interaction",
                "type": "Specialized",
                "capabilities": ["JavaScript Handling", "Dynamic Content"],
                "icon": "🖥️"
            })
        elif agent_id == "data_processing":
            metadata.update({
                "name": "Data Processing",
                "type": "Specialized",
                "capabilities": ["Data Extraction", "Data Normalization"],
                "icon": "📊"
            })
        elif agent_id == "literature":
            metadata.update({
                "name": "Literature",
                "type": "Specialized",
                "capabilities": ["Academic Research", "Paper Analysis"],
                "icon": "📚"
            })
        elif agent_id == "agent_creator":
            metadata.update({
                "name": "Agent Creator",
                "type": "Utility",
                "capabilities": ["Agent Creation", "Template Management", "Code Generation"],
                "icon": "🛠️"
            })
        elif agent_id == "story_writer":
            metadata.update({
                "name": "Story Writer",
                "type": "Utility",
                "capabilities": ["Story Generation", "Creative Writing", "Character Development"],
                "icon": "📝"
            })
        
        # Extract capabilities from agent tools
        if not metadata["capabilities"] and hasattr(agent, "tools"):
            capabilities = []
            for tool in agent.tools:
                capabilities.append(tool.name.replace("_", " ").title())
            metadata["capabilities"] = capabilities
        
        return metadata
    
    def _extract_agent_capabilities(self, agent: Any) -> List[Dict[str, Any]]:
        """
        Extract capabilities from an agent.
        
        Args:
            agent: The agent object
            
        Returns:
            A list of capability dictionaries
        """
        capabilities = []
        
        # Check if the agent is a CompiledStateGraph (supervisor)
        is_supervisor = not hasattr(agent, 'description')
        
        if is_supervisor:
            # For supervisor agents, return predefined capabilities
            capabilities = [
                {
                    "name": "chat",
                    "description": "Chat with the supervisor agent",
                    "parameters": [
                        {
                            "name": "message",
                            "type": "string",
                            "description": "The message to send to the agent",
                            "required": True
                        }
                    ]
                }
            ]
        else:
            # Extract capabilities from agent tools
            if hasattr(agent, "tools"):
                for tool in agent.tools:
                    capability = {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": []
                    }
                    
                    # Extract parameters from tool schema
                    if hasattr(tool, "args_schema"):
                        schema = tool.args_schema.schema()
                        if "properties" in schema:
                            for param_name, param_info in schema["properties"].items():
                                parameter = {
                                    "name": param_name,
                                    "type": param_info.get("type", "string"),
                                    "description": param_info.get("description", ""),
                                    "required": param_name in schema.get("required", [])
                                }
                                capability["parameters"].append(parameter)
                    
                    capabilities.append(capability)
        
        return capabilities
    
    def setup_agent_routes(self):
        """Set up routes for each agent."""
        initialized_agents = get_initialized_agents()
        
        for agent_id, agent in initialized_agents.items():
            # Create a router for this agent
            agent_router = APIRouter(prefix=f"/{agent_id}", tags=[agent_id])
            
            # Add chat routes
            self._add_chat_routes(agent_router, agent_id)
            
            # Add capability-specific routes
            self._add_capability_routes(agent_router, agent_id, agent)
            
            # Include the agent router in the main router
            self.router.include_router(agent_router)
            
            # Store the agent router
            self.agent_routers[agent_id] = agent_router
    
    def _add_chat_routes(self, router: APIRouter, agent_id: str):
        """
        Add chat routes for an agent.
        
        Args:
            router: The router to add the routes to
            agent_id: The ID of the agent
        """
        @router.get("/messages")
        async def get_messages():
            """Get all messages for a specific agent."""
            if agent_id not in self.message_store:
                self.message_store[agent_id] = []
            return self.message_store[agent_id]
        
        @router.post("/messages")
        async def send_message(message: MessageContent):
            """Send a message to an agent and get a response."""
            if agent_id not in self.message_store:
                self.message_store[agent_id] = []
            
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
            self.message_store[agent_id].append(user_message)
            
            # Get the agent from the initialized agents
            initialized_agents = get_initialized_agents()
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
            self.message_store[agent_id].append(agent_message)
            
            # Return the user message
            return user_message
    
    def _add_capability_routes(self, router: APIRouter, agent_id: str, agent: Any):
        """
        Add capability-specific routes for an agent.
        
        Args:
            router: The router to add the routes to
            agent_id: The ID of the agent
            agent: The agent object
        """
        # Check if the agent is a CompiledStateGraph (supervisor)
        is_supervisor = not hasattr(agent, 'description')
        
        if is_supervisor:
            # For supervisor agents, add a generic chat capability
            @router.post("/capabilities/chat")
            async def invoke_chat_capability(message: MessageContent):
                """Chat with the supervisor agent."""
                try:
                    # Get the agent from the initialized agents
                    initialized_agents = get_initialized_agents()
                    agent = initialized_agents.get(agent_id)
                    
                    if not agent:
                        raise HTTPException(status_code=404, detail="Agent not found")
                    
                    # Initialize the conversation state
                    state = {"messages": []}
                    
                    # Add the user message to the state
                    state["messages"].append({
                        "role": "user",
                        "content": message.content
                    })
                    
                    # Invoke the agent
                    logger.info(f"Invoking {agent_id} supervisor agent")
                    result = agent.invoke(state)
                    logger.info(f"{agent_id} supervisor agent completed processing")
                    
                    # Extract the response
                    response = "No response from supervisor agent"
                    if "messages" in result:
                        messages = result["messages"]
                        for msg in reversed(messages):
                            if isinstance(msg, dict) and msg.get("role") == "assistant":
                                response = msg.get("content", "")
                                break
                            elif hasattr(msg, "content") and (
                                getattr(msg, "type", None) == "ai" or 
                                getattr(msg, "role", None) == "assistant"
                            ):
                                response = msg.content
                                break
                    
                    return {"result": response}
                except Exception as e:
                    logger.error(f"Error invoking supervisor chat: {str(e)}")
                    raise HTTPException(status_code=500, detail=str(e))
        else:
            # Extract capabilities from agent tools
            if hasattr(agent, "tools"):
                for tool in agent.tools:
                    # Create a route for this tool
                    tool_name = tool.name
                    tool_description = tool.description
                    
                    # Create a model for the tool parameters
                    param_model = None
                    if hasattr(tool, "args_schema"):
                        param_model = tool.args_schema
                    
                    # Add the route
                    if param_model:
                        @router.post(f"/capabilities/{tool_name}")
                        async def invoke_capability(params: param_model):
                            """Invoke a capability of the agent."""
                            try:
                                # Get the agent from the initialized agents
                                initialized_agents = get_initialized_agents()
                                agent = initialized_agents.get(agent_id)
                                
                                if not agent:
                                    raise HTTPException(status_code=404, detail="Agent not found")
                                
                                # Find the tool
                                tool = None
                                for t in agent.tools:
                                    if t.name == tool_name:
                                        tool = t
                                        break
                                
                                if not tool:
                                    raise HTTPException(status_code=404, detail=f"Capability '{tool_name}' not found")
                                
                                # Invoke the tool
                                result = tool.invoke(params.dict())
                                
                                return {"result": result}
                            except Exception as e:
                                logger.error(f"Error invoking capability '{tool_name}': {str(e)}")
                                raise HTTPException(status_code=500, detail=str(e))
                    else:
                        @router.post(f"/capabilities/{tool_name}")
                        async def invoke_capability():
                            """Invoke a capability of the agent."""
                            try:
                                # Get the agent from the initialized agents
                                initialized_agents = get_initialized_agents()
                                agent = initialized_agents.get(agent_id)
                                
                                if not agent:
                                    raise HTTPException(status_code=404, detail="Agent not found")
                                
                                # Find the tool
                                tool = None
                                for t in agent.tools:
                                    if t.name == tool_name:
                                        tool = t
                                        break
                                
                                if not tool:
                                    raise HTTPException(status_code=404, detail=f"Capability '{tool_name}' not found")
                                
                                # Invoke the tool
                                result = tool.invoke({})
                                
                                return {"result": result}
                            except Exception as e:
                                logger.error(f"Error invoking capability '{tool_name}': {str(e)}")
                                raise HTTPException(status_code=500, detail=str(e))

# Create a global instance of the agent API
agent_api = AgentAPI()

# Function to get the agent API router
def get_agent_api_router():
    """Get the agent API router."""
    # Set up agent routes
    agent_api.setup_agent_routes()
    return agent_api.router
