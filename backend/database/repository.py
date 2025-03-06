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

from .models import Conversation, Message, Attachment, MessageLog, Agent, Tool, Capability
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
        metadata: Optional[Dict[str, Any]] = None
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
                meta_data=metadata
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
    def get_all_agents() -> List[Agent]:
        """
        Get all agents.
        
        Returns:
            A list of agents
        """
        with get_db_session() as session:
            agents = session.query(Agent).filter(
                Agent.is_deleted == False
            ).all()
            
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
        metadata: Optional[Dict[str, Any]] = None
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
    def json_to_db(definition: Dict[str, Any]) -> Tuple[Agent, List[Tool], List[Capability]]:
        """
        Convert a JSON agent definition to database models.
        
        Args:
            definition: The agent definition
            
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
            metadata=metadata
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
        
        return definition


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
                "url": f"/api/attachments/{attachment.id}" if not attachment.data else None,
                "data": base64.b64encode(attachment.data).decode('ascii') if attachment.data and attachment.type.startswith('image/') else None
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
