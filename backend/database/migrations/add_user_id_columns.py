"""
Migration script to add user_id columns to relevant tables for authentication.

This script adds user_id columns to Conversation, Agent, Message, and Attachment tables
to support multi-user functionality with Clerk authentication.
"""

import logging
import sqlite3
import os
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mosaic.database.migrations.add_user_id_columns")

# Add the parent directory to the path so we can import from the parent package
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import the settings from the config
try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.app.config import settings
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.app.config import settings

def get_db_path():
    """Get the absolute path to the database file."""
    # Extract database path from URL
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    logger.info(f"Using database URL: {settings.DATABASE_URL}")
    logger.info(f"Extracted database path: {db_path}")
    return db_path

def run_migration():
    """Run the migration to add user_id columns to relevant tables."""
    db_path = get_db_path()
    logger.info(f"Running migration to add user_id columns to database at {db_path}")
    
    # Ensure the database directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Start a transaction
        conn.execute("BEGIN TRANSACTION")
        
        # Add user_id column to conversations table
        logger.info("Adding user_id column to conversations table")
        cursor.execute("""
        ALTER TABLE conversations
        ADD COLUMN user_id TEXT;
        """)
        
        # Add user_id column to agents table
        logger.info("Adding user_id column to agents table")
        cursor.execute("""
        ALTER TABLE agents
        ADD COLUMN user_id TEXT;
        """)
        
        # Add user_id column to messages table
        logger.info("Adding user_id column to messages table")
        cursor.execute("""
        ALTER TABLE messages
        ADD COLUMN user_id TEXT;
        """)
        
        # Add user_id column to attachments table
        logger.info("Adding user_id column to attachments table")
        cursor.execute("""
        ALTER TABLE attachments
        ADD COLUMN user_id TEXT;
        """)
        
        # Create user_preferences table
        logger.info("Creating user_preferences table")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_preferences (
            id INTEGER PRIMARY KEY,
            user_id TEXT NOT NULL UNIQUE,
            theme TEXT DEFAULT 'system',
            language TEXT DEFAULT 'en',
            notifications BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            settings JSON
        );
        """)
        
        # Create indexes for user_id columns
        logger.info("Creating indexes for user_id columns")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_agents_user_id ON agents(user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_attachments_user_id ON attachments(user_id);")
        
        # Commit the transaction
        conn.execute("COMMIT")
        logger.info("Migration completed successfully")
        
    except Exception as e:
        # Rollback the transaction in case of error
        conn.execute("ROLLBACK")
        logger.error(f"Migration failed: {str(e)}")
        raise
    finally:
        # Close the connection
        conn.close()

if __name__ == "__main__":
    run_migration()
