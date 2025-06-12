import pytest
from fastapi.testclient import TestClient
from src.server import MCPServer

@pytest.fixture
def client():
    server = MCPServer()
    app = server.create_app()
    return TestClient(app)

def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_manifest_endpoint(client):
    """Test manifest endpoint returns proper structure."""
    response = client.get("/manifest")
    assert response.status_code == 200
    
    data = response.json()
    assert "version" in data
    assert "tools" in data
    assert len(data["tools"]) > 0
    
    # Check helloworld tool is present
    tool_names = [tool["name"] for tool in data["tools"]]
    assert "helloworld" in tool_names

def test_helloworld_endpoint(client):
    """Test helloworld tool execution."""
    response = client.post("/helloworld", json={"name": "Test"})
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "success"
    assert data["result"] == "Hello, Test!"

def test_helloworld_endpoint_no_parameters(client):
    """Test helloworld tool with no parameters."""
    response = client.post("/helloworld")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "success"
    assert data["result"] == "Hello, World!"