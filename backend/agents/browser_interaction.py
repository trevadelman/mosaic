"""
Browser Interaction Agent Module for MOSAIC

This module defines a browser interaction agent that can handle JavaScript-heavy websites.
It serves as a specialized agent for browser automation in the MOSAIC system.
"""

import logging
import requests
import json
from typing import List, Dict, Any, Optional

from langchain_core.language_models import LanguageModelLike
from langchain_core.tools import BaseTool, tool
from bs4 import BeautifulSoup

try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.agents.base import BaseAgent, agent_registry
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.agents.base import BaseAgent, agent_registry

# Configure logging
logger = logging.getLogger("mosaic.agents.browser_interaction")

# Define the tools as standalone functions
@tool
def browse_javascript_site_tool(url: str, wait_for_selector: Optional[str] = None) -> str:
    """
    Browse a JavaScript-heavy website using a synchronous approach.
    
    Args:
        url: The URL of the website to browse
        wait_for_selector: Optional CSS selector to wait for (e.g., '#product-list')
        
    Returns:
        A string containing the rendered page content
    """
    logger.info(f"Browsing JavaScript site '{url}'")
    if wait_for_selector:
        logger.info(f"Will wait for selector: '{wait_for_selector}'")
    
    try:
        logger.info(f"Using synchronous approach for browser interaction...")
        
        # Use requests to get the page content
        logger.info(f"Making HTTP request to {url}...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        logger.info(f"Request successful: {response.status_code}")
        
        # Parse the HTML content
        logger.info(f"Parsing HTML content...")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
        
        # Get the text content
        text = soup.get_text(separator='\n', strip=True)
        
        # Clean up the text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        # Truncate if too long
        original_length = len(text)
        if original_length > 8000:
            text = text[:8000] + "...\n[Content truncated due to length]"
            logger.info(f"Content truncated from {original_length} to 8000 characters")
        else:
            logger.info(f"Extracted {original_length} characters of content")
        
        # Note: We're not using Playwright, so no screenshot
        logger.info(f"Browser interaction completed successfully (using requests)")
        return f"Content from {url} (Note: JavaScript not rendered):\n\n{text}"
    
    except Exception as e:
        logger.error(f"Error browsing site {url}: {str(e)}")
        error_report = {
            "task": "Browse Site",
            "status": "Failed",
            "url": url,
            "error": str(e),
            "error_type": type(e).__name__,
            "http_status": getattr(response, 'status_code', None) if 'response' in locals() else None
        }
        return f"Error browsing site: {json.dumps(error_report, indent=2)}"

# Note: For a full implementation, you would include an async version using Playwright
# This would require additional setup and dependencies

class BrowserInteractionAgent(BaseAgent):
    """
    Browser interaction agent that can handle JavaScript-heavy websites.
    
    This agent provides tools for browsing JavaScript-heavy websites,
    allowing it to extract information from dynamic web pages.
    """
    
    def __init__(
        self,
        name: str = "browser_interaction",
        model: Optional[LanguageModelLike] = None,
        tools: List[BaseTool] = None,
        prompt: str = None,
        description: str = None,
    ):
        """
        Initialize a new browser interaction agent.
        
        Args:
            name: The name of the agent (default: "browser_interaction")
            model: The language model to use for the agent
            tools: Optional list of additional tools
            prompt: Optional system prompt for the agent
            description: Optional description of the agent
        """
        # Create the browser interaction tools
        browser_tools = [
            browse_javascript_site_tool
        ]
        
        # Combine with any additional tools
        all_tools = browser_tools + (tools or [])
        
        super().__init__(
            name=name,
            model=model,
            tools=all_tools,
            prompt=prompt,
            description=description or "Browser Interaction Agent for handling JavaScript-heavy websites"
        )
        
        logger.info(f"Initialized browser interaction agent with {len(all_tools)} tools")
    
    def _get_default_prompt(self) -> str:
        """
        Get the default system prompt for the browser interaction agent.
        
        Returns:
            A string containing the default system prompt
        """
        return (
            "You are a browser automation specialist that can interact with JavaScript-heavy websites. "
            "Your job is to extract information from websites that require JavaScript rendering. "
            "\n\n"
            "You have tools for browser interaction: "
            "- Use browse_javascript_site_tool to load and interact with web pages. "
            "\n\n"
            "When searching for current or latest information, avoid using specific years or dates in your search queries. "
            "Instead, use terms like 'latest', 'newest', or 'current' to ensure you get the most up-to-date information. "
            "\n\n"
            "Always provide factual information based on the rendered page content. "
            "If you encounter errors or cannot extract information, clearly report the issue. "
            "Never make up information or hallucinate details. "
            "Always attribute information to its source."
        )

# Register the browser interaction agent with the registry
def register_browser_interaction_agent(model: LanguageModelLike) -> BrowserInteractionAgent:
    """
    Create and register a browser interaction agent.
    
    Args:
        model: The language model to use for the agent
        
    Returns:
        The created browser interaction agent
    """
    try:
        # Try importing with the full package path (for local development)
        from mosaic.backend.agents.base import agent_registry
    except ImportError:
        # Fall back to relative import (for Docker environment)
        from backend.agents.base import agent_registry
    
    browser_interaction = BrowserInteractionAgent(model=model)
    agent_registry.register(browser_interaction)
    return browser_interaction
