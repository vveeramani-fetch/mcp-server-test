from typing import List, Dict, Any
from pydantic import BaseModel

class ToolSchema(BaseModel):
    """Schema for tool definition."""
    name: str
    description: str
    parameters: Dict[str, Any]

class MCPManifest(BaseModel):
    """MCP Manifest model."""
    version: str
    tools: List[ToolSchema]

class ManifestManager:
    """Manages MCP manifest generation."""
    
    def __init__(self):
        self.version = "1.0.0"
    
    def get_manifest(self, tools: List[Any]) -> Dict[str, Any]:
        """Generate manifest from available tools."""
        tool_schemas = []
        for tool in tools:
            schema = ToolSchema(
                name=tool.name,
                description=tool.description,
                parameters=tool.get_parameters_schema()
            )
            tool_schemas.append(schema)
        
        manifest = MCPManifest(version=self.version, tools=tool_schemas)
        return manifest.model_dump()