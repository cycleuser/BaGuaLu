"""CLI entry point for BaGuaLu (inspired by OpenLaoKe and OpenHarness)."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

from bagualu.core import BaGuaLuCore
from bagualu.config import ConfigManager, ConfigWizard
from bagualu.utils.logging import Logger

logger = Logger.get_logger(__name__)
console = Console()


@click.group(invoke_without_command=True)
@click.option("--config", "-c", type=click.Path(), help="Configuration file path")
@click.option("--version", "-v", is_flag=True, help="Show version")
@click.option("--init", is_flag=True, help="Initialize configuration")
@click.pass_context
def cli(ctx: click.Context, config: Optional[str], version: bool, init: bool) -> None:
    """BaGuaLu (八卦炉) - Intelligent Agent Orchestration Platform."""
    if version:
        from bagualu import __version__

        console.print(f"BaGuaLu version {__version__}")
        return

    if init:
        asyncio.run(initialize_config(config))
        return

    if ctx.invoked_subcommand is None:
        asyncio.run(interactive_mode(config))


@cli.command()
@click.option("--config", "-c", type=click.Path(), help="Configuration file")
@click.option("--provider", "-p", help="Provider name")
@click.option("--model", "-m", help="Model identifier")
def config(config: Optional[str], provider: Optional[str], model: Optional[str]) -> None:
    """Configure BaGuaLu."""
    asyncio.run(configure(config, provider, model))


@cli.command()
@click.argument("name")
@click.option("--role", "-r", default="executor", help="Agent role")
@click.option("--provider", "-p", help="Provider name")
@click.option("--model", "-m", help="Model identifier")
@click.option("--skills", "-s", multiple=True, help="Skills to load")
def deploy(
    name: str, role: str, provider: Optional[str], model: Optional[str], skills: tuple
) -> None:
    """Deploy an agent."""
    asyncio.run(deploy_agent(name, role, provider, model, list(skills)))


@cli.command()
@click.argument("workflow_file", type=click.Path(exists=True))
@click.option("--inputs", "-i", help="JSON inputs")
def run(workflow_file: str, inputs: Optional[str]) -> None:
    """Execute a workflow."""
    asyncio.run(execute_workflow(workflow_file, inputs))


@cli.command()
@click.option("--host", "-h", default="0.0.0.0", help="Host address")
@click.option("--port", "-p", default=8000, help="Port number")
def server(host: str, port: int) -> None:
    """Start API server."""
    import asyncio
    from bagualu.web.api_server import APIServer

    console.print(f"[bold]Starting API server on {host}:{port}[/bold]")

    # Initialize core synchronously
    core = BaGuaLuCore()
    asyncio.run(core.initialize())

    # Start server
    server = APIServer(core)
    server.run_server(host, port)


@cli.command()
def status() -> None:
    """Show cluster status."""
    asyncio.run(show_status())


async def initialize_config(config_path: Optional[str]) -> None:
    """Initialize configuration."""
    console.print(
        Panel.fit(
            "[bold cyan]BaGuaLu Configuration[/bold cyan]\n八卦炉配置向导",
            border_style="cyan",
        )
    )

    config_manager = ConfigManager(Path(config_path) if config_path else None)

    wizard = ConfigWizard(config_manager)
    await wizard.run()


async def configure(
    config_path: Optional[str], provider: Optional[str], model: Optional[str]
) -> None:
    """Configure BaGuaLu."""
    config_manager = ConfigManager(Path(config_path) if config_path else None)

    await config_manager.load()

    if provider:
        await config_manager.set_active_provider(provider)
        console.print(f"[green]✓[/green] Active provider: {provider}")

    if model:
        active = await config_manager.get_active_provider_config()
        if active:
            active.model = model
            await config_manager.save()
            console.print(f"[green]✓[/green] Model: {model}")


async def deploy_agent(
    name: str,
    role: str,
    provider: Optional[str],
    model: Optional[str],
    skills: list,
) -> None:
    """Deploy an agent."""
    console.print(f"[bold]Deploying agent:[/bold] {name}")

    core = BaGuaLuCore()

    agent_id = await core.deploy_agent(
        name=name,
        role=role,
        provider=provider,
        model=model,
        skills=skills,
    )

    console.print(f"[green]✓[/green] Agent deployed: {agent_id}")


async def execute_workflow(workflow_file: str, inputs: Optional[str]) -> None:
    """Execute a workflow."""
    import json

    console.print(f"[bold]Executing workflow:[/bold] {workflow_file}")

    workflow_path = Path(workflow_file)

    if not workflow_path.exists():
        console.print(f"[red]Error:[/red] Workflow file not found: {workflow_file}")
        return

    content = workflow_path.read_text()

    if workflow_path.suffix == ".json":
        workflow_config = json.loads(content)
    else:
        import yaml

        workflow_config = yaml.safe_load(content)

    inputs_data = json.loads(inputs) if inputs else {}

    core = BaGuaLuCore()

    workflow_id = await core.create_workflow(workflow_config)

    result = await core.execute_workflow(workflow_id, inputs_data)

    console.print(f"[green]✓[/green] Workflow executed")
    console.print_json(json.dumps(result, indent=2))


async def start_server(host: str, port: int) -> None:
    """Start API server."""
    from bagualu.web.api_server import APIServer

    console.print(f"[bold]Starting API server on {host}:{port}[/bold]")

    core = BaGuaLuCore()
    await core.initialize()

    server = APIServer(core)
    server.run_server(host, port)


async def show_status() -> None:
    """Show cluster status."""
    console.print("[bold]Cluster Status[/bold]")

    core = BaGuaLuCore()
    await core.initialize()

    status = await core.cluster.get_cluster_status()

    console.print(f"Total agents: {status['total_agents']}")
    console.print(f"Running: {status['running']}")

    for agent in status["agents"]:
        console.print(f"  - {agent['name']} ({agent['role']}): {agent['status']}")


async def interactive_mode(config_path: Optional[str]) -> None:
    """Run in interactive mode."""
    console.print(
        Panel.fit(
            "[bold cyan]BaGuaLu (八卦炉)[/bold cyan]\n"
            "Intelligent Agent Orchestration Platform\n"
            "[dim]Type 'help' for commands[/dim]",
            border_style="cyan",
        )
    )

    core = BaGuaLuCore(config_path=Path(config_path) if config_path else None)

    await core.initialize()

    while True:
        try:
            command = Prompt.ask("\n[bold cyan]bagualu>[/bold cyan]")

            if command.lower() in ["exit", "quit"]:
                console.print("[yellow]Goodbye![/yellow]")
                break

            if command.lower() == "help":
                show_help()
                continue

            if command.lower() == "status":
                await show_status()
                continue

            if command.lower() == "deploy":
                name = Prompt.ask("Agent name")
                role = Prompt.ask("Role", default="executor")

                agent_id = await core.deploy_agent(name=name, role=role)
                console.print(f"[green]✓[/green] Deployed: {agent_id}")
                continue

            if command.lower() == "evolve":
                skill_name = Prompt.ask("Skill name")
                evolved = await core.evolve_skill(skill_name)
                console.print(f"[green]✓[/green] Evolved: {evolved}")
                continue

            console.print(f"[yellow]Unknown command: {command}[/yellow]")

        except KeyboardInterrupt:
            console.print("\n[yellow]Use 'exit' to quit[/yellow]")
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")


def show_help() -> None:
    """Show help message."""
    console.print("""
[bold]Commands:[/bold]
  help      - Show this help message
  status    - Show cluster status
  deploy    - Deploy a new agent
  evolve    - Trigger skill evolution
  exit      - Exit BaGuaLu

[bold]Shortcuts:[/bold]
  Ctrl+C    - Cancel current input
  Ctrl+D    - Exit
""")


def main() -> None:
    """Main entry point."""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
