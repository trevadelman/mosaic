"""
Migration script to clear all existing conversations and associated data.

This script deletes all conversations, messages, message logs, and attachments
from the database to ensure that all new conversations will have user IDs
properly associated with them.
"""

import logging
import sqlite3
import os
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mosaic.database.migrations.clear_conversations")

# Add the parent directory to the path so we can import from the parent package
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Create a modified Settings class that ignores extra environment variables
from pydantic_settings import BaseSettings

class ModifiedSettings(BaseSettings):
    # Database settings
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        f"sqlite:///{os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'database', 'mosaic.db'))}"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra environment variables

# Create settings instance
settings = ModifiedSettings()

def get_db_path():
    """Get the absolute path to the database file."""
    # Extract database path from URL
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    logger.info(f"Using database URL: {settings.DATABASE_URL}")
    logger.info(f"Extracted database path: {db_path}")
    return db_path

def run_migration():
    """Run the migration to clear all conversations and associated data."""
    db_path = get_db_path()
    logger.info(f"Running migration to clear all conversations from database at {db_path}")
    
    # Ensure the database directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Start a transaction
        conn.execute("BEGIN TRANSACTION")
        
        # Get counts before deletion for logging
        cursor.execute("SELECT COUNT(*) FROM conversations")
        conversation_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM messages")
        message_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM message_logs")
        log_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM attachments")
        attachment_count = cursor.fetchone()[0]
        
        logger.info(f"Found {conversation_count} conversations, {message_count} messages, {log_count} logs, and {attachment_count} attachments")
        
        # Delete all message logs (foreign key to messages)
        logger.info("Deleting all message logs")
        cursor.execute("DELETE FROM message_logs")
        
        # Delete all attachments (foreign key to messages)
        logger.info("Deleting all attachments")
        cursor.execute("DELETE FROM attachments")
        
        # Delete all messages (foreign key to conversations)
        logger.info("Deleting all messages")
        cursor.execute("DELETE FROM messages")
        
        # Delete all conversations
        logger.info("Deleting all conversations")
        cursor.execute("DELETE FROM conversations")
        
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
