from typing import Dict, Any, Optional
from mcp_client import MCPClient
from tool_registry import ToolRegistry

class MCPAgent:
    """MCP Agent that discovers and executes tools."""
    
    def __init__(self, server_url: str):
        self.mcp_client = MCPClient(server_url)
        self.tool_registry = ToolRegistry()
    
    async def discover_tools(self) -> None:
        """Discover available tools from MCP server."""
        tools_response = await self.mcp_client.list_tools()
        tools_list = tools_response.get("tools", [])
        self.tool_registry.register_tools_from_list(tools_list)
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Execute a tool with given parameters."""
        if not self.tool_registry.is_tool_registered(tool_name):
            raise ValueError(f"Tool '{tool_name}' is not registered")
        
        tool_info = self.tool_registry.get_tool(tool_name)
        return await self.mcp_client.call_tool(tool_name, parameters)
    
    async def list_available_tools(self) -> list[str]:
        """List all available tools."""
        return self.tool_registry.list_tools()
    
    async def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific tool."""
        return self.tool_registry.get_tool(tool_name)
    
    async def close(self) -> None:
        """Close the agent and cleanup resources."""
        await self.mcp_client.close()