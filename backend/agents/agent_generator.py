"""
Agent Generator Module for MOSAIC

This module provides functionality for generating agent code from JSON definitions
and database records. It is used by the agent creator system to dynamically create
new agents.
"""

import json
import os
import logging
import importlib
import inspect
from typing import Dict, Any, List, Optional, Tuple, Union
from pathlib import Path
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
    Generator for creating agent code from JSON definitions.
    
    This class provides methods for validating agent definitions against a schema,
    generating Python code for agents, and registering agents with the system.
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
    
    def generate_tool_code(self, tool: Dict[str, Any]) -> str:
        """
        Generate Python code for a tool.
        
        Args:
            tool: The tool definition
            
        Returns:
            Python code for the tool
        """
        # Extract tool information
        name = tool["name"]
        description = tool["description"]
        parameters = tool["parameters"]
        returns = tool["returns"]
        implementation = tool["implementation"]["code"]
        
        logger.info(f"Generating code for tool '{name}'")
        
        # The implementation already includes the full function definition
        # We just need to return it as is
        return implementation
    
    def generate_agent_class(self, definition: Dict[str, Any]) -> str:
        """
        Generate Python code for an agent class.
        
        Args:
            definition: The agent definition
            
        Returns:
            Python code for the agent class
        """
        # Extract agent information
        agent = definition["agent"]
        name = agent["name"]
        agent_type = agent["type"]
        description = agent["description"]
        capabilities = agent.get("capabilities", [])
        icon = agent.get("icon", "🤖")
        tools = agent["tools"]
        system_prompt = agent["systemPrompt"]
        
        logger.info(f"Generating agent class for '{name}'")
        
        # Generate tool imports and code
        tool_imports = set()
        tool_code = ""
        for tool in tools:
            # Extract any imports from the tool code
            code_lines = tool["implementation"]["code"].split("\n")
            for line in code_lines:
                if line.startswith("import ") or line.startswith("from "):
                    tool_imports.add(line)
            
            # Add the tool code
            tool_code += f"\n{self.generate_tool_code(tool)}\n"
        
        # Generate the agent class
        class_code = f'''"""
{name.capitalize()} Agent Module for MOSAIC

{description}
"""

import logging
from typing import List, Dict, Any, Optional

from langchain_core.language_models import LanguageModelLike
from langchain_core.tools import BaseTool, tool

try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.agents.base import BaseAgent, agent_registry
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.agents.base import BaseAgent, agent_registry

# Import tool dependencies
{os.linesep.join(sorted(tool_imports))}

# Configure logging
logger = logging.getLogger("mosaic.agents.{name}")

{tool_code}

class {name.capitalize().replace('_', '')}Agent(BaseAgent):
    """
    {description}
    """
    
    def __init__(
        self,
        name: str = "{name}",
        model: Optional[LanguageModelLike] = None,
        tools: List[BaseTool] = None,
        prompt: str = None,
        description: str = None,
    ):
        """
        Initialize a new {name.capitalize()} agent.
        
        Args:
            name: The name of the agent (default: "{name}")
            model: The language model to use for the agent
            tools: Optional list of additional tools
            prompt: Optional system prompt for the agent
            description: Optional description of the agent
        """
        # Define the agent's tools
        agent_tools = [
            {", ".join([tool["name"] for tool in tools])}
        ]
        
        # Combine with any additional tools
        all_tools = agent_tools + (tools or [])
        
        super().__init__(
            name=name,
            model=model,
            tools=all_tools,
            prompt=prompt,
            description=description or "{description}"
        )
        
        logger.info(f"Initialized {name} agent with {{len(all_tools)}} tools")
    
    def _get_default_prompt(self) -> str:
        """
        Get the default system prompt for the {name} agent.
        
        Returns:
            A string containing the default system prompt
        """
        return """{system_prompt}"""


def register_{name}_agent(model: LanguageModelLike) -> {name.capitalize().replace('_', '')}Agent:
    """
    Create and register a {name} agent.
    
    Args:
        model: The language model to use for the agent
        
    Returns:
        The created {name} agent
    """
    try:
        # Try importing with the full package path (for local development)
        from mosaic.backend.agents.base import agent_registry
    except ImportError:
        # Fall back to relative import (for Docker environment)
        from backend.agents.base import agent_registry
    
    {name}_agent = {name.capitalize().replace('_', '')}Agent(model=model)
    agent_registry.register({name}_agent)
    return {name}_agent
'''
        
        logger.info(f"Successfully generated agent class for '{name}'")
        return class_code
    
    def write_agent_to_file(self, definition: Dict[str, Any], output_dir: str = None) -> str:
        """
        Write an agent class to a Python file.
        
        Args:
            definition: The agent definition
            output_dir: Directory to write the file to (default: current directory)
            
        Returns:
            Path to the generated file
        """
        # Validate the definition
        self.validate_definition(definition)
        
        # Generate the agent class
        agent_name = definition["agent"]["name"]
        agent_code = self.generate_agent_class(definition)
        
        # Determine the output directory
        if output_dir is None:
            output_dir = os.path.dirname(__file__)
        
        # Create the output file path
        output_file = os.path.join(output_dir, f"{agent_name}.py")
        
        # Write the agent class to the file
        try:
            with open(output_file, "w") as f:
                f.write(agent_code)
            logger.info(f"Successfully wrote agent class to {output_file}")
            return output_file
        except Exception as e:
            logger.error(f"Error writing agent class to file: {str(e)}")
            raise
    
    def generate_agent_class_from_db(self, agent_id: int) -> str:
        """
        Generate Python code for an agent class from a database record.
        
        Args:
            agent_id: The ID of the agent in the database
            
        Returns:
            Python code for the agent class
        """
        # Get the agent from the database
        agent = AgentRepository.get_agent(agent_id)
        if not agent:
            raise ValueError(f"Agent with ID {agent_id} not found in the database")
        
        # Convert the database record to a JSON definition
        definition = AgentRepository.db_to_json(agent)
        
        # Generate the agent class
        return self.generate_agent_class(definition)
    
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
        model: Any,
        sandbox: bool = True
    ) -> Any:
        """
        Register an agent from a definition.
        
        Args:
            definition: The agent definition or agent ID in the database
            model: The language model to use for the agent
            sandbox: Whether to register the agent in a sandbox environment
            
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
        
        if sandbox:
            # In sandbox mode, we generate the agent code and load it dynamically
            # This is safer but more complex
            
            # Create a temporary directory for the sandbox
            sandbox_dir = os.path.join(os.path.dirname(__file__), "sandbox")
            os.makedirs(sandbox_dir, exist_ok=True)
            
            # Write the agent to a file in the sandbox
            agent_file = self.write_agent_to_file(definition, sandbox_dir)
            
            # Import the agent module dynamically
            spec = importlib.util.spec_from_file_location(
                f"mosaic.backend.agents.sandbox.{agent_name}",
                agent_file
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Get the registration function
            register_func = getattr(module, f"register_{agent_name}_agent")
            
            # Register the agent
            agent = register_func(model)
            logger.info(f"Successfully registered agent '{agent_name}' in sandbox")
            
            return agent
        else:
            # In production mode, we assume the agent code has already been
            # generated and properly installed
            
            # Import the agent module
            try:
                module = importlib.import_module(f"mosaic.backend.agents.{agent_name}")
            except ImportError:
                module = importlib.import_module(f"backend.agents.{agent_name}")
            
            # Get the registration function
            register_func = getattr(module, f"register_{agent_name}_agent")
            
            # Register the agent
            agent = register_func(model)
            logger.info(f"Successfully registered agent '{agent_name}' in production")
            
            return agent
    
    def write_agent_to_file_from_db(self, agent_id: int, output_dir: str = None) -> str:
        """
        Write an agent class to a Python file from a database record.
        
        Args:
            agent_id: The ID of the agent in the database
            output_dir: Directory to write the file to (default: current directory)
            
        Returns:
            Path to the generated file
        """
        # Get the agent from the database
        agent = AgentRepository.get_agent(agent_id)
        if not agent:
            raise ValueError(f"Agent with ID {agent_id} not found in the database")
        
        # Convert the database record to a JSON definition
        definition = AgentRepository.db_to_json(agent)
        
        # Write the agent to a file
        return self.write_agent_to_file(definition, output_dir)


# Example usage
if __name__ == "__main__":
    # Create an agent generator
    generator = AgentGenerator()
    
    # Load an agent definition from a file
    definition_path = os.path.join(os.path.dirname(__file__), "example_agent.json")
    definition = generator.load_definition_from_file(definition_path)
    
    # Validate the definition
    generator.validate_definition(definition)
    
    # Generate the agent class
    agent_code = generator.generate_agent_class(definition)
    
    # Print the generated code
    print(agent_code)
    
    # Write the agent to a file
    output_file = generator.write_agent_to_file(definition)
    print(f"Agent written to {output_file}")
