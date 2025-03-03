"""
Base Agent Module for MOSAIC

This module defines the base agent class and related utilities for the MOSAIC system.
It provides a foundation for creating specialized agents that can be orchestrated by
a supervisor agent.
"""

import logging
import inspect
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Callable, Type, Union

from langchain_core.language_models import LanguageModelLike
from langchain_core.tools import BaseTool
from langchain_core.messages import AIMessage, ToolMessage
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph
from langgraph.pregel import Pregel

# Configure logging
logger = logging.getLogger("mosaic.agents")

class BaseAgent(ABC):
    """
    Base class for all MOSAIC agents.
    
    This class provides the foundation for creating specialized agents in the MOSAIC system.
    It handles common functionality such as initialization, tool registration, and agent creation.
    """
    
    def __init__(
        self,
        name: str,
        model: LanguageModelLike,
        tools: List[BaseTool] = None,
        prompt: str = None,
        description: str = None,
    ):
        """
        Initialize a new agent.
        
        Args:
            name: The name of the agent
            model: The language model to use for the agent
            tools: Optional list of tools for the agent to use
            prompt: Optional system prompt for the agent
            description: Optional description of the agent
        """
        self.name = name
        self.model = model
        self.tools = tools or []
        self.prompt = prompt or self._get_default_prompt()
        self.description = description or f"{name} Agent"
        self.agent = None
        
        logger.info(f"Initialized {self.name} agent with {len(self.tools)} tools")
    
    @abstractmethod
    def _get_default_prompt(self) -> str:
        """
        Get the default system prompt for this agent.
        
        This method should be implemented by subclasses to provide a default
        system prompt that describes the agent's role and capabilities.
        
        Returns:
            A string containing the default system prompt
        """
        pass
    
    def add_tool(self, tool: BaseTool) -> None:
        """
        Add a tool to the agent.
        
        Args:
            tool: The tool to add
        """
        self.tools.append(tool)
        logger.info(f"Added tool '{tool.name}' to {self.name} agent")
    
    def create(self) -> Pregel:
        """
        Create the agent using langgraph's create_react_agent.
        
        Returns:
            A Pregel object representing the agent
        """
        if self.agent is None:
            logger.info(f"Creating {self.name} agent with {len(self.tools)} tools")
            
            # Bind tools to the model if supported
            model = self.model
            if hasattr(model, "bind_tools") and "parallel_tool_calls" in inspect.signature(model.bind_tools).parameters:
                model = model.bind_tools(self.tools, parallel_tool_calls=False)
            
            self.agent = create_react_agent(
                model=model,
                tools=self.tools,
                name=self.name,
                prompt=self.prompt
            )
            
            logger.info(f"Successfully created {self.name} agent")
        
        return self.agent
    
    def invoke(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invoke the agent with the given state.
        
        Args:
            state: The current state of the conversation
            
        Returns:
            The updated state after the agent has processed it
        """
        if self.agent is None:
            self.create()
        
        logger.info(f"Invoking {self.name} agent")
        result = self.agent.invoke(state)
        logger.info(f"{self.name} agent completed processing")
        
        return result
    
    async def ainvoke(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Asynchronously invoke the agent with the given state.
        
        Args:
            state: The current state of the conversation
            
        Returns:
            The updated state after the agent has processed it
        """
        if self.agent is None:
            self.create()
        
        logger.info(f"Asynchronously invoking {self.name} agent")
        result = await self.agent.ainvoke(state)
        logger.info(f"{self.name} agent completed async processing")
        
        return result


class AgentRegistry:
    """
    Registry for managing agents in the MOSAIC system.
    
    This class provides a centralized registry for creating, retrieving, and
    managing agents in the MOSAIC system.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AgentRegistry, cls).__new__(cls)
            cls._instance.agents = {}
            cls._instance.logger = logging.getLogger("mosaic.agent_registry")
        return cls._instance
    
    def register(self, agent: BaseAgent) -> None:
        """
        Register an agent with the registry.
        
        Args:
            agent: The agent to register
        """
        if agent.name in self.agents:
            self.logger.warning(f"Agent '{agent.name}' already registered. Overwriting.")
        
        self.agents[agent.name] = agent
        self.logger.info(f"Registered agent '{agent.name}'")
    
    def get(self, name: str) -> Optional[BaseAgent]:
        """
        Get an agent by name.
        
        Args:
            name: The name of the agent to retrieve
            
        Returns:
            The agent if found, None otherwise
        """
        agent = self.agents.get(name)
        if agent is None:
            self.logger.warning(f"Agent '{name}' not found in registry")
        return agent
    
    def list_agents(self) -> List[str]:
        """
        Get a list of all registered agent names.
        
        Returns:
            A list of agent names
        """
        return list(self.agents.keys())
    
    def create_supervisor(
        self,
        model: LanguageModelLike,
        agent_names: List[str] = None,
        prompt: str = None,
        name: str = "supervisor",
        output_mode: str = "last_message"
    ) -> StateGraph:
        """
        Create a supervisor agent that can orchestrate other agents.
        
        Args:
            model: The language model to use for the supervisor
            agent_names: Optional list of agent names to include (defaults to all)
            prompt: Optional system prompt for the supervisor
            name: The name of the supervisor (default: "supervisor")
            output_mode: How to handle agent outputs ("full_history" or "last_message")
            
        Returns:
            A StateGraph representing the supervisor workflow
        """
        from langgraph_supervisor import create_supervisor
        
        # Determine which agents to include
        if agent_names is None:
            agent_names = self.list_agents()
        
        # Get the agents
        agents = []
        for agent_name in agent_names:
            agent = self.get(agent_name)
            if agent is not None:
                # Create the agent if it hasn't been created yet
                if agent.agent is None:
                    agent.create()
                agents.append(agent.agent)
        
        if not agents:
            self.logger.error("No valid agents found to create supervisor")
            raise ValueError("No valid agents found to create supervisor")
        
        # Create the supervisor
        self.logger.info(f"Creating supervisor with {len(agents)} agents: {', '.join(agent_names)}")
        supervisor = create_supervisor(
            agents=agents,
            model=model,
            prompt=prompt,
            supervisor_name=name,
            output_mode=output_mode
        )
        
        self.logger.info(f"Successfully created supervisor '{name}'")
        return supervisor


# Create a global agent registry instance
agent_registry = AgentRegistry()
