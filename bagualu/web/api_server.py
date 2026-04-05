"""API Server - REST API for workflow management."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from bagualu.utils.logging import Logger
from bagualu.web.web_ui import get_web_ui_html

logger = Logger.get_logger(__name__)


app = FastAPI(
    title="BaGuaLu API", version="0.1.0", description="Intelligent Agent Orchestration Platform"
)

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
    nodes: list[dict[str, Any]]
    edges: list[dict[str, Any]]
    inputs: dict[str, Any] | None = None


class AgentConfig(BaseModel):
    """Agent configuration model."""

    name: str
    role: str
    provider: str | None = None
    model: str | None = None
    skills: list[str] | None = None


class SkillConfig(BaseModel):
    """Skill configuration model."""

    name: str
    skill_path: str | None = None
    definition: dict[str, Any] | None = None


_core_instance: Any = None


def set_core_instance(core: Any) -> None:
    """Set the core instance for route handlers."""
    global _core_instance
    _core_instance = core


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint - Web UI."""
    return get_web_ui_html()


@app.get("/api")
async def api_info():
    """API info endpoint."""
    return {
        "message": "BaGuaLu API",
        "version": "0.1.0",
        "docs": "/docs",
        "openapi": "/openapi.json",
    }


@app.get("/models", response_model=dict[str, Any])
async def list_models():
    """List available models."""
    global _core_instance
    models = []

    if _core_instance:
        provider_config = await _core_instance.config.get_active_provider_config()
        if provider_config:
            models.append(
                {
                    "id": provider_config.model or "default",
                    "object": "model",
                    "owned_by": provider_config.name,
                }
            )

    return {"object": "list", "data": models}


@app.get("/v1/models", response_model=dict[str, Any])
async def list_models_v1():
    """List available models (OpenAI compatible)."""
    global _core_instance
    models = []

    if _core_instance:
        provider_config = await _core_instance.config.get_active_provider_config()
        if provider_config and provider_config.model:
            models.append(
                {
                    "id": provider_config.model,
                    "object": "model",
                    "created": 1700000000,
                    "owned_by": provider_config.name,
                }
            )

        for provider_name, provider in _core_instance.config.providers.providers.items():
            if (
                provider.model
                and provider.enabled
                and provider.model not in [m["id"] for m in models]
            ):
                models.append(
                    {
                        "id": provider.model,
                        "object": "model",
                        "created": 1700000000,
                        "owned_by": provider_name,
                    }
                )

    return {"object": "list", "data": models}


@app.post("/workflows")
async def create_workflow(config: WorkflowConfig):
    """Create a new workflow."""
    global _core_instance
    if not _core_instance:
        raise HTTPException(status_code=500, detail="Core not initialized")
    workflow_id = await _core_instance.create_workflow(config.model_dump())
    return {"workflow_id": workflow_id}


@app.post("/workflows/{workflow_id}/execute")
async def execute_workflow(workflow_id: str, inputs: dict[str, Any]):
    """Execute a workflow."""
    global _core_instance
    if not _core_instance:
        raise HTTPException(status_code=500, detail="Core not initialized")
    result = await _core_instance.execute_workflow(workflow_id, inputs)
    return result


@app.get("/workflows")
async def list_workflows():
    """List all workflows."""
    global _core_instance
    if not _core_instance:
        raise HTTPException(status_code=500, detail="Core not initialized")
    workflows = await _core_instance.workflow.list_workflows()
    return {"workflows": workflows}


@app.post("/agents")
async def deploy_agent(config: AgentConfig):
    """Deploy a new agent."""
    global _core_instance
    if not _core_instance:
        raise HTTPException(status_code=500, detail="Core not initialized")
    agent_id = await _core_instance.deploy_agent(
        name=config.name,
        role=config.role,
        provider=config.provider,
        model=config.model,
        skills=config.skills,
    )
    return {"agent_id": agent_id}


@app.get("/agents")
async def list_agents():
    """List all agents."""
    global _core_instance
    if not _core_instance:
        raise HTTPException(status_code=500, detail="Core not initialized")
    status = await _core_instance.cluster.get_cluster_status()
    return status


@app.delete("/agents/{agent_id}")
async def terminate_agent(agent_id: str):
    """Terminate an agent."""
    global _core_instance
    if not _core_instance:
        raise HTTPException(status_code=500, detail="Core not initialized")
    success = await _core_instance.cluster.terminate_agent(agent_id)
    if not success:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"success": True, "agent_id": agent_id}


@app.post("/skills")
async def load_skill(config: SkillConfig):
    """Load a skill."""
    global _core_instance
    if not _core_instance:
        raise HTTPException(status_code=500, detail="Core not initialized")

    if config.skill_path:
        skill_def = await _core_instance.skills.load_skill(config.skill_path)
        if not skill_def:
            raise HTTPException(status_code=400, detail="Failed to load skill from path")
        return {"skill": skill_def, "name": config.name}
    elif config.definition:
        skill_id = await _core_instance.skills._store.register_skill(config.definition)
        _core_instance.skills._skill_cache[config.name] = config.definition
        return {"skill_id": skill_id, "name": config.name}
    else:
        raise HTTPException(status_code=400, detail="Either skill_path or definition required")


@app.get("/skills")
async def list_skills():
    """List all skills."""
    global _core_instance
    if not _core_instance:
        raise HTTPException(status_code=500, detail="Core not initialized")
    skills = await _core_instance.skills.get_all_skills()
    return {"skills": skills}


@app.post("/skills/{skill_name}/evolve")
async def evolve_skill(skill_name: str):
    """Evolve a skill."""
    global _core_instance
    if not _core_instance:
        raise HTTPException(status_code=500, detail="Core not initialized")
    evolved = await _core_instance.evolve_skill(skill_name)
    return {"evolved": evolved}


@app.get("/ui", response_class=HTMLResponse)
async def web_ui():
    """Get web UI."""
    return get_web_ui_html()


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
        set_core_instance(core)

        logger.info("API server initialized")

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
