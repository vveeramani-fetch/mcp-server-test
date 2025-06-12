from typing import Dict, Any
from abc import ABC, abstractmethod

class BaseTool(ABC):
    """Abstract base class for all tools."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description."""
        pass
    
    @abstractmethod
    async def execute(self, parameters: Dict[str, Any]) -> Any:
        """Execute the tool with given parameters."""
        pass
    
    @abstractmethod
    def get_parameters_schema(self) -> Dict[str, Any]:
        """Get parameters schema for the tool."""
        pass

class HelloWorldTool(BaseTool):
    """Hello World tool implementation."""
    
    @property
    def name(self) -> str:
        return "helloworld"
    
    @property
    def description(self) -> str:
        return "A simple hello world tool that greets users"
    
    async def execute(self, parameters: Dict[str, Any]) -> str:
        """Execute hello world functionality."""
        name = parameters.get("name", "World")
        return f"Hello, {name}!"
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        """Get parameters schema."""
        return {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name to greet",
                    "default": "World"
                }
            },
            "required": []
        }