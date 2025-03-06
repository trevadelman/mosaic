"""
User Data API for MOSAIC

This module provides API endpoints for user data export and deletion.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
import json
import os
import shutil
import tempfile
import zipfile
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

from sqlalchemy.orm import Session
from .database import get_db
from ..database.user_repository import UserRepository
from ..database.repository import ConversationRepository, MessageRepository, AttachmentRepository, AgentRepository, UserPreferenceRepository
from ..database.database import get_db_session
from ..database.models import Conversation, Message, MessageLog, Attachment

# Configure logging
logger = logging.getLogger("mosaic.app.user_data_api")

def get_user_data_api_router():
    """
    Get the user data API router.
    
    Returns:
        The user data API router
    """
    router = APIRouter(prefix="/api/user-data", tags=["user-data"])
    
    @router.get("/export")
    async def export_user_data(user_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
        """
        Export all data for a user.
        
        Args:
            user_id: The Clerk user ID
            background_tasks: Background tasks for cleanup
            db: The database session
            
        Returns:
            A ZIP file containing all user data
        """
        # Check if the user exists
        user_repo = UserRepository(db)
        user = user_repo.get_user(user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Create a temporary directory to store the data
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, f"user_data_{user_id}.zip")
        
        try:
            # Create a ZIP file
            with zipfile.ZipFile(zip_path, "w") as zip_file:
                # Export user data
                user_data = user_repo.user_to_dict(user)
                user_file = os.path.join(temp_dir, "user.json")
                with open(user_file, "w") as f:
                    json.dump(user_data, f, indent=2)
                zip_file.write(user_file, "user.json")
                
                # Export user preferences
                user_preference_repo = UserPreferenceRepository()
                user_preference = user_preference_repo.get_user_preference(user_id)
                if user_preference:
                    user_preference_data = user_preference_repo.to_dict(user_preference)
                    user_preference_file = os.path.join(temp_dir, "user_preferences.json")
                    with open(user_preference_file, "w") as f:
                        json.dump(user_preference_data, f, indent=2)
                    zip_file.write(user_preference_file, "user_preferences.json")
                
                # Export conversations
                conversation_repo = ConversationRepository()
                conversations = conversation_repo.get_conversations_for_user(user_id)
                conversations_data = [conversation_repo.to_dict(conv) for conv in conversations]
                conversations_file = os.path.join(temp_dir, "conversations.json")
                with open(conversations_file, "w") as f:
                    json.dump(conversations_data, f, indent=2)
                zip_file.write(conversations_file, "conversations.json")
                
                # Export messages
                message_repo = MessageRepository()
                messages = message_repo.get_messages_for_user(user_id)
                messages_data = [message_repo.to_dict(msg) for msg in messages]
                messages_file = os.path.join(temp_dir, "messages.json")
                with open(messages_file, "w") as f:
                    json.dump(messages_data, f, indent=2)
                zip_file.write(messages_file, "messages.json")
                
                # Export attachments
                attachment_repo = AttachmentRepository()
                attachments = attachment_repo.get_attachments_for_user(user_id)
                attachments_data = [attachment_repo.to_dict(att) for att in attachments]
                attachments_file = os.path.join(temp_dir, "attachments.json")
                with open(attachments_file, "w") as f:
                    json.dump(attachments_data, f, indent=2)
                zip_file.write(attachments_file, "attachments.json")
                
                # Export agents
                agent_repo = AgentRepository()
                agents = agent_repo.get_agents_for_user(user_id)
                agents_data = [agent_repo.to_dict(agent) for agent in agents]
                agents_file = os.path.join(temp_dir, "agents.json")
                with open(agents_file, "w") as f:
                    json.dump(agents_data, f, indent=2)
                zip_file.write(agents_file, "agents.json")
                
                # Add a README file
                readme = f"""
                # MOSAIC User Data Export
                
                This ZIP file contains all data associated with your MOSAIC account.
                
                ## Files
                
                - user.json: Your user profile information
                - user_preferences.json: Your user preferences
                - conversations.json: Your conversations
                - messages.json: Your messages
                - attachments.json: Your attachments
                - agents.json: Your custom agents
                
                ## Export Date
                
                {datetime.now().isoformat()}
                
                ## User ID
                
                {user_id}
                """
                
                readme_file = os.path.join(temp_dir, "README.md")
                with open(readme_file, "w") as f:
                    f.write(readme)
                zip_file.write(readme_file, "README.md")
            
            # Schedule cleanup of temporary directory
            background_tasks.add_task(shutil.rmtree, temp_dir)
            
            # Return the ZIP file
            return FileResponse(
                zip_path,
                media_type="application/zip",
                filename=f"mosaic_user_data_{user_id}.zip"
            )
        
        except Exception as e:
            # Clean up temporary directory
            shutil.rmtree(temp_dir)
            logger.error(f"Error exporting user data: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error exporting user data: {str(e)}")
    
    @router.delete("/delete")
    async def delete_user_data(user_id: str, db: Session = Depends(get_db)):
        """
        Delete all data for a user.
        
        Args:
            user_id: The Clerk user ID
            db: The database session
            
        Returns:
            A success message
        """
        # Check if the user exists
        user_repo = UserRepository(db)
        user = user_repo.get_user(user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        try:
            # Delete user preferences
            user_preference_repo = UserPreferenceRepository()
            user_preference_repo.delete_user_preference(user_id)
            
            # Delete conversations and messages
            conversation_repo = ConversationRepository()
            conversations = conversation_repo.get_conversations_for_user(user_id)
            for conversation in conversations:
                conversation_repo.delete_conversation(conversation.id)
            
            # Delete agents
            agent_repo = AgentRepository()
            agents = agent_repo.get_agents_for_user(user_id)
            for agent in agents:
                agent_repo.delete_agent(agent.id)
            
            # Delete the user
            user_repo.delete_user(user_id)
            
            return JSONResponse(content={"status": "success", "message": "User data deleted successfully"})
        
        except Exception as e:
            logger.error(f"Error deleting user data: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error deleting user data: {str(e)}")
    
    @router.delete("/clear-conversations")
    async def clear_user_conversations(user_id: str, db: Session = Depends(get_db)):
        """
        Clear all conversations for a user.
        
        Args:
            user_id: The Clerk user ID
            db: The database session
            
        Returns:
            A success message
        """
        # Create or update the user if it doesn't exist
        user_repo = UserRepository(db)
        user = user_repo.create_or_update_user(
            user_id=user_id,
            email=None,
            first_name=None,
            last_name=None,
            metadata=None
        )
        
        try:
            # Get all conversations for the user
            with get_db_session() as session:
                # Get count of conversations before deletion for logging
                conversations = session.query(Conversation).filter(
                    Conversation.user_id == user_id
                ).all()
                
                conversation_count = len(conversations)
                conversation_ids = [conv.id for conv in conversations]
                
                # Get count of messages before deletion for logging
                message_count = session.query(Message).filter(
                    Message.conversation_id.in_(conversation_ids)
                ).count() if conversation_ids else 0
                
                # Get all message IDs for the conversations
                message_ids = [
                    msg.id for msg in session.query(Message).filter(
                        Message.conversation_id.in_(conversation_ids)
                    ).all()
                ] if conversation_ids else []
                
                # Get count of logs and attachments before deletion for logging
                log_count = session.query(MessageLog).filter(
                    MessageLog.message_id.in_(message_ids)
                ).count() if message_ids else 0
                
                attachment_count = session.query(Attachment).filter(
                    Attachment.message_id.in_(message_ids)
                ).count() if message_ids else 0
                
                logger.info(f"Found {conversation_count} conversations, {message_count} messages, {log_count} logs, and {attachment_count} attachments for user {user_id}")
                
                # Delete all message logs (foreign key to messages)
                if message_ids:
                    session.query(MessageLog).filter(
                        MessageLog.message_id.in_(message_ids)
                    ).delete(synchronize_session=False)
                    logger.info(f"Deleted {log_count} message logs for user {user_id}")
                
                # Delete all attachments (foreign key to messages)
                if message_ids:
                    session.query(Attachment).filter(
                        Attachment.message_id.in_(message_ids)
                    ).delete(synchronize_session=False)
                    logger.info(f"Deleted {attachment_count} attachments for user {user_id}")
                
                # Delete all messages (foreign key to conversations)
                if conversation_ids:
                    session.query(Message).filter(
                        Message.conversation_id.in_(conversation_ids)
                    ).delete(synchronize_session=False)
                    logger.info(f"Deleted {message_count} messages for user {user_id}")
                
                # Delete all conversations
                if conversation_ids:
                    session.query(Conversation).filter(
                        Conversation.id.in_(conversation_ids)
                    ).delete(synchronize_session=False)
                    logger.info(f"Deleted {conversation_count} conversations for user {user_id}")
                
                # Commit the transaction
                session.commit()
            
            return JSONResponse(content={
                "status": "success", 
                "message": f"Cleared {conversation_count} conversations, {message_count} messages, {log_count} logs, and {attachment_count} attachments for user {user_id}"
            })
        
        except Exception as e:
            logger.error(f"Error clearing user conversations: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error clearing user conversations: {str(e)}")
    
    return router
