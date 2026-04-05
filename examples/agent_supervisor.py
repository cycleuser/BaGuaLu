"""Example: Supervisor agent usage.

This example demonstrates how to:
1. Deploy supervisor agents
2. Configure supervision behavior
3. Monitor and manage executor agents
4. Handle task failures and retries
5. Implement quality control
"""

import asyncio
from pathlib import Path

from bagualu import BaGuaLuCore


async def main() -> None:
    """Demonstrate supervisor agent capabilities."""

    print("=" * 60)
    print("BaGuaLu Supervisor Agent Example")
    print("=" * 60)

    core = BaGuaLuCore(workspace=Path.home() / ".bagualu" / "workspace")
    await core.initialize()

    print("\n1. Understanding Supervisor Agents")
    print("-" * 60)
    print("Supervisor agents are responsible for:")
    print("  • Monitoring executor agent performance")
    print("  • Quality assurance and validation")
    print("  • Handling task failures and retries")
    print("  • Allocating tasks to appropriate executors")
    print("  • Providing feedback and corrections")

    print("\n2. Deploy Executor Agents")
    print("-" * 60)

    executor1_id = await core.deploy_agent(
        name="executor-1",
        role="executor",
        provider="ollama",
        model="llama2",
        skills=["code-analysis"],
    )
    print(f"Deployed executor-1: {executor1_id}")

    executor2_id = await core.deploy_agent(
        name="executor-2",
        role="executor",
        provider="ollama",
        model="llama2",
        skills=["test-generator"],
    )
    print(f"Deployed executor-2: {executor2_id}")

    print("\n3. Deploy Supervisor Agent")
    print("-" * 60)

    supervisor_id = await core.deploy_agent(
        name="quality-supervisor",
        role="supervisor",
        provider="ollama",
        model="llama2",
    )
    print(f"Deployed supervisor: {supervisor_id}")

    print("\n4. Supervisor Configuration")
    print("-" * 60)
    print("Supervisors can be configured with:")
    print("  • Monitoring interval")
    print("  • Quality thresholds")
    print("  • Retry policies")
    print("  • Notification settings")
    print()
    print("Example configuration (in config.yaml):")
    print("  supervisor:")
    print("    monitoring_interval: 30  # seconds")
    print("    quality_threshold: 0.8")
    print("    max_retries: 3")
    print("    notification_channels:")
    print("      - log")
    print("      - webhook")

    print("\n5. Task Assignment and Monitoring")
    print("-" * 60)
    print("Supervisors automatically:")
    print("  • Assign tasks to available executors")
    print("  • Monitor task progress")
    print("  • Validate results")
    print("  • Retry failed tasks")
    print()
    print("Example workflow with supervision:")

    result1 = await core.cluster.execute_with_agent(
        agent_id=executor1_id,
        instruction="Analyze code quality in current directory",
        inputs={},
    )
    print(f"Task 1 result: {result1}")

    result2 = await core.cluster.execute_with_agent(
        agent_id=executor2_id,
        instruction="Generate tests for analyzed code",
        inputs={"analysis": result1},
    )
    print(f"Task 2 result: {result2}")

    print("\n6. Quality Control")
    print("-" * 60)
    print("Supervisors validate outputs based on:")
    print("  • Completeness checks")
    print("  • Format validation")
    print("  • Quality metrics")
    print("  • Error detection")
    print()
    print("Validation example:")
    print("  # Supervisor validates executor output")
    print("  validation_result = await core.cluster.validate_result(")
    print("      agent_id=executor_id,")
    print("      result=task_result,")
    print("      criteria=['completeness', 'correctness', 'quality']")
    print("  )")

    print("\n7. Failure Handling")
    print("-" * 60)
    print("When tasks fail, supervisors:")
    print("  • Log the failure")
    print("  • Analyze the cause")
    print("  • Decide retry strategy")
    print("  • Reassign if needed")
    print()
    print("Failure handling configuration:")
    print("  failure_handling:")
    print("    auto_retry: true")
    print("    max_retries: 3")
    print("    retry_delay: 5  # seconds")
    print("    exponential_backoff: true")
    print("    fallback_agent: backup-executor")

    print("\n8. Supervisor Metrics")
    print("-" * 60)

    status = await core.cluster.get_agent_status(supervisor_id)
    print(f"Supervisor status: {status}")

    cluster_status = await core.cluster.get_cluster_status()
    print(f"Cluster status: {cluster_status}")

    print("\n9. Multi-Level Supervision")
    print("-" * 60)
    print("Hierarchical supervision structure:")
    print()
    print("  Level 1: Task Supervisors")
    print("    - Monitor specific task types")
    print("    - Quality control for domain-specific tasks")
    print()
    print("  Level 2: Team Supervisors")
    print("    - Coordinate multiple task supervisors")
    print("    - Resource allocation")
    print()
    print("  Level 3: Cluster Coordinator")
    print("    - Overall system health")
    print("    - Cross-team coordination")
    print()
    print("Example:")
    print("  # Deploy hierarchical supervisors")
    print("  task_sup = await core.deploy_agent('task-sup', 'supervisor')")
    print("  team_sup = await core.deploy_agent('team-sup', 'supervisor')")
    print("  coordinator = await core.deploy_agent('coordinator', 'coordinator')")

    print("\n10. Best Practices")
    print("-" * 60)
    print("✓ Deploy supervisors for production workloads")
    print("✓ Configure appropriate monitoring intervals")
    print("✓ Set up notification channels for failures")
    print("✓ Use different providers for executors and supervisors")
    print("✓ Monitor supervisor metrics regularly")
    print("✓ Implement graceful degradation")

    print("\n" + "=" * 60)
    print("Supervisor agent example completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
