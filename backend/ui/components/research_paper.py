"""
Research Paper Component for MOSAIC

This module provides a UI component for searching, visualizing, and taking notes on research papers.
It uses the ResearchPaperProvider to fetch real data from the Semantic Scholar API.
"""

import logging
import json
import asyncio
from typing import Dict, List, Any, Optional, Callable, Awaitable
from datetime import datetime

# Import the UI component base class
try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.ui.base import UIComponent, ui_component_registry
    from mosaic.backend.agents.base import agent_registry
    from mosaic.backend.data.providers.base import data_provider_registry
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.ui.base import UIComponent, ui_component_registry
    from backend.agents.base import agent_registry
    from backend.data.providers.base import data_provider_registry

# Configure logging
logger = logging.getLogger("mosaic.ui.research_paper")

class ResearchPaperComponent(UIComponent):
    """
    Research Paper Component for searching, visualizing, and taking notes on research papers.
    
    This component provides:
    - Paper search functionality using the Semantic Scholar API
    - Citation visualization
    - Note-taking features
    """
    
    def __init__(self):
        """Initialize the research paper component."""
        super().__init__(
            component_id="research-paper",
            name="Research Paper",
            description="Component for searching, visualizing, and taking notes on research papers",
            required_features=["search", "visualization", "notes"],
            default_modal_config={
                "title": "Research Paper Explorer",
                "width": "90%",
                "height": "90%",
                "resizable": True
            }
        )
        
        # Register handlers
        self.register_handler("search", self.handle_search)
        self.register_handler("get_paper_details", self.handle_get_paper_details)
        self.register_handler("get_citations", self.handle_get_citations)
        self.register_handler("get_references", self.handle_get_references)
        self.register_handler("get_author_details", self.handle_get_author_details)
        self.register_handler("save_note", self.handle_save_note)
        self.register_handler("get_notes", self.handle_get_notes)
        self.register_handler("get_citation_network", self.handle_get_citation_network)
        
        # Initialize notes storage (in a real implementation, this would be in a database)
        self.notes = {}
        
        logger.info(f"Initialized {self.name} component")
    
    async def handle_search(self, websocket: Any, event: Dict[str, Any], agent_id: str, client_id: str) -> None:
        """
        Handle paper search requests.
        
        Args:
            websocket: The WebSocket connection
            event: The event data
            agent_id: The agent ID
            client_id: The client ID
        """
        try:
            # Get search parameters
            query = event.get("query", "")
            filters = event.get("filters", {})
            page = event.get("page", 1)
            page_size = event.get("pageSize", 10)
            
            logger.info(f"Searching for papers with query: {query}, filters: {filters}, page: {page}, page_size: {page_size}")
            
            # Get the research paper provider
            paper_provider = data_provider_registry.get("research-paper")
            
            if not paper_provider:
                raise ValueError("Research paper provider not found")
            
            # Use the provider to search for papers
            search_results = await paper_provider.get_data({
                "type": "search",
                "query": query,
                "filters": filters,
                "page": page,
                "page_size": page_size
            })
            
            # Check for errors
            if "error" in search_results:
                raise ValueError(search_results["error"])
            
            # Send the search results back to the client
            await self._send_response(websocket, event, {
                "success": True,
                "results": search_results.get("results", []),
                "total": search_results.get("total", 0),
                "page": page,
                "pageSize": page_size
            })
        
        except Exception as e:
            logger.error(f"Error handling search request: {str(e)}")
            
            # Send error response
            await self._send_response(websocket, event, {
                "success": False,
                "error": f"Error searching for papers: {str(e)}"
            })
    
    async def handle_get_paper_details(self, websocket: Any, event: Dict[str, Any], agent_id: str, client_id: str) -> None:
        """
        Handle requests for paper details.
        
        Args:
            websocket: The WebSocket connection
            event: The event data
            agent_id: The agent ID
            client_id: The client ID
        """
        try:
            # Get paper ID
            paper_id = event.get("paperId", "")
            
            if not paper_id:
                raise ValueError("Paper ID is required")
            
            logger.info(f"Getting details for paper: {paper_id}")
            
            # Get the research paper provider
            paper_provider = data_provider_registry.get("research-paper")
            
            if not paper_provider:
                raise ValueError("Research paper provider not found")
            
            # Use the provider to get paper details
            paper_details = await paper_provider.get_data({
                "type": "details",
                "paper_id": paper_id
            })
            
            # Check for errors
            if "error" in paper_details:
                raise ValueError(paper_details["error"])
            
            # Send the paper details back to the client
            await self._send_response(websocket, event, {
                "success": True,
                "paper": paper_details
            })
        
        except Exception as e:
            logger.error(f"Error handling get paper details request: {str(e)}")
            
            # Send error response
            await self._send_response(websocket, event, {
                "success": False,
                "error": f"Error getting paper details: {str(e)}"
            })
    
    async def handle_get_citations(self, websocket: Any, event: Dict[str, Any], agent_id: str, client_id: str) -> None:
        """
        Handle requests for papers that cite the given paper.
        
        Args:
            websocket: The WebSocket connection
            event: The event data
            agent_id: The agent ID
            client_id: The client ID
        """
        try:
            # Get paper ID
            paper_id = event.get("paperId", "")
            page = event.get("page", 1)
            page_size = event.get("pageSize", 10)
            
            if not paper_id:
                raise ValueError("Paper ID is required")
            
            logger.info(f"Getting citations for paper: {paper_id}")
            
            # Get the research paper provider
            paper_provider = data_provider_registry.get("research-paper")
            
            if not paper_provider:
                raise ValueError("Research paper provider not found")
            
            # Use the provider to get citations
            citations = await paper_provider.get_data({
                "type": "citations",
                "paper_id": paper_id,
                "page": page,
                "page_size": page_size
            })
            
            # Check for errors
            if "error" in citations:
                raise ValueError(citations["error"])
            
            # Send the citations back to the client
            await self._send_response(websocket, event, {
                "success": True,
                "citations": citations.get("citations", []),
                "total": citations.get("total", 0),
                "page": page,
                "pageSize": page_size
            })
        
        except Exception as e:
            logger.error(f"Error handling get citations request: {str(e)}")
            
            # Send error response
            await self._send_response(websocket, event, {
                "success": False,
                "error": f"Error getting citations: {str(e)}"
            })
    
    async def handle_get_references(self, websocket: Any, event: Dict[str, Any], agent_id: str, client_id: str) -> None:
        """
        Handle requests for papers that are referenced by the given paper.
        
        Args:
            websocket: The WebSocket connection
            event: The event data
            agent_id: The agent ID
            client_id: The client ID
        """
        try:
            # Get paper ID
            paper_id = event.get("paperId", "")
            page = event.get("page", 1)
            page_size = event.get("pageSize", 10)
            
            if not paper_id:
                raise ValueError("Paper ID is required")
            
            logger.info(f"Getting references for paper: {paper_id}")
            
            # Get the research paper provider
            paper_provider = data_provider_registry.get("research-paper")
            
            if not paper_provider:
                raise ValueError("Research paper provider not found")
            
            # Use the provider to get references
            references = await paper_provider.get_data({
                "type": "references",
                "paper_id": paper_id,
                "page": page,
                "page_size": page_size
            })
            
            # Check for errors
            if "error" in references:
                raise ValueError(references["error"])
            
            # Send the references back to the client
            await self._send_response(websocket, event, {
                "success": True,
                "references": references.get("references", []),
                "total": references.get("total", 0),
                "page": page,
                "pageSize": page_size
            })
        
        except Exception as e:
            logger.error(f"Error handling get references request: {str(e)}")
            
            # Send error response
            await self._send_response(websocket, event, {
                "success": False,
                "error": f"Error getting references: {str(e)}"
            })
    
    async def handle_get_author_details(self, websocket: Any, event: Dict[str, Any], agent_id: str, client_id: str) -> None:
        """
        Handle requests for author details.
        
        Args:
            websocket: The WebSocket connection
            event: The event data
            agent_id: The agent ID
            client_id: The client ID
        """
        try:
            # Get author ID
            author_id = event.get("authorId", "")
            
            if not author_id:
                raise ValueError("Author ID is required")
            
            logger.info(f"Getting details for author: {author_id}")
            
            # Get the research paper provider
            paper_provider = data_provider_registry.get("research-paper")
            
            if not paper_provider:
                raise ValueError("Research paper provider not found")
            
            # Use the provider to get author details
            author_details = await paper_provider.get_data({
                "type": "author",
                "author_id": author_id
            })
            
            # Check for errors
            if "error" in author_details:
                raise ValueError(author_details["error"])
            
            # Send the author details back to the client
            await self._send_response(websocket, event, {
                "success": True,
                "author": author_details
            })
        
        except Exception as e:
            logger.error(f"Error handling get author details request: {str(e)}")
            
            # Send error response
            await self._send_response(websocket, event, {
                "success": False,
                "error": f"Error getting author details: {str(e)}"
            })
    
    async def handle_save_note(self, websocket: Any, event: Dict[str, Any], agent_id: str, client_id: str) -> None:
        """
        Handle requests to save notes on papers.
        
        Args:
            websocket: The WebSocket connection
            event: The event data
            agent_id: The agent ID
            client_id: The client ID
        """
        try:
            # Get note data
            paper_id = event.get("paperId", "")
            note_content = event.get("content", "")
            note_id = event.get("noteId")  # Optional, for updating existing notes
            tags = event.get("tags", [])
            
            if not paper_id:
                raise ValueError("Paper ID is required")
            
            if not note_content:
                raise ValueError("Note content is required")
            
            logger.info(f"Saving note for paper: {paper_id}")
            
            # Generate a new note ID if not provided
            if not note_id:
                note_id = f"note_{datetime.now().timestamp()}"
            
            # Create or update the note
            note = {
                "id": note_id,
                "paperId": paper_id,
                "content": note_content,
                "timestamp": int(datetime.now().timestamp() * 1000),
                "tags": tags,
                "userId": client_id,  # In a real implementation, this would be a real user ID
                "agentId": agent_id
            }
            
            # Store the note
            if paper_id not in self.notes:
                self.notes[paper_id] = []
            
            # Check if we're updating an existing note
            updated = False
            for i, existing_note in enumerate(self.notes[paper_id]):
                if existing_note["id"] == note_id:
                    self.notes[paper_id][i] = note
                    updated = True
                    break
            
            # If not updating, add as a new note
            if not updated:
                self.notes[paper_id].append(note)
            
            # Send success response
            await self._send_response(websocket, event, {
                "success": True,
                "note": note,
                "message": "Note saved successfully"
            })
        
        except Exception as e:
            logger.error(f"Error handling save note request: {str(e)}")
            
            # Send error response
            await self._send_response(websocket, event, {
                "success": False,
                "error": f"Error saving note: {str(e)}"
            })
    
    async def handle_get_notes(self, websocket: Any, event: Dict[str, Any], agent_id: str, client_id: str) -> None:
        """
        Handle requests to get notes for a paper.
        
        Args:
            websocket: The WebSocket connection
            event: The event data
            agent_id: The agent ID
            client_id: The client ID
        """
        try:
            # Get paper ID
            paper_id = event.get("paperId", "")
            
            if not paper_id:
                raise ValueError("Paper ID is required")
            
            logger.info(f"Getting notes for paper: {paper_id}")
            
            # Get notes for the paper
            paper_notes = self.notes.get(paper_id, [])
            
            # Filter notes by user ID if needed (in a real implementation)
            # paper_notes = [note for note in paper_notes if note["userId"] == client_id]
            
            # Sort notes by timestamp (newest first)
            paper_notes.sort(key=lambda x: x["timestamp"], reverse=True)
            
            # Send the notes back to the client
            await self._send_response(websocket, event, {
                "success": True,
                "notes": paper_notes
            })
        
        except Exception as e:
            logger.error(f"Error handling get notes request: {str(e)}")
            
            # Send error response
            await self._send_response(websocket, event, {
                "success": False,
                "error": f"Error getting notes: {str(e)}"
            })
    
    async def handle_get_citation_network(self, websocket: Any, event: Dict[str, Any], agent_id: str, client_id: str) -> None:
        """
        Handle requests to get a citation network for visualization.
        
        Args:
            websocket: The WebSocket connection
            event: The event data
            agent_id: The agent ID
            client_id: The client ID
        """
        try:
            # Get paper ID and network depth
            paper_id = event.get("paperId", "")
            depth = event.get("depth", 1)  # How many levels to go out
            max_papers = event.get("maxPapers", 50)  # Maximum number of papers to include
            
            if not paper_id:
                raise ValueError("Paper ID is required")
            
            logger.info(f"Getting citation network for paper: {paper_id} with depth {depth}")
            
            # Get the research paper provider
            paper_provider = data_provider_registry.get("research-paper")
            
            if not paper_provider:
                raise ValueError("Research paper provider not found")
            
            # First, get the paper details
            paper_details = await paper_provider.get_data({
                "type": "details",
                "paper_id": paper_id
            })
            
            # Check for errors
            if "error" in paper_details:
                raise ValueError(paper_details["error"])
            
            # Initialize the network
            nodes = [
                {
                    "id": paper_details["id"],
                    "title": paper_details["title"],
                    "year": paper_details["year"],
                    "authors": [author["name"] for author in paper_details.get("authors", [])],
                    "citationCount": paper_details.get("citationCount", 0),
                    "type": "central"  # Mark as the central node
                }
            ]
            links = []
            
            # Keep track of papers we've already processed
            processed_papers = {paper_details["id"]}
            
            # Get citations (papers that cite this paper)
            if depth > 0:
                citations = await paper_provider.get_data({
                    "type": "citations",
                    "paper_id": paper_id,
                    "page": 1,
                    "page_size": max_papers // 2  # Split the max between citations and references
                })
                
                # Check for errors
                if "error" not in citations:
                    # Add citation nodes and links
                    for citation in citations.get("citations", [])[:max_papers // 2]:
                        if citation["id"] not in processed_papers:
                            nodes.append({
                                "id": citation["id"],
                                "title": citation["title"],
                                "year": citation["year"],
                                "authors": [author["name"] for author in citation.get("authors", [])],
                                "citationCount": citation.get("citationCount", 0),
                                "type": "citation"  # Mark as a citation
                            })
                            
                            links.append({
                                "source": citation["id"],
                                "target": paper_details["id"],
                                "type": "cites"
                            })
                            
                            processed_papers.add(citation["id"])
            
            # Get references (papers cited by this paper)
            if depth > 0:
                references = await paper_provider.get_data({
                    "type": "references",
                    "paper_id": paper_id,
                    "page": 1,
                    "page_size": max_papers // 2  # Split the max between citations and references
                })
                
                # Check for errors
                if "error" not in references:
                    # Add reference nodes and links
                    for reference in references.get("references", [])[:max_papers // 2]:
                        if reference["id"] not in processed_papers:
                            nodes.append({
                                "id": reference["id"],
                                "title": reference["title"],
                                "year": reference["year"],
                                "authors": [author["name"] for author in reference.get("authors", [])],
                                "citationCount": reference.get("citationCount", 0),
                                "type": "reference"  # Mark as a reference
                            })
                            
                            links.append({
                                "source": paper_details["id"],
                                "target": reference["id"],
                                "type": "cites"
                            })
                            
                            processed_papers.add(reference["id"])
            
            # Send the network back to the client
            await self._send_response(websocket, event, {
                "success": True,
                "network": {
                    "nodes": nodes,
                    "links": links
                }
            })
        
        except Exception as e:
            logger.error(f"Error handling get citation network request: {str(e)}")
            
            # Send error response
            await self._send_response(websocket, event, {
                "success": False,
                "error": f"Error getting citation network: {str(e)}"
            })
    
    async def _send_response(self, websocket: Any, event: Dict[str, Any], response_data: Dict[str, Any]) -> None:
        """
        Send a response back to the client.
        
        Args:
            websocket: The WebSocket connection
            event: The original event
            response_data: The response data
        """
        # Add the component and action to the response
        response = {
            "type": "ui_event",
            "data": {
                "component": self.component_id,
                "action": event.get("action", "unknown"),
                "requestId": event.get("requestId", "unknown"),
                **response_data
            }
        }
        
        # Send the response
        await websocket.send_json(response)

# Register the component
research_paper_component = ResearchPaperComponent()
ui_component_registry.register(research_paper_component)

# Register the component with the research_supervisor agent
agent_registry.register_ui_component("research_supervisor", research_paper_component.component_id)

# Also register with the literature agent if it exists
if "literature" in agent_registry.list_agents():
    agent_registry.register_ui_component("literature", research_paper_component.component_id)

logger.info(f"Registered {research_paper_component.name} component with ID {research_paper_component.component_id}")
