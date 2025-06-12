from fastapi import FastAPI, HTTPException, Request
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
import json
from manifest import ManifestManager
from tools.hello_world import HelloWorldTool

# JSON-RPC 2.0 Models
class JsonRpcRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: Optional[Dict[str, Any]] = None
    id: Optional[Any] = None

class JsonRpcResponse(BaseModel):
    jsonrpc: str = "2.0"
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[Any] = None

class JsonRpcError(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None

# MCP Protocol Models
class ClientInfo(BaseModel):
    name: str
    version: str

class InitializeParams(BaseModel):
    protocolVersion: str
    capabilities: Dict[str, Any]
    clientInfo: ClientInfo

class ToolCallParams(BaseModel):
    name: str
    arguments: Optional[Dict[str, Any]] = None

class MCPServer:
    """MCP Server implementing JSON-RPC 2.0 protocol."""
    
    def __init__(self):
        self.manifest_manager = ManifestManager()
        self.tools = self._initialize_tools()
        self.initialized = False
        self.client_info = None
        
    def _initialize_tools(self) -> Dict[str, Any]:
        """Initialize available tools."""
        tools = {}
        hello_world_tool = HelloWorldTool()
        tools[hello_world_tool.name] = hello_world_tool
        return tools
    
    def _create_error_response(self, request_id: Any, code: int, message: str, data: Any = None) -> JsonRpcResponse:
        """Create JSON-RPC error response."""
        error = JsonRpcError(code=code, message=message, data=data)
        return JsonRpcResponse(id=request_id, error=error.dict())
    
    def _create_success_response(self, request_id: Any, result: Any) -> JsonRpcResponse:
        """Create JSON-RPC success response."""
        return JsonRpcResponse(id=request_id, result=result)
    
    async def _handle_initialize(self, params: Dict[str, Any], request_id: Any) -> JsonRpcResponse:
        """Handle MCP initialize method."""
        try:
            init_params = InitializeParams(**params)
            
            # Validate protocol version
            if init_params.protocolVersion != "2024-11-05":
                return self._create_error_response(
                    request_id, -32602, 
                    f"Unsupported protocol version: {init_params.protocolVersion}"
                )
            
            self.initialized = True
            self.client_info = init_params.clientInfo
            
            # Return server capabilities
            result = {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                    "resources": {},
                    "prompts": {}
                },
                "serverInfo": {
                    "name": "mcp-development-server",
                    "version": "1.0.0"
                }
            }
            
            return self._create_success_response(request_id, result)
            
        except Exception as e:
            return self._create_error_response(request_id, -32602, f"Invalid params: {str(e)}")
    
    async def _handle_tools_list(self, request_id: Any) -> JsonRpcResponse:
        """Handle tools/list method."""
        if not self.initialized:
            return self._create_error_response(request_id, -32002, "Server not initialized")
        
        try:
            # Get manifest and extract tools
            manifest = self.manifest_manager.get_manifest(list(self.tools.values()))
            tools_list = manifest.get("tools", [])
            
            result = {"tools": tools_list}
            return self._create_success_response(request_id, result)
            
        except Exception as e:
            return self._create_error_response(request_id, -32603, f"Internal error: {str(e)}")
    
    async def _handle_tools_call(self, params: Dict[str, Any], request_id: Any) -> JsonRpcResponse:
        """Handle tools/call method."""
        if not self.initialized:
            return self._create_error_response(request_id, -32002, "Server not initialized")
        
        try:
            call_params = ToolCallParams(**params)
            
            if call_params.name not in self.tools:
                return self._create_error_response(
                    request_id, -32601, 
                    f"Tool not found: {call_params.name}"
                )
            
            tool = self.tools[call_params.name]
            tool_result = await tool.execute(call_params.arguments or {})
            
            # Format result according to MCP spec
            result = {
                "content": [
                    {
                        "type": "text",
                        "text": str(tool_result)
                    }
                ],
                "isError": False
            }
            
            return self._create_success_response(request_id, result)
            
        except Exception as e:
            # Return error result in MCP format
            result = {
                "content": [
                    {
                        "type": "text", 
                        "text": f"Error executing tool: {str(e)}"
                    }
                ],
                "isError": True
            }
            return self._create_success_response(request_id, result)
    
    async def _handle_ping(self, request_id: Any) -> JsonRpcResponse:
        """Handle ping method."""
        return self._create_success_response(request_id, {})
    
    async def handle_jsonrpc_request(self, request_data: Dict[str, Any]) -> JsonRpcResponse:
        """Handle incoming JSON-RPC request."""
        try:
            # Validate JSON-RPC structure
            if request_data.get("jsonrpc") != "2.0":
                return self._create_error_response(
                    request_data.get("id"), -32600, "Invalid JSON-RPC version"
                )
            
            method = request_data.get("method")
            params = request_data.get("params", {})
            request_id = request_data.get("id")
            
            # Route to appropriate handler
            if method == "initialize":
                return await self._handle_initialize(params, request_id)
            elif method == "tools/list":
                return await self._handle_tools_list(request_id)
            elif method == "tools/call":
                return await self._handle_tools_call(params, request_id)
            elif method == "ping":
                return await self._handle_ping(request_id)
            else:
                return self._create_error_response(
                    request_id, -32601, f"Method not found: {method}"
                )
                
        except Exception as e:
            return self._create_error_response(
                request_data.get("id"), -32700, f"Parse error: {str(e)}"
            )
    
    def create_app(self) -> FastAPI:
        """Create and configure FastAPI application."""
        app = FastAPI(title="MCP Development Server")
        
        @app.get("/health")
        async def health_check():
            return {"status": "healthy"}
        
        @app.post("/")
        async def mcp_handler(request: Request):
            """Main MCP JSON-RPC endpoint."""
            try:
                body = await request.body()
                request_data = json.loads(body)
                
                # Handle single request
                if isinstance(request_data, dict):
                    response = await self.handle_jsonrpc_request(request_data)
                    return response.dict(exclude_none=True)
                
                # Handle batch requests
                elif isinstance(request_data, list):
                    responses = []
                    for req in request_data:
                        response = await self.handle_jsonrpc_request(req)
                        responses.append(response.dict(exclude_none=True))
                    return responses
                
                else:
                    error_response = self._create_error_response(None, -32600, "Invalid Request")
                    return error_response.dict(exclude_none=True)
                    
            except json.JSONDecodeError:
                error_response = self._create_error_response(None, -32700, "Parse error")
                return error_response.dict(exclude_none=True)
            except Exception as e:
                error_response = self._create_error_response(None, -32603, f"Internal error: {str(e)}")
                return error_response.dict(exclude_none=True)
        
        # Keep the old REST endpoints for backward compatibility (optional)
        @app.get("/manifest")
        async def get_manifest():
            """Legacy REST endpoint for manifest."""
            return self.manifest_manager.get_manifest(list(self.tools.values()))
        
        @app.post("/helloworld")
        async def execute_helloworld(request: Dict[str, Any] = None):
            """Legacy REST endpoint for helloworld."""
            if "helloworld" not in self.tools:
                raise HTTPException(status_code=404, detail="Tool not found")
            
            tool = self.tools["helloworld"]
            try:
                result = await tool.execute(request or {})
                return {"result": result, "status": "success"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        return app