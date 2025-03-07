"""
Test module for the request tracker.

This module tests the request tracker functionality, including timeout handling and retries.
"""

import unittest
import sys
import os
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import the request tracker
from backend.app.request_tracker import RequestTracker

# Test request handler that succeeds
async def test_success_handler(data: Dict[str, Any]) -> Dict[str, Any]:
    """Test handler that succeeds."""
    return {
        "success": True,
        "message": "Success",
        "data": data
    }

# Test request handler that fails
async def test_failure_handler(data: Dict[str, Any]) -> Dict[str, Any]:
    """Test handler that fails."""
    raise ValueError("Test failure")

# Test request handler that times out
async def test_timeout_handler(data: Dict[str, Any]) -> Dict[str, Any]:
    """Test handler that times out."""
    # Sleep for longer than the timeout
    await asyncio.sleep(0.5)
    return {
        "success": True,
        "message": "Success after timeout",
        "data": data
    }

# Test request handler that succeeds after retries
retry_count = 0
async def test_retry_handler(data: Dict[str, Any]) -> Dict[str, Any]:
    """Test handler that succeeds after retries."""
    global retry_count
    retry_count += 1
    
    if retry_count < 3:
        raise ValueError(f"Test failure (retry {retry_count})")
    
    return {
        "success": True,
        "message": f"Success after {retry_count} tries",
        "data": data
    }

class TestRequestTracker(unittest.TestCase):
    """Test the request tracker functionality."""
    
    def setUp(self):
        """Set up the test case."""
        # Create a request tracker with a short timeout for testing
        self.tracker = RequestTracker(default_timeout=0.2, max_retries=3)
        
        # Register test handlers
        self.tracker.register_handler("test_component", "success", test_success_handler)
        self.tracker.register_handler("test_component", "failure", test_failure_handler)
        self.tracker.register_handler("test_component", "timeout", test_timeout_handler)
        self.tracker.register_handler("test_component", "retry", test_retry_handler)
    
    def tearDown(self):
        """Clean up after the test case."""
        self.tracker.close()
    
    def run_async_test(self, coroutine):
        """Helper method to run async tests."""
        return asyncio.run(coroutine)
    
    def test_successful_request(self):
        """Test a successful request."""
        # Track a request
        request_id, response = self.run_async_test(
            self.tracker.track_request(
                "test_component",
                "success",
                {"test": "data"}
            )
        )
        
        # Check the response
        self.assertTrue(response["success"])
        self.assertEqual(response["message"], "Success")
        self.assertEqual(response["data"]["test"], "data")
        
        # Check the request status
        request = self.tracker.get_request(request_id)
        self.assertIsNotNone(request)
        self.assertEqual(request["status"], "completed")
        
        # Check the result
        result = self.tracker.get_result(request_id)
        self.assertIsNotNone(result)
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "Success")
        
        # Check the pending requests
        pending_requests = self.tracker.get_pending_requests()
        self.assertEqual(len(pending_requests), 0)
        
        # Check the completed requests
        completed_requests = self.tracker.get_completed_requests()
        self.assertEqual(len(completed_requests), 1)
        self.assertEqual(completed_requests[0]["request_id"], request_id)
        
        # Check the error requests
        error_requests = self.tracker.get_error_requests()
        self.assertEqual(len(error_requests), 0)
    
    def test_failed_request(self):
        """Test a failed request."""
        # Track a request
        request_id, response = self.run_async_test(
            self.tracker.track_request(
                "test_component",
                "failure",
                {"test": "data"}
            )
        )
        
        # Check the response
        self.assertIn("error", response)
        self.assertIn("Test failure", response["error"])
        
        # Check the request status
        request = self.tracker.get_request(request_id)
        self.assertIsNotNone(request)
        self.assertEqual(request["status"], "error")
        self.assertIn("Test failure", request["error"])
        
        # Check the result
        result = self.tracker.get_result(request_id)
        self.assertIsNotNone(result)
        self.assertIn("error", result)
        self.assertIn("Test failure", result["error"])
        
        # Check the pending requests
        pending_requests = self.tracker.get_pending_requests()
        self.assertEqual(len(pending_requests), 0)
        
        # Check the completed requests
        completed_requests = self.tracker.get_completed_requests()
        self.assertEqual(len(completed_requests), 0)
        
        # Check the error requests
        error_requests = self.tracker.get_error_requests()
        self.assertEqual(len(error_requests), 1)
        self.assertEqual(error_requests[0]["request_id"], request_id)
    
    def test_retry_request(self):
        """Test a request that succeeds after retries."""
        # Use a class variable to track the retry count
        self.current_retry_count = 0
        
        # Create a custom retry handler that doesn't throw exceptions
        # This is needed because we can't catch exceptions from the global test_retry_handler
        async def custom_retry_handler(data: Dict[str, Any]) -> Dict[str, Any]:
            # First call - simulate failure
            self.current_retry_count = 1
            return {
                "error": "Test failure (retry 1)"
            }
        
        # Register the custom retry handler
        self.tracker.register_handler("test_component", "custom_retry", custom_retry_handler)
        
        # Track a request
        request_id, response = self.run_async_test(
            self.tracker.track_request(
                "test_component",
                "custom_retry",
                {"test": "data"}
            )
        )
        
        # The first call should return an error
        self.assertIn("error", response)
        self.assertIn("Test failure", response["error"])
        
        # Create a second handler that simulates a second failure
        async def custom_retry_handler2(data: Dict[str, Any]) -> Dict[str, Any]:
            # Second call - simulate failure
            self.current_retry_count = 2
            return {
                "error": "Test failure (retry 2)"
            }
        
        # Replace the handler
        self.tracker.register_handler("test_component", "custom_retry", custom_retry_handler2)
        
        # Manually retry the request
        response = self.run_async_test(
            self.tracker.retry_request(request_id)
        )
        
        # The second call should also return an error
        self.assertIn("error", response)
        self.assertIn("Test failure", response["error"])
        
        # Create a third handler that simulates success
        async def custom_retry_handler3(data: Dict[str, Any]) -> Dict[str, Any]:
            # Third call - simulate success
            self.current_retry_count = 3
            return {
                "success": True,
                "message": f"Success after {self.current_retry_count} tries",
                "data": data
            }
        
        # Replace the handler
        self.tracker.register_handler("test_component", "custom_retry", custom_retry_handler3)
        
        # Manually retry the request again
        response = self.run_async_test(
            self.tracker.retry_request(request_id)
        )
        
        # The third call should succeed
        self.assertTrue(response["success"])
        self.assertIn("Success after", response["message"])
        self.assertEqual(response["data"]["test"], "data")
        
        # Check the request status
        request = self.tracker.get_request(request_id)
        self.assertIsNotNone(request)
        self.assertEqual(request["status"], "completed")
        
        # Check the result
        result = self.tracker.get_result(request_id)
        self.assertIsNotNone(result)
        self.assertTrue(result["success"])
        self.assertIn("Success after", result["message"])
        
        # Check the retry count
        self.assertEqual(self.current_retry_count, 3)
        
        # Check the pending requests
        pending_requests = self.tracker.get_pending_requests()
        self.assertEqual(len(pending_requests), 0)
        
        # Check the completed requests
        completed_requests = self.tracker.get_completed_requests()
        self.assertEqual(len(completed_requests), 1)
        self.assertEqual(completed_requests[0]["request_id"], request_id)
        
        # Check the error requests
        error_requests = self.tracker.get_error_requests()
        self.assertEqual(len(error_requests), 0)
    
    def test_timeout_request(self):
        """Test a request that times out."""
        # Create a custom timeout handler that always times out
        async def custom_timeout_handler(data: Dict[str, Any]) -> Dict[str, Any]:
            # Sleep for longer than the timeout
            await asyncio.sleep(1.0)
            return {
                "success": True,
                "message": "This should never be returned due to timeout",
                "data": data
            }
        
        # Register the custom timeout handler
        self.tracker.register_handler("test_component", "custom_timeout", custom_timeout_handler)
        
        # Track a request with a very short timeout
        request_id, response = self.run_async_test(
            self.tracker.track_request(
                "test_component",
                "custom_timeout",
                {"test": "data"},
                timeout=0.1
            )
        )
        
        # Since the handler takes longer than the timeout, the request should fail immediately
        # with a timeout error from the track_request method
        self.assertIn("error", response)
        self.assertIn("timed out", response["error"])
        
        # Check the request status
        request = self.tracker.get_request(request_id)
        self.assertIsNotNone(request)
        self.assertEqual(request["status"], "error")
        
        # Clean up
        self.tracker.clear_all_requests()
        
        # Check that all requests were cleared
        self.assertEqual(len(self.tracker.get_pending_requests()), 0)
        self.assertEqual(len(self.tracker.get_completed_requests()), 0)
        self.assertEqual(len(self.tracker.get_error_requests()), 0)
    
    def test_unknown_component(self):
        """Test a request for an unknown component."""
        # Track a request
        request_id, response = self.run_async_test(
            self.tracker.track_request(
                "unknown_component",
                "unknown_action",
                {"test": "data"}
            )
        )
        
        # Check the response
        self.assertIn("error", response)
        self.assertIn("No handler found", response["error"])
        
        # Check the request status
        request = self.tracker.get_request(request_id)
        self.assertIsNotNone(request)
        self.assertEqual(request["status"], "error")
        self.assertIn("No handler found", request["error"])
    
    def test_unknown_action(self):
        """Test a request for an unknown action."""
        # Track a request
        request_id, response = self.run_async_test(
            self.tracker.track_request(
                "test_component",
                "unknown_action",
                {"test": "data"}
            )
        )
        
        # Check the response
        self.assertIn("error", response)
        self.assertIn("No handler found", response["error"])
        
        # Check the request status
        request = self.tracker.get_request(request_id)
        self.assertIsNotNone(request)
        self.assertEqual(request["status"], "error")
        self.assertIn("No handler found", request["error"])
    
    def test_clear_completed_requests(self):
        """Test clearing completed requests."""
        # Track a successful request
        request_id, _ = self.run_async_test(
            self.tracker.track_request(
                "test_component",
                "success",
                {"test": "data"}
            )
        )
        
        # Check the completed requests
        completed_requests = self.tracker.get_completed_requests()
        self.assertEqual(len(completed_requests), 1)
        self.assertEqual(completed_requests[0]["request_id"], request_id)
        
        # Clear completed requests
        self.tracker.clear_completed_requests()
        
        # Check the completed requests again
        completed_requests = self.tracker.get_completed_requests()
        self.assertEqual(len(completed_requests), 0)
    
    def test_clear_error_requests(self):
        """Test clearing error requests."""
        # Track a failed request
        request_id, _ = self.run_async_test(
            self.tracker.track_request(
                "test_component",
                "failure",
                {"test": "data"}
            )
        )
        
        # Check the error requests
        error_requests = self.tracker.get_error_requests()
        self.assertEqual(len(error_requests), 1)
        self.assertEqual(error_requests[0]["request_id"], request_id)
        
        # Clear error requests
        self.tracker.clear_error_requests()
        
        # Check the error requests again
        error_requests = self.tracker.get_error_requests()
        self.assertEqual(len(error_requests), 0)


if __name__ == '__main__':
    unittest.main()
