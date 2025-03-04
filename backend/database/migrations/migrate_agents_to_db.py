#!/usr/bin/env python
"""
Migration script to migrate existing agents to the database.

This script loads agent templates from the templates directory and saves them to the database.
"""

import os
import sys
import json
import logging
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
logger = logging.getLogger("mosaic.database.migrations.migrate_agents")

# Import the agent generator
try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.agents.agent_generator import AgentGenerator
    from mosaic.backend.database.repository import AgentRepository
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.agents.agent_generator import AgentGenerator
    from backend.database.repository import AgentRepository

def migrate_agents_to_db():
    """Migrate existing agents to the database."""
    try:
        # Get the templates directory
        templates_dir = Path(parent_dir) / "agents" / "templates"
        
        # Check if the templates directory exists
        if not templates_dir.exists():
            logger.warning(f"Templates directory {templates_dir} does not exist")
            return False
        
        # Get a list of JSON files in the templates directory
        template_files = list(templates_dir.glob("*.json"))
        
        if not template_files:
            logger.warning(f"No template files found in {templates_dir}")
            return False
        
        # Create an agent generator
        generator = AgentGenerator()
        
        # Load each template and save it to the database
        for template_file in template_files:
            try:
                logger.info(f"Processing template file: {template_file}")
                
                # Load the template
                with open(template_file, "r") as f:
                    template = json.load(f)
                
                # Check if the agent already exists in the database
                agent_name = template.get("agent", {}).get("name")
                if not agent_name:
                    logger.warning(f"Template {template_file} does not have a name, skipping")
                    continue
                
                existing_agent = AgentRepository.get_agent_by_name(agent_name)
                if existing_agent:
                    logger.info(f"Agent {agent_name} already exists in the database, skipping")
                    continue
                
                # Validate the template
                generator.validate_definition(template)
                
                # Save the template to the database
                agent, tools, capabilities = generator.save_definition_to_db(template)
                
                logger.info(f"Saved agent {agent.name} to database with ID {agent.id}")
                logger.info(f"Added {len(tools)} tools and {len(capabilities)} capabilities")
                
            except Exception as e:
                logger.error(f"Error processing template {template_file}: {str(e)}")
        
        logger.info("Migration completed successfully")
        return True
    except Exception as e:
        logger.error(f"Error migrating agents to database: {str(e)}")
        return False

if __name__ == "__main__":
    # Migrate agents to the database
    success = migrate_agents_to_db()
    
    if success:
        print("Successfully migrated agents to the database")
        sys.exit(0)
    else:
        print("Error migrating agents to the database")
        sys.exit(1)
