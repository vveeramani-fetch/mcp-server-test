from typing import Dict, Any, Optional, List

class ToolRegistry:
    """Registry for managing discovered tools."""
    
    def __init__(self):
        self._tools: Dict[str, Dict[str, Any]] = {}
    
    def register_tools_from_list(self, tools_list: List[Dict[str, Any]]) -> None:
        """Register tools from MCP tools list."""
        for tool in tools_list:
            self._tools[tool["name"]] = {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["parameters"]
            }
    
    def register_tools_from_manifest(self, manifest: Dict[str, Any]) -> None:
        """Register tools from MCP manifest (legacy method)."""
        tools = manifest.get("tools", [])
        self.register_tools_from_list(tools)
    
    def is_tool_registered(self, tool_name: str) -> bool:
        """Check if a tool is registered."""
        return tool_name in self._tools
    
    def get_tool(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get tool information."""
        return self._tools.get(tool_name)
    
    def list_tools(self) -> List[str]:
        """List all registered tool names."""
        return list(self._tools.keys())
    
    def clear(self) -> None:
        """Clear all registered tools."""
        self._tools.clear()