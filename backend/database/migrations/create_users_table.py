"""
Migration script to create the users table.

This script creates the users table in the database.
"""

import os
import sys
import logging
from sqlalchemy import create_engine, Column, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mosaic.migrations.create_users_table")

# Add the parent directory to the path so we can import from the parent package
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import the settings from the config
try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.app.config import settings
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.app.config import settings

# Create a base class for declarative models
Base = declarative_base()

# Log the database URL being used
logger.info(f"Using database URL: {settings.DATABASE_URL}")

# Define the User model for this migration
class User(Base):
    """
    Model for a user.
    
    Stores user information from Clerk.
    """
    __tablename__ = "users"
    
    id = Column(String(255), primary_key=True)  # Clerk user ID
    email = Column(String(255), nullable=True, unique=True, index=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    user_metadata = Column(JSON, nullable=True)  # Renamed from metadata to avoid conflict with SQLAlchemy
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f"<User(id='{self.id}', email='{self.email}')>"

def run_migration():
    """
    Run the migration to create the users table.
    """
    # Create an engine that connects to the database
    engine = create_engine(settings.DATABASE_URL)
    
    # Create the table
    Base.metadata.create_all(engine)
    
    logger.info("Created users table")

if __name__ == "__main__":
    run_migration()
