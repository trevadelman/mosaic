"""
Agent Creator API Module

This module provides API endpoints for creating, testing, and deploying custom agents.
"""

from fastapi import APIRouter, HTTPException, Depends, Body, Query, Path
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging
import json
import os
from pathlib import Path as FilePath

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("mosaic.agent_creator_api")

# Import the agent creator and generator
try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.agents.agent_creator import (
        create_agent_template,
        add_tool_to_template,
        validate_agent_template,
        generate_agent_code,
        deploy_agent,
    )
    from mosaic.backend.agents.agent_generator import AgentGenerator
    from mosaic.backend.agents.base import agent_registry
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.agents.agent_creator import (
        create_agent_template,
        add_tool_to_template,
        validate_agent_template,
        generate_agent_code,
        deploy_agent,
    )
    from backend.agents.agent_generator import AgentGenerator
    from backend.agents.base import agent_registry

# Create the router
router = APIRouter(
    prefix="/api/agent-creator",
    tags=["agent-creator"],
    responses={404: {"description": "Not found"}},
)

# Models
class AgentSpec(BaseModel):
    """Agent specification for creating a new agent."""
    name: str = Field(..., description="Unique identifier for the agent")
    type: str = Field(..., description="Type of agent (Utility, Specialized, Supervisor)")
    description: str = Field(..., description="Human-readable description of the agent")
    capabilities: List[str] = Field(default=[], description="List of agent capabilities")
    icon: Optional[str] = Field(None, description="Emoji icon for the agent")
    prompt: str = Field(..., description="System prompt for the agent")

class ToolSpec(BaseModel):
    """Tool specification for adding a tool to an agent."""
    name: str = Field(..., description="Name of the tool")
    description: str = Field(..., description="Human-readable description of the tool")
    parameters: List[Dict[str, Any]] = Field(..., description="List of parameters for the tool")
    returns: Dict[str, Any] = Field(..., description="Return type and description of the tool")
    implementation: str = Field(..., description="Python code implementing the tool")

class AgentTemplate(BaseModel):
    """Agent template in JSON format."""
    template: Dict[str, Any] = Field(..., description="Agent template in JSON format")

class DeploymentOptions(BaseModel):
    """Options for deploying an agent."""
    sandbox: bool = Field(True, description="Whether to deploy the agent to the sandbox environment")

class ValidationResult(BaseModel):
    """Result of validating an agent template."""
    valid: bool = Field(..., description="Whether the template is valid")
    message: str = Field(..., description="Validation message")
    errors: Optional[List[str]] = Field(None, description="List of validation errors")

class CodeGenerationResult(BaseModel):
    """Result of generating code for an agent."""
    code: str = Field(..., description="Generated Python code for the agent")

class DeploymentResult(BaseModel):
    """Result of deploying an agent."""
    success: bool = Field(..., description="Whether the deployment was successful")
    message: str = Field(..., description="Deployment message")
    agent_id: Optional[str] = Field(None, description="ID of the deployed agent")

class AgentSchemaResponse(BaseModel):
    """Response containing the agent schema."""
    schema: Dict[str, Any] = Field(..., description="JSON schema for agent definitions")

# Routes
@router.get("/schema", response_model=AgentSchemaResponse)
async def get_agent_schema():
    """Get the JSON schema for agent definitions."""
    try:
        # Get the schema from the agent generator
        generator = AgentGenerator()
        schema = generator.schema
        return {"schema": schema}
    except Exception as e:
        logger.error(f"Error getting agent schema: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting agent schema: {str(e)}")

@router.post("/template", response_model=Dict[str, Any])
async def create_template(agent_spec: AgentSpec):
    """Create a new agent template from an agent specification."""
    try:
        # Convert the agent spec to a string format expected by the agent creator
        spec_str = f"""
        name: {agent_spec.name}
        type: {agent_spec.type}
        description: {agent_spec.description}
        capabilities: {', '.join(agent_spec.capabilities)}
        icon: {agent_spec.icon or '🤖'}
        prompt: {agent_spec.prompt}
        """
        
        # Create the agent template
        template_json = create_agent_template(spec_str)
        
        # Parse the template JSON
        template = json.loads(template_json)
        
        return template
    except Exception as e:
        logger.error(f"Error creating agent template: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating agent template: {str(e)}")

@router.post("/add-tool", response_model=Dict[str, Any])
async def add_tool(template: Dict[str, Any], tool_spec: ToolSpec):
    """Add a tool to an agent template."""
    try:
        # Convert the template to JSON
        template_json = json.dumps(template)
        
        # Convert the tool spec to a string format expected by the agent creator
        tool_str = f"""
        name: {tool_spec.name}
        description: {tool_spec.description}
        parameters:
        {os.linesep.join([f'- {param["name"]}: {param["type"]}: {param["description"]}' for param in tool_spec.parameters])}
        returns: {tool_spec.returns["type"]}: {tool_spec.returns["description"]}
        implementation:
        {tool_spec.implementation}
        """
        
        # Add the tool to the template
        updated_template_json = add_tool_to_template(template_json, tool_str)
        
        # Parse the updated template JSON
        updated_template = json.loads(updated_template_json)
        
        return updated_template
    except Exception as e:
        logger.error(f"Error adding tool to agent template: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error adding tool to agent template: {str(e)}")

@router.post("/validate", response_model=ValidationResult)
async def validate_template(template: Dict[str, Any]):
    """Validate an agent template."""
    try:
        # Convert the template to JSON
        template_json = json.dumps(template)
        
        # Validate the template
        result = validate_agent_template(template_json)
        
        # Return the validation result
        return {
            "valid": True,
            "message": result,
            "errors": None
        }
    except Exception as e:
        logger.error(f"Error validating agent template: {str(e)}")
        return {
            "valid": False,
            "message": f"Error validating agent template: {str(e)}",
            "errors": [str(e)]
        }

@router.post("/generate-code", response_model=CodeGenerationResult)
async def generate_code(template: Dict[str, Any]):
    """Generate Python code for an agent from a template."""
    try:
        # Convert the template to JSON
        template_json = json.dumps(template)
        
        # Generate the code
        code = generate_agent_code(template_json)
        
        # Return the generated code
        return {"code": code}
    except Exception as e:
        logger.error(f"Error generating agent code: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating agent code: {str(e)}")

@router.post("/deploy", response_model=DeploymentResult)
async def deploy_agent_endpoint(template: Dict[str, Any], options: DeploymentOptions):
    """Deploy an agent from a template."""
    try:
        # Convert the template to JSON
        template_json = json.dumps(template)
        
        # Deploy the agent
        result = deploy_agent(template_json)  # Removed sandbox parameter to fix deployment issue
        
        # Extract the agent ID from the result
        agent_id = template["agent"]["name"]
        
        # Return the deployment result
        return {
            "success": True,
            "message": result,
            "agent_id": agent_id
        }
    except Exception as e:
        logger.error(f"Error deploying agent: {str(e)}")
        return {
            "success": False,
            "message": f"Error deploying agent: {str(e)}",
            "agent_id": None
        }

@router.get("/sandbox-agents", response_model=List[Dict[str, Any]])
async def get_sandbox_agents():
    """Get a list of agents in the sandbox environment."""
    try:
        # Get the sandbox directory
        sandbox_dir = FilePath(__file__).parent.parent / "agents" / "sandbox"
        
        # Check if the sandbox directory exists
        if not sandbox_dir.exists():
            return []
        
        # Get a list of Python files in the sandbox directory
        agent_files = list(sandbox_dir.glob("*.py"))
        
        # Extract agent information from the files
        agents = []
        for agent_file in agent_files:
            agent_name = agent_file.stem
            agents.append({
                "id": agent_name,
                "name": agent_name.capitalize(),
                "file": str(agent_file),
                "sandbox": True
            })
        
        return agents
    except Exception as e:
        logger.error(f"Error getting sandbox agents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting sandbox agents: {str(e)}")

@router.get("/templates", response_model=List[Dict[str, Any]])
async def get_templates():
    """Get a list of available agent templates."""
    try:
        # Define the templates directory
        templates_dir = FilePath(__file__).parent.parent / "agents" / "templates"
        
        # Check if the templates directory exists
        if not templates_dir.exists():
            templates_dir.mkdir(parents=True, exist_ok=True)
            return []
        
        # Get a list of JSON files in the templates directory
        template_files = list(templates_dir.glob("*.json"))
        
        # Extract template information from the files
        templates = []
        for template_file in template_files:
            try:
                with open(template_file, "r") as f:
                    template = json.load(f)
                
                templates.append({
                    "id": template_file.stem,
                    "name": template.get("agent", {}).get("name", template_file.stem),
                    "description": template.get("agent", {}).get("description", ""),
                    "type": template.get("agent", {}).get("type", ""),
                    "file": str(template_file),
                    "template": template
                })
            except Exception as e:
                logger.error(f"Error loading template {template_file}: {str(e)}")
        
        return templates
    except Exception as e:
        logger.error(f"Error getting templates: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting templates: {str(e)}")

@router.post("/templates/{template_id}", response_model=Dict[str, Any])
async def save_template(template_id: str, template: Dict[str, Any]):
    """Save an agent template."""
    try:
        # Define the templates directory
        templates_dir = FilePath(__file__).parent.parent / "agents" / "templates"
        
        # Create the templates directory if it doesn't exist
        templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Define the template file path
        template_file = templates_dir / f"{template_id}.json"
        
        # Write the template to the file
        with open(template_file, "w") as f:
            json.dump(template, f, indent=2)
        
        return {
            "id": template_id,
            "name": template.get("agent", {}).get("name", template_id),
            "description": template.get("agent", {}).get("description", ""),
            "type": template.get("agent", {}).get("type", ""),
            "file": str(template_file),
            "template": template
        }
    except Exception as e:
        logger.error(f"Error saving template: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saving template: {str(e)}")

@router.get("/templates/{template_id}", response_model=Dict[str, Any])
async def get_template(template_id: str):
    """Get an agent template by ID."""
    try:
        # Define the templates directory
        templates_dir = FilePath(__file__).parent.parent / "agents" / "templates"
        
        # Define the template file path
        template_file = templates_dir / f"{template_id}.json"
        
        # Check if the template file exists
        if not template_file.exists():
            raise HTTPException(status_code=404, detail=f"Template {template_id} not found")
        
        # Read the template from the file
        with open(template_file, "r") as f:
            template = json.load(f)
        
        return {
            "id": template_id,
            "name": template.get("agent", {}).get("name", template_id),
            "description": template.get("agent", {}).get("description", ""),
            "type": template.get("agent", {}).get("type", ""),
            "file": str(template_file),
            "template": template
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting template: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting template: {str(e)}")

@router.delete("/templates/{template_id}", response_model=Dict[str, Any])
async def delete_template(template_id: str):
    """Delete an agent template by ID."""
    try:
        # Define the templates directory
        templates_dir = FilePath(__file__).parent.parent / "agents" / "templates"
        
        # Define the template file path
        template_file = templates_dir / f"{template_id}.json"
        
        # Check if the template file exists
        if not template_file.exists():
            raise HTTPException(status_code=404, detail=f"Template {template_id} not found")
        
        # Delete the template file
        template_file.unlink()
        
        return {"message": f"Template {template_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting template: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting template: {str(e)}")
