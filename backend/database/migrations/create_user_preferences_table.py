"""
Migration script to create the user_preferences table.

This script creates the user_preferences table in the database.
"""

import os
import sys
import json
import logging
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, JSON, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("mosaic.migrations.create_user_preferences_table")

# Add the parent directory to the path so we can import the database module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Import the database module
try:
    from mosaic.backend.database import Base, get_engine, get_db_session
    from mosaic.backend.database.models import UserPreference
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.database import Base, get_engine, get_db_session
    from backend.database.models import UserPreference

def create_user_preferences_table():
    """Create the user_preferences table."""
    # Get the engine
    engine = get_engine()
    
    # Create the table
    UserPreference.__table__.create(engine, checkfirst=True)
    
    logger.info("Created user_preferences table")

def main():
    """Run the migration."""
    try:
        # Create the user_preferences table
        create_user_preferences_table()
        
        # Create a default user preference
        with get_db_session() as session:
            # Check if the default user preference already exists
            default_user_preference = session.query(UserPreference).filter(
                UserPreference.user_id == "default"
            ).first()
            
            if not default_user_preference:
                # Create the default user preference
                default_user_preference = UserPreference(
                    user_id="default",
                    theme="system",
                    language="en",
                    notifications=True,
                    settings={}
                )
                
                # Add to the session
                session.add(default_user_preference)
                
                # Commit the changes
                session.commit()
                
                logger.info("Created default user preference")
            else:
                logger.info("Default user preference already exists")
        
        logger.info("Migration completed successfully")
    except Exception as e:
        logger.error(f"Error running migration: {str(e)}")
        raise

if __name__ == "__main__":
    main()
