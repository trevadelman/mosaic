"""
User Repository for MOSAIC

This module provides a repository class for user-related database operations.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

from sqlalchemy.orm import Session

from .models import User
from .database import get_db_session

# Configure logging
logger = logging.getLogger("mosaic.database.user_repository")

class UserRepository:
    """
    Repository for user-related database operations.
    """
    
    def __init__(self, db: Session):
        """
        Initialize the repository with a database session.
        
        Args:
            db: The database session
        """
        self.db = db
    
    def create_user(
        self,
        user_id: str,
        email: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> User:
        """
        Create a new user.
        
        Args:
            user_id: The Clerk user ID
            email: Optional email address
            first_name: Optional first name
            last_name: Optional last name
            metadata: Optional metadata
            
        Returns:
            The created user
        """
        user = User(
            id=user_id,
            email=email,
            first_name=first_name,
            last_name=last_name,
            user_metadata=metadata or {}
        )
        self.db.add(user)
        self.db.commit()
        logger.info(f"Created user {user_id}")
        
        return user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """
        Get a user by ID.
        
        Args:
            user_id: The Clerk user ID
            
        Returns:
            The user, or None if not found
        """
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email.
        
        Args:
            email: The email address
            
        Returns:
            The user, or None if not found
        """
        return self.db.query(User).filter(User.email == email).first()
    
    def get_all_users(self) -> List[User]:
        """
        Get all users.
        
        Returns:
            A list of users
        """
        return self.db.query(User).all()
    
    def update_user(
        self,
        user_id: str,
        email: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[User]:
        """
        Update a user.
        
        Args:
            user_id: The Clerk user ID
            email: Optional new email address
            first_name: Optional new first name
            last_name: Optional new last name
            metadata: Optional new metadata
            
        Returns:
            The updated user, or None if not found
        """
        user = self.get_user(user_id)
        
        if user:
            if email is not None:
                user.email = email
            if first_name is not None:
                user.first_name = first_name
            if last_name is not None:
                user.last_name = last_name
            if metadata is not None:
                user.user_metadata = metadata
            
            user.updated_at = datetime.utcnow()
            self.db.commit()
            logger.info(f"Updated user {user_id}")
            
            return user
        
        return None
    
    def create_or_update_user(
        self,
        user_id: str,
        email: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> User:
        """
        Create a user if it doesn't exist, or update it if it does.
        
        Args:
            user_id: The Clerk user ID
            email: Optional email address
            first_name: Optional first name
            last_name: Optional last name
            metadata: Optional metadata
            
        Returns:
            The created or updated user
        """
        user = self.get_user(user_id)
        
        if user:
            # Update the user
            if email is not None:
                user.email = email
            if first_name is not None:
                user.first_name = first_name
            if last_name is not None:
                user.last_name = last_name
            if metadata is not None:
                user.user_metadata = metadata
            
            user.updated_at = datetime.utcnow()
            self.db.commit()
            logger.info(f"Updated user {user_id}")
            
            return user
        else:
            # Create a new user
            return self.create_user(
                user_id=user_id,
                email=email,
                first_name=first_name,
                last_name=last_name,
                metadata=metadata
            )
    
    def delete_user(self, user_id: str) -> bool:
        """
        Delete a user.
        
        Args:
            user_id: The Clerk user ID
            
        Returns:
            True if the user was deleted, False otherwise
        """
        user = self.get_user(user_id)
        
        if user:
            self.db.delete(user)
            self.db.commit()
            logger.info(f"Deleted user {user_id}")
            return True
        
        return False
    
    def user_to_dict(self, user: User) -> Dict[str, Any]:
        """
        Convert a User model to a dictionary for API responses.
        
        Args:
            user: The User model
            
        Returns:
            A dictionary representation of the user
        """
        result = {
            "id": user.id,
            "createdAt": user.created_at.isoformat(),
            "updatedAt": user.updated_at.isoformat()
        }
        
        # Add optional fields
        if user.email:
            result["email"] = user.email
        
        if user.first_name:
            result["firstName"] = user.first_name
        
        if user.last_name:
            result["lastName"] = user.last_name
        
        if user.user_metadata:
            result["metadata"] = user.user_metadata
        
        return result
