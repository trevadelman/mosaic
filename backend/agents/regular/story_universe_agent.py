"""
Story Universe Explorer Agent Module for MOSAIC

This module defines a story universe explorer agent that can generate and manage interconnected
story elements (characters, places, events) and their relationships. It provides tools for
creating, exploring, and visualizing a story universe.
"""

import logging
import json
import uuid
import os
import datetime
from typing import List, Dict, Any, Optional, Union, Tuple
from json import JSONEncoder
from langchain_core.language_models import LanguageModelLike
from langchain_core.tools import BaseTool, tool

class StoryUniverseEncoder(JSONEncoder):
    """Custom JSON encoder for Story Universe data structures."""
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return JSONEncoder.default(self, obj)

def json_dumps(obj: Any) -> str:
    """Helper function to consistently encode JSON with our custom encoder."""
    return json.dumps(obj, cls=StoryUniverseEncoder, ensure_ascii=False)

try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.agents.base import BaseAgent, agent_registry
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.agents.base import BaseAgent, agent_registry

# Configure logging
logger = logging.getLogger("mosaic.agents.story_universe_agent")

# Get absolute paths to output directories
try:
    # Get backend directory (go up two levels: regular -> agents -> backend)
    BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    STORY_UNIVERSES_DIR = os.path.join(BACKEND_DIR, "story_universes")
    
    # Create directories if they don't exist
    os.makedirs(STORY_UNIVERSES_DIR, exist_ok=True)
except Exception as e:
    logger.error(f"Error setting up directories: {str(e)}")
    raise

# Define story element types
ELEMENT_TYPES = ["character", "location", "event"]

# Define relationship types
RELATIONSHIP_TYPES = [
    "knows", "related_to", "friends_with", "enemies_with", "loves", "hates",
    "works_at", "lives_in", "visited", "created", "destroyed", "participated_in",
    "owns", "leads", "follows", "betrayed", "saved", "located_in", "happened_at",
    "happened_before", "happened_after", "caused", "resulted_from"
]

# In-memory storage for story universe
# This will be replaced with a more robust solution in later phases
story_universe = {
    "elements": {},  # Dictionary of elements by ID
    "relationships": []  # List of relationships
}

def _format_universe_state() -> str:
    """Format the current universe state as a structured message."""
    return json.dumps({
        "type": "universe_update",
        "state": {
            "elements": story_universe["elements"],
            "relationships": story_universe["relationships"]
        }
    }, cls=StoryUniverseEncoder)

def _format_tool_response(result: Any, include_state: bool = True) -> str:
    """Format a tool response with optional universe state."""
    response = {
        "type": "tool_response",
        "result": result
    }
    if include_state:
        response["universe_state"] = story_universe
    return json.dumps(response, cls=StoryUniverseEncoder)

def _generate_id() -> str:
    """Generate a unique ID for a story element."""
    return str(uuid.uuid4())[:8]

def _get_element_by_id(element_id: str) -> Optional[Dict[str, Any]]:
    """Get a story element by its ID."""
    return story_universe["elements"].get(element_id)

def _get_elements_by_type(element_type: str) -> List[Dict[str, Any]]:
    """Get all story elements of a specific type."""
    return [
        element for element in story_universe["elements"].values()
        if element["type"] == element_type
    ]

def _get_relationships_for_element(element_id: str) -> List[Dict[str, Any]]:
    """Get all relationships involving a specific element."""
    return [
        rel for rel in story_universe["relationships"]
        if rel["source"] == element_id or rel["target"] == element_id
    ]

def _validate_universe_state() -> bool:
    """Validate the current universe state."""
    try:
        # Check basic structure
        if not isinstance(story_universe, dict):
            return False
        if "elements" not in story_universe or "relationships" not in story_universe:
            return False
        
        # Validate elements
        if not isinstance(story_universe["elements"], dict):
            return False
        
        # Validate relationships
        if not isinstance(story_universe["relationships"], list):
            return False
        
        # Validate element references in relationships
        element_ids = set(story_universe["elements"].keys())
        for rel in story_universe["relationships"]:
            if rel["source"] not in element_ids or rel["target"] not in element_ids:
                return False
        
        return True
    except Exception:
        return False

def _save_universe_to_file(universe_id: str = None) -> dict:
    """Save the current story universe to a file."""
    try:
        # Generate a filename using timestamp if no ID provided
        if not universe_id:
            universe_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create the filename
        filename = f"universe_{universe_id}.json"
        filepath = os.path.join(STORY_UNIVERSES_DIR, filename)
        
        # Save the universe data
        with open(filepath, 'w') as f:
            json.dump(story_universe, f, indent=2, cls=StoryUniverseEncoder, ensure_ascii=False)
        
        return {
            "success": True,
            "universe_id": universe_id,
            "message": f"Universe saved successfully with ID: {universe_id}"
        }
    except Exception as e:
        logger.error(f"Error saving universe to file: {str(e)}")
        return None

def _load_universe_from_file(universe_id: str) -> dict:
    """Load a story universe from a file."""
    try:
        # Create the filename
        filename = f"universe_{universe_id}.json"
        filepath = os.path.join(STORY_UNIVERSES_DIR, filename)
        
        # Check if file exists
        if not os.path.exists(filepath):
            logger.error(f"Universe file not found: {filepath}")
            return {
                "success": False,
                "error": f"Universe {universe_id} not found"
            }
        
        # Load the universe data
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        # Update the story universe
        story_universe["elements"] = data["elements"]
        story_universe["relationships"] = data["relationships"]
        
        return {
            "success": True,
            "message": f"Universe {universe_id} loaded successfully",
            "universe": story_universe
        }
    except Exception as e:
        logger.error(f"Error loading universe from file: {str(e)}")
        return False

@tool
def generate_story_element(element_type: str, description: str) -> str:
    """
    Generate a new story element (character, location, or event).
    
    Args:
        element_type: The type of element to generate (character, location, or event)
        description: A brief description or requirements for the element
        
    Returns:
        A JSON string containing the generated element and universe state
    """
    logger.info(f"Generating {element_type} with description: {description}")
    
    if element_type not in ELEMENT_TYPES:
        error_msg = f"Invalid element type: {element_type}. Must be one of {ELEMENT_TYPES}"
        logger.error(error_msg)
        return _format_tool_response({"error": error_msg}, include_state=False)
    
    try:
        # Validate current state
        if not _validate_universe_state():
            logger.warning("Invalid universe state detected, resetting to empty state")
            story_universe["elements"] = {}
            story_universe["relationships"] = []
        
        # Generate a unique ID for the element
        element_id = _generate_id()
        
        # Create the element
        element = {
            "id": element_id,
            "type": element_type,
            "name": "",  # Will be filled by the LLM
            "description": "",  # Will be filled by the LLM
            "attributes": {},  # Will be filled by the LLM
            "created_from": description
        }
        
        # Add the element to the story universe
        story_universe["elements"][element_id] = element
        
        # Return the element and complete universe state
        return _format_tool_response(element)
    
    except Exception as e:
        logger.error(f"Error generating story element: {str(e)}")
        return _format_tool_response({"error": str(e)}, include_state=False)

@tool
def create_relationship(source_id: str, target_id: str, relationship_type: str, description: str) -> str:
    """
    Create a relationship between two story elements.
    
    Args:
        source_id: The ID of the source element
        target_id: The ID of the target element
        relationship_type: The type of relationship
        description: A description of the relationship
        
    Returns:
        A JSON string containing the created relationship
    """
    logger.info(f"Creating relationship from {source_id} to {target_id} of type {relationship_type}")
    
    # Validate the relationship type
    if relationship_type not in RELATIONSHIP_TYPES:
        error_msg = f"Invalid relationship type: {relationship_type}. Must be one of {RELATIONSHIP_TYPES}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})
    
    # Validate the source and target elements
    source_element = _get_element_by_id(source_id)
    target_element = _get_element_by_id(target_id)
    
    if not source_element:
        error_msg = f"Source element with ID {source_id} not found"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})
    
    if not target_element:
        error_msg = f"Target element with ID {target_id} not found"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})
    
    try:
        # Create the relationship
        relationship = {
            "id": _generate_id(),
            "source": source_id,
            "target": target_id,
            "type": relationship_type,
            "description": description
        }
        
        # Add the relationship to the story universe
        story_universe["relationships"].append(relationship)
        
        # Return the relationship as a JSON string using custom encoder
        return json.dumps(relationship, cls=StoryUniverseEncoder, ensure_ascii=False)
    
    except Exception as e:
        logger.error(f"Error creating relationship: {str(e)}")
        return json.dumps({"error": str(e)})

@tool
def get_story_universe() -> str:
    """
    Get the current state of the story universe.
    
    Returns:
        A JSON string containing the entire story universe
    """
    logger.info("Getting story universe")
    
    try:
        # Initialize story universe if it's empty
        if not story_universe["elements"] and not story_universe["relationships"]:
            logger.info("Initializing empty story universe")
            story_universe["elements"] = {}
            story_universe["relationships"] = []
        
        # Return the story universe as a JSON string using custom encoder
        return json.dumps({
            "elements": story_universe["elements"],
            "relationships": story_universe["relationships"]
        }, cls=StoryUniverseEncoder, ensure_ascii=False)
    
    except Exception as e:
        logger.error(f"Error getting story universe: {str(e)}")
        return json.dumps({"error": str(e)})

@tool
def reset_story_universe() -> str:
    """
    Reset the story universe to an empty state.
    
    Returns:
        A JSON string containing the empty story universe
    """
    logger.info("Resetting story universe")
    
    try:
        # Clear the story universe
        story_universe["elements"] = {}
        story_universe["relationships"] = []
        
        # Return the empty story universe using custom encoder
        return json.dumps({
            "elements": {},
            "relationships": []
        }, cls=StoryUniverseEncoder, ensure_ascii=False)
    
    except Exception as e:
        logger.error(f"Error resetting story universe: {str(e)}")
        return json.dumps({"error": str(e)})

@tool
def save_universe(universe_id: str = None) -> str:
    """
    Save the current story universe to a file.
    
    Args:
        universe_id: Optional ID for the universe. If not provided, a timestamp will be used.
        
    Returns:
        A JSON string containing the save result
    """
    logger.info(f"Saving universe{' with ID ' + universe_id if universe_id else ''}")
    
    try:
        # Save the universe and return the result
        result = _save_universe_to_file(universe_id)
        return json.dumps(result)
    
    except Exception as e:
        logger.error(f"Error saving universe: {str(e)}")
        return json.dumps({
            "success": False,
            "error": str(e)
        })

@tool
def load_universe(universe_id: str) -> str:
    """
    Load a story universe from a file.
    
    Args:
        universe_id: The ID of the universe to load
        
    Returns:
        A JSON string containing the load result
    """
    logger.info(f"Loading universe with ID {universe_id}")
    
    try:
        # Load the universe and return the result
        result = _load_universe_from_file(universe_id)
        return json.dumps(result)
    
    except Exception as e:
        logger.error(f"Error loading universe: {str(e)}")
        return json.dumps({
            "success": False,
            "error": str(e)
        })

@tool
def generate_universe_from_text(text: str) -> str:
    """
    Generate a story universe from a plaintext story description.
    
    Args:
        text: The plaintext story to parse and generate elements and relationships from
        
    Returns:
        A JSON string containing the generated story universe
    """
    logger.info("Generating universe from text")
    
    try:
        # Clear the existing story universe
        story_universe["elements"] = {}
        story_universe["relationships"] = []
        
        # Extract potential elements and relationships using the LLM
        # The actual implementation will be handled by the agent's LLM
        # which will analyze the text and identify:
        # - Characters and their descriptions
        # - Locations and their descriptions
        # - Events and their descriptions
        # - Relationships between these elements
        
        # For now, return an empty universe that will be populated by the LLM
        return json.dumps({
            "elements": story_universe["elements"],
            "relationships": story_universe["relationships"]
        })
    
    except Exception as e:
        logger.error(f"Error generating universe from text: {str(e)}")
        return json.dumps({"error": str(e)})

@tool
def get_element_details(element_id: str) -> str:
    """
    Get detailed information about a specific story element.
    
    Args:
        element_id: The ID of the element to get details for
        
    Returns:
        A JSON string containing the element details and its relationships
    """
    logger.info(f"Getting details for element {element_id}")
    
    # Get the element
    element = _get_element_by_id(element_id)
    
    if not element:
        error_msg = f"Element with ID {element_id} not found"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})
    
    try:
        # Get the element's relationships
        relationships = _get_relationships_for_element(element_id)
        
        # Create the result
        result = {
            "element": element,
            "relationships": relationships
        }
        
        # Return the result as a JSON string using custom encoder
        return json.dumps(result, cls=StoryUniverseEncoder, ensure_ascii=False)
    
    except Exception as e:
        logger.error(f"Error getting element details: {str(e)}")
        return json.dumps({"error": str(e)})

@tool
def analyze_relationships(element_id: str = None) -> str:
    """
    Analyze relationships in the story universe to provide insights.
    
    Args:
        element_id: Optional ID of a specific element to analyze. If not provided,
                   analyzes the entire story universe.
        
    Returns:
        A JSON string containing relationship analysis results
    """
    logger.info(f"Analyzing relationships for {'element ' + element_id if element_id else 'entire universe'}")
    
    try:
        if element_id:
            # Get the element
            element = _get_element_by_id(element_id)
            
            if not element:
                error_msg = f"Element with ID {element_id} not found"
                logger.error(error_msg)
                return json.dumps({"error": error_msg})
            
            # Get the element's relationships
            relationships = _get_relationships_for_element(element_id)
            
            # Analyze the element's role in the story
            element_type = element.get("type", "unknown")
            element_name = element.get("name", f"{element_type} {element_id}")
            
            # Count relationship types
            relationship_counts = {}
            connected_elements = set()
            
            for rel in relationships:
                rel_type = rel.get("type", "unknown")
                relationship_counts[rel_type] = relationship_counts.get(rel_type, 0) + 1
                
                # Track connected elements
                if rel["source"] == element_id:
                    connected_elements.add(rel["target"])
                else:
                    connected_elements.add(rel["source"])
            
            # Get connected elements details
            connected_element_details = []
            for connected_id in connected_elements:
                connected_element = _get_element_by_id(connected_id)
                if connected_element:
                    connected_element_details.append({
                        "id": connected_id,
                        "type": connected_element.get("type", "unknown"),
                        "name": connected_element.get("name", f"Element {connected_id}")
                    })
            
            # Create analysis result
            analysis = {
                "element": {
                    "id": element_id,
                    "type": element_type,
                    "name": element_name
                },
                "relationship_count": len(relationships),
                "relationship_types": relationship_counts,
                "connected_elements": connected_element_details,
                "centrality": len(connected_elements),
                "insights": {
                    "role": f"This {element_type} is connected to {len(connected_elements)} other elements",
                    "significance": "High" if len(connected_elements) > 2 else "Medium" if len(connected_elements) > 0 else "Low"
                }
            }
            
            return json.dumps(analysis, cls=StoryUniverseEncoder, ensure_ascii=False)
        else:
            # Analyze the entire story universe
            elements = story_universe["elements"]
            relationships = story_universe["relationships"]
            
            # Count elements by type
            element_counts = {}
            for element_id, element in elements.items():
                element_type = element.get("type", "unknown")
                element_counts[element_type] = element_counts.get(element_type, 0) + 1
            
            # Count relationship types
            relationship_counts = {}
            for rel in relationships:
                rel_type = rel.get("type", "unknown")
                relationship_counts[rel_type] = relationship_counts.get(rel_type, 0) + 1
            
            # Calculate centrality for each element
            centrality = {}
            for element_id in elements:
                element_relationships = _get_relationships_for_element(element_id)
                centrality[element_id] = len(element_relationships)
            
            # Find most central elements
            most_central = []
            if centrality:
                max_centrality = max(centrality.values()) if centrality else 0
                most_central = [
                    {
                        "id": element_id,
                        "type": elements[element_id].get("type", "unknown"),
                        "name": elements[element_id].get("name", f"Element {element_id}"),
                        "centrality": centrality[element_id]
                    }
                    for element_id, count in centrality.items()
                    if count == max_centrality
                ]
            
            # Create analysis result
            analysis = {
                "universe_stats": {
                    "element_count": len(elements),
                    "element_types": element_counts,
                    "relationship_count": len(relationships),
                    "relationship_types": relationship_counts
                },
                "most_central_elements": most_central,
                "insights": {
                    "universe_complexity": "High" if len(relationships) > 10 else "Medium" if len(relationships) > 5 else "Low",
                    "character_driven": element_counts.get("character", 0) > element_counts.get("location", 0) + element_counts.get("event", 0),
                    "location_driven": element_counts.get("location", 0) > element_counts.get("character", 0),
                    "event_driven": element_counts.get("event", 0) > element_counts.get("character", 0)
                }
            }
            
            return json.dumps(analysis)
    
    except Exception as e:
        logger.error(f"Error analyzing relationships: {str(e)}")
        return json.dumps({"error": str(e)})

@tool
def update_element(element_id: str, updates: str) -> str:
    """
    Update a story element with new information.
    
    Args:
        element_id: The ID of the element to update
        updates: A JSON string containing the updates to apply
        
    Returns:
        A JSON string containing the updated element
    """
    logger.info(f"Updating element {element_id}")
    
    # Get the element
    element = _get_element_by_id(element_id)
    
    if not element:
        error_msg = f"Element with ID {element_id} not found"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})
    
    try:
        # Parse the updates
        updates_dict = json.loads(updates)
        
        # Apply the updates
        for key, value in updates_dict.items():
            if key != "id" and key != "type":  # Don't allow changing ID or type
                element[key] = value
        
        # Return the updated element as a JSON string
        return json.dumps(element)
    
    except json.JSONDecodeError:
        error_msg = "Invalid JSON in updates parameter"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})
    
    except Exception as e:
        logger.error(f"Error updating element: {str(e)}")
        return json.dumps({"error": str(e)})

@tool
def generate_story_universe(genre: str, num_characters: int = 3, num_locations: int = 2, num_events: int = 2) -> str:
    """
    Generate a complete story universe with multiple elements and relationships.
    
    Args:
        genre: The genre of the story (e.g., fantasy, sci-fi, mystery, romance)
        num_characters: The number of characters to generate (default: 3)
        num_locations: The number of locations to generate (default: 2)
        num_events: The number of events to generate (default: 2)
        
    Returns:
        A JSON string containing the generated story universe
    """
    logger.info(f"Generating story universe with genre: {genre}, {num_characters} characters, {num_locations} locations, {num_events} events")
    
    try:
        # Clear the existing story universe
        story_universe["elements"] = {}
        story_universe["relationships"] = []
        
        # Generate elements
        element_ids = {
            "character": [],
            "location": [],
            "event": []
        }
        
        # Generate characters
        for i in range(num_characters):
            element_id = _generate_id()
            story_universe["elements"][element_id] = {
                "id": element_id,
                "type": "character",
                "name": f"{genre.title()} Character {i+1}",
                "description": f"A unique character in this {genre} story.",
                "attributes": {
                    "genre": genre,
                    "index": i+1,
                    "created": datetime.datetime.now().isoformat()
                }
            }
            element_ids["character"].append(element_id)
        
        # Generate locations
        for i in range(num_locations):
            element_id = _generate_id()
            story_universe["elements"][element_id] = {
                "id": element_id,
                "type": "location",
                "name": f"{genre.title()} Location {i+1}",
                "description": f"A significant location in this {genre} story.",
                "attributes": {
                    "genre": genre,
                    "index": i+1,
                    "created": datetime.datetime.now().isoformat()
                }
            }
            element_ids["location"].append(element_id)
        
        # Generate events
        for i in range(num_events):
            element_id = _generate_id()
            story_universe["elements"][element_id] = {
                "id": element_id,
                "type": "event",
                "name": f"{genre.title()} Event {i+1}",
                "description": f"A key event in this {genre} story.",
                "attributes": {
                    "genre": genre,
                    "index": i+1,
                    "created": datetime.datetime.now().isoformat()
                }
            }
            element_ids["event"].append(element_id)
        
        # Generate relationships with controlled complexity
        relationships = []
        timestamp = datetime.datetime.now().isoformat()
        
        def add_relationship(source: str, target: str, rel_type: str, desc: str) -> None:
            """Helper to add a relationship with consistent structure"""
            relationships.append({
                "id": _generate_id(),
                "source": source,
                "target": target,
                "type": rel_type,
                "description": desc,
                "created": timestamp
            })
        
        # Build relationships in a controlled order
        try:
            # Character relationships
            for i in range(len(element_ids["character"]) - 1):
                add_relationship(
                    element_ids["character"][i],
                    element_ids["character"][i + 1],
                    "knows",
                    f"These characters know each other in this {genre} story."
                )
            
            # Location relationships
            if element_ids["location"]:
                loc_id = element_ids["location"][0]
                for char_id in element_ids["character"]:
                    add_relationship(
                        char_id,
                        loc_id,
                        "lives_in",
                        f"This character's primary location in the {genre} story."
                    )
            
            # Event relationships
            if element_ids["event"]:
                event_id = element_ids["event"][0]
                for char_id in element_ids["character"]:
                    add_relationship(
                        char_id,
                        event_id,
                        "participated_in",
                        f"This character was involved in this {genre} event."
                    )
            
            # Event-Location relationships
            if element_ids["event"] and element_ids["location"]:
                add_relationship(
                    element_ids["event"][0],
                    element_ids["location"][0],
                    "happened_at",
                    f"This {genre} event took place at this location."
                )
        except Exception as e:
            logger.error(f"Error generating relationships: {str(e)}")
            relationships = []  # Reset to empty list if any error occurs
        
        # Add all relationships to the universe
        story_universe["relationships"] = relationships
        
        # Validate the data structure before serializing
        elements = story_universe["elements"]
        relationships = story_universe["relationships"]
        
        # Ensure elements is a dictionary
        if not isinstance(elements, dict):
            elements = {}
        
        # Ensure relationships is a list
        if not isinstance(relationships, list):
            relationships = []
        
        # Create a clean data structure
        universe_data = {
            "elements": elements,
            "relationships": relationships
        }
        
        # Return the generated story universe using custom encoder
        return json.dumps(universe_data, cls=StoryUniverseEncoder, ensure_ascii=False, indent=None)
    
    except Exception as e:
        logger.error(f"Error generating story universe: {str(e)}")
        return json.dumps({"error": str(e)})

class StoryUniverseAgent(BaseAgent):
    """
    Story Universe Explorer agent that can generate and manage interconnected story elements.
    
    This agent provides tools for creating, exploring, and visualizing a story universe
    consisting of characters, locations, events, and their relationships.
    """
    
    def __init__(
        self,
        name: str = "story_universe_agent",
        model: Optional[LanguageModelLike] = None,
        tools: List[BaseTool] = None,
        prompt: str = None,
        description: str = None,
        type: str = "Creative",
        capabilities: List[str] = None,
        icon: str = "🌌"
    ):
        """
        Initialize a new story universe agent.
        
        Args:
            name: The name of the agent (default: "story_universe_agent")
            model: The language model to use for the agent
            tools: Optional list of additional tools
            prompt: Optional system prompt for the agent
            description: Optional description of the agent
            type: The type of agent (default: "Creative")
            capabilities: Optional list of capabilities
            icon: The icon to display for the agent (default: "🌌")
        """
        # Create the story universe tools
        story_universe_tools = [
            generate_story_element,
            create_relationship,
            get_story_universe,
            get_element_details,
            update_element,
            generate_story_universe,
            analyze_relationships,
            reset_story_universe,
            generate_universe_from_text,
            save_universe,
            load_universe
        ]
        
        # Combine with any additional tools
        all_tools = story_universe_tools + (tools or [])
        
        # Default capabilities if none provided
        if capabilities is None:
            capabilities = [
                "Story Element Generation",
                "Relationship Creation",
                "Universe Exploration",
                "Interactive Visualization"
            ]
        
        super().__init__(
            name=name,
            model=model,
            tools=all_tools,
            prompt=prompt,
            description=description or "Story Universe Explorer for generating and visualizing interconnected story elements",
            type=type,
            capabilities=capabilities,
            icon=icon
        )
        
        # Set custom view properties
        self.has_custom_view = True
        self.custom_view = {
            "name": "StoryUniverseView",
            "layout": "full",
            "capabilities": capabilities
        }
        
        logger.debug(f"Initialized story universe agent with {len(all_tools)} tools")
    
    def _get_default_prompt(self) -> str:
        """
        Get the default system prompt for the story universe agent.
        
        Returns:
            A string containing the default system prompt
        """
        return (
            "You are a Story Universe Explorer agent specialized in generating and managing "
            "interconnected story elements (characters, locations, events) and their relationships. "
            "Your primary goal is to help users create rich, coherent story universes that can be "
            "explored and visualized interactively."
            "\n\n"
            "CRITICAL: You must ALWAYS return valid JSON with the EXACT structure shown in these examples:"
            "\n\n"
            "CRITICAL JSON STRUCTURE RULES:"
            "\n\n"
            "1. Elements MUST be a dictionary with element IDs as keys:"
            "\n"
            "CORRECT:"
            '{'
            '  "elements": {'
            '    "abc123": {'
            '      "id": "abc123",'
            '      "type": "character",'
            '      "name": "Fantasy Character 1",'
            '      "description": "A brave character in this fantasy story.",'
            '      "attributes": {'
            '        "genre": "fantasy",'
            '        "index": 1,'
            '        "created": "2025-03-21T16:16:07.602055"'
            '      }'
            '    }'
            '  }'
            '}'
            "\n"
            "INCORRECT:"
            '{'
            '  "elements": {'
            '    "abc123": {...},'
            '    {"id": "def456", ...}  // WRONG: Extra braces'
            '  }'
            '}'
            "\n\n"
            "2. Relationships MUST be an array of objects:"
            "\n"
            "CORRECT:"
            '{'
            '  "relationships": ['
            '    {'
            '      "id": "xyz789",'
            '      "source": "abc123",'
            '      "target": "def456",'
            '      "type": "lives_in",'
            '      "description": "This character lives in this location.",'
            '      "created": "2025-03-21T16:16:07.602096"'
            '    }'
            '  ]'
            '}'
            "\n"
            "INCORRECT:"
            '{'
            '  "relationships": {  // WRONG: Object instead of array'
            '    "xyz789": {...}'
            '  }'
            '}'
            "\n\n"
            "3. Element structure must be exactly:"
            '{'
            '  "id": string (8 chars),'
            '  "type": "character"|"location"|"event",'
            '  "name": string (format: "[Genre] [Type] [Number]"),'
            '  "description": string (format: "A [adjective] [type] in this [genre] story."),'
            '  "attributes": {'
            '    "genre": string (lowercase),'
            '    "index": number,'
            '    "created": timestamp'
            '  }'
            '}'
            "\n\n"
            "4. Relationship structure must be exactly:"
            '{'
            '  "id": string (8 chars),'
            '  "source": string (element id),'
            '  "target": string (element id),'
            '  "type": string (from RELATIONSHIP_TYPES),'
            '  "description": string (format: "[standard description for relationship type]"),'
            '  "created": timestamp'
            '}'
            "\n\n"
            "IMPORTANT RULES:"
            "\n"
            "1. Always use double quotes for property names and string values"
            "\n"
            "2. Never use single quotes in JSON"
            "\n"
            "3. Never add extra braces or brackets"
            "\n"
            "4. Never add extra fields or nested structures"
            "\n\n"
            "IMPORTANT: When using tools, follow these rules:"
            "\n"
            "1. Return ONLY the JSON response, no additional text"
            "\n"
            "2. Never deviate from the standard formats:"
            "   - Names: '[Genre] [Type] [Number]'"
            "   - Descriptions: 'A [adjective] [type] in this [genre] story.'"
            "   - Relationships: Use standard descriptions for each type"
            "\n"
            "3. Never add creative details or variations"
            "\n"
            "4. Always use lowercase for genres and relationship types"
            "\n"
            "- generate_story_element"
            "\n"
            "- create_relationship"
            "\n"
            "- get_story_universe"
            "\n"
            "- get_element_details"
            "\n"
            "- update_element"
            "\n"
            "- generate_story_universe"
            "\n"
            "- analyze_relationships"
            "\n\n"
            "For example, if the tool returns '{\"id\": \"abc123\", \"type\": \"character\"}', "
            "your response should be exactly that JSON string, with no additional text before or after it."
            "\n\n"
            "Always follow these guidelines when generating story elements:"
            "\n"
            "1. Create rich, detailed descriptions with unique characteristics"
            "\n"
            "2. Ensure consistency with existing elements in the story universe"
            "\n"
            "3. Consider the implications of new elements on the overall narrative"
            "\n"
            "4. Provide enough detail for visualization but leave room for expansion"
            "\n"
            "5. Balance realism with creativity appropriate to the genre"
            "\n\n"
            "When generating characters, include details such as personality traits, motivations, "
            "background, appearance, and goals. For locations, describe the physical characteristics, "
            "atmosphere, history, and significance. For events, specify when and where they occurred, "
            "who was involved, what happened, and the consequences."
            "\n\n"
            "When creating relationships between elements, provide a clear description of how they "
            "are connected and why the relationship is significant to the story."
            "\n\n"
            "Remember that the story universe will be visualized as an interactive graph, so consider "
            "how elements and relationships will appear visually."
        )

def register_story_universe_agent(model: LanguageModelLike) -> StoryUniverseAgent:
    """
    Create and register a story universe agent.
    
    Args:
        model: The language model to use for the agent
        
    Returns:
        The created story universe agent
    """
    try:
        # Try importing with the full package path (for local development)
        from mosaic.backend.agents.base import agent_registry
    except ImportError:
        # Fall back to relative import (for Docker environment)
        from backend.agents.base import agent_registry
    
    story_universe = StoryUniverseAgent(model=model)
    agent_registry.register(story_universe)
    return story_universe
