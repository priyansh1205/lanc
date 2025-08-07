"""Main entry point for langgraph-mcp-client."""

def main():
    """Application entry point."""
    pass

if __name__ == "__main__":
    main()
import asyncio
from config.settings import load_settings
from services.llm_service import LLMServiceFactory
from services.mcp_service import MCPServiceFactory
from workflows.react_workflow import ReactWorkflow
from clients.terminal_client import TerminalClient

class Application:
    """Main application orchestrator"""
    
    def __init__(self):
        self.settings = load_settings()
        self.llm_service = None
        self.mcp_service = None
        self.workflow = None
        self.client = None
    
    async def initialize(self):
        """Initialize all services and components"""
        print("🚀 Initializing LangGraph MCP Client...")
        
        # Initialize LLM service
        print("\n📦 Setting up LLM providers...")
        self.llm_service = LLMServiceFactory.create_llm_service(self.settings.llm_configs)
        
        # Initialize MCP service
        print("\n🔗 Connecting to MCP servers...")
        self.mcp_service = await MCPServiceFactory.create_mcp_service(self.settings.mcp_servers)
        
        # Get all tools
        tools = await self.mcp_service.get_all_tools()
        if not tools:
            print("⚠️ No tools available. Check your MCP server connections.")
        
        # Create workflow
        print(f"\n⚙️ Setting up workflow with {self.settings.default_llm} LLM...")
        self.workflow = ReactWorkflow(self.llm_service, self.settings.default_llm)
        self.workflow.set_tools(tools)
        
        # Create client
        print(f"\n🖥️ Initializing {self.settings.client_type} client...")
        if self.settings.client_type == "terminal":
            self.client = TerminalClient(self.workflow)
        else:
            raise ValueError(f"Client type '{self.settings.client_type}' not implemented yet")
        
        print("✅ Initialization complete!")
    
    async def run(self):
        """Run the application"""
        try:
            await self.initialize()
            await self.client.start()
        except Exception as e:
            print(f"❌ Application error: {e}")
        finally:
            await self.cleanup()
    
    async def cleanup(self):
        """Cleanup resources"""
        print("🧹 Cleaning up...")
        if self.client:
            await self.client.stop()

async def main():
    """Main entry point"""
    app = Application()
    await app.run()

if __name__ == "__main__":
    asyncio.run(main())
