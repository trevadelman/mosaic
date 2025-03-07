"""
Agent Generator Module for MOSAIC

This module is a compatibility layer that imports from the internal module.
It is kept for backward compatibility with existing code.
"""

try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.agents.internal.agent_generator import AgentGenerator
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.agents.internal.agent_generator import AgentGenerator

__all__ = ["AgentGenerator"]
