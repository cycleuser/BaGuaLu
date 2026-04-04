"""BaGuaLu Core - Main orchestration system for agent clusters."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional

from bagualu.agents import AgentCluster
from bagualu.config import ConfigManager
from bagualu.skills import SkillEngine
from bagualu.workflow import WorkflowEngine
from bagualu.utils.logging import Logger

logger = Logger.get_logger(__name__)


class BaGuaLuCore:
    """Main orchestration system for deploying and managing intelligent agent clusters.

    Features:
    - One-click deployment for single agents, matrices, and clusters
    - Skill loading from OpenCode/Claude Code
    - Multi-provider support (Ollama, LMStudio, OpenAI, Claude, etc.)
    - Workflow orchestration with web-based drag-and-drop design
    - Self-evolving agents and skills
    """

    def __init__(
        self,
        config_path: Optional[Path] = None,
        workspace: Optional[Path] = None,
        skill_dirs: Optional[List[Path]] = None,
    ) -> None:
        """Initialize BaGuaLu core system.

        Args:
            config_path: Path to configuration file
            workspace: Working directory for agents and workflows
            skill_dirs: List of directories containing skills
        """
        self._config_manager = ConfigManager(config_path)
        self._skill_engine = SkillEngine(skill_dirs or [], self._config_manager)
        self._cluster = AgentCluster(self._config_manager, self._skill_engine)
        self._workflow_engine = WorkflowEngine(self._cluster, self._skill_engine)
        self._workspace = workspace or Path.cwd() / ".bagualu"
        self._initialized = False

        logger.info("BaGuaLu core initialized")

    async def initialize(self) -> None:
        """Initialize all components asynchronously."""
        if self._initialized:
            return

        await self._config_manager.load()
        await self._skill_engine.initialize()
        await self._cluster.initialize()
        await self._workflow_engine.initialize()

        self._initialized = True
        logger.info("BaGuaLu core fully initialized")

    async def deploy_agent(
        self,
        name: str,
        role: str = "executor",
        provider: Optional[str] = None,
        model: Optional[str] = None,
        skills: Optional[List[str]] = None,
    ) -> str:
        """Deploy a single agent with specified configuration.

        Args:
            name: Unique agent name
            role: Agent role (executor, supervisor, scheduler, etc.)
            provider: LLM provider name
            model: Model identifier
            skills: List of skill names to load

        Returns:
            Agent ID
        """
        await self.initialize()

        agent_id = await self._cluster.deploy_agent(
            name=name,
            role=role,
            provider=provider,
            model=model,
            skills=skills,
        )

        logger.info(f"Deployed agent: {name} (ID: {agent_id})")
        return agent_id

    async def deploy_cluster(
        self,
        cluster_config: Dict[str, Any],
    ) -> List[str]:
        """Deploy an agent cluster from configuration.

        Args:
            cluster_config: Cluster configuration dictionary
                {
                    "name": "cluster_name",
                    "agents": [
                        {"name": "agent1", "role": "executor", ...},
                        {"name": "agent2", "role": "supervisor", ...},
                    ],
                    "connections": [...]
                }

        Returns:
            List of agent IDs
        """
        await self.initialize()

        agent_ids = await self._cluster.deploy_from_config(cluster_config)
        logger.info(f"Deployed cluster: {cluster_config.get('name')} with {len(agent_ids)} agents")
        return agent_ids

    async def execute_workflow(
        self,
        workflow_id: str,
        inputs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute a workflow with specified inputs.

        Args:
            workflow_id: Workflow ID or name
            inputs: Input data for workflow

        Returns:
            Execution results
        """
        await self.initialize()

        result = await self._workflow_engine.execute(workflow_id, inputs or {})
        logger.info(f"Workflow {workflow_id} executed successfully")
        return result

    async def create_workflow(
        self,
        workflow_config: Dict[str, Any],
    ) -> str:
        """Create a new workflow from configuration.

        Args:
            workflow_config: Workflow configuration
                {
                    "name": "workflow_name",
                    "nodes": [...],
                    "edges": [...],
                    "inputs": [...],
                    "outputs": [...]
                }

        Returns:
            Workflow ID
        """
        await self.initialize()

        workflow_id = await self._workflow_engine.create(workflow_config)
        logger.info(f"Created workflow: {workflow_config.get('name')} (ID: {workflow_id})")
        return workflow_id

    async def evolve_skill(
        self,
        skill_name: str,
        evolution_type: str = "auto",
    ) -> bool:
        """Trigger skill evolution.

        Args:
            skill_name: Skill name to evolve
            evolution_type: Evolution type (fix, derived, captured, auto)

        Returns:
            True if evolution succeeded
        """
        await self.initialize()

        success = await self._skill_engine.evolve(skill_name, evolution_type)
        logger.info(f"Skill {skill_name} evolution: {success}")
        return success

    @property
    def config(self) -> ConfigManager:
        """Get configuration manager."""
        return self._config_manager

    @property
    def skills(self) -> SkillEngine:
        """Get skill engine."""
        return self._skill_engine

    @property
    def cluster(self) -> AgentCluster:
        """Get agent cluster."""
        return self._cluster

    @property
    def workflow(self) -> WorkflowEngine:
        """Get workflow engine."""
        return self._workflow_engine
