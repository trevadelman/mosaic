"""
Migration script to create agent-related database tables.

This script creates the tables for agents, tools, and capabilities.
"""

import os
import sys
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
logger = logging.getLogger("mosaic.database.migrations")

# Import the database models and connection
try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.database.models import Base, Agent, Tool, Capability
    from mosaic.backend.database.database import get_engine
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.database.models import Base, Agent, Tool, Capability
    from backend.database.database import get_engine

def create_agent_tables():
    """Create the agent-related database tables."""
    try:
        # Get the database engine
        engine = get_engine()
        
        # Create the tables
        Base.metadata.create_all(engine, tables=[
            Agent.__table__,
            Tool.__table__,
            Capability.__table__
        ])
        
        logger.info("Successfully created agent-related database tables")
        return True
    except Exception as e:
        logger.error(f"Error creating agent-related database tables: {str(e)}")
        return False

if __name__ == "__main__":
    # Create the migrations directory if it doesn't exist
    migrations_dir = Path(__file__).parent
    migrations_dir.mkdir(parents=True, exist_ok=True)
    
    # Create the agent-related database tables
    success = create_agent_tables()
    
    if success:
        print("Successfully created agent-related database tables")
        sys.exit(0)
    else:
        print("Error creating agent-related database tables")
        sys.exit(1)
