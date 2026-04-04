"""Workflow DAG - Directed Acyclic Graph for workflows."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from bagualu.utils.logging import Logger

logger = Logger.get_logger(__name__)


@dataclass
class WorkflowNode:
    """Workflow node."""

    id: str
    agent_role: str
    instruction: str
    inputs: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    priority: int = 5


@dataclass
class WorkflowEdge:
    """Workflow edge."""

    from_node: str
    to_node: str
    condition: Optional[str] = None


class WorkflowDAG:
    """Workflow DAG structure."""

    def __init__(
        self,
        workflow_id: str,
        name: str,
        nodes: List[WorkflowNode],
        edges: List[WorkflowEdge],
    ) -> None:
        """Initialize workflow DAG.

        Args:
            workflow_id: Workflow ID
            name: Workflow name
            nodes: List of nodes
            edges: List of edges
        """
        self.workflow_id = workflow_id
        self.name = name
        self.nodes = nodes
        self.edges = edges

        self._node_map: Dict[str, WorkflowNode] = {node.id: node for node in nodes}

        self._dependency_map: Dict[str, Set[str]] = {}

        for node in nodes:
            self._dependency_map[node.id] = set(node.dependencies)

        logger.info(f"Workflow DAG created: {name} ({len(nodes)} nodes)")

    def compute_execution_order(self) -> List[List[WorkflowNode]]:
        """Compute execution order (parallelizable levels).

        Returns:
            List of execution levels
        """
        levels = []
        remaining_nodes = set(self.nodes)
        completed_nodes = set()

        while remaining_nodes:
            ready_nodes = [
                node
                for node in remaining_nodes
                if self._dependency_map.get(node.id, set()).issubset(
                    {n.id for n in completed_nodes}
                )
            ]

            if not ready_nodes:
                logger.warning("Circular dependency detected")
                break

            levels.append(ready_nodes)

            completed_nodes.update(ready_nodes)
            remaining_nodes -= set(ready_nodes)

        return levels

    def get_node(
        self,
        node_id: str,
    ) -> Optional[WorkflowNode]:
        """Get node by ID.

        Args:
            node_id: Node ID

        Returns:
            Workflow node
        """
        return self._node_map.get(node_id)

    def get_dependencies(
        self,
        node_id: str,
    ) -> Set[str]:
        """Get node dependencies.

        Args:
            node_id: Node ID

        Returns:
            Set of dependency node IDs
        """
        return self._dependency_map.get(node_id, set())

    def validate(self) -> Dict[str, Any]:
        """Validate workflow DAG.

        Returns:
            Validation result
        """
        issues = []

        for node in self.nodes:
            if not node.id:
                issues.append(f"Node missing ID")

            if not node.instruction:
                issues.append(f"Node {node.id} missing instruction")

            for dep_id in node.dependencies:
                if dep_id not in self._node_map:
                    issues.append(f"Node {node.id} has invalid dependency: {dep_id}")

        execution_order = self.compute_execution_order()

        if len(execution_order) != len(self.nodes):
            issues.append("Circular dependency detected")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            "id": self.workflow_id,
            "name": self.name,
            "nodes": [
                {
                    "id": node.id,
                    "role": node.agent_role,
                    "instruction": node.instruction,
                    "inputs": node.inputs,
                    "dependencies": node.dependencies,
                    "priority": node.priority,
                }
                for node in self.nodes
            ],
            "edges": [
                {
                    "from": edge.from_node,
                    "to": edge.to_node,
                    "condition": edge.condition,
                }
                for edge in self.edges
            ],
        }
