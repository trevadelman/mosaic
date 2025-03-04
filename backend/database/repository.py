"""
Database Repository for MOSAIC

This module provides repository classes for database operations.
These classes provide a clean API for the rest of the application
to interact with the database.
"""

import logging
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import desc

from .models import Conversation, Message, Attachment, MessageLog
from .database import get_db_session

# Configure logging
logger = logging.getLogger("mosaic.database.repository")

class ConversationRepository:
    """
    Repository for conversation-related database operations.
    """
    
    @staticmethod
    def create_conversation(agent_id: str, title: Optional[str] = None) -> Conversation:
        """
        Create a new conversation.
        
        Args:
            agent_id: The ID of the agent
            title: Optional title for the conversation
            
        Returns:
            The created conversation
        """
        with get_db_session() as session:
            conversation = Conversation(
                agent_id=agent_id,
                title=title or f"Conversation with {agent_id}"
            )
            session.add(conversation)
            session.commit()
            logger.info(f"Created conversation {conversation.id} for agent {agent_id}")
            
            # Detach the conversation from the session by expunging it
            session.expunge(conversation)
            
            return conversation
    
    @staticmethod
    def get_conversation(conversation_id: int) -> Optional[Conversation]:
        """
        Get a conversation by ID.
        
        Args:
            conversation_id: The ID of the conversation
            
        Returns:
            The conversation, or None if not found
        """
        with get_db_session() as session:
            conversation = session.query(Conversation).filter(Conversation.id == conversation_id).first()
            
            # If we found a conversation, detach it from the session by expunging it
            if conversation:
                session.expunge(conversation)
                
            return conversation
    
    @staticmethod
    def get_conversations_for_agent(agent_id: str) -> List[Conversation]:
        """
        Get all conversations for an agent.
        
        Args:
            agent_id: The ID of the agent
            
        Returns:
            A list of conversations
        """
        with get_db_session() as session:
            conversations = session.query(Conversation).filter(
                Conversation.agent_id == agent_id
            ).order_by(desc(Conversation.updated_at)).all()
            
            # Detach all conversations from the session by expunging them
            for conversation in conversations:
                session.expunge(conversation)
                
            return conversations
    
    @staticmethod
    def get_active_conversation_for_agent(agent_id: str) -> Optional[Conversation]:
        """
        Get the active conversation for an agent.
        
        Args:
            agent_id: The ID of the agent
            
        Returns:
            The active conversation, or None if not found
        """
        with get_db_session() as session:
            conversation = session.query(Conversation).filter(
                Conversation.agent_id == agent_id,
                Conversation.is_active == True
            ).order_by(desc(Conversation.updated_at)).first()
            
            # If we found a conversation, detach it from the session by expunging it
            if conversation:
                session.expunge(conversation)
                
            return conversation
    
    @staticmethod
    def update_conversation_title(conversation_id: int, title: str) -> Optional[Conversation]:
        """
        Update the title of a conversation.
        
        Args:
            conversation_id: The ID of the conversation
            title: The new title
            
        Returns:
            The updated conversation, or None if not found
        """
        with get_db_session() as session:
            conversation = session.query(Conversation).filter(Conversation.id == conversation_id).first()
            if conversation:
                conversation.title = title
                session.commit()
                logger.info(f"Updated title for conversation {conversation_id}")
                
                # Detach the conversation from the session by expunging it
                session.expunge(conversation)
            
            return conversation
    
    @staticmethod
    def deactivate_conversation(conversation_id: int) -> Optional[Conversation]:
        """
        Deactivate a conversation.
        
        Args:
            conversation_id: The ID of the conversation
            
        Returns:
            The updated conversation, or None if not found
        """
        with get_db_session() as session:
            conversation = session.query(Conversation).filter(Conversation.id == conversation_id).first()
            if conversation:
                conversation.is_active = False
                session.commit()
                logger.info(f"Deactivated conversation {conversation_id}")
                
                # Detach the conversation from the session by expunging it
                session.expunge(conversation)
            
            return conversation
    
    @staticmethod
    def delete_conversation(conversation_id: int) -> bool:
        """
        Delete a conversation and all its messages.
        
        Args:
            conversation_id: The ID of the conversation
            
        Returns:
            True if the conversation was deleted, False otherwise
        """
        with get_db_session() as session:
            conversation = session.query(Conversation).filter(Conversation.id == conversation_id).first()
            if conversation:
                session.delete(conversation)
                session.commit()
                logger.info(f"Deleted conversation {conversation_id}")
                return True
            return False


class MessageRepository:
    """
    Repository for message-related database operations.
    """
    
    @staticmethod
    def create_message(
        conversation_id: int,
        role: str,
        content: str,
        timestamp: Optional[int] = None,
        status: Optional[str] = None,
        error: Optional[str] = None,
        client_message_id: Optional[str] = None,
        message_id: Optional[str] = None
    ) -> Message:
        """
        Create a new message.
        
        Args:
            conversation_id: The ID of the conversation
            role: The role of the message sender ("user" or "assistant")
            content: The content of the message
            timestamp: Optional timestamp (defaults to current time in milliseconds)
            status: Optional status of the message
            error: Optional error message
            client_message_id: Optional client-side message ID
            message_id: Optional message ID (defaults to a new UUID)
            
        Returns:
            The created message
        """
        with get_db_session() as session:
            message = Message(
                id=message_id or str(uuid.uuid4()),
                conversation_id=conversation_id,
                role=role,
                content=content,
                timestamp=timestamp or int(datetime.now().timestamp() * 1000),
                status=status,
                error=error,
                client_message_id=client_message_id
            )
            session.add(message)
            session.commit()
            logger.info(f"Created message {message.id} in conversation {conversation_id}")
            
            # Detach the message from the session by expunging it
            session.expunge(message)
            
            return message
    
    @staticmethod
    def get_message(message_id: str) -> Optional[Message]:
        """
        Get a message by ID.
        
        Args:
            message_id: The ID of the message
            
        Returns:
            The message, or None if not found
        """
        with get_db_session() as session:
            message = session.query(Message).filter(Message.id == message_id).first()
            
            # If we found a message, detach it from the session by expunging it
            if message:
                session.expunge(message)
                
            return message
    
    @staticmethod
    def get_messages_for_conversation(conversation_id: int) -> List[Message]:
        """
        Get all messages for a conversation.
        
        Args:
            conversation_id: The ID of the conversation
            
        Returns:
            A list of messages
        """
        with get_db_session() as session:
            messages = session.query(Message).filter(
                Message.conversation_id == conversation_id
            ).order_by(Message.timestamp).all()
            
            # Detach all messages from the session by expunging them
            for message in messages:
                session.expunge(message)
                
            return messages
    
    @staticmethod
    def add_log_to_message(message_id: str, log_entry: str) -> MessageLog:
        """
        Add a log entry to a message.
        
        Args:
            message_id: The ID of the message
            log_entry: The log entry to add
            
        Returns:
            The created message log
        """
        with get_db_session() as session:
            message_log = MessageLog(
                message_id=message_id,
                log_entry=log_entry
            )
            session.add(message_log)
            session.commit()
            
            # Detach the message log from the session by expunging it
            session.expunge(message_log)
            
            return message_log
    
    @staticmethod
    def get_logs_for_message(message_id: str) -> List[MessageLog]:
        """
        Get all logs for a message.
        
        Args:
            message_id: The ID of the message
            
        Returns:
            A list of message logs
        """
        with get_db_session() as session:
            logs = session.query(MessageLog).filter(
                MessageLog.message_id == message_id
            ).order_by(MessageLog.timestamp).all()
            
            # Detach all logs from the session by expunging them
            for log in logs:
                session.expunge(log)
                
            return logs


class AttachmentRepository:
    """
    Repository for attachment-related database operations.
    """
    
    @staticmethod
    def create_attachment(
        message_id: str,
        attachment_type: str,
        filename: Optional[str] = None,
        content_type: Optional[str] = None,
        size: Optional[int] = None,
        storage_path: Optional[str] = None,
        data: Optional[bytes] = None
    ) -> Attachment:
        """
        Create a new attachment.
        
        Args:
            message_id: The ID of the message
            attachment_type: The type of attachment ("image", "file", etc.)
            filename: Optional filename
            content_type: Optional MIME type
            size: Optional size in bytes
            storage_path: Optional path to file on disk
            data: Optional binary data
            
        Returns:
            The created attachment
        """
        with get_db_session() as session:
            attachment = Attachment(
                message_id=message_id,
                type=attachment_type,
                filename=filename,
                content_type=content_type,
                size=size,
                storage_path=storage_path,
                data=data
            )
            session.add(attachment)
            session.commit()
            logger.info(f"Created attachment for message {message_id}")
            
            # Detach the attachment from the session by expunging it
            session.expunge(attachment)
            
            return attachment
    
    @staticmethod
    def get_attachment(attachment_id: int) -> Optional[Attachment]:
        """
        Get an attachment by ID.
        
        Args:
            attachment_id: The ID of the attachment
            
        Returns:
            The attachment, or None if not found
        """
        with get_db_session() as session:
            attachment = session.query(Attachment).filter(Attachment.id == attachment_id).first()
            
            # If we found an attachment, detach it from the session by expunging it
            if attachment:
                session.expunge(attachment)
                
            return attachment
    
    @staticmethod
    def get_attachments_for_message(message_id: str) -> List[Attachment]:
        """
        Get all attachments for a message.
        
        Args:
            message_id: The ID of the message
            
        Returns:
            A list of attachments
        """
        with get_db_session() as session:
            attachments = session.query(Attachment).filter(
                Attachment.message_id == message_id
            ).all()
            
            # Detach all attachments from the session by expunging them
            for attachment in attachments:
                session.expunge(attachment)
                
            return attachments


# Helper functions for converting between database models and API models

def message_to_dict(message: Message) -> Dict[str, Any]:
    """
    Convert a Message model to a dictionary for API responses.
    
    Args:
        message: The Message model
        
    Returns:
        A dictionary representation of the message
    """
    # Get the agent_id safely
    agent_id = None
    try:
        # Try to access the conversation attribute directly
        agent_id = message.conversation.agent_id
    except Exception:
        # If that fails, query the database for the conversation
        with get_db_session() as session:
            conversation = session.query(Conversation).filter(
                Conversation.id == message.conversation_id
            ).first()
            if conversation:
                agent_id = conversation.agent_id
    
    result = {
        "id": message.id,
        "role": message.role,
        "content": message.content,
        "timestamp": message.timestamp,
        "agentId": agent_id
    }
    
    if message.status:
        result["status"] = message.status
    
    if message.error:
        result["error"] = message.error
    
    if message.client_message_id:
        result["clientMessageId"] = message.client_message_id
    
    # Add logs if available
    logs = MessageRepository.get_logs_for_message(message.id)
    if logs:
        result["logs"] = [log.log_entry for log in logs]
    
    # Add attachments if available
    attachments = AttachmentRepository.get_attachments_for_message(message.id)
    if attachments:
        result["attachments"] = [
            {
                "id": attachment.id,
                "type": attachment.type,
                "filename": attachment.filename,
                "contentType": attachment.content_type,
                "size": attachment.size,
                "url": f"/api/attachments/{attachment.id}" if not attachment.data else None
            }
            for attachment in attachments
        ]
    
    return result


def conversation_to_dict(conversation: Conversation, include_messages: bool = False) -> Dict[str, Any]:
    """
    Convert a Conversation model to a dictionary for API responses.
    
    Args:
        conversation: The Conversation model
        include_messages: Whether to include messages in the result
        
    Returns:
        A dictionary representation of the conversation
    """
    result = {
        "id": conversation.id,
        "agentId": conversation.agent_id,
        "title": conversation.title,
        "createdAt": conversation.created_at.isoformat(),
        "updatedAt": conversation.updated_at.isoformat(),
        "isActive": conversation.is_active
    }
    
    if include_messages:
        messages = MessageRepository.get_messages_for_conversation(conversation.id)
        result["messages"] = [message_to_dict(message) for message in messages]
    
    return result
