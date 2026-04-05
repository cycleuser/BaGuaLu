"""Executor Agent - Task execution specialist."""

from __future__ import annotations

import json
from typing import Any

from bagualu.agents.base import AgentContext, AgentRole, AgentStatus, BaseAgent
from bagualu.utils.logging import Logger

logger = Logger.get_logger(__name__)


class ExecutorAgent(BaseAgent):
    """Executor agent specialized in task execution.

    Responsibilities:
    - Execute assigned tasks with skills
    - Report execution progress and results
    - Handle errors and recoveries
    - Optimize execution based on experience
    """

    def __init__(
        self,
        name: str,
        provider: str | None = None,
        model: str | None = None,
        skills: list[str] | None = None,
        max_retries: int = 3,
    ) -> None:
        """Initialize executor agent.

        Args:
            name: Agent name
            provider: LLM provider
            model: Model identifier
            skills: List of skills to load
            max_retries: Maximum retry attempts for failed tasks
        """
        super().__init__(
            name=name,
            role=AgentRole.EXECUTOR,
            provider=provider,
            model=model,
            skills=skills,
        )

        self._max_retries = max_retries
        self._execution_history: list[dict[str, Any]] = []
        self._success_rate = 0.0

        logger.info(f"Executor agent {name} initialized")

    async def process(
        self,
        instruction: str,
        inputs: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute a task.

        Args:
            instruction: Task instruction
            inputs: Input data

        Returns:
            Execution result
        """
        inputs = inputs or {}
        context = AgentContext(
            task_id=f"task-{self._step}",
            instruction=instruction,
            inputs=inputs,
        )

        self._context = context
        await self.update_status(AgentStatus.RUNNING)

        try:
            result = await self._execute_with_skills(instruction, inputs)

            context.outputs = result
            self._execution_history.append(
                {
                    "task_id": context.task_id,
                    "instruction": instruction,
                    "inputs": inputs,
                    "outputs": result,
                    "success": True,
                }
            )

            self._update_success_rate(True)

            await self.update_status(AgentStatus.READY)
            self.increment_step()

            return result
        except Exception as e:
            logger.error(f"Executor {self._name} failed: {e}")

            self._execution_history.append(
                {
                    "task_id": context.task_id,
                    "instruction": instruction,
                    "inputs": inputs,
                    "error": str(e),
                    "success": False,
                }
            )

            self._update_success_rate(False)

            await self.update_status(AgentStatus.ERROR)

            return {
                "success": False,
                "error": str(e),
                "agent": self._name,
            }

    async def _execute_with_skills(
        self,
        instruction: str,
        inputs: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute task using loaded skills.

        Args:
            instruction: Task instruction
            inputs: Input data

        Returns:
            Execution result
        """
        relevant_skills = await self._find_relevant_skills(instruction)

        if not relevant_skills:
            return await self._execute_without_skills(instruction, inputs)

        skill_results = []
        for skill_name in relevant_skills[:3]:
            try:
                result = await self.execute_skill(skill_name, inputs)
                skill_results.append(result)
            except Exception as e:
                logger.warning(f"Skill {skill_name} failed: {e}")

        if skill_results:
            best_result = skill_results[0]
            return {
                "success": True,
                "outputs": best_result.get("response", {}),
                "skills_used": relevant_skills[:3],
                "agent": self._name,
            }

        return await self._execute_without_skills(instruction, inputs)

    async def _execute_without_skills(
        self,
        instruction: str,
        inputs: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute task without skills (direct LLM call).

        Args:
            instruction: Task instruction
            inputs: Input data

        Returns:
            Execution result
        """
        messages = [
            {
                "role": "system",
                "content": "You are an executor agent. Execute the given task efficiently and accurately.",
            },
            {
                "role": "user",
                "content": f"Instruction: {instruction}\n\nInputs: {json.dumps(inputs)}",
            },
        ]

        response = await self.call_llm(messages)

        return {
            "success": True,
            "outputs": response,
            "skills_used": [],
            "agent": self._name,
        }

    async def _find_relevant_skills(
        self,
        instruction: str,
    ) -> list[str]:
        """Find skills relevant to the instruction.

        Args:
            instruction: Task instruction

        Returns:
            List of relevant skill names
        """
        relevant = []
        instruction_lower = instruction.lower()

        for skill_name, skill_def in self._skills.items():
            for trigger in skill_def.triggers:
                if trigger.lower() in instruction_lower:
                    relevant.append(skill_name)
                    break

        return relevant

    async def evolve(self) -> bool:
        """Evolve executor agent based on execution history.

        Returns:
            True if evolution succeeded
        """
        if self._success_rate > 0.8:
            logger.info(f"Executor {self._name} has high success rate, no evolution needed")
            return False

        recent_failures = [
            entry for entry in self._execution_history[-10:] if not entry.get("success", False)
        ]

        if len(recent_failures) < 3:
            return False

        evolution_suggestion = await self._analyze_failures(recent_failures)

        if evolution_suggestion:
            logger.info(f"Executor {self._name} evolution suggestion: {evolution_suggestion}")
            self._evolution_history.append(
                {
                    "timestamp": self._step,
                    "suggestion": evolution_suggestion,
                    "failures_analyzed": len(recent_failures),
                }
            )
            return True

        return False

    async def _analyze_failures(
        self,
        failures: list[dict[str, Any]],
    ) -> str | None:
        """Analyze failure patterns to generate evolution suggestions.

        Args:
            failures: List of failed executions

        Returns:
            Evolution suggestion or None
        """
        if not failures:
            return None

        failure_patterns: dict[str, int] = {}
        for failure in failures:
            error = failure.get("error", "unknown")
            failure_patterns[error] = failure_patterns.get(error, 0) + 1

        most_common_error = max(failure_patterns.items(), key=lambda x: x[1])

        return f"Consider adding skill for handling '{most_common_error[0]}' errors"

    def _update_success_rate(
        self,
        success: bool,
    ) -> None:
        """Update success rate based on execution result.

        Args:
            success: Whether execution succeeded
        """
        total_executions = len(self._execution_history)
        successful_executions = sum(
            1 for entry in self._execution_history if entry.get("success", False)
        )

        self._success_rate = (
            successful_executions / total_executions if total_executions > 0 else 0.0
        )

    async def get_performance_metrics(self) -> dict[str, Any]:
        """Get performance metrics for this executor.

        Returns:
            Performance metrics dictionary
        """
        return {
            "name": self._name,
            "role": self._role.value,
            "total_executions": len(self._execution_history),
            "success_rate": self._success_rate,
            "skills_loaded": list(self._skills.keys()),
            "evolution_count": len(self._evolution_history),
            "recent_failures": len(
                [
                    entry
                    for entry in self._execution_history[-10:]
                    if not entry.get("success", False)
                ]
            ),
        }
