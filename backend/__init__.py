"""
MOSAIC Backend Package

This package contains the backend components of the MOSAIC system,
including the FastAPI application, agent system, and database models.

The agents are organized into subdirectories:
- regular: Contains regular agents that provide specific functionality
- supervisors: Contains supervisor agents that orchestrate other agents
- sandbox: Contains experimental agents that are under development

Note: Only the base components are imported here. Specific agents are discovered
and registered automatically by the agent_discovery.py process.
"""

# Import key components for easier access
try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.agents import (
        BaseAgent,
        AgentRegistry,
        agent_registry
    )
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.agents import (
        BaseAgent,
        AgentRegistry,
        agent_registry
    )

__all__ = [
    "BaseAgent",
    "AgentRegistry",
    "agent_registry"
]
