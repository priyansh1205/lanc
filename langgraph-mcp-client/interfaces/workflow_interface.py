from abc import ABC, abstractmethod
from typing import Any, Dict, List
from models.conversation import Conversation

class IWorkflow(ABC):
    """Interface for workflow implementations"""
    
    @abstractmethod
    async def execute(self, conversation: Conversation, query: str) -> str:
        """Execute workflow with given conversation and query"""
        pass
    
    @abstractmethod
    def set_tools(self, tools: List[Any]):
        """Set available tools for workflow"""
        pass
