"""Built-in workflow nodes - Comprehensive node library."""

from __future__ import annotations

import json
from typing import Any

from bagualu.workflow.nodes.base import (
    BaseNode,
    NodeDefinition,
    NodeInput,
    NodeOutput,
    NodeExecutionContext,
)


def prop(type_str: str, default_val: Any = None, **kwargs) -> dict:
    """Helper to create property definitions."""
    result = {"type": type_str}
    if default_val is not None:
        result["default"] = default_val
    result.update(kwargs)
    return result


class TextInputNode(BaseNode):
    """Simple text input node."""
    definition = NodeDefinition(
        type="input.text", category="Input", title="Text Input",
        description="Simple text input", inputs=[],
        outputs=[NodeOutput(name="text", type="string")],
        properties={"default_value": prop("string", "")}
    )
    async def execute(self, context): return {"text": self.get_property("default_value", "")}


class JSONInputNode(BaseNode):
    """JSON input node."""
    definition = NodeDefinition(
        type="input.json", category="Input", title="JSON Input",
        description="Parse JSON",
        inputs=[NodeInput(name="json_string", type="string", required=False)],
        outputs=[NodeOutput(name="data", type="object")],
        properties={"default_json": prop("string", "{}")}
    )
    async def execute(self, context):
        try:
            return {"data": json.loads(self.get_input("json_string") or self.get_property("default_json", "{}"))}
        except Exception as e:
            return {"data": {}, "error": str(e)}


class ConditionNode(BaseNode):
    """Conditional branching."""
    definition = NodeDefinition(
        type="logic.condition", category="Logic", title="Condition",
        description="Route based on conditions",
        inputs=[NodeInput(name="value", type="any", required=True)],
        outputs=[NodeOutput(name="true", type="any"), NodeOutput(name="false", type="any")],
        properties={"operator": prop("string", "equals"), "compare_value": prop("any", "")}
    )
    async def execute(self, context):
        value = self.get_input("value")
        compare = self.get_property("compare_value", "")
        met = value == compare
        return {"true" if met else "false": value, "met": met}


class MergeNode(BaseNode):
    """Merge inputs."""
    definition = NodeDefinition(
        type="logic.merge", category="Logic", title="Merge",
        inputs=[NodeInput(name="in", type="any", required=True)],
        outputs=[NodeOutput(name="merged", type="array")],
        properties={"mode": prop("string", "array")}
    )
    async def execute(self, context): return {"merged": [self.get_input("in")]}


class HTTPRequestNode(BaseNode):
    """HTTP requests."""
    definition = NodeDefinition(
        type="api.http", category="API", title="HTTP Request",
        inputs=[NodeInput(name="url", type="string", required=True)],
        outputs=[NodeOutput(name="response", type="object"), NodeOutput(name="status", type="number")],
        properties={"method": prop("string", "GET"), "timeout": prop("number", 30)}
    )
    async def execute(self, context):
        import httpx
        try:
            async with httpx.AsyncClient() as client:
                r = await client.request(self.get_property("method", "GET"), self.get_input("url", ""), timeout=self.get_property("timeout", 30))
                return {"response": r.json() if r.content else {}, "status": r.status_code}
        except Exception as e:
            return {"response": {}, "status": 0, "error": str(e)}


def register_builtin_nodes(registry):
    for cls in [TextInputNode, JSONInputNode, ConditionNode, MergeNode, HTTPRequestNode]:
        registry.register_node(cls)
