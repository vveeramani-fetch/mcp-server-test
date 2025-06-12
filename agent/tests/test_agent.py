import pytest
from unittest.mock import AsyncMock, Mock
from src.agent import MCPAgent

@pytest.fixture
def mock_mcp_client():
    return AsyncMock()

@pytest.fixture
def mock_tool_registry():
    return Mock()

@pytest.fixture
def agent_with_mocks(mock_mcp_client, mock_tool_registry, monkeypatch):
    agent = MCPAgent("http://test:8000")
    monkeypatch.setattr(agent, "mcp_client", mock_mcp_client)
    monkeypatch.setattr(agent, "tool_registry", mock_tool_registry)
    return agent

@pytest.mark.asyncio
async def test_discover_tools(agent_with_mocks):
    """Test tool discovery process."""
    tools_response = {"tools": [{"name": "test", "description": "test"}]}
    agent_with_mocks.mcp_client.list_tools.return_value = tools_response
    
    await agent_with_mocks.discover_tools()
    
    agent_with_mocks.mcp_client.list_tools.assert_called_once()
    agent_with_mocks.tool_registry.register_tools_from_list.assert_called_once_with([{"name": "test", "description": "test"}])

@pytest.mark.asyncio
async def test_execute_tool_success(agent_with_mocks):
    """Test successful tool execution."""
    agent_with_mocks.tool_registry.is_tool_registered.return_value = True
    agent_with_mocks.tool_registry.get_tool.return_value = {"name": "test"}
    agent_with_mocks.mcp_client.call_tool.return_value = "result"
    
    result = await agent_with_mocks.execute_tool("test", {"param": "value"})
    
    assert result == "result"
    agent_with_mocks.mcp_client.call_tool.assert_called_once_with("test", {"param": "value"})

@pytest.mark.asyncio
async def test_execute_tool_not_registered(agent_with_mocks):
    """Test tool execution with unregistered tool."""
    agent_with_mocks.tool_registry.is_tool_registered.return_value = False
    
    with pytest.raises(ValueError, match="Tool 'unknown' is not registered"):
        await agent_with_mocks.execute_tool("unknown", {})