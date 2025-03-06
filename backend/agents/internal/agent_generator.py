"""
Agent Generator Module for MOSAIC

This module provides functionality for validating agent definitions against a schema
and registering agents with the system. It is used for agent discovery and auto-registration.
"""

import json
import os
import logging
import importlib
from typing import Dict, Any, List, Optional, Tuple, Union
import jsonschema

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("mosaic.agent_generator")

# Import database models and repository
try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.database.models import Agent, Tool, Capability
    from mosaic.backend.database.repository import AgentRepository
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.database.models import Agent, Tool, Capability
    from backend.database.repository import AgentRepository

class AgentGenerator:
    """
    Generator for validating agent definitions and registering agents.
    
    This class provides methods for validating agent definitions against a schema
    and registering agents with the system.
    """
    
    def __init__(self, schema_path: str = None):
        """
        Initialize the agent generator.
        
        Args:
            schema_path: Path to the JSON schema file for agent definitions
        """
        self.schema_path = schema_path or os.path.join(
            os.path.dirname(__file__), "agent_schema.json"
        )
        self.schema = self._load_schema()
        logger.info(f"Initialized agent generator with schema from {self.schema_path}")
    
    def _load_schema(self) -> Dict[str, Any]:
        """
        Load the JSON schema for agent definitions.
        
        Returns:
            The JSON schema as a dictionary
        """
        try:
            with open(self.schema_path, "r") as f:
                schema = json.load(f)
            logger.info(f"Successfully loaded schema from {self.schema_path}")
            return schema
        except Exception as e:
            logger.error(f"Error loading schema: {str(e)}")
            raise
    
    def validate_definition(self, definition: Dict[str, Any]) -> bool:
        """
        Validate an agent definition against the schema.
        
        Args:
            definition: The agent definition to validate
            
        Returns:
            True if the definition is valid, False otherwise
            
        Raises:
            jsonschema.exceptions.ValidationError: If the definition is invalid
        """
        try:
            jsonschema.validate(instance=definition, schema=self.schema)
            logger.info(f"Agent definition for '{definition['agent']['name']}' is valid")
            return True
        except jsonschema.exceptions.ValidationError as e:
            logger.error(f"Agent definition validation error: {str(e)}")
            raise
    
    def load_definition_from_file(self, file_path: str) -> Dict[str, Any]:
        """
        Load an agent definition from a JSON file.
        
        Args:
            file_path: Path to the JSON file containing the agent definition
            
        Returns:
            The agent definition as a dictionary
        """
        try:
            with open(file_path, "r") as f:
                definition = json.load(f)
            logger.info(f"Successfully loaded agent definition from {file_path}")
            return definition
        except Exception as e:
            logger.error(f"Error loading agent definition: {str(e)}")
            raise
    
    def save_definition_to_db(self, definition: Dict[str, Any]) -> Tuple[Agent, List[Tool], List[Capability]]:
        """
        Save an agent definition to the database.
        
        Args:
            definition: The agent definition
            
        Returns:
            A tuple containing the agent, tools, and capabilities
        """
        # Validate the definition
        self.validate_definition(definition)
        
        # Convert the JSON definition to database records
        return AgentRepository.json_to_db(definition)
    
    def load_definition_from_db(self, agent_id: int) -> Dict[str, Any]:
        """
        Load an agent definition from the database.
        
        Args:
            agent_id: The ID of the agent in the database
            
        Returns:
            The agent definition as a dictionary
        """
        # Get the agent from the database
        agent = AgentRepository.get_agent(agent_id)
        if not agent:
            raise ValueError(f"Agent with ID {agent_id} not found in the database")
        
        # Convert the database record to a JSON definition
        return AgentRepository.db_to_json(agent)
    
    def register_agent_from_definition(
        self, 
        definition: Union[Dict[str, Any], int], 
        model: Any
    ) -> Any:
        """
        Register an agent from a definition.
        
        Args:
            definition: The agent definition or agent ID in the database
            model: The language model to use for the agent
            
        Returns:
            The registered agent
        """
        # If definition is an integer, load it from the database
        if isinstance(definition, int):
            definition = self.load_definition_from_db(definition)
        else:
            # Validate the definition
            self.validate_definition(definition)
        
        # Extract agent information
        agent_name = definition["agent"]["name"]
        
        # Import the agent module
        try:
            module = importlib.import_module(f"mosaic.backend.agents.{agent_name}")
        except ImportError:
            try:
                module = importlib.import_module(f"backend.agents.{agent_name}")
            except ImportError:
                raise ValueError(f"Agent module '{agent_name}' not found")
        
        # Get the registration function
        register_func = getattr(module, f"register_{agent_name}_agent")
        
        # Register the agent
        agent = register_func(model)
        logger.info(f"Successfully registered agent '{agent_name}'")
        
        return agent
