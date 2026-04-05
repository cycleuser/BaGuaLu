"""Skill Types - Type definitions for skills system."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Any


class SkillOrigin(StrEnum):
    """Skill origin types."""

    IMPORTED = "imported"
    CAPTURED = "captured"
    DERIVED = "derived"
    FIXED = "fixed"
    MANUAL = "manual"


class EvolutionType(StrEnum):
    """Skill evolution types."""

    FIX = "fix"
    DERIVED = "derived"
    CAPTURED = "captured"


class SkillPriority(StrEnum):
    """Skill priority levels."""

    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


@dataclass
class SkillCommand:
    """Skill command definition."""

    command: str
    description: str
    arguments: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)


@dataclass
class SkillTrigger:
    """Skill trigger definition."""

    condition: str
    keywords: list[str] = field(default_factory=list)
    patterns: list[str] = field(default_factory=list)


@dataclass
class SkillParameter:
    """Skill parameter definition."""

    name: str
    type: str
    default: Any = None
    description: str = ""
    required: bool = False
    choices: list[str] = field(default_factory=list)


@dataclass
class SkillLineage:
    """Skill evolution lineage."""

    origin: SkillOrigin
    generation: int = 0
    parent_skill_ids: list[str] = field(default_factory=list)
    source_task_id: str | None = None
    change_summary: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""


@dataclass
class SkillFrontmatter:
    """YAML frontmatter metadata from SKILL.md."""

    name: str
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    license: str = "MIT"
    priority: int = 50
    auto_load: bool = False
    compatibility: list[str] = field(default_factory=list)
    triggers: list[str] = field(default_factory=list)
    commands: list[dict[str, str]] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    requires: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)


@dataclass
class SkillDefinition:
    """Complete skill definition."""

    name: str
    description: str
    instructions: str
    frontmatter: SkillFrontmatter | None = None
    triggers: list[SkillTrigger] = field(default_factory=list)
    commands: list[SkillCommand] = field(default_factory=list)
    parameters: list[SkillParameter] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)
    rules: list[str] = field(default_factory=list)
    lineage: SkillLineage | None = None
    source_path: Path | None = None
    skill_id: str = ""
    hash: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "instructions": self.instructions,
            "triggers": [
                {
                    "condition": t.condition,
                    "keywords": t.keywords,
                    "patterns": t.patterns,
                }
                for t in self.triggers
            ],
            "commands": [
                {
                    "command": c.command,
                    "description": c.description,
                    "arguments": c.arguments,
                }
                for c in self.commands
            ],
            "parameters": [
                {
                    "name": p.name,
                    "type": p.type,
                    "default": p.default,
                    "required": p.required,
                }
                for p in self.parameters
            ],
            "examples": self.examples,
            "rules": self.rules,
            "skill_id": self.skill_id,
            "source_path": str(self.source_path) if self.source_path else None,
        }
