"""
Chart Data Generator Agent Module for MOSAIC

This module defines an agent that generates random data for various chart types.
It serves as a simple example of a specialized agent with a UI component in the MOSAIC system.
"""

import logging
import random
from typing import List, Dict, Any, Optional
import datetime

from langchain_core.language_models import LanguageModelLike
from langchain_core.tools import BaseTool, tool

try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.agents.base import BaseAgent, agent_registry
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.agents.base import BaseAgent, agent_registry

# Configure logging
logger = logging.getLogger("mosaic.agents.chart_data_generator")

# Define the tools as standalone functions
@tool
def generate_bar_chart_data(categories: Optional[List[str]] = None, min_value: int = 0, max_value: int = 100, num_categories: int = 5) -> Dict[str, Any]:
    """
    Generate random data for a bar chart.
    
    Args:
        categories: Optional list of category names. If not provided, generic categories will be used.
        min_value: Minimum value for the random data (default: 0)
        max_value: Maximum value for the random data (default: 100)
        num_categories: Number of categories to generate if categories not provided (default: 5)
        
    Returns:
        A dictionary containing the bar chart data with categories and values
    """
    logger.info(f"Generating bar chart data with {num_categories} categories")
    
    if not categories:
        categories = [f"Category {i+1}" for i in range(num_categories)]
    else:
        num_categories = len(categories)
    
    values = [random.randint(min_value, max_value) for _ in range(num_categories)]
    colors = [f"hsl({random.randint(0, 360)}, 70%, 50%)" for _ in range(num_categories)]
    
    data = {
        "type": "bar",
        "categories": categories,
        "values": values,
        "colors": colors
    }
    
    logger.info(f"Generated bar chart data with {len(categories)} categories")
    return data

@tool
def generate_line_chart_data(points: int = 20, min_value: int = 0, max_value: int = 100, num_series: int = 1, series_names: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Generate random data for a line chart.
    
    Args:
        points: Number of data points to generate (default: 20)
        min_value: Minimum value for the random data (default: 0)
        max_value: Maximum value for the random data (default: 100)
        num_series: Number of data series to generate (default: 1)
        series_names: Optional list of series names. If not provided, generic names will be used.
        
    Returns:
        A dictionary containing the line chart data with x-values and series data
    """
    logger.info(f"Generating line chart data with {points} points and {num_series} series")
    
    if not series_names:
        series_names = [f"Series {i+1}" for i in range(num_series)]
    else:
        num_series = len(series_names)
    
    # Generate dates for x-axis (last N days)
    today = datetime.datetime.now()
    dates = [(today - datetime.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(points)]
    dates.reverse()  # Oldest to newest
    
    # Generate series data
    series_data = []
    for i in range(num_series):
        # Start with a random value
        current = random.randint(min_value, max_value)
        values = [current]
        
        # Generate rest of the values with some continuity
        for _ in range(points - 1):
            change = random.randint(-10, 10)
            current = max(min_value, min(max_value, current + change))
            values.append(current)
        
        series_data.append({
            "name": series_names[i],
            "values": values,
            "color": f"hsl({random.randint(0, 360)}, 70%, 50%)"
        })
    
    data = {
        "type": "line",
        "dates": dates,
        "series": series_data
    }
    
    logger.info(f"Generated line chart data with {len(dates)} points and {len(series_data)} series")
    return data

@tool
def generate_pie_chart_data(segments: Optional[List[str]] = None, min_value: int = 10, max_value: int = 100, num_segments: int = 5) -> Dict[str, Any]:
    """
    Generate random data for a pie chart.
    
    Args:
        segments: Optional list of segment names. If not provided, generic segments will be used.
        min_value: Minimum value for the random data (default: 10)
        max_value: Maximum value for the random data (default: 100)
        num_segments: Number of segments to generate if segments not provided (default: 5)
        
    Returns:
        A dictionary containing the pie chart data with segments and values
    """
    logger.info(f"Generating pie chart data with {num_segments} segments")
    
    if not segments:
        segments = [f"Segment {i+1}" for i in range(num_segments)]
    else:
        num_segments = len(segments)
    
    values = [random.randint(min_value, max_value) for _ in range(num_segments)]
    colors = [f"hsl({random.randint(0, 360)}, 70%, 50%)" for _ in range(num_segments)]
    
    data = {
        "type": "pie",
        "segments": segments,
        "values": values,
        "colors": colors
    }
    
    logger.info(f"Generated pie chart data with {len(segments)} segments")
    return data

@tool
def generate_scatter_plot_data(points: int = 50, x_min: int = 0, x_max: int = 100, y_min: int = 0, y_max: int = 100, num_series: int = 1, series_names: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Generate random data for a scatter plot.
    
    Args:
        points: Number of data points per series to generate (default: 50)
        x_min: Minimum x-value (default: 0)
        x_max: Maximum x-value (default: 100)
        y_min: Minimum y-value (default: 0)
        y_max: Maximum y-value (default: 100)
        num_series: Number of data series to generate (default: 1)
        series_names: Optional list of series names. If not provided, generic names will be used.
        
    Returns:
        A dictionary containing the scatter plot data with series data
    """
    logger.info(f"Generating scatter plot data with {points} points and {num_series} series")
    
    if not series_names:
        series_names = [f"Series {i+1}" for i in range(num_series)]
    else:
        num_series = len(series_names)
    
    # Generate series data
    series_data = []
    for i in range(num_series):
        data_points = []
        for _ in range(points):
            x = random.uniform(x_min, x_max)
            y = random.uniform(y_min, y_max)
            data_points.append({"x": x, "y": y})
        
        series_data.append({
            "name": series_names[i],
            "data": data_points,
            "color": f"hsl({random.randint(0, 360)}, 70%, 50%)"
        })
    
    data = {
        "type": "scatter",
        "series": series_data
    }
    
    logger.info(f"Generated scatter plot data with {num_series} series of {points} points each")
    return data

class ChartDataGeneratorAgent(BaseAgent):
    """
    Chart Data Generator agent that generates random data for various chart types.
    
    This agent provides tools for generating data for bar charts, line charts, pie charts,
    and scatter plots, which can be visualized using D3.js or other charting libraries.
    """
    
    def __init__(
        self,
        name: str = "chart_data_generator",
        model: Optional[LanguageModelLike] = None,
        tools: List[BaseTool] = None,
        prompt: str = None,
        description: str = None,
        type: str = "Utility",
        capabilities: List[str] = None,
        icon: str = "📊",
    ):
        """
        Initialize a new chart data generator agent.
        
        Args:
            name: The name of the agent (default: "chart_data_generator")
            model: The language model to use for the agent
            tools: Optional list of additional tools
            prompt: Optional system prompt for the agent
            description: Optional description of the agent
            type: The type of agent (default: "Utility")
            capabilities: List of agent capabilities
            icon: Emoji icon for the agent (default: "📊")
        """
        # Create the chart data generator tools
        chart_tools = [
            generate_bar_chart_data,
            generate_line_chart_data,
            generate_pie_chart_data,
            generate_scatter_plot_data
        ]
        
        # Combine with any additional tools
        all_tools = chart_tools + (tools or [])
        
        # Default capabilities if none provided
        if capabilities is None:
            capabilities = ["Data Generation", "Chart Data", "Visualization Data"]
        
        super().__init__(
            name=name,
            model=model,
            tools=all_tools,
            prompt=prompt,
            description=description or "Chart Data Generator Agent for creating random data for various chart types",
            type=type,
            capabilities=capabilities,
            icon=icon
        )
        
        logger.debug(f"Initialized chart data generator agent with {len(all_tools)} tools")
    
    def _get_default_prompt(self) -> str:
        """
        Get the default system prompt for the chart data generator agent.
        
        Returns:
            A string containing the default system prompt
        """
        return (
            "You are a chart data generator agent that can create random data for various chart types. "
            "You have tools for generating data for bar charts, line charts, pie charts, and scatter plots. "
            "ALWAYS use the appropriate tool to generate data for the requested chart type. "
            "NEVER generate the data yourself - ALWAYS use one of the provided tools. "
            "For bar charts, use the generate_bar_chart_data tool. "
            "For line charts, use the generate_line_chart_data tool. "
            "For pie charts, use the generate_pie_chart_data tool. "
            "For scatter plots, use the generate_scatter_plot_data tool. "
            "If the user asks for a specific chart type, use the appropriate tool. "
            "If the user doesn't specify a chart type, ask them which type they want. "
            "You can customize the data by providing parameters to the tools, such as the number of categories, "
            "minimum and maximum values, number of data points, etc. "
            "Always explain what you're generating and what the data represents."
        )

# Register the chart data generator agent with the registry
def register_chart_data_generator_agent(model: LanguageModelLike) -> ChartDataGeneratorAgent:
    """
    Create and register a chart data generator agent.
    
    Args:
        model: The language model to use for the agent
        
    Returns:
        The created chart data generator agent
    """
    try:
        # Try importing with the full package path (for local development)
        from mosaic.backend.agents.base import agent_registry
    except ImportError:
        # Fall back to relative import (for Docker environment)
        from backend.agents.base import agent_registry
    
    chart_data_generator = ChartDataGeneratorAgent(model=model)
    agent_registry.register(chart_data_generator)
    
    # Register UI component for this agent
    agent_registry.register_ui_component("chart_data_generator", "chart-visualizer")
    
    return chart_data_generator
