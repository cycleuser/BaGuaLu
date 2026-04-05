"""Scheduler Agent - Resource scheduling and task prioritization."""

from __future__ import annotations

import heapq
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, StrEnum
from typing import Any

from bagualu.agents.base import AgentRole, BaseAgent
from bagualu.utils.logging import Logger

logger = Logger.get_logger(__name__)


class PriorityLevel(int, Enum):
    """Task priority levels."""

    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BACKGROUND = 5


class SchedulingStrategy(StrEnum):
    """Scheduling strategies."""

    FIFO = "fifo"
    PRIORITY = "priority"
    ROUND_ROBIN = "round_robin"
    DEADLINE = "deadline"
    ADAPTIVE = "adaptive"


@dataclass
class ScheduledTask:
    """Scheduled task information."""

    task_id: str
    priority: PriorityLevel
    deadline: datetime | None = None
    estimated_duration: timedelta | None = None
    required_resources: dict[str, Any] = field(default_factory=dict)
    dependencies: list[str] = field(default_factory=list)
    assigned_agent: str | None = None
    scheduled_at: datetime | None = None
    completed_at: datetime | None = None


class SchedulerAgent(BaseAgent):
    """Scheduler agent for task scheduling and resource allocation.

    Responsibilities:
    - Schedule tasks based on priority and dependencies
    - Allocate resources efficiently
    - Handle deadline constraints
    - Balance workload across agents
    - Optimize scheduling strategy
    """

    def __init__(
        self,
        name: str,
        provider: str | None = None,
        model: str | None = None,
        strategy: SchedulingStrategy = SchedulingStrategy.PRIORITY,
        max_concurrent_tasks: int = 5,
    ) -> None:
        """Initialize scheduler agent.

        Args:
            name: Agent name
            provider: LLM provider
            model: Model identifier
            strategy: Scheduling strategy
            max_concurrent_tasks: Maximum concurrent tasks
        """
        super().__init__(
            name=name,
            role=AgentRole.SCHEDULER,
            provider=provider,
            model=model,
        )

        self._strategy = strategy
        self._max_concurrent_tasks = max_concurrent_tasks
        self._task_queue: list[tuple[int, ScheduledTask]] = []
        self._active_tasks: dict[str, ScheduledTask] = {}
        self._completed_tasks: list[ScheduledTask] = []
        self._resource_pool: dict[str, set[str]] = {}
        self._scheduling_history: list[dict[str, Any]] = []

        logger.info(f"Scheduler agent {name} initialized with {strategy} strategy")

    async def process(
        self,
        instruction: str,
        inputs: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Process scheduling request.

        Args:
            instruction: Scheduling instruction
            inputs: Input data

        Returns:
            Scheduling result
        """
        inputs = inputs or {}

        try:
            if "schedule" in instruction.lower():
                return await self._handle_schedule_request(inputs)

            if "prioritize" in instruction.lower():
                return await self._handle_prioritize_request(inputs)

            if "allocate" in instruction.lower():
                return await self._handle_allocate_request(inputs)

            return await self._general_scheduling(instruction, inputs)
        except Exception as e:
            logger.error(f"Scheduler {self._name} failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent": self._name,
            }

    async def _handle_schedule_request(
        self,
        inputs: dict[str, Any],
    ) -> dict[str, Any]:
        """Handle task scheduling request.

        Args:
            inputs: Schedule request inputs

        Returns:
            Scheduling result
        """
        task_def = inputs.get("task", {})

        scheduled_task = ScheduledTask(
            task_id=task_def.get("id", f"task-{len(self._task_queue)}"),
            priority=PriorityLevel(task_def.get("priority", PriorityLevel.MEDIUM.value)),
            deadline=task_def.get("deadline"),
            estimated_duration=task_def.get("estimated_duration"),
            required_resources=task_def.get("required_resources", {}),
            dependencies=task_def.get("dependencies", []),
        )

        if self._strategy == SchedulingStrategy.PRIORITY:
            heapq.heappush(
                self._task_queue,
                (int(scheduled_task.priority.value), scheduled_task),
            )
        else:
            self._task_queue.append((int(scheduled_task.priority.value), scheduled_task))

        logger.info(
            f"Task {scheduled_task.task_id} scheduled with priority {scheduled_task.priority.name}"
        )

        return {
            "success": True,
            "task_id": scheduled_task.task_id,
            "priority": scheduled_task.priority.name,
            "queue_position": len(self._task_queue),
            "agent": self._name,
        }

    async def _handle_prioritize_request(
        self,
        inputs: dict[str, Any],
    ) -> dict[str, Any]:
        """Handle task prioritization request.

        Args:
            inputs: Prioritize request inputs

        Returns:
            Prioritization result
        """
        task_id = inputs.get("task_id")
        new_priority = inputs.get("priority")

        if not task_id or not new_priority:
            return {
                "success": False,
                "error": "Missing task_id or priority",
            }

        for i, (priority, task) in enumerate(self._task_queue):
            if task.task_id == task_id:
                new_task = ScheduledTask(
                    task_id=task.task_id,
                    priority=PriorityLevel(new_priority),
                    deadline=task.deadline,
                    estimated_duration=task.estimated_duration,
                    required_resources=task.required_resources,
                    dependencies=task.dependencies,
                )

                self._task_queue[i] = (new_priority, new_task)
                heapq.heapify(self._task_queue)

                logger.info(
                    f"Task {task_id} priority changed to {PriorityLevel(new_priority).name}"
                )

                return {
                    "success": True,
                    "task_id": task_id,
                    "old_priority": PriorityLevel(priority).name,
                    "new_priority": PriorityLevel(new_priority).name,
                }

        return {
            "success": False,
            "error": f"Task {task_id} not found in queue",
        }

    async def _handle_allocate_request(
        self,
        inputs: dict[str, Any],
    ) -> dict[str, Any]:
        """Handle resource allocation request.

        Args:
            inputs: Allocate request inputs

        Returns:
            Allocation result
        """
        if len(self._active_tasks) >= self._max_concurrent_tasks:
            return {
                "success": False,
                "error": "Maximum concurrent tasks reached",
            }

        if not self._task_queue:
            return {
                "success": False,
                "error": "No tasks in queue",
            }

        next_task = await self._get_next_task()

        if next_task:
            next_task.scheduled_at = datetime.now()
            self._active_tasks[next_task.task_id] = next_task

            logger.info(f"Task {next_task.task_id} allocated")

            return {
                "success": True,
                "task_id": next_task.task_id,
                "priority": next_task.priority.name,
                "scheduled_at": next_task.scheduled_at.isoformat(),
            }

        return {
            "success": False,
            "error": "No suitable task available",
        }

    async def _get_next_task(self) -> ScheduledTask | None:
        """Get next task based on scheduling strategy.

        Returns:
            Next scheduled task or None
        """
        if not self._task_queue:
            return None

        if self._strategy == SchedulingStrategy.PRIORITY:
            if self._task_queue:
                priority, task = heapq.heappop(self._task_queue)
                return task
            return None

        if self._strategy == SchedulingStrategy.FIFO:
            if self._task_queue:
                _, task = self._task_queue.pop(0)
                return task
            return None

        if self._strategy == SchedulingStrategy.DEADLINE:
            sorted_tasks = sorted(
                [t for _, t in self._task_queue],
                key=lambda t: t.deadline or datetime.max,
            )
            if sorted_tasks:
                task = sorted_tasks[0]
                self._task_queue = [
                    (p, t) for p, t in self._task_queue if t.task_id != task.task_id
                ]
                heapq.heapify(self._task_queue)
                return task

        if self._task_queue:
            _, task = self._task_queue.pop(0)
            return task
        return None

    async def _general_scheduling(
        self,
        instruction: str,
        inputs: dict[str, Any],
    ) -> dict[str, Any]:
        """Handle general scheduling request.

        Args:
            instruction: Instruction
            inputs: Inputs

        Returns:
            Scheduling result
        """
        messages = [
            {
                "role": "system",
                "content": "You are a scheduler agent. Provide scheduling recommendations.",
            },
            {
                "role": "user",
                "content": f"Instruction: {instruction}\n\nInputs: {inputs}",
            },
        ]

        response = await self.call_llm(messages)

        return {
            "success": True,
            "recommendation": response,
            "agent": self._name,
        }

    async def evolve(self) -> bool:
        """Evolve scheduler agent based on performance.

        Returns:
            True if evolution succeeded
        """
        if len(self._completed_tasks) < 10:
            return False

        avg_completion_time = self._calculate_avg_completion_time()

        if avg_completion_time and avg_completion_time > timedelta(minutes=5):
            logger.info(f"Scheduler {self._name} needs optimization")
            return True

        return False

    def _calculate_avg_completion_time(self) -> timedelta | None:
        """Calculate average completion time for tasks.

        Returns:
            Average completion time or None
        """
        completed_with_times = [
            t for t in self._completed_tasks if t.scheduled_at and t.completed_at
        ]

        if not completed_with_times:
            return None

        total_time = sum(
            (t.completed_at - t.scheduled_at).total_seconds()
            for t in completed_with_times
            if t.completed_at and t.scheduled_at
        )

        return timedelta(seconds=total_time / len(completed_with_times))

    async def complete_task(
        self,
        task_id: str,
    ) -> None:
        """Mark a task as completed.

        Args:
            task_id: Task ID
        """
        task = self._active_tasks.pop(task_id, None)

        if task:
            task.completed_at = datetime.now()
            self._completed_tasks.append(task)

            logger.info(f"Task {task_id} completed")

    async def get_queue_status(self) -> dict[str, Any]:
        """Get current queue status.

        Returns:
            Queue status dictionary
        """
        return {
            "scheduler": self._name,
            "strategy": self._strategy.value,
            "queued_tasks": len(self._task_queue),
            "active_tasks": len(self._active_tasks),
            "completed_tasks": len(self._completed_tasks),
            "max_concurrent": self._max_concurrent_tasks,
            "queue_details": [
                {
                    "task_id": task.task_id,
                    "priority": task.priority.name,
                    "deadline": task.deadline.isoformat() if task.deadline else None,
                }
                for _, task in self._task_queue[:10]
            ],
        }

    async def optimize_strategy(self) -> dict[str, Any]:
        """Analyze and optimize scheduling strategy.

        Returns:
            Optimization analysis
        """
        analysis: dict[str, Any] = {
            "current_strategy": self._strategy.value,
            "performance_metrics": {},
            "recommendation": None,
        }

        avg_time = self._calculate_avg_completion_time()

        if avg_time:
            analysis["performance_metrics"]["avg_completion_time"] = avg_time.total_seconds()

        missed_deadlines = [
            t
            for t in self._completed_tasks
            if t.deadline and t.completed_at and t.completed_at > t.deadline
        ]

        analysis["performance_metrics"]["missed_deadlines"] = len(missed_deadlines)

        if len(missed_deadlines) > len(self._completed_tasks) * 0.1:
            analysis["recommendation"] = "Switch to deadline-based scheduling"

        return analysis
