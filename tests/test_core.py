"""Tests for BaGuaLu core functionality."""

import pytest
from pathlib import Path

from bagualu.core import BaGuaLuCore
from bagualu.config import ConfigManager


@pytest.mark.asyncio
async def test_core_initialization():
    """Test BaGuaLu core initialization."""
    core = BaGuaLuCore()

    assert core is not None
    assert core.config is not None
    assert core.skills is not None
    assert core.cluster is not None


@pytest.mark.asyncio
async def test_agent_deployment():
    """Test agent deployment."""
    core = BaGuaLuCore()
    await core.initialize()

    agent_id = await core.deploy_agent(
        name="test-agent",
        role="executor",
        provider="ollama",
        model="llama2",
    )

    assert agent_id is not None
    assert "test-agent" in agent_id


@pytest.mark.asyncio
async def test_workflow_creation():
    """Test workflow creation."""
    core = BaGuaLuCore()
    await core.initialize()

    workflow_config = {
        "name": "test-workflow",
        "nodes": [
            {"id": "task1", "role": "executor", "instruction": "Test task"},
        ],
        "edges": [],
    }

    workflow_id = await core.create_workflow(workflow_config)

    assert workflow_id is not None


@pytest.mark.asyncio
async def test_skill_loading():
    """Test skill loading."""
    core = BaGuaLuCore()
    await core.initialize()

    skills = await core.skills.get_all_skills()

    assert isinstance(skills, list)


def test_config_manager():
    """Test configuration manager."""
    config = ConfigManager()

    assert config is not None
    assert config.providers is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
