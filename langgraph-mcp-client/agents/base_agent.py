from abc import ABC, abstractmethod
from typing import Any, List, Dict, Optional
from models.conversation import Conversation
from models.message import Message
from interfaces.llm_interface import ILLMProvider

class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, name: str, llm_provider: ILLMProvider, description: str = ""):
        self.name = name
        self.llm_provider = llm_provider
        self.description = description
        self.tools: List[Any] = []
        self.system_prompt = self._get_default_system_prompt()
    
    def _get_default_system_prompt(self) -> str:
        """Get default system prompt for the agent"""
        return f"""You are {self.name}, a helpful AI assistant.
{self.description}

Available tools: {[tool.name for tool in self.tools] if self.tools else 'None'}

Always be helpful, accurate, and provide clear responses."""
    
    def set_tools(self, tools: List[Any]):
        """Set available tools for this agent"""
        self.tools = tools
        # Update system prompt with new tools
        self.system_prompt = self._get_default_system_prompt()
        print(f"🔧 Agent '{self.name}' loaded {len(tools)} tools")
    
    def add_tool(self, tool: Any):
        """Add a single tool to the agent"""
        self.tools.append(tool)
        self.system_prompt = self._get_default_system_prompt()
    
    def get_relevant_tools(self, query: str) -> List[Any]:
        """Filter tools relevant to the query"""
        # Base implementation returns all tools
        # Override in subclasses for more sophisticated filtering
        return self.tools
    
    @abstractmethod
    async def process_query(self, conversation: Conversation, query: str) -> str:
        """Process a query and return a response"""
        pass
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent information"""
        return {
            "name": self.name,
            "description": self.description,
            "llm_model": self.llm_provider.get_model_info(),
            "tools_count": len(self.tools),
            "tools": [tool.name for tool in self.tools] if self.tools else []
        }
