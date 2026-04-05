"""Comprehensive Web API tests for BaGuaLu."""

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


class TestRootEndpoints:
    """Test root and basic endpoints."""

    def test_api_root(self, client):
        """Test API root endpoint."""
        response = client.get("/api")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "BaGuaLu API"
        assert data["version"] == "0.1.0"
        assert "docs" in data

    def test_root_ui(self, client):
        """Test root UI endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        assert "BaGuaLu" in response.text
        assert "八卦炉" in response.text

    def test_web_ui(self, client):
        """Test /ui endpoint."""
        response = client.get("/ui")
        assert response.status_code == 200
        assert "BaGuaLu" in response.text


class TestModelEndpoints:
    """Test model listing endpoints."""

    def test_list_models(self, client, core_instance):
        """Test listing models."""
        set_core_instance(core_instance)
        response = client.get("/models")
        assert response.status_code == 200
        data = response.json()
        assert data["object"] == "list"

    def test_list_models_v1(self, client, core_instance):
        """Test v1 models endpoint."""
        set_core_instance(core_instance)
        response = client.get("/v1/models")
        assert response.status_code == 200
        data = response.json()
        assert data["object"] == "list"


class TestAgentEndpoints:
    """Test agent management endpoints."""

    def test_deploy_agent(self, client, core_instance):
        """Test agent deployment."""
        set_core_instance(core_instance)

        response = client.post(
            "/agents",
            json={
                "name": "test-agent",
                "role": "executor",
                "provider": "ollama",
                "model": "llama2",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "agent_id" in data
        assert "test-agent" in data["agent_id"]

    def test_list_agents(self, client, core_instance):
        """Test listing agents."""
        set_core_instance(core_instance)

        # Deploy an agent first
        client.post("/agents", json={"name": "list-test-agent", "role": "executor"})

        response = client.get("/agents")
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data or "total_agents" in data

    def test_terminate_agent(self, client, core_instance):
        """Test agent termination."""
        set_core_instance(core_instance)

        # Deploy agent
        deploy_response = client.post(
            "/agents", json={"name": "terminate-test", "role": "executor"}
        )
        agent_id = deploy_response.json()["agent_id"]

        # Terminate agent
        terminate_response = client.delete(f"/agents/{agent_id}")
        assert terminate_response.status_code == 200
        data = terminate_response.json()
        assert data["success"] is True

    def test_terminate_nonexistent_agent(self, client, core_instance):
        """Test terminating non-existent agent."""
        set_core_instance(core_instance)

        response = client.delete("/agents/nonexistent-agent-id")
        assert response.status_code == 404


class TestSkillEndpoints:
    """Test skill management endpoints."""

    def test_list_skills(self, client, core_instance):
        """Test listing skills."""
        set_core_instance(core_instance)

        response = client.get("/skills")
        assert response.status_code == 200
        data = response.json()
        assert "skills" in data
        assert "total" in data
        assert isinstance(data["skills"], list)

    def test_list_skill_sources(self, client, core_instance):
        """Test listing skill sources."""
        set_core_instance(core_instance)

        response = client.get("/skills/sources")
        assert response.status_code == 200
        data = response.json()
        assert "sources" in data
        assert isinstance(data["sources"], list)

    def test_get_skill_details(self, client, core_instance):
        """Test getting skill details."""
        set_core_instance(core_instance)

        # First, list skills to get a skill name
        list_response = client.get("/skills")
        skills = list_response.json()["skills"]

        if skills:
            skill_name = skills[0]["name"]
            response = client.get(f"/skills/{skill_name}")
            assert response.status_code == 200
            data = response.json()
            assert "name" in data
            assert "description" in data
            assert "version" in data
            assert "source" in data

    def test_get_nonexistent_skill(self, client, core_instance):
        """Test getting non-existent skill."""
        set_core_instance(core_instance)

        response = client.get("/skills/nonexistent-skill-xyz")
        assert response.status_code == 404

    def test_load_skill_with_definition(self, client, core_instance):
        """Test loading skill with definition."""
        set_core_instance(core_instance)

        response = client.post(
            "/skills",
            json={
                "name": "test-skill-via-api",
                "definition": {
                    "name": "test-skill-via-api",
                    "description": "Test skill created via API",
                    "instructions": "Test instructions",
                    "version": "1.0.0",
                },
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "skill_id" in data or "skill" in data


class TestWorkflowEndpoints:
    """Test workflow management endpoints."""

    def test_create_workflow(self, client, core_instance):
        """Test workflow creation."""
        set_core_instance(core_instance)

        response = client.post(
            "/workflows",
            json={
                "name": "test-workflow",
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

    def test_list_workflows(self, client, core_instance):
        """Test listing workflows."""
        set_core_instance(core_instance)

        # Create a workflow first
        client.post(
            "/workflows",
            json={
                "name": "list-test-workflow",
                "nodes": [{"id": "node-1", "role": "executor", "instruction": "Test"}],
                "edges": [],
            },
        )

        response = client.get("/workflows")
        assert response.status_code == 200
        data = response.json()
        assert "workflows" in data


class TestErrorHandling:
    """Test error handling."""

    def test_404_endpoint(self, client):
        """Test 404 for non-existent endpoint."""
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404

    def test_invalid_json(self, client, core_instance):
        """Test invalid JSON handling."""
        set_core_instance(core_instance)

        response = client.post(
            "/agents", content="invalid json", headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
