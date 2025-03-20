"""
Story Universe Explorer Agent Module for MOSAIC

This module defines a story universe explorer agent that can generate and manage interconnected
story elements (characters, places, events) and their relationships. It provides tools for
creating, exploring, and visualizing a story universe.
"""

import logging
import json
import uuid
from typing import List, Dict, Any, Optional, Union, Tuple

from langchain_core.language_models import LanguageModelLike
from langchain_core.tools import BaseTool, tool

try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.agents.base import BaseAgent, agent_registry
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.agents.base import BaseAgent, agent_registry

# Configure logging
logger = logging.getLogger("mosaic.agents.story_universe_agent")

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

@tool
def generate_story_element(element_type: str, description: str) -> str:
    """
    Generate a new story element (character, location, or event).
    
    Args:
        element_type: The type of element to generate (character, location, or event)
        description: A brief description or requirements for the element
        
    Returns:
        A JSON string containing the generated element
    """
    logger.info(f"Generating {element_type} with description: {description}")
    
    if element_type not in ELEMENT_TYPES:
        error_msg = f"Invalid element type: {element_type}. Must be one of {ELEMENT_TYPES}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})
    
    try:
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
        
        # Return the element as a JSON string
        # Note: The actual element generation (name, description, attributes)
        # will be handled by the LLM through the agent
        return json.dumps(element)
    
    except Exception as e:
        logger.error(f"Error generating story element: {str(e)}")
        return json.dumps({"error": str(e)})

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
        
        # Return the relationship as a JSON string
        return json.dumps(relationship)
    
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
        
        # Return the story universe as a JSON string
        return json.dumps({
            "elements": story_universe["elements"],
            "relationships": story_universe["relationships"]
        })
    
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
        
        # Return the empty story universe
        return json.dumps({
            "elements": {},
            "relationships": []
        })
    
    except Exception as e:
        logger.error(f"Error resetting story universe: {str(e)}")
        return json.dumps({"error": str(e)})

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
        
        # Return the result as a JSON string
        return json.dumps(result)
    
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
            
            return json.dumps(analysis)
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
        
        # Generate characters
        character_ids = []
        for i in range(num_characters):
            character_id = _generate_id()
            character = {
                "id": character_id,
                "type": "character",
                "name": f"Character {i+1}",  # Will be filled by the LLM
                "description": f"A character in a {genre} story",  # Will be filled by the LLM
                "attributes": {},  # Will be filled by the LLM
                "created_from": f"Generated as part of a {genre} story universe"
            }
            story_universe["elements"][character_id] = character
            character_ids.append(character_id)
        
        # Generate locations
        location_ids = []
        for i in range(num_locations):
            location_id = _generate_id()
            location = {
                "id": location_id,
                "type": "location",
                "name": f"Location {i+1}",  # Will be filled by the LLM
                "description": f"A location in a {genre} story",  # Will be filled by the LLM
                "attributes": {},  # Will be filled by the LLM
                "created_from": f"Generated as part of a {genre} story universe"
            }
            story_universe["elements"][location_id] = location
            location_ids.append(location_id)
        
        # Generate events
        event_ids = []
        for i in range(num_events):
            event_id = _generate_id()
            event = {
                "id": event_id,
                "type": "event",
                "name": f"Event {i+1}",  # Will be filled by the LLM
                "description": f"An event in a {genre} story",  # Will be filled by the LLM
                "attributes": {},  # Will be filled by the LLM
                "created_from": f"Generated as part of a {genre} story universe"
            }
            story_universe["elements"][event_id] = event
            event_ids.append(event_id)
        
        # Generate relationships between characters
        for i in range(len(character_ids)):
            for j in range(i+1, len(character_ids)):
                relationship_type = RELATIONSHIP_TYPES[i % len(RELATIONSHIP_TYPES)]
                relationship = {
                    "id": _generate_id(),
                    "source": character_ids[i],
                    "target": character_ids[j],
                    "type": relationship_type,
                    "description": f"A {relationship_type} relationship"  # Will be filled by the LLM
                }
                story_universe["relationships"].append(relationship)
        
        # Generate relationships between characters and locations
        for i in range(len(character_ids)):
            for j in range(len(location_ids)):
                if i % 2 == j % 2:  # Just a simple way to not create too many relationships
                    relationship_type = "lives_in" if i % 2 == 0 else "visited"
                    relationship = {
                        "id": _generate_id(),
                        "source": character_ids[i],
                        "target": location_ids[j],
                        "type": relationship_type,
                        "description": f"A {relationship_type} relationship"  # Will be filled by the LLM
                    }
                    story_universe["relationships"].append(relationship)
        
        # Generate relationships between characters and events
        for i in range(len(character_ids)):
            for j in range(len(event_ids)):
                if i % 2 == j % 2:  # Just a simple way to not create too many relationships
                    relationship_type = "participated_in"
                    relationship = {
                        "id": _generate_id(),
                        "source": character_ids[i],
                        "target": event_ids[j],
                        "type": relationship_type,
                        "description": f"A {relationship_type} relationship"  # Will be filled by the LLM
                    }
                    story_universe["relationships"].append(relationship)
        
        # Generate relationships between events and locations
        for i in range(len(event_ids)):
            for j in range(len(location_ids)):
                if i % 2 == j % 2:  # Just a simple way to not create too many relationships
                    relationship_type = "happened_at"
                    relationship = {
                        "id": _generate_id(),
                        "source": event_ids[i],
                        "target": location_ids[j],
                        "type": relationship_type,
                        "description": f"A {relationship_type} relationship"  # Will be filled by the LLM
                    }
                    story_universe["relationships"].append(relationship)
        
        # Return the generated story universe
        return json.dumps({
            "elements": story_universe["elements"],
            "relationships": story_universe["relationships"]
        })
    
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
            generate_universe_from_text
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
            "You have tools for generating story elements, creating relationships between elements, "
            "and exploring the story universe. When asked to generate a story element, create a "
            "detailed and interesting character, location, or event that fits the user's requirements. "
            "When creating relationships, ensure they make sense in the context of the story universe."
            "\n\n"
            "IMPORTANT: When you use any of the following tools, you MUST return the JSON response directly "
            "without any additional text or explanation:"
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
