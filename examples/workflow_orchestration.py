"""Example: Workflow orchestration."""

import asyncio
import json
from pathlib import Path

from bagualu import BaGuaLuCore


async def main() -> None:
    """Execute a multi-step workflow."""

    # Initialize
    core = BaGuaLuCore()
    await core.initialize()

    # Define workflow
    workflow_config = {
        "name": "code-review-workflow",
        "nodes": [
            {
                "id": "analyze",
                "role": "executor",
                "instruction": "Analyze codebase structure and identify main components",
            },
            {
                "id": "review",
                "role": "supervisor",
                "instruction": "Review the analysis and identify potential improvements",
                "dependencies": ["analyze"],
            },
            {
                "id": "report",
                "role": "executor",
                "instruction": "Generate a comprehensive report with recommendations",
                "dependencies": ["review"],
            },
        ],
        "edges": [
            {"from": "analyze", "to": "review"},
            {"from": "review", "to": "report"},
        ],
    }

    # Create workflow
    workflow_id = await core.create_workflow(workflow_config)
    print(f"Created workflow: {workflow_id}")

    # Execute workflow
    result = await core.execute_workflow(
        workflow_id,
        inputs={
            "target_directory": str(Path.cwd()),
            "analysis_depth": "deep",
        },
    )

    print("Workflow result:")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
