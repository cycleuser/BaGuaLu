"""Skill Store - Skill persistence and versioning."""

from __future__ import annotations

import asyncio
import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

from bagualu.utils.logging import Logger

logger = Logger.get_logger(__name__)


class SkillStore:
    """Skill store for persistence and versioning.

    Features:
    - SQLite-based persistence
    - Version DAG tracking
    - Lineage management
    - Quality metrics storage
    """

    def __init__(
        self,
        db_path: Optional[Path] = None,
    ) -> None:
        """Initialize skill store.

        Args:
            db_path: Path to SQLite database
        """
        self._db_path = db_path or Path.home() / ".bagualu" / "skills.db"
        self._db: Optional[sqlite3.Connection] = None
        self._initialized = False

        logger.info(f"Skill store initialized (db: {self._db_path})")

    async def initialize(self) -> None:
        """Initialize skill store asynchronously."""
        if self._initialized:
            return

        self._db_path.parent.mkdir(parents=True, exist_ok=True)

        self._db = sqlite3.connect(str(self._db_path))

        await self._create_tables()

        self._initialized = True

        logger.info("Skill store fully initialized")

    async def _create_tables(self) -> None:
        """Create database tables."""
        cursor = self._db.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS skills (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                version TEXT NOT NULL,
                definition TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS skill_versions (
                id TEXT PRIMARY KEY,
                skill_name TEXT NOT NULL,
                version TEXT NOT NULL,
                parent_version TEXT,
                evolution_type TEXT,
                created_at TEXT NOT NULL,
                definition TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS skill_lineage (
                skill_name TEXT NOT NULL,
                version TEXT NOT NULL,
                parent_name TEXT,
                parent_version TEXT,
                lineage_type TEXT,
                created_at TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS skill_metrics (
                skill_name TEXT NOT NULL,
                version TEXT NOT NULL,
                execution_count INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                failure_count INTEGER DEFAULT 0,
                quality_score REAL DEFAULT 0.0,
                updated_at TEXT NOT NULL
            )
        """)

        self._db.commit()

        logger.info("Database tables created")

    async def register_skill(
        self,
        skill_def: Dict[str, Any],
    ) -> str:
        """Register a skill.

        Args:
            skill_def: Skill definition

        Returns:
            Skill ID
        """
        if not self._db:
            await self.initialize()

        skill_id = f"{skill_def.get('name')}-{skill_def.get('version', '1.0.0')}"

        definition_json = json.dumps(skill_def)

        now = datetime.now().isoformat()

        cursor = self._db.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO skills
            (id, name, version, definition, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                skill_id,
                skill_def.get("name"),
                skill_def.get("version", "1.0.0"),
                definition_json,
                now,
                now,
            ),
        )

        cursor.execute(
            """
            INSERT OR REPLACE INTO skill_versions
            (id, skill_name, version, parent_version, evolution_type, created_at, definition)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                skill_id,
                skill_def.get("name"),
                skill_def.get("version", "1.0.0"),
                skill_def.get("parent_version"),
                skill_def.get("evolution_type"),
                now,
                definition_json,
            ),
        )

        cursor.execute(
            """
            INSERT OR REPLACE INTO skill_metrics
            (skill_name, version, execution_count, success_count, failure_count, quality_score, updated_at)
            VALUES (?, ?, 0, 0, 0, 0.0, ?)
        """,
            (
                skill_def.get("name"),
                skill_def.get("version", "1.0.0"),
                now,
            ),
        )

        self._db.commit()

        logger.info(f"Registered skill: {skill_id}")

        return skill_id

    async def get_skill(
        self,
        skill_name: str,
        version: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Get skill by name and version.

        Args:
            skill_name: Skill name
            version: Version (optional, defaults to latest)

        Returns:
            Skill definition
        """
        if not self._db:
            await self.initialize()

        cursor = self._db.cursor()

        if version:
            skill_id = f"{skill_name}-{version}"

            cursor.execute(
                """
                SELECT definition FROM skills WHERE id = ?
            """,
                (skill_id,),
            )
        else:
            cursor.execute(
                """
                SELECT definition FROM skills
                WHERE name = ?
                ORDER BY updated_at DESC LIMIT 1
            """,
                (skill_name,),
            )

        row = cursor.fetchone()

        if row:
            return json.loads(row[0])

        return None

    async def update_skill_version(
        self,
        skill_name: str,
        new_skill_def: Dict[str, Any],
    ) -> str:
        """Update skill with new version.

        Args:
            skill_name: Skill name
            new_skill_def: New skill definition

        Returns:
            New skill ID
        """
        if not self._db:
            await self.initialize()

        skill_id = await self.register_skill(new_skill_def)

        parent_version = new_skill_def.get("parent_version")

        if parent_version:
            cursor = self._db.cursor()

            cursor.execute(
                """
                INSERT INTO skill_lineage
                (skill_name, version, parent_name, parent_version, lineage_type, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    skill_name,
                    new_skill_def.get("version"),
                    skill_name,
                    parent_version,
                    new_skill_def.get("evolution_type", "update"),
                    datetime.now().isoformat(),
                ),
            )

            self._db.commit()

        logger.info(f"Updated skill: {skill_name} to version {new_skill_def.get('version')}")

        return skill_id

    async def get_lineage(
        self,
        skill_name: str,
    ) -> Dict[str, Any]:
        """Get skill lineage.

        Args:
            skill_name: Skill name

        Returns:
            Lineage information
        """
        if not self._db:
            await self.initialize()

        cursor = self._db.cursor()

        cursor.execute(
            """
            SELECT skill_name, version, parent_name, parent_version, lineage_type, created_at
            FROM skill_lineage
            WHERE skill_name = ?
            ORDER BY created_at DESC
        """,
            (skill_name,),
        )

        lineage_entries = []

        for row in cursor.fetchall():
            lineage_entries.append(
                {
                    "skill_name": row[0],
                    "version": row[1],
                    "parent_name": row[2],
                    "parent_version": row[3],
                    "lineage_type": row[4],
                    "created_at": row[5],
                }
            )

        return {
            "skill_name": skill_name,
            "lineage": lineage_entries,
            "version_count": len(lineage_entries),
        }

    async def update_metrics(
        self,
        skill_name: str,
        version: str,
        success: bool,
    ) -> None:
        """Update skill metrics after execution.

        Args:
            skill_name: Skill name
            version: Version
            success: Whether execution succeeded
        """
        if not self._db:
            await self.initialize()

        cursor = self._db.cursor()

        cursor.execute(
            """
            UPDATE skill_metrics
            SET execution_count = execution_count + 1,
                success_count = success_count + ?,
                failure_count = failure_count + ?,
                updated_at = ?
            WHERE skill_name = ? AND version = ?
        """,
            (
                1 if success else 0,
                0 if success else 1,
                datetime.now().isoformat(),
                skill_name,
                version,
            ),
        )

        self._db.commit()

    async def get_metrics(
        self,
        skill_name: str,
        version: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Get skill metrics.

        Args:
            skill_name: Skill name
            version: Version (optional)

        Returns:
            Metrics dictionary
        """
        if not self._db:
            await self.initialize()

        cursor = self._db.cursor()

        if version:
            cursor.execute(
                """
                SELECT execution_count, success_count, failure_count, quality_score, updated_at
                FROM skill_metrics
                WHERE skill_name = ? AND version = ?
            """,
                (skill_name, version),
            )
        else:
            cursor.execute(
                """
                SELECT execution_count, success_count, failure_count, quality_score, updated_at
                FROM skill_metrics
                WHERE skill_name = ?
                ORDER BY updated_at DESC LIMIT 1
            """,
                (skill_name,),
            )

        row = cursor.fetchone()

        if row:
            return {
                "execution_count": row[0],
                "success_count": row[1],
                "failure_count": row[2],
                "quality_score": row[3],
                "updated_at": row[4],
                "success_rate": row[1] / row[0] if row[0] > 0 else 0.0,
            }

        return None

    async def cleanup_versions(
        self,
        skill_name: str,
        keep_versions: int = 5,
    ) -> List[str]:
        """Clean up old skill versions.

        Args:
            skill_name: Skill name
            keep_versions: Number of versions to keep

        Returns:
            List of removed version IDs
        """
        if not self._db:
            await self.initialize()

        cursor = self._db.cursor()

        cursor.execute(
            """
            SELECT id FROM skill_versions
            WHERE skill_name = ?
            ORDER BY created_at DESC
        """,
            (skill_name,),
        )

        all_versions = [row[0] for row in cursor.fetchall()]

        removed_ids = []

        for version_id in all_versions[keep_versions:]:
            cursor.execute(
                """
                DELETE FROM skill_versions WHERE id = ?
            """,
                (version_id,),
            )

            cursor.execute(
                """
                DELETE FROM skill_metrics
                WHERE skill_name = ? AND version = ?
            """,
                (
                    skill_name,
                    version_id.split("-")[-1],
                ),
            )

            removed_ids.append(version_id)

        self._db.commit()

        logger.info(f"Cleaned up {len(removed_ids)} versions for {skill_name}")

        return removed_ids

    async def get_all_skills_with_metrics(self) -> List[Dict[str, Any]]:
        """Get all skills with their metrics.

        Returns:
            List of skills with metrics
        """
        if not self._db:
            await self.initialize()

        cursor = self._db.cursor()

        cursor.execute("""
            SELECT s.name, s.version, s.definition, m.execution_count, m.success_count, m.failure_count, m.quality_score
            FROM skills s
            LEFT JOIN skill_metrics m ON s.name = m.skill_name AND s.version = m.version
            ORDER BY s.updated_at DESC
        """)

        skills = []

        for row in cursor.fetchall():
            skill_def = json.loads(row[2])
            skill_def["metrics"] = {
                "execution_count": row[3] or 0,
                "success_count": row[4] or 0,
                "failure_count": row[5] or 0,
                "quality_score": row[6] or 0.0,
            }
            skills.append(skill_def)

        return skills

    async def close(self) -> None:
        """Close database connection."""
        if self._db:
            self._db.close()
            self._db = None
            self._initialized = False

            logger.info("Skill store closed")
