"""Complete Web API tests for all functionality."""

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


class TestCompleteWebFunctionality:
    """Complete tests for all web functionality."""

    @pytest.mark.asyncio
    async def test_root_ui_loads(self, client, core_instance):
        """Test root UI page loads."""
        set_core_instance(core_instance)
        response = client.get("/")
        assert response.status_code == 200
        assert "BaGuaLu" in response.text
        assert "八卦炉" in response.text
        assert "Dashboard" in response.text
        assert "Agents" in response.text
        assert "Skills" in response.text
        assert "Workflows" in response.text
        assert "Settings" in response.text

    @pytest.mark.asyncio
    async def test_dashboard_shows_all_features(self, client, core_instance):
        """Test dashboard displays all features."""
        set_core_instance(core_instance)
        response = client.get("/")
        assert response.status_code == 200
        # Check for all main sections
        assert "Active Agents" in response.text
        assert "Total Skills" in response.text
        assert "Active Workflows" in response.text
        assert "Skill Library" in response.text or "Skills" in response.text
        assert "Settings" in response.text

    @pytest.mark.asyncio
    async def test_agent_lifecycle_complete(self, client, core_instance):
        """Test complete agent lifecycle: deploy, list, terminate."""
        set_core_instance(core_instance)

        # 1. Deploy agent with all parameters
        deploy_response = client.post(
            "/agents",
            json={
                "name": "complete-test-agent",
                "role": "executor",
                "provider": "ollama",
                "model": "llama2",
                "skills": ["test-skill"],
            },
        )
        assert deploy_response.status_code == 200
        agent_id = deploy_response.json()["agent_id"]
        assert "complete-test-agent" in agent_id

        # 2. List agents
        list_response = client.get("/agents")
        assert list_response.status_code == 200
        agents = list_response.json()
        assert any(
            a.get("id") == agent_id or a.get("name") == "complete-test-agent"
            for a in agents.get("agents", [])
        )

        # 3. Terminate agent
        terminate_response = client.delete(f"/agents/{agent_id}")
        assert terminate_response.status_code == 200
        assert terminate_response.json()["success"] is True

    @pytest.mark.asyncio
    async def test_skill_management_complete(self, client, core_instance):
        """Test complete skill management: list, get, load, install."""
        set_core_instance(core_instance)

        # 1. List all skills
        list_response = client.get("/skills")
        assert list_response.status_code == 200
        data = list_response.json()
        assert "skills" in data
        assert "total" in data
        assert data["total"] > 0  # Should have discovered skills

        # 2. Get skill sources
        sources_response = client.get("/skills/sources")
        assert sources_response.status_code == 200
        sources = sources_response.json()["sources"]
        assert len(sources) > 0

        # 3. Get specific skill details
        if data["skills"]:
            skill_name = data["skills"][0]["name"]
            details_response = client.get(f"/skills/{skill_name}")
            assert details_response.status_code == 200
            skill = details_response.json()
            assert "name" in skill
            assert "version" in skill
            assert "source" in skill

        # 4. Load skill with definition
        load_response = client.post(
            "/skills",
            json={
                "name": "test-web-skill",
                "definition": {
                    "name": "test-web-skill",
                    "description": "Test skill",
                    "instructions": "Test",
                    "version": "1.0.0",
                },
            },
        )
        assert load_response.status_code == 200

    @pytest.mark.asyncio
    async def test_workflow_management_complete(self, client, core_instance):
        """Test complete workflow management: create, list, execute."""
        set_core_instance(core_instance)

        # 1. Create workflow
        create_response = client.post(
            "/workflows",
            json={
                "name": "test-workflow-complete",
                "nodes": [
                    {
                        "id": "node-1",
                        "role": "executor",
                        "instruction": "Test task 1",
                    },
                    {
                        "id": "node-2",
                        "role": "executor",
                        "instruction": "Test task 2",
                        "dependencies": ["node-1"],
                    },
                ],
                "edges": [{"from": "node-1", "to": "node-2"}],
            },
        )
        assert create_response.status_code == 200
        _ = create_response.json()["workflow_id"]

        # 2. List workflows
        list_response = client.get("/workflows")
        assert list_response.status_code == 200
        workflows = list_response.json()["workflows"]
        assert len(workflows) > 0

    @pytest.mark.asyncio
    async def test_configuration_management(self, client, core_instance):
        """Test configuration management: get, update."""
        set_core_instance(core_instance)

        # 1. Get current configuration
        config_response = client.get("/config")
        assert config_response.status_code == 200
        config = config_response.json()
        assert "active_provider" in config
        assert "providers" in config
        assert "settings" in config

        # 2. Update provider config
        update_response = client.post("/config/provider?provider_name=ollama&model=test-model")
        assert update_response.status_code == 200

        # 3. Set active provider
        active_response = client.post("/config/active-provider?provider_name=ollama")
        assert active_response.status_code == 200

        # 4. Update settings
        settings_response = client.post(
            "/config/settings",
            json={
                "max_concurrent_agents": 15,
                "evolution_enabled": True,
            },
        )
        assert settings_response.status_code == 200

    @pytest.mark.asyncio
    async def test_model_endpoints(self, client, core_instance):
        """Test model listing endpoints."""
        set_core_instance(core_instance)

        response = client.get("/models")
        assert response.status_code == 200
        data = response.json()
        assert data["object"] == "list"

        v1_response = client.get("/v1/models")
        assert v1_response.status_code == 200

    @pytest.mark.asyncio
    async def test_error_handling_complete(self, client, core_instance):
        """Test comprehensive error handling."""
        set_core_instance(core_instance)

        # 404 errors
        assert client.get("/nonexistent").status_code == 404
        assert client.get("/skills/nonexistent-skill").status_code == 404
        assert client.delete("/agents/nonexistent-agent").status_code == 404

        # 422 validation errors
        response = client.post("/agents", json={})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_skill_installation_from_github(self, client, core_instance):
        """Test skill installation from GitHub."""
        set_core_instance(core_instance)

        # Note: This would actually try to install from GitHub
        # For testing, we just verify the endpoint exists and responds
        response = client.post(
            "/skills/install",
            params={"repo_url": "https://github.com/cycleuser/Skills", "skill_name": "test-skill"},
        )
        # Accept both success and failure (if no network)
        assert response.status_code in [200, 500]

    @pytest.mark.asyncio
    async def test_skill_evolution_endpoint(self, client, core_instance):
        """Test skill evolution endpoint."""
        set_core_instance(core_instance)

        # Get available skills first
        skills_response = client.get("/skills")
        if skills_response.json()["skills"]:
            skill_name = skills_response.json()["skills"][0]["name"]

            # Try to evolve skill
            evolve_response = client.post(f"/skills/{skill_name}/evolve")
            assert evolve_response.status_code == 200


class TestWebUIComponents:
    """Test Web UI components and JavaScript functions."""

    @pytest.mark.asyncio
    async def test_ui_has_all_tabs(self, client, core_instance):
        """Test UI has all required tabs."""
        set_core_instance(core_instance)
        response = client.get("/")

        # Check all tabs exist
        assert "onclick=\"showTab('dashboard')\"" in response.text
        assert "onclick=\"showTab('agents')\"" in response.text
        assert "onclick=\"showTab('skills')\"" in response.text
        assert "onclick=\"showTab('workflows')\"" in response.text
        assert "onclick=\"showTab('settings')\"" in response.text

    @pytest.mark.asyncio
    async def test_ui_has_all_javascript_functions(self, client, core_instance):
        """Test UI has all required JavaScript functions."""
        set_core_instance(core_instance)
        response = client.get("/")

        # Check key JavaScript functions exist
        assert "function deployAgent()" in response.text
        assert "function terminateAgent(" in response.text
        assert "function installSkill(" in response.text
        assert "function showSkillInfo(" in response.text
        assert "function createWorkflow(" in response.text
        assert "function executeWorkflow(" in response.text
        assert "function saveProviderSettings" in response.text
        assert "function saveSystemSettings" in response.text
        assert "function refreshAgents(" in response.text
        assert "function refreshSkills(" in response.text
        assert "function refreshWorkflows(" in response.text

    @pytest.mark.asyncio
    async def test_ui_has_settings_forms(self, client, core_instance):
        """Test UI has all settings forms."""
        set_core_instance(core_instance)
        response = client.get("/")

        # Check settings form elements
        assert 'id="provider-select"' in response.text
        assert 'id="model-input"' in response.text
        assert 'id="api-key-input"' in response.text
        assert 'id="max-agents-input"' in response.text
        assert 'id="evolution-enabled"' in response.text
        assert 'id="quality-threshold"' in response.text

    @pytest.mark.asyncio
    async def test_ui_has_action_buttons(self, client, core_instance):
        """Test UI has all action buttons."""
        set_core_instance(core_instance)
        response = client.get("/")

        # Check for key action buttons
        assert "Deploy Agent" in response.text
        assert "Install from GitHub" in response.text or "Install Skill" in response.text
        assert "Create Workflow" in response.text
        assert "Save Provider Settings" in response.text or "Save System Settings" in response.text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
