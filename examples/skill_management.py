"""Example: Skill management - list, install, and load skills.

This example demonstrates how to:
1. List available skills from multiple sources (OpenCode, Claude Code, OpenLaoKe)
2. Get detailed information about a specific skill
3. Install skills from GitHub repositories
4. Load and use skills in agents
5. Rescan skill directories to discover new skills
"""

import asyncio
from pathlib import Path

from bagualu import BaGuaLuCore


async def main() -> None:
    """Demonstrate skill management capabilities."""

    print("=" * 60)
    print("BaGuaLu Skill Management Example")
    print("=" * 60)

    core = BaGuaLuCore(workspace=Path.home() / ".bagualu" / "workspace")
    await core.initialize()

    print("\n1. List all available skills from all sources")
    print("-" * 60)
    skills = core.list_skills()
    print(f"Found {len(skills)} skills:")
    for i, skill_name in enumerate(skills[:10], 1):
        print(f"  {i}. {skill_name}")
    if len(skills) > 10:
        print(f"  ... and {len(skills) - 10} more")

    print("\n2. Get detailed information about a skill")
    print("-" * 60)
    if skills:
        skill_name = skills[0]
        skill_info = core.get_skill_info(skill_name)
        if skill_info:
            print(f"Skill: {skill_name}")
            print(f"  Name: {skill_info.name}")
            print(
                f"  Description: {skill_info.description[:100] if skill_info.description else 'N/A'}..."
            )
            print(f"  Version: {skill_info.version}")
            print(f"  Source: {skill_info.source}")
            print(f"  Location: {skill_info.path}")

    print("\n3. List skill source directories")
    print("-" * 60)
    from bagualu.skills import get_skill_registry

    registry = get_skill_registry()
    sources = registry.get_sources()
    for path, source_name in sources:
        exists = "✓" if path.exists() else "✗"
        print(f"  {exists} {source_name}: {path}")

    print("\n4. Install a skill from GitHub (example)")
    print("-" * 60)
    print("To install a skill from GitHub:")
    print("  CLI: bagualu skill install https://github.com/user/skill-repo")
    print("  Python API:")
    print("    success = await core.install_skill(")
    print("        repo_url='https://github.com/user/skill-repo',")
    print("        skill_name='my-skill'")
    print("    )")

    print("\n5. Rescan skill directories")
    print("-" * 60)
    print("After manually adding skills, rescan to discover them:")
    print("  CLI: bagualu skill rescan")
    print("  Python API: await core.skills.rescan()")

    print("\n6. Load a skill into an agent")
    print("-" * 60)
    if skills:
        agent_id = await core.deploy_agent(
            name="skill-demo-agent",
            role="executor",
            provider="ollama",
            model="llama2",
            skills=[skills[0]],
        )
        print(f"Deployed agent with skill '{skills[0]}' (ID: {agent_id})")

        cluster_status = await core.cluster.get_cluster_status()
        print(f"Cluster status: {cluster_status}")

    print("\n7. Skill evolution example")
    print("-" * 60)
    print("Evolve skills based on execution history:")
    print("  CLI: bagualu skill evolve <skill-name>")
    print("  Python API:")
    print("    evolved = await core.evolve_skill(")
    print("        skill_name='my-skill',")
    print("        evolution_type='auto'")
    print("    )")

    print("\n" + "=" * 60)
    print("Skill management example completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
