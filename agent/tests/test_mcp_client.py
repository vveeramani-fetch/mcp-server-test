import pytest
from unittest.mock import AsyncMock, Mock
import httpx
from src.mcp_client import MCPClient

@pytest.fixture
def mock_httpx_client():
    return AsyncMock()

@pytest.fixture
def mcp_client_with_mock(mock_httpx_client, monkeypatch):
    client = MCPClient("http://test:8000")
    monkeypatch.setattr(client, "client", mock_httpx_client)
    return client

@pytest.mark.asyncio
async def test_initialize_success(mcp_client_with_mock):
    """Test successful MCP initialization."""
    expected_response = {"jsonrpc": "2.0", "result": {"protocolVersion": "2024-11-05"}, "id": 2}
    mock_response = Mock()
    mock_response.json.return_value = expected_response
    mock_response.raise_for_status.return_value = None
    
    mcp_client_with_mock.client.post.return_value = mock_response
    
    result = await mcp_client_with_mock.initialize()
    
    assert result == {"protocolVersion": "2024-11-05"}
    assert mcp_client_with_mock.initialized == True

@pytest.mark.asyncio
async def test_list_tools_success(mcp_client_with_mock):
    """Test successful tools listing."""
    expected_response = {"jsonrpc": "2.0", "result": {"tools": [{"name": "helloworld"}]}, "id": 3}
    mock_response = Mock()
    mock_response.json.return_value = expected_response
    mock_response.raise_for_status.return_value = None
    
    mcp_client_with_mock.client.post.return_value = mock_response
    mcp_client_with_mock.initialized = True
    
    result = await mcp_client_with_mock.list_tools()
    
    assert result == {"tools": [{"name": "helloworld"}]}

@pytest.mark.asyncio
async def test_call_tool_success(mcp_client_with_mock):
    """Test successful tool call."""
    expected_response = {"jsonrpc": "2.0", "result": {"content": [{"type": "text", "text": "Hello, World!"}]}, "id": 4}
    mock_response = Mock()
    mock_response.json.return_value = expected_response
    mock_response.raise_for_status.return_value = None
    
    mcp_client_with_mock.client.post.return_value = mock_response
    mcp_client_with_mock.initialized = True
    
    result = await mcp_client_with_mock.call_tool("helloworld", {"name": "World"})
    
    assert result == {"content": [{"type": "text", "text": "Hello, World!"}]}

@pytest.mark.asyncio
async def test_connection_error(mcp_client_with_mock):
    """Test connection error handling."""
    mcp_client_with_mock.client.post.side_effect = httpx.RequestError("Connection failed")
    
    with pytest.raises(ConnectionError, match="Failed to connect to MCP server"):
        await mcp_client_with_mock.initialize()
