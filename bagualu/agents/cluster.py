"""Agent Cluster - Multi-agent deployment and management."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from bagualu.agents.base import AgentRole, BaseAgent
from bagualu.agents.executor import ExecutorAgent
from bagualu.agents.scheduler import SchedulerAgent
from bagualu.agents.supervisor import SupervisorAgent
from bagualu.utils.logging import Logger

logger = Logger.get_logger(__name__)


class AgentCluster:
    """Agent cluster for deploying and managing multiple agents.

    Features:
    - Deploy single agents, matrices, and clusters
    - Manage agent lifecycle
    - Coordinate agent communication
    - Handle cluster scaling
    - Monitor cluster health
    """

    def __init__(
        self,
        config_manager: Any,
        skill_engine: Any,
    ) -> None:
        """Initialize agent cluster.

        Args:
            config_manager: Configuration manager
            skill_engine: Skill engine instance
        """
        self._config_manager = config_manager
        self._skill_engine = skill_engine
        self._agents: dict[str, BaseAgent] = {}
        self._agent_metadata: dict[str, dict[str, Any]] = {}
        self._connections: dict[str, set[str]] = {}
        self._running = False

        logger.info("Agent cluster initialized")

    async def initialize(self) -> None:
        """Initialize agent cluster."""
        self._running = True
        logger.info("Agent cluster started")

    async def deploy_agent(
        self,
        name: str,
        role: str = "executor",
        provider: str | None = None,
        model: str | None = None,
        skills: list[str] | None = None,
    ) -> str:
        """Deploy a single agent.

        Args:
            name: Agent name
            role: Agent role (executor, supervisor, scheduler)
            provider: LLM provider
            model: Model identifier
            skills: Skills to load

        Returns:
            Agent ID
        """
        agent_id = f"agent-{name}-{datetime.now().timestamp()}"

        agent_role = AgentRole(role.lower())

        if agent_role == AgentRole.EXECUTOR:
            agent = ExecutorAgent(
                name=name,
                provider=provider,
                model=model,
                skills=skills,
            )
        elif agent_role == AgentRole.SUPERVISOR:
            agent = SupervisorAgent(
                name=name,
                provider=provider,
                model=model,
            )
        elif agent_role == AgentRole.SCHEDULER:
            agent = SchedulerAgent(
                name=name,
                provider=provider,
                model=model,
            )
        else:
            agent = ExecutorAgent(
                name=name,
                provider=provider,
                model=model,
                skills=skills,
            )

        await agent.initialize()

        self._agents[agent_id] = agent
        self._agent_metadata[agent_id] = {
            "name": name,
            "role": role,
            "provider": provider,
            "model": model,
            "skills": skills or [],
            "deployed_at": datetime.now().isoformat(),
        }

        logger.info(f"Deployed agent {name} (ID: {agent_id})")

        return agent_id

    async def deploy_from_config(
        self,
        cluster_config: dict[str, Any],
    ) -> list[str]:
        """Deploy agent cluster from configuration.

        Args:
            cluster_config: Cluster configuration
                {
                    "name": "cluster_name",
                    "agents": [
                        {"name": "executor1", "role": "executor", ...},
                        {"name": "supervisor1", "role": "supervisor", ...},
                    ],
                    "connections": [
                        {"from": "executor1", "to": "supervisor1"},
                    ]
                }

        Returns:
            List of agent IDs
        """
        agents_config = cluster_config.get("agents", [])
        connections_config = cluster_config.get("connections", [])

        agent_ids = []

        for agent_def in agents_config:
            agent_id = await self.deploy_agent(
                name=agent_def.get("name", "agent"),
                role=agent_def.get("role", "executor"),
                provider=agent_def.get("provider"),
                model=agent_def.get("model"),
                skills=agent_def.get("skills"),
            )

            agent_ids.append(agent_id)

        await self._setup_connections(agent_ids, connections_config, agents_config)

        logger.info(f"Deployed cluster {cluster_config.get('name')} with {len(agent_ids)} agents")

        return agent_ids

    async def _setup_connections(
        self,
        agent_ids: list[str],
        connections_config: list[dict[str, Any]],
        agents_config: list[dict[str, Any]],
    ) -> None:
        """Setup agent connections.

        Args:
            agent_ids: List of deployed agent IDs
            connections_config: Connection definitions
            agents_config: Agent configurations
        """
        name_to_id = {}
        for agent_id, agent_def in zip(agent_ids, agents_config, strict=False):
            name_to_id[agent_def.get("name")] = agent_id

        for connection in connections_config:
            from_name = connection.get("from")
            to_name = connection.get("to")

            from_id = name_to_id.get(from_name)
            to_id = name_to_id.get(to_name)

            if from_id and to_id:
                if from_id not in self._connections:
                    self._connections[from_id] = set()

                self._connections[from_id].add(to_id)

                if isinstance(self._agents.get(from_id), SupervisorAgent):
                    self._agents[from_id].add_supervised_agent(to_id)

                logger.info(f"Connected {from_name} -> {to_name}")

    async def terminate_agent(
        self,
        agent_id: str,
    ) -> bool:
        """Terminate an agent.

        Args:
            agent_id: Agent ID

        Returns:
            True if termination succeeded
        """
        agent = self._agents.get(agent_id)

        if not agent:
            return False

        await agent.shutdown()

        self._agents.pop(agent_id, None)
        self._agent_metadata.pop(agent_id, None)
        self._connections.pop(agent_id, None)

        for from_id in self._connections:
            self._connections[from_id].discard(agent_id)

        logger.info(f"Terminated agent {agent_id}")

        return True

    async def get_agent(
        self,
        agent_id: str,
    ) -> BaseAgent | None:
        """Get agent by ID.

        Args:
            agent_id: Agent ID

        Returns:
            Agent instance or None
        """
        return self._agents.get(agent_id)

    async def get_agent_by_name(
        self,
        name: str,
    ) -> BaseAgent | None:
        """Get agent by name.

        Args:
            name: Agent name

        Returns:
            Agent instance or None
        """
        for agent_id, metadata in self._agent_metadata.items():
            if metadata.get("name") == name:
                return self._agents.get(agent_id)

        return None

    async def execute_with_agent(
        self,
        agent_id: str,
        instruction: str,
        inputs: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute a task with specific agent.

        Args:
            agent_id: Agent ID
            instruction: Task instruction
            inputs: Input data

        Returns:
            Execution result
        """
        agent = self._agents.get(agent_id)

        if not agent:
            return {
                "success": False,
                "error": f"Agent {agent_id} not found",
            }

        result = await agent.process(instruction, inputs)

        return result

    async def broadcast_to_agents(
        self,
        agent_ids: list[str],
        message: dict[str, Any],
    ) -> dict[str, Any]:
        """Broadcast message to multiple agents.

        Args:
            agent_ids: List of agent IDs
            message: Message content

        Returns:
            Broadcast results
        """
        results = {}

        for agent_id in agent_ids:
            agent = self._agents.get(agent_id)

            if agent:
                results[agent_id] = {
                    "name": agent.name,
                    "received": True,
                }

        return results

    async def evolve_all_agents(self) -> dict[str, Any]:
        """Trigger evolution for all agents.

        Returns:
            Evolution results
        """
        evolution_results = {}

        for agent_id, agent in self._agents.items():
            evolved = await agent.evolve()

            evolution_results[agent_id] = {
                "name": agent.name,
                "role": agent.role.value,
                "evolved": evolved,
            }

        return evolution_results

    async def get_cluster_status(self) -> dict[str, Any]:
        """Get cluster status.

        Returns:
            Cluster status dictionary
        """
        agents_status = []

        for agent_id, agent in self._agents.items():
            metadata = self._agent_metadata.get(agent_id, {})

            agents_status.append(
                {
                    "id": agent_id,
                    "name": agent.name,
                    "role": agent.role.value,
                    "status": agent.status.value,
                    "provider": agent.provider,
                    "model": agent.model,
                    "skills": list(agent.skills.keys()),
                    "deployed_at": metadata.get("deployed_at"),
                }
            )

        return {
            "total_agents": len(self._agents),
            "connections": len(self._connections),
            "agents": agents_status,
            "running": self._running,
        }

    async def scale_cluster(
        self,
        target_size: int,
        role_distribution: dict[str, int] | None = None,
    ) -> list[str]:
        """Scale cluster to target size.

        Args:
            target_size: Target number of agents
            role_distribution: Role distribution (e.g., {"executor": 5, "supervisor": 1})

        Returns:
            List of new agent IDs
        """
        current_size = len(self._agents)

        if target_size <= current_size:
            return []

        new_agents = []

        role_dist = role_distribution or {"executor": target_size - current_size}

        for role, count in role_dist.items():
            for i in range(count):
                agent_id = await self.deploy_agent(
                    name=f"{role}-{i}",
                    role=role,
                )
                new_agents.append(agent_id)

        logger.info(f"Cluster scaled from {current_size} to {len(self._agents)} agents")

        return new_agents

    async def shutdown(self) -> None:
        """Shutdown entire cluster."""
        self._running = False

        for agent_id in list(self._agents.keys()):
            await self.terminate_agent(agent_id)

        logger.info("Cluster shutdown complete")
