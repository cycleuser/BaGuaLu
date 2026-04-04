"""Provider Configuration - Multi-provider setup."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional

from bagualu.utils.logging import Logger

logger = Logger.get_logger(__name__)


class ProviderType(str, Enum):
    """Provider types."""

    LOCAL = "local"
    CLOUD = "cloud"
    CUSTOM = "custom"


@dataclass
class ProviderConfig:
    """Provider configuration."""

    name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = None
    enabled: bool = True
    provider_type: ProviderType = ProviderType.CLOUD
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_ready(self) -> bool:
        """Check if provider is ready to use."""
        if not self.enabled:
            return False

        if self.provider_type == ProviderType.LOCAL:
            return self.base_url is not None

        return self.api_key is not None or self.base_url is not None

    def get_status_message(self) -> str:
        """Get provider status message."""
        if self.enabled and self.is_ready():
            return "Ready"

        if not self.enabled:
            return "Disabled"

        if self.provider_type == ProviderType.LOCAL:
            if not self.base_url:
                return "Missing base URL"

        if self.provider_type == ProviderType.CLOUD:
            if not self.api_key:
                return "Missing API key"

        return "Not configured"


class MultiProviderConfig:
    """Multi-provider configuration manager."""

    def __init__(self) -> None:
        """Initialize multi-provider config."""
        self._providers: Dict[str, ProviderConfig] = {}
        self._active_provider: Optional[str] = None

    def add_provider(
        self,
        provider: ProviderConfig,
    ) -> None:
        """Add a provider.

        Args:
            provider: Provider configuration
        """
        self._providers[provider.name] = provider
        logger.info(f"Added provider: {provider.name}")

    def get_provider(
        self,
        name: str,
    ) -> Optional[ProviderConfig]:
        """Get provider by name.

        Args:
            name: Provider name

        Returns:
            Provider configuration
        """
        return self._providers.get(name)

    def get_active_provider(self) -> Optional[ProviderConfig]:
        """Get active provider.

        Returns:
            Active provider configuration
        """
        if self._active_provider:
            return self._providers.get(self._active_provider)

        for provider in self._providers.values():
            if provider.is_ready():
                return provider

        return None

    def set_active_provider(
        self,
        name: str,
    ) -> bool:
        """Set active provider.

        Args:
            name: Provider name

        Returns:
            True if provider exists
        """
        if name in self._providers:
            self._active_provider = name
            return True

        return False

    def get_active_model(self) -> Optional[str]:
        """Get active provider's model.

        Returns:
            Model identifier
        """
        provider = self.get_active_provider()

        if provider:
            return provider.model

        return None

    def list_providers(self) -> Dict[str, ProviderConfig]:
        """List all providers.

        Returns:
            Dictionary of providers
        """
        return self._providers

    def list_ready_providers(self) -> List[str]:
        """List ready providers.

        Returns:
            List of ready provider names
        """
        return [name for name, provider in self._providers.items() if provider.is_ready()]

    def remove_provider(
        self,
        name: str,
    ) -> bool:
        """Remove a provider.

        Args:
            name: Provider name

        Returns:
            True if provider was removed
        """
        if name in self._providers:
            self._providers.pop(name)

            if self._active_provider == name:
                self._active_provider = None

            return True

        return False

    @property
    def providers(self) -> Dict[str, ProviderConfig]:
        """Get all providers."""
        return self._providers

    @property
    def active_provider(self) -> Optional[str]:
        """Get active provider name."""
        return self._active_provider

    @active_provider.setter
    def active_provider(self, value: str) -> None:
        """Set active provider name."""
        self._active_provider = value
