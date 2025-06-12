import pytest
from src.tools.hello_world import HelloWorldTool

@pytest.fixture
def hello_world_tool():
    return HelloWorldTool()

def test_tool_properties(hello_world_tool):
    """Test tool basic properties."""
    assert hello_world_tool.name == "helloworld"
    assert "hello world" in hello_world_tool.description.lower()

@pytest.mark.asyncio
async def test_execute_with_name(hello_world_tool):
    """Test execute with name parameter."""
    result = await hello_world_tool.execute({"name": "Alice"})
    assert result == "Hello, Alice!"

@pytest.mark.asyncio
async def test_execute_without_name(hello_world_tool):
    """Test execute without name parameter."""
    result = await hello_world_tool.execute({})
    assert result == "Hello, World!"

def test_parameters_schema(hello_world_tool):
    """Test parameters schema structure."""
    schema = hello_world_tool.get_parameters_schema()
    assert schema["type"] == "object"
    assert "name" in schema["properties"]
    assert schema["properties"]["name"]["type"] == "string"
