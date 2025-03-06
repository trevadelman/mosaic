"""
User API Module for MOSAIC

This module provides API endpoints for user-related operations,
including user preferences.
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("mosaic.user_api")

# Import the user preference service
try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.database import UserPreferenceService
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.database import UserPreferenceService

# Models for user preferences
class UserPreferenceCreate(BaseModel):
    theme: Optional[str] = "system"
    language: Optional[str] = "en"
    notifications: Optional[bool] = True
    settings: Optional[Dict[str, Any]] = None

class UserPreferenceUpdate(BaseModel):
    theme: Optional[str] = None
    language: Optional[str] = None
    notifications: Optional[bool] = None
    settings: Optional[Dict[str, Any]] = None

class UserPreference(BaseModel):
    userId: str
    theme: str
    language: str
    notifications: bool
    settings: Dict[str, Any]
    createdAt: str
    updatedAt: str

# Create a router for user-related endpoints
router = APIRouter(prefix="/api/users", tags=["users"])

# Helper function to get the user ID from the request
# In a real application, this would be extracted from the authentication token
# For now, we'll use a simple function that returns a fixed user ID
def get_current_user_id() -> str:
    """
    Get the current user ID.
    
    In a real application, this would be extracted from the authentication token.
    For now, we'll use a simple function that returns a fixed user ID.
    
    Returns:
        The current user ID
    """
    # TODO: Replace with actual authentication logic
    return "user_123"

@router.get("/me/preferences", response_model=UserPreference)
async def get_user_preferences(user_id: str = Depends(get_current_user_id)):
    """
    Get the preferences for the current user.
    
    Args:
        user_id: The ID of the current user (injected by dependency)
        
    Returns:
        The user preferences
    """
    try:
        # Get or create the user preferences
        user_preference = UserPreferenceService.get_or_create_user_preference(user_id)
        
        if not user_preference:
            raise HTTPException(status_code=404, detail="User preferences not found")
        
        return user_preference
    except Exception as e:
        logger.error(f"Error getting user preferences: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting user preferences: {str(e)}")

@router.post("/me/preferences", response_model=UserPreference)
async def create_user_preferences(
    preferences: UserPreferenceCreate,
    user_id: str = Depends(get_current_user_id)
):
    """
    Create preferences for the current user.
    
    Args:
        preferences: The preferences to create
        user_id: The ID of the current user (injected by dependency)
        
    Returns:
        The created user preferences
    """
    try:
        # Create the user preferences
        user_preference = UserPreferenceService.create_user_preference(
            user_id=user_id,
            theme=preferences.theme,
            language=preferences.language,
            notifications=preferences.notifications,
            settings=preferences.settings
        )
        
        return user_preference
    except Exception as e:
        logger.error(f"Error creating user preferences: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating user preferences: {str(e)}")

@router.put("/me/preferences", response_model=UserPreference)
async def update_user_preferences(
    preferences: UserPreferenceUpdate,
    user_id: str = Depends(get_current_user_id)
):
    """
    Update preferences for the current user.
    
    Args:
        preferences: The preferences to update
        user_id: The ID of the current user (injected by dependency)
        
    Returns:
        The updated user preferences
    """
    try:
        # Update the user preferences
        user_preference = UserPreferenceService.update_user_preference(
            user_id=user_id,
            theme=preferences.theme,
            language=preferences.language,
            notifications=preferences.notifications,
            settings=preferences.settings
        )
        
        if not user_preference:
            raise HTTPException(status_code=404, detail="User preferences not found")
        
        return user_preference
    except Exception as e:
        logger.error(f"Error updating user preferences: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating user preferences: {str(e)}")

@router.delete("/me/preferences", response_model=dict)
async def delete_user_preferences(user_id: str = Depends(get_current_user_id)):
    """
    Delete preferences for the current user.
    
    Args:
        user_id: The ID of the current user (injected by dependency)
        
    Returns:
        A success message
    """
    try:
        # Delete the user preferences
        success = UserPreferenceService.delete_user_preference(user_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="User preferences not found")
        
        return {"message": "User preferences deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting user preferences: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting user preferences: {str(e)}")

# Function to get the user API router
def get_user_api_router():
    """Get the user API router."""
    return router
