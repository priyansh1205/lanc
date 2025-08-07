from abc import ABC, abstractmethod
from typing import List, Dict, Any

class IMCPServer(ABC):
    """Interface for MCP server connections"""
    
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to MCP server"""
        pass
    
    @abstractmethod
    async def get_tools(self) -> List[Any]:
        """Get available tools"""
        pass
    
    @abstractmethod
    async def disconnect(self):
        """Disconnect from server"""
        pass

class IMCPService(ABC):
    """Interface for MCP service management"""
    
    @abstractmethod
    async def add_server(self, name: str, server: IMCPServer):
        """Add MCP server"""
        pass
    
    @abstractmethod
    async def get_all_tools(self) -> List[Any]:
        """Get tools from all servers"""
        pass
