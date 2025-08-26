"""Base Agent class for the multi-agent system."""

from abc import ABC, abstractmethod
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class Agent(ABC):
    """Base class for all agents in the system."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"agent.{name.lower().replace(' ', '_')}")
    
    @abstractmethod
    def run(self, input_data: str) -> str:
        """Main entry point for the agent. Must be implemented by subclasses."""
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """Get agent information."""
        return {
            'name': self.name,
            'description': self.description,
            'type': self.__class__.__name__
        }