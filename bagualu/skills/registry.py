"""Skill Registry - Skill discovery and registration."""

from __future__ import annotations

import asyncio
import hashlib
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from bagualu.utils.logging import Logger

logger = Logger.get_logger(__name__)


class SkillRegistry:
    """Skill registry for discovery and registration.

    Features:
    - Auto-discovery from skill directories
    - Skill registration with metadata
    - Skill search (BM25 + embedding)
    - Skill validation
    """

    def __init__(
        self,
        skill_dirs: list[Path],
    ) -> None:
        """Initialize skill registry.

        Args:
            skill_dirs: List of skill directories
        """
        self._skill_dirs = skill_dirs
        self._skills: dict[str, dict[str, Any]] = {}
        self._skill_metadata: dict[str, dict[str, Any]] = {}
        self._skill_embeddings: dict[str, list[float]] = {}
        self._initialized = False

        logger.info(f"Skill registry initialized with {len(skill_dirs)} directories")

    async def discover_skills(self) -> list[str]:
        """Discover skills from configured directories.

        Returns:
            List of discovered skill names
        """
        discovered = []

        for skill_dir in self._skill_dirs:
            if not skill_dir.exists():
                continue

            skills_in_dir = await self._discover_in_directory(skill_dir)

            discovered.extend(skills_in_dir)

        logger.info(f"Discovered {len(discovered)} skills")

        self._initialized = True

        return discovered

    async def _discover_in_directory(
        self,
        directory: Path,
    ) -> list[str]:
        """Discover skills in a directory.

        Args:
            directory: Directory path

        Returns:
            List of skill names
        """
        skills = []

        skill_files = list(directory.rglob("SKILL.md"))

        for skill_file in skill_files:
            try:
                skill_def = await self._parse_skill_file(skill_file)

                if skill_def:
                    self._skills[skill_def["name"]] = skill_def
                    self._skill_metadata[skill_def["name"]] = {
                        "path": str(skill_file),
                        "discovered_at": datetime.now().isoformat(),
                        "source": "file",
                    }

                    skills.append(skill_def["name"])
            except Exception as e:
                logger.warning(f"Failed to parse {skill_file}: {e}")

        return skills

    async def _parse_skill_file(
        self,
        skill_file: Path,
    ) -> dict[str, Any] | None:
        """Parse SKILL.md file.

        Args:
            skill_file: Path to SKILL.md

        Returns:
            Skill definition dictionary
        """
        if not skill_file.exists():
            return None

        content = await asyncio.to_thread(skill_file.read_text)

        lines = content.strip().split("\n")

        if not lines:
            return None

        name = lines[0].replace("#", "").strip()

        if not name:
            name = skill_file.parent.name

        description = ""
        instructions = ""
        triggers = []
        parameters = {}
        examples = []

        current_section = "description"

        for line in lines[1:]:
            if line.startswith("## Triggers") or line.startswith("##触发"):
                current_section = "triggers"
                continue
            elif line.startswith("## Parameters") or line.startswith("##参数"):
                current_section = "parameters"
                continue
            elif line.startswith("## Examples") or line.startswith("##示例"):
                current_section = "examples"
                continue
            elif line.startswith("##") or line.startswith("#"):
                current_section = "description" if not instructions else "instructions"
                continue

            if current_section == "description":
                description += line + "\n"
            elif current_section == "triggers":
                if line.strip():
                    triggers.append(line.strip())
            elif current_section == "parameters":
                if line.strip() and ":" in line:
                    key, value = line.split(":")
                    parameters[key.strip()] = value.strip()
            elif current_section == "examples":
                if line.strip():
                    examples.append(line.strip())
            elif current_section == "instructions":
                instructions += line + "\n"

        version = self._extract_version(content)

        skill_def = {
            "name": name,
            "description": description.strip(),
            "instructions": instructions.strip(),
            "triggers": triggers,
            "parameters": parameters,
            "examples": examples,
            "version": version,
            "source_path": str(skill_file),
            "hash": self._compute_hash(content),
        }

        return skill_def

    def _extract_version(
        self,
        content: str,
    ) -> str:
        """Extract version from skill content.

        Args:
            content: Skill content

        Returns:
            Version string
        """
        match = re.search(r"version:\s*(\S+)", content)

        if match:
            return match.group(1)

        return "1.0.0"

    def _compute_hash(
        self,
        content: str,
    ) -> str:
        """Compute hash of skill content.

        Args:
            content: Skill content

        Returns:
            Hash string
        """
        return hashlib.md5(content.encode()).hexdigest()[:16]

    async def load_skill(
        self,
        skill_path: Path,
    ) -> dict[str, Any] | None:
        """Load a skill from a specific path.

        Args:
            skill_path: Path to SKILL.md

        Returns:
            Skill definition
        """
        skill_def = await self._parse_skill_file(skill_path)

        if skill_def:
            self._skills[skill_def["name"]] = skill_def

        return skill_def

    async def get_skill(
        self,
        skill_name: str,
    ) -> dict[str, Any] | None:
        """Get skill by name.

        Args:
            skill_name: Skill name

        Returns:
            Skill definition
        """
        return self._skills.get(skill_name)

    async def get_all_skills(self) -> list[dict[str, Any]]:
        """Get all registered skills.

        Returns:
            List of all skill definitions
        """
        return list(self._skills.values())

    async def search_skills(
        self,
        query: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Search skills by query.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of matching skills
        """
        query_lower = query.lower()

        scores = {}

        for skill_name, skill_def in self._skills.items():
            score = self._compute_search_score(skill_def, query_lower)

            if score > 0:
                scores[skill_name] = score

        sorted_skills = sorted(
            scores.items(),
            key=lambda x: x[1],
            reverse=True,
        )

        results = []

        for skill_name, score in sorted_skills[:limit]:
            skill_def = self._skills[skill_name]
            skill_def["_search_score"] = score
            results.append(skill_def)

        return results

    def _compute_search_score(
        self,
        skill_def: dict[str, Any],
        query: str,
    ) -> float:
        """Compute search score for skill.

        Args:
            skill_def: Skill definition
            query: Search query

        Returns:
            Search score
        """
        score = 0.0

        name = skill_def.get("name", "").lower()
        description = skill_def.get("description", "").lower()
        instructions = skill_def.get("instructions", "").lower()
        triggers = skill_def.get("triggers", [])

        if query in name:
            score += 2.0

        if query in description:
            score += 1.0

        if query in instructions:
            score += 0.5

        for trigger in triggers:
            if query in trigger.lower():
                score += 1.5

        return score

    async def register_skill(
        self,
        skill_def: dict[str, Any],
    ) -> bool:
        """Register a skill manually.

        Args:
            skill_def: Skill definition

        Returns:
            True if registration succeeded
        """
        skill_name = skill_def.get("name")

        if not skill_name:
            return False

        self._skills[skill_name] = skill_def

        self._skill_metadata[skill_name] = {
            "registered_at": datetime.now().isoformat(),
            "source": "manual",
        }

        logger.info(f"Registered skill: {skill_name}")

        return True

    async def unregister_skill(
        self,
        skill_name: str,
    ) -> bool:
        """Unregister a skill.

        Args:
            skill_name: Skill name

        Returns:
            True if unregistration succeeded
        """
        if skill_name not in self._skills:
            return False

        self._skills.pop(skill_name, None)
        self._skill_metadata.pop(skill_name, None)

        logger.info(f"Unregistered skill: {skill_name}")

        return True

    async def get_skill_metadata(
        self,
        skill_name: str,
    ) -> dict[str, Any] | None:
        """Get skill metadata.

        Args:
            skill_name: Skill name

        Returns:
            Metadata dictionary
        """
        return self._skill_metadata.get(skill_name)

    async def validate_skill(
        self,
        skill_def: dict[str, Any],
    ) -> dict[str, Any]:
        """Validate skill definition.

        Args:
            skill_def: Skill definition

        Returns:
            Validation result
        """
        issues = []

        if not skill_def.get("name"):
            issues.append("Missing skill name")

        if not skill_def.get("description"):
            issues.append("Missing skill description")

        if not skill_def.get("instructions"):
            issues.append("Missing skill instructions")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "skill_name": skill_def.get("name", "unknown"),
        }

    async def get_registry_statistics(self) -> dict[str, Any]:
        """Get registry statistics.

        Returns:
            Statistics dictionary
        """
        return {
            "total_skills": len(self._skills),
            "initialized": self._initialized,
            "skill_dirs": len(self._skill_dirs),
            "skills_by_source": {
                source: sum(
                    1 for meta in self._skill_metadata.values() if meta.get("source") == source
                )
                for source in ["file", "manual", "captured", "derived"]
            },
        }
