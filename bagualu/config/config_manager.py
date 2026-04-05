"""Config Manager - Configuration loading and management."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

import yaml

from bagualu.config.providers import MultiProviderConfig, ProviderConfig
from bagualu.utils.logging import Logger

logger = Logger.get_logger(__name__)


class ConfigManager:
    """Configuration manager for multi-provider setup (inspired by OpenLaoKe).

    Features:
    - Multi-provider configuration (Ollama, LMStudio, OpenAI, Claude, etc.)
    - API key management and persistence
    - Coding Plan API key support
    - Configuration wizard
    - Auto-detection of existing configurations
    """

    def __init__(
        self,
        config_path: Path | None = None,
    ) -> None:
        """Initialize configuration manager.

        Args:
            config_path: Path to configuration file
        """
        self._config_path = config_path or Path.home() / ".bagualu" / "config.yaml"
        self._providers = MultiProviderConfig()
        self._settings: dict[str, Any] = {}
        self._loaded = False

        logger.info(f"Config manager initialized (path: {self._config_path})")

    async def load(self) -> None:
        """Load configuration from file."""
        if self._loaded:
            return

        if self._config_path.exists():
            await self._load_from_file()
        else:
            await self._create_default_config()

        self._loaded = True
        logger.info("Configuration loaded")

    async def _load_from_file(self) -> None:
        """Load configuration from YAML file."""
        try:
            content = await asyncio.to_thread(self._config_path.read_text)

            config_data = yaml.safe_load(content)

            if config_data:
                providers_data = config_data.get("providers", {})

                for provider_name, provider_config in providers_data.items():
                    provider = ProviderConfig(
                        name=provider_name,
                        api_key=provider_config.get("api_key"),
                        base_url=provider_config.get("base_url"),
                        model=provider_config.get("model"),
                        enabled=provider_config.get("enabled", True),
                    )

                    self._providers.add_provider(provider)

                self._settings = config_data.get("settings", {})

                self._providers.active_provider = config_data.get("active_provider", "ollama")

                logger.info(f"Loaded configuration from {self._config_path}")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            await self._create_default_config()

    async def _create_default_config(self) -> None:
        """Create default configuration."""
        default_providers = [
            ProviderConfig(
                name="ollama",
                base_url="http://localhost:11434",
                model="llama2",
                enabled=True,
            ),
            ProviderConfig(
                name="lmstudio",
                base_url="http://localhost:1234/v1",
                model="local-model",
                enabled=True,
            ),
            ProviderConfig(
                name="openai",
                api_key=None,
                base_url="https://api.openai.com/v1",
                model="gpt-4",
                enabled=False,
            ),
            ProviderConfig(
                name="anthropic",
                api_key=None,
                base_url="https://api.anthropic.com",
                model="claude-3-5-sonnet-20241022",
                enabled=False,
            ),
            ProviderConfig(
                name="coding_plan",
                api_key=None,
                base_url="https://api.codingplan.com/v1",
                model="default",
                enabled=False,
            ),
        ]

        for provider in default_providers:
            self._providers.add_provider(provider)

        self._providers.active_provider = "ollama"

        self._settings = {
            "max_concurrent_agents": 10,
            "default_agent_role": "executor",
            "skill_dirs": [],
            "evolution_enabled": True,
            "quality_threshold": 0.8,
        }

        await self.save()

        logger.info("Created default configuration")

    async def save(self) -> None:
        """Save configuration to file."""
        self._config_path.parent.mkdir(parents=True, exist_ok=True)

        config_data: dict[str, Any] = {
            "providers": {},
            "active_provider": self._providers.active_provider,
            "settings": self._settings,
        }

        for provider_name, provider in self._providers.providers.items():
            providers_dict = config_data["providers"]
            if isinstance(providers_dict, dict):
                providers_dict[provider_name] = {
                    "api_key": provider.api_key,
                    "base_url": provider.base_url,
                    "model": provider.model,
                    "enabled": provider.enabled,
                }

        content = yaml.dump(config_data, default_flow_style=False)

        await asyncio.to_thread(self._config_path.write_text, content)

        logger.info(f"Saved configuration to {self._config_path}")

    async def configure_provider(
        self,
        provider_name: str,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
    ) -> None:
        """Configure a specific provider.

        Args:
            provider_name: Provider name
            api_key: API key (optional)
            base_url: Base URL (optional)
            model: Model identifier (optional)
        """
        provider = self._providers.get_provider(provider_name)

        if provider:
            if api_key:
                provider.api_key = api_key

            if base_url:
                provider.base_url = base_url

            if model:
                provider.model = model

            provider.enabled = True
        else:
            new_provider = ProviderConfig(
                name=provider_name,
                api_key=api_key,
                base_url=base_url,
                model=model,
                enabled=True,
            )

            self._providers.add_provider(new_provider)

        await self.save()

        logger.info(f"Configured provider: {provider_name}")

    async def set_active_provider(
        self,
        provider_name: str,
    ) -> None:
        """Set active provider.

        Args:
            provider_name: Provider name
        """
        if provider_name in self._providers.providers:
            self._providers.active_provider = provider_name
            await self.save()
            logger.info(f"Active provider set to: {provider_name}")
        else:
            logger.warning(f"Provider {provider_name} not found")

    async def get_active_provider_config(self) -> ProviderConfig | None:
        """Get active provider configuration.

        Returns:
            Active provider config
        """
        return self._providers.get_active_provider()

    async def get_provider_config(
        self,
        provider_name: str,
    ) -> ProviderConfig | None:
        """Get specific provider configuration.

        Args:
            provider_name: Provider name

        Returns:
            Provider config
        """
        return self._providers.get_provider(provider_name)

    async def list_providers(self) -> list[str]:
        """List all configured providers.

        Returns:
            List of provider names
        """
        return list(self._providers.providers.keys())

    async def update_settings(
        self,
        key: str,
        value: Any,
    ) -> None:
        """Update a setting.

        Args:
            key: Setting key
            value: Setting value
        """
        self._settings[key] = value
        await self.save()
        logger.info(f"Updated setting: {key}")

    async def get_setting(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """Get a setting.

        Args:
            key: Setting key
            default: Default value

        Returns:
            Setting value
        """
        return self._settings.get(key, default)

    async def add_coding_plan_key(
        self,
        api_key: str,
        provider_name: str | None = None,
    ) -> None:
        """Add Coding Plan API key (multiple keys support).

        Args:
            api_key: Coding Plan API key
            provider_name: Provider name (optional)
        """
        provider = provider_name or "coding_plan"

        await self.configure_provider(
            provider_name=provider,
            api_key=api_key,
        )

        logger.info(f"Added Coding Plan API key for provider: {provider}")

    async def get_all_coding_plan_keys(self) -> list[str]:
        """Get all Coding Plan API keys.

        Returns:
            List of API keys
        """
        keys = []

        for provider_name, provider in self._providers.providers.items():
            if (
                "coding" in provider_name.lower() or "plan" in provider_name.lower()
            ) and provider.api_key:
                keys.append(provider.api_key)

        return keys

    @property
    def providers(self) -> MultiProviderConfig:
        """Get providers configuration."""
        return self._providers

    @property
    def settings(self) -> dict[str, Any]:
        """Get settings."""
        return self._settings
