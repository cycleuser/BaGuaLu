"""Resource Manager - Agent and resource allocation management."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

from bagualu.utils.logging import Logger

logger = Logger.get_logger(__name__)


class ResourceType(str, Enum):
    """Resource types."""

    AGENT = "agent"
    COMPUTE = "compute"
    MEMORY = "memory"
    NETWORK = "network"


class AgentState(str, Enum):
    """Agent states."""

    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


@dataclass
class AgentInfo:
    """Agent information."""

    id: str
    name: str
    role: str
    state: AgentState = AgentState.IDLE
    provider: Optional[str] = None
    model: Optional[str] = None
    skills: List[str] = field(default_factory=list)
    current_task: Optional[str] = None
    allocated_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourceRequest:
    """Resource request specification."""

    request_id: str
    task_id: str
    required_role: Optional[str] = None
    required_skills: List[str] = field(default_factory=list)
    priority: int = 5
    timeout: timedelta = field(default_factory=lambda: timedelta(minutes=30))
    created_at: datetime = field(default_factory=datetime.now)


class ResourceManager:
    """Manages agent and resource allocation.

    Responsibilities:
    - Agent lifecycle management (registration, allocation, release)
    - Resource tracking and monitoring
    - Load balancing and scheduling optimization
    - Resource cleanup and garbage collection
    """

    def __init__(
        self,
        cluster: Any,
        max_concurrent_agents: int = 10,
    ) -> None:
        """Initialize resource manager.

        Args:
            cluster: Agent cluster instance
            max_concurrent_agents: Maximum number of concurrently active agents
        """
        self._cluster = cluster
        self._max_concurrent_agents = max_concurrent_agents
        self._agents: Dict[str, AgentInfo] = {}
        self._allocation_queue: asyncio.Queue[ResourceRequest] = asyncio.Queue()
        self._pending_requests: Dict[str, ResourceRequest] = {}
        self._running = False

        logger.info(f"Resource manager initialized (max agents: {max_concurrent_agents})")

    async def initialize(self) -> None:
        """Initialize resource manager."""
        self._running = True
        asyncio.create_task(self._allocation_loop())
        logger.info("Resource manager started")

    async def register_agent(
        self,
        agent_id: str,
        name: str,
        role: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        skills: Optional[List[str]] = None,
    ) -> None:
        """Register a new agent.

        Args:
            agent_id: Unique agent ID
            name: Agent name
            role: Agent role
            provider: LLM provider
            model: Model identifier
            skills: List of available skills
        """
        info = AgentInfo(
            id=agent_id,
            name=name,
            role=role,
            provider=provider,
            model=model,
            skills=skills or [],
        )

        self._agents[agent_id] = info
        logger.info(f"Registered agent: {name} (ID: {agent_id})")

    async def allocate_agent(
        self,
        task: Any,
    ) -> str:
        """Allocate an agent for a task.

        Args:
            task: Task definition

        Returns:
            Allocated agent ID

        Raises:
            ValueError: If no suitable agent is available
        """
        request = ResourceRequest(
            request_id=f"req-{datetime.now().timestamp()}",
            task_id=task.id,
            required_role=task.required_role,
            required_skills=task.required_skills,
            priority=task.priority,
        )

        self._pending_requests[request.request_id] = request

        try:
            agent_id = await asyncio.wait_for(
                self._find_available_agent(request),
                timeout=request.timeout.total_seconds(),
            )

            agent = self._agents[agent_id]
            agent.state = AgentState.BUSY
            agent.current_task = task.id
            agent.allocated_at = datetime.now()

            logger.info(f"Allocated agent {agent_id} for task {task.id}")
            return agent_id
        except asyncio.TimeoutError:
            self._pending_requests.pop(request.request_id, None)
            raise ValueError(f"No agent available for task {task.id} within timeout")

    async def release_agent(
        self,
        agent_id: str,
    ) -> None:
        """Release an allocated agent.

        Args:
            agent_id: Agent ID to release
        """
        agent = self._agents.get(agent_id)
        if agent:
            agent.state = AgentState.IDLE
            agent.current_task = None
            agent.allocated_at = None
            logger.info(f"Released agent {agent_id}")

    async def _find_available_agent(
        self,
        request: ResourceRequest,
    ) -> str:
        """Find an available agent matching request requirements.

        Args:
            request: Resource request

        Returns:
            Agent ID
        """
        suitable_agents = [
            agent_id
            for agent_id, info in self._agents.items()
            if info.state == AgentState.IDLE and self._matches_requirements(info, request)
        ]

        if not suitable_agents:
            await asyncio.sleep(0.1)
            return await self._find_available_agent(request)

        return suitable_agents[0]

    def _matches_requirements(
        self,
        agent: AgentInfo,
        request: ResourceRequest,
    ) -> bool:
        """Check if agent matches request requirements.

        Args:
            agent: Agent info
            request: Resource request

        Returns:
            True if agent matches requirements
        """
        if request.required_role and agent.role != request.required_role:
            return False

        if request.required_skills:
            if not all(skill in agent.skills for skill in request.required_skills):
                return False

        return True

    async def _allocation_loop(self) -> None:
        """Background loop for processing allocation requests."""
        while self._running:
            try:
                await asyncio.sleep(0.1)
            except asyncio.CancelledError:
                break

    async def get_agent_status(
        self,
        agent_id: str,
    ) -> Dict[str, Any]:
        """Get agent status.

        Args:
            agent_id: Agent ID

        Returns:
            Agent status dictionary
        """
        agent = self._agents.get(agent_id)
        if not agent:
            return {"error": "Agent not found"}

        return {
            "id": agent.id,
            "name": agent.name,
            "role": agent.role,
            "state": agent.state.value,
            "provider": agent.provider,
            "model": agent.model,
            "skills": agent.skills,
            "current_task": agent.current_task,
            "allocated_at": agent.allocated_at.isoformat() if agent.allocated_at else None,
        }

    async def get_all_agents_status(self) -> List[Dict[str, Any]]:
        """Get status of all agents.

        Returns:
            List of agent status dictionaries
        """
        return [await self.get_agent_status(agent_id) for agent_id in self._agents]

    async def cleanup_stale_agents(
        self,
        max_idle_time: timedelta = timedelta(hours=1),
    ) -> List[str]:
        """Clean up agents that have been idle for too long.

        Args:
            max_idle_time: Maximum idle time before cleanup

        Returns:
            List of cleaned up agent IDs
        """
        now = datetime.now()
        stale_agents = []

        for agent_id, info in self._agents.items():
            if info.state == AgentState.IDLE and info.allocated_at:
                idle_time = now - info.allocated_at
                if idle_time > max_idle_time:
                    stale_agents.append(agent_id)

        for agent_id in stale_agents:
            await self._cluster.terminate_agent(agent_id)
            self._agents.pop(agent_id, None)
            logger.info(f"Cleaned up stale agent {agent_id}")

        return stale_agents

    async def shutdown(self) -> None:
        """Shutdown resource manager."""
        self._running = False

        for agent_id in self._agents:
            await self._cluster.terminate_agent(agent_id)

        self._agents.clear()
        logger.info("Resource manager shutdown complete")
