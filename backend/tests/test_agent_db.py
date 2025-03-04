"""
Test script for database-driven agent metadata.

This script tests the database-driven agent metadata functionality.
"""

import os
import sys
import logging
import json
from pathlib import Path

# Add the parent directory to the Python path
parent_dir = str(Path(__file__).parent.parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("mosaic.tests.agent_db")

# Import the agent generator and database models
try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.agents.agent_generator import AgentGenerator
    from mosaic.backend.database.repository import AgentRepository
    from mosaic.backend.database.models import Agent, Tool, Capability
    from mosaic.backend.database.migrations.create_agent_tables import create_agent_tables
    from mosaic.backend.agents.base import agent_registry
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.agents.agent_generator import AgentGenerator
    from backend.database.repository import AgentRepository
    from backend.database.models import Agent, Tool, Capability
    from backend.database.migrations.create_agent_tables import create_agent_tables
    from backend.agents.base import agent_registry

def test_agent_db():
    """Test the database-driven agent metadata functionality."""
    try:
        # Create the agent-related database tables
        create_agent_tables()
        
        # Create an agent generator
        generator = AgentGenerator()
        
        # Create a sample agent definition
        definition = {
            "agent": {
                "name": "test_db_agent",
                "type": "Utility",
                "description": "A test agent for database-driven metadata",
                "icon": "🧪",
                "systemPrompt": "You are a test agent for database-driven metadata.",
                "tools": [
                    {
                        "name": "test_tool",
                        "description": "A test tool",
                        "parameters": [
                            {
                                "name": "param1",
                                "type": "string",
                                "description": "A test parameter"
                            }
                        ],
                        "returns": {
                            "type": "string",
                            "description": "A test return value"
                        },
                        "implementation": {
                            "code": """
@tool
def test_tool(param1: str) -> str:
    \"\"\"
    A test tool.
    
    Args:
        param1: A test parameter
        
    Returns:
        A test return value
    \"\"\"
    return f"Test tool called with param1={param1}"
""",
                            "dependencies": []
                        }
                    }
                ],
                "capabilities": ["testing"]
            }
        }
        
        # Validate the definition
        generator.validate_definition(definition)
        
        # Save the definition to the database
        agent, tools, capabilities = generator.save_definition_to_db(definition)
        logger.info(f"Saved agent to database with ID {agent.id}")
        
        # Load the definition from the database
        loaded_definition = generator.load_definition_from_db(agent.id)
        logger.info(f"Loaded agent definition from database: {loaded_definition['agent']['name']}")
        
        # Generate code for the agent
        code = generator.generate_agent_class_from_db(agent.id)
        logger.info(f"Generated code for agent: {len(code)} characters")
        
        # Create a simple model for testing
        class MockModel:
            def invoke(self, messages):
                return {"content": "This is a test response"}
        
        # Register the agent
        agent_registry.model = MockModel()
        agent_obj = generator.register_agent_from_definition(agent.id, agent_registry.model)
        logger.info(f"Registered agent: {agent_obj.name}")
        
        # Clean up
        AgentRepository.delete_agent(agent.id, hard_delete=True)
        logger.info(f"Deleted agent with ID {agent.id}")
        
        return True
    except Exception as e:
        logger.error(f"Error testing database-driven agent metadata: {str(e)}")
        return False

if __name__ == "__main__":
    # Test the database-driven agent metadata functionality
    success = test_agent_db()
    
    if success:
        print("Successfully tested database-driven agent metadata")
        sys.exit(0)
    else:
        print("Error testing database-driven agent metadata")
        sys.exit(1)
