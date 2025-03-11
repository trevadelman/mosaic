"""
File Operations API Module for MOSAIC

This module provides direct API endpoints for file operations, separate from agent-based operations.
It implements efficient file operations with proper security checks and error handling.
"""

import logging
import os
import re
import json
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query, Body, Depends
from pydantic import BaseModel, Field

# Configure logging
logger = logging.getLogger("mosaic.backend.app.file_operations_api")

# Create router
router = APIRouter(prefix="/api/files", tags=["file_operations"])

# Models for request and response
class FileContent(BaseModel):
    """Model for file content."""
    content: str = Field(..., description="The content of the file")

class FileResponse(BaseModel):
    """Model for file operation response."""
    success: bool = Field(..., description="Whether the operation was successful")
    path: str = Field(..., description="The path of the file")
    content: Optional[str] = Field(None, description="The content of the file (for read operations)")
    size: Optional[int] = Field(None, description="The size of the file in bytes")
    error: Optional[str] = Field(None, description="Error message if the operation failed")

class DirectoryResponse(BaseModel):
    """Model for directory listing response."""
    success: bool = Field(..., description="Whether the operation was successful")
    path: str = Field(..., description="The path of the directory")
    files: List[str] = Field(default_factory=list, description="List of files in the directory")
    directories: List[str] = Field(default_factory=list, description="List of subdirectories in the directory")
    error: Optional[str] = Field(None, description="Error message if the operation failed")

# Global variable to store the working directory
_WORKING_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "code-editor-working-dir"))

# Helper functions
def _is_path_allowed(path: str, operation: str) -> bool:
    """
    Check if a path is allowed for the specified operation.
    
    This function strictly enforces that all operations can only occur within
    the working directory.
    
    Args:
        path: The path to check
        operation: The operation to check ("read" or "write")
        
    Returns:
        True if the path is allowed, False otherwise
    """
    global _WORKING_DIRECTORY
    
    logger.debug(f"Checking if path is allowed: {path} for operation: {operation}")
    logger.debug(f"Working directory: {_WORKING_DIRECTORY}")
    
    # Handle relative paths that start with the working directory name
    if path.startswith("code-editor-working-dir"):
        # Extract the relative part and join with the actual working directory
        relative_path = path.replace("code-editor-working-dir", "")
        path = os.path.join(_WORKING_DIRECTORY, relative_path.lstrip("/"))
        logger.debug(f"Converted relative path to absolute path: {path}")
    
    # Get absolute path
    path = os.path.abspath(os.path.expanduser(path))
    logger.debug(f"Absolute path: {path}")
    
    # If working directory is not set, default to disallowing all operations
    if not _WORKING_DIRECTORY:
        logger.error("Working directory not set, disallowing all operations")
        return False
    
    # STRICT SAFETY CHECK: Only allow operations within the working directory
    if not path.startswith(_WORKING_DIRECTORY):
        logger.warning(f"Path not allowed: {path} is outside of working directory {_WORKING_DIRECTORY}")
        return False
    
    # Additional safety check for sensitive files
    sensitive_patterns = [
        r"\.env$",
        r"config\.json$",
        r"secrets\.json$",
        r"credentials\.json$",
        r"password",
        r"\.pem$",
        r"\.key$",
        r"\.crt$"
    ]
    
    for pattern in sensitive_patterns:
        if re.search(pattern, path):
            logger.warning(f"Path not allowed: {path} matches sensitive file pattern {pattern}")
            return False
    
    # Path is within working directory and not sensitive
    logger.debug(f"Path allowed: {path}")
    return True

def _get_normalized_path(path: str) -> str:
    """
    Normalize a path for consistent handling.
    
    Args:
        path: The path to normalize
        
    Returns:
        The normalized path
    """
    # Handle relative paths that start with the working directory name
    if path.startswith("code-editor-working-dir"):
        # Extract the relative part and join with the actual working directory
        relative_path = path.replace("code-editor-working-dir", "")
        path = os.path.join(_WORKING_DIRECTORY, relative_path.lstrip("/"))
    else:
        # If the path doesn't start with the working directory name, assume it's relative to the working directory
        path = os.path.join(_WORKING_DIRECTORY, path)
    
    # Get absolute path
    return os.path.abspath(os.path.expanduser(path))

# API endpoints
@router.get("/read", response_model=FileResponse)
async def read_file(path: str = Query(..., description="The path of the file to read")):
    """
    Read a file from the filesystem.
    
    Args:
        path: The path of the file to read
        
    Returns:
        A FileResponse object with the file content and metadata
    """
    logger.info(f"Reading file: {path}")
    
    # Initialize the result
    result = FileResponse(
        success=False,
        path=path,
        content="",
        size=0,
        error=None
    )
    
    # Check if the path is allowed
    if not _is_path_allowed(path, "read"):
        error_msg = f"Reading from path not allowed: {path}"
        logger.warning(error_msg)
        result.error = error_msg
        return result
    
    # Get normalized path
    file_path = _get_normalized_path(path)
    
    # Check if the file exists
    if not os.path.exists(file_path):
        error_msg = f"File does not exist: {file_path}"
        logger.warning(error_msg)
        result.error = error_msg
        return result
    
    # Check if the path is a file
    if not os.path.isfile(file_path):
        error_msg = f"Path is not a file: {file_path}"
        logger.warning(error_msg)
        result.error = error_msg
        return result
    
    # Get file size
    file_size = os.path.getsize(file_path)
    result.size = file_size
    
    # Check if the file is too large
    max_size = 10 * 1024 * 1024  # 10 MB
    if file_size > max_size:
        error_msg = f"File is too large: {file_size} bytes (max: {max_size} bytes)"
        logger.warning(error_msg)
        result.error = error_msg
        return result
    
    # Read the file
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            result.content = content
            result.success = True
            logger.info(f"Successfully read file: {file_path} ({file_size} bytes)")
    except Exception as e:
        error_msg = f"Error reading file: {str(e)}"
        logger.error(error_msg)
        result.error = error_msg
    
    return result

@router.post("/write", response_model=FileResponse)
async def write_file(path: str = Query(..., description="The path of the file to write to"), 
                    file_content: FileContent = Body(..., description="The content to write to the file")):
    """
    Write content to a file.
    
    Args:
        path: The path of the file to write to
        file_content: The content to write to the file
        
    Returns:
        A FileResponse object with the result of the operation
    """
    logger.info(f"Writing to file: {path}")
    
    # Initialize the result
    result = FileResponse(
        success=False,
        path=path,
        size=0,
        error=None
    )
    
    # Check if the path is allowed
    if not _is_path_allowed(path, "write"):
        error_msg = f"Writing to path not allowed: {path}"
        logger.warning(error_msg)
        result.error = error_msg
        return result
    
    # Get normalized path
    file_path = _get_normalized_path(path)
    
    # Create the directory if it doesn't exist
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Created directory: {directory}")
        except Exception as e:
            error_msg = f"Error creating directory: {str(e)}"
            logger.error(error_msg)
            result.error = error_msg
            return result
    
    # Write the file
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(file_content.content)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        result.size = file_size
        result.success = True
        logger.info(f"Successfully wrote to file: {file_path} ({file_size} bytes)")
    except Exception as e:
        error_msg = f"Error writing to file: {str(e)}"
        logger.error(error_msg)
        result.error = error_msg
    
    return result

@router.get("/list", response_model=DirectoryResponse)
async def list_files(path: str = Query(..., description="The path of the directory to list")):
    """
    List files in a directory.
    
    Args:
        path: The path of the directory to list
        
    Returns:
        A DirectoryResponse object with the directory contents
    """
    logger.info(f"Listing directory: {path}")
    
    # Initialize the result
    result = DirectoryResponse(
        success=False,
        path=path,
        files=[],
        directories=[],
        error=None
    )
    
    # Check if the path is allowed
    if not _is_path_allowed(path, "read"):
        error_msg = f"Listing directory not allowed: {path}"
        logger.warning(error_msg)
        result.error = error_msg
        return result
    
    # Get normalized path
    dir_path = _get_normalized_path(path)
    
    # Check if the directory exists
    if not os.path.exists(dir_path):
        error_msg = f"Directory does not exist: {dir_path}"
        logger.warning(error_msg)
        result.error = error_msg
        return result
    
    # Check if the path is a directory
    if not os.path.isdir(dir_path):
        error_msg = f"Path is not a directory: {dir_path}"
        logger.warning(error_msg)
        result.error = error_msg
        return result
    
    # List the directory
    try:
        for item in os.listdir(dir_path):
            item_path = os.path.join(dir_path, item)
            if os.path.isfile(item_path):
                result.files.append(item)
            elif os.path.isdir(item_path):
                result.directories.append(item)
        
        result.success = True
        logger.info(f"Successfully listed directory: {dir_path} ({len(result.files)} files, {len(result.directories)} directories)")
    except Exception as e:
        error_msg = f"Error listing directory: {str(e)}"
        logger.error(error_msg)
        result.error = error_msg
    
    return result

@router.post("/create", response_model=FileResponse)
async def create_file(path: str = Query(..., description="The path of the file to create"), 
                     file_content: FileContent = Body(..., description="The initial content of the file")):
    """
    Create a new file with the specified content.
    
    Args:
        path: The path of the file to create
        file_content: The initial content of the file
        
    Returns:
        A FileResponse object with the result of the operation
    """
    logger.info(f"Creating file: {path}")
    
    # Initialize the result
    result = FileResponse(
        success=False,
        path=path,
        size=0,
        error=None
    )
    
    # Check if the path is allowed
    if not _is_path_allowed(path, "write"):
        error_msg = f"Writing to path not allowed: {path}"
        logger.warning(error_msg)
        result.error = error_msg
        return result
    
    # Get normalized path
    file_path = _get_normalized_path(path)
    
    # Check if the file already exists
    if os.path.exists(file_path):
        error_msg = f"File already exists: {file_path}"
        logger.warning(error_msg)
        result.error = error_msg
        return result
    
    # Create the directory if it doesn't exist
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Created directory: {directory}")
        except Exception as e:
            error_msg = f"Error creating directory: {str(e)}"
            logger.error(error_msg)
            result.error = error_msg
            return result
    
    # Create the file
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(file_content.content)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        result.size = file_size
        result.success = True
        logger.info(f"Successfully created file: {file_path} ({file_size} bytes)")
    except Exception as e:
        error_msg = f"Error creating file: {str(e)}"
        logger.error(error_msg)
        result.error = error_msg
    
    return result

@router.delete("/delete", response_model=FileResponse)
async def delete_file(path: str = Query(..., description="The path of the file to delete")):
    """
    Delete a file from the filesystem.
    
    Args:
        path: The path of the file to delete
        
    Returns:
        A FileResponse object with the result of the operation
    """
    logger.info(f"Deleting file: {path}")
    
    # Initialize the result
    result = FileResponse(
        success=False,
        path=path,
        error=None
    )
    
    # Check if the path is allowed
    if not _is_path_allowed(path, "write"):
        error_msg = f"Deleting from path not allowed: {path}"
        logger.warning(error_msg)
        result.error = error_msg
        return result
    
    # Get normalized path
    file_path = _get_normalized_path(path)
    
    # Check if the file exists
    if not os.path.exists(file_path):
        error_msg = f"File does not exist: {file_path}"
        logger.warning(error_msg)
        result.error = error_msg
        return result
    
    # Check if the path is a file
    if not os.path.isfile(file_path):
        error_msg = f"Path is not a file: {file_path}"
        logger.warning(error_msg)
        result.error = error_msg
        return result
    
    # Delete the file
    try:
        os.remove(file_path)
        result.success = True
        logger.info(f"Successfully deleted file: {file_path}")
    except Exception as e:
        error_msg = f"Error deleting file: {str(e)}"
        logger.error(error_msg)
        result.error = error_msg
    
    return result

@router.delete("/delete-directory", response_model=FileResponse)
async def delete_directory(path: str = Query(..., description="The path of the directory to delete")):
    """
    Delete a directory and all its contents from the filesystem.
    
    Args:
        path: The path of the directory to delete
        
    Returns:
        A FileResponse object with the result of the operation
    """
    logger.info(f"Deleting directory: {path}")
    
    # Initialize the result
    result = FileResponse(
        success=False,
        path=path,
        error=None
    )
    
    # Check if the path is allowed
    if not _is_path_allowed(path, "write"):
        error_msg = f"Deleting from path not allowed: {path}"
        logger.warning(error_msg)
        result.error = error_msg
        return result
    
    # Get normalized path
    dir_path = _get_normalized_path(path)
    
    # Check if the directory exists
    if not os.path.exists(dir_path):
        error_msg = f"Directory does not exist: {dir_path}"
        logger.warning(error_msg)
        result.error = error_msg
        return result
    
    # Check if the path is a directory
    if not os.path.isdir(dir_path):
        error_msg = f"Path is not a directory: {dir_path}"
        logger.warning(error_msg)
        result.error = error_msg
        return result
    
    # Delete the directory and all its contents
    try:
        import shutil
        shutil.rmtree(dir_path)
        result.success = True
        logger.info(f"Successfully deleted directory: {dir_path}")
    except Exception as e:
        error_msg = f"Error deleting directory: {str(e)}"
        logger.error(error_msg)
        result.error = error_msg
    
    return result

# Function to set the working directory
def set_working_directory(directory: str):
    """
    Set the working directory for file operations.
    
    Args:
        directory: The directory to set as the working directory
    """
    global _WORKING_DIRECTORY
    _WORKING_DIRECTORY = os.path.abspath(os.path.expanduser(directory))
    logger.info(f"Set working directory to: {_WORKING_DIRECTORY}")
    
    # Create the directory if it doesn't exist
    if not os.path.exists(_WORKING_DIRECTORY):
        try:
            os.makedirs(_WORKING_DIRECTORY, exist_ok=True)
            logger.info(f"Created working directory: {_WORKING_DIRECTORY}")
        except Exception as e:
            logger.error(f"Error creating working directory: {str(e)}")
