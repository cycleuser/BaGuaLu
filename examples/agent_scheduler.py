"""Example: Scheduler agent usage.

This example demonstrates how to:
1. Deploy scheduler agents
2. Configure scheduling policies
3. Manage task queues and priorities
4. Handle resource allocation
5. Implement batch processing
"""

import asyncio
from pathlib import Path

from bagualu import BaGuaLuCore


async def main() -> None:
    """Demonstrate scheduler agent capabilities."""

    print("=" * 60)
    print("BaGuaLu Scheduler Agent Example")
    print("=" * 60)

    core = BaGuaLuCore(workspace=Path.home() / ".bagualu" / "workspace")
    await core.initialize()

    print("\n1. Understanding Scheduler Agents")
    print("-" * 60)
    print("Scheduler agents are responsible for:")
    print("  • Task queue management")
    print("  • Priority-based task assignment")
    print("  • Resource allocation and load balancing")
    print("  • Batch processing coordination")
    print("  • Scheduling policies (round-robin, priority, etc.)")

    print("\n2. Deploy Executor Pool")
    print("-" * 60)

    executors = []
    for i in range(3):
        executor_id = await core.deploy_agent(
            name=f"executor-{i + 1}",
            role="executor",
            provider="ollama",
            model="llama2",
        )
        executors.append(executor_id)
        print(f"Deployed executor-{i + 1}: {executor_id}")

    print("\n3. Deploy Scheduler Agent")
    print("-" * 60)

    scheduler_id = await core.deploy_agent(
        name="task-scheduler",
        role="scheduler",
        provider="ollama",
        model="llama2",
    )
    print(f"Deployed scheduler: {scheduler_id}")

    print("\n4. Scheduling Policies")
    print("-" * 60)
    print("Available scheduling policies:")
    print()
    print("  1. Round Robin")
    print("     - Tasks distributed equally among executors")
    print("     - Fair resource usage")
    print()
    print("  2. Priority-based")
    print("     - High-priority tasks processed first")
    print("     - Critical tasks get dedicated resources")
    print()
    print("  3. Load-balanced")
    print("     - Tasks assigned to least busy executor")
    print("     - Optimizes throughput")
    print()
    print("  4. Skill-based")
    print("     - Tasks matched with executors having required skills")
    print("     - Specialized task handling")
    print()
    print("Configuration example:")
    print("  scheduler:")
    print("    policy: priority")
    print("    queue_size: 100")
    print("    batch_size: 10")
    print("    timeout: 300  # seconds")

    print("\n5. Task Queue Management")
    print("-" * 60)
    print("Submit tasks to the queue:")
    print()
    print("  # Submit single task")
    print("  task_id = await core.cluster.submit_task(")
    print("      instruction='Process data file',")
    print("      priority='high',")
    print("      inputs={'file': 'data.csv'}")
    print("  )")
    print()
    print("  # Submit batch tasks")
    print("  batch_ids = await core.cluster.submit_batch(")
    print("      tasks=[")
    print("          {'instruction': 'Task 1', 'priority': 'medium'},")
    print("          {'instruction': 'Task 2', 'priority': 'high'},")
    print("          {'instruction': 'Task 3', 'priority': 'low'},")
    print("      ]")
    print("  )")

    print("\n6. Priority Levels")
    print("-" * 60)
    print("Task priority hierarchy:")
    print()
    print("  critical - Immediate processing")
    print("  high     - Priority queue")
    print("  medium   - Standard queue")
    print("  low      - Background processing")
    print("  batch    - Batch queue")
    print()
    print("Priority configuration:")
    print("  priorities:")
    print("    critical:")
    print("      max_concurrent: 5")
    print("      timeout: 60")
    print("    high:")
    print("      max_concurrent: 10")
    print("      timeout: 120")
    print("    medium:")
    print("      max_concurrent: 20")
    print("      timeout: 300")

    print("\n7. Resource Allocation")
    print("-" * 60)
    print("Scheduler manages resources:")
    print()
    print("  • CPU/Memory allocation per executor")
    print("  • Concurrent task limits")
    print("  • Time-based quotas")
    print("  • Provider-specific limits")
    print()
    print("Resource limits configuration:")
    print("  resources:")
    print("    max_cpu_per_agent: 50%")
    print("    max_memory_per_agent: 2GB")
    print("    max_concurrent_tasks: 10")
    print("    time_quota:")
    print("      daily_limit: 1000  # tasks per day")
    print("      hourly_limit: 100")

    print("\n8. Batch Processing")
    print("-" * 60)
    print("Schedule batch processing jobs:")
    print()
    print("  # Create batch job")
    print("  batch_job = await core.cluster.create_batch_job(")
    print("      name='daily-report',")
    print("      tasks=[...],")
    print("      schedule='0 6 * * *'  # cron format")
    print("  )")
    print()
    print("  # Common batch schedules:")
    print("  schedule='0 */2 * * *'  # Every 2 hours")
    print("  schedule='0 0 * * 0'    # Weekly on Sunday")
    print("  schedule='0 9 1 * *'    # Monthly on 1st at 9am")

    print("\n9. Queue Monitoring")
    print("-" * 60)

    status = await core.cluster.get_agent_status(scheduler_id)
    print(f"Scheduler status: {status}")

    cluster_status = await core.cluster.get_cluster_status()
    print(f"Cluster status: {cluster_status}")
    print(f"Executor pool size: {len(executors)}")

    print("\n10. Task Retry and Timeout")
    print("-" * 60)
    print("Configure retry and timeout policies:")
    print()
    print("  retry_policy:")
    print("    max_retries: 3")
    print("    retry_delay: 10")
    print("    exponential_backoff: true")
    print()
    print("  timeout_policy:")
    print("    default_timeout: 300")
    print("    critical_timeout: 60")
    print("    graceful_shutdown: 30")

    print("\n11. Scheduler Metrics")
    print("-" * 60)
    print("Monitor scheduler performance:")
    print()
    print("  # Get queue statistics")
    print("  queue_stats = await core.cluster.get_queue_stats()")
    print("  print(f'Queue size: {queue_stats.size}')")
    print("  print(f'Average wait time: {queue_stats.avg_wait_time}')")
    print()
    print("  # Get throughput metrics")
    print("  metrics = await core.cluster.get_scheduler_metrics()")
    print("  print(f'Tasks processed: {metrics.total_tasks}')")
    print("  print(f'Throughput: {metrics.throughput} tasks/min')")

    print("\n12. Best Practices")
    print("-" * 60)
    print("✓ Use appropriate scheduling policy for workload")
    print("✓ Set realistic priority levels")
    print("✓ Configure proper timeouts")
    print("✓ Monitor queue sizes regularly")
    print("✓ Implement retry policies for reliability")
    print("✓ Use batch processing for repetitive tasks")
    print("✓ Balance executor pool size with workload")

    print("\n" + "=" * 60)
    print("Scheduler agent example completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
