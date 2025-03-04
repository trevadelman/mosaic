"""
Web Search Agent Module for MOSAIC

This module defines a web search agent that can search the web and fetch webpage content.
It serves as a specialized agent for web research in the MOSAIC system.
"""

import logging
import requests
import json
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus

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
logger = logging.getLogger("mosaic.agents.web_search")

# Define the tools as standalone functions
@tool
def search_web_tool(query: str, num_results: int = 5) -> str:
    """
    Search the web using DuckDuckGo and return the results.
    
    Args:
        query: The search query
        num_results: Number of results to return (default: 5)
        
    Returns:
        A string containing search results with titles, snippets, and URLs
    """
    logger.info(f"Searching web for '{query}'")
    try:
        # Import DDGS here to avoid import errors if the package is not installed
        from duckduckgo_search import DDGS
        
        logger.info(f"Making DuckDuckGo API request...")
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=num_results))
        
        if not results:
            logger.warning(f"No results found for query: '{query}'")
            return f"No results found for query: {query}"
        
        logger.info(f"Found {len(results)} results for query: '{query}'")
        formatted_results = f"Search results for '{query}':\n\n"
        
        for i, result in enumerate(results, 1):
            title = result.get('title', 'No Title')
            body = result.get('body', 'No Description')
            href = result.get('href', 'No URL')
            
            formatted_results += f"{i}. {title}\n"
            formatted_results += f"   {body}\n"
            formatted_results += f"   URL: {href}\n\n"
            
            logger.info(f"Result {i}: {title} - {href}")
        
        return formatted_results
    
    except Exception as e:
        logger.error(f"Error in web search: {str(e)}")
        error_report = {
            "task": "Web Search",
            "status": "Failed",
            "query": query,
            "error": str(e),
            "error_type": type(e).__name__
        }
        return f"Error performing web search: {json.dumps(error_report, indent=2)}"

@tool
def fetch_webpage_content_tool(url: str) -> str:
    """
    Fetch the content of a webpage using simple HTTP requests.
    
    Args:
        url: The URL of the webpage to fetch
        
    Returns:
        A string containing the main text content of the webpage
    """
    logger.info(f"Fetching webpage content from '{url}'")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        logger.info(f"Making HTTP request to {url}...")
        response = requests.get(url, headers=headers, timeout=10)
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
        
        return f"Content from {url}:\n\n{text}"
    
    except Exception as e:
        logger.error(f"Error fetching webpage {url}: {str(e)}")
        error_report = {
            "task": "Fetch Webpage",
            "status": "Failed",
            "url": url,
            "error": str(e),
            "error_type": type(e).__name__,
            "http_status": getattr(response, 'status_code', None) if 'response' in locals() else None
        }
        return f"Error fetching webpage: {json.dumps(error_report, indent=2)}"

class WebSearchAgent(BaseAgent):
    """
    Web search agent that can search the web and fetch webpage content.
    
    This agent provides tools for web search and webpage content retrieval,
    allowing it to gather information from the internet.
    """
    
    def __init__(
        self,
        name: str = "web_search",
        model: Optional[LanguageModelLike] = None,
        tools: List[BaseTool] = None,
        prompt: str = None,
        description: str = None,
        type: str = "Specialized",
        capabilities: List[str] = None,
        icon: str = "🌐",
    ):
        """
        Initialize a new web search agent.
        
        Args:
            name: The name of the agent (default: "web_search")
            model: The language model to use for the agent
            tools: Optional list of additional tools
            prompt: Optional system prompt for the agent
            description: Optional description of the agent
            type: The type of agent (default: "Specialized")
            capabilities: List of agent capabilities
            icon: Emoji icon for the agent (default: "🌐")
        """
        # Create the web search tools
        web_search_tools = [
            search_web_tool,
            fetch_webpage_content_tool
        ]
        
        # Combine with any additional tools
        all_tools = web_search_tools + (tools or [])
        
        # Default capabilities if none provided
        if capabilities is None:
            capabilities = ["Web Search", "Content Retrieval"]
        
        super().__init__(
            name=name,
            model=model,
            tools=all_tools,
            prompt=prompt,
            description=description or "Web Search Agent for searching the web and fetching webpage content",
            type=type,
            capabilities=capabilities,
            icon=icon
        )
        
        logger.info(f"Initialized web search agent with {len(all_tools)} tools")
    
    def _get_default_prompt(self) -> str:
        """
        Get the default system prompt for the web search agent.
        
        Returns:
            A string containing the default system prompt
        """
        return (
            "You are a web research specialist with access to search engines and webpage content retrieval. "
            "Your job is to find accurate information on the web about products, companies, and topics. "
            "\n\n"
            "You have tools for web search and webpage content retrieval: "
            "- Use search_web_tool to find relevant web pages based on a query. "
            "- Use fetch_webpage_content_tool to get detailed information from a specific URL. "
            "\n\n"
            "When searching for current or latest information, avoid using specific years or dates in your search queries. "
            "Instead, use terms like 'latest', 'newest', or 'current' to ensure you get the most up-to-date information. "
            "\n\n"
            "Always provide factual information based on your search results. "
            "If you cannot find information, clearly state that and explain why. "
            "Never make up information or hallucinate details. "
            "Always attribute information to its source."
        )

# Register the web search agent with the registry
def register_web_search_agent(model: LanguageModelLike) -> WebSearchAgent:
    """
    Create and register a web search agent.
    
    Args:
        model: The language model to use for the agent
        
    Returns:
        The created web search agent
    """
    try:
        # Try importing with the full package path (for local development)
        from mosaic.backend.agents.base import agent_registry
    except ImportError:
        # Fall back to relative import (for Docker environment)
        from backend.agents.base import agent_registry
    
    web_search = WebSearchAgent(model=model)
    agent_registry.register(web_search)
    return web_search
