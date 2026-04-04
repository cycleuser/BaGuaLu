"""Example: Skill evolution."""

import asyncio

from bagualu import BaGuaLuCore
from bagualu.skills.evolver import EvolutionTrigger


async def main() -> None:
    """Demonstrate skill evolution."""

    # Initialize
    core = BaGuaLuCore()
    await core.initialize()

    # Get skill statistics
    stats = await core.skills.get_execution_statistics("my-skill")
    print(f"Skill statistics: {stats}")

    # Trigger evolution
    evolved = await core.evolve_skill(
        skill_name="my-skill",
        evolution_type="auto",
    )

    if evolved:
        print("Skill evolved successfully!")

        # Get lineage
        lineage = await core.skills.get_skill_lineage("my-skill")
        print(f"Skill lineage: {lineage}")
    else:
        print("Skill did not evolve")

    # Evolve all agents
    evolution_results = await core.cluster.evolve_all_agents()
    print(f"Agent evolution results: {evolution_results}")


if __name__ == "__main__":
    asyncio.run(main())
