"""Base Node - Abstract base class for all workflow nodes.

Inspired by ComfyUI and n8n node architecture.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class NodeInput:
    """Node input definition."""

    name: str
    type: str  # string, number, boolean, object, array, any
    required: bool = True
    default: Any = None
    description: str = ""
    options: list[str] | None = None  # For select type
    min_value: float | None = None  # For number type
    max_value: float | None = None  # For number type


@dataclass
class NodeOutput:
    """Node output definition."""

    name: str
    type: str
    description: str = ""


@dataclass
class NodeCategory:
    """Node category for organization."""

    name: str
    icon: str
    color: str


@dataclass
class NodeDefinition:
    """Complete node definition."""

    type: str
    category: str
    title: str
    description: str
    inputs: list[NodeInput] = field(default_factory=list)
    outputs: list[NodeOutput] = field(default_factory=list)
    properties: dict[str, Any] = field(default_factory=dict)


class BaseNode(ABC):
    """Base class for all workflow nodes.

    Features:
    - Typed inputs/outputs
    - Dynamic properties
    - Validation
    - Execution context
    """

    # Class-level definition
    definition: NodeDefinition = None

    # Instance state
    id: str = ""
    properties: dict[str, Any] = field(default_factory=dict)
    inputs_data: dict[str, Any] = field(default_factory=dict)
    outputs_data: dict[str, Any] = field(default_factory=dict)

    @abstractmethod
    async def execute(self, context: NodeExecutionContext) -> dict[str, Any]:
        """Execute the node logic.

        Args:
            context: Execution context with inputs and runtime data

        Returns:
            Dictionary of output values
        """
        pass

    def validate_input(self, name: str, value: Any) -> tuple[bool, str | None]:
        """Validate an input value.

        Args:
            name: Input name
            value: Value to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        input_def = None
        for inp in self.definition.inputs:
            if inp.name == name:
                input_def = inp
                break

        if not input_def:
            return False, f"Unknown input: {name}"

        if input_def.required and value is None:
            return False, f"Required input missing: {name}"

        if value is None:
            return True, None

        # Type validation
        if input_def.type != "any":
            type_validators = {
                "string": lambda v: isinstance(v, str),
                "number": lambda v: isinstance(v, (int, float)),
                "boolean": lambda v: isinstance(v, bool),
                "object": lambda v: isinstance(v, dict),
                "array": lambda v: isinstance(v, list),
            }

            validator = type_validators.get(input_def.type)
            if validator and not validator(value):
                return False, f"Invalid type for {name}: expected {input_def.type}"

        # Range validation for numbers
        if input_def.type == "number" and isinstance(value, (int, float)):
            if input_def.min_value is not None and value < input_def.min_value:
                return False, f"Value {value} below minimum {input_def.min_value}"
            if input_def.max_value is not None and value > input_def.max_value:
                return False, f"Value {value} above maximum {input_def.max_value}"

        # Options validation for select
        if input_def.options and value not in input_def.options:
            return False, f"Value {value} not in allowed options: {input_def.options}"

        return True, None

    def get_property(self, name: str, default: Any = None) -> Any:
        """Get a node property."""
        return self.properties.get(name, default)

    def set_property(self, name: str, value: Any) -> None:
        """Set a node property."""
        self.properties[name] = value

    def get_input(self, name: str, default: Any = None) -> Any:
        """Get an input value."""
        return self.inputs_data.get(name, default)

    def set_output(self, name: str, value: Any) -> None:
        """Set an output value."""
        self.outputs_data[name] = value

    def to_dict(self) -> dict[str, Any]:
        """Serialize node to dictionary."""
        return {
            "id": self.id,
            "type": self.definition.type,
            "category": self.definition.category,
            "title": self.definition.title,
            "properties": self.properties,
            "inputs": [inp.name for inp in self.definition.inputs],
            "outputs": [out.name for out in self.definition.outputs],
        }


@dataclass
class NodeExecutionContext:
    """Context for node execution."""

    node_id: str
    workflow_id: str
    inputs: dict[str, Any]
    global_context: dict[str, Any] = field(default_factory=dict)
    previous_outputs: dict[str, dict[str, Any]] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


class NodeRegistry:
    """Registry for managing node types."""

    _instance: NodeRegistry = None
    _nodes: dict[str, type[BaseNode]] = {}
    _categories: dict[str, NodeCategory] = {}

    def __new__(cls) -> NodeRegistry:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def register_category(self, category: NodeCategory) -> None:
        """Register a node category."""
        self._categories[category.name] = category

    def register_node(self, node_class: type[BaseNode]) -> None:
        """Register a node type."""
        if node_class.definition:
            self._nodes[node_class.definition.type] = node_class

            # Auto-register category if not exists
            cat_name = node_class.definition.category
            if cat_name not in self._categories:
                self.register_category(NodeCategory(name=cat_name, icon="📦", color="#667eea"))

    def get_node(self, node_type: str) -> type[BaseNode] | None:
        """Get a node class by type."""
        return self._nodes.get(node_type)

    def list_nodes(self) -> list[dict[str, Any]]:
        """List all registered nodes."""
        return [
            {
                "type": node_class.definition.type,
                "category": node_class.definition.category,
                "title": node_class.definition.title,
                "description": node_class.definition.description,
                "inputs": [
                    {
                        "name": inp.name,
                        "type": inp.type,
                        "required": inp.required,
                        "default": inp.default,
                        "description": inp.description,
                        "options": inp.options,
                    }
                    for inp in node_class.definition.inputs
                ],
                "outputs": [
                    {
                        "name": out.name,
                        "type": out.type,
                        "description": out.description,
                    }
                    for out in node_class.definition.outputs
                ],
            }
            for node_class in self._nodes.values()
        ]

    def list_categories(self) -> list[dict[str, Any]]:
        """List all categories."""
        return [
            {"name": cat.name, "icon": cat.icon, "color": cat.color}
            for cat in self._categories.values()
        ]

    def create_node(self, node_type: str, node_id: str) -> BaseNode | None:
        """Create a node instance."""
        node_class = self.get_node(node_type)
        if not node_class:
            return None

        node = node_class()
        node.id = node_id
        return node


# Global registry instance
def get_node_registry() -> NodeRegistry:
    """Get the global node registry."""
    return NodeRegistry()
