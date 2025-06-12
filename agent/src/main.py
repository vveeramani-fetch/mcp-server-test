import asyncio
import os
from agent import MCPAgent

async def main():
    """Main entry point for the agent."""
    mcp_server_url = os.getenv("MCP_SERVER_URL", "http://localhost:8000")
    
    print(f"Starting MCP Agent, connecting to: {mcp_server_url}")
    
    agent = MCPAgent(mcp_server_url)
    
    try:
        # Discover and register tools
        await agent.discover_tools()
        print("Tools discovered and registered successfully")
        
        # Execute hello world tool
        result = await agent.execute_tool("helloworld", {"name": "MCP Agent"})
        print(f"Tool execution result: {result}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await agent.close()

if __name__ == "__main__":
    asyncio.run(main())