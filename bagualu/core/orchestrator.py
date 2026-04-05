"""Orchestrator - Workflow execution and agent coordination."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any

from bagualu.utils.logging import Logger

logger = Logger.get_logger(__name__)


class OrchestrationStrategy(StrEnum):
    """Orchestration strategies for agent coordination."""

    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    ROUND_ROBIN = "round_robin"
    PRIORITY = "priority"
    ADAPTIVE = "adaptive"


@dataclass
class OrchestrationContext:
    """Context for orchestration execution."""

    workflow_id: str
    inputs: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, Any] = field(default_factory=dict)
    active_agents: set[str] = field(default_factory=set)
    completed_tasks: list[str] = field(default_factory=list)
    failed_tasks: list[str] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime | None = None
    strategy: OrchestrationStrategy = OrchestrationStrategy.ADAPTIVE


class Orchestrator:
    """Orchestrates workflow execution and coordinates agents.

    Responsibilities:
    - Execute workflows according to defined DAG
    - Coordinate agents based on orchestration strategy
    - Handle task dependencies and parallel execution
    - Monitor execution progress and handle failures
    - Optimize resource allocation
    """

    def __init__(
        self,
        workflow_engine: Any,
        resource_manager: Any,
    ) -> None:
        """Initialize orchestrator.

        Args:
            workflow_engine: Workflow engine instance
            resource_manager: Resource manager instance
        """
        self._workflow_engine = workflow_engine
        self._resource_manager = resource_manager
        self._active_contexts: dict[str, OrchestrationContext] = {}
        self._task_queue: asyncio.Queue = asyncio.Queue()
        self._running = False

        logger.info("Orchestrator initialized")

    async def orchestrate(
        self,
        workflow_id: str,
        inputs: dict[str, Any],
        strategy: OrchestrationStrategy = OrchestrationStrategy.ADAPTIVE,
    ) -> dict[str, Any]:
        """Orchestrate workflow execution.

        Args:
            workflow_id: Workflow ID
            inputs: Input data
            strategy: Orchestration strategy

        Returns:
            Execution results
        """
        context = OrchestrationContext(
            workflow_id=workflow_id,
            inputs=inputs,
            strategy=strategy,
        )

        self._active_contexts[workflow_id] = context

        try:
            workflow = await self._workflow_engine.get_workflow(workflow_id)
            execution_order = await self._plan_execution(workflow, strategy)

            results = await self._execute_workflow(workflow, execution_order, context)

            context.end_time = datetime.now()
            context.outputs = results

            return {
                "success": True,
                "outputs": results,
                "execution_time": (context.end_time - context.start_time).total_seconds(),
                "tasks_completed": len(context.completed_tasks),
                "tasks_failed": len(context.failed_tasks),
            }
        except Exception as e:
            logger.error(f"Orchestration failed for {workflow_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "outputs": {},
            }
        finally:
            self._active_contexts.pop(workflow_id, None)

    async def _plan_execution(
        self,
        workflow: Any,
        strategy: OrchestrationStrategy,
    ) -> list[list[str]]:
        """Plan execution order based on workflow DAG and strategy.

        Args:
            workflow: Workflow definition
            strategy: Orchestration strategy

        Returns:
            List of execution batches (parallelizable tasks in each batch)
        """
        if strategy == OrchestrationStrategy.SEQUENTIAL:
            return [[task] for task in workflow.tasks]

        if strategy == OrchestrationStrategy.PARALLEL:
            return [workflow.tasks]

        return await self._compute_execution_levels(workflow)

    async def _compute_execution_levels(
        self,
        workflow: Any,
    ) -> list[list[str]]:
        """Compute execution levels for DAG-based execution.

        Tasks at the same level can be executed in parallel.
        """
        levels = []
        remaining_tasks = set(workflow.tasks)
        completed_tasks = set()

        while remaining_tasks:
            ready_tasks = [
                task
                for task in remaining_tasks
                if all(dep in completed_tasks for dep in workflow.get_dependencies(task))
            ]

            if not ready_tasks:
                raise ValueError("Circular dependency detected in workflow")

            levels.append(ready_tasks)
            completed_tasks.update(ready_tasks)
            remaining_tasks -= set(ready_tasks)

        return levels

    async def _execute_workflow(
        self,
        workflow: Any,
        execution_order: list[list[str]],
        context: OrchestrationContext,
    ) -> dict[str, Any]:
        """Execute workflow according to planned order.

        Args:
            workflow: Workflow definition
            execution_order: Planned execution batches
            context: Execution context

        Returns:
            Execution results
        """
        results = {}

        for batch in execution_order:
            batch_results = await asyncio.gather(
                *[self._execute_task(workflow, task_id, context) for task_id in batch],
                return_exceptions=True,
            )

            for task_id, result in zip(batch, batch_results, strict=False):
                if isinstance(result, Exception):
                    context.failed_tasks.append(task_id)
                    logger.error(f"Task {task_id} failed: {result}")
                else:
                    context.completed_tasks.append(task_id)
                    results[task_id] = result

        return results

    async def _execute_task(
        self,
        workflow: Any,
        task_id: str,
        context: OrchestrationContext,
    ) -> Any:
        """Execute a single task.

        Args:
            workflow: Workflow definition
            task_id: Task ID
            context: Execution context

        Returns:
            Task result
        """
        task = workflow.get_task(task_id)
        agent_id = await self._resource_manager.allocate_agent(task)
        context.active_agents.add(agent_id)

        try:
            result = await self._workflow_engine.execute_task(
                task_id=task_id,
                agent_id=agent_id,
                inputs=context.inputs,
            )

            return result
        finally:
            await self._resource_manager.release_agent(agent_id)
            context.active_agents.discard(agent_id)

    async def start_continuous_orchestration(self) -> None:
        """Start continuous orchestration loop for queued workflows."""
        self._running = True

        while self._running:
            try:
                workflow_id, inputs = await asyncio.wait_for(
                    self._task_queue.get(),
                    timeout=1.0,
                )

                await self.orchestrate(workflow_id, inputs)
            except TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Continuous orchestration error: {e}")

    async def stop_continuous_orchestration(self) -> None:
        """Stop continuous orchestration loop."""
        self._running = False

    async def queue_workflow(
        self,
        workflow_id: str,
        inputs: dict[str, Any],
    ) -> None:
        """Queue a workflow for execution.

        Args:
            workflow_id: Workflow ID
            inputs: Input data
        """
        await self._task_queue.put((workflow_id, inputs))
