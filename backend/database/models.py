"""
Database Models for MOSAIC

This module defines the SQLAlchemy models for the MOSAIC database.
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, LargeBinary, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class Conversation(Base):
    """
    Model for a conversation with an agent.
    
    A conversation is a collection of messages between a user and an agent.
    """
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True)
    agent_id = Column(String(50), nullable=False, index=True)
    title = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, agent_id='{self.agent_id}', title='{self.title}')>"


class Message(Base):
    """
    Model for a message in a conversation.
    
    A message can be from a user or an agent, and can contain text content
    and references to attachments.
    """
    __tablename__ = "messages"
    
    id = Column(String(36), primary_key=True)  # UUID as string
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    timestamp = Column(Integer, nullable=False)  # Unix timestamp in milliseconds
    status = Column(String(20), nullable=True)  # "sent", "error", etc.
    error = Column(Text, nullable=True)
    client_message_id = Column(String(36), nullable=True)  # For client-side message tracking
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    attachments = relationship("Attachment", back_populates="message", cascade="all, delete-orphan")
    logs = relationship("MessageLog", back_populates="message", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Message(id='{self.id}', role='{self.role}', conversation_id={self.conversation_id})>"


class Attachment(Base):
    """
    Model for an attachment to a message.
    
    An attachment can be an image, file, or other binary data.
    """
    __tablename__ = "attachments"
    
    id = Column(Integer, primary_key=True)
    message_id = Column(String(36), ForeignKey("messages.id"), nullable=False)
    type = Column(String(50), nullable=False)  # "image", "file", etc.
    filename = Column(String(255), nullable=True)
    content_type = Column(String(100), nullable=True)  # MIME type
    size = Column(Integer, nullable=True)  # Size in bytes
    storage_path = Column(String(255), nullable=True)  # Path to file on disk
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # For small attachments, store directly in the database
    data = Column(LargeBinary, nullable=True)
    
    # Relationships
    message = relationship("Message", back_populates="attachments")
    
    def __repr__(self):
        return f"<Attachment(id={self.id}, type='{self.type}', filename='{self.filename}')>"


class MessageLog(Base):
    """
    Model for logs associated with a message.
    
    Logs are generated during message processing and can be used for debugging.
    """
    __tablename__ = "message_logs"
    
    id = Column(Integer, primary_key=True)
    message_id = Column(String(36), ForeignKey("messages.id"), nullable=False)
    log_entry = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    message = relationship("Message", back_populates="logs")
    
    def __repr__(self):
        return f"<MessageLog(id={self.id}, message_id='{self.message_id}')>"


class Agent(Base):
    """
    Model for an agent definition.
    
    An agent is a specialized AI assistant with specific capabilities and tools.
    """
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True, index=True)
    type = Column(String(20), nullable=False)  # "Utility", "Specialized", "Supervisor"
    description = Column(Text, nullable=False)
    icon = Column(String(10), nullable=True)  # Emoji icon
    system_prompt = Column(Text, nullable=False)
    meta_data = Column(JSON, nullable=True)  # version, author, created, updated, tags
    is_deleted = Column(Boolean, default=False)  # Soft delete
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    tools = relationship("Tool", back_populates="agent", cascade="all, delete-orphan")
    capabilities = relationship("Capability", back_populates="agent", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Agent(id={self.id}, name='{self.name}', type='{self.type}')>"


class Tool(Base):
    """
    Model for a tool available to an agent.
    
    A tool is a function that an agent can use to perform a specific task.
    """
    __tablename__ = "tools"
    
    id = Column(Integer, primary_key=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    name = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    parameters = Column(JSON, nullable=False)  # Array of parameter objects
    returns = Column(JSON, nullable=False)  # Type and description
    implementation_code = Column(Text, nullable=False)
    dependencies = Column(JSON, nullable=True)  # Array of package names
    is_deleted = Column(Boolean, default=False)  # Soft delete
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    agent = relationship("Agent", back_populates="tools")
    
    def __repr__(self):
        return f"<Tool(id={self.id}, name='{self.name}', agent_id={self.agent_id})>"


class Capability(Base):
    """
    Model for a capability of an agent.
    
    A capability is a high-level description of what an agent can do.
    """
    __tablename__ = "capabilities"
    
    id = Column(Integer, primary_key=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    name = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    is_deleted = Column(Boolean, default=False)  # Soft delete
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    agent = relationship("Agent", back_populates="capabilities")
    
    def __repr__(self):
        return f"<Capability(id={self.id}, name='{self.name}', agent_id={self.agent_id})>"
