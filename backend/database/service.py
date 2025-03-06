"""
Database Service for MOSAIC

This module provides service functions for managing conversations and messages.
These functions provide a higher-level interface for the API endpoints to
interact with the database.
"""

import logging
import base64
from typing import List, Dict, Any, Optional, Tuple

from .repository import (
    ConversationRepository,
    MessageRepository,
    AttachmentRepository,
    UserPreferenceRepository,
    message_to_dict,
    conversation_to_dict,
    user_preference_to_dict
)
from .models import Attachment
from .database import get_db_session

# Configure logging
logger = logging.getLogger("mosaic.database.service")

class ChatService:
    """
    Service for managing chat conversations and messages.
    """
    
    @staticmethod
    def get_or_create_conversation(agent_id: str, user_id: Optional[str] = None) -> Tuple[int, bool]:
        """
        Get the active conversation for an agent, or create a new one if none exists.
        
        Args:
            agent_id: The ID of the agent
            user_id: Optional user ID to filter by
            
        Returns:
            A tuple of (conversation_id, created) where created is True if a new
            conversation was created, False otherwise
        """
        # Try to get the active conversation
        conversation = ConversationRepository.get_active_conversation_for_agent(agent_id, user_id)
        
        if conversation:
            return conversation.id, False
        
        # Create a new conversation
        conversation = ConversationRepository.create_conversation(agent_id, user_id=user_id)
        return conversation.id, True
    
    @staticmethod
    def get_conversation_messages(agent_id: str, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all messages for the active conversation with an agent.
        
        Args:
            agent_id: The ID of the agent
            user_id: Optional user ID to filter by
            
        Returns:
            A list of message dictionaries
        """
        # Get the active conversation
        conversation = ConversationRepository.get_active_conversation_for_agent(agent_id, user_id)
        
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
        message_id: Optional[str] = None,
        user_id: Optional[str] = None
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
            user_id: Optional user ID to filter by
            
        Returns:
            The created message as a dictionary
        """
        # Get or create the active conversation
        conversation_id, created = ChatService.get_or_create_conversation(agent_id, user_id)
        
        # Create the message
        message = MessageRepository.create_message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            timestamp=timestamp,
            status=status,
            error=error,
            client_message_id=client_message_id,
            message_id=message_id,
            user_id=user_id
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
    def clear_conversation(agent_id: str, user_id: Optional[str] = None) -> bool:
        """
        Clear the active conversation with an agent by deactivating it.
        
        Args:
            agent_id: The ID of the agent
            user_id: Optional user ID to filter by
            
        Returns:
            True if the conversation was cleared, False otherwise
        """
        # Get the active conversation
        conversation = ConversationRepository.get_active_conversation_for_agent(agent_id, user_id)
        
        if not conversation:
            # No active conversation to clear
            return False
        
        # Deactivate the conversation
        ConversationRepository.deactivate_conversation(conversation.id)
        
        # Create a new conversation
        ConversationRepository.create_conversation(agent_id, user_id=user_id)
        
        return True
    
    @staticmethod
    def activate_conversation(conversation_id: int, agent_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Activate a specific conversation and deactivate all other conversations for the same agent and user.
        
        Args:
            conversation_id: The ID of the conversation to activate
            agent_id: The ID of the agent
            user_id: Optional user ID to filter by
            
        Returns:
            The activated conversation as a dictionary, or None if not found
        """
        # Activate the conversation
        conversation = ConversationRepository.activate_conversation(conversation_id, agent_id, user_id)
        
        if not conversation:
            return None
        
        # Convert to dictionary
        return conversation_to_dict(conversation)
    
    @staticmethod
    def delete_conversation(conversation_id: int) -> bool:
        """
        Delete a conversation and all its messages.
        
        Args:
            conversation_id: The ID of the conversation
            
        Returns:
            True if the conversation was deleted, False otherwise
        """
        return ConversationRepository.delete_conversation(conversation_id)
    
    @staticmethod
    def get_conversation_history(agent_id: str, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get the conversation history for an agent.
        
        Args:
            agent_id: The ID of the agent
            user_id: Optional user ID to filter by
            
        Returns:
            A list of conversation dictionaries
        """
        # Get all conversations for the agent
        conversations = ConversationRepository.get_conversations_for_agent(agent_id, user_id)
        
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
    def get_messages_for_agent_state(agent_id: str, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get messages for an agent in a format suitable for the agent state.
        
        Args:
            agent_id: The ID of the agent
            user_id: Optional user ID to filter by
            
        Returns:
            A list of message dictionaries in the format expected by the agent
        """
        # Get messages for the active conversation
        messages = ChatService.get_conversation_messages(agent_id, user_id)
        
        # Convert to the format expected by the agent
        return [
            {
                "role": message["role"],
                "content": message["content"],
                "attachments": message.get("attachments", [])
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
    def update_attachment_message(attachment_id: int, message_id: str) -> bool:
        """
        Update the message ID for an attachment.
        
        Args:
            attachment_id: The ID of the attachment
            message_id: The new message ID
            
        Returns:
            True if the attachment was updated, False otherwise
        """
        try:
            with get_db_session() as session:
                attachment = session.query(Attachment).filter(Attachment.id == attachment_id).first()
                if attachment:
                    attachment.message_id = message_id
                    session.commit()
                    logger.info(f"Updated message ID for attachment {attachment_id} to {message_id}")
                    return True
                return False
        except Exception as e:
            logger.error(f"Error updating attachment message ID: {str(e)}")
            return False
    
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
            "data": base64.b64encode(attachment.data).decode('ascii') if attachment.data and attachment.type.startswith('image/') else None
        }


class UserPreferenceService:
    """
    Service for managing user preferences.
    """
    
    @staticmethod
    def get_user_preference(user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a user preference by user ID.
        
        Args:
            user_id: The Clerk user ID
            
        Returns:
            The user preference as a dictionary, or None if not found
        """
        # Get the user preference
        user_preference = UserPreferenceRepository.get_user_preference(user_id)
        
        if not user_preference:
            return None
        
        # Convert to dictionary
        return user_preference_to_dict(user_preference)
    
    @staticmethod
    def create_user_preference(
        user_id: str,
        theme: Optional[str] = "system",
        language: Optional[str] = "en",
        notifications: Optional[bool] = True,
        settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new user preference.
        
        Args:
            user_id: The Clerk user ID
            theme: Optional theme preference (default: "system")
            language: Optional language preference (default: "en")
            notifications: Optional notifications preference (default: True)
            settings: Optional additional settings
            
        Returns:
            The created user preference as a dictionary
        """
        try:
            # Check if the user preference already exists
            existing_preference = UserPreferenceRepository.get_user_preference(user_id)
            if existing_preference:
                # If it exists, update it instead
                return UserPreferenceService.update_user_preference(
                    user_id=user_id,
                    theme=theme,
                    language=language,
                    notifications=notifications,
                    settings=settings
                )
            
            # Create the user preference
            user_preference = UserPreferenceRepository.create_user_preference(
                user_id=user_id,
                theme=theme,
                language=language,
                notifications=notifications,
                settings=settings
            )
            
            # Convert to dictionary
            return user_preference_to_dict(user_preference)
        except Exception as e:
            logger.error(f"Error creating user preference: {str(e)}")
            raise
    
    @staticmethod
    def update_user_preference(
        user_id: str,
        theme: Optional[str] = None,
        language: Optional[str] = None,
        notifications: Optional[bool] = None,
        settings: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Update a user preference.
        
        Args:
            user_id: The Clerk user ID
            theme: Optional new theme preference
            language: Optional new language preference
            notifications: Optional new notifications preference
            settings: Optional new additional settings
            
        Returns:
            The updated user preference as a dictionary, or None if not found
        """
        # Update the user preference
        user_preference = UserPreferenceRepository.update_user_preference(
            user_id=user_id,
            theme=theme,
            language=language,
            notifications=notifications,
            settings=settings
        )
        
        if not user_preference:
            return None
        
        # Convert to dictionary
        return user_preference_to_dict(user_preference)
    
    @staticmethod
    def delete_user_preference(user_id: str) -> bool:
        """
        Delete a user preference.
        
        Args:
            user_id: The Clerk user ID
            
        Returns:
            True if the user preference was deleted, False otherwise
        """
        return UserPreferenceRepository.delete_user_preference(user_id)
    
    @staticmethod
    def get_or_create_user_preference(
        user_id: str,
        theme: Optional[str] = "system",
        language: Optional[str] = "en",
        notifications: Optional[bool] = True,
        settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get a user preference by user ID, or create it if it doesn't exist.
        
        Args:
            user_id: The Clerk user ID
            theme: Optional theme preference (default: "system")
            language: Optional language preference (default: "en")
            notifications: Optional notifications preference (default: True)
            settings: Optional additional settings
            
        Returns:
            The user preference as a dictionary
        """
        # Try to get the user preference first
        user_preference = UserPreferenceRepository.get_user_preference(user_id)
        
        # If not found, create a new one
        if not user_preference:
            user_preference = UserPreferenceRepository.create_user_preference(
                user_id=user_id,
                theme=theme,
                language=language,
                notifications=notifications,
                settings=settings
            )
        
        # Convert to dictionary
        return user_preference_to_dict(user_preference)
