"""
Writer Agent Module for MOSAIC

This module defines a writer agent that can perform file operations with security boundaries.
It serves as a secure way to read and write files in the MOSAIC system.
"""

import logging
import os
import re
import json
from typing import List, Dict, Any, Optional, Union
from pathlib import Path

from langchain_core.language_models import LanguageModelLike
from langchain_core.tools import BaseTool, tool

try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.agents.base import BaseAgent, agent_registry
    from mosaic.backend.agents.regular.safety import validate_content_tool
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.agents.base import BaseAgent, agent_registry
    from backend.agents.regular.safety import validate_content_tool

# Configure logging
logger = logging.getLogger("mosaic.agents.writer")

# Define the tools as standalone functions
@tool
def read_file_tool(file_path: str) -> Dict[str, Any]:
    """
    Read a file from the filesystem.
    
    This tool reads a file from the filesystem and returns its content.
    It includes security checks to prevent reading sensitive files.
    
    Args:
        file_path: The path to the file to read
        
    Returns:
        A dictionary with the file content and metadata:
        {
            "content": str,
            "exists": bool,
            "size": int,
            "error": str (if any)
        }
    """
    logger.info(f"Reading file: {file_path}")
    
    # Initialize the result
    result = {
        "content": "",
        "exists": False,
        "size": 0,
        "error": None
    }
    
    # Check if the path is allowed
    if not _is_path_allowed(file_path, "read"):
        error_msg = f"Reading from path not allowed: {file_path}"
        logger.warning(error_msg)
        result["error"] = error_msg
        return result
    
    # Check if the file exists
    file_path = os.path.expanduser(file_path)
    if not os.path.exists(file_path):
        error_msg = f"File does not exist: {file_path}"
        logger.warning(error_msg)
        result["error"] = error_msg
        return result
    
    # Check if the path is a file
    if not os.path.isfile(file_path):
        error_msg = f"Path is not a file: {file_path}"
        logger.warning(error_msg)
        result["error"] = error_msg
        return result
    
    # Get file size
    file_size = os.path.getsize(file_path)
    result["size"] = file_size
    result["exists"] = True
    
    # Check if the file is too large
    max_size = 10 * 1024 * 1024  # 10 MB
    if file_size > max_size:
        error_msg = f"File is too large: {file_size} bytes (max: {max_size} bytes)"
        logger.warning(error_msg)
        result["error"] = error_msg
        return result
    
    # Read the file
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            result["content"] = content
            logger.info(f"Successfully read file: {file_path} ({file_size} bytes)")
    except Exception as e:
        error_msg = f"Error reading file: {str(e)}"
        logger.error(error_msg)
        result["error"] = error_msg
    
    return result

@tool
def write_file_tool(input_str: str) -> Dict[str, Any]:
    """
    Write content to a file.
    
    This tool writes content to a file on the filesystem.
    It includes security checks to prevent writing to sensitive files.
    
    Args:
        input_str: A string containing the file path and content in JSON format.
                  Format: "<file_path> <json_content>"
                  Example: "/tmp/test.txt {"content": "Hello, world!"}"
        
    Returns:
        A dictionary with the result of the operation:
        {
            "success": bool,
            "path": str,
            "size": int,
            "error": str (if any)
        }
    """
    # Parse the input string
    try:
        # Split the input string into file path and content
        parts = input_str.split(' ', 1)
        if len(parts) != 2:
            return {
                "success": False,
                "path": "",
                "size": 0,
                "error": f"Invalid input format: {input_str}. Expected format: '<file_path> <json_content>'"
            }
        
        file_path = parts[0]
        content_json = parts[1]
        
        # Parse the content JSON
        try:
            content_obj = json.loads(content_json)
            if "content" not in content_obj:
                return {
                    "success": False,
                    "path": file_path,
                    "size": 0,
                    "error": f"Missing 'content' field in JSON: {content_json}"
                }
            content = content_obj["content"]
        except json.JSONDecodeError:
            return {
                "success": False,
                "path": file_path,
                "size": 0,
                "error": f"Invalid content JSON: {content_json}"
            }
        
        logger.info(f"Writing to file: {file_path}")
    except Exception as e:
        return {
            "success": False,
            "path": "",
            "size": 0,
            "error": f"Error parsing input: {str(e)}"
        }
    
    # Initialize the result
    result = {
        "success": False,
        "path": file_path,
        "size": 0,
        "error": None
    }
    
    # Check if the path is allowed
    if not _is_path_allowed(file_path, "write"):
        error_msg = f"Writing to path not allowed: {file_path}"
        logger.warning(error_msg)
        result["error"] = error_msg
        return result
    
    # Validate the content
    content_check = validate_content_tool(content)
    if not content_check["is_safe"]:
        error_msg = f"Content contains safety issues: {content_check['issues']}"
        logger.warning(error_msg)
        result["error"] = error_msg
        return result
    
    # Create the directory if it doesn't exist
    file_path = os.path.expanduser(file_path)
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Created directory: {directory}")
        except Exception as e:
            error_msg = f"Error creating directory: {str(e)}"
            logger.error(error_msg)
            result["error"] = error_msg
            return result
    
    # Write the file
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        result["size"] = file_size
        result["success"] = True
        logger.info(f"Successfully wrote to file: {file_path} ({file_size} bytes)")
    except Exception as e:
        error_msg = f"Error writing to file: {str(e)}"
        logger.error(error_msg)
        result["error"] = error_msg
    
    return result

@tool
def list_files_tool(directory_path: str) -> Dict[str, Any]:
    """
    List files in a directory.
    
    This tool lists files and directories in the specified directory.
    It includes security checks to prevent listing sensitive directories.
    
    Args:
        directory_path: The path to the directory to list
        
    Returns:
        A dictionary with the directory contents:
        {
            "files": List[str],
            "directories": List[str],
            "exists": bool,
            "error": str (if any)
        }
    """
    logger.info(f"Listing directory: {directory_path}")
    
    # Initialize the result
    result = {
        "files": [],
        "directories": [],
        "exists": False,
        "error": None
    }
    
    # Check if the path is allowed
    if not _is_path_allowed(directory_path, "read"):
        error_msg = f"Listing directory not allowed: {directory_path}"
        logger.warning(error_msg)
        result["error"] = error_msg
        return result
    
    # Check if the directory exists
    directory_path = os.path.expanduser(directory_path)
    if not os.path.exists(directory_path):
        error_msg = f"Directory does not exist: {directory_path}"
        logger.warning(error_msg)
        result["error"] = error_msg
        return result
    
    # Check if the path is a directory
    if not os.path.isdir(directory_path):
        error_msg = f"Path is not a directory: {directory_path}"
        logger.warning(error_msg)
        result["error"] = error_msg
        return result
    
    # List the directory
    try:
        result["exists"] = True
        for item in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item)
            if os.path.isfile(item_path):
                result["files"].append(item)
            elif os.path.isdir(item_path):
                result["directories"].append(item)
        
        logger.info(f"Successfully listed directory: {directory_path} ({len(result['files'])} files, {len(result['directories'])} directories)")
    except Exception as e:
        error_msg = f"Error listing directory: {str(e)}"
        logger.error(error_msg)
        result["error"] = error_msg
    
    return result

# Helper functions
def _is_path_allowed(path: str, operation: str) -> bool:
    """
    Check if a path is allowed for the specified operation.
    
    Args:
        path: The path to check
        operation: The operation to check ("read" or "write")
        
    Returns:
        True if the path is allowed, False otherwise
    """
    # Expand user directory
    path = os.path.expanduser(path)
    
    # Define allowed and disallowed paths
    allowed_paths = [
        os.path.expanduser("~/Documents"),
        os.path.expanduser("~/Downloads"),
        os.path.expanduser("~/Desktop"),
        "/tmp",
        "./",
        "../"
    ]
    
    disallowed_paths = [
        "/etc",
        "/var",
        "/usr",
        "/bin",
        "/sbin",
        "/boot",
        "/dev",
        "/lib",
        "/opt",
        "/proc",
        "/root",
        "/run",
        "/sys",
        os.path.expanduser("~/.ssh"),
        os.path.expanduser("~/.aws"),
        os.path.expanduser("~/.config")
    ]
    
    # Check for disallowed paths
    for disallowed in disallowed_paths:
        if path.startswith(disallowed):
            return False
    
    # Check for allowed paths
    for allowed in allowed_paths:
        if path.startswith(allowed):
            return True
    
    # Check for sensitive file patterns
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
            # Allow reading but not writing to sensitive files
            if operation == "write":
                return False
    
    # Default to disallowing the path
    return False

class WriterAgent(BaseAgent):
    """
    Writer agent that can perform file operations with security boundaries.
    
    This agent provides tools for reading and writing files with security checks
    to prevent access to sensitive files and directories.
    """
    
    def __init__(
        self,
        name: str = "writer",
        model: Optional[LanguageModelLike] = None,
        tools: List[BaseTool] = None,
        prompt: str = None,
        description: str = None,
    ):
        """
        Initialize a new writer agent.
        
        Args:
            name: The name of the agent (default: "writer")
            model: The language model to use for the agent
            tools: Optional list of additional tools
            prompt: Optional system prompt for the agent
            description: Optional description of the agent
        """
        # Create the writer tools
        writer_tools = [
            read_file_tool,
            write_file_tool,
            list_files_tool
        ]
        
        # Combine with any additional tools
        all_tools = writer_tools + (tools or [])
        
        super().__init__(
            name=name,
            model=model,
            tools=all_tools,
            prompt=prompt,
            description=description or "Writer Agent for secure file operations"
        )
        
        logger.info(f"Initialized writer agent with {len(all_tools)} tools")
    
    def _get_default_prompt(self) -> str:
        """
        Get the default system prompt for the writer agent.
        
        Returns:
            A string containing the default system prompt
        """
        return (
            "You are a writer agent responsible for secure file operations. "
            "Your primary goal is to read and write files while maintaining security boundaries. "
            "\n\n"
            "You have tools for reading files, writing files, and listing directories. "
            "When asked to perform a file operation, use the appropriate tool. "
            "\n\n"
            "For reading files, check if the file exists and is within allowed directories. "
            "For writing files, validate the content and ensure the path is allowed. "
            "For listing directories, check if the directory exists and is within allowed directories. "
            "\n\n"
            "Always explain your actions and provide clear error messages when operations fail. "
            "If a requested operation is not allowed, suggest safer alternatives when possible. "
            "Remember that your role is critical for maintaining system security while providing file access."
        )

# Register the writer agent with the registry
def register_writer_agent(model: LanguageModelLike) -> WriterAgent:
    """
    Create and register a writer agent.
    
    Args:
        model: The language model to use for the agent
        
    Returns:
        The created writer agent
    """
    try:
        # Try importing with the full package path (for local development)
        from mosaic.backend.agents.base import agent_registry
    except ImportError:
        # Fall back to relative import (for Docker environment)
        from backend.agents.base import agent_registry
    
    writer = WriterAgent(model=model)
    agent_registry.register(writer)
    return writer
