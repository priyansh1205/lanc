import os
import asyncio
import subprocess
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

load_dotenv()

# --------------------------------
# CONFIGURATION
# --------------------------------
MS365_MODE = os.getenv("MS365_MODE", "device")  # device | http | byot
MS365_PORT = int(os.getenv("MS365_PORT", "3000"))
MS365_TOKEN = os.getenv("MS365_MCP_OAUTH_TOKEN")  # Used in BYOT or HTTP
MS365_SERVER_PATH = os.getenv("MS365_SERVER_PATH", "@softeria/ms-365-mcp-server")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")


async def start_ms365_server():
    """
    Starts the ms-365-mcp-server in the chosen mode.
    """
    env = os.environ.copy()

    if MS365_MODE == "device":
        print("🚀 Starting ms-365-mcp-server in DEVICE CODE mode (stdio transport)")
        proc = subprocess.Popen(
            ["npx", "-y", MS365_SERVER_PATH, "--login"],
            env=env
        )
        return {"transport": "sse", "url": "stdio"}  # not a real URL, handled internally

    elif MS365_MODE == "http":
        print(f"🚀 Starting ms-365-mcp-server in HTTP mode on port {MS365_PORT}")
        args = ["npx", "-y", MS365_SERVER_PATH, "--http", str(MS365_PORT)]
        proc = subprocess.Popen(args, env=env)
        return {
            "transport": "streamable-http",
            "url": f"http://localhost:{MS365_PORT}/mcp",
            "headers": {"Authorization": f"Bearer {MS365_TOKEN}"}
        }

    elif MS365_MODE == "byot":
        if not MS365_TOKEN:
            raise ValueError("❌ MS365_MCP_OAUTH_TOKEN must be set for BYOT mode.")
        print(f"🚀 Starting ms-365-mcp-server in BYOT mode on port {MS365_PORT}")
        env["MS365_MCP_OAUTH_TOKEN"] = MS365_TOKEN
        args = ["npx", "-y", MS365_SERVER_PATH, "--http", str(MS365_PORT)]
        proc = subprocess.Popen(args, env=env)
        return {
            "transport": "streamable-http",
            "url": f"http://localhost:{MS365_PORT}/mcp",
            "headers": {"Authorization": f"Bearer {MS365_TOKEN}"}
        }

    else:
        raise ValueError(f"Invalid MS365_MODE: {MS365_MODE}")


async def connect_ms365_client(server_info):
    """
    Connects to the running ms-365-mcp-server and retrieves tools.
    """
    client_config = {
        "ms365": {
            "url": server_info["url"],
            "transport": server_info["transport"]
        }
    }
    if "headers" in server_info:
        client_config["ms365"]["headers"] = server_info["headers"]

    client = MultiServerMCPClient(client_config)
    tools = await client.get_tools()
    print(f"✅ Connected to MS-365 MCP Server with {len(tools)} tools.")
    for t in tools:
        print(f" • {t.name}: {t.description}")
    return client, tools


async def run_langgraph_with_ms365():
    """
    Full flow: start server, connect, run LangGraph agent loop.
    """
    # Start server
    server_info = await start_ms365_server()

    # Connect client
    client, tools = await connect_ms365_client(server_info)

    # Init Gemini LLM
    llm = ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        google_api_key=GOOGLE_API_KEY,
        temperature=0.3
    )

    # Create LangGraph agent
    agent = create_react_agent(llm, tools)

    # Interactive loop
    state = {"messages": []}
    while True:
        user_in = input("\n💬 You: ")
        if user_in.lower() in ["quit", "exit", "q"]:
            print("👋 Exiting.")
            break
        state["messages"].append({"role": "user", "content": user_in})
        result = await agent.ainvoke(state)
        if isinstance(result, dict) and "messages" in result:
            state = result
            reply = result["messages"][-1]["content"]
        else:
            reply = str(result)
        print(f"🤖 {reply}")


if __name__ == "__main__":
    asyncio.run(run_langgraph_with_ms365())
