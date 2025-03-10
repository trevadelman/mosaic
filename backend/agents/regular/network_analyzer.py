"""
Network Analyzer Agent Module for MOSAIC

This module defines an agent that analyzes network data.
"""

import logging
import random
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
logger = logging.getLogger("mosaic.agents.network_analyzer")

# Define a function to generate a network with a specified number of nodes and topology
def generate_network(query: str = "", num_nodes: int = 2, model: Optional[LanguageModelLike] = None) -> Dict[str, Any]:
    """
    Generate a network with the specified number of nodes and topology.
    
    Args:
        query: Optional query string to determine the network topology
        num_nodes: The number of nodes to generate (default: 2)
        model: Optional language model to use for generating the network
        
    Returns:
        A dictionary containing the network data
    """
    # Ensure at least 2 nodes
    num_nodes = max(2, num_nodes)
    
    # Generate nodes
    nodes = []
    for i in range(num_nodes):
        node_id = chr(65 + i)  # A, B, C, ...
        nodes.append({
            "id": node_id,
            "label": f"Node {node_id}"
        })
    
    # If no query or model, use a simple chain topology
    if not query or not model:
        # Generate links (simple chain topology)
        links = []
        for i in range(num_nodes - 1):
            source_id = chr(65 + i)
            target_id = chr(65 + i + 1)
            links.append({
                "source": source_id,
                "target": target_id
            })
    else:
        # Use the LLM to generate a network structure based on the query
        try:
            # Prepare the prompt for the LLM
            prompt = f"""
            Generate a network structure based on the following query: "{query}"
            
            The network has {num_nodes} nodes labeled from A to {chr(64 + num_nodes)}.
            
            Return a JSON array of links between nodes, where each link is an object with "source" and "target" properties.
            The source and target should be node IDs (A, B, C, etc.).
            
            Example:
            [
                {{"source": "A", "target": "B"}},
                {{"source": "B", "target": "C"}},
                {{"source": "A", "target": "C"}}
            ]
            
            Only return the JSON array, nothing else.
            """
            
            # Get the response from the LLM
            response = model.invoke(prompt)
            
            # Extract the content from the response
            # The response might be an AIMessage object or a string
            if hasattr(response, 'content'):
                # If it's an AIMessage object, extract the content
                response_text = response.content
            else:
                # If it's already a string, use it directly
                response_text = str(response)
            
            # Parse the response as JSON
            import json
            import re
            
            # Extract JSON array from the response
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                links_data = json.loads(json_str)
                
                # Validate the links
                links = []
                valid_node_ids = set(node["id"] for node in nodes)
                
                for link in links_data:
                    source = link.get("source")
                    target = link.get("target")
                    
                    if source in valid_node_ids and target in valid_node_ids and source != target:
                        links.append({
                            "source": source,
                            "target": target
                        })
                
                # If no valid links were found, fall back to chain topology
                if not links:
                    logger.warning("No valid links found in LLM response, falling back to chain topology")
                    for i in range(num_nodes - 1):
                        source_id = chr(65 + i)
                        target_id = chr(65 + i + 1)
                        links.append({
                            "source": source_id,
                            "target": target_id
                        })
            else:
                # Fall back to chain topology
                logger.warning("Could not parse LLM response, falling back to chain topology")
                links = []
                for i in range(num_nodes - 1):
                    source_id = chr(65 + i)
                    target_id = chr(65 + i + 1)
                    links.append({
                        "source": source_id,
                        "target": target_id
                    })
        except Exception as e:
            # Log the error and fall back to chain topology
            logger.error(f"Error generating network structure: {str(e)}")
            links = []
            for i in range(num_nodes - 1):
                source_id = chr(65 + i)
                target_id = chr(65 + i + 1)
                links.append({
                    "source": source_id,
                    "target": target_id
                })
    
    return {
        "nodes": nodes,
        "links": links
    }

# Define the network tool
@tool
def network_tool(query: str = "", num_nodes: int = 2) -> Dict[str, Any]:
    """
    Generate a network visualization with the specified number of nodes and topology.
    
    Args:
        query: Optional query string to determine the network topology
        num_nodes: The number of nodes to generate (default: 2)
        
    Returns:
        A dictionary containing the network data
    """
    # We don't have access to the agent_id here, so we can't get the model
    # Just use a simple chain topology
    model = None
    
    return generate_network(query, num_nodes, model)

# No replacement - removing the simple_network_tool function

# No WebSocket handlers needed

class NetworkAnalyzerAgent(BaseAgent):
    """
    Network Analyzer agent that analyzes network data.
    
    This agent provides tools for analyzing network data.
    """
    
    def __init__(
        self,
        name: str = "network_analyzer",
        model: Optional[LanguageModelLike] = None,
        tools: List[BaseTool] = None,
        prompt: str = None,
        description: str = None,
        type: str = "Utility",
        capabilities: List[str] = None,
        icon: str = "🔍",
    ):
        """
        Initialize a new network analyzer agent.
        
        Args:
            name: The name of the agent (default: "network_analyzer")
            model: The language model to use for the agent
            tools: Optional list of additional tools
            prompt: Optional system prompt for the agent
            description: Optional description of the agent
            type: The type of agent (default: "Utility")
            capabilities: List of agent capabilities
            icon: Emoji icon for the agent (default: "🔍")
        """
        # Create the network analyzer tools
        network_tools = [
            network_tool
        ]
        
        # Combine with any additional tools
        all_tools = network_tools + (tools or [])
        
        # Default capabilities if none provided
        if capabilities is None:
            capabilities = ["Network Analysis"]
        
        super().__init__(
            name=name,
            model=model,
            tools=all_tools,
            prompt=prompt,
            description=description or "Network Analyzer Agent for visualizing network data",
            type=type,
            capabilities=capabilities,
            icon=icon
        )
        
        logger.debug(f"Initialized network analyzer agent with {len(all_tools)} tools")
    
    def _get_default_prompt(self) -> str:
        """
        Get the default system prompt for the network analyzer agent.
        
        Returns:
            A string containing the default system prompt
        """
        return (
            "You are a network analyzer agent that can analyze network data. "
            "You have tools for generating network data. "
            "ALWAYS use the appropriate tool to generate data for the requested network. "
            "NEVER generate the data yourself - ALWAYS use one of the provided tools. "
            "If the user asks for a network visualization, use the network_tool. "
            "You can generate different network structures based on user queries. "
            "For example, you can create star networks, ring networks, fully connected networks, etc. "
            "Always explain what you're generating and what the data represents."
        )

# Register the network analyzer agent with the registry
def register_network_analyzer_agent(model: LanguageModelLike) -> NetworkAnalyzerAgent:
    """
    Create and register a network analyzer agent.
    
    Args:
        model: The language model to use for the agent
        
    Returns:
        The created network analyzer agent
    """
    # Create the agent
    network_analyzer = NetworkAnalyzerAgent(model=model)
    
    # Register the agent with the registry
    agent_registry.register(network_analyzer)
    
    return network_analyzer
