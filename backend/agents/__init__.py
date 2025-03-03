"""
MOSAIC Agents Package

This package contains the agent implementations for the MOSAIC system.
It includes the base agent class and specialized agents for different tasks.
"""

try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.agents.base import BaseAgent, AgentRegistry, agent_registry
    from mosaic.backend.agents.calculator import CalculatorAgent, register_calculator_agent
    from mosaic.backend.agents.safety import SafetyAgent, register_safety_agent
    from mosaic.backend.agents.writer import WriterAgent, register_writer_agent
    from mosaic.backend.agents.supervisor import create_calculator_supervisor, create_multi_agent_supervisor
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.agents.base import BaseAgent, AgentRegistry, agent_registry
    from backend.agents.calculator import CalculatorAgent, register_calculator_agent
    from backend.agents.safety import SafetyAgent, register_safety_agent
    from backend.agents.writer import WriterAgent, register_writer_agent
    from backend.agents.supervisor import create_calculator_supervisor, create_multi_agent_supervisor

__all__ = [
    "BaseAgent", 
    "AgentRegistry", 
    "agent_registry",
    "CalculatorAgent",
    "register_calculator_agent",
    "SafetyAgent",
    "register_safety_agent",
    "WriterAgent",
    "register_writer_agent",
    "create_calculator_supervisor",
    "create_multi_agent_supervisor"
]
