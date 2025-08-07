import os
import asyncio
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

load_dotenv()

async def setup_langgraph_client():
    """Set up LangGraph client with connections to both MCP servers"""
    
    # Initialize Gemini LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.1
    )

    # Get server URLs from environment
    weather_url = os.getenv("WEATHER_MCP_URL")
    news_url = os.getenv("NEWS_MCP_URL")
    
    if not weather_url or not news_url:
        print("❌ Please set WEATHER_MCP_URL and NEWS_MCP_URL in your .env file")
        return None, []

    print("🔗 Connecting to MCP servers...")
    print(f"Weather server: {weather_url}")
    print(f"News server: {news_url}")
    
    try:
        # Create MultiServerMCPClient
        client = MultiServerMCPClient({
            "weather": {
                "url": f"{weather_url}/sse",
                "transport": "sse"
            },
            "news": {
                "url": f"{news_url}/sse", 
                "transport": "sse"
            }
        })
        
        print("📡 Fetching tools from both servers...")
        all_tools = await client.get_tools()
        
        print(f"✅ Successfully loaded {len(all_tools)} tools:")
        for tool in all_tools:
            print(f"   • {tool.name}: {tool.description}")
        
        # Create LangGraph agent with all tools
        agent = create_react_agent(llm, all_tools)
        
        return agent, all_tools, client
        
    except Exception as e:
        print(f"❌ Error connecting to MCP servers: {e}")
        return None, [], None

def extract_response_content(response):
    """Extract content from LangGraph response - handles different response formats"""
    try:
        # Method 1: Check if it's a dict with messages
        if isinstance(response, dict):
            if "messages" in response and len(response["messages"]) > 0:
                last_message = response["messages"][-1]
                # Handle both dict and object message formats
                if isinstance(last_message, dict):
                    return last_message.get("content", str(last_message))
                elif hasattr(last_message, 'content'):
                    return last_message.content
                else:
                    return str(last_message)
            else:
                return str(response)
        
        # Method 2: If response is directly an AIMessage
        elif hasattr(response, 'content'):
            return response.content
            
        # Method 3: If response has messages attribute
        elif hasattr(response, 'messages') and len(response.messages) > 0:
            return response.messages[-1].content
            
        # Fallback: convert to string
        return str(response)
        
    except Exception as e:
        return f"Could not extract response content: {e}. Response type: {type(response)}"

async def run_interactive_client_with_memory():
    """Run interactive LangGraph client with conversation memory"""
    
    agent, tools, client = await setup_langgraph_client()
    
    if not agent:
        print("Failed to initialize client. Please check your MCP server URLs.")
        return
    
    print("\n" + "="*60)
    print("🤖 LangGraph Multi-MCP Client Ready! (With Memory)")
    print("="*60)
    print("\nExample queries you can try:")
    print("• 'What's the weather like in New York?'")
    print("• 'tell weather' then 'delhi' (conversation context)")
    print("• 'Get me the latest technology news'") 
    print("• 'Check rain probability in London and get business news'")
    print("="*60 + "\n")
    
    # Initialize conversation history
    conversation_state = {"messages": []}
    
    try:
        # Interactive loop
        while True:
            try:
                query = input("🔍 Enter your query (or 'quit' to exit): ")
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                    
                if not query.strip():
                    continue
                    
                print(f"\n🤔 Processing: {query}")
                print("⏳ Agent is working...")
                
                # Add user message to conversation history
                conversation_state["messages"].append({"role": "user", "content": query})
                
                # Invoke the agent with full conversation history
                response = await agent.ainvoke(conversation_state)
                
                # Extract content using the helper function
                final_message = extract_response_content(response)
                print(f"\n🤖 Agent Response:\n{final_message}\n")
                print("-" * 60)
                
                # Update conversation state with the response
                if isinstance(response, dict) and "messages" in response:
                    conversation_state = response
                else:
                    # If response format is different, manually add assistant message
                    conversation_state["messages"].append({"role": "assistant", "content": final_message})
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error processing query: {e}")
                print("Please try again or check your MCP server connections.\n")
    
    except Exception as e:
        print(f"❌ Error in interactive client: {e}")
    
    finally:
        print("🧹 Cleaning up connections...")

# Enhanced version with conversation context display
async def run_enhanced_interactive_client():
    """Enhanced interactive client with conversation context display"""
    
    agent, tools, client = await setup_langgraph_client()
    
    if not agent:
        print("Failed to initialize client.")
        return
    
    print("\n🤖 Enhanced Interactive LangGraph Client Ready!\n")
    
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
            
            # Show conversation context (last 2 exchanges for brevity)
            if len(conversation_state["messages"]) > 0:
                print("📝 Context: " + str(len(conversation_state["messages"])//2) + " previous exchanges")
            
            try:
                # Add user message to conversation history
                conversation_state["messages"].append({"role": "user", "content": query})
                
                # Use the same logic as the working simple client but with conversation state
                result = await agent.ainvoke(conversation_state)
                
                # Handle different response formats
                if hasattr(result, 'content'):
                    response_content = result.content
                elif isinstance(result, dict):
                    if 'messages' in result and len(result['messages']) > 0:
                        conversation_state = result  # Update full state
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
                
                # If we didn't update conversation_state from result, manually add assistant message
                if not (isinstance(result, dict) and 'messages' in result):
                    conversation_state["messages"].append({"role": "assistant", "content": response_content})
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                
            print("-" * 60)
    
    except Exception as e:
        print(f"❌ Error in enhanced interactive client: {e}")

if __name__ == "__main__":
    # Use the enhanced version with conversation memory
    asyncio.run(run_enhanced_interactive_client())
