"""
UI WebSocket Handler Module for MOSAIC

This module handles WebSocket connections for custom UI components.
It provides a way for the frontend to communicate with the backend for custom UI events.
"""

import logging
import json
import asyncio
from typing import Dict, List, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime
import uuid

# Configure logging
logger = logging.getLogger("mosaic.ui_websocket_handler")

# UI WebSocket connection manager
class UIConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.component_connections: Dict[str, Dict[str, WebSocket]] = {}

    async def connect(self, websocket: WebSocket, client_id: str, agent_id: str):
        """
        Connect a client to the UI WebSocket.
        
        Args:
            websocket: The WebSocket connection
            client_id: The client ID
            agent_id: The agent ID
        """
        await websocket.accept()
        
        # Add to active connections
        if agent_id not in self.active_connections:
            self.active_connections[agent_id] = []
        self.active_connections[agent_id].append(websocket)
        
        # Add to component connections
        if agent_id not in self.component_connections:
            self.component_connections[agent_id] = {}
        self.component_connections[agent_id][client_id] = websocket
        
        logger.info(f"Client {client_id} connected to UI WebSocket for agent {agent_id}")

    def disconnect(self, websocket: WebSocket, client_id: str, agent_id: str):
        """
        Disconnect a client from the UI WebSocket.
        
        Args:
            websocket: The WebSocket connection
            client_id: The client ID
            agent_id: The agent ID
        """
        # Remove from active connections
        if agent_id in self.active_connections:
            if websocket in self.active_connections[agent_id]:
                self.active_connections[agent_id].remove(websocket)
        
        # Remove from component connections
        if agent_id in self.component_connections:
            if client_id in self.component_connections[agent_id]:
                del self.component_connections[agent_id][client_id]
        
        logger.info(f"Client {client_id} disconnected from UI WebSocket for agent {agent_id}")

    async def send_ui_event(self, event: Dict[str, Any], agent_id: str, client_id: Optional[str] = None):
        """
        Send a UI event to a client or all clients for an agent.
        
        Args:
            event: The UI event to send
            agent_id: The agent ID
            client_id: Optional client ID to send to a specific client
        """
        if agent_id in self.active_connections:
            if client_id and agent_id in self.component_connections and client_id in self.component_connections[agent_id]:
                # Send to a specific client
                websocket = self.component_connections[agent_id][client_id]
                await websocket.send_json({
                    "type": "ui_event",
                    "data": event,
                    "timestamp": datetime.now().isoformat()
                })
                logger.info(f"Sent UI event to client {client_id} for agent {agent_id}")
            else:
                # Send to all clients for this agent
                for websocket in self.active_connections[agent_id]:
                    await websocket.send_json({
                        "type": "ui_event",
                        "data": event,
                        "timestamp": datetime.now().isoformat()
                    })
                logger.info(f"Sent UI event to all clients for agent {agent_id}")

    async def send_component_registrations(self, registrations: List[Dict[str, Any]], agent_id: str, client_id: Optional[str] = None):
        """
        Send component registrations to a client or all clients for an agent.
        
        Args:
            registrations: The component registrations to send
            agent_id: The agent ID
            client_id: Optional client ID to send to a specific client
        """
        if agent_id in self.active_connections:
            if client_id and agent_id in self.component_connections and client_id in self.component_connections[agent_id]:
                # Send to a specific client
                websocket = self.component_connections[agent_id][client_id]
                await websocket.send_json({
                    "type": "component_registrations",
                    "data": {
                        "registrations": registrations
                    },
                    "timestamp": datetime.now().isoformat()
                })
                logger.info(f"Sent component registrations to client {client_id} for agent {agent_id}")
            else:
                # Send to all clients for this agent
                for websocket in self.active_connections[agent_id]:
                    await websocket.send_json({
                        "type": "component_registrations",
                        "data": {
                            "registrations": registrations
                        },
                        "timestamp": datetime.now().isoformat()
                    })
                logger.info(f"Sent component registrations to all clients for agent {agent_id}")

# Create a global UI connection manager
ui_manager = UIConnectionManager()

# Mock component registrations for testing
MOCK_COMPONENT_REGISTRATIONS = {
    "financial_supervisor": [
        {
            "id": "stock-chart",
            "name": "Stock Chart",
            "description": "Interactive stock chart with technical indicators",
            "agentId": "financial_supervisor",
            "requiredFeatures": ["charts"],
            "defaultModalConfig": {
                "size": "large",
                "panels": ["chart", "controls"],
                "features": ["zoom", "pan", "export"],
                "closable": True
            }
        }
    ]
}

# WebSocket handler for UI events
async def handle_ui_websocket(websocket: WebSocket, agent_id: str):
    """
    Handle WebSocket connections for UI events.
    
    Args:
        websocket: The WebSocket connection
        agent_id: The agent ID
    """
    client_id = str(uuid.uuid4())
    
    try:
        await ui_manager.connect(websocket, client_id, agent_id)
        
        # Send component registrations for this agent
        if agent_id in MOCK_COMPONENT_REGISTRATIONS:
            await ui_manager.send_component_registrations(
                MOCK_COMPONENT_REGISTRATIONS[agent_id],
                agent_id,
                client_id
            )
        
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "ping":
                # Respond to ping with a pong to keep the connection alive
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                })
                continue
            
            elif data.get("type") == "ui_event":
                # Process UI event
                event_data = data.get("data", {})
                
                # Log the event
                logger.info(f"Received UI event from client {client_id} for agent {agent_id}: {event_data.get('type')} - {event_data.get('action')}")
                
                # Handle different event types
                if event_data.get("type") == "data_request":
                    # Handle data request
                    component = event_data.get("component")
                    action = event_data.get("action")
                    request_data = event_data.get("data", {})
                    
                    # Process the data request
                    if component == "stock-chart" and action == "get_stock_data":
                        # Get the stock symbol and range
                        symbol = request_data.get("symbol", "AAPL")
                        range_value = request_data.get("range", "1M")
                        
                        # Get real stock data using yfinance
                        try:
                            # Import yfinance
                            import yfinance as yf
                            
                            # Convert range to yfinance period and interval
                            period, interval = convert_range_to_yfinance(range_value)
                            
                            # Get the stock data
                            logger.info(f"Getting stock data for {symbol} with period {period} and interval {interval}")
                            stock_data = get_stock_data(symbol, period, interval)
                            
                            # Send the response
                            await ui_manager.send_ui_event({
                                "type": "data_response",
                                "component": component,
                                "action": "stock_data",
                                "data": {
                                    "symbol": symbol,
                                    "range": range_value,
                                    "data": stock_data
                                }
                            }, agent_id, client_id)
                            
                            logger.info(f"Sent real stock data for {symbol} with range {range_value}")
                        except Exception as e:
                            logger.error(f"Error getting stock data: {str(e)}")
                            
                            # Fall back to mock data if there's an error
                            await ui_manager.send_ui_event({
                                "type": "data_response",
                                "component": component,
                                "action": "stock_data",
                                "data": {
                                    "symbol": symbol,
                                    "range": range_value,
                                    "data": generate_mock_stock_data(symbol, range_value)
                                }
                            }, agent_id, client_id)
                            
                            logger.info(f"Sent mock stock data for {symbol} with range {range_value} (fallback)")
                
                elif event_data.get("type") == "user_action":
                    # Handle user action
                    component = event_data.get("component")
                    action = event_data.get("action")
                    action_data = event_data.get("data", {})
                    
                    # Process the user action
                    if component == "stock-chart":
                        if action == "open":
                            # User opened the stock chart
                            logger.info(f"User opened stock chart for {action_data.get('symbol', 'AAPL')}")
                        
                        elif action == "close":
                            # User closed the stock chart
                            logger.info(f"User closed stock chart")
                        
                        elif action == "change_range":
                            # User changed the time range
                            symbol = action_data.get("symbol", "AAPL")
                            range_value = action_data.get("range", "1M")
                            logger.info(f"User changed time range to {range_value} for {symbol}")
                            
                            # Get real stock data using yfinance
                            try:
                                # Import yfinance
                                import yfinance as yf
                                
                                # Convert range to yfinance period and interval
                                period, interval = convert_range_to_yfinance(range_value)
                                
                                # Get the stock data
                                logger.info(f"Getting stock data for {symbol} with period {period} and interval {interval}")
                                stock_data = get_stock_data(symbol, period, interval)
                                
                                # Send the response
                                await ui_manager.send_ui_event({
                                    "type": "data_response",
                                    "component": component,
                                    "action": "stock_data",
                                    "data": {
                                        "symbol": symbol,
                                        "range": range_value,
                                        "data": stock_data
                                    }
                                }, agent_id, client_id)
                                
                                logger.info(f"Sent real stock data for {symbol} with range {range_value}")
                            except Exception as e:
                                logger.error(f"Error getting stock data: {str(e)}")
                                
                                # Fall back to mock data if there's an error
                                await ui_manager.send_ui_event({
                                    "type": "data_response",
                                    "component": component,
                                    "action": "stock_data",
                                    "data": {
                                        "symbol": symbol,
                                        "range": range_value,
                                        "data": generate_mock_stock_data(symbol, range_value)
                                    }
                                }, agent_id, client_id)
                                
                                logger.info(f"Sent mock stock data for {symbol} with range {range_value} (fallback)")
                        
                        elif action == "change_symbol":
                            # User changed the stock symbol
                            symbol = action_data.get("symbol", "AAPL")
                            range_value = action_data.get("range", "1M")
                            logger.info(f"User changed symbol to {symbol} with range {range_value}")
                            
                            # Get real stock data using yfinance
                            try:
                                # Import yfinance
                                import yfinance as yf
                                
                                # Convert range to yfinance period and interval
                                period, interval = convert_range_to_yfinance(range_value)
                                
                                # Get the stock data
                                logger.info(f"Getting stock data for {symbol} with period {period} and interval {interval}")
                                stock_data = get_stock_data(symbol, period, interval)
                                
                                # Send the response
                                await ui_manager.send_ui_event({
                                    "type": "data_response",
                                    "component": component,
                                    "action": "stock_data",
                                    "data": {
                                        "symbol": symbol,
                                        "range": range_value,
                                        "data": stock_data
                                    }
                                }, agent_id, client_id)
                                
                                logger.info(f"Sent real stock data for {symbol} with range {range_value}")
                            except Exception as e:
                                logger.error(f"Error getting stock data: {str(e)}")
                                
                                # Fall back to mock data if there's an error
                                await ui_manager.send_ui_event({
                                    "type": "data_response",
                                    "component": component,
                                    "action": "stock_data",
                                    "data": {
                                        "symbol": symbol,
                                        "range": range_value,
                                        "data": generate_mock_stock_data(symbol, range_value)
                                    }
                                }, agent_id, client_id)
                                
                                logger.info(f"Sent mock stock data for {symbol} with range {range_value} (fallback)")
                        
                        elif action == "change_type":
                            # User changed the chart type
                            logger.info(f"User changed chart type to {action_data.get('type', 'line')}")
                
                # Echo the event back to the client for testing
                await websocket.send_json({
                    "type": "ui_event_received",
                    "data": event_data,
                    "timestamp": datetime.now().isoformat()
                })
            
            elif data.get("type") == "get_component_registrations":
                # Send component registrations for this agent
                if agent_id in MOCK_COMPONENT_REGISTRATIONS:
                    await ui_manager.send_component_registrations(
                        MOCK_COMPONENT_REGISTRATIONS[agent_id],
                        agent_id,
                        client_id
                    )
                else:
                    await ui_manager.send_component_registrations([], agent_id, client_id)
    
    except WebSocketDisconnect:
        ui_manager.disconnect(websocket, client_id, agent_id)
        logger.info(f"Client {client_id} disconnected from UI WebSocket for agent {agent_id}")
    
    except Exception as e:
        logger.error(f"Error in UI WebSocket handler: {str(e)}")
        ui_manager.disconnect(websocket, client_id, agent_id)

# Helper function to convert range to yfinance period and interval
def convert_range_to_yfinance(range_value: str) -> tuple:
    """
    Convert a range value to yfinance period and interval.
    
    Args:
        range_value: The range value (1D, 1W, 1M, 3M, 1Y, 5Y)
        
    Returns:
        A tuple of (period, interval)
    """
    if range_value == "1D":
        return "1d", "5m"
    elif range_value == "1W":
        return "1wk", "1h"
    elif range_value == "1M":
        return "1mo", "1d"
    elif range_value == "3M":
        return "3mo", "1d"
    elif range_value == "1Y":
        return "1y", "1d"
    elif range_value == "5Y":
        return "5y", "1wk"
    else:
        return "1mo", "1d"  # Default to 1 month with daily intervals

# Helper function to get stock data from yfinance
def get_stock_data(symbol: str, period: str, interval: str) -> List[Dict[str, Any]]:
    """
    Get stock data from yfinance.
    
    Args:
        symbol: The stock symbol
        period: The period (1d, 1wk, 1mo, 3mo, 1y, 5y)
        interval: The interval (5m, 1h, 1d, 1wk)
        
    Returns:
        A list of stock data points
    """
    import yfinance as yf
    
    # Get the stock data
    ticker = yf.Ticker(symbol)
    history = ticker.history(period=period, interval=interval)
    
    # Convert to list of dictionaries
    data = []
    for date, row in history.iterrows():
        data.append({
            "date": date.strftime("%Y-%m-%d"),
            "open": round(float(row["Open"]), 2),
            "high": round(float(row["High"]), 2),
            "low": round(float(row["Low"]), 2),
            "close": round(float(row["Close"]), 2),
            "volume": int(row["Volume"])
        })
    
    return data

# Helper function to generate mock stock data
def generate_mock_stock_data(symbol: str, range_value: str) -> List[Dict[str, Any]]:
    """
    Generate mock stock data for testing.
    
    Args:
        symbol: The stock symbol
        range_value: The time range
        
    Returns:
        A list of stock data points
    """
    import random
    from datetime import datetime, timedelta
    
    # Determine the number of data points based on the range
    if range_value == "1D":
        days = 1
        interval = timedelta(minutes=5)
        data_points = 78  # 6.5 hours of trading, 5-minute intervals
    elif range_value == "1W":
        days = 7
        interval = timedelta(hours=1)
        data_points = 7 * 7  # 7 days, 7 hours per day
    elif range_value == "1M":
        days = 30
        interval = timedelta(days=1)
        data_points = 30
    elif range_value == "3M":
        days = 90
        interval = timedelta(days=1)
        data_points = 90
    elif range_value == "1Y":
        days = 365
        interval = timedelta(days=1)
        data_points = 365
    elif range_value == "5Y":
        days = 365 * 5
        interval = timedelta(days=7)
        data_points = 365 * 5 // 7
    else:
        days = 30
        interval = timedelta(days=1)
        data_points = 30
    
    # Generate random stock data
    data = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Set a base price based on the symbol
    if symbol == "AAPL":
        base_price = 150.0
    elif symbol == "MSFT":
        base_price = 300.0
    elif symbol == "GOOGL":
        base_price = 120.0
    else:
        base_price = 100.0
    
    # Generate data points
    price = base_price
    for i in range(data_points):
        date = start_date + interval * i
        
        # Random price movement
        change = (random.random() - 0.5) * 5
        price += change
        
        # Ensure price doesn't go below 50
        price = max(50, price)
        
        # Generate OHLC data
        open_price = price
        high = price + random.random() * 3
        low = price - random.random() * 3
        close = price + (random.random() - 0.5) * 2
        
        # Generate volume data
        volume = int(random.random() * 1000000) + 500000
        
        data.append({
            "date": date.strftime("%Y-%m-%d"),
            "open": round(open_price, 2),
            "high": round(high, 2),
            "low": round(low, 2),
            "close": round(close, 2),
            "volume": volume
        })
    
    return data
