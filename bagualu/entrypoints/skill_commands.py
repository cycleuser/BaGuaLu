"""Skill management commands for BaGuaLu CLI."""

from __future__ import annotations

import asyncio

import click
from rich.console import Console
from rich.table import Table

from bagualu.skills import (
    get_skill_registry,
    load_skill,
    rescan_skills,
)

console = Console()


@click.group()
def skill():
    """Manage skills: list, install, remove, info."""
    pass


@skill.command("list")
@click.option("--source", "-s", help="Filter by source (claude-code, opencode, openlaoke, bagualu)")
def list_skills(source: str | None):
    """List all available skills."""
    registry = get_skill_registry()
    skills = registry.get_all_skills()

    if source:
        skills = [s for s in skills if s.source == source]

    table = Table(title=f"Available Skills ({len(skills)} total)")
    table.add_column("Name", style="cyan")
    table.add_column("Source", style="green")
    table.add_column("Version", style="yellow")
    table.add_column("Description", style="white")

    for skill in sorted(skills, key=lambda s: s.name):
        desc = skill.description[:60] + "..." if len(skill.description) > 60 else skill.description
        table.add_row(skill.name, skill.source, skill.version, desc)

    console.print(table)


@skill.command("info")
@click.argument("skill_name")
def skill_info(skill_name: str):
    """Show detailed information about a skill."""
    skill = load_skill(skill_name)

    if not skill:
        console.print(f"[red]Skill not found: {skill_name}[/red]")
        console.print("\nUse [cyan]bagualu skill list[/cyan] to see available skills.")
        return

    console.print(f"\n[bold cyan]Skill: {skill.name}[/bold cyan]")
    console.print(f"[green]Version:[/green] {skill.version}")
    console.print(f"[green]Source:[/green] {skill.source}")

    if skill.description:
        console.print(f"\n[bold]Description:[/bold]\n{skill.description}")

    if skill.allowed_tools:
        console.print(f"\n[green]Allowed tools:[/green] {', '.join(skill.allowed_tools)}")

    if skill.path:
        console.print(f"\n[green]Path:[/green] {skill.path}")


@skill.command("install")
@click.argument("repo_url")
@click.option("--name", "-n", help="Specific skill name to install")
def install_skill(repo_url: str, name: str | None):
    """Install skills from a GitHub repository."""
    from bagualu.core import BaGuaLuCore

    async def do_install():
        core = BaGuaLuCore()
        await core.initialize()

        console.print(f"\n[cyan]Installing skills from: {repo_url}[/cyan]")
        if name:
            console.print(f"[cyan]Filtering: {name}[/cyan]")

        results = await core.install_skill(repo_url, name)

        success_count = sum(1 for r in results if r.success)
        fail_count = sum(1 for r in results if not r.success)

        console.print(
            f"\n[bold]Installation complete:[/bold] {success_count} succeeded, {fail_count} failed"
        )

        for r in results:
            if r.success:
                console.print(f"  [green]✓[/green] {r.skill_name}: {r.message}")
            else:
                console.print(f"  [red]✗[/red] {r.skill_name}: {r.message}")

        if success_count > 0:
            console.print("\n[green]Skills are now available![/green]")
            console.print("Use [cyan]bagualu skill list[/cyan] to see all skills.")

    asyncio.run(do_install())


@skill.command("rescan")
def rescan():
    """Rescan all skill directories."""
    total = rescan_skills()
    console.print(f"[green]Rescanned skills. Total available: {total}[/green]")


@skill.command("sources")
def list_sources():
    """List skill source directories."""
    registry = get_skill_registry()
    sources = registry.get_sources()

    table = Table(title="Skill Sources")
    table.add_column("Source", style="cyan")
    table.add_column("Path", style="green")

    for path, name in sources:
        table.add_row(name, str(path))

    console.print(table)


if __name__ == "__main__":
    skill()
