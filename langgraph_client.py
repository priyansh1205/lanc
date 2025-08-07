import os
import asyncio
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

load_dotenv()

async def connect_to_mcp(name, url):
    """Helper function to test connection to an MCP server and get tools."""
    try:
        client = MultiServerMCPClient({
            name: {
                "url": f"{url.rstrip('/')}/sse",
                "transport": "sse"
            }
        })
        tools = await client.get_tools()
        return (name, client, tools, None)
    except Exception as e:
        return (name, None, None, str(e))

async def setup_langgraph_client():
    """Set up LangGraph client with connections to MCP servers dynamically handling errors"""
    
    # Initialize Gemini LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.3
    )

    # Get server URLs from environment
    weather_url = os.getenv("WEATHER_MCP_URL")
    news_url = os.getenv("NEWS_MCP_URL")
    servicenow_url = os.getenv("SERVICENOW_MCP_URL")

    servers = {
        "weather": weather_url,
        "news": news_url,
        "servicenow": servicenow_url
    }

    # Filter out any missing URLs
    servers = {k: v for k, v in servers.items() if v}

    if not servers:
        print("❌ No MCP server URLs configured.")
        return None, [], None

    print("🔗 Connecting to MCP servers...")
    for name, url in servers.items():
        print(f"{name.capitalize()} server: {url}")

    successful_clients = {}
    all_tools = []

    # Attempt to connect to each server individually
    for name, url in servers.items():
        print(f"📡 Connecting to {name} server...")
        n, client, tools, error = await connect_to_mcp(name, url)
        if error:
            print(f"❌ Error connecting to {name} MCP server: {error}")
        else:
            print(f"✅ Connected to {name} MCP server with {len(tools)} tools:")
            for tool in tools:
                print(f"   • {tool.name}: {tool.description}")
            successful_clients[name] = {
                "url": f"{url.rstrip('/')}/sse",
                "transport": "sse"
            }
            all_tools.extend(tools)

    if not successful_clients:
        print("❌ Could not connect to any MCP servers.")
        return None, [], None

    # Create MultiServerMCPClient with only successful clients
    try:
        client = MultiServerMCPClient(successful_clients)
        print(f"\n✅ Successfully created multi-server client with {len(successful_clients)} servers and {len(all_tools)} total tools.")
        
        # Create LangGraph agent with all tools from successful connections
        agent = create_react_agent(llm, all_tools)
        
        return agent, all_tools, client
        
    except Exception as e:
        print(f"❌ Error creating MultiServerMCPClient with successful connections: {e}")
        return None, [], None

def extract_response_content(response):
    """Extract content from LangGraph response - handles different response formats"""
    try:
        if isinstance(response, dict):
            if "messages" in response and len(response["messages"]) > 0:
                last_message = response["messages"][-1]
                if isinstance(last_message, dict):
                    return last_message.get("content", str(last_message))
                elif hasattr(last_message, 'content'):
                    return last_message.content
                else:
                    return str(last_message)
            else:
                return str(response)
        elif hasattr(response, 'content'):
            return response.content
        elif hasattr(response, 'messages') and len(response.messages) > 0:
            return response.messages[-1].content
        return str(response)
    except Exception as e:
        return f"Could not extract response content: {e}. Response type: {type(response)}"

async def run_enhanced_interactive_client():
    """Enhanced interactive client with conversation context display"""
    
    agent, tools, client = await setup_langgraph_client()
    
    if not agent:
        print("Failed to initialize client with any MCP servers.")
        return
    
    print("\n" + "="*60)
    print("🤖 Enhanced Interactive LangGraph Client Ready!")
    print("="*60)
    print("\nAvailable tools from connected MCP servers:")
    for tool in tools:
        print(f"• {tool.name}: {tool.description}")
    
    # Show ServiceNow specific examples if connected
    servicenow_connected = any("servicenow" in str(tool.name).lower() or 
                              "incident" in str(tool.name).lower() or 
                              "catalog" in str(tool.name).lower() 
                              for tool in tools)
    
    if servicenow_connected:
        print("\n📋 ServiceNow Examples:")
        print("• 'Create a new incident for network connectivity issues'")
        print("• 'List all high priority incidents'")
        print("• 'Show me service catalog items'")
        print("• 'Create a change request for server maintenance'")
    
    print("="*60 + "\n")
    
    # Initialize conversation history
    conversation_state = {"messages": []}
    
    try:
        while True:
            query = input("🔍 Enter your query (or 'quit', 'clear' to clear history): ")
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if query.lower() in ['clear', 'reset']:
                conversation_state = {"messages": []}
                print("🗑️ Conversation history cleared!")
                continue
                
            if not query.strip():
                continue
                
            print(f"\n⏳ Processing: {query}")
            
            if len(conversation_state["messages"]) > 0:
                print("📝 Context: " + str(len(conversation_state["messages"])//2) + " previous exchanges")
            
            try:
                conversation_state["messages"].append({"role": "user", "content": query})
                result = await agent.ainvoke(conversation_state)
                
                if hasattr(result, 'content'):
                    response_content = result.content
                elif isinstance(result, dict):
                    if 'messages' in result and len(result['messages']) > 0:
                        conversation_state = result
                        last_message = result['messages'][-1]
                        if isinstance(last_message, dict):
                            response_content = last_message.get('content', str(last_message))
                        else:
                            response_content = last_message.content if hasattr(last_message, 'content') else str(last_message)
                    else:
                        response_content = str(result)
                else:
                    response_content = str(result)
                
                print(f"🤖 Response: {response_content}")
                
                if not (isinstance(result, dict) and 'messages' in result):
                    conversation_state["messages"].append({"role": "assistant", "content": response_content})
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                
            print("-" * 60)
    
    except Exception as e:
        print(f"❌ Error in enhanced interactive client: {e}")
    
    finally:
        print("🧹 Cleaning up connections...")

if __name__ == "__main__":
    asyncio.run(run_enhanced_interactive_client())
