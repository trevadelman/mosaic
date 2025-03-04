"""
Safety Agent Module for MOSAIC

This module defines a safety agent that can validate and approve operations
based on predefined safety rules. It serves as a gatekeeper for potentially
risky operations in the MOSAIC system.
"""

import logging
import re
import json
from typing import List, Dict, Any, Optional, Union

from langchain_core.language_models import LanguageModelLike
from langchain_core.tools import BaseTool, tool

try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.agents.base import BaseAgent, agent_registry
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.agents.base import BaseAgent, agent_registry

# Configure logging
logger = logging.getLogger("mosaic.agents.safety")

# Define the tools as standalone functions
@tool
def validate_content_tool(content: str) -> Dict[str, Any]:
    """
    Validate content against safety rules.
    
    This tool checks if the provided content contains any potentially harmful
    elements such as offensive language, personal information, or dangerous instructions.
    
    Args:
        content: The content to validate
        
    Returns:
        A dictionary with validation results:
        {
            "is_safe": bool,
            "issues": List[str],
            "severity": str,
            "recommendation": str
        }
    """
    logger.info(f"Validating content (length: {len(content)})")
    
    # Initialize the result
    result = {
        "is_safe": True,
        "issues": [],
        "severity": "none",
        "recommendation": "Content appears safe"
    }
    
    # Check for potentially harmful patterns
    patterns = {
        "personal_info": {
            "regex": r'\b(?:\d[ -]*?){13,16}\b',  # Credit card numbers
            "message": "Potential credit card number detected",
            "severity": "high"
        },
        "email": {
            "regex": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "message": "Email address detected",
            "severity": "medium"
        },
        "phone": {
            "regex": r'\b(?:\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b',
            "message": "Phone number detected",
            "severity": "medium"
        },
        "ip_address": {
            "regex": r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
            "message": "IP address detected",
            "severity": "medium"
        },
        "dangerous_commands": {
            "regex": r'\b(?:rm\s+-rf|format|del\s+\/[a-z]|drop\s+database|DROP\s+TABLE)\b',
            "message": "Potentially dangerous command detected",
            "severity": "high"
        }
    }
    
    # Check each pattern
    for check_name, check_info in patterns.items():
        matches = re.findall(check_info["regex"], content)
        if matches:
            result["is_safe"] = False
            result["issues"].append(f"{check_info['message']}: {matches}")
            
            # Update severity if this issue has higher severity
            severity_levels = {"none": 0, "low": 1, "medium": 2, "high": 3}
            if severity_levels.get(check_info["severity"], 0) > severity_levels.get(result["severity"], 0):
                result["severity"] = check_info["severity"]
    
    # Generate recommendation based on issues
    if result["issues"]:
        result["recommendation"] = "Content contains potential safety issues and should be reviewed"
        logger.warning(f"Safety issues detected: {result['issues']}")
    else:
        logger.info("Content validation passed")
    
    return result

@tool
def approve_operation_tool(input_str: str) -> Dict[str, Any]:
    """
    Approve or reject an operation based on safety rules.
    
    This tool evaluates an operation and its context to determine if it should
    be allowed to proceed.
    
    Args:
        input_str: A string containing the operation and context in JSON format.
                  Format: "<operation> <json_context>"
                  Example: "file_write {"path": "/tmp/test.txt", "content": "Hello"}"
        
    Returns:
        A dictionary with approval results:
        {
            "approved": bool,
            "reason": str,
            "restrictions": List[str]
        }
    """
    # Parse the input string
    try:
        # Split the input string into operation and context
        parts = input_str.split(' ', 1)
        if len(parts) != 2:
            return {
                "approved": False,
                "reason": f"Invalid input format: {input_str}. Expected format: '<operation> <json_context>'",
                "restrictions": []
            }
        
        operation = parts[0]
        context_str = parts[1]
        
        # Parse the context JSON
        try:
            context = json.loads(context_str)
        except json.JSONDecodeError:
            return {
                "approved": False,
                "reason": f"Invalid context JSON: {context_str}",
                "restrictions": []
            }
        
        logger.info(f"Evaluating approval for operation: {operation}")
    except Exception as e:
        return {
            "approved": False,
            "reason": f"Error parsing input: {str(e)}",
            "restrictions": []
        }
    
    # Initialize the result
    result = {
        "approved": True,
        "reason": "Operation approved",
        "restrictions": []
    }
    
    # Define operation-specific checks
    operation_checks = {
        "file_write": lambda ctx: _check_file_write(ctx),
        "api_call": lambda ctx: _check_api_call(ctx),
        "execute_command": lambda ctx: _check_execute_command(ctx),
        "database_query": lambda ctx: _check_database_query(ctx)
    }
    
    # Run the appropriate check
    if operation in operation_checks:
        check_result = operation_checks[operation](context)
        result.update(check_result)
    else:
        result["approved"] = False
        result["reason"] = f"Unknown operation: {operation}"
        logger.warning(f"Unknown operation requested: {operation}")
    
    # Log the result
    if result["approved"]:
        logger.info(f"Operation '{operation}' approved")
    else:
        logger.warning(f"Operation '{operation}' rejected: {result['reason']}")
    
    return result

# Helper functions for approval checks
def _check_file_write(context: Dict[str, Any]) -> Dict[str, Any]:
    """Check if a file write operation should be approved."""
    result = {
        "approved": True,
        "reason": "File write operation approved",
        "restrictions": []
    }
    
    # Check if path is provided
    if "path" not in context:
        result["approved"] = False
        result["reason"] = "Missing required parameter: path"
        return result
    
    # Check for sensitive paths
    sensitive_paths = [
        "/etc/", "/var/", "/usr/", "~/.ssh/", 
        "~/.aws/", "~/.config/", "/root/", 
        ".env", "config.json", "secrets"
    ]
    
    path = context["path"]
    for sensitive_path in sensitive_paths:
        if sensitive_path in path:
            result["approved"] = False
            result["reason"] = f"Writing to sensitive path not allowed: {path}"
            return result
    
    # Check content if provided
    if "content" in context:
        content_check = validate_content_tool(context["content"])
        if not content_check["is_safe"]:
            result["approved"] = False
            result["reason"] = f"Content contains safety issues: {content_check['issues']}"
            return result
    
    return result

def _check_api_call(context: Dict[str, Any]) -> Dict[str, Any]:
    """Check if an API call should be approved."""
    result = {
        "approved": True,
        "reason": "API call approved",
        "restrictions": []
    }
    
    # Check if URL is provided
    if "url" not in context:
        result["approved"] = False
        result["reason"] = "Missing required parameter: url"
        return result
    
    # Check for allowed domains
    allowed_domains = [
        "api.openai.com",
        "api.github.com",
        "api.example.com",
        "localhost"
    ]
    
    url = context["url"]
    domain_allowed = False
    for allowed_domain in allowed_domains:
        if allowed_domain in url:
            domain_allowed = True
            break
    
    if not domain_allowed:
        result["approved"] = False
        result["reason"] = f"API calls to this domain are not allowed: {url}"
        return result
    
    # Add rate limiting restriction
    result["restrictions"].append("Rate limited to 10 requests per minute")
    
    return result

def _check_execute_command(context: Dict[str, Any]) -> Dict[str, Any]:
    """Check if a command execution should be approved."""
    result = {
        "approved": True,
        "reason": "Command execution approved",
        "restrictions": []
    }
    
    # Check if command is provided
    if "command" not in context:
        result["approved"] = False
        result["reason"] = "Missing required parameter: command"
        return result
    
    command = context["command"]
    
    # Check if this is a package installation command
    package_managers = [
        r"pip\s+install", r"npm\s+install", r"apt(-get)?\s+install",
        r"yum\s+install", r"brew\s+install", r"gem\s+install",
        r"cargo\s+install", r"go\s+get"
    ]
    
    for pattern in package_managers:
        if re.search(pattern, command):
            return _check_package_installation(command)
    
    # Check for dangerous commands
    dangerous_patterns = [
        r"rm\s+-rf", r"sudo", r"chmod\s+777", 
        r"format", r"mkfs", r"dd\s+if=", 
        r">\s+/dev/", r">\s+/etc/"
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, command):
            result["approved"] = False
            result["reason"] = f"Potentially dangerous command detected: {command}"
            return result
    
    return result

def _check_package_installation(command: str) -> Dict[str, Any]:
    """Check if a package installation command should be approved."""
    result = {
        "approved": True,
        "reason": "Package installation approved",
        "restrictions": []
    }
    
    # Extract package manager and packages
    package_manager = ""
    packages = []
    
    # Identify package manager
    if "pip install" in command:
        package_manager = "pip"
        # Extract packages, handling various formats
        parts = command.split("pip install")[1].strip().split()
        packages = [p for p in parts if not p.startswith("-")]
    elif "npm install" in command:
        package_manager = "npm"
        parts = command.split("npm install")[1].strip().split()
        packages = [p for p in parts if not p.startswith("-")]
    elif re.search(r"apt(-get)?\s+install", command):
        package_manager = "apt"
        match = re.search(r"apt(-get)?\s+install\s+(.*)", command)
        if match:
            parts = match.group(2).strip().split()
            packages = [p for p in parts if not p.startswith("-")]
    elif "brew install" in command:
        package_manager = "brew"
        parts = command.split("brew install")[1].strip().split()
        packages = [p for p in parts if not p.startswith("-")]
    else:
        # Other package managers
        for pm in ["yum", "gem", "cargo", "go"]:
            if f"{pm} install" in command or f"{pm} get" in command:
                package_manager = pm
                parts = command.split(f"{pm} install" if "install" in command else f"{pm} get")[1].strip().split()
                packages = [p for p in parts if not p.startswith("-")]
                break
    
    logger.info(f"Package installation detected: {package_manager} with packages {packages}")
    
    # Check for version pinning
    has_version_pinning = False
    for package in packages:
        if "==" in package or "@" in package or ":" in package:
            has_version_pinning = True
            break
    
    if not has_version_pinning and packages:
        result["restrictions"].append("Version pinning is recommended for security (e.g., package==1.0.0)")
    
    # Check for suspicious packages or flags
    suspicious_flags = ["-e", "--editable", "--pre", "--user", "--force-reinstall"]
    for flag in suspicious_flags:
        if flag in command:
            result["restrictions"].append(f"Using {flag} flag requires caution")
    
    # Check for direct URLs or git repositories
    if "git+" in command or "http://" in command or "https://" in command:
        result["restrictions"].append("Installing from URLs or git repositories requires verification")
    
    # Check for sudo usage
    if "sudo" in command:
        result["approved"] = False
        result["reason"] = "Using sudo with package installation is not allowed"
        result["restrictions"] = []  # Clear restrictions for sudo commands
        return result
    
    # Check for global installation without virtual environment
    if package_manager == "pip" and "--user" not in command and "venv" not in command and ".venv" not in command:
        result["restrictions"].append("Consider using a virtual environment or --user flag")
    
    # Add general restrictions
    result["restrictions"].append("Only install packages from trusted sources")
    result["restrictions"].append("Review package dependencies before installation")
    
    return result

def _check_database_query(context: Dict[str, Any]) -> Dict[str, Any]:
    """Check if a database query should be approved."""
    result = {
        "approved": True,
        "reason": "Database query approved",
        "restrictions": []
    }
    
    # Check if query is provided
    if "query" not in context:
        result["approved"] = False
        result["reason"] = "Missing required parameter: query"
        return result
    
    # Check for dangerous SQL operations
    dangerous_operations = [
        "DROP", "TRUNCATE", "DELETE FROM", "UPDATE", 
        "ALTER TABLE", "GRANT", "REVOKE"
    ]
    
    query = context["query"].upper()
    for operation in dangerous_operations:
        if operation in query:
            result["approved"] = False
            result["reason"] = f"Potentially dangerous SQL operation detected: {operation}"
            return result
    
    # Add query restrictions
    result["restrictions"].append("Query results limited to 1000 rows")
    result["restrictions"].append("Query timeout set to 30 seconds")
    
    return result

class SafetyAgent(BaseAgent):
    """
    Safety agent that can validate and approve operations.
    
    This agent provides tools for content validation and operation approval
    based on predefined safety rules.
    """
    
    def __init__(
        self,
        name: str = "safety",
        model: Optional[LanguageModelLike] = None,
        tools: List[BaseTool] = None,
        prompt: str = None,
        description: str = None,
    ):
        """
        Initialize a new safety agent.
        
        Args:
            name: The name of the agent (default: "safety")
            model: The language model to use for the agent
            tools: Optional list of additional tools
            prompt: Optional system prompt for the agent
            description: Optional description of the agent
        """
        # Create the safety tools
        safety_tools = [
            validate_content_tool,
            approve_operation_tool
        ]
        
        # Combine with any additional tools
        all_tools = safety_tools + (tools or [])
        
        super().__init__(
            name=name,
            model=model,
            tools=all_tools,
            prompt=prompt,
            description=description or "Safety Agent for validating and approving operations"
        )
        
        logger.info(f"Initialized safety agent with {len(all_tools)} tools")
    
    def _get_default_prompt(self) -> str:
        """
        Get the default system prompt for the safety agent.
        
        Returns:
            A string containing the default system prompt
        """
        return (
            "You are a safety agent responsible for validating content and approving operations. "
            "Your primary goal is to identify and prevent potentially harmful actions. "
            "\n\n"
            "You have tools for content validation and operation approval based on predefined safety rules. "
            "When asked to evaluate content or approve an operation, use the appropriate tool. "
            "\n\n"
            "For content validation, check for personal information, offensive language, and dangerous instructions. "
            "For operation approval, evaluate the operation and its context against safety rules. "
            "\n\n"
            "Always explain your reasoning and provide clear recommendations. "
            "If you reject an operation or flag content, suggest safer alternatives when possible. "
            "Remember that your role is critical for maintaining system security and user safety."
        )

# Register the safety agent with the registry
def register_safety_agent(model: LanguageModelLike) -> SafetyAgent:
    """
    Create and register a safety agent.
    
    Args:
        model: The language model to use for the agent
        
    Returns:
        The created safety agent
    """
    try:
        # Try importing with the full package path (for local development)
        from mosaic.backend.agents.base import agent_registry
    except ImportError:
        # Fall back to relative import (for Docker environment)
        from backend.agents.base import agent_registry
    
    safety = SafetyAgent(model=model)
    agent_registry.register(safety)
    return safety
