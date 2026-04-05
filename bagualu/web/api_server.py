"""API Server - REST API for workflow management."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

from bagualu.utils.logging import Logger

logger = Logger.get_logger(__name__)


app = FastAPI(title="BaGuaLu API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class WorkflowConfig(BaseModel):
    """Workflow configuration model."""

    name: str
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    inputs: Optional[Dict[str, Any]] = None


class AgentConfig(BaseModel):
    """Agent configuration model."""

    name: str
    role: str
    provider: Optional[str] = None
    model: Optional[str] = None
    skills: Optional[List[str]] = None


class APIServer:
    """REST API server for BaGuaLu.

    Endpoints:
    - Workflows: create, execute, list
    - Agents: deploy, terminate, status
    - Skills: load, evolve, search
    - Cluster: status, scale
    """

    def __init__(
        self,
        core: Any,
    ) -> None:
        """Initialize API server.

        Args:
            core: BaGuaLu core instance
        """
        self._core = core
        self._setup_routes()

        logger.info("API server initialized")

    def _setup_routes(self) -> None:
        """Setup API routes."""

        @app.get("/")
        async def root():
            return {"message": "BaGuaLu API", "version": "0.1.0"}

        @app.post("/workflows")
        async def create_workflow(config: WorkflowConfig):
            workflow_id = await self._core.create_workflow(config.dict())
            return {"workflow_id": workflow_id}

        @app.post("/workflows/{workflow_id}/execute")
        async def execute_workflow(workflow_id: str, inputs: Dict[str, Any]):
            result = await self._core.execute_workflow(workflow_id, inputs)
            return result

        @app.get("/workflows")
        async def list_workflows():
            workflows = await self._core.workflow.list_workflows()
            return {"workflows": workflows}

        @app.post("/agents")
        async def deploy_agent(config: AgentConfig):
            agent_id = await self._core.deploy_agent(
                name=config.name,
                role=config.role,
                provider=config.provider,
                model=config.model,
                skills=config.skills,
            )
            return {"agent_id": agent_id}

        @app.get("/agents")
        async def list_agents():
            status = await self._core.cluster.get_cluster_status()
            return status

        @app.get("/skills")
        async def list_skills():
            skills = await self._core.skills.get_all_skills()
            return {"skills": skills}

        @app.post("/skills/{skill_name}/evolve")
        async def evolve_skill(skill_name: str):
            evolved = await self._core.evolve_skill(skill_name)
            return {"evolved": evolved}

    def run_server(
        self,
        host: str = "0.0.0.0",
        port: int = 8000,
    ) -> None:
        """Run API server (synchronous).

        Args:
            host: Host address
            port: Port number
        """
        import uvicorn

        logger.info(f"Starting API server on {host}:{port}")

        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info",
        )
