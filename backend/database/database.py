"""
Database Connection Management for MOSAIC

This module handles database connection management for the MOSAIC system.
It provides functions for creating the database connection, creating tables,
and managing database sessions.
"""

import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager

from .models import Base

# Configure logging
logger = logging.getLogger("mosaic.database")

# Get database path from environment variable or use default
DATABASE_PATH = os.getenv("DATABASE_PATH", "database/mosaic.db")

# Ensure the database directory exists
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

# Create database URL
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

# Create session factory
SessionFactory = sessionmaker(bind=engine)

# Create scoped session for thread safety
Session = scoped_session(SessionFactory)

def init_db():
    """
    Initialize the database by creating all tables.
    
    This function creates all tables defined in the models module
    if they don't already exist.
    """
    logger.info(f"Initializing database at {DATABASE_PATH}")
    Base.metadata.create_all(engine)
    logger.info("Database initialization complete")

@contextmanager
def get_db_session():
    """
    Context manager for database sessions.
    
    This function provides a context manager for database sessions,
    ensuring that sessions are properly closed and transactions are
    committed or rolled back as appropriate.
    
    Example:
        with get_db_session() as session:
            session.query(User).all()
    """
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database error: {str(e)}")
        raise
    finally:
        session.close()

def get_engine():
    """
    Get the SQLAlchemy engine.
    
    Returns:
        The SQLAlchemy engine instance.
    """
    return engine

def close_db_connection():
    """
    Close the database connection.
    
    This function should be called when the application is shutting down.
    """
    logger.info("Closing database connection")
    Session.remove()
    engine.dispose()
    logger.info("Database connection closed")
