# BaGuaLu (八卦炉)

<div align="center">

**八卦炉 - Intelligent Agent Orchestration Platform for Self-Evolving Agent Clusters**

[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![PyPI](https://img.shields.io/badge/PyPI-0.1.0-orange.svg)](https://pypi.org/project/bagualu/)

**一键部署智能体集群 | 技能自我进化 | 多工作流编排**

English | [中文](README_CN.md)

</div>

---

## 🎯 What is BaGuaLu?

**BaGuaLu (八卦炉)** 是一个强大的智能体编排平台，融合了 **OpenLaoKe**、**OpenSpace** 和 **OpenHarness** 的优秀设计理念：

### ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 🚀 **一键部署** | 单个智能体、智能体矩阵、集群的一键部署 |
| 🧬 **自我进化** | 智能体和技能的自我进化能力（FIX, DERIVED, CAPTURED） |
| 🔧 **多提供商支持** | Ollama、LMStudio、OpenAI、Claude、CodingPlan 等 |
| 📚 **技能系统** | OpenCode/Claude Code 技能加载和按需知识 |
| 🌐 **工作流编排** | Web界面拖拽设计工作流，DAG执行 |
| 🤝 **多智能体协调** | Supervisor、Scheduler、Executor 协同工作 |
| 🛡️ **权限管理** | 多级权限控制和钩子系统 |
| 📊 **资源调度** | 智能资源分配和负载均衡 |

---

## 🏗️ Architecture

```
bagualu/
├── core/              # 核心编排系统
│   ├── bagualu_core.py    # 主核心类
│   ├── orchestrator.py    # 编排器
│   └── resource_manager.py # 资源管理
├── agents/            # 智能体系统
│   ├── base.py            # 基础智能体
│   ├── executor.py        # 执行智能体
│   ├── supervisor.py      # 监工智能体
│   ├── scheduler.py       # 调度智能体
│   └── cluster.py         # 智能体集群
├── skills/            # 技能系统（参考 OpenSpace）
│   ├── skill_engine.py    # 技能引擎
│   ├── evolver.py         # 自我进化引擎
│   ├── registry.py        # 技能注册
│   └── store.py           # 持久化存储
├── config/            # 配置系统（参考 OpenLaoKe）
│   ├── config_manager.py  # 配置管理
│   ├── providers.py       # 多提供商配置
│   └── wizard.py          # 配置向导
├── workflow/          # 工作流系统
│   ├── workflow_engine.py # 工作流引擎
│   └── workflow_dag.py    # DAG定义
├── tools/             # 工具系统（参考 OpenHarness）
│   └── base.py            # 工具基类
├── web/               # Web界面
│   ├── api_server.py      # REST API
│   └── workflow_ui.py     # 工作流UI
└── entrypoints/       # 入口点
    └── cli.py             # CLI入口
```

---

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/cycleuser/BaGuaLu.git
cd BaGuaLu

# Install with pip
pip install -e .

# Or install from PyPI
pip install bagualu
```

### Initialize Configuration

```bash
# Run configuration wizard
bagualu --init
```

### Deploy an Agent

```bash
# Deploy a single agent
bagualu deploy my-agent --role executor --provider ollama --model llama2

# Or interactively
bagualu
> deploy
```

### Execute a Workflow

```bash
# Create workflow.json
{
  "name": "my-workflow",
  "nodes": [
    {"id": "task1", "role": "executor", "instruction": "Analyze codebase"},
    {"id": "task2", "role": "supervisor", "instruction": "Review results", "dependencies": ["task1"]}
  ],
  "edges": [
    {"from": "task1", "to": "task2"}
  ]
}

# Execute workflow
bagualu run workflow.json
```

---

## 🔧 Configuration

### Multi-Provider Setup

BaGuaLu 支持多种 LLM 提供商：

```yaml
# ~/.bagualu/config.yaml
providers:
  ollama:
    base_url: http://localhost:11434
    model: llama2
    enabled: true
  
  openai:
    api_key: sk-xxx
    model: gpt-4
    enabled: true
  
  anthropic:
    api_key: sk-xxx
    model: claude-3-5-sonnet-20241022
    enabled: true
  
  coding_plan:
    api_key: sk-xxx
    model: default
    enabled: true

active_provider: ollama

settings:
  max_concurrent_agents: 10
  evolution_enabled: true
  quality_threshold: 0.8
```

---

## 🧬 Self-Evolution

BaGuaLu 的技能自我进化系统（参考 OpenSpace）：

### Evolution Types

| Type | Description |
|------|-------------|
| **FIX** | 修复破损或过时的技能指令 |
| **DERIVED** | 从现有技能创建增强版本 |
| **CAPTURED** | 从成功执行中捕获新模式 |

### Trigger Evolution

```bash
# CLI
bagualu evolve skill-name

# Python API
await core.evolve_skill("skill-name", evolution_type="auto")
```

---

## 🤝 Multi-Agent Coordination

### Agent Roles

| Role | Responsibility |
|------|----------------|
| **Executor** | 执行具体任务 |
| **Supervisor** | 监督和质量控制 |
| **Scheduler** | 任务调度和资源分配 |
| **Coordinator** | 多智能体协调 |

### Deploy a Cluster

```python
import asyncio
from bagualu import BaGuaLuCore

async def main():
    core = BaGuaLuCore()
    await core.initialize()
    
    # Deploy cluster
    cluster_config = {
        "name": "my-cluster",
        "agents": [
            {"name": "executor1", "role": "executor"},
            {"name": "executor2", "role": "executor"},
            {"name": "supervisor1", "role": "supervisor"},
            {"name": "scheduler1", "role": "scheduler"},
        ],
        "connections": [
            {"from": "executor1", "to": "supervisor1"},
            {"from": "executor2", "to": "supervisor1"},
        ]
    }
    
    agent_ids = await core.deploy_cluster(cluster_config)
    print(f"Deployed {len(agent_ids)} agents")

asyncio.run(main())
```

---

## 🌐 Web Interface

### Start Web Server

```bash
bagualu server --host 0.0.0.0 --port 8000
```

### REST API Endpoints

- `POST /agents` - Deploy agent
- `GET /agents` - List agents
- `POST /workflows` - Create workflow
- `POST /workflows/{id}/execute` - Execute workflow
- `GET /skills` - List skills
- `POST /skills/{name}/evolve` - Evolve skill

---

## 📚 Skills System

### Load Skills

```python
# Load from OpenCode/Claude Code skill directory
await core.skills.import_skill_from_opencode(
    Path("~/.config/opencode/skills/my-skill")
)
```

### Create Custom Skill

```markdown
# ~/.bagualu/skills/my-skill.md

# My Custom Skill

## When to use
Use when the user asks about [specific domain].

## Workflow
1. Step one
2. Step two
3. Step three

## Triggers
- trigger keyword 1
- trigger keyword 2
```

---

## 🔌 Integration with Other Projects

BaGuaLu 兼容以下项目的技能和插件：

- ✅ **OpenCode** skills
- ✅ **Claude Code** skills
- ✅ **OpenLaoKe** configurations
- ✅ **OpenSpace** evolution patterns
- ✅ **OpenHarness** tool system

---

## 📊 Examples

See [`examples/`](examples/) directory for comprehensive examples:

### Available Examples

| Example | Description |
|---------|-------------|
| **[skill_management.py](examples/skill_management.py)** | List, install, and load skills from multiple sources |
| **[multi_provider_config.py](examples/multi_provider_config.py)** | Configure multiple LLM providers with fallbacks |
| **[web_ui_usage.py](examples/web_ui_usage.py)** | Use REST API and Web UI features |
| **[cli_usage.sh](examples/cli_usage.sh)** | All CLI commands and workflows |
| **[agent_supervisor.py](examples/agent_supervisor.py)** | Deploy and configure supervisor agents |
| **[agent_scheduler.py](examples/agent_scheduler.py)** | Task scheduling and queue management |
| **[tool_system.py](examples/tool_system.py)** | Create and use custom tools |
| **[complete_example.py](examples/complete_example.py)** | Full comprehensive workflow demonstration |
| **[simple_cluster.py](examples/simple_cluster.py)** | Basic cluster deployment |
| **[workflow_orchestration.py](examples/workflow_orchestration.py)** | Workflow creation and execution |
| **[skill_evolution.py](examples/skill_evolution.py)** | Skill evolution and lineage |

### Quick Run Examples

```bash
# Run skill management example
python examples/skill_management.py

# Run complete example
python examples/complete_example.py

# Run workflow example
python examples/workflow_orchestration.py

# View CLI usage examples
bash examples/cli_usage.sh
```

### Example Skills

BaGuaLu includes example skills in [`bagualu/skills/examples/`](bagualu/skills/examples/):

- **data-analysis** - Data processing and analysis
- **code-review** - Code quality review
- **test-generator** - Test generation and execution

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file.

---

## 🙏 Acknowledgments

BaGuaLu is inspired by and incorporates design patterns from:

- **OpenLaoKe** - Multi-provider configuration system
- **OpenSpace** - Self-evolving skill system
- **OpenHarness** - Tool and plugin architecture

Special thanks to all contributors and the open-source community!

---

<div align="center">

**八卦炉 - 锻造智能，炼化知识**

**Made with ❤️ by the BaGuaLu Community**

</div>