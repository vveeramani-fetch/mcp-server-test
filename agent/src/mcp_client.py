import httpx
from typing import Dict, Any, Optional

class MCPClient:
    """Client for communicating with MCP server using JSON-RPC 2.0 protocol."""
    
    def __init__(self, server_url: str):
        self.server_url = server_url.rstrip('/')
        self.client = httpx.AsyncClient()
        self.initialized = False
        self.request_id = 1
    
    def _get_next_id(self) -> int:
        """Get next request ID."""
        self.request_id += 1
        return self.request_id
    
    async def _send_jsonrpc_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send JSON-RPC 2.0 request."""
        request_data = {
            "jsonrpc": "2.0",
            "method": method,
            "id": self._get_next_id()
        }
        
        if params:
            request_data["params"] = params
        
        try:
            response = await self.client.post(
                self.server_url,
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            raise ConnectionError(f"Failed to connect to MCP server: {e}")
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"HTTP error from MCP server: {e}")
    
    async def initialize(self) -> Dict[str, Any]:
        """Initialize connection with MCP server."""
        params = {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "clientInfo": {
                "name": "mcp-test-agent",
                "version": "1.0.0"
            }
        }
        
        response = await self._send_jsonrpc_request("initialize", params)
        
        if "error" in response:
            raise RuntimeError(f"Initialize failed: {response['error']}")
        
        self.initialized = True
        return response.get("result", {})
    
    async def list_tools(self) -> Dict[str, Any]:
        """List available tools from MCP server."""
        if not self.initialized:
            await self.initialize()
        
        response = await self._send_jsonrpc_request("tools/list")
        
        if "error" in response:
            raise RuntimeError(f"Tools list failed: {response['error']}")
        
        return response.get("result", {})
    
    async def call_tool(self, tool_name: str, arguments: Optional[Dict[str, Any]] = None) -> Any:
        """Call a tool on the MCP server."""
        if not self.initialized:
            await self.initialize()
        
        params = {
            "name": tool_name
        }
        if arguments:
            params["arguments"] = arguments
        
        response = await self._send_jsonrpc_request("tools/call", params)
        
        if "error" in response:
            raise RuntimeError(f"Tool call failed: {response['error']}")
        
        return response.get("result", {})
    
    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()
