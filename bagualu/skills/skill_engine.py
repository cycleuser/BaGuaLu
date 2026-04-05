"""Skill Engine - Skill loading, execution, and evolution system."""

from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any

from bagualu.skills.evolver import (
    EvolutionContext,
    EvolutionTrigger,
    EvolutionType,
    SkillEvolver,
)
from bagualu.skills.registry import SkillRegistry
from bagualu.skills.store import SkillStore
from bagualu.utils.logging import Logger

logger = Logger.get_logger(__name__)


class SkillEngine:
    """Skill engine for loading, executing, and evolving skills.

    Features (Inspired by OpenSpace):
    - Load skills from OpenCode/Claude Code SKILL.md files
    - Auto-discovery and registration
    - Self-evolution (FIX, DERIVED, CAPTURED)
    - Quality monitoring
    - Skill versioning and lineage tracking
    """

    def __init__(
        self,
        skill_dirs: list[Path],
        config_manager: Any,
    ) -> None:
        """Initialize skill engine.

        Args:
            skill_dirs: List of directories containing skills
            config_manager: Configuration manager
        """
        self._skill_dirs = skill_dirs
        self._config_manager = config_manager
        self._registry = SkillRegistry(skill_dirs)
        self._evolver = SkillEvolver(self._registry)
        self._store = SkillStore()
        self._initialized = False
        self._skill_cache: dict[str, Any] = {}
        self._execution_history: list[dict[str, Any]] = []

        logger.info(f"Skill engine initialized with {len(skill_dirs)} skill directories")

    async def initialize(self) -> None:
        """Initialize skill engine asynchronously."""
        if self._initialized:
            return

        await self._registry.discover_skills()
        await self._store.initialize()

        self._initialized = True
        logger.info("Skill engine fully initialized")

    async def load_skill(
        self,
        skill_path: Path,
    ) -> dict[str, Any] | None:
        """Load a skill from SKILL.md file.

        Args:
            skill_path: Path to SKILL.md file

        Returns:
            Skill definition or None
        """
        skill_def = await self._registry.load_skill(skill_path)

        if skill_def:
            self._skill_cache[skill_def["name"]] = skill_def
            await self._store.register_skill(skill_def)
            logger.info(f"Loaded skill: {skill_def['name']}")

        return skill_def

    async def get_skill(
        self,
        skill_name: str,
    ) -> dict[str, Any] | None:
        """Get skill by name.

        Args:
            skill_name: Skill name

        Returns:
            Skill definition or None
        """
        if skill_name in self._skill_cache:
            cached: dict[str, Any] = self._skill_cache[skill_name]
            return cached

        skill_def = await self._registry.get_skill(skill_name)

        if skill_def:
            self._skill_cache[skill_name] = skill_def

        return skill_def if skill_def else None

    async def find_relevant_skills(
        self,
        query: str,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """Find skills relevant to a query.

        Args:
            query: Query string
            limit: Maximum number of skills to return

        Returns:
            List of relevant skill definitions
        """
        skills = await self._registry.search_skills(query)

        return skills[:limit]

    async def execute_skill(
        self,
        skill_name: str,
        inputs: dict[str, Any],
        agent: Any | None = None,
    ) -> dict[str, Any]:
        """Execute a skill.

        Args:
            skill_name: Skill name
            inputs: Input data
            agent: Agent to execute with

        Returns:
            Execution result
        """
        skill_def = await self.get_skill(skill_name)

        if not skill_def:
            return {
                "success": False,
                "error": f"Skill not found: {skill_name}",
            }

        execution_id = f"exec-{datetime.now().timestamp()}"

        execution_record: dict[str, Any] = {
            "id": execution_id,
            "skill": skill_name,
            "inputs": inputs,
            "start_time": datetime.now().isoformat(),
        }

        try:
            result = await self._execute_skill_internal(skill_def, inputs, agent)

            execution_record["success"] = True
            execution_record["result"] = result
            execution_record["end_time"] = datetime.now().isoformat()

            self._execution_history.append(execution_record)

            await self._trigger_post_execution_analysis(execution_record)

            return result
        except Exception as e:
            execution_record["success"] = False
            execution_record["error"] = str(e)
            execution_record["end_time"] = datetime.now().isoformat()

            self._execution_history.append(execution_record)

            logger.error(f"Skill {skill_name} execution failed: {e}")

            return {
                "success": False,
                "error": str(e),
                "skill": skill_name,
            }

    async def _execute_skill_internal(
        self,
        skill_def: dict[str, Any],
        inputs: dict[str, Any],
        agent: Any | None,
    ) -> dict[str, Any]:
        """Internal skill execution.

        Args:
            skill_def: Skill definition
            inputs: Input data
            agent: Agent to execute with

        Returns:
            Execution result
        """
        instructions = skill_def.get("instructions", "")

        if agent:
            result = await agent.process(
                instruction=instructions,
                inputs=inputs,
            )
        else:
            result = {
                "instructions": instructions,
                "inputs": inputs,
                "note": "Skill instructions available for execution",
            }

        return {
            "success": True,
            "skill": skill_def.get("name"),
            "outputs": result,
        }

    async def evolve(
        self,
        skill_name: str,
        evolution_type: str = "auto",
        trigger: EvolutionTrigger = EvolutionTrigger.MANUAL,
    ) -> bool:
        """Trigger skill evolution.

        Args:
            skill_name: Skill name to evolve
            evolution_type: Evolution type (fix, derived, captured, auto)
            trigger: Evolution trigger

        Returns:
            True if evolution succeeded
        """
        skill_def = await self.get_skill(skill_name)

        if not skill_def:
            logger.warning(f"Skill {skill_name} not found for evolution")
            return False

        if evolution_type == "auto":
            evolution_type = await self._determine_evolution_type(skill_name)

        evo_type = EvolutionType(evolution_type.upper())

        evolution_context = EvolutionContext(
            skill_name=skill_name,
            skill_def=skill_def,
            trigger=trigger,
            evolution_type=evo_type,
            execution_history=self._execution_history[-10:],
        )

        evolved = await self._evolver.evolve(evolution_context, evo_type)

        if evolved:
            await self._store.update_skill_version(skill_name, evolved)
            self._skill_cache[skill_name] = evolved

            logger.info(f"Skill {skill_name} evolved successfully")

        return bool(evolved)

    async def _determine_evolution_type(
        self,
        skill_name: str,
    ) -> str:
        """Determine appropriate evolution type based on execution history.

        Args:
            skill_name: Skill name

        Returns:
            Evolution type string
        """
        skill_executions = [
            entry for entry in self._execution_history[-20:] if entry.get("skill") == skill_name
        ]

        if not skill_executions:
            return "fix"

        failed_executions = [entry for entry in skill_executions if not entry.get("success", False)]

        if len(failed_executions) >= len(skill_executions) * 0.3:
            return "fix"

        return "derived"

    async def _trigger_post_execution_analysis(
        self,
        execution_record: dict[str, Any],
    ) -> None:
        """Trigger post-execution analysis for potential evolution.

        Args:
            execution_record: Execution record
        """
        if not execution_record.get("success", False):
            await asyncio.sleep(0.1)

            skill_name = execution_record.get("skill")

            if skill_name:
                await self.evolve(
                    skill_name=skill_name,
                    evolution_type="auto",
                    trigger=EvolutionTrigger.POST_EXECUTION,
                )

    async def get_skill_lineage(
        self,
        skill_name: str,
    ) -> dict[str, Any]:
        """Get skill version lineage.

        Args:
            skill_name: Skill name

        Returns:
            Lineage information
        """
        lineage = await self._store.get_lineage(skill_name)

        return lineage

    async def get_all_skills(self) -> list[dict[str, Any]]:
        """Get all registered skills.

        Returns:
            List of all skill definitions
        """
        skills = await self._registry.get_all_skills()

        return skills

    async def import_skill_from_opencode(
        self,
        skill_dir: Path,
    ) -> dict[str, Any] | None:
        """Import skill from OpenCode/Claude Code skill directory.

        Args:
            skill_dir: Path to skill directory containing SKILL.md

        Returns:
            Imported skill definition
        """
        skill_md_path = skill_dir / "SKILL.md"

        if not skill_md_path.exists():
            logger.warning(f"No SKILL.md found in {skill_dir}")
            return None

        return await self.load_skill(skill_md_path)

    async def get_execution_statistics(
        self,
        skill_name: str | None = None,
    ) -> dict[str, Any]:
        """Get execution statistics.

        Args:
            skill_name: Optional skill name to filter

        Returns:
            Statistics dictionary
        """
        executions = self._execution_history

        if skill_name:
            executions = [entry for entry in executions if entry.get("skill") == skill_name]

        total = len(executions)
        successful = sum(1 for entry in executions if entry.get("success", False))

        return {
            "total_executions": total,
            "successful": successful,
            "failed": total - successful,
            "success_rate": successful / total if total > 0 else 0.0,
        }

    async def cleanup_old_versions(
        self,
        skill_name: str,
        keep_versions: int = 5,
    ) -> list[str]:
        """Clean up old skill versions.

        Args:
            skill_name: Skill name
            keep_versions: Number of versions to keep

        Returns:
            List of removed version IDs
        """
        removed = await self._store.cleanup_versions(skill_name, keep_versions)

        logger.info(f"Cleaned up {len(removed)} old versions for skill {skill_name}")

        return removed
