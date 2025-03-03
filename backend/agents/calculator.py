"""
Calculator Agent Module for MOSAIC

This module defines a calculator agent that can perform basic mathematical operations.
It serves as a simple example of a specialized agent in the MOSAIC system.
"""

import logging
import operator
from typing import List, Dict, Any, Optional
import re

from langchain_core.language_models import LanguageModelLike
from langchain_core.tools import BaseTool, tool

try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.agents.base import BaseAgent, agent_registry
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.agents.base import BaseAgent, agent_registry

# Configure logging
logger = logging.getLogger("mosaic.agents.calculator")

# Define the tools as standalone functions
@tool
def add_tool(a: float, b: float) -> float:
    """
    Add two numbers.
    
    Args:
        a: The first number
        b: The second number
        
    Returns:
        The sum of a and b
    """
    logger.info(f"Adding {a} + {b}")
    try:
        result = a + b
        logger.info(f"Addition result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error in add operation: {str(e)}")
        raise

@tool
def subtract_tool(a: float, b: float) -> float:
    """
    Subtract one number from another.
    
    Args:
        a: The number to subtract from
        b: The number to subtract
        
    Returns:
        The result of a - b
    """
    logger.info(f"Subtracting {a} - {b}")
    try:
        result = a - b
        logger.info(f"Subtraction result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error in subtract operation: {str(e)}")
        raise

@tool
def multiply_tool(a: float, b: float) -> float:
    """
    Multiply two numbers.
    
    Args:
        a: The first number
        b: The second number
        
    Returns:
        The product of a and b
    """
    logger.info(f"Multiplying {a} * {b}")
    try:
        result = a * b
        logger.info(f"Multiplication result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error in multiply operation: {str(e)}")
        raise

@tool
def divide_tool(a: float, b: float) -> float:
    """
    Divide one number by another.
    
    Args:
        a: The dividend
        b: The divisor
        
    Returns:
        The result of a / b
        
    Raises:
        ZeroDivisionError: If b is zero
    """
    logger.info(f"Dividing {a} / {b}")
    if b == 0:
        error_msg = "Cannot divide by zero"
        logger.error(error_msg)
        raise ZeroDivisionError(error_msg)
    try:
        result = a / b
        logger.info(f"Division result: {result}")
        return result
    except Exception as e:
        if not isinstance(e, ZeroDivisionError):
            logger.error(f"Error in divide operation: {str(e)}")
        raise

@tool
def parse_expression_tool(expression: str) -> float:
    """
    Parse and evaluate a simple mathematical expression.
    
    This tool can handle basic expressions with +, -, *, and / operators.
    It respects the standard order of operations (PEMDAS).
    
    Args:
        expression: The mathematical expression to evaluate
        
    Returns:
        The result of evaluating the expression
        
    Raises:
        ValueError: If the expression is invalid or contains unsupported operations
        ZeroDivisionError: If the expression involves division by zero
    """
    logger.info(f"Parsing expression: {expression}")
    
    # Remove whitespace and validate characters
    expression = re.sub(r'\s+', '', expression)
    if not re.match(r'^[\d\+\-\*\/\(\)\.]+$', expression):
        error_msg = f"Invalid expression: {expression}. Only numbers and basic operators (+, -, *, /) are supported."
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    try:
        # Use eval with a restricted namespace for safety
        # This is still not completely safe for production use
        namespace = {
            '__builtins__': None,
            'abs': abs,
            'float': float,
            'int': int,
            'pow': pow,
            'round': round
        }
        
        # Add the basic arithmetic operators
        namespace.update({
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.truediv
        })
        
        # Evaluate the expression
        result = eval(expression, namespace)
        logger.info(f"Expression result: {result}")
        return result
        
    except ZeroDivisionError:
        error_msg = f"Division by zero in expression: {expression}"
        logger.error(error_msg)
        raise
        
    except Exception as e:
        error_msg = f"Error evaluating expression '{expression}': {str(e)}"
        logger.error(error_msg)
        raise ValueError(error_msg)

class CalculatorAgent(BaseAgent):
    """
    Calculator agent that can perform basic mathematical operations.
    
    This agent provides tools for addition, subtraction, multiplication, and division,
    as well as a parser for handling mathematical expressions.
    """
    
    def __init__(
        self,
        name: str = "calculator",
        model: Optional[LanguageModelLike] = None,
        tools: List[BaseTool] = None,
        prompt: str = None,
        description: str = None,
    ):
        """
        Initialize a new calculator agent.
        
        Args:
            name: The name of the agent (default: "calculator")
            model: The language model to use for the agent
            tools: Optional list of additional tools
            prompt: Optional system prompt for the agent
            description: Optional description of the agent
        """
        # Create the basic calculator tools
        calculator_tools = [
            add_tool,
            subtract_tool,
            multiply_tool,
            divide_tool,
            parse_expression_tool
        ]
        
        # Combine with any additional tools
        all_tools = calculator_tools + (tools or [])
        
        super().__init__(
            name=name,
            model=model,
            tools=all_tools,
            prompt=prompt,
            description=description or "Calculator Agent for basic mathematical operations"
        )
        
        logger.info(f"Initialized calculator agent with {len(all_tools)} tools")
    
    def _get_default_prompt(self) -> str:
        """
        Get the default system prompt for the calculator agent.
        
        Returns:
            A string containing the default system prompt
        """
        return (
            "You are a calculator agent that can perform basic mathematical operations. "
            "You have tools for addition, subtraction, multiplication, and division, "
            "as well as a parser for handling mathematical expressions. "
            "ALWAYS use the appropriate tool to solve mathematical problems. "
            "NEVER calculate the result yourself - ALWAYS use one of the provided tools. "
            "For simple operations like addition, subtraction, multiplication, or division, "
            "use the specific tool for that operation. "
            "For expressions with multiple operations, use the parse_expression_tool. "
            "Always show your work and explain the steps you're taking. "
            "If you encounter an error (like division by zero), explain the issue clearly. "
            "For complex expressions, break them down into smaller operations and use the tools for each step."
        )

# Register the calculator agent with the registry
def register_calculator_agent(model: LanguageModelLike) -> CalculatorAgent:
    """
    Create and register a calculator agent.
    
    Args:
        model: The language model to use for the agent
        
    Returns:
        The created calculator agent
    """
    try:
        # Try importing with the full package path (for local development)
        from mosaic.backend.agents.base import agent_registry
    except ImportError:
        # Fall back to relative import (for Docker environment)
        from backend.agents.base import agent_registry
    
    calculator = CalculatorAgent(model=model)
    agent_registry.register(calculator)
    return calculator
