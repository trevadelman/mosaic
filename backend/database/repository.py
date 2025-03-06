"""
Database Repository for MOSAIC

This module provides repository classes for database operations.
These classes provide a clean API for the rest of the application
to interact with the database.
"""

import logging
import uuid
import base64
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import desc

from .models import Conversation, Message, Attachment, MessageLog, Agent, Tool, Capability, UserPreference
from .database import get_db_session

# Configure logging
logger = logging.getLogger("mosaic.database.repository")

class ConversationRepository:
    """
    Repository for conversation-related database operations.
    """
    
    @staticmethod
    def create_conversation(agent_id: str, title: Optional[str] = None, user_id: Optional[str] = None) -> Conversation:
        """
        Create a new conversation.
        
        Args:
            agent_id: The ID of the agent
            title: Optional title for the conversation
            user_id: Optional Clerk user ID
            
        Returns:
            The created conversation
        """
        with get_db_session() as session:
            conversation = Conversation(
                agent_id=agent_id,
                title=title or f"Conversation with {agent_id}",
                user_id=user_id
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
    def get_conversations_for_agent(agent_id: str, user_id: Optional[str] = None) -> List[Conversation]:
        """
        Get all conversations for an agent.
        
        Args:
            agent_id: The ID of the agent
            user_id: Optional Clerk user ID to filter by
            
        Returns:
            A list of conversations
        """
        with get_db_session() as session:
            query = session.query(Conversation).filter(
                Conversation.agent_id == agent_id
            )
            
            # Filter by user_id if provided
            if user_id:
                query = query.filter(Conversation.user_id == user_id)
                
            conversations = query.order_by(desc(Conversation.updated_at)).all()
            
            # Detach all conversations from the session by expunging them
            for conversation in conversations:
                session.expunge(conversation)
                
            return conversations
    
    @staticmethod
    def get_active_conversation_for_agent(agent_id: str, user_id: Optional[str] = None) -> Optional[Conversation]:
        """
        Get the active conversation for an agent.
        
        Args:
            agent_id: The ID of the agent
            user_id: Optional Clerk user ID to filter by
            
        Returns:
            The active conversation, or None if not found
        """
        with get_db_session() as session:
            query = session.query(Conversation).filter(
                Conversation.agent_id == agent_id,
                Conversation.is_active == True
            )
            
            # Filter by user_id if provided
            if user_id:
                query = query.filter(Conversation.user_id == user_id)
                
            conversation = query.order_by(desc(Conversation.updated_at)).first()
            
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
    def activate_conversation(conversation_id: int, agent_id: str, user_id: Optional[str] = None) -> Optional[Conversation]:
        """
        Activate a conversation and deactivate all other conversations for the same agent and user.
        
        Args:
            conversation_id: The ID of the conversation to activate
            agent_id: The ID of the agent
            user_id: Optional user ID to filter by
            
        Returns:
            The activated conversation, or None if not found
        """
        with get_db_session() as session:
            # First, deactivate all conversations for this agent and user
            query = session.query(Conversation).filter(
                Conversation.agent_id == agent_id,
                Conversation.is_active == True
            )
            
            # Filter by user_id if provided
            if user_id:
                query = query.filter(Conversation.user_id == user_id)
                
            for active_conversation in query.all():
                active_conversation.is_active = False
                logger.info(f"Deactivated conversation {active_conversation.id}")
            
            # Then, activate the specified conversation
            conversation = session.query(Conversation).filter(Conversation.id == conversation_id).first()
            if conversation:
                conversation.is_active = True
                session.commit()
                logger.info(f"Activated conversation {conversation_id}")
                
                # Create a new instance of the conversation to return
                # This avoids the "not bound to a Session" error
                activated_conversation = Conversation(
                    id=conversation.id,
                    agent_id=conversation.agent_id,
                    title=conversation.title,
                    is_active=True,
                    user_id=conversation.user_id,
                    created_at=conversation.created_at,
                    updated_at=conversation.updated_at
                )
                
                return activated_conversation
            else:
                # If the conversation wasn't found, still commit the deactivations
                session.commit()
                return None
    
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
    
    @staticmethod
    def get_conversations_for_user(user_id: str) -> List[Conversation]:
        """
        Get all conversations for a user.
        
        Args:
            user_id: The Clerk user ID
            
        Returns:
            A list of conversations
        """
        with get_db_session() as session:
            conversations = session.query(Conversation).filter(
                Conversation.user_id == user_id
            ).order_by(desc(Conversation.updated_at)).all()
            
            # Detach all conversations from the session by expunging them
            for conversation in conversations:
                session.expunge(conversation)
                
            return conversations


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
        message_id: Optional[str] = None,
        user_id: Optional[str] = None
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
            user_id: Optional Clerk user ID
            
        Returns:
            The created message
        """
        with get_db_session() as session:
            # If user_id is not provided, try to get it from the conversation
            if user_id is None:
                conversation = session.query(Conversation).filter(Conversation.id == conversation_id).first()
                if conversation:
                    user_id = conversation.user_id
            
            message = Message(
                id=message_id or str(uuid.uuid4()),
                conversation_id=conversation_id,
                role=role,
                content=content,
                timestamp=timestamp or int(datetime.now().timestamp() * 1000),
                status=status,
                error=error,
                client_message_id=client_message_id,
                user_id=user_id
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
    
    @staticmethod
    def get_messages_for_user(user_id: str) -> List[Message]:
        """
        Get all messages for a user.
        
        Args:
            user_id: The Clerk user ID
            
        Returns:
            A list of messages
        """
        with get_db_session() as session:
            messages = session.query(Message).filter(
                Message.user_id == user_id
            ).order_by(Message.timestamp).all()
            
            # Detach all messages from the session by expunging them
            for message in messages:
                session.expunge(message)
                
            return messages


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
        data: Optional[bytes] = None,
        user_id: Optional[str] = None
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
            user_id: Optional Clerk user ID
            
        Returns:
            The created attachment
        """
        with get_db_session() as session:
            # If user_id is not provided, try to get it from the message
            if user_id is None:
                message = session.query(Message).filter(Message.id == message_id).first()
                if message:
                    user_id = message.user_id
            
            attachment = Attachment(
                message_id=message_id,
                type=attachment_type,
                filename=filename,
                content_type=content_type,
                size=size,
                storage_path=storage_path,
                data=data,
                user_id=user_id
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
    
    @staticmethod
    def get_attachments_for_user(user_id: str) -> List[Attachment]:
        """
        Get all attachments for a user.
        
        Args:
            user_id: The Clerk user ID
            
        Returns:
            A list of attachments
        """
        with get_db_session() as session:
            attachments = session.query(Attachment).filter(
                Attachment.user_id == user_id
            ).all()
            
            # Detach all attachments from the session by expunging them
            for attachment in attachments:
                session.expunge(attachment)
                
            return attachments


# Agent Repository for database operations related to agents, tools, and capabilities

class AgentRepository:
    """
    Repository for agent-related database operations.
    """
    
    @staticmethod
    def create_agent(
        name: str,
        agent_type: str,
        description: str,
        system_prompt: str,
        icon: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> Agent:
        """
        Create a new agent.
        
        Args:
            name: The name of the agent
            agent_type: The type of agent ("Utility", "Specialized", "Supervisor")
            description: The description of the agent
            system_prompt: The system prompt for the agent
            icon: Optional emoji icon for the agent
            metadata: Optional metadata for the agent
            user_id: Optional Clerk user ID
            
        Returns:
            The created agent
        """
        with get_db_session() as session:
            agent = Agent(
                name=name,
                type=agent_type,
                description=description,
                system_prompt=system_prompt,
                icon=icon,
                meta_data=metadata,
                user_id=user_id
            )
            session.add(agent)
            session.commit()
            logger.info(f"Created agent {agent.id} with name {name}")
            
            # Detach the agent from the session by expunging it
            session.expunge(agent)
            
            return agent
    
    @staticmethod
    def get_agent(agent_id: int) -> Optional[Agent]:
        """
        Get an agent by ID.
        
        Args:
            agent_id: The ID of the agent
            
        Returns:
            The agent, or None if not found
        """
        with get_db_session() as session:
            agent = session.query(Agent).filter(
                Agent.id == agent_id,
                Agent.is_deleted == False
            ).first()
            
            # If we found an agent, detach it from the session by expunging it
            if agent:
                session.expunge(agent)
                
            return agent
    
    @staticmethod
    def get_agent_by_name(name: str) -> Optional[Agent]:
        """
        Get an agent by name.
        
        Args:
            name: The name of the agent
            
        Returns:
            The agent, or None if not found
        """
        with get_db_session() as session:
            agent = session.query(Agent).filter(
                Agent.name == name,
                Agent.is_deleted == False
            ).first()
            
            # If we found an agent, detach it from the session by expunging it
            if agent:
                session.expunge(agent)
                
            return agent
    
    @staticmethod
    def get_all_agents(user_id: Optional[str] = None) -> List[Agent]:
        """
        Get all agents.
        
        Args:
            user_id: Optional Clerk user ID to filter by
            
        Returns:
            A list of agents
        """
        with get_db_session() as session:
            query = session.query(Agent).filter(
                Agent.is_deleted == False
            )
            
            # Filter by user_id if provided, or get public agents (user_id is None)
            if user_id:
                # Get agents created by this user or public agents (user_id is None)
                query = query.filter((Agent.user_id == user_id) | (Agent.user_id == None))
            else:
                # Only get public agents
                query = query.filter(Agent.user_id == None)
                
            agents = query.all()
            
            # Detach all agents from the session by expunging them
            for agent in agents:
                session.expunge(agent)
                
            return agents
    
    @staticmethod
    def update_agent(
        agent_id: int,
        name: Optional[str] = None,
        agent_type: Optional[str] = None,
        description: Optional[str] = None,
        system_prompt: Optional[str] = None,
        icon: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> Optional[Agent]:
        """
        Update an agent.
        
        Args:
            agent_id: The ID of the agent
            name: Optional new name for the agent
            agent_type: Optional new type for the agent
            description: Optional new description for the agent
            system_prompt: Optional new system prompt for the agent
            icon: Optional new icon for the agent
            metadata: Optional new metadata for the agent
            user_id: Optional new Clerk user ID for the agent
            
        Returns:
            The updated agent, or None if not found
        """
        with get_db_session() as session:
            agent = session.query(Agent).filter(
                Agent.id == agent_id,
                Agent.is_deleted == False
            ).first()
            
            if agent:
                if name is not None:
                    agent.name = name
                if agent_type is not None:
                    agent.type = agent_type
                if description is not None:
                    agent.description = description
                if system_prompt is not None:
                    agent.system_prompt = system_prompt
                if icon is not None:
                    agent.icon = icon
                if metadata is not None:
                    agent.meta_data = metadata
                if user_id is not None:
                    agent.user_id = user_id
                
                session.commit()
                logger.info(f"Updated agent {agent_id}")
                
                # Detach the agent from the session by expunging it
                session.expunge(agent)
            
            return agent
    
    @staticmethod
    def delete_agent(agent_id: int, hard_delete: bool = False) -> bool:
        """
        Delete an agent.
        
        Args:
            agent_id: The ID of the agent
            hard_delete: Whether to hard delete the agent (default: False)
            
        Returns:
            True if the agent was deleted, False otherwise
        """
        with get_db_session() as session:
            agent = session.query(Agent).filter(Agent.id == agent_id).first()
            
            if agent:
                if hard_delete:
                    session.delete(agent)
                    logger.info(f"Hard deleted agent {agent_id}")
                else:
                    agent.is_deleted = True
                    logger.info(f"Soft deleted agent {agent_id}")
                
                session.commit()
                return True
            
            return False
    
    @staticmethod
    def create_tool(
        agent_id: int,
        name: str,
        description: str,
        parameters: List[Dict[str, Any]],
        returns: Dict[str, Any],
        implementation_code: str,
        dependencies: Optional[List[str]] = None
    ) -> Tool:
        """
        Create a new tool for an agent.
        
        Args:
            agent_id: The ID of the agent
            name: The name of the tool
            description: The description of the tool
            parameters: The parameters for the tool
            returns: The return type and description for the tool
            implementation_code: The implementation code for the tool
            dependencies: Optional list of dependencies for the tool
            
        Returns:
            The created tool
        """
        with get_db_session() as session:
            tool = Tool(
                agent_id=agent_id,
                name=name,
                description=description,
                parameters=parameters,
                returns=returns,
                implementation_code=implementation_code,
                dependencies=dependencies
            )
            session.add(tool)
            session.commit()
            logger.info(f"Created tool {tool.id} for agent {agent_id}")
            
            # Detach the tool from the session by expunging it
            session.expunge(tool)
            
            return tool
    
    @staticmethod
    def get_tools_for_agent(agent_id: int) -> List[Tool]:
        """
        Get all tools for an agent.
        
        Args:
            agent_id: The ID of the agent
            
        Returns:
            A list of tools
        """
        with get_db_session() as session:
            tools = session.query(Tool).filter(
                Tool.agent_id == agent_id,
                Tool.is_deleted == False
            ).all()
            
            # Detach all tools from the session by expunging them
            for tool in tools:
                session.expunge(tool)
                
            return tools
    
    @staticmethod
    def create_capability(
        agent_id: int,
        name: str,
        description: Optional[str] = None
    ) -> Capability:
        """
        Create a new capability for an agent.
        
        Args:
            agent_id: The ID of the agent
            name: The name of the capability
            description: Optional description of the capability
            
        Returns:
            The created capability
        """
        with get_db_session() as session:
            capability = Capability(
                agent_id=agent_id,
                name=name,
                description=description
            )
            session.add(capability)
            session.commit()
            logger.info(f"Created capability {capability.id} for agent {agent_id}")
            
            # Detach the capability from the session by expunging it
            session.expunge(capability)
            
            return capability
    
    @staticmethod
    def get_capabilities_for_agent(agent_id: int) -> List[Capability]:
        """
        Get all capabilities for an agent.
        
        Args:
            agent_id: The ID of the agent
            
        Returns:
            A list of capabilities
        """
        with get_db_session() as session:
            capabilities = session.query(Capability).filter(
                Capability.agent_id == agent_id,
                Capability.is_deleted == False
            ).all()
            
            # Detach all capabilities from the session by expunging them
            for capability in capabilities:
                session.expunge(capability)
                
            return capabilities
    
    @staticmethod
    def json_to_db(definition: Dict[str, Any], user_id: Optional[str] = None) -> Tuple[Agent, List[Tool], List[Capability]]:
        """
        Convert a JSON agent definition to database models.
        
        Args:
            definition: The agent definition
            user_id: Optional Clerk user ID
            
        Returns:
            A tuple containing the agent, tools, and capabilities
        """
        # Extract agent information
        agent_data = definition["agent"]
        name = agent_data["name"]
        agent_type = agent_data["type"]
        description = agent_data["description"]
        icon = agent_data.get("icon")
        system_prompt = agent_data["systemPrompt"]
        metadata = agent_data.get("metadata", {})
        
        # Create the agent
        agent = AgentRepository.create_agent(
            name=name,
            agent_type=agent_type,
            description=description,
            system_prompt=system_prompt,
            icon=icon,
            metadata=metadata,
            user_id=user_id
        )
        
        # Create tools
        tools = []
        for tool_data in agent_data["tools"]:
            tool = AgentRepository.create_tool(
                agent_id=agent.id,
                name=tool_data["name"],
                description=tool_data["description"],
                parameters=tool_data["parameters"],
                returns=tool_data["returns"],
                implementation_code=tool_data["implementation"]["code"],
                dependencies=tool_data["implementation"].get("dependencies")
            )
            tools.append(tool)
        
        # Create capabilities
        capabilities = []
        for capability_name in agent_data.get("capabilities", []):
            capability = AgentRepository.create_capability(
                agent_id=agent.id,
                name=capability_name
            )
            capabilities.append(capability)
        
        return agent, tools, capabilities
    
    @staticmethod
    def db_to_json(agent: Agent) -> Dict[str, Any]:
        """
        Convert database models to a JSON agent definition.
        
        Args:
            agent: The agent model
            
        Returns:
            The agent definition as a dictionary
        """
        # Get tools and capabilities
        tools = AgentRepository.get_tools_for_agent(agent.id)
        capabilities = AgentRepository.get_capabilities_for_agent(agent.id)
        
        # Build the agent definition
        definition = {
            "agent": {
                "name": agent.name,
                "type": agent.type,
                "description": agent.description,
                "systemPrompt": agent.system_prompt,
                "tools": [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.parameters,
                        "returns": tool.returns,
                        "implementation": {
                            "code": tool.implementation_code,
                            "dependencies": tool.dependencies
                        }
                    }
                    for tool in tools
                ],
                "capabilities": [capability.name for capability in capabilities]
            }
        }
        
        # Add optional fields
        if agent.icon:
            definition["agent"]["icon"] = agent.icon
        
        if agent.meta_data:
            definition["agent"]["metadata"] = agent.meta_data
            
        # Add user_id if available
        if agent.user_id:
            definition["agent"]["userId"] = agent.user_id
        
        return definition


class UserPreferenceRepository:
    """
    Repository for user preference-related database operations.
    """
    
    @staticmethod
    def create_user_preference(
        user_id: str,
        theme: Optional[str] = "system",
        language: Optional[str] = "en",
        notifications: Optional[bool] = True,
        settings: Optional[Dict[str, Any]] = None
    ) -> UserPreference:
        """
        Create a new user preference.
        
        Args:
            user_id: The Clerk user ID
            theme: Optional theme preference (default: "system")
            language: Optional language preference (default: "en")
            notifications: Optional notifications preference (default: True)
            settings: Optional additional settings
            
        Returns:
            The created user preference
        """
        with get_db_session() as session:
            user_preference = UserPreference(
                user_id=user_id,
                theme=theme,
                language=language,
                notifications=notifications,
                settings=settings or {}
            )
            session.add(user_preference)
            session.commit()
            logger.info(f"Created user preference for user {user_id}")
            
            # Detach the user preference from the session by expunging it
            session.expunge(user_preference)
            
            return user_preference
    
    @staticmethod
    def get_user_preference(user_id: str) -> Optional[UserPreference]:
        """
        Get a user preference by user ID.
        
        Args:
            user_id: The Clerk user ID
            
        Returns:
            The user preference, or None if not found
        """
        with get_db_session() as session:
            user_preference = session.query(UserPreference).filter(
                UserPreference.user_id == user_id
            ).first()
            
            # If we found a user preference, detach it from the session by expunging it
            if user_preference:
                session.expunge(user_preference)
                
            return user_preference
    
    @staticmethod
    def update_user_preference(
        user_id: str,
        theme: Optional[str] = None,
        language: Optional[str] = None,
        notifications: Optional[bool] = None,
        settings: Optional[Dict[str, Any]] = None
    ) -> Optional[UserPreference]:
        """
        Update a user preference.
        
        Args:
            user_id: The Clerk user ID
            theme: Optional new theme preference
            language: Optional new language preference
            notifications: Optional new notifications preference
            settings: Optional new additional settings
            
        Returns:
            The updated user preference, or None if not found
        """
        with get_db_session() as session:
            user_preference = session.query(UserPreference).filter(
                UserPreference.user_id == user_id
            ).first()
            
            if user_preference:
                if theme is not None:
                    user_preference.theme = theme
                if language is not None:
                    user_preference.language = language
                if notifications is not None:
                    user_preference.notifications = notifications
                if settings is not None:
                    user_preference.settings = settings
                
                user_preference.updated_at = datetime.utcnow()
                session.commit()
                logger.info(f"Updated user preference for user {user_id}")
                
                # Create a copy of the user preference before detaching it
                updated_preference = UserPreference(
                    id=user_preference.id,
                    user_id=user_preference.user_id,
                    theme=user_preference.theme,
                    language=user_preference.language,
                    notifications=user_preference.notifications,
                    settings=user_preference.settings,
                    created_at=user_preference.created_at,
                    updated_at=user_preference.updated_at
                )
                
                # Detach the user preference from the session by expunging it
                session.expunge(user_preference)
                
                return updated_preference
            
            return None
    
    @staticmethod
    def delete_user_preference(user_id: str) -> bool:
        """
        Delete a user preference.
        
        Args:
            user_id: The Clerk user ID
            
        Returns:
            True if the user preference was deleted, False otherwise
        """
        with get_db_session() as session:
            user_preference = session.query(UserPreference).filter(
                UserPreference.user_id == user_id
            ).first()
            
            if user_preference:
                session.delete(user_preference)
                session.commit()
                logger.info(f"Deleted user preference for user {user_id}")
                return True
            
            return False
    
    @staticmethod
    def get_or_create_user_preference(
        user_id: str,
        theme: Optional[str] = "system",
        language: Optional[str] = "en",
        notifications: Optional[bool] = True,
        settings: Optional[Dict[str, Any]] = None
    ) -> UserPreference:
        """
        Get a user preference by user ID, or create it if it doesn't exist.
        
        Args:
            user_id: The Clerk user ID
            theme: Optional theme preference (default: "system")
            language: Optional language preference (default: "en")
            notifications: Optional notifications preference (default: True)
            settings: Optional additional settings
            
        Returns:
            The user preference
        """
        user_preference = UserPreferenceRepository.get_user_preference(user_id)
        
        if user_preference:
            return user_preference
        
        return UserPreferenceRepository.create_user_preference(
            user_id=user_id,
            theme=theme,
            language=language,
            notifications=notifications,
            settings=settings
        )


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
    
    # Add user_id if available
    if message.user_id:
        result["userId"] = message.user_id
    
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
                "url": f"/api/attachments/{attachment.id}" if not attachment.data else None,
                "data": base64.b64encode(attachment.data).decode('ascii') if attachment.data and attachment.type.startswith('image/') else None
            }
            for attachment in attachments
        ]
    
    return result


def agent_to_dict(agent: Agent, include_tools: bool = False, include_capabilities: bool = False) -> Dict[str, Any]:
    """
    Convert an Agent model to a dictionary for API responses.
    
    Args:
        agent: The Agent model
        include_tools: Whether to include tools in the result
        include_capabilities: Whether to include capabilities in the result
        
    Returns:
        A dictionary representation of the agent
    """
    result = {
        "id": agent.id,
        "name": agent.name,
        "type": agent.type,
        "description": agent.description,
        "systemPrompt": agent.system_prompt,
        "createdAt": agent.created_at.isoformat(),
        "updatedAt": agent.updated_at.isoformat()
    }
    
    # Add optional fields
    if agent.icon:
        result["icon"] = agent.icon
    
    if agent.meta_data:
        result["metadata"] = agent.meta_data
    
    # Add user_id if available
    if agent.user_id:
        result["userId"] = agent.user_id
    
    # Add tools if requested
    if include_tools:
        tools = AgentRepository.get_tools_for_agent(agent.id)
        result["tools"] = [
            {
                "id": tool.id,
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
                "returns": tool.returns
            }
            for tool in tools
        ]
    
    # Add capabilities if requested
    if include_capabilities:
        capabilities = AgentRepository.get_capabilities_for_agent(agent.id)
        result["capabilities"] = [
            {
                "id": capability.id,
                "name": capability.name,
                "description": capability.description
            }
            for capability in capabilities
        ]
    
    return result


def user_preference_to_dict(user_preference: UserPreference) -> Dict[str, Any]:
    """
    Convert a UserPreference model to a dictionary for API responses.
    
    Args:
        user_preference: The UserPreference model
        
    Returns:
        A dictionary representation of the user preference
    """
    result = {
        "userId": user_preference.user_id,
        "theme": user_preference.theme,
        "language": user_preference.language,
        "notifications": user_preference.notifications,
        "settings": user_preference.settings,
        "createdAt": user_preference.created_at.isoformat(),
        "updatedAt": user_preference.updated_at.isoformat()
    }
    
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
    
    # Add user_id if available
    if conversation.user_id:
        result["userId"] = conversation.user_id
    
    if include_messages:
        messages = MessageRepository.get_messages_for_conversation(conversation.id)
        result["messages"] = [message_to_dict(message) for message in messages]
    
    return result
