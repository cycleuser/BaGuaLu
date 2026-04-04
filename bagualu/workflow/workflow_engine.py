"""Workflow Engine - Workflow execution and management."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from datetime import datetime

from bagualu.workflow.workflow_dag import WorkflowDAG
from bagualu.utils.logging import Logger

logger = Logger.get_logger(__name__)


@dataclass
class WorkflowNode:
    """Workflow node representing an agent task."""

    id: str
    agent_role: str
    instruction: str
    inputs: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    priority: int = 5


@dataclass
class WorkflowEdge:
    """Workflow edge representing connection between nodes."""

    from_node: str
    to_node: str
    condition: Optional[str] = None


class WorkflowEngine:
    """Workflow engine for designing and executing workflows.

    Features:
    - Web-based drag-and-drop workflow design
    - DAG-based execution
    - Multi-agent orchestration
    - Parallel and sequential execution
    - Workflow versioning
    """

    def __init__(
        self,
        cluster: Any,
        skill_engine: Any,
    ) -> None:
        """Initialize workflow engine.

        Args:
            cluster: Agent cluster
            skill_engine: Skill engine
        """
        self._cluster = cluster
        self._skill_engine = skill_engine
        self._workflows: Dict[str, WorkflowDAG] = {}
        self._execution_history: List[Dict[str, Any]] = []

        logger.info("Workflow engine initialized")

    async def initialize(self) -> None:
        """Initialize workflow engine."""
        logger.info("Workflow engine ready")

    async def create(
        self,
        workflow_config: Dict[str, Any],
    ) -> str:
        """Create a workflow from configuration.

        Args:
            workflow_config: Workflow configuration

        Returns:
            Workflow ID
        """
        workflow_id = workflow_config.get("id", f"workflow-{datetime.now().timestamp()}")

        nodes = [
            WorkflowNode(
                id=node.get("id"),
                agent_role=node.get("role", "executor"),
                instruction=node.get("instruction", ""),
                inputs=node.get("inputs", {}),
                dependencies=node.get("dependencies", []),
                priority=node.get("priority", 5),
            )
            for node in workflow_config.get("nodes", [])
        ]

        edges = [
            WorkflowEdge(
                from_node=edge.get("from"),
                to_node=edge.get("to"),
                condition=edge.get("condition"),
            )
            for edge in workflow_config.get("edges", [])
        ]

        dag = WorkflowDAG(
            workflow_id=workflow_id,
            name=workflow_config.get("name", "unnamed"),
            nodes=nodes,
            edges=edges,
        )

        self._workflows[workflow_id] = dag

        logger.info(f"Created workflow: {workflow_id}")

        return workflow_id

    async def execute(
        self,
        workflow_id: str,
        inputs: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute a workflow.

        Args:
            workflow_id: Workflow ID
            inputs: Input data

        Returns:
            Execution results
        """
        workflow = self._workflows.get(workflow_id)

        if not workflow:
            return {
                "success": False,
                "error": f"Workflow {workflow_id} not found",
            }

        execution_id = f"exec-{datetime.now().timestamp()}"

        execution_record = {
            "id": execution_id,
            "workflow_id": workflow_id,
            "inputs": inputs,
            "start_time": datetime.now().isoformat(),
        }

        try:
            results = await self._execute_workflow(workflow, inputs)

            execution_record["success"] = True
            execution_record["results"] = results
            execution_record["end_time"] = datetime.now().isoformat()

            self._execution_history.append(execution_record)

            return results
        except Exception as e:
            execution_record["success"] = False
            execution_record["error"] = str(e)
            execution_record["end_time"] = datetime.now().isoformat()

            self._execution_history.append(execution_record)

            logger.error(f"Workflow {workflow_id} execution failed: {e}")

            return {
                "success": False,
                "error": str(e),
            }

    async def _execute_workflow(
        self,
        workflow: WorkflowDAG,
        inputs: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute workflow DAG.

        Args:
            workflow: Workflow DAG
            inputs: Input data

        Returns:
            Execution results
        """
        execution_order = workflow.compute_execution_order()

        results = {}

        for level_nodes in execution_order:
            level_results = await asyncio.gather(
                *[self._execute_node(node, inputs, results) for node in level_nodes],
                return_exceptions=True,
            )

            for node, result in zip(level_nodes, level_results):
                if isinstance(result, Exception):
                    results[node.id] = {
                        "success": False,
                        "error": str(result),
                    }
                else:
                    results[node.id] = result

        return {
            "success": True,
            "workflow": workflow.name,
            "node_results": results,
        }

    async def _execute_node(
        self,
        node: WorkflowNode,
        workflow_inputs: Dict[str, Any],
        previous_results: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute a workflow node.

        Args:
            node: Workflow node
            workflow_inputs: Workflow inputs
            previous_results: Previous node results

        Returns:
            Node execution result
        """
        node_inputs = {**workflow_inputs, **node.inputs}

        for dep_id in node.dependencies:
            if dep_id in previous_results:
                node_inputs[f"{dep_id}_output"] = previous_results[dep_id]

        agent_ids = await self._cluster.get_cluster_status()

        suitable_agents = [
            agent for agent in agent_ids.get("agents", []) if agent.get("role") == node.agent_role
        ]

        if not suitable_agents:
            suitable_agents = agent_ids.get("agents", [])

        if suitable_agents:
            agent_id = suitable_agents[0].get("id")

            result = await self._cluster.execute_with_agent(
                agent_id=agent_id,
                instruction=node.instruction,
                inputs=node_inputs,
            )

            return result

        return {
            "success": False,
            "error": "No suitable agent available",
        }

    async def get_workflow(
        self,
        workflow_id: str,
    ) -> Optional[WorkflowDAG]:
        """Get workflow by ID.

        Args:
            workflow_id: Workflow ID

        Returns:
            Workflow DAG
        """
        return self._workflows.get(workflow_id)

    async def list_workflows(self) -> List[Dict[str, Any]]:
        """List all workflows.

        Returns:
            List of workflow info
        """
        return [
            {
                "id": workflow.workflow_id,
                "name": workflow.name,
                "nodes": len(workflow.nodes),
                "edges": len(workflow.edges),
            }
            for workflow in self._workflows.values()
        ]
