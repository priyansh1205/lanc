from typing import Dict, List, Any
from interfaces.mcp_interface import IMCPServer, IMCPService
from config.settings import MCPServerConfig

try:
    from langchain_mcp_adapters.client import MultiServerMCPClient
except ImportError:
    MultiServerMCPClient = None

class MCPServer(IMCPServer):
    """Single MCP Server implementation"""
    
    def __init__(self, config: MCPServerConfig):
        self.config = config
        self.client = None
        self.tools = []
        
    async def connect(self) -> bool:
        """Connect to MCP server"""
        try:
            if MultiServerMCPClient is None:
                raise ImportError("langchain_mcp_adapters not installed")
                
            self.client = MultiServerMCPClient({
                self.config.name: {
                    "url": f"{self.config.url}/sse",
                    "transport": self.config.transport
                }
            })
            
            self.tools = await self.client.get_tools()
            print(f"✅ Connected to {self.config.name}: {len(self.tools)} tools")
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to {self.config.name}: {e}")
            return False
    
    async def get_tools(self) -> List[Any]:
        """Get available tools from this server"""
        return self.tools
    
    async def disconnect(self):
        """Disconnect from server"""
        if self.client:
            # Add cleanup logic if needed
            self.client = None

class MCPService(IMCPService):
    """Service for managing multiple MCP servers"""
    
    def __init__(self):
        self._servers: Dict[str, IMCPServer] = {}
    
    async def add_server(self, name: str, server: IMCPServer):
        """Add MCP server"""
        success = await server.connect()
        if success:
            self._servers[name] = server
    
    async def get_all_tools(self) -> List[Any]:
        """Get tools from all connected servers"""
        all_tools = []
        for server in self._servers.values():
            tools = await server.get_tools()
            all_tools.extend(tools)
        return all_tools
    
    def list_servers(self) -> List[str]:
        """List all connected servers"""
        return list(self._servers.keys())

class MCPServiceFactory:
    """Factory for creating MCP services"""
    
    @staticmethod
    async def create_mcp_service(server_configs: List[MCPServerConfig]) -> MCPService:
        """Create and configure MCP service with servers"""
        service = MCPService()
        
        for config in server_configs:
            if not config.url:
                print(f"⚠️ Skipping {config.name}: URL not configured")
                continue
                
            server = MCPServer(config)
            await service.add_server(config.name, server)
        
        return service
