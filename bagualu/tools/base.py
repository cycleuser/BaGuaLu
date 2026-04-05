"""Base Tool - Tool abstraction (inspired by OpenHarness)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel

from bagualu.utils.logging import Logger

logger = Logger.get_logger(__name__)


@dataclass
class ToolResult:
    """Tool execution result."""

    output: Any
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_success(self) -> bool:
        """Check if execution succeeded."""
        return self.error is None


@dataclass
class ToolExecutionContext:
    """Tool execution context."""

    agent_id: str
    session_id: str
    workspace: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseTool(ABC):
    """Base tool abstraction (inspired by OpenHarness).

    Features:
    - Pydantic input validation
    - Self-describing JSON Schema
    - Permission integration
    - Hook support
    """

    name: str = "base_tool"
    description: str = "Base tool"
    input_model: type[BaseModel] | None = None

    @abstractmethod
    async def execute(
        self,
        arguments: dict[str, Any],
        context: ToolExecutionContext,
    ) -> ToolResult:
        """Execute the tool.

        Args:
            arguments: Tool arguments
            context: Execution context

        Returns:
            Tool result
        """
        pass

    def validate_input(
        self,
        arguments: dict[str, Any],
    ) -> BaseModel | None:
        """Validate input using Pydantic model.

        Args:
            arguments: Input arguments

        Returns:
            Validated model or None
        """
        if not self.input_model:
            return None

        try:
            return self.input_model(**arguments)
        except Exception as e:
            logger.error(f"Input validation failed for {self.name}: {e}")
            return None

    def get_schema(self) -> dict[str, Any]:
        """Get tool JSON schema.

        Returns:
            JSON schema dictionary
        """
        schema = {
            "name": self.name,
            "description": self.description,
        }

        if self.input_model:
            schema["input_schema"] = self.input_model.model_json_schema()

        return schema


class ToolRegistry:
    """Tool registry for managing tools (inspired by OpenHarness)."""

    def __init__(self) -> None:
        """Initialize tool registry."""
        self._tools: dict[str, BaseTool] = {}

    def register(
        self,
        tool: BaseTool,
    ) -> None:
        """Register a tool.

        Args:
            tool: Tool instance
        """
        self._tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")

    def unregister(
        self,
        tool_name: str,
    ) -> bool:
        """Unregister a tool.

        Args:
            tool_name: Tool name

        Returns:
            True if tool was unregistered
        """
        if tool_name in self._tools:
            self._tools.pop(tool_name)
            return True
        return False

    def get_tool(
        self,
        tool_name: str,
    ) -> BaseTool | None:
        """Get tool by name.

        Args:
            tool_name: Tool name

        Returns:
            Tool instance
        """
        return self._tools.get(tool_name)

    def list_tools(self) -> list[str]:
        """List all registered tools.

        Returns:
            List of tool names
        """
        return list(self._tools.keys())

    def get_all_schemas(self) -> list[dict[str, Any]]:
        """Get all tool schemas.

        Returns:
            List of tool schemas
        """
        return [tool.get_schema() for tool in self._tools.values()]

    async def execute_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        context: ToolExecutionContext,
    ) -> ToolResult:
        """Execute a tool.

        Args:
            tool_name: Tool name
            arguments: Tool arguments
            context: Execution context

        Returns:
            Tool result
        """
        tool = self._tools.get(tool_name)

        if not tool:
            return ToolResult(
                output=None,
                error=f"Tool not found: {tool_name}",
            )

        validated_input = tool.validate_input(arguments)

        if tool.input_model and not validated_input:
            return ToolResult(
                output=None,
                error=f"Invalid input for tool: {tool_name}",
            )

        try:
            result = await tool.execute(arguments, context)
            logger.info(f"Tool {tool_name} executed successfully")
            return result
        except Exception as e:
            logger.error(f"Tool {tool_name} execution failed: {e}")
            return ToolResult(
                output=None,
                error=str(e),
            )
