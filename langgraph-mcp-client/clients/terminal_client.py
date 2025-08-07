import asyncio
from clients.base_client import BaseClient

class TerminalClient(BaseClient):
    """Terminal-based interactive client"""
    
    def __init__(self, workflow):
        super().__init__(workflow)
        self.running = False
    
    async def start(self):
        """Start the terminal client"""
        print("\n" + "="*60)
        print("🤖 LangGraph Multi-MCP Terminal Client Ready!")
        print("="*60)
        print("\nAvailable commands:")
        print("• Enter any query to process")
        print("• 'clear' or 'reset' - Clear conversation history")
        print("• 'quit', 'exit', or 'q' - Exit the client")
        print("="*60 + "\n")
        
        self.running = True
        
        try:
            while self.running:
                try:
                    query = input("🔍 Enter your query: ").strip()
                    
                    if not query:
                        continue
                    
                    if query.lower() in ['quit', 'exit', 'q']:
                        print("👋 Goodbye!")
                        break
                    
                    if query.lower() in ['clear', 'reset']:
                        self.conversation.clear()
                        print("🗑️ Conversation history cleared!")
                        continue
                    
                    await self._process_query(query)
                    
                except KeyboardInterrupt:
                    print("\n👋 Goodbye!")
                    break
                except Exception as e:
                    print(f"❌ Error: {e}")
                    
        finally:
            await self.stop()
    
    async def _process_query(self, query: str):
        """Process user query"""
        print(f"\n⏳ Processing: {query}")
        
        # Show conversation context
        context_summary = self.conversation.get_context_summary()
        if context_summary != "No previous context":
            print(f"📝 {context_summary}")
        
        try:
            response = await self.workflow.execute(self.conversation, query)
            print(f"\n🤖 Response:\n{response}\n")
            print("-" * 60)
            
        except Exception as e:
            print(f"❌ Error processing query: {e}")
    
    async def stop(self):
        """Stop the terminal client"""
        self.running = False
        print("🧹 Terminal client stopped.")
