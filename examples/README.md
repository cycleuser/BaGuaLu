# BaGuaLu Examples

This directory contains comprehensive examples demonstrating all BaGuaLu features.

## Examples Overview

### 1. Skill Management (`skill_management.py`)
Demonstrates how to:
- List available skills from multiple sources (OpenCode, Claude Code, OpenLaoKe)
- Get detailed skill information
- Install skills from GitHub repositories
- Load skills into agents
- Rescan skill directories

**Run:**
```bash
python examples/skill_management.py
```

### 2. Multi-Provider Configuration (`multi_provider_config.py`)
Demonstrates how to:
- Configure multiple LLM providers (Ollama, OpenAI, Claude, etc.)
- Set up provider priorities and fallbacks
- Deploy agents with different providers
- Switch between providers dynamically

**Run:**
```bash
python examples/multi_provider_config.py
```

### 3. Web UI Usage (`web_ui_usage.py`)
Demonstrates how to:
- Start the BaGuaLu web server
- Use REST API endpoints
- Manage agents via web interface
- Execute workflows through the API
- Configure settings via Web UI

**Run:**
```bash
python examples/web_ui_usage.py
```

### 4. CLI Usage (`cli_usage.sh`)
Comprehensive CLI command examples:
- Initialize and configure
- Skill management commands
- Agent deployment
- Workflow execution
- Web server management
- Common workflows

**Run:**
```bash
bash examples/cli_usage.sh
```

### 5. Supervisor Agent (`agent_supervisor.py`)
Demonstrates how to:
- Deploy supervisor agents
- Configure supervision behavior
- Monitor executor agents
- Handle task failures and retries
- Implement quality control

**Run:**
```bash
python examples/agent_supervisor.py
```

### 6. Scheduler Agent (`agent_scheduler.py`)
Demonstrates how to:
- Deploy scheduler agents
- Configure scheduling policies
- Manage task queues and priorities
- Handle resource allocation
- Implement batch processing

**Run:**
```bash
python examples/agent_scheduler.py
```

### 7. Tool System (`tool_system.py`)
Demonstrates how to:
- Create custom tools
- Register tools in the tool registry
- Use tools in agents and skills
- Validate tool inputs with Pydantic
- Handle tool execution results

**Run:**
```bash
python examples/tool_system.py
```

### 8. Complete Example (`complete_example.py`)
Full comprehensive workflow demonstrating:
- Initialization with multi-provider configuration
- Skill discovery and installation
- Multi-role agent cluster deployment
- Workflow creation and execution
- Tool and skill evolution
- System monitoring and management

**Run:**
```bash
python examples/complete_example.py
```

### 9. Simple Cluster (`simple_cluster.py`)
Basic example showing:
- Initialize BaGuaLu
- Deploy a single agent
- Execute a task
- Get cluster status

**Run:**
```bash
python examples/simple_cluster.py
```

### 10. Workflow Orchestration (`workflow_orchestration.py`)
Demonstrates:
- Define workflow DAG
- Create workflow with dependencies
- Execute multi-step workflow
- Handle workflow results

**Run:**
```bash
python examples/workflow_orchestration.py
```

### 11. Skill Evolution (`skill_evolution.py`)
Demonstrates:
- Get skill statistics
- Trigger skill evolution
- View skill lineage
- Evolve all agents in cluster

**Run:**
```bash
python examples/skill_evolution.py
```

## Example Skills

Example skills are located in `bagualu/skills/examples/`:

- **data-analysis** - Data processing and analysis skill
- **code-review** - Code quality review skill
- **test-generator** - Test generation and execution skill

## Running Examples

### Prerequisites

1. Install BaGuaLu:
```bash
pip install -e ".[dev,web]"
```

2. Initialize configuration:
```bash
bagualu --init
```

3. Configure at least one provider (e.g., Ollama):
```bash
bagualu config --provider ollama --model llama2
```

### Run Examples

All Python examples can be run directly:

```bash
# Run any example
python examples/<example_name>.py

# Run complete example (recommended first)
python examples/complete_example.py
```

### Web UI Examples

For Web UI examples:

1. Start the web server:
```bash
bagualu server
```

2. Open browser: http://localhost:8000

3. Explore features through the UI

## Example Workflows

### Development Workflow

```bash
# Initialize
bagualu --init

# Configure for development
bagualu config --provider ollama --model llama2

# List available skills
bagualu skill list

# Deploy development agent
bagualu deploy dev-agent --role executor --skills code-analysis

# Start web UI
bagualu server &
open http://localhost:8000

# Monitor status
bagualu status
```

### Production Workflow

```bash
# Configure production provider
bagualu config --provider openai --model gpt-4

# Deploy production cluster
python examples/complete_example.py

# Run workflow
bagualu run production-workflow.yaml

# Monitor cluster
bagualu status
```

## Creating Custom Examples

To create your own example:

1. Import BaGuaLu:
```python
import asyncio
from pathlib import Path
from bagualu import BaGuaLuCore

async def main():
    core = BaGuaLuCore(workspace=Path.home() / ".bagualu" / "my_workspace")
    await core.initialize()
    
    # Your custom logic here
    agent_id = await core.deploy_agent(
        name="my-agent",
        role="executor",
        provider="ollama",
        model="llama2",
    )
    
    result = await core.cluster.execute_with_agent(
        agent_id=agent_id,
        instruction="My custom task",
        inputs={},
    )
    
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

2. Save as `examples/my_example.py`

3. Run:
```bash
python examples/my_example.py
```

## Troubleshooting

### Common Issues

1. **Provider not configured**
   - Run `bagualu config --provider <name> --model <model>`

2. **Skills not found**
   - Run `bagualu skill rescan`
   - Check skill directories with `bagualu skill sources`

3. **Ollama not running**
   - Start Ollama: `ollama serve`
   - Pull model: `ollama pull llama2`

4. **Web server not starting**
   - Check port availability
   - Install web dependencies: `pip install -e ".[web]"`

## Next Steps

After running examples:

- Read the [README](../README.md) for full documentation
- Check [AGENTS.md](../AGENTS.md) for development guidelines
- Create your own skills in `~/.bagualu/skills/`
- Explore the Web UI at http://localhost:8000
- Join the community and contribute!