"""
Database Service for MOSAIC

This module provides service functions for managing conversations and messages.
These functions provide a higher-level interface for the API endpoints to
interact with the database.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple

from .repository import (
    ConversationRepository,
    MessageRepository,
    AttachmentRepository,
    message_to_dict,
    conversation_to_dict
)

# Configure logging
logger = logging.getLogger("mosaic.database.service")

class ChatService:
    """
    Service for managing chat conversations and messages.
    """
    
    @staticmethod
    def get_or_create_conversation(agent_id: str) -> Tuple[int, bool]:
        """
        Get the active conversation for an agent, or create a new one if none exists.
        
        Args:
            agent_id: The ID of the agent
            
        Returns:
            A tuple of (conversation_id, created) where created is True if a new
            conversation was created, False otherwise
        """
        # Try to get the active conversation
        conversation = ConversationRepository.get_active_conversation_for_agent(agent_id)
        
        if conversation:
            return conversation.id, False
        
        # Create a new conversation
        conversation = ConversationRepository.create_conversation(agent_id)
        return conversation.id, True
    
    @staticmethod
    def get_conversation_messages(agent_id: str) -> List[Dict[str, Any]]:
        """
        Get all messages for the active conversation with an agent.
        
        Args:
            agent_id: The ID of the agent
            
        Returns:
            A list of message dictionaries
        """
        # Get the active conversation
        conversation = ConversationRepository.get_active_conversation_for_agent(agent_id)
        
        if not conversation:
            # No active conversation, return empty list
            return []
        
        # Get messages for the conversation
        messages = MessageRepository.get_messages_for_conversation(conversation.id)
        
        # Convert to dictionaries
        return [message_to_dict(message) for message in messages]
    
    @staticmethod
    def add_message(
        agent_id: str,
        role: str,
        content: str,
        timestamp: Optional[int] = None,
        status: Optional[str] = None,
        error: Optional[str] = None,
        client_message_id: Optional[str] = None,
        message_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a message to the active conversation with an agent.
        
        Args:
            agent_id: The ID of the agent
            role: The role of the message sender ("user" or "assistant")
            content: The content of the message
            timestamp: Optional timestamp (defaults to current time in milliseconds)
            status: Optional status of the message
            error: Optional error message
            client_message_id: Optional client-side message ID
            message_id: Optional message ID (defaults to a new UUID)
            
        Returns:
            The created message as a dictionary
        """
        # Get or create the active conversation
        conversation_id, created = ChatService.get_or_create_conversation(agent_id)
        
        # Create the message
        message = MessageRepository.create_message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            timestamp=timestamp,
            status=status,
            error=error,
            client_message_id=client_message_id,
            message_id=message_id
        )
        
        # Convert to dictionary
        return message_to_dict(message)
    
    @staticmethod
    def add_log_to_message(message_id: str, log_entry: str) -> None:
        """
        Add a log entry to a message.
        
        Args:
            message_id: The ID of the message
            log_entry: The log entry to add
        """
        MessageRepository.add_log_to_message(message_id, log_entry)
    
    @staticmethod
    def clear_conversation(agent_id: str) -> bool:
        """
        Clear the active conversation with an agent by deactivating it.
        
        Args:
            agent_id: The ID of the agent
            
        Returns:
            True if the conversation was cleared, False otherwise
        """
        # Get the active conversation
        conversation = ConversationRepository.get_active_conversation_for_agent(agent_id)
        
        if not conversation:
            # No active conversation to clear
            return False
        
        # Deactivate the conversation
        ConversationRepository.deactivate_conversation(conversation.id)
        
        # Create a new conversation
        ConversationRepository.create_conversation(agent_id)
        
        return True
    
    @staticmethod
    def get_conversation_history(agent_id: str) -> List[Dict[str, Any]]:
        """
        Get the conversation history for an agent.
        
        Args:
            agent_id: The ID of the agent
            
        Returns:
            A list of conversation dictionaries
        """
        # Get all conversations for the agent
        conversations = ConversationRepository.get_conversations_for_agent(agent_id)
        
        # Convert to dictionaries
        return [conversation_to_dict(conversation) for conversation in conversations]
    
    @staticmethod
    def get_conversation_with_messages(conversation_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a conversation with all its messages.
        
        Args:
            conversation_id: The ID of the conversation
            
        Returns:
            The conversation dictionary with messages, or None if not found
        """
        # Get the conversation
        conversation = ConversationRepository.get_conversation(conversation_id)
        
        if not conversation:
            return None
        
        # Convert to dictionary with messages
        return conversation_to_dict(conversation, include_messages=True)
    
    @staticmethod
    def get_messages_for_agent_state(agent_id: str) -> List[Dict[str, str]]:
        """
        Get messages for an agent in a format suitable for the agent state.
        
        Args:
            agent_id: The ID of the agent
            
        Returns:
            A list of message dictionaries in the format expected by the agent
        """
        # Get messages for the active conversation
        messages = ChatService.get_conversation_messages(agent_id)
        
        # Convert to the format expected by the agent
        return [
            {
                "role": message["role"],
                "content": message["content"]
            }
            for message in messages
        ]


class AttachmentService:
    """
    Service for managing attachments.
    """
    
    @staticmethod
    def add_attachment(
        message_id: str,
        attachment_type: str,
        filename: Optional[str] = None,
        content_type: Optional[str] = None,
        size: Optional[int] = None,
        storage_path: Optional[str] = None,
        data: Optional[bytes] = None
    ) -> Dict[str, Any]:
        """
        Add an attachment to a message.
        
        Args:
            message_id: The ID of the message
            attachment_type: The type of attachment ("image", "file", etc.)
            filename: Optional filename
            content_type: Optional MIME type
            size: Optional size in bytes
            storage_path: Optional path to file on disk
            data: Optional binary data
            
        Returns:
            The created attachment as a dictionary
        """
        # Create the attachment
        attachment = AttachmentRepository.create_attachment(
            message_id=message_id,
            attachment_type=attachment_type,
            filename=filename,
            content_type=content_type,
            size=size,
            storage_path=storage_path,
            data=data
        )
        
        # Convert to dictionary
        return {
            "id": attachment.id,
            "type": attachment.type,
            "filename": attachment.filename,
            "contentType": attachment.content_type,
            "size": attachment.size,
            "url": f"/api/attachments/{attachment.id}" if not attachment.data else None
        }
    
    @staticmethod
    def get_attachment(attachment_id: int) -> Optional[Dict[str, Any]]:
        """
        Get an attachment by ID.
        
        Args:
            attachment_id: The ID of the attachment
            
        Returns:
            The attachment as a dictionary, or None if not found
        """
        # Get the attachment
        attachment = AttachmentRepository.get_attachment(attachment_id)
        
        if not attachment:
            return None
        
        # Convert to dictionary
        return {
            "id": attachment.id,
            "type": attachment.type,
            "filename": attachment.filename,
            "contentType": attachment.content_type,
            "size": attachment.size,
            "url": f"/api/attachments/{attachment.id}" if not attachment.data else None,
            "data": attachment.data
        }
