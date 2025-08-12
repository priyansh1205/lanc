from langchain_mcp_adapters import MCPGraphClient
import asyncio

async def main():
    # MCP server info
    server_info = {
        "name": "ms365",
        "url": "http://localhost:3000/mcp",
        "transport": "streamable-http",  # Required for HTTP mode
    }

    # Create MCP client
    client = MCPGraphClient(**server_info)

    # Connect
    await client.connect()

    # List available tools
    tools = await client.list_tools()
    print("Available tools:", tools)

    # Example: call a tool (replace with a real tool name from the list above)
    # result = await client.call_tool("mails.list", {"limit": 5})
    # print("Tool result:", result)

    # Disconnect
    await client.disconnect()

# Run the async function
asyncio.run(main())
