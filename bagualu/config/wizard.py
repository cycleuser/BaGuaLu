"""Config Wizard - Interactive configuration wizard."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from bagualu.config.config_manager import ConfigManager
from bagualu.utils.logging import Logger

logger = Logger.get_logger(__name__)
console = Console()


class ConfigWizard:
    """Interactive configuration wizard (inspired by OpenLaoKe).

    Features:
    - Step-by-step provider configuration
    - API key input
    - Model selection
    - Multiple Coding Plan API keys support
    - Local provider (Ollama, LMStudio) setup
    """

    def __init__(
        self,
        config_manager: ConfigManager,
    ) -> None:
        """Initialize configuration wizard.

        Args:
            config_manager: Configuration manager
        """
        self._config_manager = config_manager

    async def run(self) -> None:
        """Run interactive configuration wizard."""
        await self._config_manager.load()

        console.clear()
        console.print(
            Panel.fit(
                "[bold cyan]BaGuaLu Configuration Wizard[/bold cyan]\n[dim]八卦炉配置向导[/dim]",
                border_style="cyan",
            )
        )
        console.print()

        await self._configure_provider()

        await self._configure_settings()

        await self._config_manager.save()

        console.print()
        console.print("[bold green]Configuration complete![/bold green]")
        console.print(f"Configuration saved to: {self._config_manager._config_path}")
        console.print()

    async def _configure_provider(self) -> None:
        """Configure provider step."""
        console.print("[bold]Step 1: Choose your AI provider[/bold]")
        console.print()

        table = Table(show_header=False, box=None)
        table.add_column("Option", style="cyan")
        table.add_column("Provider", style="bold")
        table.add_column("Type", style="dim")
        table.add_column("Status", style="dim")

        providers = [
            ("1", "Ollama (Local)", "local", "http://localhost:11434"),
            ("2", "LM Studio (Local)", "local", "http://localhost:1234/v1"),
            ("3", "OpenAI", "cloud", "api.openai.com"),
            ("4", "Anthropic Claude", "cloud", "api.anthropic.com"),
            ("5", "Coding Plan", "cloud", "api.codingplan.com"),
            ("6", "Azure OpenAI", "cloud", "azure"),
            ("7", "Google AI (Gemini)", "cloud", "generativelanguage.googleapis.com"),
            ("8", "Custom Provider", "custom", "custom base URL"),
            ("9", "Skip (configure later)", "", ""),
        ]

        for opt, name, ptype, _url in providers:
            status = ""

            if ptype == "local":
                status = "No API key needed"
            elif ptype == "cloud":
                status = "Requires API key"
            elif ptype == "custom":
                status = "Custom configuration"

            table.add_row(f"  [{opt}]", name, ptype, status)

        console.print(table)
        console.print()

        choice = Prompt.ask(
            "Select provider",
            choices=[str(i) for i in range(1, 10)],
            default="1",
        )

        provider_map = {
            "1": "ollama",
            "2": "lmstudio",
            "3": "openai",
            "4": "anthropic",
            "5": "coding_plan",
            "6": "azure_openai",
            "7": "google",
            "8": "custom",
        }

        if choice == "9":
            console.print("\n[yellow]You can configure later[/yellow]")
            return

        provider_name = provider_map[choice]

        await self._configure_provider_details(provider_name)

    async def _configure_provider_details(
        self,
        provider_name: str,
    ) -> None:
        """Configure provider details.

        Args:
            provider_name: Provider name
        """
        console.print(f"\n[bold]Configuring {provider_name}[/bold]")

        if provider_name in ["ollama", "lmstudio"]:
            base_url = Prompt.ask(
                "Base URL",
                default="http://localhost:11434"
                if provider_name == "ollama"
                else "http://localhost:1234/v1",
            )

            model = Prompt.ask(
                "Model name",
                default="llama2" if provider_name == "ollama" else "local-model",
            )

            await self._config_manager.configure_provider(
                provider_name=provider_name,
                base_url=base_url,
                model=model,
            )

        elif provider_name in ["openai", "anthropic", "coding_plan", "azure_openai", "google"]:
            api_key = Prompt.ask(
                "API key",
                password=True,
            )

            if provider_name == "coding_plan":
                console.print("[dim]You can add multiple Coding Plan API keys[/dim]")

                add_more = Confirm.ask("Add another Coding Plan key?", default=False)

                if add_more:
                    another_key = Prompt.ask("Another API key", password=True)

                    await self._config_manager.add_coding_plan_key(api_key, "coding_plan_1")
                    await self._config_manager.add_coding_plan_key(another_key, "coding_plan_2")
                else:
                    await self._config_manager.configure_provider(
                        provider_name=provider_name,
                        api_key=api_key,
                    )
            else:
                model = Prompt.ask(
                    "Model",
                    default="gpt-4" if provider_name == "openai" else "claude-3-5-sonnet-20241022",
                )

                await self._config_manager.configure_provider(
                    provider_name=provider_name,
                    api_key=api_key,
                    model=model,
                )

        elif provider_name == "custom":
            base_url = Prompt.ask("Base URL")
            api_key = Prompt.ask("API key (optional)", password=True, default="")
            model = Prompt.ask("Model name", default="default")

            await self._config_manager.configure_provider(
                provider_name="custom",
                base_url=base_url,
                api_key=api_key if api_key else None,
                model=model,
            )

        set_as_default = Confirm.ask(
            f"\nSet {provider_name} as default provider?",
            default=True,
        )

        if set_as_default:
            await self._config_manager.set_active_provider(provider_name)
            console.print(f"[green]✓[/green] Active provider: {provider_name}")

    async def _configure_settings(self) -> None:
        """Configure general settings."""
        console.print("\n[bold]Step 2: General settings[/bold]")

        max_agents = Prompt.ask(
            "Maximum concurrent agents",
            default="10",
        )

        await self._config_manager.update_settings(
            "max_concurrent_agents",
            int(max_agents),
        )

        evolution_enabled = Confirm.ask(
            "Enable skill self-evolution?",
            default=True,
        )

        await self._config_manager.update_settings(
            "evolution_enabled",
            evolution_enabled,
        )

        console.print("[green]✓[/green] Settings configured")
