"""
Agent Generator Module for MOSAIC

This module is a compatibility layer that imports from the internal module.
It is kept for backward compatibility with existing code.
"""

from mosaic.backend.agents.internal.agent_generator import AgentGenerator

__all__ = ["AgentGenerator"]
