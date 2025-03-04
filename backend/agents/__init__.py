"""
MOSAIC Agents Package

This package contains the agent implementations for the MOSAIC system.
It includes the base agent class and specialized agents for different tasks.

The agents are organized into subdirectories:
- regular: Contains regular agents that provide specific functionality
- supervisors: Contains supervisor agents that orchestrate other agents
- sandbox: Contains experimental agents that are under development

Note: Only the base components are imported here. Specific agents are discovered
and registered automatically by the agent_discovery.py process.
"""

try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.agents.base import BaseAgent, AgentRegistry, agent_registry
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.agents.base import BaseAgent, AgentRegistry, agent_registry

__all__ = [
    "BaseAgent", 
    "AgentRegistry", 
    "agent_registry"
]
