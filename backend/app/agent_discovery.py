"""
Agent Discovery Module for MOSAIC

This module provides functionality for dynamically discovering and registering agents.
It scans the agents directory for Python files, extracts agent registration functions,
and calls them automatically during startup.
"""

import os
import importlib
import inspect
import logging
import pkgutil
from typing import Dict, List, Any, Callable, Optional, Type
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("mosaic.agent_discovery")

# Try to import the agent registry
try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.agents.base import BaseAgent, agent_registry
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.agents.base import BaseAgent, agent_registry

class AgentDiscovery:
    """
    Class for discovering and registering agents dynamically.
    """
    
    def __init__(self, agents_package: str = "backend.agents"):
        """
        Initialize the agent discovery system.
        
        Args:
            agents_package: The package path where agents are located
        """
        self.agents_package = agents_package
        self.discovered_agents: Dict[str, Dict[str, Any]] = {}
        self.registration_functions: Dict[str, Callable] = {}
        
        # Try to import the agents package
        try:
            self.agents_module = importlib.import_module(agents_package)
            self.agents_path = os.path.dirname(self.agents_module.__file__)
            logger.info(f"Agents module found at: {self.agents_path}")
        except ImportError:
            logger.error(f"Could not import agents package: {agents_package}")
            self.agents_module = None
            self.agents_path = None
    
    def discover_agents(self) -> Dict[str, Dict[str, Any]]:
        """
        Discover all agent modules in the agents package.
        
        Returns:
            A dictionary mapping agent names to their metadata
        """
        if not self.agents_module:
            logger.error("Agents module not found, cannot discover agents")
            return {}
        
        logger.info(f"Discovering agents in package: {self.agents_package}")
        
        # Walk through the agents package and find all Python modules
        for _, name, is_pkg in pkgutil.iter_modules([self.agents_path]):
            # Skip __pycache__ and other special directories
            if name.startswith("__") or is_pkg:
                continue
            
            # Skip the base module
            if name == "base":
                continue
            
            # Try to import the module
            module_name = f"{self.agents_package}.{name}"
            try:
                module = importlib.import_module(module_name)
                logger.info(f"Examining module: {module_name}")
                
                # Look for agent classes that inherit from BaseAgent
                agent_classes = self._find_agent_classes(module)
                
                # Look for registration functions
                registration_functions = self._find_registration_functions(module)
                
                if agent_classes or registration_functions:
                    # Extract metadata from the agent classes
                    metadata = self._extract_agent_metadata(module, agent_classes)
                    
                    # Store the discovered agent
                    self.discovered_agents[name] = {
                        "module": module,
                        "classes": agent_classes,
                        "registration_functions": registration_functions,
                        "metadata": metadata
                    }
                    
                    # Store the registration functions
                    for func_name, func in registration_functions.items():
                        self.registration_functions[func_name] = func
                    
                    logger.info(f"Discovered agent: {name} with {len(agent_classes)} classes and {len(registration_functions)} registration functions")
                else:
                    logger.info(f"No agent classes or registration functions found in module: {module_name}")
            
            except ImportError as e:
                logger.error(f"Error importing module {module_name}: {str(e)}")
        
        return self.discovered_agents
    
    def _find_agent_classes(self, module) -> Dict[str, Type[BaseAgent]]:
        """
        Find all agent classes in a module that inherit from BaseAgent.
        
        Args:
            module: The module to search
            
        Returns:
            A dictionary mapping class names to class objects
        """
        agent_classes = {}
        
        for name, obj in inspect.getmembers(module):
            # Check if it's a class that inherits from BaseAgent
            if (inspect.isclass(obj) and 
                issubclass(obj, BaseAgent) and 
                obj != BaseAgent):
                agent_classes[name] = obj
                logger.info(f"Found agent class: {name}")
        
        return agent_classes
    
    def _find_registration_functions(self, module) -> Dict[str, Callable]:
        """
        Find all registration functions in a module.
        
        Args:
            module: The module to search
            
        Returns:
            A dictionary mapping function names to function objects
        """
        registration_functions = {}
        
        for name, obj in inspect.getmembers(module):
            # Check if it's a function that starts with "register_" and returns a BaseAgent
            if (inspect.isfunction(obj) and 
                name.startswith("register_") and 
                "model" in inspect.signature(obj).parameters):
                registration_functions[name] = obj
                logger.info(f"Found registration function: {name}")
        
        return registration_functions
    
    def _extract_agent_metadata(self, module, agent_classes: Dict[str, Type[BaseAgent]]) -> Dict[str, Any]:
        """
        Extract metadata from agent classes.
        
        Args:
            module: The module containing the agent classes
            agent_classes: A dictionary mapping class names to class objects
            
        Returns:
            A dictionary containing agent metadata
        """
        metadata = {}
        
        # Try to extract metadata from the module docstring
        if module.__doc__:
            metadata["description"] = module.__doc__.strip()
        
        # Extract metadata from the first agent class
        if agent_classes:
            first_class_name = next(iter(agent_classes))
            first_class = agent_classes[first_class_name]
            
            # Get the default name from the class
            if hasattr(first_class, "name"):
                metadata["name"] = getattr(first_class, "name")
            else:
                # Extract name from the class name
                name = first_class_name.lower()
                if name.endswith("agent"):
                    name = name[:-5]  # Remove "agent" suffix
                metadata["name"] = name
            
            # Get the description from the class docstring
            if first_class.__doc__:
                metadata["description"] = first_class.__doc__.strip()
            
            # Try to extract capabilities and icon from class attributes or docstring
            metadata["capabilities"] = self._extract_capabilities(first_class)
            metadata["icon"] = self._extract_icon(first_class)
            metadata["type"] = self._extract_type(first_class)
        
        return metadata
    
    def _extract_capabilities(self, agent_class: Type[BaseAgent]) -> List[str]:
        """
        Extract capabilities from an agent class.
        
        Args:
            agent_class: The agent class
            
        Returns:
            A list of capability strings
        """
        capabilities = []
        
        # Check if the class has a capabilities attribute
        if hasattr(agent_class, "capabilities"):
            capabilities = getattr(agent_class, "capabilities")
        
        # If no capabilities found, try to extract from the docstring
        if not capabilities and agent_class.__doc__:
            docstring = agent_class.__doc__.lower()
            
            # Look for keywords in the docstring
            keywords = ["can", "able to", "capable of", "supports", "provides"]
            for keyword in keywords:
                if keyword in docstring:
                    # Extract the capability after the keyword
                    parts = docstring.split(keyword, 1)
                    if len(parts) > 1:
                        capability = parts[1].strip().split(".")[0].strip()
                        capabilities.append(capability)
        
        return capabilities
    
    def _extract_icon(self, agent_class: Type[BaseAgent]) -> str:
        """
        Extract icon from an agent class.
        
        Args:
            agent_class: The agent class
            
        Returns:
            An icon string (emoji)
        """
        # Check if the class has an icon attribute
        if hasattr(agent_class, "icon"):
            return getattr(agent_class, "icon")
        
        # Default icon based on class name
        class_name = agent_class.__name__.lower()
        
        # Map common agent types to icons
        icon_map = {
            "calculator": "🧮",
            "math": "🧮",
            "writer": "✍️",
            "story": "📝",
            "research": "🔍",
            "search": "🔍",
            "web": "🌐",
            "browser": "🖥️",
            "data": "📊",
            "process": "⚙️",
            "literature": "📚",
            "creator": "🛠️",
            "supervisor": "👨‍💼"
        }
        
        # Find the first matching icon
        for key, icon in icon_map.items():
            if key in class_name:
                return icon
        
        # Default icon
        return "🤖"
    
    def _extract_type(self, agent_class: Type[BaseAgent]) -> str:
        """
        Extract agent type from an agent class.
        
        Args:
            agent_class: The agent class
            
        Returns:
            An agent type string
        """
        # Check if the class has a type attribute
        if hasattr(agent_class, "type"):
            return getattr(agent_class, "type")
        
        # Default type based on class name
        class_name = agent_class.__name__.lower()
        
        # Map common agent names to types
        type_map = {
            "supervisor": "Supervisor",
            "research": "Supervisor",
            "web": "Specialized",
            "browser": "Specialized",
            "data": "Specialized",
            "literature": "Specialized",
            "calculator": "Utility",
            "writer": "Utility",
            "creator": "Utility"
        }
        
        # Find the first matching type
        for key, agent_type in type_map.items():
            if key in class_name:
                return agent_type
        
        # Default type
        return "Utility"
    
    def register_agents(self, model) -> Dict[str, Any]:
        """
        Register all discovered agents with the agent registry.
        
        Args:
            model: The language model to use for the agents
            
        Returns:
            A dictionary mapping agent names to agent instances
        """
        registered_agents = {}
        
        logger.info(f"Registering {len(self.registration_functions)} agents")
        
        # Call each registration function with the model
        for func_name, func in self.registration_functions.items():
            try:
                logger.info(f"Registering agent with function: {func_name}")
                agent = func(model)
                
                if agent:
                    registered_agents[agent.name] = agent
                    logger.info(f"Successfully registered agent: {agent.name}")
                else:
                    logger.warning(f"Registration function {func_name} returned None")
            
            except Exception as e:
                logger.error(f"Error registering agent with function {func_name}: {str(e)}")
        
        return registered_agents


# Function to discover and register all agents
def discover_and_register_agents(model) -> Dict[str, Any]:
    """
    Discover and register all agents.
    
    Args:
        model: The language model to use for the agents
        
    Returns:
        A dictionary mapping agent names to agent instances
    """
    # Create the agent discovery system
    discovery = AgentDiscovery()
    
    # Discover all agents
    discovery.discover_agents()
    
    # Register all agents
    registered_agents = discovery.register_agents(model)
    
    return registered_agents
