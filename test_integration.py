"""
Integration Test Script for MOSAIC

This script tests the integration between the backend and frontend components
of the MOSAIC system. It starts the backend server, makes API requests, and
verifies that the responses are correct.
"""

import os
import time
import json
import logging
import subprocess
import requests
import websocket
import threading
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("mosaic.test_integration")

# Load environment variables
load_dotenv()

# Constants
BACKEND_URL = "http://localhost:8000"
WEBSOCKET_URL = "ws://localhost:8000/ws"
BACKEND_COMMAND = ["python", "-m", "uvicorn", "mosaic.backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]

def start_backend_server():
    """Start the backend server in a separate process."""
    logger.info("Starting backend server...")
    process = subprocess.Popen(
        BACKEND_COMMAND,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    # Wait for the server to start
    time.sleep(5)
    return process

def stop_backend_server(process):
    """Stop the backend server."""
    logger.info("Stopping backend server...")
    process.terminate()
    process.wait()

def test_backend_api():
    """Test the backend API endpoints."""
    logger.info("Testing backend API endpoints...")
    
    # Test the root endpoint
    try:
        response = requests.get(f"{BACKEND_URL}/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        logger.info(f"Root endpoint test passed: {data}")
    except Exception as e:
        logger.error(f"Root endpoint test failed: {str(e)}")
        return False
    
    # Test the agents endpoint
    try:
        response = requests.get(f"{BACKEND_URL}/api/agents")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        logger.info(f"Agents endpoint test passed: {data}")
    except Exception as e:
        logger.error(f"Agents endpoint test failed: {str(e)}")
        return False
    
    # Test the debug endpoint
    try:
        response = requests.get(f"{BACKEND_URL}/api/debug/agents")
        assert response.status_code == 200
        data = response.json()
        assert "initialized_agents" in data
        assert "registry_agents" in data
        logger.info(f"Debug endpoint test passed: {data}")
    except Exception as e:
        logger.error(f"Debug endpoint test failed: {str(e)}")
        return False
    
    return True

def on_message(ws, message):
    """Handle WebSocket messages."""
    logger.info(f"Received WebSocket message: {message}")
    data = json.loads(message)
    assert "type" in data
    if data["type"] == "message":
        assert "message" in data
        message_data = data["message"]
        assert "id" in message_data
        assert "role" in message_data
        assert "content" in message_data
        assert "timestamp" in message_data
    elif data["type"] == "log_update":
        assert "log" in data
        assert "messageId" in data

def on_error(ws, error):
    """Handle WebSocket errors."""
    logger.error(f"WebSocket error: {error}")

def on_close(ws, close_status_code, close_msg):
    """Handle WebSocket connection close."""
    logger.info(f"WebSocket connection closed: {close_status_code} - {close_msg}")

def on_open(ws):
    """Handle WebSocket connection open."""
    logger.info("WebSocket connection opened")
    # Send a test message
    ws.send(json.dumps({
        "type": "message",
        "message": {
            "role": "user",
            "content": "What is 2+2?",
            "agentId": "calculator"
        }
    }))

def test_websocket():
    """Test the WebSocket connection."""
    logger.info("Testing WebSocket connection...")
    
    try:
        # Connect to the WebSocket
        ws = websocket.WebSocketApp(
            f"{WEBSOCKET_URL}/chat/calculator",
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
        )
        
        # Start the WebSocket connection in a separate thread
        wst = threading.Thread(target=ws.run_forever)
        wst.daemon = True
        wst.start()
        
        # Wait for the connection to establish
        time.sleep(2)
        
        # Close the WebSocket connection
        ws.close()
        
        logger.info("WebSocket test passed")
        return True
    except Exception as e:
        logger.error(f"WebSocket test failed: {str(e)}")
        return False

def main():
    """Run the integration tests."""
    logger.info("Starting integration tests...")
    
    # Check if the OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("Please set your OPENAI_API_KEY in the .env file")
        return
    
    # Start the backend server
    backend_process = start_backend_server()
    
    try:
        # Test the backend API
        api_test_passed = test_backend_api()
        
        # Test the WebSocket connection
        websocket_test_passed = test_websocket()
        
        # Print the test results
        logger.info("Integration test results:")
        logger.info(f"API Test: {'PASSED' if api_test_passed else 'FAILED'}")
        logger.info(f"WebSocket Test: {'PASSED' if websocket_test_passed else 'FAILED'}")
        
        if api_test_passed and websocket_test_passed:
            logger.info("All integration tests passed!")
        else:
            logger.error("Some integration tests failed.")
    
    finally:
        # Stop the backend server
        stop_backend_server(backend_process)

if __name__ == "__main__":
    main()
