"""
Universal Podcaster Agent Module for MOSAIC

This module defines a podcaster agent that leverages OpenAI's text-to-speech and speech-to-text
capabilities to create podcast-style audio content. It provides tools for generating high-quality
speech using various voices and transcribing audio content.
"""

import logging
import json
import os
import time
import datetime
from typing import List, Dict, Any, Optional

from langchain_core.language_models import LanguageModelLike
from langchain_core.tools import BaseTool, tool
from openai import OpenAI

# Constants
TTS_MODEL = "gpt-4o-mini-tts"

# Get absolute path to audio output directory
try:
    # Get backend directory (go up two levels: regular -> agents -> backend)
    BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    AUDIO_OUTPUT_DIR = os.path.join(BACKEND_DIR, "audio_output")
except Exception as e:
    logger.error(f"Error setting up audio directory: {str(e)}")
    raise

try:
    from mosaic.backend.agents.base import BaseAgent, agent_registry
except ImportError:
    from backend.agents.base import BaseAgent, agent_registry

# Configure logging
logger = logging.getLogger("mosaic.agents.podcaster_agent")

# Initialize OpenAI client
client = OpenAI()

@tool
def generate_speech(text: str, voice_config: str, filename: str = "") -> str:
    """
    Generate speech using OpenAI's text-to-speech API.
    
    Args:
        text: The text to convert to speech
        voice_config: JSON string containing voice settings and instructions
        filename: Optional custom filename (without extension)
    """
    logger.info("Generating speech with OpenAI TTS")
    
    try:
        # Parse voice configuration
        config = json.loads(voice_config)
        voice = config.get("voice", "shimmer")
        instructions = config.get("instructions")
        
        # Validate voice
        if voice not in ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]:
            raise ValueError("Invalid voice selection")
        
        # Ensure output directory exists
        os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)
        
        # Generate filename
        if filename:
            # Clean filename and ensure it's safe
            safe_filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_')).strip()
            if not safe_filename:
                safe_filename = "speech"
            filename = f"{safe_filename}.mp3"
        else:
            # Use timestamp if no filename provided
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"speech_{timestamp}.mp3"
        output_path = os.path.join(AUDIO_OUTPUT_DIR, filename)
        logger.info(f"Using output path: {output_path}")
        
        # Log API call details
        logger.info(f"Making OpenAI TTS API call with voice: {voice}")
        if instructions:
            logger.info(f"Voice instructions: {instructions}")
        
        # Generate speech
        logger.info("Starting OpenAI TTS API call...")
        response = client.audio.speech.create(
            model=TTS_MODEL,
            voice=voice,
            input=text,
            instructions=instructions,
            response_format="mp3"
        )
        logger.info("OpenAI TTS API call completed successfully")
        
        # Save file and verify it exists
        logger.info("Streaming audio file to disk...")
        response.stream_to_file(output_path)
        logger.info(f"Audio file saved to: {output_path}")
        
        # Verify file exists with retries
        max_retries = 3
        retry_delay = 0.5  # seconds
        for attempt in range(max_retries):
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                if file_size > 0:
                    logger.info(f"File verified: {output_path} (size: {file_size} bytes)")
                    # Get file timestamps
                    stat = os.stat(output_path)
                    created = datetime.datetime.fromtimestamp(stat.st_ctime)
                    modified = datetime.datetime.fromtimestamp(stat.st_mtime)
                    
                    # Create response
                    result = {
                        "success": True,
                        "format": "mp3",
                        "voice": voice,
                        "file_info": {
                            "name": filename,
                            "size": file_size,
                            "created": created.isoformat(),
                            "modified": modified.isoformat(),
                            "format": "mp3",
                            "url": f"/api/audio/{filename}"
                        }
                    }
                    break
            else:
                if attempt < max_retries - 1:
                    logger.info(f"File not ready, retrying in {retry_delay}s (attempt {attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                else:
                    raise Exception("Failed to verify file exists after retries")
        
        return result
        
    except Exception as e:
        logger.error(f"Error generating speech: {str(e)}")
        return {"success": False, "error": str(e)}

@tool
def generate_content(prompt: str) -> str:
    """
    Generate text content using OpenAI's GPT model.
    
    Args:
        prompt: The prompt to generate content from
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a content writer. Create natural, conversational content that sounds good when read aloud."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error generating content: {str(e)}")
        return str(e)

@tool
def generate_voice_tone(prompt: str) -> str:
    """
    Generate voice tone description using OpenAI's GPT model.
    
    Args:
        prompt: The prompt to generate voice tone from
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a voice expert. Create brief, clear descriptions of how a voice should sound."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error generating voice tone: {str(e)}")
        return str(e)

class PodcasterAgent(BaseAgent):
    """Universal Podcaster agent for generating and transcribing audio content."""
    
    def __init__(
        self,
        name: str = "podcaster",
        model: Optional[LanguageModelLike] = None,
        tools: List[BaseTool] = None,
        prompt: str = None,
        description: str = None,
        type: str = "Audio",
        capabilities: List[str] = None,
        icon: str = "🎙️"
    ):
        # Create tools
        podcaster_tools = [generate_speech, generate_content, generate_voice_tone]
        all_tools = podcaster_tools + (tools or [])
        
        # Default capabilities
        if capabilities is None:
            capabilities = [
                "Text-to-Speech Generation",
                "Voice Customization",
                "Audio Format Control"
            ]
        
        super().__init__(
            name=name,
            model=model,
            tools=all_tools,
            prompt=prompt,
            description=description or "Universal Podcaster for generating and transcribing audio content",
            type=type,
            capabilities=capabilities,
            icon=icon
        )
        
        # Set custom view
        self.has_custom_view = True
        self.custom_view = {
            "name": "PodcasterView",
            "layout": "split",
            "capabilities": capabilities
        }
    
    def _get_default_prompt(self) -> str:
        return (
            "You are a Universal Podcaster agent specialized in generating high-quality audio content. "
            "You have two main capabilities:\n"
            "1. generate_content: Generate natural text content from a prompt\n"
            "2. generate_speech: Convert text to speech with customizable voices\n\n"
            "Available voices:\n"
            "- alloy: A versatile, balanced voice\n"
            "- echo: A deep, resonant male voice\n"
            "- fable: A warm, engaging voice\n"
            "- onyx: A deep, authoritative voice\n"
            "- nova: A bright, energetic voice\n"
            "- shimmer: A clear, professional female voice\n\n"
            "When you receive a message:\n"
            "1. If it contains text to convert to speech, use generate_speech with the specified voice settings\n"
            "2. If it's a prompt for content generation, use generate_content to create the text\n"
            "3. If it's a voice instruction, format it as a voice_config JSON\n\n"
            "Example voice_config format:\n"
            "{\n"
            '  "voice": "shimmer",\n'
            '  "instructions": "Voice: Clear and professional..."\n'
            "}\n\n"
            "IMPORTANT: Always return the raw tool result without additional formatting."
        )

def register_podcaster_agent(model: LanguageModelLike) -> PodcasterAgent:
    """Create and register a podcaster agent."""
    try:
        from mosaic.backend.agents.base import agent_registry
    except ImportError:
        from backend.agents.base import agent_registry
    
    podcaster = PodcasterAgent(model=model)
    agent_registry.register(podcaster)
    return podcaster
