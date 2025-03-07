"""
Stock Chart Component Module for MOSAIC

This module provides a real implementation of a stock chart component that uses
the financial_analysis agent to fetch real stock market data.
"""

import logging
import json
from typing import List, Dict, Any, Optional, Callable, Union
from datetime import datetime

# Import the base visualization component
try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.ui.components.visualization import VisualizationComponent
    from mosaic.backend.ui.base import ui_component_registry
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.ui.components.visualization import VisualizationComponent
    from backend.ui.base import ui_component_registry

# Configure logging
logger = logging.getLogger("mosaic.ui_components.stock_chart")

class StockChartComponent(VisualizationComponent):
    """
    Real implementation of a stock chart component that uses the financial_analysis agent.
    
    This component provides an interactive stock chart with real-time and historical
    stock market data. It supports multiple chart types and time ranges.
    """
    
    def __init__(self):
        """
        Initialize a new stock chart component.
        """
        super().__init__(
            component_id="stock-chart",
            name="Stock Chart",
            description="Interactive stock chart with real-time and historical data",
            required_features=["charts"],
            chart_types=["line", "bar", "candle"]
        )
        
        # Register additional handlers
        self.register_handler("change_symbol", self.handle_change_symbol)
        self.register_handler("change_range", self.handle_change_range)
        self.register_handler("get_stock_data", self.handle_get_stock_data)
        
        # Add stock-specific properties
        self.current_symbol = "AAPL"
        self.current_range = "1M"
        
        logger.info(f"Initialized stock chart component")
    
    async def handle_get_data(self, websocket: Any, event_data: Dict[str, Any], agent_id: str, client_id: str) -> Any:
        """
        Handle a request to get data for the visualization.
        
        Args:
            websocket: The WebSocket connection
            event_data: The event data
            agent_id: The ID of the agent
            client_id: The ID of the client
            
        Returns:
            The result of the handler
        """
        logger.info(f"Handling get_data request for component {self.component_id}")
        
        # Get the parameters from the event data
        params = event_data.get("data", {})
        symbol = params.get("symbol", self.current_symbol)
        range_value = params.get("range", self.current_range)
        
        # Get the stock data from the financial analysis agent
        stock_data = await self._get_stock_data_from_agent(symbol, range_value)
        
        # Send the data back to the client
        await self._send_data_response(websocket, event_data, stock_data, agent_id, client_id)
        
        return stock_data
    
    async def handle_get_stock_data(self, websocket: Any, event_data: Dict[str, Any], agent_id: str, client_id: str) -> Any:
        """
        Handle a request to get stock data.
        
        This is a specialized handler for stock data requests.
        
        Args:
            websocket: The WebSocket connection
            event_data: The event data
            agent_id: The ID of the agent
            client_id: The ID of the client
            
        Returns:
            The result of the handler
        """
        logger.info(f"Handling get_stock_data request for component {self.component_id}")
        
        # Get the parameters from the event data
        params = event_data.get("data", {})
        symbol = params.get("symbol", self.current_symbol)
        range_value = params.get("range", self.current_range)
        skip_cache = params.get("skip_cache", False)
        
        # Get the stock data from the financial analysis agent
        stock_data = await self._get_stock_data_from_agent(symbol, range_value, skip_cache)
        
        # Create the response data
        response_data = {
            "type": "data_response",
            "component": self.component_id,
            "action": "stock_data",
            "data": stock_data
        }
        
        # Send the response
        await websocket.send_json({
            "type": "ui_event",
            "data": response_data,
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"Sent stock data response for component {self.component_id}")
        
        return stock_data
    
    async def _get_stock_data_from_agent(self, symbol: str, range_value: str, skip_cache: bool = False) -> Dict[str, Any]:
        """
        Get stock data from the financial analysis agent.
        
        Args:
            symbol: The stock symbol
            range_value: The time range
            skip_cache: Whether to skip the cache
            
        Returns:
            The stock data
        """
        try:
            # Use the financial analysis agent to get stock history
            agent_id = "financial_analysis"  # The ID of the financial analysis agent
            
            # Convert range to agent period and determine interval
            period = self._convert_range_to_agent_period(range_value)
            
            # Use 15-minute intervals for 1-day charts, daily intervals for everything else
            interval = "15m" if range_value == "1D" else "1d"
            
            # Get the initialized agents
            try:
                # Try importing with the full package path (for local development)
                from mosaic.backend.app.agent_runner import get_initialized_agents
            except ImportError:
                # Fall back to relative import (for Docker environment)
                from backend.app.agent_runner import get_initialized_agents
            
            # Get the financial analysis agent
            initialized_agents = get_initialized_agents()
            agent = initialized_agents.get(agent_id)
            
            if not agent:
                raise ValueError(f"Agent '{agent_id}' not found")
            
            # Find the get_stock_history_tool
            tool = None
            for t in agent.tools:
                if t.name == "get_stock_history_tool":
                    tool = t
                    break
            
            if not tool:
                raise ValueError(f"Tool 'get_stock_history_tool' not found in agent '{agent_id}'")
            
            # Invoke the tool directly
            agent_response = tool.invoke({
                "symbol": symbol,
                "period": period,
                "interval": interval
            })
            
            # Parse the response from the agent
            # The agent returns a formatted string, so we need to parse it
            data_points = self._parse_stock_history_response(agent_response, symbol)
            
            # Create the stock data object
            stock_data = {
                "symbol": symbol,
                "range": range_value,
                "data": data_points,
                "timestamp": datetime.now().isoformat()
            }
            
            # Log the number of data points for debugging
            logger.info(f"Parsed {len(data_points)} data points for {symbol} with range {range_value}")
            
            return stock_data
        
        except Exception as e:
            logger.error(f"Error getting stock data from agent for {symbol}: {str(e)}")
            
            # Return an empty data object with an error message
            return {
                "symbol": symbol,
                "range": range_value,
                "data": [],
                "error": f"Error getting stock data: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def _convert_range_to_agent_period(self, range_value: str) -> str:
        """
        Convert a range value to a period string for the agent's get_stock_history_tool.
        
        Args:
            range_value: The range value (1D, 1W, 1M, 3M, 6M, 1Y, 5Y)
            
        Returns:
            A period string for the agent
        """
        if range_value == "1D":
            return "1d"
        elif range_value == "5D":
            return "5d"
        elif range_value == "1W":
            return "1wk"  # Add support for 1 week
        elif range_value == "1M":
            return "1mo"
        elif range_value == "3M":
            return "3mo"
        elif range_value == "6M":
            return "6mo"
        elif range_value == "1Y":
            return "1y"
        elif range_value == "5Y":
            return "5y"
        else:
            logger.warning(f"Unknown range value: {range_value}, defaulting to 1 month")
            return "1mo"  # Default to 1 month
    
    def _parse_stock_history_response(self, response: str, symbol: str) -> List[Dict[str, Any]]:
        """
        Parse the response from the agent's get_stock_history_tool.
        
        Args:
            response: The response string from the agent
            symbol: The stock symbol
            
        Returns:
            A list of data points
        """
        # The agent returns a formatted string, so we need to parse it
        # Example response:
        # Historical Stock Data for AAPL:
        #
        # Period: 1y, Interval: 1d
        # Date Range: 2024-03-07 to 2025-03-06
        #
        # Starting Price: $150.00
        # Ending Price: $180.00
        # Price Change: +$30.00 (+20.00%)
        #
        # Average Price: $165.00
        # Minimum Price: $145.00
        # Maximum Price: $190.00
        #
        # Sample of Historical Data:
        # 2025-03-02: Open $178.00, High $182.00, Low $177.00, Close $180.00, Volume 12345678
        # 2025-03-03: Open $180.00, High $185.00, Low $179.00, Close $183.00, Volume 23456789
        # ...
        
        # Initialize data points
        data_points = []
        
        try:
            # Split the response into lines
            lines = response.strip().split('\n')
            
            # Find the historical data section
            data_index = -1
            for i, line in enumerate(lines):
                if line.startswith("Historical Data:"):
                    data_index = i
                    break
            
            if data_index == -1:
                logger.warning(f"Could not find historical data section in response for {symbol}")
                return []
            
            # Parse the historical data
            for i in range(data_index + 1, len(lines)):
                line = lines[i].strip()
                if not line:
                    continue
                
                # Parse the line
                # Format: 2025-03-02: Open $178.00, High $182.00, Low $177.00, Close $180.00, Volume 12345678
                try:
                    # Split the date and data
                    date_str, data_str = line.split(':', 1)
                    date_str = date_str.strip()
                    
                    # For 15-minute intervals, the date string includes time
                    # Format: 2025-03-07 09:30:00-05:00
                    if ' ' in date_str and ':' in date_str:
                        # Extract just the date and time without timezone
                        date_parts = date_str.split(' ')
                        date = f"{date_parts[0]} {date_parts[1].split('-')[0]}"
                    else:
                        date = date_str
                    
                    # Parse the data
                    data_parts = data_str.split(',')
                    
                    # Extract values
                    open_price = float(data_parts[0].split('$')[1].strip())
                    high_price = float(data_parts[1].split('$')[1].strip())
                    low_price = float(data_parts[2].split('$')[1].strip())
                    close_price = float(data_parts[3].split('$')[1].strip())
                    volume = int(data_parts[4].split(' ')[2].strip().replace(',', ''))
                    
                    # Create a data point
                    data_point = {
                        "date": date,
                        "open": open_price,
                        "high": high_price,
                        "low": low_price,
                        "close": close_price,
                        "volume": volume
                    }
                    
                    data_points.append(data_point)
                except Exception as e:
                    logger.warning(f"Error parsing line '{line}' for {symbol}: {str(e)}")
                    continue
            
            # If we couldn't parse any sample data, try to extract the overall statistics
            if not data_points:
                # Extract starting and ending prices
                start_price = None
                end_price = None
                
                for line in lines:
                    if line.startswith("Starting Price:"):
                        try:
                            start_price = float(line.split('$')[1].split(' ')[0])
                        except:
                            pass
                    elif line.startswith("Ending Price:"):
                        try:
                            end_price = float(line.split('$')[1].split(' ')[0])
                        except:
                            pass
                
                if start_price is not None and end_price is not None:
                    # Create two data points for start and end
                    date_range = None
                    for line in lines:
                        if line.startswith("Date Range:"):
                            try:
                                date_range = line.split(':', 1)[1].strip()
                                break
                            except:
                                pass
                    
                    if date_range:
                        try:
                            start_date, end_date = date_range.split(' to ')
                            
                            # Create start data point
                            data_points.append({
                                "date": start_date,
                                "open": start_price,
                                "high": start_price,
                                "low": start_price,
                                "close": start_price,
                                "volume": 0
                            })
                            
                            # Create end data point
                            data_points.append({
                                "date": end_date,
                                "open": end_price,
                                "high": end_price,
                                "low": end_price,
                                "close": end_price,
                                "volume": 0
                            })
                        except:
                            pass
            
            return data_points
        
        except Exception as e:
            logger.error(f"Error parsing stock history response for {symbol}: {str(e)}")
            return []
    
    async def handle_change_chart_type(self, websocket: Any, event_data: Dict[str, Any], agent_id: str, client_id: str) -> Any:
        """
        Handle a request to change the chart type.
        
        Args:
            websocket: The WebSocket connection
            event_data: The event data
            agent_id: The ID of the agent
            client_id: The ID of the client
            
        Returns:
            The result of the handler
        """
        logger.info(f"Handling change_chart_type request for component {self.component_id}")
        
        # Get the chart type from the event data
        chart_type = event_data.get("data", {}).get("type")
        if not chart_type or chart_type not in self.chart_types:
            logger.warning(f"Invalid chart type: {chart_type}")
            return None
        
        # Update the current chart type
        self.current_chart_type = chart_type
        
        # Send a UI update back to the client
        update_data = {"chartType": chart_type}
        await self._send_ui_update(websocket, event_data, update_data, agent_id, client_id)
        
        return update_data
    
    async def handle_change_symbol(self, websocket: Any, event_data: Dict[str, Any], agent_id: str, client_id: str) -> Any:
        """
        Handle a request to change the stock symbol.
        
        Args:
            websocket: The WebSocket connection
            event_data: The event data
            agent_id: The ID of the agent
            client_id: The ID of the client
            
        Returns:
            The result of the handler
        """
        logger.info(f"Handling change_symbol request for component {self.component_id}")
        
        # Get the symbol from the event data
        symbol = event_data.get("data", {}).get("symbol")
        if not symbol:
            logger.warning(f"Invalid symbol: {symbol}")
            return None
        
        # Update the current symbol
        self.current_symbol = symbol
        
        # Send a UI update back to the client
        update_data = {"symbol": symbol}
        await self._send_ui_update(websocket, event_data, update_data, agent_id, client_id)
        
        # Also send new data for the new symbol
        await self.handle_get_stock_data(
            websocket, 
            {
                "action": "get_stock_data",
                "data": {
                    "symbol": symbol,
                    "range": self.current_range
                }
            }, 
            agent_id, 
            client_id
        )
        
        return update_data
    
    async def handle_change_range(self, websocket: Any, event_data: Dict[str, Any], agent_id: str, client_id: str) -> Any:
        """
        Handle a request to change the time range.
        
        Args:
            websocket: The WebSocket connection
            event_data: The event data
            agent_id: The ID of the agent
            client_id: The ID of the client
            
        Returns:
            The result of the handler
        """
        logger.info(f"Handling change_range request for component {self.component_id}")
        
        # Get the range from the event data
        range_value = event_data.get("data", {}).get("range")
        if not range_value:
            logger.warning(f"Invalid range: {range_value}")
            return None
        
        # Update the current range
        self.current_range = range_value
        
        # Send a UI update back to the client
        update_data = {"range": range_value}
        await self._send_ui_update(websocket, event_data, update_data, agent_id, client_id)
        
        # Also send new data for the new range
        await self.handle_get_stock_data(
            websocket, 
            {
                "action": "get_stock_data",
                "data": {
                    "symbol": self.current_symbol,
                    "range": range_value
                }
            }, 
            agent_id, 
            client_id
        )
        
        return update_data
    
    async def handle_export_data(self, websocket: Any, event_data: Dict[str, Any], agent_id: str, client_id: str) -> Any:
        """
        Handle a request to export data.
        
        Args:
            websocket: The WebSocket connection
            event_data: The event data
            agent_id: The ID of the agent
            client_id: The ID of the client
            
        Returns:
            The result of the handler
        """
        logger.info(f"Handling export_data request for component {self.component_id}")
        
        # Get the export format from the event data
        export_format = event_data.get("data", {}).get("format", "csv")
        
        # Get the current stock data from the agent
        stock_data = await self._get_stock_data_from_agent(self.current_symbol, self.current_range)
        
        # Format the data based on the requested format
        if export_format == "csv":
            export_data = self._format_as_csv(stock_data)
        elif export_format == "json":
            export_data = json.dumps(stock_data, indent=2)
        else:
            logger.warning(f"Unsupported export format: {export_format}")
            export_data = json.dumps(stock_data, indent=2)
        
        # Create the export response
        export_response = {
            "format": export_format,
            "data": export_data,
            "symbol": self.current_symbol,
            "range": self.current_range,
            "timestamp": datetime.now().isoformat()
        }
        
        # Send the export data back to the client
        await self._send_data_response(
            websocket, 
            event_data, 
            {"exportData": export_response}, 
            agent_id, 
            client_id
        )
        
        return export_response
    
    def _format_as_csv(self, stock_data: Dict[str, Any]) -> str:
        """
        Format stock data as CSV.
        
        Args:
            stock_data: The stock data to format
            
        Returns:
            The formatted CSV data
        """
        # Extract the data points
        data_points = stock_data.get("data", [])
        
        # Create the CSV header
        csv_lines = ["date,open,high,low,close,volume"]
        
        # Add each data point as a CSV line
        for point in data_points:
            csv_line = f"{point['date']},{point['open']},{point['high']},{point['low']},{point['close']},{point['volume']}"
            csv_lines.append(csv_line)
        
        # Join the lines with newlines
        return "\n".join(csv_lines)
    
    async def _send_data_response(self, websocket: Any, event_data: Dict[str, Any], data: Dict[str, Any], agent_id: str, client_id: str) -> None:
        """
        Send a data response to the client.
        
        Args:
            websocket: The WebSocket connection
            event_data: The original event data
            data: The data to send
            agent_id: The ID of the agent
            client_id: The ID of the client
        """
        # Create the response event
        response_event = {
            "type": "data_response",
            "component": self.component_id,
            "action": event_data.get("action", "data"),
            "data": data
        }
        
        # Send the response
        await websocket.send_json({
            "type": "ui_event",
            "data": response_event,
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"Sent data response for component {self.component_id}")
    
    async def _send_ui_update(self, websocket: Any, event_data: Dict[str, Any], update_data: Dict[str, Any], agent_id: str, client_id: str) -> None:
        """
        Send a UI update to the client.
        
        Args:
            websocket: The WebSocket connection
            event_data: The original event data
            update_data: The update data to send
            agent_id: The ID of the agent
            client_id: The ID of the client
        """
        # Create the response event
        response_event = {
            "type": "ui_update",
            "component": self.component_id,
            "action": event_data.get("action", "update"),
            "data": update_data
        }
        
        # Send the response
        await websocket.send_json({
            "type": "ui_event",
            "data": response_event,
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"Sent UI update for component {self.component_id}")


# Create and register the stock chart component
stock_chart_component = StockChartComponent()
ui_component_registry.register(stock_chart_component)

# Register the component with the financial_analysis agent if it exists
try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.agents.base import agent_registry
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.agents.base import agent_registry

# Register the component with the financial_analysis agent
if "financial_analysis" in agent_registry.list_agents():
    agent_registry.register_ui_component("financial_analysis", stock_chart_component.component_id)
    logger.info(f"Registered {stock_chart_component.name} component with financial_analysis agent")
