import pytest
from src.tool_registry import ToolRegistry

@pytest.fixture
def tool_registry():
    return ToolRegistry()

@pytest.fixture
def sample_manifest():
    return {
        "version": "1.0",
        "tools": [
            {
                "name": "helloworld",
                "description": "Hello world tool",
                "parameters": {"type": "object"}
            }
        ]
    }

def test_register_tools_from_manifest(tool_registry, sample_manifest):
    """Test registering tools from manifest."""
    tool_registry.register_tools_from_manifest(sample_manifest)
    
    assert tool_registry.is_tool_registered("helloworld")
    assert "helloworld" in tool_registry.list_tools()

def test_get_tool_info(tool_registry, sample_manifest):
    """Test getting tool information."""
    tool_registry.register_tools_from_manifest(sample_manifest)
    
    tool_info = tool_registry.get_tool("helloworld")
    assert tool_info is not None
    assert tool_info["name"] == "helloworld"
    assert tool_info["description"] == "Hello world tool"

def test_get_nonexistent_tool(tool_registry):
    """Test getting information for non-existent tool."""
    tool_info = tool_registry.get_tool("nonexistent")
    assert tool_info is None

def test_clear_tools(tool_registry, sample_manifest):
    """Test clearing all tools."""
    tool_registry.register_tools_from_manifest(sample_manifest)
    assert len(tool_registry.list_tools()) > 0
    
    tool_registry.clear()
    assert len(tool_registry.list_tools()) == 0

def test_empty_manifest(tool_registry):
    """Test handling empty manifest."""
    empty_manifest = {"version": "1.0", "tools": []}
    tool_registry.register_tools_from_manifest(empty_manifest)
    
    assert len(tool_registry.list_tools()) == 0