"""Example: Complete comprehensive example.

This example demonstrates a full workflow:
1. Initialize BaGuaLu with multi-provider configuration
2. Discover and install skills
3. Deploy a multi-role agent cluster
4. Create and execute workflows
5. Use tools and skill evolution
6. Monitor and manage the system
"""

import asyncio
import json
from pathlib import Path

from bagualu import BaGuaLuCore


async def main() -> None:
    """Demonstrate complete BaGuaLu workflow."""

    print("=" * 80)
    print("BaGuaLu Complete Comprehensive Example")
    print("=" * 80)

    workspace = Path.home() / ".bagualu" / "demo_workspace"
    workspace.mkdir(parents=True, exist_ok=True)

    print("\n[Phase 1: Initialization]")
    print("-" * 80)

    core = BaGuaLuCore(workspace=workspace)
    await core.initialize()

    print("✓ BaGuaLu initialized")
    print(f"✓ Workspace: {workspace}")

    config = await core.config.get_config()
    print("✓ Configuration loaded")
    print(f"  Providers: {list(config.get('providers', {}).keys())}")

    print("\n[Phase 2: Skill Discovery]")
    print("-" * 80)

    skills = core.list_skills()
    print(f"✓ Discovered {len(skills)} skills from multiple sources")

    if skills:
        sample_skills = skills[:5]
        for skill_name in sample_skills:
            skill_info = core.get_skill_info(skill_name)
            if skill_info:
                print(f"  • {skill_name} ({skill_info.get('source', 'unknown')})")

    print("\n[Phase 3: Agent Deployment]")
    print("-" * 80)

    print("\n3.1. Deploy Executor Agents")
    executors = []
    for i in range(2):
        executor_id = await core.deploy_agent(
            name=f"executor-{i + 1}",
            role="executor",
            provider="ollama",
            model="llama2",
            skills=["code-analysis"] if skills else [],
        )
        executors.append(executor_id)
        print(f"  ✓ Executor-{i + 1}: {executor_id}")

    print("\n3.2. Deploy Supervisor Agent")
    supervisor_id = await core.deploy_agent(
        name="quality-supervisor",
        role="supervisor",
        provider="ollama",
        model="llama2",
    )
    print(f"  ✓ Supervisor: {supervisor_id}")

    print("\n3.3. Deploy Scheduler Agent")
    scheduler_id = await core.deploy_agent(
        name="task-scheduler",
        role="scheduler",
        provider="ollama",
        model="llama2",
    )
    print(f"  ✓ Scheduler: {scheduler_id}")

    print("\n3.4. Deploy Agent Cluster")
    cluster_config = [
        {"name": "cluster-exec-1", "role": "executor", "provider": "ollama", "model": "llama2"},
        {"name": "cluster-exec-2", "role": "executor", "provider": "ollama", "model": "llama2"},
        {"name": "cluster-sup", "role": "supervisor", "provider": "ollama", "model": "llama2"},
    ]

    cluster_id = await core.deploy_cluster(
        name="production-cluster",
        agents=cluster_config,
    )
    print(f"  ✓ Cluster deployed: {cluster_id}")

    print("\n[Phase 4: Workflow Execution]")
    print("-" * 80)

    workflow_config = {
        "name": "data-processing-pipeline",
        "nodes": [
            {
                "id": "extract",
                "role": "executor",
                "instruction": "Extract data from source files",
            },
            {
                "id": "transform",
                "role": "executor",
                "instruction": "Transform and clean the extracted data",
                "dependencies": ["extract"],
            },
            {
                "id": "validate",
                "role": "supervisor",
                "instruction": "Validate transformed data quality",
                "dependencies": ["transform"],
            },
            {
                "id": "load",
                "role": "executor",
                "instruction": "Load validated data to destination",
                "dependencies": ["validate"],
            },
        ],
        "edges": [
            {"from": "extract", "to": "transform"},
            {"from": "transform", "to": "validate"},
            {"from": "validate", "to": "load"},
        ],
    }

    workflow_id = await core.create_workflow(workflow_config)
    print(f"✓ Workflow created: {workflow_id}")

    print("\nExecuting workflow...")
    workflow_result = await core.execute_workflow(
        workflow_id,
        inputs={
            "source_directory": str(workspace),
            "output_format": "json",
        },
    )

    print("✓ Workflow executed")
    print(f"  Result keys: {list(workflow_result.keys())}")

    print("\n[Phase 5: Task Execution]")
    print("-" * 80)

    if executors:
        task_result = await core.cluster.execute_with_agent(
            agent_id=executors[0],
            instruction="Analyze the workspace structure",
            inputs={"workspace": str(workspace)},
        )
        print("✓ Task executed on executor")
        print(f"  Result: {json.dumps(task_result, indent=2)[:200]}...")

    print("\n[Phase 6: Skill Management]")
    print("-" * 80)

    print("\n6.1. Install skill from GitHub (example)")
    print("  Command: bagualu skill install https://github.com/user/skill-repo")
    print("  API: await core.install_skill(repo_url='...', skill_name='...')")

    print("\n6.2. Skill evolution")
    if skills:
        print("  Evolving skills based on execution history...")
        stats = await core.skills.get_execution_statistics(skills[0])
        print(f"  Statistics for {skills[0]}:")
        print(f"    Executions: {stats.get('executions', 0)}")
        print(f"    Success rate: {stats.get('success_rate', 0)}")

    print("\n[Phase 7: Cluster Management]")
    print("-" * 80)

    cluster_status = await core.cluster.get_cluster_status()
    print("✓ Cluster status:")
    print(f"  Agents: {cluster_status.get('agents', {})}")
    print(f"  Active: {cluster_status.get('active_agents', 0)}")

    if executors:
        agent_status = await core.cluster.get_agent_status(executors[0])
        print(f"\n✓ Agent {executors[0]} status:")
        print(f"  Role: {agent_status.get('role', 'unknown')}")
        print(f"  Provider: {agent_status.get('provider', 'unknown')}")
        print(f"  Status: {agent_status.get('status', 'unknown')}")

    print("\n[Phase 8: Monitoring]")
    print("-" * 80)

    print("Monitoring metrics:")
    print(f"  • Total skills: {len(skills)}")
    print(f"  • Total agents: {len(executors) + 2}")
    print("  • Workflow executions: 1")
    print(f"  • Task executions: {len(executors)}")

    print("\n[Phase 9: Web UI]")
    print("-" * 80)

    print("Access BaGuaLu web UI:")
    print("  1. Start server: bagualu server")
    print("  2. Open browser: http://localhost:8000")
    print()
    print("Web UI features:")
    print("  • Dashboard - Overview and metrics")
    print("  • Agents - Deploy and manage agents")
    print("  • Skills - Browse and install skills")
    print("  • Workflows - Create and execute workflows")
    print("  • Settings - Configure providers and preferences")

    print("\n[Phase 10: Cleanup]")
    print("-" * 80)

    print("Cleaning up agents...")
    for executor_id in executors:
        await core.cluster.remove_agent(executor_id)
        print(f"  ✓ Removed executor: {executor_id}")

    await core.cluster.remove_agent(supervisor_id)
    print(f"  ✓ Removed supervisor: {supervisor_id}")

    await core.cluster.remove_agent(scheduler_id)
    print(f"  ✓ Removed scheduler: {scheduler_id}")

    print("\n" + "=" * 80)
    print("Complete comprehensive example finished!")
    print("=" * 80)

    print("\nSummary:")
    print("  ✓ Initialized BaGuaLu system")
    print(f"  ✓ Discovered {len(skills)} skills")
    print(f"  ✓ Deployed {len(executors) + 2} agents")
    print("  ✓ Created and executed workflow")
    print("  ✓ Managed cluster and monitored status")
    print("  ✓ Demonstrated all major features")

    print("\nNext steps:")
    print("  • Explore examples/ directory for specific use cases")
    print("  • Run 'bagualu server' to use the web UI")
    print("  • Create custom skills for your needs")
    print("  • Configure additional providers")


if __name__ == "__main__":
    asyncio.run(main())
