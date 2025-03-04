"""
Literature Agent Module for MOSAIC

This module defines a literature agent that can search for academic papers and articles.
It serves as a specialized agent for academic research in the MOSAIC system.
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
logger = logging.getLogger("mosaic.agents.literature")

# Define the tools as standalone functions
@tool
def search_arxiv_tool(query: str, max_results: int = 5) -> str:
    """
    Search for academic papers on arXiv.
    
    Args:
        query: The search query
        max_results: Maximum number of results to return (default: 5)
        
    Returns:
        A string containing paper titles, authors, and abstracts
    """
    logger.info(f"Searching arXiv for '{query}'")
    try:
        # Encode the query for URL
        encoded_query = quote_plus(query)
        
        # Make request to arXiv API
        logger.info(f"Making request to arXiv API...")
        url = f"http://export.arxiv.org/api/query?search_query=all:{encoded_query}&start=0&max_results={max_results}"
        response = requests.get(url)
        response.raise_for_status()
        logger.info(f"Request successful: {response.status_code}")
        
        # Parse the XML response
        logger.info(f"Parsing XML response...")
        soup = BeautifulSoup(response.content, 'xml')
        entries = soup.find_all('entry')
        
        if not entries:
            logger.warning(f"No papers found on arXiv for query: '{query}'")
            return f"No papers found on arXiv for query: {query}"
        
        # Format the results
        logger.info(f"Found {len(entries)} papers on arXiv for query: '{query}'")
        results = f"arXiv papers related to '{query}':\n\n"
        
        for i, entry in enumerate(entries, 1):
            title = entry.find('title').text.strip()
            authors = [author.find('name').text for author in entry.find_all('author')]
            authors_str = ", ".join(authors)
            abstract = entry.find('summary').text.strip().replace('\n', ' ')
            published = entry.find('published').text.split('T')[0]  # Just get the date part
            arxiv_id = entry.find('id').text.split('/')[-1]
            pdf_link = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
            
            results += f"{i}. {title}\n"
            results += f"   Authors: {authors_str}\n"
            results += f"   Published: {published}\n"
            results += f"   PDF: {pdf_link}\n"
            results += f"   Abstract: {abstract[:300]}...\n\n"
            
            logger.info(f"Paper {i}: {title} (ID: {arxiv_id})")
        
        return results
    
    except Exception as e:
        logger.error(f"Error searching arXiv: {str(e)}")
        error_report = {
            "task": "arXiv Search",
            "status": "Failed",
            "query": query,
            "error": str(e),
            "error_type": type(e).__name__,
            "http_status": getattr(response, 'status_code', None) if 'response' in locals() else None
        }
        return f"Error searching arXiv: {json.dumps(error_report, indent=2)}"

@tool
def search_open_access_journals_tool(query: str, max_results: int = 5) -> str:
    """
    Search for open access journal articles.
    
    Args:
        query: The search query
        max_results: Maximum number of results to return (default: 5)
        
    Returns:
        A string containing article titles, authors, and abstracts
    """
    logger.info(f"Searching open access journals for '{query}'")
    try:
        # For demo purposes, we'll use a simpler API that doesn't require authentication
        # In a real implementation, you would use the CORE API with an API key
        
        # Encode the query for URL
        encoded_query = quote_plus(query)
        
        # Make request to the Open Access Button API
        logger.info(f"Making request to Open Access Button API...")
        url = f"https://api.openaccessbutton.org/find?q={encoded_query}&limit={max_results}"
        response = requests.get(url)
        response.raise_for_status()
        logger.info(f"Request successful: {response.status_code}")
        
        # Check if the response is JSON
        content_type = response.headers.get('Content-Type', '')
        if 'application/json' in content_type:
            data = response.json()
        else:
            logger.warning(f"API returned non-JSON response: {content_type}")
            return f"The Open Access Button API returned a non-JSON response for query: {query}"
        
        # Check if data is a list or dictionary
        if isinstance(data, str):
            logger.warning(f"API returned a string instead of JSON: {data[:100]}...")
            return f"The Open Access Button API returned an unexpected response format for query: {query}"
        
        if not data or (isinstance(data, list) and len(data) == 0):
            logger.warning(f"No open access articles found for query: '{query}'")
            return f"No open access articles found for query: {query}"
        
        # Format the results
        if isinstance(data, list):
            logger.info(f"Found {len(data)} open access articles for query: '{query}'")
            results = f"Open access articles related to '{query}':\n\n"
            
            for i, article in enumerate(data, 1):
                if not isinstance(article, dict):
                    continue
                    
                title = article.get('title', 'No Title')
                authors = article.get('authors', [])
                authors_str = ", ".join(authors) if authors else "Unknown Authors"
                article_url = article.get('url', 'No URL')
                source = article.get('source', 'Unknown Source')
                
                results += f"{i}. {title}\n"
                results += f"   Authors: {authors_str}\n"
                results += f"   Source: {source}\n"
                results += f"   URL: {article_url}\n\n"
                
                logger.info(f"Article {i}: {title} (Source: {source})")
        else:
            # Handle case where data is a dictionary or other format
            results = f"Found information related to '{query}', but the format is not as expected.\n\n"
            results += f"Raw data: {json.dumps(data, indent=2)[:500]}...\n"
            logger.warning(f"Unexpected data format from API: {type(data)}")
        
        return results
    
    except Exception as e:
        logger.error(f"Error searching open access journals: {str(e)}")
        error_report = {
            "task": "Open Access Journal Search",
            "status": "Failed",
            "query": query,
            "error": str(e),
            "error_type": type(e).__name__,
            "http_status": getattr(response, 'status_code', None) if 'response' in locals() else None
        }
        # Return a graceful error message that won't break the agent system
        return f"Unable to search open access journals due to an error: {str(e)}"

class LiteratureAgent(BaseAgent):
    """
    Literature agent that can search for academic papers and articles.
    
    This agent provides tools for searching academic repositories and open access journals,
    allowing it to gather scholarly information on various topics.
    """
    
    def __init__(
        self,
        name: str = "literature",
        model: Optional[LanguageModelLike] = None,
        tools: List[BaseTool] = None,
        prompt: str = None,
        description: str = None,
        type: str = "Specialized",
        capabilities: List[str] = None,
        icon: str = "📚",
    ):
        """
        Initialize a new literature agent.
        
        Args:
            name: The name of the agent (default: "literature")
            model: The language model to use for the agent
            tools: Optional list of additional tools
            prompt: Optional system prompt for the agent
            description: Optional description of the agent
            type: The type of agent (default: "Specialized")
            capabilities: List of agent capabilities
            icon: Emoji icon for the agent (default: "📚")
        """
        # Create the literature tools
        literature_tools = [
            search_arxiv_tool,
            search_open_access_journals_tool
        ]
        
        # Combine with any additional tools
        all_tools = literature_tools + (tools or [])
        
        # Default capabilities if none provided
        if capabilities is None:
            capabilities = ["Academic Research", "Paper Analysis"]
        
        super().__init__(
            name=name,
            model=model,
            tools=all_tools,
            prompt=prompt,
            description=description or "Literature Agent for searching academic papers and articles",
            type=type,
            capabilities=capabilities,
            icon=icon
        )
        
        logger.info(f"Initialized literature agent with {len(all_tools)} tools")
    
    def _get_default_prompt(self) -> str:
        """
        Get the default system prompt for the literature agent.
        
        Returns:
            A string containing the default system prompt
        """
        return (
            "You are a literature research specialist with access to academic paper repositories. "
            "Your job is to find relevant academic papers and articles on specific topics. "
            "\n\n"
            "You have tools for literature search: "
            "- Use search_arxiv_tool to find papers on arXiv. "
            "- Use search_open_access_journals_tool for journal articles. "
            "\n\n"
            "Always provide factual information based on your search results. "
            "If you cannot find relevant papers, clearly state that and explain why. "
            "Never make up information or hallucinate details about papers or research. "
            "Always attribute information to its source and provide links to papers when available."
        )

# Register the literature agent with the registry
def register_literature_agent(model: LanguageModelLike) -> LiteratureAgent:
    """
    Create and register a literature agent.
    
    Args:
        model: The language model to use for the agent
        
    Returns:
        The created literature agent
    """
    try:
        # Try importing with the full package path (for local development)
        from mosaic.backend.agents.base import agent_registry
    except ImportError:
        # Fall back to relative import (for Docker environment)
        from backend.agents.base import agent_registry
    
    literature = LiteratureAgent(model=model)
    agent_registry.register(literature)
    return literature
