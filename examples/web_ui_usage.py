"""Example: Web UI usage.

This example demonstrates how to:
1. Start the BaGuaLu web server
2. Use the REST API endpoints
3. Interact with the web UI
4. Manage agents via web interface
5. Execute workflows through the API
"""

import asyncio

import httpx


async def main() -> None:
    """Demonstrate Web UI usage."""

    print("=" * 60)
    print("BaGuaLu Web UI Usage Example")
    print("=" * 60)

    base_url = "http://localhost:8000"

    print("\n1. Starting the Web Server")
    print("-" * 60)
    print("Start the BaGuaLu web server:")
    print("  CLI: bagualu server --host 0.0.0.0 --port 8000")
    print("  Python: from bagualu.web import start_server")
    print("          await start_server(host='0.0.0.0', port=8000)")
    print()
    print("The web UI will be available at: http://localhost:8000")

    print("\n2. Web UI Features")
    print("-" * 60)
    print("Available pages:")
    print("  • Dashboard: http://localhost:8000/")
    print("    - Cluster overview and status")
    print("    - Agent health monitoring")
    print("    - Recent activity")
    print()
    print("  • Agents: http://localhost:8000/agents")
    print("    - List all agents")
    print("    - Deploy new agents")
    print("    - Configure agent settings")
    print()
    print("  • Skills: http://localhost:8000/skills")
    print("    - Browse available skills")
    print("    - Install new skills")
    print("    - View skill details")
    print()
    print("  • Workflows: http://localhost:8000/workflows")
    print("    - Create workflows")
    print("    - Execute workflows")
    print("    - Monitor progress")
    print()
    print("  • Settings: http://localhost:8000/settings")
    print("    - Configure providers")
    print("    - Set API keys")
    print("    - Manage preferences")

    print("\n3. REST API Endpoints")
    print("-" * 60)
    print("Available API endpoints:")
    print()
    print("  GET  /api/status")
    print("       Get cluster status")
    print()
    print("  GET  /api/agents")
    print("       List all agents")
    print()
    print("  POST /api/agents")
    print("       Deploy a new agent")
    print(
        "       Body: {'name': 'my-agent', 'role': 'executor', 'provider': 'ollama', 'model': 'llama2'}"
    )
    print()
    print("  GET  /api/agents/{agent_id}")
    print("       Get agent details")
    print()
    print("  DELETE /api/agents/{agent_id}")
    print("       Remove an agent")
    print()
    print("  GET  /api/skills")
    print("       List all available skills")
    print()
    print("  GET  /api/skills/{skill_name}")
    print("       Get skill details")
    print()
    print("  POST /api/workflows")
    print("       Create a new workflow")
    print()
    print("  POST /api/workflows/{workflow_id}/execute")
    print("       Execute a workflow")
    print()
    print("  GET  /api/config")
    print("       Get current configuration")
    print()
    print("  PUT  /api/config")
    print("       Update configuration")

    print("\n4. API Usage Examples (Python)")
    print("-" * 60)
    print("Using httpx or requests:")
    print()
    print("  import httpx")
    print()
    print("  # Get cluster status")
    print("  response = httpx.get('http://localhost:8000/api/status')")
    print("  status = response.json()")
    print()
    print("  # Deploy an agent")
    print("  response = httpx.post(")
    print("      'http://localhost:8000/api/agents',")
    print("      json={")
    print("          'name': 'my-agent',")
    print("          'role': 'executor',")
    print("          'provider': 'ollama',")
    print("          'model': 'llama2',")
    print("          'skills': ['code-analysis'],")
    print("      }")
    print("  )")
    print("  agent_id = response.json()['agent_id']")
    print()
    print("  # List skills")
    print("  response = httpx.get('http://localhost:8000/api/skills')")
    print("  skills = response.json()['skills']")

    print("\n5. Testing Web API")
    print("-" * 60)
    print("Testing API connectivity:")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/api/status", timeout=5.0)
            if response.status_code == 200:
                print("  ✓ Web server is running")
                print(f"  ✓ Status: {response.json()}")
            else:
                print("  ✗ Web server returned error")
    except Exception as e:
        print(f"  ✗ Cannot connect to web server: {e}")
        print("  Start the server with: bagualu server")

    print("\n6. Web UI Workflow Example")
    print("-" * 60)
    print("Create and execute a workflow via API:")
    print()
    print("  # Create workflow")
    print("  workflow_config = {")
    print("      'name': 'data-pipeline',")
    print("      'nodes': [")
    print("          {'id': 'extract', 'role': 'executor', 'instruction': 'Extract data'},")
    print("          {'id': 'transform', 'role': 'executor', 'instruction': 'Transform data'},")
    print("          {'id': 'load', 'role': 'executor', 'instruction': 'Load data'},")
    print("      ],")
    print("      'edges': [")
    print("          {'from': 'extract', 'to': 'transform'},")
    print("          {'from': 'transform', 'to': 'load'},")
    print("      ],")
    print("  }")
    print()
    print("  response = httpx.post(")
    print("      'http://localhost:8000/api/workflows',")
    print("      json=workflow_config")
    print("  )")
    print("  workflow_id = response.json()['workflow_id']")
    print()
    print("  # Execute workflow")
    print("  response = httpx.post(")
    print("      f'http://localhost:8000/api/workflows/{workflow_id}/execute',")
    print("      json={'inputs': {'source': 'database'}}")
    print("  )")
    print("  result = response.json()")

    print("\n7. Configuration via Web UI")
    print("-" * 60)
    print("Access settings at: http://localhost:8000/settings")
    print()
    print("Configure providers:")
    print("  • Add/remove providers (Ollama, OpenAI, Claude, etc.)")
    print("  • Set API keys")
    print("  • Configure base URLs")
    print("  • Set default provider/model")
    print()
    print("Configure skills:")
    print("  • Add skill directories")
    print("  • Rescan for new skills")
    print("  • View skill statistics")

    print("\n" + "=" * 60)
    print("Web UI usage example completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
