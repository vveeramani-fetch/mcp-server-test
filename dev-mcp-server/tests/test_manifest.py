import pytest
from src.manifest import ManifestManager
from src.tools.hello_world import HelloWorldTool

@pytest.fixture
def manifest_manager():
    return ManifestManager()

@pytest.fixture
def hello_world_tool():
    return HelloWorldTool()

def test_manifest_generation(manifest_manager, hello_world_tool):
    """Test manifest generation with tools."""
    tools = [hello_world_tool]
    manifest = manifest_manager.get_manifest(tools)
    
    assert "version" in manifest
    assert "tools" in manifest
    assert len(manifest["tools"]) == 1
    assert manifest["tools"][0]["name"] == "helloworld"

def test_empty_manifest(manifest_manager):
    """Test manifest generation with no tools."""
    manifest = manifest_manager.get_manifest([])
    
    assert "version" in manifest
    assert "tools" in manifest
    assert len(manifest["tools"]) == 0