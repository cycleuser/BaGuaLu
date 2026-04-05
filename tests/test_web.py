"""Tests for BaGuaLu Web API functionality."""

import pytest
from fastapi.testclient import TestClient

from bagualu.core import BaGuaLuCore
from bagualu.web.api_server import app, set_core_instance


@pytest.fixture
async def core_instance():
    """Create and initialize core instance."""
    core = BaGuaLuCore()
    await core.initialize()
    return core


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.mark.asyncio
async def test_api_root(client):
    """Test API root endpoint."""
    response = client.get("/api")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "BaGuaLu API"
    assert data["version"] == "0.1.0"


@pytest.mark.asyncio
async def test_list_models(client, core_instance):
    """Test listing models."""
    set_core_instance(core_instance)
    response = client.get("/models")
    assert response.status_code == 200
    data = response.json()
    assert data["object"] == "list"


@pytest.mark.asyncio
async def test_agent_deployment_api(client, core_instance):
    """Test agent deployment via API."""
    set_core_instance(core_instance)

    response = client.post(
        "/agents",
        json={
            "name": "test-api-agent",
            "role": "executor",
            "provider": "ollama",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "agent_id" in data


@pytest.mark.asyncio
async def test_agent_termination_api(client, core_instance):
    """Test agent termination via API."""
    set_core_instance(core_instance)

    deploy_response = client.post(
        "/agents",
        json={
            "name": "test-terminate-agent",
            "role": "executor",
        },
    )

    assert deploy_response.status_code == 200
    agent_id = deploy_response.json()["agent_id"]

    terminate_response = client.delete(f"/agents/{agent_id}")

    assert terminate_response.status_code == 200
    data = terminate_response.json()
    assert data["success"] is True


@pytest.mark.asyncio
async def test_skill_loading_api(client, core_instance):
    """Test skill loading via API."""
    set_core_instance(core_instance)

    response = client.post(
        "/skills",
        json={
            "name": "test-skill",
            "definition": {
                "name": "test-skill",
                "description": "Test skill for unit testing",
                "instructions": "Test instructions",
            },
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "skill_id" in data or "skill" in data


@pytest.mark.asyncio
async def test_workflow_creation_api(client, core_instance):
    """Test workflow creation via API."""
    set_core_instance(core_instance)

    response = client.post(
        "/workflows",
        json={
            "name": "test-api-workflow",
            "nodes": [
                {
                    "id": "node-1",
                    "role": "executor",
                    "instruction": "Test task",
                }
            ],
            "edges": [],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "workflow_id" in data


@pytest.mark.asyncio
async def test_web_ui(client):
    """Test web UI endpoint."""
    response = client.get("/ui")
    assert response.status_code == 200
    assert "BaGuaLu" in response.text
    assert "八卦炉" in response.text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
