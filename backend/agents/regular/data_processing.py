"""
Data Processing Agent Module for MOSAIC

This module defines a data processing agent that can extract and normalize information.
It serves as a specialized agent for data processing in the MOSAIC system.
"""

import logging
import json
import re
from typing import List, Dict, Any, Optional

from langchain_core.language_models import LanguageModelLike
from langchain_core.tools import BaseTool, tool

try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.agents.base import BaseAgent, agent_registry
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.agents.base import BaseAgent, agent_registry

# Configure logging
logger = logging.getLogger("mosaic.agents.data_processing")

# Define the tools as standalone functions
@tool
def extract_product_info_tool(content: str) -> str:
    """
    Extract product information from webpage content.
    
    Args:
        content: The webpage content to analyze
        
    Returns:
        A string containing structured product information
    """
    logger.info(f"Extracting product information from content")
    try:
        # Extract potential product information using regex patterns
        logger.info(f"Applying regex patterns to extract product information...")
        
        # Price patterns
        price_patterns = [
            r'\$\d+(?:\.\d{2})?',  # $XX.XX
            r'USD\s*\d+(?:\.\d{2})?',  # USD XX.XX
            r'Price:?\s*\$?\d+(?:\.\d{2})?',  # Price: $XX.XX
            r'Cost:?\s*\$?\d+(?:\.\d{2})?',  # Cost: $XX.XX
        ]
        
        # Product name patterns
        name_patterns = [
            r'Product(?:\s+Name)?:?\s*([A-Za-z0-9][-A-Za-z0-9\s]+)',
            r'Name:?\s*([A-Za-z0-9][-A-Za-z0-9\s]+)',
            r'Title:?\s*([A-Za-z0-9][-A-Za-z0-9\s]+)',
        ]
        
        # Feature patterns
        feature_patterns = [
            r'Features?:?\s*(.*?)(?:\n|$)',
            r'Specifications?:?\s*(.*?)(?:\n|$)',
            r'Details?:?\s*(.*?)(?:\n|$)',
        ]
        
        # Extract information
        prices = []
        for pattern in price_patterns:
            matches = re.findall(pattern, content)
            prices.extend(matches)
        
        names = []
        for pattern in name_patterns:
            matches = re.findall(pattern, content)
            names.extend(matches)
        
        features = []
        for pattern in feature_patterns:
            matches = re.findall(pattern, content)
            features.extend(matches)
        
        # Log extraction results
        logger.info(f"Extracted {len(names)} potential product names")
        logger.info(f"Extracted {len(prices)} potential prices")
        logger.info(f"Extracted {len(features)} potential features/specifications")
        
        # Format the results
        result = "Extracted Product Information:\n\n"
        
        if names:
            result += "Potential Product Names:\n"
            for i, name in enumerate(names[:5], 1):  # Limit to top 5
                result += f"{i}. {name.strip()}\n"
            result += "\n"
        
        if prices:
            result += "Potential Prices:\n"
            for i, price in enumerate(prices[:5], 1):  # Limit to top 5
                result += f"{i}. {price.strip()}\n"
            result += "\n"
        
        if features:
            result += "Potential Features/Specifications:\n"
            for i, feature in enumerate(features[:10], 1):  # Limit to top 10
                result += f"{i}. {feature.strip()}\n"
            result += "\n"
        
        if not (names or prices or features):
            logger.warning(f"No product information could be extracted from the content")
            result += "No clear product information could be extracted from the content.\n"
            result += "The content may not contain product details or may be in a format that's difficult to parse.\n"
        
        return result
    
    except Exception as e:
        logger.error(f"Error extracting product information: {str(e)}")
        error_report = {
            "task": "Extract Product Info",
            "status": "Failed",
            "error": str(e),
            "error_type": type(e).__name__
        }
        return f"Error extracting product information: {json.dumps(error_report, indent=2)}"

@tool
def clean_and_normalize_data_tool(data: str) -> str:
    """
    Clean and normalize extracted data.
    
    Args:
        data: The data to clean and normalize
        
    Returns:
        A string containing cleaned and normalized data
    """
    logger.info(f"Cleaning and normalizing data")
    try:
        # Remove extra whitespace
        logger.info(f"Removing extra whitespace...")
        cleaned_data = re.sub(r'\s+', ' ', data).strip()
        
        # Normalize price formats
        logger.info(f"Normalizing price formats...")
        cleaned_data = re.sub(r'USD\s*(\d+)', r'$\1', cleaned_data)
        cleaned_data = re.sub(r'(\d+)\s*USD', r'$\1', cleaned_data)
        
        # Normalize product names (capitalize properly)
        logger.info(f"Normalizing product names...")
        def capitalize_match(match):
            return ' '.join(word.capitalize() for word in match.group(0).split())
        
        cleaned_data = re.sub(r'Product\s+Name:?\s*([A-Za-z0-9][-A-Za-z0-9\s]+)', 
                             lambda m: f"Product Name: {capitalize_match(m)}", 
                             cleaned_data)
        
        logger.info(f"Data cleaning and normalization completed")
        return f"Cleaned and Normalized Data:\n\n{cleaned_data}"
    
    except Exception as e:
        logger.error(f"Error cleaning and normalizing data: {str(e)}")
        error_report = {
            "task": "Clean and Normalize Data",
            "status": "Failed",
            "error": str(e),
            "error_type": type(e).__name__
        }
        return f"Error cleaning and normalizing data: {json.dumps(error_report, indent=2)}"

class DataProcessingAgent(BaseAgent):
    """
    Data processing agent that can extract and normalize information.
    
    This agent provides tools for extracting structured information from text
    and normalizing data formats.
    """
    
    def __init__(
        self,
        name: str = "data_processing",
        model: Optional[LanguageModelLike] = None,
        tools: List[BaseTool] = None,
        prompt: str = None,
        description: str = None,
        type: str = "Specialized",
        capabilities: List[str] = None,
        icon: str = "📊",
    ):
        """
        Initialize a new data processing agent.
        
        Args:
            name: The name of the agent (default: "data_processing")
            model: The language model to use for the agent
            tools: Optional list of additional tools
            prompt: Optional system prompt for the agent
            description: Optional description of the agent
            type: The type of agent (default: "Specialized")
            capabilities: List of agent capabilities
            icon: Emoji icon for the agent (default: "📊")
        """
        # Create the data processing tools
        data_processing_tools = [
            extract_product_info_tool,
            clean_and_normalize_data_tool
        ]
        
        # Combine with any additional tools
        all_tools = data_processing_tools + (tools or [])
        
        # Default capabilities if none provided
        if capabilities is None:
            capabilities = ["Data Extraction", "Data Normalization"]
        
        super().__init__(
            name=name,
            model=model,
            tools=all_tools,
            prompt=prompt,
            description=description or "Data Processing Agent for extracting and normalizing information",
            type=type,
            capabilities=capabilities,
            icon=icon
        )
        
        logger.debug(f"Initialized data processing agent with {len(all_tools)} tools")
    
    def _get_default_prompt(self) -> str:
        """
        Get the default system prompt for the data processing agent.
        
        Returns:
            A string containing the default system prompt
        """
        return (
            "You are a data processing specialist that can extract and normalize information. "
            "Your job is to process raw webpage content to extract structured information about products. "
            "\n\n"
            "You have tools for data processing: "
            "- Use extract_product_info_tool to identify product details from text. "
            "- Use clean_and_normalize_data_tool to format and standardize data. "
            "\n\n"
            "Always work with the actual data provided to you. "
            "If you cannot extract meaningful information, clearly state that and explain why. "
            "Never make up information or hallucinate details. "
            "Always provide clear explanations of your data processing steps."
        )

# Register the data processing agent with the registry
def register_data_processing_agent(model: LanguageModelLike) -> DataProcessingAgent:
    """
    Create and register a data processing agent.
    
    Args:
        model: The language model to use for the agent
        
    Returns:
        The created data processing agent
    """
    try:
        # Try importing with the full package path (for local development)
        from mosaic.backend.agents.base import agent_registry
    except ImportError:
        # Fall back to relative import (for Docker environment)
        from backend.agents.base import agent_registry
    
    data_processing = DataProcessingAgent(model=model)
    agent_registry.register(data_processing)
    return data_processing
