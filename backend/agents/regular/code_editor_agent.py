"""
Code Editor Agent Module for MOSAIC

This module defines a code editor agent that can generate and modify code based on user prompts.
It integrates with the direct file operations API for efficient file handling.
"""

import logging
import os
import json
from typing import List, Dict, Any, Optional, Union
from pathlib import Path

from langchain_core.language_models import LanguageModelLike
from langchain_core.tools import BaseTool, tool

try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.agents.base import BaseAgent, agent_registry
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.agents.base import BaseAgent, agent_registry

# Configure logging
logger = logging.getLogger("mosaic.agents.code_editor_agent")

@tool
def generate_code_tool(prompt: str) -> str:
    """
    Generate code based on a user prompt.
    
    This tool generates code based on a user's description or requirements.
    
    Args:
        prompt: The user's description of the code they want to generate
        
    Returns:
        The generated code as a string
    """
    logger.info(f"Generating code based on prompt: {prompt}")
    
    # Note: The actual code generation is handled by the LLM through the agent
    # This tool is mainly for documentation and logging purposes
    
    # Return an empty string to let the LLM generate the code
    # This prevents the recursion limit error
    return ""

@tool
def explain_code_tool(code: str) -> str:
    """
    Explain the provided code.
    
    This tool analyzes and explains the provided code in natural language.
    
    Args:
        code: The code to explain
        
    Returns:
        A natural language explanation of the code
    """
    logger.info(f"Explaining code: {code[:100]}...")
    
    # Note: The actual code explanation is handled by the LLM through the agent
    # This tool is mainly for documentation and logging purposes
    
    return "I'll analyze and explain this code for you."

@tool
def improve_code_tool(code: str, requirements: str) -> str:
    """
    Improve or modify the provided code based on requirements.
    
    This tool analyzes the provided code and suggests improvements or modifications
    based on the specified requirements.
    
    Args:
        code: The code to improve or modify
        requirements: The requirements for the improvements or modifications
        
    Returns:
        The improved or modified code
    """
    logger.info(f"Improving code based on requirements: {requirements}")
    
    # Note: The actual code improvement is handled by the LLM through the agent
    # This tool is mainly for documentation and logging purposes
    
    return "I'll improve this code based on your requirements."

class CodeEditorAgent(BaseAgent):
    """
    Code editor agent that can generate and modify code based on user prompts.
    
    This agent provides tools for generating code, explaining code, and improving code.
    It integrates with the direct file operations API for efficient file handling.
    """
    
    def __init__(
        self,
        name: str = "code_editor_agent",
        model: Optional[LanguageModelLike] = None,
        tools: List[BaseTool] = None,
        prompt: str = None,
        description: str = None,
        type: str = "Utility",
        capabilities: List[str] = None,
        icon: str = "💻"
    ):
        """
        Initialize a new code editor agent.
        
        Args:
            name: The name of the agent (default: "code_editor_agent")
            model: The language model to use for the agent
            tools: Optional list of additional tools
            prompt: Optional system prompt for the agent
            description: Optional description of the agent
            type: The type of agent (default: "Utility")
            capabilities: Optional list of capabilities
            icon: The icon to display for the agent (default: "💻")
        """
        # Create the code editor tools
        code_editor_tools = [
            generate_code_tool,
            explain_code_tool,
            improve_code_tool
        ]
        
        # Combine with any additional tools
        all_tools = code_editor_tools + (tools or [])
        
        # Default capabilities if none provided
        if capabilities is None:
            capabilities = [
                "Code Generation",
                "Code Explanation",
                "Code Improvement"
            ]
        
        super().__init__(
            name=name,
            model=model,
            tools=all_tools,
            prompt=prompt,
            description=description or "Code Editor Agent for generating and modifying code",
            type=type,
            capabilities=capabilities,
            icon=icon
        )
        
        # Set custom view properties
        self.has_custom_view = True
        self.custom_view = {
            "name": "CodeEditorView",
            "layout": "full",
            "capabilities": capabilities
        }
        
        logger.debug(f"Initialized code editor agent with {len(all_tools)} tools")
    
    def _get_default_prompt(self) -> str:
        """
        Get the default system prompt for the code editor agent.
        
        Returns:
            A string containing the default system prompt
        """
        return (
            "You are a code editor agent specialized in generating and modifying code based on user prompts. "
            "Your primary goal is to help users write, understand, and improve code. "
            "\n\n"
            "You have tools for generating code, explaining code, and improving code. "
            "When asked to generate code, provide clean, efficient, and well-documented code that meets the user's requirements. "
            "When asked to explain code, provide a clear and concise explanation of what the code does and how it works. "
            "When asked to improve code, analyze the code for potential issues and suggest improvements. "
            "\n\n"
            "Always follow these guidelines when generating or modifying code:"
            "\n"
            "1. Write clean, readable code with appropriate comments"
            "\n"
            "2. Follow best practices and conventions for the language"
            "\n"
            "3. Handle edge cases and potential errors"
            "\n"
            "4. Optimize for performance and maintainability"
            "\n"
            "5. Provide explanations for complex or non-obvious parts"
            "\n\n"
            "When generating code, make sure to understand the user's requirements fully. "
            "If the requirements are ambiguous or incomplete, make reasonable assumptions and explain them. "
            "Always provide complete, working solutions rather than code snippets when possible."
        )

def register_code_editor_agent(model: LanguageModelLike) -> CodeEditorAgent:
    """
    Create and register a code editor agent.
    
    Args:
        model: The language model to use for the agent
        
    Returns:
        The created code editor agent
    """
    try:
        # Try importing with the full package path (for local development)
        from mosaic.backend.agents.base import agent_registry
    except ImportError:
        # Fall back to relative import (for Docker environment)
        from backend.agents.base import agent_registry
    
    code_editor = CodeEditorAgent(model=model)
    agent_registry.register(code_editor)
    return code_editor
