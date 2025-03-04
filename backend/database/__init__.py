"""
Database Package for MOSAIC

This package provides database functionality for the MOSAIC system.
"""

from .models import Base, Conversation, Message, Attachment, MessageLog
from .database import init_db, get_db_session, get_engine, close_db_connection
from .repository import (
    ConversationRepository,
    MessageRepository,
    AttachmentRepository,
    message_to_dict,
    conversation_to_dict
)
from .service import ChatService, AttachmentService

__all__ = [
    # Models
    'Base',
    'Conversation',
    'Message',
    'Attachment',
    'MessageLog',
    
    # Database functions
    'init_db',
    'get_db_session',
    'get_engine',
    'close_db_connection',
    
    # Repositories
    'ConversationRepository',
    'MessageRepository',
    'AttachmentRepository',
    
    # Services
    'ChatService',
    'AttachmentService',
    
    # Helper functions
    'message_to_dict',
    'conversation_to_dict'
]
