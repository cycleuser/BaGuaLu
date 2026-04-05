"""Skill Evolver - Self-evolution system for skills."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any

from bagualu.utils.logging import Logger

logger = Logger.get_logger(__name__)


class EvolutionTrigger(StrEnum):
    """Evolution trigger sources."""

    MANUAL = "manual"
    POST_EXECUTION = "post_execution"
    TOOL_DEGRADATION = "tool_degradation"
    METRIC_MONITOR = "metric_monitor"
    ANALYSIS = "analysis"


class EvolutionType(StrEnum):
    """Evolution types."""

    FIX = "fix"
    DERIVED = "derived"
    CAPTURED = "captured"
    AUTO = "auto"


@dataclass
class EvolutionContext:
    """Evolution context information."""

    skill_name: str
    skill_def: dict[str, Any]
    trigger: EvolutionTrigger
    evolution_type: EvolutionType
    execution_history: list[dict[str, Any]] = field(default_factory=list)
    failure_patterns: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)


@dataclass
class EvolutionResult:
    """Evolution result."""

    success: bool
    skill_name: str
    evolution_type: EvolutionType
    new_version: str
    changes: dict[str, Any]
    lineage: dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)


class SkillEvolver:
    """Skill self-evolution system (inspired by OpenSpace).

    Evolution Types:
    - FIX: Repair broken/outdated instructions (in-place, same name)
    - DERIVED: Create enhanced version from existing skill (new directory)
    - CAPTURED: Capture novel reusable pattern from execution (brand new skill)

    Evolution Triggers:
    - Post-execution analysis
    - Tool degradation detection
    - Metric monitoring
    - Manual request
    """

    def __init__(
        self,
        registry: Any,
        max_iterations: int = 3,
        quality_threshold: float = 0.8,
    ) -> None:
        """Initialize skill evolver.

        Args:
            registry: Skill registry
            max_iterations: Maximum evolution iterations
            quality_threshold: Quality threshold for auto-evolution
        """
        self._registry = registry
        self._max_iterations = max_iterations
        self._quality_threshold = quality_threshold
        self._evolution_history: dict[str, list[EvolutionResult]] = {}

        logger.info("Skill evolver initialized")

    async def evolve(
        self,
        context: EvolutionContext,
        evolution_type: EvolutionType,
    ) -> dict[str, Any] | None:
        """Execute skill evolution.

        Args:
            context: Evolution context
            evolution_type: Evolution type

        Returns:
            Evolved skill definition or None
        """
        try:
            if evolution_type == EvolutionType.FIX:
                return await self._fix_skill(context)

            if evolution_type == EvolutionType.DERIVED:
                return await self._derive_skill(context)

            if evolution_type == EvolutionType.CAPTURED:
                return await self._capture_skill(context)

            return None
        except Exception as e:
            logger.error(f"Evolution failed for {context.skill_name}: {e}")
            return None

    async def _fix_skill(
        self,
        context: EvolutionContext,
    ) -> dict[str, Any] | None:
        """Fix broken or outdated skill instructions.

        Args:
            context: Evolution context

        Returns:
            Fixed skill definition
        """
        skill_def = context.skill_def
        instructions = skill_def.get("instructions", "")

        failure_patterns = await self._analyze_failures(context.execution_history)

        if not failure_patterns:
            logger.info(f"No failures to fix for {context.skill_name}")
            return None

        fix_suggestions = await self._generate_fix_suggestions(
            instructions,
            failure_patterns,
        )

        fixed_instructions = await self._apply_fixes(
            instructions,
            fix_suggestions,
        )

        if fixed_instructions == instructions:
            logger.info(f"No fixes applied for {context.skill_name}")
            return None

        new_version = self._compute_version(skill_def.get("version", "1.0.0"))

        evolved_skill = {
            "name": skill_def.get("name"),
            "description": skill_def.get("description", ""),
            "instructions": fixed_instructions,
            "version": new_version,
            "evolution_type": "fix",
            "parent_version": skill_def.get("version", "1.0.0"),
            "evolved_at": datetime.now().isoformat(),
            "fixes": fix_suggestions,
        }

        result = EvolutionResult(
            success=True,
            skill_name=context.skill_name,
            evolution_type=EvolutionType.FIX,
            new_version=new_version,
            changes={"instructions": {"old": instructions, "new": fixed_instructions}},
            lineage={
                "parent": skill_def.get("version", "1.0.0"),
                "type": "fix",
            },
        )

        self._record_evolution(context.skill_name, result)

        logger.info(f"Skill {context.skill_name} fixed (version: {new_version})")

        return evolved_skill

    async def _derive_skill(
        self,
        context: EvolutionContext,
    ) -> dict[str, Any] | None:
        """Derive enhanced skill from parent.

        Args:
            context: Evolution context

        Returns:
            Derived skill definition
        """
        skill_def = context.skill_def

        enhancements = await self._identify_enhancements(context)

        if not enhancements:
            return None

        derived_name = f"{skill_def.get('name')}-enhanced"

        enhanced_instructions = await self._generate_derived_instructions(
            skill_def.get("instructions", ""),
            enhancements,
        )

        derived_skill = {
            "name": derived_name,
            "description": f"Enhanced version of {skill_def.get('name')}",
            "instructions": enhanced_instructions,
            "version": "1.0.0",
            "evolution_type": "derived",
            "parent_skill": skill_def.get("name"),
            "parent_version": skill_def.get("version", "1.0.0"),
            "enhancements": enhancements,
            "evolved_at": datetime.now().isoformat(),
        }

        result = EvolutionResult(
            success=True,
            skill_name=derived_name,
            evolution_type=EvolutionType.DERIVED,
            new_version="1.0.0",
            changes={"enhancements": enhancements},
            lineage={
                "parent": skill_def.get("name"),
                "parent_version": skill_def.get("version", "1.0.0"),
                "type": "derived",
            },
        )

        self._record_evolution(derived_name, result)

        logger.info(f"Derived skill: {derived_name} from {context.skill_name}")

        return derived_skill

    async def _capture_skill(
        self,
        context: EvolutionContext,
    ) -> dict[str, Any] | None:
        """Capture novel pattern from successful executions.

        Args:
            context: Evolution context

        Returns:
            Captured skill definition
        """
        successful_executions = [
            entry for entry in context.execution_history if entry.get("success", False)
        ]

        if len(successful_executions) < 3:
            logger.info("Insufficient successful executions for capture")
            return None

        pattern = await self._extract_pattern(successful_executions)

        if not pattern:
            return None

        captured_name = await self._generate_skill_name(pattern)

        captured_skill = {
            "name": captured_name,
            "description": f"Captured pattern from {len(successful_executions)} successful executions",
            "instructions": pattern,
            "version": "1.0.0",
            "evolution_type": "captured",
            "source_executions": [entry.get("id") for entry in successful_executions],
            "evolved_at": datetime.now().isoformat(),
        }

        result = EvolutionResult(
            success=True,
            skill_name=captured_name,
            evolution_type=EvolutionType.CAPTURED,
            new_version="1.0.0",
            changes={"pattern": pattern},
            lineage={
                "source": "execution_capture",
                "executions": len(successful_executions),
                "type": "captured",
            },
        )

        self._record_evolution(captured_name, result)

        logger.info(f"Captured new skill: {captured_name}")

        return captured_skill

    async def _analyze_failures(
        self,
        execution_history: list[dict[str, Any]],
    ) -> list[str]:
        """Analyze execution failures to identify patterns.

        Args:
            execution_history: List of execution records

        Returns:
            List of failure patterns
        """
        failures = [entry for entry in execution_history if not entry.get("success", False)]

        if not failures:
            return []

        patterns = []

        for failure in failures:
            error = failure.get("error", "unknown")
            patterns.append(error)

        return patterns

    async def _generate_fix_suggestions(
        self,
        instructions: str,
        failure_patterns: list[str],
    ) -> list[str]:
        """Generate fix suggestions based on failure patterns.

        Args:
            instructions: Current instructions
            failure_patterns: Failure patterns

        Returns:
            List of fix suggestions
        """
        suggestions = []

        for pattern in failure_patterns[:5]:
            if "timeout" in pattern.lower():
                suggestions.append("Add timeout handling and retry logic")

            if "error" in pattern.lower() or "failed" in pattern.lower():
                suggestions.append("Add error handling and recovery steps")

            if "invalid" in pattern.lower():
                suggestions.append("Add input validation and sanitization")

        return suggestions[:5]

    async def _apply_fixes(
        self,
        instructions: str,
        fix_suggestions: list[str],
    ) -> str:
        """Apply fix suggestions to instructions.

        Args:
            instructions: Current instructions
            fix_suggestions: Fix suggestions

        Returns:
            Fixed instructions
        """
        if not fix_suggestions:
            return instructions

        fix_section = "\n\n## Error Handling\n\n"

        for suggestion in fix_suggestions:
            fix_section += f"- {suggestion}\n"

        fixed_instructions = instructions + fix_section

        return fixed_instructions

    async def _identify_enhancements(
        self,
        context: EvolutionContext,
    ) -> list[str]:
        """Identify potential enhancements for derivation.

        Args:
            context: Evolution context

        Returns:
            List of enhancement suggestions
        """
        enhancements = []

        successful_count = sum(
            1 for entry in context.execution_history if entry.get("success", False)
        )

        if successful_count > 5:
            enhancements.append("Optimize for repeated successful patterns")

        enhancements.append("Add comprehensive error handling")
        enhancements.append("Include performance optimization tips")

        return enhancements[:5]

    async def _generate_derived_instructions(
        self,
        base_instructions: str,
        enhancements: list[str],
    ) -> str:
        """Generate derived instructions with enhancements.

        Args:
            base_instructions: Base instructions
            enhancements: Enhancements to apply

        Returns:
            Enhanced instructions
        """
        enhanced = base_instructions

        enhanced += "\n\n## Enhancements\n\n"

        for enhancement in enhancements:
            enhanced += f"### {enhancement}\n\n"
            enhanced += f"Apply {enhancement.lower()} for improved performance.\n\n"

        return enhanced

    async def _extract_pattern(
        self,
        executions: list[dict[str, Any]],
    ) -> str | None:
        """Extract reusable pattern from successful executions.

        Args:
            executions: Successful execution records

        Returns:
            Extracted pattern or None
        """
        if not executions:
            return None

        common_inputs = []

        for execution in executions:
            inputs = execution.get("inputs", {})

            for key in inputs:
                if key not in common_inputs:
                    common_inputs.append(key)

        pattern = "## Pattern\n\n"
        pattern += f"Successfully executed {len(executions)} times.\n\n"
        pattern += f"Common inputs: {', '.join(common_inputs)}\n\n"
        pattern += "## Instructions\n\n"
        pattern += "Follow the successful execution pattern.\n\n"

        return pattern

    async def _generate_skill_name(
        self,
        pattern: str,
    ) -> str:
        """Generate skill name from pattern.

        Args:
            pattern: Extracted pattern

        Returns:
            Generated skill name
        """
        hash_value = hashlib.md5(pattern.encode()).hexdigest()[:8]

        return f"captured-skill-{hash_value}"

    def _compute_version(
        self,
        current_version: str,
    ) -> str:
        """Compute new version number.

        Args:
            current_version: Current version

        Returns:
            New version
        """
        try:
            parts = current_version.split(".")

            if len(parts) >= 2:
                minor = int(parts[1]) + 1
                return f"{parts[0]}.{minor}"

            return "1.1"
        except Exception:
            return "1.1"

    def _record_evolution(
        self,
        skill_name: str,
        result: EvolutionResult,
    ) -> None:
        """Record evolution result.

        Args:
            skill_name: Skill name
            result: Evolution result
        """
        if skill_name not in self._evolution_history:
            self._evolution_history[skill_name] = []

        self._evolution_history[skill_name].append(result)

    async def get_evolution_history(
        self,
        skill_name: str,
    ) -> list[EvolutionResult]:
        """Get evolution history for a skill.

        Args:
            skill_name: Skill name

        Returns:
            List of evolution results
        """
        return self._evolution_history.get(skill_name, [])

    async def get_all_evolution_statistics(self) -> dict[str, Any]:
        """Get overall evolution statistics.

        Returns:
            Statistics dictionary
        """
        total_evolutions = sum(len(history) for history in self._evolution_history.values())

        fix_count = sum(
            1
            for history in self._evolution_history.values()
            for result in history
            if result.evolution_type == EvolutionType.FIX
        )

        derived_count = sum(
            1
            for history in self._evolution_history.values()
            for result in history
            if result.evolution_type == EvolutionType.DERIVED
        )

        captured_count = sum(
            1
            for history in self._evolution_history.values()
            for result in history
            if result.evolution_type == EvolutionType.CAPTURED
        )

        return {
            "total_evolutions": total_evolutions,
            "fix_evolutions": fix_count,
            "derived_evolutions": derived_count,
            "captured_evolutions": captured_count,
            "skills_evolved": len(self._evolution_history),
        }
