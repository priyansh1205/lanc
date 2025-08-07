from abc import ABC, abstractmethod
from typing import Any, List
from models.message import Message

class ILLMProvider(ABC):
    """Interface for LLM providers"""
    
    @abstractmethod
    async def generate_response(self, messages: List[Message]) -> str:
        """Generate response from LLM"""
        pass
    
    @abstractmethod
    def get_model_info(self) -> dict:
        """Get model information"""
        pass

class ILLMService(ABC):
    """Interface for LLM service management"""
    
    @abstractmethod
    def get_llm(self, name: str) -> ILLMProvider:
        """Get LLM provider by name"""
        pass
    
    @abstractmethod
    def register_llm(self, name: str, provider: ILLMProvider):
        """Register new LLM provider"""
        pass
