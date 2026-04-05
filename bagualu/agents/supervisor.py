"""Supervisor Agent - Task supervision and quality control."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from bagualu.agents.base import AgentRole, BaseAgent
from bagualu.utils.logging import Logger

logger = Logger.get_logger(__name__)


class SupervisorAgent(BaseAgent):
    """Supervisor agent for task oversight and quality control.

    Responsibilities:
    - Monitor executor agent performance
    - Validate task outputs
    - Handle escalations and exceptions
    - Optimize workflow execution
    - Coordinate multiple executors
    """

    def __init__(
        self,
        name: str,
        provider: str | None = None,
        model: str | None = None,
        supervised_agents: list[str] | None = None,
        quality_threshold: float = 0.85,
    ) -> None:
        """Initialize supervisor agent.

        Args:
            name: Agent name
            provider: LLM provider
            model: Model identifier
            supervised_agents: List of agent IDs to supervise
            quality_threshold: Minimum quality threshold for outputs
        """
        super().__init__(
            name=name,
            role=AgentRole.SUPERVISOR,
            provider=provider,
            model=model,
        )

        self._supervised_agents: set[str] = set(supervised_agents or [])
        self._quality_threshold = quality_threshold
        self._quality_metrics: dict[str, dict[str, Any]] = {}
        self._escalations: list[dict[str, Any]] = []
        self._optimization_history: list[dict[str, Any]] = []

        logger.info(f"Supervisor agent {name} initialized")

    async def process(
        self,
        instruction: str,
        inputs: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Supervise task execution.

        Args:
            instruction: Supervision instruction
            inputs: Input data

        Returns:
            Supervision result
        """
        inputs = inputs or {}

        try:
            result = await self._supervise(instruction, inputs)

            return {
                "success": True,
                "supervision_result": result,
                "agent": self._name,
            }
        except Exception as e:
            logger.error(f"Supervisor {self._name} failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent": self._name,
            }

    async def _supervise(
        self,
        instruction: str,
        inputs: dict[str, Any],
    ) -> dict[str, Any]:
        """Perform supervision.

        Args:
            instruction: Supervision instruction
            inputs: Input data

        Returns:
            Supervision details
        """
        if "validate" in instruction.lower():
            return await self._validate_outputs(inputs)

        if "monitor" in instruction.lower():
            return await self._monitor_agents(inputs)

        if "optimize" in instruction.lower():
            return await self._optimize_workflow(inputs)

        return await self._general_supervision(instruction, inputs)

    async def _validate_outputs(
        self,
        inputs: dict[str, Any],
    ) -> dict[str, Any]:
        """Validate task outputs against quality threshold.

        Args:
            inputs: Output data to validate

        Returns:
            Validation result
        """
        outputs = inputs.get("outputs", {})
        quality_score = await self._assess_quality(outputs)

        validation_result = {
            "quality_score": quality_score,
            "threshold": self._quality_threshold,
            "passed": quality_score >= self._quality_threshold,
            "feedback": [],
        }

        if quality_score < self._quality_threshold:
            validation_result["feedback"] = await self._generate_quality_feedback(outputs)

            self._escalations.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "agent": inputs.get("agent", "unknown"),
                    "quality_score": quality_score,
                    "feedback": validation_result["feedback"],
                }
            )

        return validation_result

    async def _assess_quality(
        self,
        outputs: dict[str, Any],
    ) -> float:
        """Assess quality of outputs.

        Args:
            outputs: Output data

        Returns:
            Quality score (0.0 to 1.0)
        """
        if not outputs:
            return 0.0

        messages = [
            {
                "role": "system",
                "content": "Assess the quality of the given output on a scale of 0 to 1. Consider completeness, accuracy, and usefulness.",
            },
            {
                "role": "user",
                "content": f"Output: {outputs}",
            },
        ]

        try:
            response = await self.call_llm(messages)
            score_text = response.get("content", "0.5")

            import re

            match = re.search(r"(\d+\.?\d*)", score_text)
            if match:
                score = float(match.group(1))
                return min(max(score, 0.0), 1.0)

            return 0.5
        except Exception as e:
            logger.error(f"Quality assessment failed: {e}")
            return 0.5

    async def _generate_quality_feedback(
        self,
        outputs: dict[str, Any],
    ) -> list[str]:
        """Generate feedback for improving output quality.

        Args:
            outputs: Output data

        Returns:
            List of feedback suggestions
        """
        messages = [
            {
                "role": "system",
                "content": "Generate specific feedback to improve the quality of this output.",
            },
            {
                "role": "user",
                "content": f"Output: {outputs}",
            },
        ]

        try:
            response = await self.call_llm(messages)
            feedback_text = response.get("content", "")

            feedback_lines = [line.strip() for line in feedback_text.split("\n") if line.strip()]

            return feedback_lines[:5]
        except Exception as e:
            logger.error(f"Feedback generation failed: {e}")
            return ["Output quality below threshold"]

    async def _monitor_agents(
        self,
        inputs: dict[str, Any],
    ) -> dict[str, Any]:
        """Monitor supervised agents.

        Args:
            inputs: Monitoring inputs

        Returns:
            Monitoring results
        """
        monitoring_result: dict[str, Any] = {
            "agents_monitored": len(self._supervised_agents),
            "agent_statuses": {},
            "alerts": [],
        }

        for agent_id in self._supervised_agents:
            metrics = self._quality_metrics.get(agent_id, {})

            if metrics.get("success_rate", 1.0) < 0.7:
                monitoring_result["alerts"].append(
                    {
                        "agent": agent_id,
                        "issue": "Low success rate",
                        "value": metrics.get("success_rate", 0.0),
                    }
                )

            if metrics.get("error_count", 0) > 5:
                monitoring_result["alerts"].append(
                    {
                        "agent": agent_id,
                        "issue": "High error count",
                        "value": metrics.get("error_count", 0),
                    }
                )

            monitoring_result["agent_statuses"][agent_id] = metrics

        return monitoring_result

    async def _optimize_workflow(
        self,
        inputs: dict[str, Any],
    ) -> dict[str, Any]:
        """Optimize workflow execution based on historical data.

        Args:
            inputs: Workflow data

        Returns:
            Optimization suggestions
        """
        optimization: dict[str, Any] = {
            "suggestions": [],
            "estimated_improvement": 0.0,
        }

        for agent_id in self._supervised_agents:
            metrics = self._quality_metrics.get(agent_id, {})

            if metrics.get("success_rate", 1.0) < 0.8:
                optimization["suggestions"].append(
                    {
                        "agent": agent_id,
                        "suggestion": "Consider skill evolution",
                        "current_rate": metrics.get("success_rate", 0.0),
                    }
                )

        if optimization["suggestions"]:
            optimization["estimated_improvement"] = 0.15

        self._optimization_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "suggestions": optimization["suggestions"],
            }
        )

        return optimization

    async def _general_supervision(
        self,
        instruction: str,
        inputs: dict[str, Any],
    ) -> dict[str, Any]:
        """Perform general supervision.

        Args:
            instruction: Instruction
            inputs: Inputs

        Returns:
            Supervision result
        """
        messages = [
            {
                "role": "system",
                "content": "You are a supervisor agent. Provide oversight and coordination.",
            },
            {
                "role": "user",
                "content": f"Instruction: {instruction}\n\nInputs: {inputs}",
            },
        ]

        response = await self.call_llm(messages)

        return {
            "guidance": response,
        }

    async def evolve(self) -> bool:
        """Evolve supervisor agent.

        Returns:
            True if evolution succeeded
        """
        if len(self._escalations) < 3:
            return False

        logger.info(f"Supervisor {self._name} analyzing escalation patterns")

        return True

    def add_supervised_agent(
        self,
        agent_id: str,
    ) -> None:
        """Add an agent to supervision.

        Args:
            agent_id: Agent ID
        """
        self._supervised_agents.add(agent_id)
        self._quality_metrics[agent_id] = {
            "success_rate": 1.0,
            "error_count": 0,
            "quality_scores": [],
        }
        logger.info(f"Supervisor {self._name} now supervising agent {agent_id}")

    def remove_supervised_agent(
        self,
        agent_id: str,
    ) -> None:
        """Remove an agent from supervision.

        Args:
            agent_id: Agent ID
        """
        self._supervised_agents.discard(agent_id)
        self._quality_metrics.pop(agent_id, None)
        logger.info(f"Supervisor {self._name} stopped supervising agent {agent_id}")

    async def update_agent_metrics(
        self,
        agent_id: str,
        metrics: dict[str, Any],
    ) -> None:
        """Update metrics for a supervised agent.

        Args:
            agent_id: Agent ID
            metrics: Performance metrics
        """
        if agent_id not in self._supervised_agents:
            return

        self._quality_metrics[agent_id].update(metrics)

    async def get_supervision_report(self) -> dict[str, Any]:
        """Get comprehensive supervision report.

        Returns:
            Supervision report
        """
        return {
            "supervisor": self._name,
            "agents_supervised": list(self._supervised_agents),
            "escalation_count": len(self._escalations),
            "optimization_count": len(self._optimization_history),
            "quality_threshold": self._quality_threshold,
            "recent_escalations": self._escalations[-5:],
            "agent_metrics": self._quality_metrics,
        }
