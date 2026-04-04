"""Base Agent - Abstract base class for all agents."""

from __future__ import annotations

import asyncio
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from datetime import datetime

from bagualu.utils.logging import Logger

logger = Logger.get_logger(__name__)


class AgentRole(str, Enum):
    """Agent roles."""

    EXECUTOR = "executor"
    SUPERVISOR = "supervisor"
    SCHEDULER = "scheduler"
    OBSERVER = "observer"
    COORDINATOR = "coordinator"


class AgentStatus(str, Enum):
    """Agent status."""

    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    TERMINATED = "terminated"


@dataclass
class AgentContext:
    """Agent execution context."""

    task_id: str
    instruction: str
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class SkillDefinition:
    """Skill definition loaded from SKILL.md."""

    name: str
    description: str
    instructions: str
    triggers: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    examples: List[str] = field(default_factory=list)
    source: Optional[Path] = None


class BaseAgent(ABC):
    """Abstract base class for all intelligent agents.

    Features:
    - Skill loading and execution
    - LLM interaction via multiple providers
    - Task processing and state management
    - Evolution capability
    - Communication with other agents
    """

    def __init__(
        self,
        name: str,
        role: AgentRole,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        skills: Optional[List[str]] = None,
    ) -> None:
        """Initialize agent.

        Args:
            name: Unique agent name
            role: Agent role
            provider: LLM provider (ollama, openai, anthropic, etc.)
            model: Model identifier
            skills: List of skill names to load
        """
        self._name = name
        self._role = role
        self._provider = provider
        self._model = model
        self._skills: Dict[str, SkillDefinition] = {}
        self._status = AgentStatus.INITIALIZING
        self._context: Optional[AgentContext] = None
        self._llm_client: Optional[Any] = None
        self._evolution_history: List[Dict[str, Any]] = []
        self._step = 0

        if skills:
            for skill_name in skills:
                self._load_skill(skill_name)

        logger.info(f"Initialized {self.__class__.__name__}: {name} (role: {role})")

    @property
    def name(self) -> str:
        """Get agent name."""
        return self._name

    @property
    def role(self) -> AgentRole:
        """Get agent role."""
        return self._role

    @property
    def status(self) -> AgentStatus:
        """Get agent status."""
        return self._status

    @property
    def skills(self) -> Dict[str, SkillDefinition]:
        """Get loaded skills."""
        return self._skills

    @property
    def provider(self) -> Optional[str]:
        """Get LLM provider."""
        return self._provider

    @property
    def model(self) -> Optional[str]:
        """Get model identifier."""
        return self._model

    async def initialize(self) -> None:
        """Initialize agent asynchronously."""
        await self._setup_llm_client()
        self._status = AgentStatus.READY
        logger.info(f"Agent {self._name} initialized and ready")

    @abstractmethod
    async def process(
        self,
        instruction: str,
        inputs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Process a task.

        Args:
            instruction: Task instruction
            inputs: Input data

        Returns:
            Processing result
        """
        pass

    @abstractmethod
    async def evolve(self) -> bool:
        """Trigger agent self-evolution.

        Returns:
            True if evolution succeeded
        """
        pass

    async def load_skill(
        self,
        skill_path: Path,
    ) -> bool:
        """Load a skill from SKILL.md file.

        Args:
            skill_path: Path to SKILL.md file

        Returns:
            True if skill loaded successfully
        """
        try:
            skill_def = await self._parse_skill_file(skill_path)
            self._skills[skill_def.name] = skill_def
            logger.info(f"Agent {self._name} loaded skill: {skill_def.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to load skill from {skill_path}: {e}")
            return False

    def _load_skill(self, skill_name: str) -> None:
        """Load a skill by name (synchronous initialization).

        Args:
            skill_name: Skill name to load
        """
        pass

    async def _parse_skill_file(
        self,
        skill_path: Path,
    ) -> SkillDefinition:
        """Parse SKILL.md file to extract skill definition.

        Args:
            skill_path: Path to SKILL.md

        Returns:
            Skill definition
        """
        if not skill_path.exists():
            raise FileNotFoundError(f"Skill file not found: {skill_path}")

        content = await asyncio.to_thread(skill_path.read_text)

        lines = content.strip().split("\n")
        name = lines[0].replace("#", "").strip() if lines else skill_path.parent.name

        description = ""
        instructions = ""
        triggers = []
        parameters = {}
        examples = []

        in_instructions = False
        in_triggers = False

        for line in lines[1:]:
            if line.startswith("## Triggers") or line.startswith("##触发"):
                in_triggers = True
                in_instructions = False
                continue
            elif line.startswith("##") or line.startswith("**"):
                in_triggers = False
                in_instructions = False
                continue

            if in_triggers and line.strip():
                triggers.append(line.strip())
            elif line.strip() and not in_triggers:
                if not instructions:
                    description += line + "\n"
                instructions += line + "\n"

        return SkillDefinition(
            name=name,
            description=description.strip(),
            instructions=instructions.strip(),
            triggers=triggers,
            parameters=parameters,
            examples=examples,
            source=skill_path,
        )

    async def _setup_llm_client(self) -> None:
        """Set up LLM client based on provider configuration."""
        pass

    async def call_llm(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Call LLM with messages and optional tools.

        Args:
            messages: Conversation messages
            tools: Available tools

        Returns:
            LLM response
        """
        if not self._llm_client:
            raise ValueError(f"LLM client not initialized for agent {self._name}")

        try:
            response = await self._llm_client.complete(
                messages=messages,
                tools=tools,
            )
            return response
        except Exception as e:
            logger.error(f"LLM call failed for agent {self._name}: {e}")
            raise

    async def execute_skill(
        self,
        skill_name: str,
        inputs: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute a loaded skill.

        Args:
            skill_name: Skill name
            inputs: Skill inputs

        Returns:
            Skill execution result
        """
        skill = self._skills.get(skill_name)
        if not skill:
            raise ValueError(f"Skill not loaded: {skill_name}")

        messages = [
            {
                "role": "system",
                "content": skill.instructions,
            },
            {
                "role": "user",
                "content": f"Execute skill '{skill_name}' with inputs: {json.dumps(inputs)}",
            },
        ]

        response = await self.call_llm(messages)

        return {
            "skill": skill_name,
            "response": response,
            "inputs": inputs,
        }

    async def update_status(
        self,
        new_status: AgentStatus,
    ) -> None:
        """Update agent status.

        Args:
            new_status: New status
        """
        old_status = self._status
        self._status = new_status
        logger.info(f"Agent {self._name} status: {old_status} -> {new_status}")

    def increment_step(self) -> None:
        """Increment step counter."""
        self._step += 1

    async def communicate(
        self,
        target_agent: str,
        message: Dict[str, Any],
    ) -> None:
        """Send message to another agent.

        Args:
            target_agent: Target agent name
            message: Message content
        """
        logger.info(f"Agent {self._name} communicating with {target_agent}")

    async def shutdown(self) -> None:
        """Shutdown agent."""
        self._status = AgentStatus.TERMINATED
        logger.info(f"Agent {self._name} shutdown")
