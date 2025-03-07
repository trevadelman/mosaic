"""
Request Tracker Module for MOSAIC

This module provides a request tracking system for UI components.
It tracks requests and responses, handles timeouts, and provides retry logic.
"""

import logging
import asyncio
import uuid
from typing import Dict, Any, Optional, Callable, Awaitable, List, Tuple
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger("mosaic.request_tracker")

class RequestTracker:
    """
    Request tracker for UI components.
    
    This class tracks requests and responses, handles timeouts, and provides retry logic.
    It is used by the UI WebSocket handler to track requests and responses.
    """
    
    def __init__(self, default_timeout: float = 30.0, max_retries: int = 3):
        """
        Initialize the request tracker.
        
        Args:
            default_timeout: The default timeout in seconds
            max_retries: The maximum number of retries
        """
        # Track pending requests by request ID
        self.pending_requests: Dict[str, Dict[str, Any]] = {}
        
        # Track request handlers by component ID and action
        self.request_handlers: Dict[str, Dict[str, Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]]] = {}
        
        # Track request timeouts
        self.request_timeouts: Dict[str, float] = {}
        
        # Track request retries
        self.request_retries: Dict[str, int] = {}
        
        # Track request timestamps
        self.request_timestamps: Dict[str, datetime] = {}
        
        # Track request results
        self.request_results: Dict[str, Dict[str, Any]] = {}
        
        # Default timeout in seconds
        self.default_timeout = default_timeout
        
        # Maximum number of retries
        self.max_retries = max_retries
        
        # Initialize the timeout task
        self.timeout_task = None
        
        # Try to start the timeout checker task if there's a running event loop
        try:
            loop = asyncio.get_running_loop()
            self.timeout_task = asyncio.create_task(self._check_timeouts())
            logger.info("Started timeout checker task")
        except RuntimeError:
            # No running event loop, the task will be started when needed
            logger.info("No running event loop, timeout checker task will be started when needed")
        
        logger.info(f"Initialized request tracker with default timeout {default_timeout}s and max retries {max_retries}")
    
    def register_handler(self, component_id: str, action: str, handler: Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]) -> None:
        """
        Register a request handler for a component and action.
        
        Args:
            component_id: The component ID
            action: The action
            handler: The handler function
        """
        if component_id not in self.request_handlers:
            self.request_handlers[component_id] = {}
        
        self.request_handlers[component_id][action] = handler
        
        logger.info(f"Registered handler for component {component_id}, action {action}")
    
    def get_handler(self, component_id: str, action: str) -> Optional[Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]]:
        """
        Get a request handler for a component and action.
        
        Args:
            component_id: The component ID
            action: The action
            
        Returns:
            The handler function, or None if not found
        """
        if component_id in self.request_handlers:
            return self.request_handlers[component_id].get(action)
        
        return None
    
    async def track_request(self, component_id: str, action: str, data: Dict[str, Any], timeout: Optional[float] = None) -> Tuple[str, Dict[str, Any]]:
        """
        Track a request and wait for a response.
        
        Args:
            component_id: The component ID
            action: The action
            data: The request data
            timeout: Optional timeout in seconds
            
        Returns:
            A tuple of (request_id, response_data)
        """
        # Generate a request ID
        request_id = str(uuid.uuid4())
        
        # Store the request
        self.pending_requests[request_id] = {
            "component_id": component_id,
            "action": action,
            "data": data,
            "timestamp": datetime.now(),
            "status": "pending"
        }
        
        # Set the timeout
        self.request_timeouts[request_id] = timeout or self.default_timeout
        
        # Set the retry count
        self.request_retries[request_id] = 0
        
        # Set the timestamp
        self.request_timestamps[request_id] = datetime.now()
        
        # Get the handler
        handler = self.get_handler(component_id, action)
        
        if handler:
            try:
                # Call the handler with a timeout
                logger.info(f"Calling handler for request {request_id} (component {component_id}, action {action}) with timeout {self.request_timeouts[request_id]}s")
                
                try:
                    # Create a task for the handler
                    handler_task = asyncio.create_task(handler(data))
                    
                    # Wait for the handler to complete with a timeout
                    response = await asyncio.wait_for(handler_task, timeout=self.request_timeouts[request_id])
                    
                    # Store the response
                    self.request_results[request_id] = response
                    
                    # Update the request status
                    self.pending_requests[request_id]["status"] = "completed"
                    
                    # Return the response
                    return request_id, response
                
                except asyncio.TimeoutError:
                    logger.warning(f"Handler for request {request_id} timed out after {self.request_timeouts[request_id]}s")
                    
                    # Update the request status
                    self.pending_requests[request_id]["status"] = "error"
                    self.pending_requests[request_id]["error"] = f"Request timed out after {self.request_timeouts[request_id]}s"
                    
                    # Store the error response
                    self.request_results[request_id] = {
                        "error": f"Request timed out after {self.request_timeouts[request_id]}s"
                    }
                    
                    # Return the error response
                    return request_id, {
                        "error": f"Request timed out after {self.request_timeouts[request_id]}s"
                    }
            
            except Exception as e:
                logger.error(f"Error calling handler for request {request_id}: {str(e)}")
                
                # Update the request status
                self.pending_requests[request_id]["status"] = "error"
                self.pending_requests[request_id]["error"] = str(e)
                
                # Store the error response
                self.request_results[request_id] = {
                    "error": str(e)
                }
                
                # Return the error response
                return request_id, {
                    "error": str(e)
                }
        else:
            logger.warning(f"No handler found for component {component_id}, action {action}")
            
            # Update the request status
            self.pending_requests[request_id]["status"] = "error"
            self.pending_requests[request_id]["error"] = f"No handler found for component {component_id}, action {action}"
            
            # Store the error response
            self.request_results[request_id] = {
                "error": f"No handler found for component {component_id}, action {action}"
            }
            
            # Return the error response
            return request_id, {
                "error": f"No handler found for component {component_id}, action {action}"
            }
    
    async def retry_request(self, request_id: str) -> Optional[Dict[str, Any]]:
        """
        Retry a request.
        
        Args:
            request_id: The request ID
            
        Returns:
            The response data, or None if the request was not found or could not be retried
        """
        if request_id not in self.pending_requests:
            logger.warning(f"Request {request_id} not found for retry")
            return None
        
        # Get the request
        request = self.pending_requests[request_id]
        
        # Check if we've reached the maximum number of retries
        if self.request_retries[request_id] >= self.max_retries:
            logger.warning(f"Maximum retries reached for request {request_id}")
            
            # Update the request status
            request["status"] = "error"
            request["error"] = "Maximum retries reached"
            
            # Store the error response
            self.request_results[request_id] = {
                "error": "Maximum retries reached"
            }
            
            return {
                "error": "Maximum retries reached"
            }
        
        # Increment the retry count
        self.request_retries[request_id] += 1
        
        # Update the timestamp
        self.request_timestamps[request_id] = datetime.now()
        
        # Update the request status
        request["status"] = "retrying"
        
        # Get the handler
        handler = self.get_handler(request["component_id"], request["action"])
        
        if handler:
            try:
                # Call the handler
                logger.info(f"Retrying request {request_id} (component {request['component_id']}, action {request['action']}, retry {self.request_retries[request_id]})")
                response = await handler(request["data"])
                
                # Store the response
                self.request_results[request_id] = response
                
                # Update the request status
                request["status"] = "completed"
                
                # Return the response
                return response
            
            except Exception as e:
                logger.error(f"Error retrying request {request_id}: {str(e)}")
                
                # Update the request status
                request["status"] = "error"
                request["error"] = str(e)
                
                # Store the error response
                self.request_results[request_id] = {
                    "error": str(e)
                }
                
                # Return the error response
                return {
                    "error": str(e)
                }
        else:
            logger.warning(f"No handler found for component {request['component_id']}, action {request['action']}")
            
            # Update the request status
            request["status"] = "error"
            request["error"] = f"No handler found for component {request['component_id']}, action {request['action']}"
            
            # Store the error response
            self.request_results[request_id] = {
                "error": f"No handler found for component {request['component_id']}, action {request['action']}"
            }
            
            # Return the error response
            return {
                "error": f"No handler found for component {request['component_id']}, action {request['action']}"
            }
    
    def get_request(self, request_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a request by ID.
        
        Args:
            request_id: The request ID
            
        Returns:
            The request data, or None if not found
        """
        return self.pending_requests.get(request_id)
    
    def get_result(self, request_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a request result by ID.
        
        Args:
            request_id: The request ID
            
        Returns:
            The result data, or None if not found
        """
        return self.request_results.get(request_id)
    
    def get_pending_requests(self) -> List[Dict[str, Any]]:
        """
        Get all pending requests.
        
        Returns:
            A list of pending requests
        """
        return [
            {
                "request_id": request_id,
                **request
            }
            for request_id, request in self.pending_requests.items()
            if request["status"] in ["pending", "retrying"]
        ]
    
    def get_completed_requests(self) -> List[Dict[str, Any]]:
        """
        Get all completed requests.
        
        Returns:
            A list of completed requests
        """
        return [
            {
                "request_id": request_id,
                **request
            }
            for request_id, request in self.pending_requests.items()
            if request["status"] == "completed"
        ]
    
    def get_error_requests(self) -> List[Dict[str, Any]]:
        """
        Get all error requests.
        
        Returns:
            A list of error requests
        """
        return [
            {
                "request_id": request_id,
                **request
            }
            for request_id, request in self.pending_requests.items()
            if request["status"] == "error"
        ]
    
    def clear_completed_requests(self) -> None:
        """
        Clear all completed requests.
        """
        # Get all completed request IDs
        completed_request_ids = [
            request_id
            for request_id, request in self.pending_requests.items()
            if request["status"] == "completed"
        ]
        
        # Remove the requests
        for request_id in completed_request_ids:
            del self.pending_requests[request_id]
            
            # Remove from other tracking dictionaries
            if request_id in self.request_timeouts:
                del self.request_timeouts[request_id]
            
            if request_id in self.request_retries:
                del self.request_retries[request_id]
            
            if request_id in self.request_timestamps:
                del self.request_timestamps[request_id]
            
            if request_id in self.request_results:
                del self.request_results[request_id]
        
        logger.info(f"Cleared {len(completed_request_ids)} completed requests")
    
    def clear_error_requests(self) -> None:
        """
        Clear all error requests.
        """
        # Get all error request IDs
        error_request_ids = [
            request_id
            for request_id, request in self.pending_requests.items()
            if request["status"] == "error"
        ]
        
        # Remove the requests
        for request_id in error_request_ids:
            del self.pending_requests[request_id]
            
            # Remove from other tracking dictionaries
            if request_id in self.request_timeouts:
                del self.request_timeouts[request_id]
            
            if request_id in self.request_retries:
                del self.request_retries[request_id]
            
            if request_id in self.request_timestamps:
                del self.request_timestamps[request_id]
            
            if request_id in self.request_results:
                del self.request_results[request_id]
        
        logger.info(f"Cleared {len(error_request_ids)} error requests")
    
    def clear_all_requests(self) -> None:
        """
        Clear all requests.
        """
        # Clear all tracking dictionaries
        self.pending_requests.clear()
        self.request_timeouts.clear()
        self.request_retries.clear()
        self.request_timestamps.clear()
        self.request_results.clear()
        
        logger.info("Cleared all requests")
    
    async def _check_timeouts(self) -> None:
        """
        Check for timed out requests and retry them.
        """
        while True:
            try:
                # Get the current time
                now = datetime.now()
                
                # Check for timed out requests
                for request_id, timestamp in list(self.request_timestamps.items()):
                    # Skip if the request is not pending
                    if request_id not in self.pending_requests:
                        continue
                    
                    if self.pending_requests[request_id]["status"] not in ["pending", "retrying"]:
                        continue
                    
                    # Check if the request has timed out
                    timeout = self.request_timeouts.get(request_id, self.default_timeout)
                    if now - timestamp > timedelta(seconds=timeout):
                        logger.warning(f"Request {request_id} timed out after {timeout}s")
                        
                        # Retry the request
                        await self.retry_request(request_id)
                
                # Wait for a short time before checking again
                await asyncio.sleep(1)
            
            except Exception as e:
                logger.error(f"Error checking timeouts: {str(e)}")
                
                # Wait for a short time before trying again
                await asyncio.sleep(1)
    
    def close(self) -> None:
        """
        Close the request tracker.
        """
        # Cancel the timeout checker task
        if self.timeout_task:
            self.timeout_task.cancel()
        
        logger.info("Closed request tracker")

# Create a global request tracker
request_tracker = RequestTracker()
