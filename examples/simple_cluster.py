"""Example: Deploy a simple agent cluster."""

import asyncio
from pathlib import Path

from bagualu import BaGuaLuCore


async def main() -> None:
    """Deploy a simple agent cluster."""

    # Initialize BaGuaLu
    core = BaGuaLuCore(workspace=Path.home() / ".bagualu" / "workspace")

    await core.initialize()

    print("BaGuaLu initialized successfully!")

    # Deploy a single agent
    agent_id = await core.deploy_agent(
        name="my-executor",
        role="executor",
        provider="ollama",
        model="llama2",
        skills=["code-analysis"],
    )

    print(f"Deployed agent: {agent_id}")

    # Execute a task
    result = await core.cluster.execute_with_agent(
        agent_id=agent_id,
        instruction="Analyze the current directory structure",
        inputs={},
    )

    print(f"Result: {result}")

    # Get cluster status
    status = await core.cluster.get_cluster_status()
    print(f"Cluster status: {status}")


if __name__ == "__main__":
    asyncio.run(main())
