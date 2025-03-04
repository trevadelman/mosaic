"""
Agent Creator Module for MOSAIC

This module defines an agent that can create new agents based on natural language descriptions.
It serves as a specialized agent for agent creation in the MOSAIC system.
"""

import json
import os
import logging
import datetime
from typing import List, Dict, Any, Optional

from langchain_core.language_models import LanguageModelLike
from langchain_core.tools import BaseTool, tool

try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.agents.base import BaseAgent, agent_registry
    from mosaic.backend.agents.agent_generator import AgentGenerator
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.agents.base import BaseAgent, agent_registry
    from backend.agents.agent_generator import AgentGenerator

# Configure logging
logger = logging.getLogger("mosaic.agents.agent_creator")

# Initialize the agent generator
generator = AgentGenerator()

@tool
def create_agent_template(spec: str) -> str:
    """
    Create a JSON template for a new agent based on a natural language specification.
    
    Args:
        spec: Natural language description of the agent to create
        
    Returns:
        JSON template for the agent
    """
    logger.info(f"Creating agent template from specification: {spec}")
    
    try:
        # Extract key information from the specification
        # In a real implementation, this would use the LLM to parse the specification
        # For this example, we'll use a simple approach
        
        # Default values
        agent_name = "custom_agent"
        agent_type = "Specialized"
        description = "Custom agent created from specification"
        capabilities = []
        icon = "🤖"
        tools = []
        system_prompt = "You are a helpful assistant."
        
        # Extract information from the specification
        lines = spec.strip().split("\n")
        for line in lines:
            line = line.strip()
            if line.lower().startswith("name:"):
                agent_name = line[5:].strip().lower().replace(" ", "_")
            elif line.lower().startswith("type:"):
                agent_type = line[5:].strip()
            elif line.lower().startswith("description:"):
                description = line[12:].strip()
            elif line.lower().startswith("capabilities:"):
                capabilities_str = line[13:].strip()
                capabilities = [cap.strip() for cap in capabilities_str.split(",")]
            elif line.lower().startswith("icon:"):
                icon = line[5:].strip()
            elif line.lower().startswith("prompt:"):
                system_prompt = line[7:].strip()
        
        # Create a basic template
        template = {
            "agent": {
                "name": agent_name,
                "type": agent_type,
                "description": description,
                "capabilities": capabilities,
                "icon": icon,
                "tools": tools,
                "systemPrompt": system_prompt,
                "metadata": {
                    "version": "1.0.0",
                    "author": "Agent Creator",
                    "created": datetime.datetime.now().isoformat(),
                    "tags": capabilities
                }
            }
        }
        
        # Convert to JSON
        template_json = json.dumps(template, indent=2)
        
        logger.info(f"Successfully created agent template for '{agent_name}'")
        return template_json
    
    except Exception as e:
        logger.error(f"Error creating agent template: {str(e)}")
        return f"Error creating agent template: {str(e)}"

@tool
def add_tool_to_template(template_json: str, tool_spec: str) -> str:
    """
    Add a tool to an agent template.
    
    Args:
        template_json: JSON template for the agent
        tool_spec: Natural language description of the tool to add
        
    Returns:
        Updated JSON template for the agent
    """
    logger.info(f"Adding tool to agent template")
    
    try:
        # Parse the template
        template = json.loads(template_json)
        
        # Extract key information from the tool specification
        # In a real implementation, this would use the LLM to parse the specification
        # For this example, we'll use a simple approach
        
        # Default values
        tool_name = "custom_tool"
        tool_description = "Custom tool created from specification"
        parameters = []
        returns_type = "string"
        returns_description = "Result of the tool execution"
        implementation = "def custom_tool():\n    return 'Not implemented'"
        dependencies = []
        
        # Extract information from the specification
        lines = tool_spec.strip().split("\n")
        for i, line in enumerate(lines):
            line = line.strip()
            if line.lower().startswith("name:"):
                tool_name = line[5:].strip().lower().replace(" ", "_")
            elif line.lower().startswith("description:"):
                tool_description = line[12:].strip()
            elif line.lower().startswith("parameters:"):
                # Parse parameters
                param_lines = []
                j = i + 1
                while j < len(lines) and lines[j].strip().startswith("-"):
                    param_lines.append(lines[j].strip()[2:])
                    j += 1
                
                for param_line in param_lines:
                    param_parts = param_line.split(":")
                    if len(param_parts) >= 2:
                        param_name = param_parts[0].strip()
                        param_type = param_parts[1].strip()
                        param_desc = ":".join(param_parts[2:]).strip() if len(param_parts) > 2 else ""
                        
                        parameters.append({
                            "name": param_name,
                            "type": param_type,
                            "description": param_desc,
                            "required": True
                        })
            
            elif line.lower().startswith("returns:"):
                returns_parts = line[8:].strip().split(":")
                if len(returns_parts) >= 1:
                    returns_type = returns_parts[0].strip()
                    returns_description = ":".join(returns_parts[1:]).strip() if len(returns_parts) > 1 else ""
            
            elif line.lower().startswith("implementation:"):
                # Collect all subsequent lines as the implementation
                implementation_lines = []
                j = i + 1
                while j < len(lines):
                    implementation_lines.append(lines[j])
                    j += 1
                
                implementation = "\n".join(implementation_lines)
                break
        
        # Create the tool
        tool = {
            "name": tool_name,
            "description": tool_description,
            "parameters": parameters,
            "returns": {
                "type": returns_type,
                "description": returns_description
            },
            "implementation": {
                "code": implementation,
                "dependencies": dependencies
            }
        }
        
        # Add the tool to the template
        template["agent"]["tools"].append(tool)
        
        # Convert to JSON
        updated_template_json = json.dumps(template, indent=2)
        
        logger.info(f"Successfully added tool '{tool_name}' to agent template")
        return updated_template_json
    
    except Exception as e:
        logger.error(f"Error adding tool to agent template: {str(e)}")
        return f"Error adding tool to agent template: {str(e)}"

@tool
def validate_agent_template(template_json: str) -> str:
    """
    Validate an agent template against the schema.
    
    Args:
        template_json: JSON template for the agent
        
    Returns:
        Validation result
    """
    logger.info(f"Validating agent template")
    
    try:
        # Parse the template
        template = json.loads(template_json)
        
        # Validate the template
        generator.validate_definition(template)
        
        logger.info(f"Agent template is valid")
        return "Agent template is valid"
    
    except Exception as e:
        logger.error(f"Error validating agent template: {str(e)}")
        return f"Error validating agent template: {str(e)}"

@tool
def generate_agent_code(template_json: str) -> str:
    """
    Generate Python code for an agent from a template.
    
    Args:
        template_json: JSON template for the agent
        
    Returns:
        Generated Python code
    """
    logger.info(f"Generating agent code from template")
    
    try:
        # Parse the template
        template = json.loads(template_json)
        
        # Generate the agent code
        agent_code = generator.generate_agent_class(template)
        
        logger.info(f"Successfully generated agent code")
        return agent_code
    
    except Exception as e:
        logger.error(f"Error generating agent code: {str(e)}")
        return f"Error generating agent code: {str(e)}"

@tool
def save_agent_template(template_json: str, filename: str = None) -> str:
    """
    Save an agent template to a file.
    
    Args:
        template_json: JSON template for the agent
        filename: Name of the file to save the template to (default: agent_name.json)
        
    Returns:
        Path to the saved file
    """
    logger.info(f"Saving agent template to file")
    
    try:
        # Parse the template
        template = json.loads(template_json)
        
        # Determine the filename
        agent_name = template["agent"]["name"]
        if filename is None:
            filename = f"{agent_name}.json"
        
        # Determine the output directory
        output_dir = os.path.join(os.path.dirname(__file__), "templates")
        os.makedirs(output_dir, exist_ok=True)
        
        # Create the output file path
        output_file = os.path.join(output_dir, filename)
        
        # Write the template to the file
        with open(output_file, "w") as f:
            f.write(template_json)
        
        logger.info(f"Successfully saved agent template to {output_file}")
        return f"Agent template saved to {output_file}"
    
    except Exception as e:
        logger.error(f"Error saving agent template: {str(e)}")
        return f"Error saving agent template: {str(e)}"

@tool
def deploy_agent(template_json: str, sandbox: bool = True) -> str:
    """
    Deploy an agent from a template.
    
    Args:
        template_json: JSON template for the agent
        sandbox: Whether to deploy the agent in a sandbox environment
        
    Returns:
        Deployment result
    """
    logger.info(f"Deploying agent from template (sandbox={sandbox})")
    
    try:
        # Parse the template
        template = json.loads(template_json)
        
        # Validate the template
        generator.validate_definition(template)
        
        # Extract agent information
        agent_name = template["agent"]["name"]
        
        # Generate the agent code
        if sandbox:
            # In sandbox mode, we generate the agent code and save it to a sandbox directory
            sandbox_dir = os.path.join(os.path.dirname(__file__), "sandbox")
            os.makedirs(sandbox_dir, exist_ok=True)
            
            # Write the agent to a file in the sandbox
            agent_file = generator.write_agent_to_file(template, sandbox_dir)
            
            # Import the agent discovery module to register the agent
            try:
                # Try importing with the full package path (for local development)
                from mosaic.backend.app.agent_discovery import discover_and_register_agents
            except ImportError:
                # Fall back to relative import (for Docker environment)
                from app.agent_discovery import discover_and_register_agents
            
            logger.info(f"Successfully deployed agent '{agent_name}' to sandbox at {agent_file}")
            logger.info(f"The agent will be automatically discovered and registered on server restart")
            return f"Agent '{agent_name}' deployed to sandbox at {agent_file}. The agent will be automatically discovered and registered on server restart."
        else:
            # In production mode, we generate the agent code and save it to the agents directory
            agent_file = generator.write_agent_to_file(template)
            
            # Import the agent discovery module to register the agent
            try:
                # Try importing with the full package path (for local development)
                from mosaic.backend.app.agent_discovery import discover_and_register_agents
            except ImportError:
                # Fall back to relative import (for Docker environment)
                from app.agent_discovery import discover_and_register_agents
            
            logger.info(f"Successfully deployed agent '{agent_name}' to production at {agent_file}")
            logger.info(f"The agent will be automatically discovered and registered on server restart")
            return f"Agent '{agent_name}' deployed to production at {agent_file}. The agent will be automatically discovered and registered on server restart."
    
    except Exception as e:
        logger.error(f"Error deploying agent: {str(e)}")
        return f"Error deploying agent: {str(e)}"

class AgentCreatorAgent(BaseAgent):
    """
    Agent for creating new agents based on natural language descriptions.
    
    This agent provides tools for creating agent templates, adding tools to templates,
    validating templates, generating agent code, and deploying agents.
    """
    
    def __init__(
        self,
        name: str = "agent_creator",
        model: Optional[LanguageModelLike] = None,
        tools: List[BaseTool] = None,
        prompt: str = None,
        description: str = None,
    ):
        """
        Initialize a new agent creator agent.
        
        Args:
            name: The name of the agent (default: "agent_creator")
            model: The language model to use for the agent
            tools: Optional list of additional tools
            prompt: Optional system prompt for the agent
            description: Optional description of the agent
        """
        # Define the agent's tools
        agent_tools = [
            create_agent_template,
            add_tool_to_template,
            validate_agent_template,
            generate_agent_code,
            save_agent_template,
            deploy_agent
        ]
        
        # Combine with any additional tools
        all_tools = agent_tools + (tools or [])
        
        super().__init__(
            name=name,
            model=model,
            tools=all_tools,
            prompt=prompt,
            description=description or "Agent for creating new agents based on natural language descriptions"
        )
        
        logger.info(f"Initialized agent creator agent with {len(all_tools)} tools")
    
    def _get_default_prompt(self) -> str:
        """
        Get the default system prompt for the agent creator agent.
        
        Returns:
            A string containing the default system prompt
        """
        return """You are an agent creation specialist with the ability to create new agents for the MOSAIC system. Your job is to help users create new agents based on their requirements.

You have the following tools at your disposal:
- Use create_agent_template to create a JSON template for a new agent based on a natural language specification.
- Use add_tool_to_template to add a tool to an agent template.
- Use validate_agent_template to validate an agent template against the schema.
- Use generate_agent_code to generate Python code for an agent from a template.
- Use save_agent_template to save an agent template to a file.
- Use deploy_agent to deploy an agent from a template.

When creating a new agent, follow these steps:
1. Create a template for the agent using create_agent_template.
2. Add tools to the template using add_tool_to_template.
3. Validate the template using validate_agent_template.
4. Generate the agent code using generate_agent_code.
5. Save the template using save_agent_template.
6. Deploy the agent using deploy_agent.

The MOSAIC system includes a dynamic agent discovery system that automatically scans the agents directory for Python files, extracts agent registration functions, and calls them automatically during startup. This means that once you deploy an agent, it will be automatically discovered and registered with the system on the next server restart. The system also automatically generates API endpoints for each agent, so the agent will be immediately available through the API.

Always provide clear explanations of what you're doing and why. If you encounter any errors, explain them to the user and suggest how to fix them.

Never create agents that could be harmful or malicious. Always validate that the agent's purpose and tools are safe and ethical."""


def register_agent_creator_agent(model: LanguageModelLike) -> AgentCreatorAgent:
    """
    Create and register an agent creator agent.
    
    Args:
        model: The language model to use for the agent
        
    Returns:
        The created agent creator agent
    """
    try:
        # Try importing with the full package path (for local development)
        from mosaic.backend.agents.base import agent_registry
    except ImportError:
        # Fall back to relative import (for Docker environment)
        from backend.agents.base import agent_registry
    
    agent_creator = AgentCreatorAgent(model=model)
    agent_registry.register(agent_creator)
    return agent_creator
