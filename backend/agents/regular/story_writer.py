"""
Story_writer Agent Module for MOSAIC

A creative agent that can generate short stories based on prompts
"""

import logging
from typing import List, Dict, Any, Optional

from langchain_core.language_models import LanguageModelLike
from langchain_core.tools import BaseTool, tool

try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.agents.base import BaseAgent, agent_registry
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.agents.base import BaseAgent, agent_registry

# Import tool dependencies
from langchain.tools import tool

# Configure logging
logger = logging.getLogger("mosaic.agents.story_writer")


from langchain.tools import tool

@tool
def generate_story(prompt: str, length: str = "medium", genre: str = "general") -> dict:
    """Generate a short story based on a prompt, length, and genre."""
    # This function would typically call an LLM to generate the story
    # For now, we'll return a placeholder that explains what would happen
    
    # Determine word count based on length
    word_counts = {
        "short": "approximately 500 words",
        "medium": "approximately 1000 words",
        "long": "approximately 2000 words"
    }
    
    word_count = word_counts.get(length.lower(), "a variable length")
    
    return {
        "title": f"A {genre.title()} Story Based on '{prompt}'",
        "content": f"This would be a {word_count} story in the {genre} genre, based on the prompt: {prompt}. The story would have a clear beginning, middle, and end, with well-developed characters and engaging dialogue.",
        "metadata": {
            "prompt": prompt,
            "length": length,
            "genre": genre,
            "word_count": word_count
        }
    }

from langchain.tools import tool

@tool
def develop_character(name: str, traits: str = "", background: str = "") -> dict:
    """Develop a detailed character profile for a story."""
    # This function would typically call an LLM to generate the character profile
    # For now, we'll return a placeholder that explains what would happen
    
    traits_list = [trait.strip() for trait in traits.split(",") if trait.strip()] if traits else ["determined", "resourceful"]
    
    return {
        "name": name,
        "traits": traits_list,
        "background": background or "A mysterious past that shapes their current motivations and actions.",
        "profile": f"This would be a detailed profile for {name}, a character with traits such as {', '.join(traits_list)}. Their background would include: {background or 'A mysterious past that shapes their current motivations and actions.'}\n\nThe profile would include details about their appearance, personality, motivations, fears, desires, and how they might evolve throughout a story."
    }

from langchain.tools import tool

@tool
def create_story_outline(title: str, premise: str, num_acts: int = 3) -> dict:
    """Create a structured outline for a story with the specified number of acts."""
    # This function would typically call an LLM to generate the outline
    # For now, we'll return a placeholder that explains what would happen
    
    acts = []
    
    if num_acts == 3:
        acts = [
            {
                "name": "Act 1: Setup",
                "description": "Introduction of the main characters, setting, and the inciting incident that sets the story in motion."
            },
            {
                "name": "Act 2: Confrontation",
                "description": "The main characters face obstacles and conflicts as they pursue their goals. The stakes increase and challenges become more difficult."
            },
            {
                "name": "Act 3: Resolution",
                "description": "The climax of the story where the main conflict comes to a head, followed by the resolution and denouement."
            }
        ]
    elif num_acts == 5:
        acts = [
            {
                "name": "Act 1: Exposition",
                "description": "Introduction of the main characters, setting, and the normal world."
            },
            {
                "name": "Act 2: Rising Action",
                "description": "The inciting incident occurs and the main characters begin their journey."
            },
            {
                "name": "Act 3: Complication",
                "description": "Obstacles and conflicts intensify, raising the stakes for the main characters."
            },
            {
                "name": "Act 4: Climax",
                "description": "The main conflict comes to a head, and the main characters face their greatest challenge."
            },
            {
                "name": "Act 5: Resolution",
                "description": "The aftermath of the climax, where loose ends are tied up and the new normal is established."
            }
        ]
    else:
        acts = [{
            "name": f"Act {i+1}",
            "description": f"This would be act {i+1} of the story."
        } for i in range(num_acts)]
    
    return {
        "title": title,
        "premise": premise,
        "num_acts": num_acts,
        "acts": acts,
        "notes": f"This outline would provide a structured framework for a story titled '{title}' based on the premise: {premise}. It would include {num_acts} acts with key plot points, character development moments, and thematic elements."
    }


class StorywriterAgent(BaseAgent):
    """
    A creative agent that can generate short stories based on prompts
    """
    
    def __init__(
        self,
        name: str = "story_writer",
        model: Optional[LanguageModelLike] = None,
        tools: List[BaseTool] = None,
        prompt: str = None,
        description: str = None,
    ):
        """
        Initialize a new Story_writer agent.
        
        Args:
            name: The name of the agent (default: "story_writer")
            model: The language model to use for the agent
            tools: Optional list of additional tools
            prompt: Optional system prompt for the agent
            description: Optional description of the agent
        """
        # Define the agent's tools
        agent_tools = [
            generate_story, develop_character, create_story_outline
        ]
        
        # Combine with any additional tools
        all_tools = agent_tools + (tools or [])
        
        super().__init__(
            name=name,
            model=model,
            tools=all_tools,
            prompt=prompt,
            description=description or "A creative agent that can generate short stories based on prompts"
        )
        
        logger.debug(f"Initialized story_writer agent with {len(all_tools)} tools")
    
    def _get_default_prompt(self) -> str:
        """
        Get the default system prompt for the story_writer agent.
        
        Returns:
            A string containing the default system prompt
        """
        return """You are a creative short story writer. You can generate engaging stories based on prompts, themes, or characters provided by the user. Your stories should be well-structured with a beginning, middle, and end, and include vivid descriptions and compelling characters."""


def register_story_writer_agent(model: LanguageModelLike) -> StorywriterAgent:
    """
    Create and register a story_writer agent.
    
    Args:
        model: The language model to use for the agent
        
    Returns:
        The created story_writer agent
    """
    try:
        # Try importing with the full package path (for local development)
        from mosaic.backend.agents.base import agent_registry
    except ImportError:
        # Fall back to relative import (for Docker environment)
        from backend.agents.base import agent_registry
    
    story_writer_agent = StorywriterAgent(model=model)
    agent_registry.register(story_writer_agent)
    return story_writer_agent
