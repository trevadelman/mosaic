"""
MOSAIC Backend Package

This package contains the backend components of the MOSAIC system,
including the FastAPI application, agent system, and database models.
"""

# Import key components for easier access
try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.agents import (
        BaseAgent,
        AgentRegistry,
        agent_registry,
        CalculatorAgent,
        register_calculator_agent,
        create_calculator_supervisor,
        create_multi_agent_supervisor
    )
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.agents import (
        BaseAgent,
        AgentRegistry,
        agent_registry,
        CalculatorAgent,
        register_calculator_agent,
        create_calculator_supervisor,
        create_multi_agent_supervisor
    )

__all__ = [
    "BaseAgent",
    "AgentRegistry",
    "agent_registry",
    "CalculatorAgent",
    "register_calculator_agent",
    "create_calculator_supervisor",
    "create_multi_agent_supervisor"
]
