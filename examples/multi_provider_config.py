"""Example: Multi-provider configuration.

This example demonstrates how to:
1. Configure multiple LLM providers (Ollama, OpenAI, Claude, etc.)
2. Set up provider priorities and fallbacks
3. Deploy agents with different providers
4. Switch between providers dynamically
5. Configure API keys and endpoints
"""

import asyncio
from pathlib import Path

from bagualu import BaGuaLuCore
from bagualu.config import ConfigManager


async def main() -> None:
    """Demonstrate multi-provider configuration."""

    print("=" * 60)
    print("BaGuaLu Multi-Provider Configuration Example")
    print("=" * 60)

    config_path = Path.home() / ".bagualu" / "config.yaml"
    config_manager = ConfigManager(config_path)

    print("\n1. Current configuration")
    print("-" * 60)
    await config_manager.load()
    config = await config_manager.get_config()
    print(f"Config file: {config_path}")
    print(f"Current providers: {list(config.get('providers', {}).keys())}")

    print("\n2. Provider configuration examples")
    print("-" * 60)
    print("Configure different providers in ~/.bagualu/config.yaml:")
    print()
    print("# Ollama (local)")
    print("providers:")
    print("  ollama:")
    print("    base_url: http://localhost:11434")
    print("    models:")
    print("      - llama2")
    print("      - codellama")
    print()
    print("# LMStudio (local)")
    print("  lmstudio:")
    print("    base_url: http://localhost:1234/v1")
    print("    models:")
    print("      - local-model")
    print()
    print("# OpenAI")
    print("  openai:")
    print("    api_key: ${OPENAI_API_KEY}")
    print("    models:")
    print("      - gpt-4")
    print("      - gpt-3.5-turbo")
    print()
    print("# Claude")
    print("  claude:")
    print("    api_key: ${ANTHROPIC_API_KEY}")
    print("    models:")
    print("      - claude-3-opus")
    print("      - claude-3-sonnet")
    print()
    print("# CodingPlan")
    print("  codingplan:")
    print("    api_key: ${CODINGPLAN_API_KEY}")
    print("    base_url: https://api.codingplan.com")
    print("    models:")
    print("      - glm-4")

    print("\n3. Set default provider and model")
    print("-" * 60)
    print("CLI commands:")
    print("  bagualu config --provider ollama --model llama2")
    print("  bagualu config --provider openai --model gpt-4")
    print()
    print("Python API:")
    print("  await config_manager.set_default_provider('ollama')")
    print("  await config_manager.set_default_model('llama2')")

    print("\n4. Deploy agents with different providers")
    print("-" * 60)
    core = BaGuaLuCore(config_path=config_path)
    await core.initialize()

    print("\nDeploying agents with different providers...")

    agents = []

    ollama_agent = await core.deploy_agent(
        name="local-agent",
        role="executor",
        provider="ollama",
        model="llama2",
    )
    agents.append(("Ollama", ollama_agent))
    print(f"  ✓ Ollama agent: {ollama_agent}")

    print("\n  Note: To deploy with other providers, ensure API keys are set:")
    print("    OpenAI agent:")
    print("      await core.deploy_agent(")
    print("          name='openai-agent',")
    print("          provider='openai',")
    print("          model='gpt-4',")
    print("      )")
    print("    Claude agent:")
    print("      await core.deploy_agent(")
    print("          name='claude-agent',")
    print("          provider='claude',")
    print("          model='claude-3-opus',")
    print("      )")

    print("\n5. Multi-provider cluster")
    print("-" * 60)
    print("Deploy a cluster with mixed providers:")
    print("  cluster_id = await core.deploy_cluster(")
    print("      name='multi-provider-cluster',")
    print("      agents=[")
    print("          {'name': 'local-executor', 'provider': 'ollama', 'model': 'llama2'},")
    print("          {'name': 'cloud-supervisor', 'provider': 'openai', 'model': 'gpt-4'},")
    print("          {'name': 'claude-reviewer', 'provider': 'claude', 'model': 'claude-3-opus'},")
    print("      ],")
    print("  )")

    print("\n6. Provider fallback configuration")
    print("-" * 60)
    print("Configure fallback providers in config.yaml:")
    print("  fallback_chain:")
    print("    - ollama")
    print("    - openai")
    print("    - claude")
    print()
    print("When primary provider fails, BaGuaLu will try fallback providers in order.")

    print("\n7. Environment variables for API keys")
    print("-" * 60)
    print("Set API keys as environment variables:")
    print("  export OPENAI_API_KEY='sk-...'")
    print("  export ANTHROPIC_API_KEY='sk-ant-...'")
    print("  export CODINGPLAN_API_KEY='...'")
    print()
    print("Or use .env file in project root:")
    print("  OPENAI_API_KEY=sk-...")
    print("  ANTHROPIC_API_KEY=sk-ant-...")

    print("\n8. Check cluster status")
    print("-" * 60)
    status = await core.cluster.get_cluster_status()
    print(f"Cluster status: {status}")

    print("\n" + "=" * 60)
    print("Multi-provider configuration example completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
