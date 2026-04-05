"""Enhanced Skill Registry - Discovers and loads skills from all installed sources.

Supports:
- Claude Code skills (~/.claude/skills/)
- OpenCode skills (~/.config/opencode/skills/)
- OpenLaoKe skills (~/.openlaoke/skills/)
- BaGuaLu skills (~/.bagualu/skills/)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


def _sanitize_frontmatter(frontmatter: str) -> str:
    """Sanitize YAML frontmatter with colons in values."""
    lines = frontmatter.splitlines()
    result = []

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("#") or stripped == "":
            result.append(line)
            continue

        if line.startswith((" ", "\t")):
            result.append(line)
            continue

        kv = re.match(r"^([a-zA-Z_][a-zA-Z0-9_-]*)\s*:\s*(.*)$", line)
        if not kv:
            result.append(line)
            continue

        key = kv.group(1)
        value = kv.group(2).strip()

        if not value or value in (">", "|") or value.startswith(('"', "'")):
            result.append(line)
            continue

        if ":" in value:
            result.append(f"{key}: |-")
            result.append(f"  {value}")
            continue

        result.append(line)

    return "\n".join(result)


@dataclass
class Skill:
    """A skill definition loaded from SKILL.md file."""

    name: str
    description: str = ""
    version: str = "1.0.0"
    allowed_tools: list[str] = field(default_factory=list)
    content: str = ""
    path: Path | None = None
    source: str = "unknown"
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_file(cls, path: Path, source: str = "unknown") -> Skill | None:
        """Load a skill from SKILL.md file."""
        if not path.exists():
            return None

        try:
            content = path.read_text(encoding="utf-8")
            return cls.from_content(content, path, source)
        except Exception as e:
            print(f"Error loading skill {path}: {e}")
            return None

    @classmethod
    def from_content(cls, content: str, path: Path | None = None, source: str = "unknown") -> Skill:
        """Parse skill from content string."""
        metadata = {}
        body = content

        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1].strip()
                body = parts[2].strip()

                try:
                    metadata = yaml.safe_load(frontmatter) or {}
                except yaml.YAMLError:
                    try:
                        sanitized = _sanitize_frontmatter(frontmatter)
                        metadata = yaml.safe_load(sanitized) or {}
                    except yaml.YAMLError:
                        metadata = cls._extract_frontmatter_manual(frontmatter)

        name = metadata.get("name", "")
        if not name or name == "SKILL":
            if path and path.parent:
                name = path.parent.name
            elif path:
                name = path.stem
            else:
                name = "unknown"

        description = metadata.get("description", "")
        if isinstance(description, str):
            description = description.strip()
        version = metadata.get("version", "1.0.0")
        allowed_tools = metadata.get("allowed-tools", metadata.get("allowed_tools", []))

        return cls(
            name=name,
            description=description,
            version=str(version),
            allowed_tools=allowed_tools if isinstance(allowed_tools, list) else [],
            content=body,
            path=path,
            source=source,
            metadata=metadata,
        )

    @staticmethod
    def _extract_frontmatter_manual(frontmatter: str) -> dict[str, Any]:
        """Extract key-value pairs from broken frontmatter."""
        result = {}
        for line in frontmatter.splitlines():
            kv = re.match(r"^([a-zA-Z_][a-zA-Z0-9_-]*)\s*:\s*(.*)$", line.strip())
            if kv:
                key = kv.group(1)
                value = kv.group(2).strip()
                if value:
                    result[key] = value
        return result

    def get_system_prompt(self) -> str:
        """Get the skill content as system prompt."""
        return self.content


class EnhancedSkillRegistry:
    """Enhanced registry that discovers skills from all sources."""

    def __init__(self):
        self._skills: dict[str, Skill] = {}
        self._skill_dirs: list[tuple[Path, str]] = []
        self._initialized = False

    def discover_all_skills(self) -> int:
        """Discover skills from all default directories."""
        if self._initialized:
            return len(self._skills)

        home = Path.home()

        skill_sources = [
            (home / ".claude" / "skills", "claude-code", 1),
            (home / ".openlaoke" / "skills", "openlaoke", 2),
            (home / ".config" / "opencode" / "skills", "opencode", 3),
            (home / ".bagualu" / "skills", "bagualu", 4),
        ]

        total = 0
        for skill_dir, source, _priority in skill_sources:
            if skill_dir.exists():
                count = self._load_skills_from_dir(skill_dir, source)
                total += count
                if count > 0:
                    self._skill_dirs.append((skill_dir, source))

        self._initialized = True
        return total

    def _load_skills_from_dir(self, directory: Path, source: str) -> int:
        """Load all skills from a directory."""
        count = 0

        for skill_dir in directory.iterdir():
            if not skill_dir.is_dir():
                continue

            if skill_dir.is_symlink():
                skill_dir = skill_dir.resolve()

            skill_file = skill_dir / "SKILL.md"
            if skill_file.exists():
                skill = Skill.from_file(skill_file, source)
                if skill and skill.name and skill.name not in self._skills:
                    self._skills[skill.name] = skill
                    count += 1

        return count

    def add_skill_directory(self, directory: Path | str, source: str = "custom") -> int:
        """Add a custom directory to search for skills."""
        directory = Path(directory).expanduser()
        if not directory.exists():
            return 0

        self._skill_dirs.append((directory, source))
        return self._load_skills_from_dir(directory, source)

    def get_skill(self, name: str) -> Skill | None:
        """Get a skill by name."""
        if not self._initialized:
            self.discover_all_skills()
        return self._skills.get(name)

    def list_skills(self) -> list[str]:
        """List all available skill names."""
        if not self._initialized:
            self.discover_all_skills()
        return list(self._skills.keys())

    def get_all_skills(self) -> list[Skill]:
        """Get all loaded skills."""
        if not self._initialized:
            self.discover_all_skills()
        return list(self._skills.values())

    def get_skills_by_source(self, source: str) -> list[Skill]:
        """Get skills filtered by source."""
        if not self._initialized:
            self.discover_all_skills()
        return [s for s in self._skills.values() if s.source == source]

    def get_skill_prompt(self, name: str) -> str | None:
        """Get the system prompt for a skill."""
        skill = self.get_skill(name)
        if skill:
            return skill.get_system_prompt()
        return None

    def has_skill(self, name: str) -> bool:
        """Check if a skill is loaded."""
        if not self._initialized:
            self.discover_all_skills()
        return name in self._skills

    def get_sources(self) -> list[tuple[Path, str]]:
        """Get list of skill sources."""
        return self._skill_dirs

    def rescan(self) -> int:
        """Rescan all skill directories."""
        self._skills.clear()
        self._initialized = False
        return self.discover_all_skills()


_global_registry: EnhancedSkillRegistry | None = None


def get_skill_registry() -> EnhancedSkillRegistry:
    """Get the global skill registry."""
    global _global_registry

    if _global_registry is None:
        _global_registry = EnhancedSkillRegistry()
        _global_registry.discover_all_skills()

    return _global_registry


def rescan_skills() -> int:
    """Rescan all skill directories."""
    global _global_registry
    if _global_registry is None:
        _global_registry = EnhancedSkillRegistry()
    return _global_registry.rescan()


def load_skill(name: str) -> Skill | None:
    """Load a specific skill by name."""
    return get_skill_registry().get_skill(name)


def list_available_skills() -> list[str]:
    """List all available skill names."""
    return get_skill_registry().list_skills()


def get_skill_system_prompt(skill_names: list[str]) -> str:
    """Get combined system prompt for multiple skills."""
    registry = get_skill_registry()
    prompts = []

    for name in skill_names:
        skill = registry.get_skill(name)
        if skill:
            prompts.append(f"\n## Skill: {skill.name}\n\n{skill.content}")

    return "\n".join(prompts)
