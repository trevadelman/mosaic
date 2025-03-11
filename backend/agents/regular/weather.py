"""
Weather Agent Module for MOSAIC

This module defines a weather agent that provides detailed weather information
for locations using the Open-Meteo API.
"""

import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

from langchain_core.language_models import LanguageModelLike
from langchain_core.tools import BaseTool, tool

try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.agents.base import BaseAgent, agent_registry
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.agents.base import BaseAgent, agent_registry

# Configure logging
logger = logging.getLogger("mosaic.agents.weather")

# Open-Meteo API base URL
OPEN_METEO_BASE_URL = "https://api.open-meteo.com/v1"

# Weather code descriptions
WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail"
}

# Weather code to emoji mapping
WEATHER_EMOJIS = {
    0: "☀️",  # Clear sky
    1: "🌤️",  # Mainly clear
    2: "⛅",  # Partly cloudy
    3: "☁️",  # Overcast
    45: "🌫️",  # Fog
    48: "🌫️",  # Depositing rime fog
    51: "🌦️",  # Light drizzle
    53: "🌦️",  # Moderate drizzle
    55: "🌧️",  # Dense drizzle
    61: "🌧️",  # Slight rain
    63: "🌧️",  # Moderate rain
    65: "🌧️",  # Heavy rain
    71: "🌨️",  # Slight snow fall
    73: "🌨️",  # Moderate snow fall
    75: "❄️",  # Heavy snow fall
    80: "🌦️",  # Slight rain showers
    81: "🌧️",  # Moderate rain showers
    82: "⛈️",  # Violent rain showers
    85: "🌨️",  # Slight snow showers
    86: "❄️",  # Heavy snow showers
    95: "⛈️",  # Thunderstorm
    96: "⛈️",  # Thunderstorm with slight hail
    99: "⛈️"   # Thunderstorm with heavy hail
}

@tool
def search_location(query: str) -> str:
    """
    Search for a location by name and return matching results.
    
    Args:
        query: The location name to search for
        
    Returns:
        A JSON string containing matching locations with coordinates
    """
    logger.info(f"Searching for location: {query}")
    
    try:
        import requests
        search_response = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={
                "name": query,
                "count": 5,  # Get top 5 results
                "language": "en",
                "format": "json"
            },
            timeout=10
        )
        
        # Check if the search request was successful
        search_response.raise_for_status()
        
        # Parse the search response
        search_data = search_response.json()
        
        # Check if results were found
        if not search_data.get("results"):
            error_msg = f"No locations found matching '{query}'"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
        
        # Format the results
        locations = []
        for result in search_data["results"]:
            location = {
                "name": result["name"],
                "country": result.get("country", ""),
                "admin1": result.get("admin1", ""),
                "latitude": result["latitude"],
                "longitude": result["longitude"],
                "population": result.get("population", None),
                "display_name": ""
            }
            
            # Create a display name
            display_name = result["name"]
            if result.get("admin1"):
                display_name += f", {result['admin1']}"
            if result.get("country"):
                display_name += f", {result['country']}"
            location["display_name"] = display_name
            
            locations.append(location)
        
        # Create the result as a JSON string
        result = json.dumps({
            "locations": locations
        })
        
        logger.info(f"Found {len(locations)} locations matching '{query}'")
        return result
    
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP error: {str(e)}"
        logger.error(f"Error searching for location: {error_msg}")
        return json.dumps({"error": error_msg})
    
    except Exception as e:
        logger.error(f"Error searching for location: {str(e)}")
        return json.dumps({"error": str(e)})

@tool
def get_current_weather(latitude: float, longitude: float) -> str:
    """
    Get detailed current weather for specific coordinates.
    
    Args:
        latitude: The latitude coordinate
        longitude: The longitude coordinate
        
    Returns:
        A JSON string containing detailed current weather information
    """
    logger.info(f"Getting current weather for coordinates: ({latitude}, {longitude})")
    
    try:
        import requests
        
        # Try to get the location name from reverse geocoding
        try:
            search_response = requests.get(
                "https://geocoding-api.open-meteo.com/v1/reverse",
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "language": "en",
                    "format": "json"
                },
                timeout=10
            )
            
            # Check if the search request was successful
            search_response.raise_for_status()
            
            # Parse the search response
            search_data = search_response.json()
            
            # Get the location name
            location_name = "Unknown Location"
            if search_data.get("results") and len(search_data["results"]) > 0:
                result = search_data["results"][0]
                location_name = result["name"]
                if result.get("admin1"):
                    location_name += f", {result['admin1']}"
                if result.get("country"):
                    location_name += f", {result['country']}"
        except Exception as e:
            # If reverse geocoding fails, use a generic location name with coordinates
            logger.warning(f"Reverse geocoding failed: {str(e)}")
            location_name = f"Location at {latitude:.4f}, {longitude:.4f}"
        
        # Get the current weather
        weather_response = requests.get(
            f"{OPEN_METEO_BASE_URL}/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": [
                    "temperature_2m",
                    "relative_humidity_2m",
                    "apparent_temperature",
                    "is_day",
                    "precipitation",
                    "rain",
                    "showers",
                    "snowfall",
                    "weather_code",
                    "cloud_cover",
                    "pressure_msl",
                    "surface_pressure",
                    "wind_speed_10m",
                    "wind_direction_10m",
                    "wind_gusts_10m"
                ],
                "temperature_unit": "celsius",
                "wind_speed_unit": "kmh",
                "precipitation_unit": "mm",
                "timezone": "auto"
            },
            timeout=10
        )
        
        # Check if the weather request was successful
        weather_response.raise_for_status()
        
        # Parse the weather response
        weather_data = weather_response.json()
        
        # Extract the current weather
        current = weather_data["current"]
        
        # Get the weather code description and emoji
        weather_code = current["weather_code"]
        weather_description = WEATHER_CODES.get(weather_code, "Unknown")
        weather_emoji = WEATHER_EMOJIS.get(weather_code, "🌡️")
        
        # Create the result
        result = {
            "location": {
                "name": location_name,
                "coordinates": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "timezone": weather_data.get("timezone", "Unknown")
            },
            "current": {
                "temperature": {
                    "celsius": current["temperature_2m"],
                    "fahrenheit": round((current["temperature_2m"] * 9/5) + 32, 1)
                },
                "feels_like": {
                    "celsius": current["apparent_temperature"],
                    "fahrenheit": round((current["apparent_temperature"] * 9/5) + 32, 1)
                },
                "humidity": current["relative_humidity_2m"],
                "weather": {
                    "code": weather_code,
                    "description": weather_description,
                    "emoji": weather_emoji
                },
                "precipitation": {
                    "total": current["precipitation"],
                    "rain": current["rain"],
                    "showers": current["showers"],
                    "snowfall": current["snowfall"]
                },
                "cloud_cover": current["cloud_cover"],
                "pressure": {
                    "msl": current["pressure_msl"],
                    "surface": current["surface_pressure"]
                },
                "wind": {
                    "speed": {
                        "kmh": current["wind_speed_10m"],
                        "mph": round(current["wind_speed_10m"] * 0.621371, 1)
                    },
                    "direction": current["wind_direction_10m"],
                    "gusts": {
                        "kmh": current["wind_gusts_10m"],
                        "mph": round(current["wind_gusts_10m"] * 0.621371, 1)
                    }
                },
                "is_day": bool(current["is_day"]),
                "timestamp": current["time"]
            },
            "meta": {
                "source": "Open-Meteo API",
                "retrieved_at": datetime.now().isoformat()
            }
        }
        
        # Convert to JSON string
        json_result = json.dumps(result)
        
        logger.info(f"Successfully retrieved current weather for {location_name}")
        return json_result
    
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP error: {str(e)}"
        logger.error(f"Error getting current weather: {error_msg}")
        return json.dumps({"error": error_msg})
    
    except Exception as e:
        logger.error(f"Error getting current weather: {str(e)}")
        return json.dumps({"error": str(e)})

@tool
def get_weather_forecast(latitude: float, longitude: float, days: int = 5) -> str:
    """
    Get a weather forecast for specific coordinates.
    
    Args:
        latitude: The latitude coordinate
        longitude: The longitude coordinate
        days: Number of days to forecast (1-7)
        
    Returns:
        A JSON string containing the weather forecast
    """
    logger.info(f"Getting weather forecast for coordinates: ({latitude}, {longitude}), days: {days}")
    
    # Ensure days is within valid range
    days = max(1, min(7, days))
    
    try:
        import requests
        
        # Try to get the location name from reverse geocoding
        try:
            search_response = requests.get(
                "https://geocoding-api.open-meteo.com/v1/reverse",
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "language": "en",
                    "format": "json"
                },
                timeout=10
            )
            
            # Check if the search request was successful
            search_response.raise_for_status()
            
            # Parse the search response
            search_data = search_response.json()
            
            # Get the location name
            location_name = "Unknown Location"
            if search_data.get("results") and len(search_data["results"]) > 0:
                result = search_data["results"][0]
                location_name = result["name"]
                if result.get("admin1"):
                    location_name += f", {result['admin1']}"
                if result.get("country"):
                    location_name += f", {result['country']}"
        except Exception as e:
            # If reverse geocoding fails, use a generic location name with coordinates
            logger.warning(f"Reverse geocoding failed: {str(e)}")
            location_name = f"Location at {latitude:.4f}, {longitude:.4f}"
        
        # Get the weather forecast
        weather_response = requests.get(
            f"{OPEN_METEO_BASE_URL}/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "daily": [
                    "weather_code",
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "apparent_temperature_max",
                    "apparent_temperature_min",
                    "sunrise",
                    "sunset",
                    "precipitation_sum",
                    "rain_sum",
                    "showers_sum",
                    "snowfall_sum",
                    "precipitation_hours",
                    "precipitation_probability_max",
                    "wind_speed_10m_max",
                    "wind_gusts_10m_max",
                    "wind_direction_10m_dominant"
                ],
                "temperature_unit": "celsius",
                "wind_speed_unit": "kmh",
                "precipitation_unit": "mm",
                "timezone": "auto",
                "forecast_days": days
            },
            timeout=10
        )
        
        # Check if the weather request was successful
        weather_response.raise_for_status()
        
        # Parse the weather response
        weather_data = weather_response.json()
        
        # Extract the daily forecast
        daily = weather_data["daily"]
        
        # Create the forecast data
        forecast_days = []
        for i in range(len(daily["time"])):
            # Get the weather code description and emoji
            weather_code = daily["weather_code"][i]
            weather_description = WEATHER_CODES.get(weather_code, "Unknown")
            weather_emoji = WEATHER_EMOJIS.get(weather_code, "🌡️")
            
            # Create the day forecast
            day_forecast = {
                "date": daily["time"][i],
                "weather": {
                    "code": weather_code,
                    "description": weather_description,
                    "emoji": weather_emoji
                },
                "temperature": {
                    "min": {
                        "celsius": daily["temperature_2m_min"][i],
                        "fahrenheit": round((daily["temperature_2m_min"][i] * 9/5) + 32, 1)
                    },
                    "max": {
                        "celsius": daily["temperature_2m_max"][i],
                        "fahrenheit": round((daily["temperature_2m_max"][i] * 9/5) + 32, 1)
                    }
                },
                "feels_like": {
                    "min": {
                        "celsius": daily["apparent_temperature_min"][i],
                        "fahrenheit": round((daily["apparent_temperature_min"][i] * 9/5) + 32, 1)
                    },
                    "max": {
                        "celsius": daily["apparent_temperature_max"][i],
                        "fahrenheit": round((daily["apparent_temperature_max"][i] * 9/5) + 32, 1)
                    }
                },
                "sun": {
                    "sunrise": daily["sunrise"][i],
                    "sunset": daily["sunset"][i]
                },
                "precipitation": {
                    "sum": daily["precipitation_sum"][i],
                    "rain_sum": daily["rain_sum"][i],
                    "showers_sum": daily["showers_sum"][i],
                    "snowfall_sum": daily["snowfall_sum"][i],
                    "hours": daily["precipitation_hours"][i],
                    "probability": daily["precipitation_probability_max"][i]
                },
                "wind": {
                    "speed_max": {
                        "kmh": daily["wind_speed_10m_max"][i],
                        "mph": round(daily["wind_speed_10m_max"][i] * 0.621371, 1)
                    },
                    "gusts_max": {
                        "kmh": daily["wind_gusts_10m_max"][i],
                        "mph": round(daily["wind_gusts_10m_max"][i] * 0.621371, 1)
                    },
                    "direction": daily["wind_direction_10m_dominant"][i]
                }
            }
            
            forecast_days.append(day_forecast)
        
        # Create the result
        result = {
            "location": {
                "name": location_name,
                "coordinates": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "timezone": weather_data.get("timezone", "Unknown")
            },
            "forecast": {
                "days": forecast_days
            },
            "meta": {
                "source": "Open-Meteo API",
                "retrieved_at": datetime.now().isoformat()
            }
        }
        
        # Convert to JSON string
        json_result = json.dumps(result)
        
        logger.info(f"Successfully retrieved {days}-day forecast for {location_name}")
        return json_result
    
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP error: {str(e)}"
        logger.error(f"Error getting weather forecast: {error_msg}")
        return json.dumps({"error": error_msg})
    
    except Exception as e:
        logger.error(f"Error getting weather forecast: {str(e)}")
        return json.dumps({"error": str(e)})

@tool
def get_temperature(city: str) -> str:
    """
    Get the current temperature for a city.
    
    Args:
        city: The name of the city
        
    Returns:
        A JSON string containing the city name and current temperature
    """
    logger.info(f"Getting temperature for city: {city}")
    
    try:
        # Extract just the city name if the input contains commas
        # This helps when the input is a full display name like "San Diego, California, United States"
        search_query = city.split(',')[0].strip() if ',' in city else city
        
        logger.info(f"Searching for location with query: {search_query}")
        
        # Step 1: Search for the location to get coordinates
        import requests
        search_response = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={
                "name": search_query,
                "count": 1,  # Get just the top result
                "language": "en",
                "format": "json"
            },
            timeout=10
        )
        
        # Check if the search request was successful
        search_response.raise_for_status()
        
        # Parse the search response
        search_data = search_response.json()
        
        # Check if results were found
        if not search_data.get("results"):
            error_msg = f"No location found matching '{city}'"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
        
        # Get the first result
        result = search_data["results"][0]
        latitude = result["latitude"]
        longitude = result["longitude"]
        
        # Format the city name
        city_name = result["name"]
        if result.get("admin1"):
            city_name += f", {result['admin1']}"
        if result.get("country"):
            city_name += f", {result['country']}"
        
        logger.info(f"Found location: {city_name} ({latitude}, {longitude})")
        
        # Step 2: Get the current weather for the coordinates
        weather_response = requests.get(
            f"{OPEN_METEO_BASE_URL}/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m",
                "temperature_unit": "celsius",
                "timezone": "auto"
            },
            timeout=10
        )
        
        # Check if the weather request was successful
        weather_response.raise_for_status()
        
        # Parse the weather response
        weather_data = weather_response.json()
        
        # Extract the current temperature
        temperature = weather_data["current"]["temperature_2m"]
        
        # Create the result as a JSON string
        result = json.dumps({
            "city": city_name,
            "temperature_celsius": temperature
        })
        
        logger.info(f"Successfully retrieved temperature for {city_name}: {temperature}°C")
        return result
    
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP error: {str(e)}"
        logger.error(f"Error getting temperature: {error_msg}")
        return json.dumps({"error": error_msg})
    
    except Exception as e:
        logger.error(f"Error getting temperature: {str(e)}")
        return json.dumps({"error": str(e)})

class WeatherAgent(BaseAgent):
    """
    Weather agent that provides detailed weather information for locations.
    """
    
    def __init__(
        self,
        name: str = "weather",
        model: Optional[LanguageModelLike] = None,
        tools: List[BaseTool] = None,
        prompt: str = None,
        description: str = None,
        type: str = "Specialized",
        capabilities: List[str] = None,
        icon: str = "🌦️",
    ):
        """Initialize a new weather agent."""
        # Create the weather tools
        weather_tools = [
            search_location,
            get_current_weather,
            get_weather_forecast,
            get_temperature
        ]
        
        # Combine with any additional tools
        all_tools = weather_tools + (tools or [])
        
        # Default capabilities if none provided
        if capabilities is None:
            capabilities = [
                "Location Search",
                "Current Weather",
                "Weather Forecasts",
                "Temperature Information"
            ]
        
        # Set stateless mode to true to avoid loading previous conversations
        self.stateless = True
        
        super().__init__(
            name=name,
            model=model,
            tools=all_tools,
            prompt=prompt,
            description=description or "Weather Agent for providing detailed weather information",
            type=type,
            capabilities=capabilities,
            icon=icon
        )
        
        # Set custom view properties after initialization
        self.has_custom_view = True
        self.custom_view = {
            "name": "WeatherView",
            "layout": "full",
            "capabilities": capabilities
        }
        
        logger.debug(f"Initialized weather agent with {len(all_tools)} tools")
    
    def _get_default_prompt(self) -> str:
        """Get the default system prompt for the weather agent."""
        return (
            "You are a weather assistant that provides detailed weather information. "
            "Your job is to help users get weather information for any location they ask about. "
            "\n\n"
            "You have the following tools available:"
            "\n"
            "- search_location: Search for a location by name and return matching results."
            "\n"
            "- get_current_weather: Get detailed current weather for specific coordinates."
            "\n"
            "- get_weather_forecast: Get a weather forecast for specific coordinates."
            "\n"
            "- get_temperature: Get the current temperature for a city."
            "\n\n"
            "Important guidelines:"
            "\n"
            "- Always use the appropriate tool to get weather information. Never make up data."
            "\n"
            "- If a user asks about weather without specifying a location, ask them to provide a location name."
            "\n"
            "- If the tool returns an error, explain the issue clearly and suggest alternatives."
            "\n"
            "- If a user asks for the temperature of a city, use the get_temperature tool."
            "\n"
            "- If a user asks for detailed current weather, use search_location to find the coordinates, then use get_current_weather."
            "\n"
            "- If a user asks for a forecast, use search_location to find the coordinates, then use get_weather_forecast."
            "\n\n"
            "IMPORTANT: When you receive a JSON response from any tool, return it directly to the user without any additional text. "
            "Do not add any explanations, formatting, or other text. Just return the JSON object exactly as it is."
            "\n\n"
            "Example:"
            "\n"
            "User: What's the temperature in New York?"
            "\n"
            "You: {\"city\": \"New York, New York, United States\", \"temperature_celsius\": 22.5}"
            "\n\n"
            "Do not include any other text in your response, just the JSON object."
        )
    
    def invoke(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Override the invoke method to create a stateless agent that doesn't load previous conversations.
        Also intercept tool results to ensure structured output.
        
        Args:
            state: The current state of the conversation
            
        Returns:
            The updated state with the agent's response
        """
        # Extract just the last message from the state
        messages = state.get("messages", [])
        if messages:
            last_message = messages[-1]
            # Create a new state with just the last message
            new_state = {"messages": [last_message]}
        else:
            new_state = {"messages": []}
        
        # Call the parent invoke method with the new state
        result = super().invoke(new_state)
        
        # Extract the tool result from the messages
        for message in result.get("messages", []):
            if hasattr(message, "type") and message.type == "tool" and hasattr(message, "name") and hasattr(message, "result"):
                tool_name = message.name
                tool_result = message.result
                
                # Replace the last AI message with the tool result
                for i in range(len(result["messages"]) - 1, -1, -1):
                    if hasattr(result["messages"][i], "type") and result["messages"][i].type == "ai":
                        result["messages"][i].content = tool_result
                        logger.info(f"Replaced AI message with {tool_name} tool result")
                        break
                
                break
        
        return result

def register_weather_agent(model: LanguageModelLike) -> WeatherAgent:
    """
    Create and register a weather agent.
    
    Args:
        model: The language model to use for the agent
        
    Returns:
        The created weather agent
    """
    try:
        # Try importing with the full package path (for local development)
        from mosaic.backend.agents.base import agent_registry
    except ImportError:
        # Fall back to relative import (for Docker environment)
        from backend.agents.base import agent_registry
    
    weather_agent = WeatherAgent(model=model)
    agent_registry.register(weather_agent)
    return weather_agent
