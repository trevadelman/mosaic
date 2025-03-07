"""
Data Visualization Component for MOSAIC

This module provides a UI component for creating and interacting with data visualizations.
It supports various chart types, data filtering, and export functionality.
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
logger = logging.getLogger("mosaic.ui.data_visualization")

class DataVisualizationComponent(UIComponent):
    """
    Data Visualization Component for creating and interacting with data visualizations.
    
    This component provides:
    - Multiple chart types (bar, line, pie, scatter, etc.)
    - Data filtering and transformation
    - Export functionality
    """
    
    # Supported chart types
    CHART_TYPES = ["bar", "line", "pie", "scatter", "area", "bubble", "radar", "polar", "heatmap"]
    
    def __init__(self):
        """Initialize the data visualization component."""
        super().__init__(
            component_id="data-visualization",
            name="Data Visualization",
            description="Component for creating and interacting with data visualizations",
            required_features=["charts", "data_processing"],
            default_modal_config={
                "title": "Data Visualization",
                "width": "90%",
                "height": "90%",
                "resizable": True
            }
        )
        
        # Register handlers
        self.register_handler("process_data", self.handle_process_data)
        self.register_handler("analyze_data", self.handle_analyze_data)
        self.register_handler("generate_data", self.handle_generate_data)
        self.register_handler("get_chart_data", self.handle_get_chart_data)
        self.register_handler("change_chart_type", self.handle_change_chart_type)
        self.register_handler("apply_filters", self.handle_apply_filters)
        self.register_handler("export_data", self.handle_export_data)
        self.register_handler("get_chart_types", self.handle_get_chart_types)
        
        # Initialize state
        self.current_chart_type = "bar"
        self.current_data = None
        self.current_filters = []
        
        logger.info(f"Initialized {self.name} component")
    
    async def handle_process_data(self, websocket: Any, event: Dict[str, Any], agent_id: str, client_id: str) -> None:
        """
        Handle data processing requests.
        
        Args:
            websocket: The WebSocket connection
            event: The event data
            agent_id: The agent ID
            client_id: The client ID
        """
        try:
            # Get the data and options
            data = event.get("data")
            data_format = event.get("format", "json")
            options = event.get("options", {})
            
            if not data:
                raise ValueError("Data is required")
            
            logger.info(f"Processing data with format: {data_format}")
            
            # Get the visualization data provider
            data_provider = data_provider_registry.get("visualization-data")
            
            if not data_provider:
                raise ValueError("Visualization data provider not found")
            
            # Process the data
            result = await data_provider.get_data({
                "type": "process",
                "data": data,
                "format": data_format,
                "options": options
            })
            
            # Check for errors
            if "error" in result:
                raise ValueError(result["error"])
            
            # Store the processed data
            self.current_data = result
            
            # Send the processed data back to the client
            await self._send_response(websocket, event, {
                "success": True,
                "data": result.get("data"),
                "metadata": result.get("metadata")
            })
        
        except Exception as e:
            logger.error(f"Error handling process data request: {str(e)}")
            
            # Send error response
            await self._send_response(websocket, event, {
                "success": False,
                "error": f"Error processing data: {str(e)}"
            })
    
    async def handle_analyze_data(self, websocket: Any, event: Dict[str, Any], agent_id: str, client_id: str) -> None:
        """
        Handle data analysis requests.
        
        Args:
            websocket: The WebSocket connection
            event: The event data
            agent_id: The agent ID
            client_id: The client ID
        """
        try:
            # Get the data and options
            data = event.get("data")
            data_format = event.get("format", "json")
            analysis_type = event.get("analysis", "summary")
            options = event.get("options", {})
            
            if not data:
                raise ValueError("Data is required")
            
            logger.info(f"Analyzing data with analysis type: {analysis_type}")
            
            # Get the visualization data provider
            data_provider = data_provider_registry.get("visualization-data")
            
            if not data_provider:
                raise ValueError("Visualization data provider not found")
            
            # Analyze the data
            result = await data_provider.get_data({
                "type": "analyze",
                "data": data,
                "format": data_format,
                "analysis": analysis_type,
                "options": options
            })
            
            # Check for errors
            if "error" in result:
                raise ValueError(result["error"])
            
            # Send the analysis results back to the client
            await self._send_response(websocket, event, {
                "success": True,
                "analysis": result.get("analysis"),
                "metadata": result.get("metadata")
            })
        
        except Exception as e:
            logger.error(f"Error handling analyze data request: {str(e)}")
            
            # Send error response
            await self._send_response(websocket, event, {
                "success": False,
                "error": f"Error analyzing data: {str(e)}"
            })
    
    async def handle_generate_data(self, websocket: Any, event: Dict[str, Any], agent_id: str, client_id: str) -> None:
        """
        Handle data generation requests.
        
        Args:
            websocket: The WebSocket connection
            event: The event data
            agent_id: The agent ID
            client_id: The client ID
        """
        try:
            # Get the generation parameters
            data_type = event.get("data_type", "random")
            rows = event.get("rows", 100)
            columns = event.get("columns", ["x", "y"])
            options = event.get("options", {})
            
            logger.info(f"Generating {data_type} data with {rows} rows")
            
            # Get the visualization data provider
            data_provider = data_provider_registry.get("visualization-data")
            
            if not data_provider:
                raise ValueError("Visualization data provider not found")
            
            # Generate the data
            result = await data_provider.get_data({
                "type": "generate",
                "data_type": data_type,
                "rows": rows,
                "columns": columns,
                "options": options
            })
            
            # Check for errors
            if "error" in result:
                raise ValueError(result["error"])
            
            # Store the generated data
            self.current_data = result
            
            # Send the generated data back to the client
            await self._send_response(websocket, event, {
                "success": True,
                "data": result.get("data"),
                "metadata": result.get("metadata")
            })
        
        except Exception as e:
            logger.error(f"Error handling generate data request: {str(e)}")
            
            # Send error response
            await self._send_response(websocket, event, {
                "success": False,
                "error": f"Error generating data: {str(e)}"
            })
    
    async def handle_get_chart_data(self, websocket: Any, event: Dict[str, Any], agent_id: str, client_id: str) -> None:
        """
        Handle requests for chart data.
        
        Args:
            websocket: The WebSocket connection
            event: The event data
            agent_id: The agent ID
            client_id: The client ID
        """
        try:
            # Get the data and options
            data = event.get("data") or (self.current_data.get("data") if self.current_data else None)
            chart_type = event.get("chart_type") or self.current_chart_type
            options = event.get("options", {})
            
            if not data:
                raise ValueError("Data is required")
            
            logger.info(f"Getting chart data for chart type: {chart_type}")
            
            # Format the data for the chart type
            chart_data = self._format_for_chart_type(data, chart_type, options)
            
            # Send the chart data back to the client
            await self._send_response(websocket, event, {
                "success": True,
                "chart_type": chart_type,
                "chart_data": chart_data,
                "options": options
            })
        
        except Exception as e:
            logger.error(f"Error handling get chart data request: {str(e)}")
            
            # Send error response
            await self._send_response(websocket, event, {
                "success": False,
                "error": f"Error getting chart data: {str(e)}"
            })
    
    async def handle_change_chart_type(self, websocket: Any, event: Dict[str, Any], agent_id: str, client_id: str) -> None:
        """
        Handle requests to change the chart type.
        
        Args:
            websocket: The WebSocket connection
            event: The event data
            agent_id: The agent ID
            client_id: The client ID
        """
        try:
            # Get the new chart type
            chart_type = event.get("chart_type")
            
            if not chart_type:
                raise ValueError("Chart type is required")
            
            if chart_type not in self.CHART_TYPES:
                raise ValueError(f"Unsupported chart type: {chart_type}")
            
            logger.info(f"Changing chart type to: {chart_type}")
            
            # Update the current chart type
            self.current_chart_type = chart_type
            
            # Send success response
            await self._send_response(websocket, event, {
                "success": True,
                "chart_type": chart_type
            })
            
            # If we have current data, also send updated chart data
            if self.current_data:
                # Format the data for the new chart type
                chart_data = self._format_for_chart_type(
                    self.current_data.get("data"),
                    chart_type,
                    {}
                )
                
                # Send the updated chart data
                await self._send_response(websocket, {
                    "action": "chart_data_update",
                    "requestId": event.get("requestId")
                }, {
                    "success": True,
                    "chart_type": chart_type,
                    "chart_data": chart_data
                })
        
        except Exception as e:
            logger.error(f"Error handling change chart type request: {str(e)}")
            
            # Send error response
            await self._send_response(websocket, event, {
                "success": False,
                "error": f"Error changing chart type: {str(e)}"
            })
    
    async def handle_apply_filters(self, websocket: Any, event: Dict[str, Any], agent_id: str, client_id: str) -> None:
        """
        Handle requests to apply filters to the data.
        
        Args:
            websocket: The WebSocket connection
            event: The event data
            agent_id: The agent ID
            client_id: The client ID
        """
        try:
            # Get the filters
            filters = event.get("filters", [])
            
            if not self.current_data:
                raise ValueError("No data to filter")
            
            logger.info(f"Applying {len(filters)} filters to data")
            
            # Get the visualization data provider
            data_provider = data_provider_registry.get("visualization-data")
            
            if not data_provider:
                raise ValueError("Visualization data provider not found")
            
            # Apply the filters
            result = await data_provider.get_data({
                "type": "process",
                "data": self.current_data.get("data"),
                "format": "json",
                "options": {
                    "filter": filters
                }
            })
            
            # Check for errors
            if "error" in result:
                raise ValueError(result["error"])
            
            # Update the current data
            self.current_data = result
            self.current_filters = filters
            
            # Send the filtered data back to the client
            await self._send_response(websocket, event, {
                "success": True,
                "data": result.get("data"),
                "metadata": result.get("metadata"),
                "filters": filters
            })
            
            # Also send updated chart data
            chart_data = self._format_for_chart_type(
                result.get("data"),
                self.current_chart_type,
                {}
            )
            
            # Send the updated chart data
            await self._send_response(websocket, {
                "action": "chart_data_update",
                "requestId": event.get("requestId")
            }, {
                "success": True,
                "chart_type": self.current_chart_type,
                "chart_data": chart_data
            })
        
        except Exception as e:
            logger.error(f"Error handling apply filters request: {str(e)}")
            
            # Send error response
            await self._send_response(websocket, event, {
                "success": False,
                "error": f"Error applying filters: {str(e)}"
            })
    
    async def handle_export_data(self, websocket: Any, event: Dict[str, Any], agent_id: str, client_id: str) -> None:
        """
        Handle requests to export data.
        
        Args:
            websocket: The WebSocket connection
            event: The event data
            agent_id: The agent ID
            client_id: The client ID
        """
        try:
            # Get the export format
            export_format = event.get("format", "csv")
            
            if not self.current_data:
                raise ValueError("No data to export")
            
            logger.info(f"Exporting data in {export_format} format")
            
            # Get the visualization data provider
            data_provider = data_provider_registry.get("visualization-data")
            
            if not data_provider:
                raise ValueError("Visualization data provider not found")
            
            # Convert the data to the desired format
            result = await data_provider.get_data({
                "type": "process",
                "data": self.current_data.get("data"),
                "format": "json",
                "options": {
                    "output_format": export_format
                }
            })
            
            # Check for errors
            if "error" in result:
                raise ValueError(result["error"])
            
            # Send the exported data back to the client
            await self._send_response(websocket, event, {
                "success": True,
                "format": export_format,
                "data": result.get("data"),
                "metadata": result.get("metadata")
            })
        
        except Exception as e:
            logger.error(f"Error handling export data request: {str(e)}")
            
            # Send error response
            await self._send_response(websocket, event, {
                "success": False,
                "error": f"Error exporting data: {str(e)}"
            })
    
    async def handle_get_chart_types(self, websocket: Any, event: Dict[str, Any], agent_id: str, client_id: str) -> None:
        """
        Handle requests to get available chart types.
        
        Args:
            websocket: The WebSocket connection
            event: The event data
            agent_id: The agent ID
            client_id: The client ID
        """
        try:
            logger.info("Getting available chart types")
            
            # Send the chart types back to the client
            await self._send_response(websocket, event, {
                "success": True,
                "chart_types": self.CHART_TYPES,
                "current_chart_type": self.current_chart_type
            })
        
        except Exception as e:
            logger.error(f"Error handling get chart types request: {str(e)}")
            
            # Send error response
            await self._send_response(websocket, event, {
                "success": False,
                "error": f"Error getting chart types: {str(e)}"
            })
    
    def _format_for_chart_type(self, data: Any, chart_type: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format data for a specific chart type.
        
        Args:
            data: The data to format
            chart_type: The chart type
            options: Additional options
            
        Returns:
            Formatted chart data
        """
        # For most chart types, we can use the same format
        if chart_type in ["bar", "line", "area", "radar"]:
            # These chart types expect data in the format:
            # {
            #   "labels": ["Label1", "Label2", ...],
            #   "datasets": [
            #     {
            #       "label": "Dataset 1",
            #       "data": [1, 2, 3, ...]
            #     },
            #     ...
            #   ]
            # }
            
            # If the data is already in this format, return it as is
            if isinstance(data, dict) and "labels" in data and "datasets" in data:
                return data
            
            # Otherwise, convert it to this format
            if isinstance(data, list):
                # Assume the first item has the structure we need
                if not data:
                    return {"labels": [], "datasets": []}
                
                first_item = data[0]
                
                # Get the keys
                keys = list(first_item.keys())
                
                if len(keys) < 2:
                    raise ValueError("Data must have at least two columns")
                
                # Use the first column as labels
                label_key = keys[0]
                labels = [item[label_key] for item in data]
                
                # Use the remaining columns as datasets
                datasets = []
                for key in keys[1:]:
                    datasets.append({
                        "label": key,
                        "data": [item[key] for item in data]
                    })
                
                return {
                    "labels": labels,
                    "datasets": datasets
                }
            
            else:
                raise ValueError("Unsupported data format for chart type")
        
        elif chart_type == "pie":
            # Pie charts expect data in the format:
            # {
            #   "labels": ["Label1", "Label2", ...],
            #   "datasets": [
            #     {
            #       "data": [1, 2, 3, ...]
            #     }
            #   ]
            # }
            
            # If the data is already in this format, return it as is
            if isinstance(data, dict) and "labels" in data and "datasets" in data:
                return data
            
            # Otherwise, convert it to this format
            if isinstance(data, list):
                # Assume the first item has the structure we need
                if not data:
                    return {"labels": [], "datasets": [{"data": []}]}
                
                first_item = data[0]
                
                # Get the keys
                keys = list(first_item.keys())
                
                if len(keys) < 2:
                    raise ValueError("Data must have at least two columns")
                
                # Use the first column as labels
                label_key = keys[0]
                labels = [item[label_key] for item in data]
                
                # Use the second column as data
                data_key = keys[1]
                values = [item[data_key] for item in data]
                
                return {
                    "labels": labels,
                    "datasets": [{
                        "data": values
                    }]
                }
            
            else:
                raise ValueError("Unsupported data format for chart type")
        
        elif chart_type == "scatter":
            # Scatter charts expect data in the format:
            # {
            #   "datasets": [
            #     {
            #       "label": "Dataset 1",
            #       "data": [
            #         {"x": 1, "y": 2},
            #         {"x": 2, "y": 3},
            #         ...
            #       ]
            #     },
            #     ...
            #   ]
            # }
            
            # If the data is already in this format, return it as is
            if isinstance(data, dict) and "datasets" in data:
                return data
            
            # Otherwise, convert it to this format
            if isinstance(data, list):
                # Assume the first item has the structure we need
                if not data:
                    return {"datasets": []}
                
                first_item = data[0]
                
                # Get the keys
                keys = list(first_item.keys())
                
                if len(keys) < 2:
                    raise ValueError("Data must have at least two columns")
                
                # Use the first two columns as x and y
                x_key = keys[0]
                y_key = keys[1]
                
                # Create the dataset
                dataset = {
                    "label": f"{x_key} vs {y_key}",
                    "data": [
                        {"x": item[x_key], "y": item[y_key]}
                        for item in data
                    ]
                }
                
                return {
                    "datasets": [dataset]
                }
            
            else:
                raise ValueError("Unsupported data format for chart type")
        
        elif chart_type == "bubble":
            # Bubble charts expect data in the format:
            # {
            #   "datasets": [
            #     {
            #       "label": "Dataset 1",
            #       "data": [
            #         {"x": 1, "y": 2, "r": 5},
            #         {"x": 2, "y": 3, "r": 10},
            #         ...
            #       ]
            #     },
            #     ...
            #   ]
            # }
            
            # If the data is already in this format, return it as is
            if isinstance(data, dict) and "datasets" in data:
                return data
            
            # Otherwise, convert it to this format
            if isinstance(data, list):
                # Assume the first item has the structure we need
                if not data:
                    return {"datasets": []}
                
                first_item = data[0]
                
                # Get the keys
                keys = list(first_item.keys())
                
                if len(keys) < 3:
                    raise ValueError("Data must have at least three columns")
                
                # Use the first three columns as x, y, and r
                x_key = keys[0]
                y_key = keys[1]
                r_key = keys[2]
                
                # Create the dataset
                dataset = {
                    "label": f"{x_key} vs {y_key} (size: {r_key})",
                    "data": [
                        {"x": item[x_key], "y": item[y_key], "r": item[r_key]}
                        for item in data
                    ]
                }
                
                return {
                    "datasets": [dataset]
                }
            
            else:
                raise ValueError("Unsupported data format for chart type")
        
        elif chart_type == "polar":
            # Polar charts expect data in the format:
            # {
            #   "labels": ["Label1", "Label2", ...],
            #   "datasets": [
            #     {
            #       "label": "Dataset 1",
            #       "data": [1, 2, 3, ...]
            #     },
            #     ...
            #   ]
            # }
            
            # This is the same as bar/line/area/radar, so reuse that code
            return self._format_for_chart_type(data, "bar", options)
        
        elif chart_type == "heatmap":
            # Heatmap charts expect data in the format:
            # {
            #   "labels": {
            #     "x": ["Label1", "Label2", ...],
            #     "y": ["Label1", "Label2", ...]
            #   },
            #   "data": [
            #     {"x": 0, "y": 0, "value": 1},
            #     {"x": 0, "y": 1, "value": 2},
            #     ...
            #   ]
            # }
            
            # If the data is already in this format, return it as is
            if isinstance(data, dict) and "labels" in data and "data" in data:
                return data
            
            # Otherwise, convert it to this format
            if isinstance(data, list):
                # Assume the first item has the structure we need
                if not data:
                    return {"labels": {"x": [], "y": []}, "data": []}
                
                first_item = data[0]
                
                # Get the keys
                keys = list(first_item.keys())
                
                if len(keys) < 3:
                    raise ValueError("Data must have at least three columns")
                
                # Use the first two columns as x and y labels
                x_key = keys[0]
                y_key = keys[1]
                value_key = keys[2]
                
                # Get unique x and y values
                x_values = sorted(list(set(item[x_key] for item in data)))
                y_values = sorted(list(set(item[y_key] for item in data)))
                
                # Create the heatmap data
                heatmap_data = []
                for item in data:
                    x_index = x_values.index(item[x_key])
                    y_index = y_values.index(item[y_key])
                    value = item[value_key]
                    
                    heatmap_data.append({
                        "x": x_index,
                        "y": y_index,
                        "value": value
                    })
                
                return {
                    "labels": {
                        "x": x_values,
                        "y": y_values
                    },
                    "data": heatmap_data
                }
            
            else:
                raise ValueError("Unsupported data format for chart type")
        
        else:
            raise ValueError(f"Unsupported chart type: {chart_type}")
    
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
data_visualization_component = DataVisualizationComponent()
ui_component_registry.register(data_visualization_component)

# Register the component with the data_processing agent if it exists
if "data_processing" in agent_registry.list_agents():
    agent_registry.register_ui_component("data_processing", data_visualization_component.component_id)

# Also register with the financial_analysis agent if it exists
if "financial_analysis" in agent_registry.list_agents():
    agent_registry.register_ui_component("financial_analysis", data_visualization_component.component_id)

logger.info(f"Registered {data_visualization_component.name} component with ID {data_visualization_component.component_id}")
