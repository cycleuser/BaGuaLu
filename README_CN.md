# BaGuaLu (八卦炉)

<div align="center">

**八卦炉 - 智能体编排平台，支持自我进化的智能体集群**

[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![PyPI](https://img.shields.io/badge/PyPI-0.1.0-orange.svg)](https://pypi.org/project/bagualu/)

**一键部署智能体集群 | 技能自我进化 | 多工作流编排**

[English](README.md) | 中文

</div>

---

## 🎯 什么是八卦炉？

**BaGuaLu（八卦炉）** 是一个强大的智能体编排平台，融合了 **OpenLaoKe**、**OpenSpace** 和 **OpenHarness** 的优秀设计理念，为开发者提供一站式的智能体部署、管理和进化解决方案。

### ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 🚀 **一键部署** | 单个智能体、智能体矩阵、集群的一键部署，支持多种角色 |
| 🧬 **自我进化** | 智能体和技能的自我进化能力（FIX、DERIVED、CAPTURED 三种模式） |
| 🔧 **多提供商支持** | 支持 Ollama、LMStudio、OpenAI、Claude、CodingPlan 等多种 LLM 提供商 |
| 📚 **技能系统** | 兼容 OpenCode/Claude Code 技能格式，支持按需加载和自动发现 |
| 🌐 **工作流编排** | 提供 Web 界面拖拽设计工作流，支持 DAG 执行引擎 |
| 🤝 **多智能体协调** | Supervisor、Scheduler、Executor 协同工作，实现复杂任务编排 |
| 🛡️ **权限管理** | 多级权限控制和钩子系统，确保执行安全 |
| 📊 **资源调度** | 智能资源分配和负载均衡，优化执行效率 |

---

## 🏗️ 系统架构

```
bagualu/
├── core/              # 核心编排系统
│   ├── bagualu_core.py    # 主核心类
│   ├── orchestrator.py    # 工作流编排器
│   └── resource_manager.py # 资源管理器
├── agents/            # 智能体系统
│   ├── base.py            # 基础智能体抽象
│   ├── executor.py        # 执行智能体
│   ├── supervisor.py      # 监工智能体
│   ├── scheduler.py       # 调度智能体
│   └── cluster.py         # 集群管理
├── skills/            # 技能系统（参考 OpenSpace）
│   ├── skill_engine.py    # 技能引擎
│   ├── evolver.py         # 自我进化引擎
│   ├── registry.py        # 技能注册表
│   └── store.py           # 持久化存储
├── config/            # 配置系统（参考 OpenLaoKe）
│   ├── config_manager.py  # 配置管理
│   ├── providers.py       # 多提供商配置
│   └── wizard.py          # 配置向导
├── workflow/          # 工作流系统
│   ├── workflow_engine.py # 工作流引擎
│   └── workflow_dag.py    # DAG 定义
├── tools/             # 工具系统（参考 OpenHarness）
│   └── base.py            # 工具基类
├── web/               # Web 界面
│   ├── api_server.py      # REST API 服务
│   └── workflow_ui.py     # 工作流 UI
└── entrypoints/       # 入口点
    └── cli.py             # CLI 命令行工具
```

---

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/cycleuser/BaGuaLu.git
cd BaGuaLu

# 使用 pip 安装
pip install -e .

# 或从 PyPI 安装
pip install bagualu
```

### 初始化配置

```bash
# 运行配置向导
bagualu --init
```

配置向导会引导你：
1. 选择 LLM 提供商（Ollama、OpenAI、Claude 等）
2. 输入 API Key（如需要）
3. 选择默认模型
4. 设置系统参数

### 部署智能体

```bash
# 部署单个智能体
bagualu deploy my-agent --role executor --provider ollama --model llama2

# 或使用交互模式
bagualu
> deploy
智能体名称: my-agent
角色: executor
提供商: ollama
模型: llama2
```

### 执行工作流

```bash
# 创建工作流文件 workflow.json
{
  "name": "my-workflow",
  "nodes": [
    {
      "id": "analyze",
      "role": "executor",
      "instruction": "分析代码库结构"
    },
    {
      "id": "review",
      "role": "supervisor", 
      "instruction": "审查分析结果",
      "dependencies": ["analyze"]
    }
  ],
  "edges": [
    {"from": "analyze", "to": "review"}
  ]
}

# 执行工作流
bagualu run workflow.json
```

---

## 🔧 配置说明

### 多提供商配置

BaGuaLu 支持多种 LLM 提供商，配置文件位于 `~/.bagualu/config.yaml`：

```yaml
providers:
  # 本地提供商
  ollama:
    base_url: http://localhost:11434
    model: llama2
    enabled: true
  
  lmstudio:
    base_url: http://localhost:1234/v1
    model: local-model
    enabled: true
  
  # 云端提供商
  openai:
    api_key: sk-xxx
    model: gpt-4
    enabled: true
  
  anthropic:
    api_key: sk-xxx
    model: claude-3-5-sonnet-20241022
    enabled: true
  
  # Coding Plan（支持多个 API Key）
  coding_plan_1:
    api_key: sk-xxx
    model: default
    enabled: true
  
  coding_plan_2:
    api_key: sk-yyy
    model: default
    enabled: true

# 当前活跃的提供商
active_provider: ollama

# 系统设置
settings:
  max_concurrent_agents: 10     # 最大并发智能体数
  evolution_enabled: true        # 启用技能进化
  quality_threshold: 0.8        # 质量阈值
```

### 环境变量

也可以通过环境变量配置：

```bash
# OpenAI
export OPENAI_API_KEY=sk-xxx

# Anthropic
export ANTHROPIC_API_KEY=sk-xxx

# 自定义提供商
export BAGUALU_PROVIDER=ollama
export BAGUALU_MODEL=llama2
```

---

## 🧬 自我进化系统

BaGuaLu 的技能自我进化系统参考了 OpenSpace 的设计，支持三种进化模式：

### 进化类型

| 类型 | 描述 | 使用场景 |
|------|------|----------|
| **FIX** | 修复破损或过时的技能指令 | 技能执行失败率过高时 |
| **DERIVED** | 从现有技能创建增强版本 | 需要扩展或优化技能时 |
| **CAPTURED** | 从成功执行中捕获新模式 | 发现新的成功模式时 |

### 触发进化

```bash
# CLI 方式
bagualu evolve skill-name

# Python API 方式
from bagualu import BaGuaLuCore

async def evolve():
    core = BaGuaLuCore()
    await core.initialize()
    
    # 自动进化
    evolved = await core.evolve_skill("my-skill", evolution_type="auto")
    
    # 指定进化类型
    fixed = await core.evolve_skill("my-skill", evolution_type="fix")
    derived = await core.evolve_skill("my-skill", evolution_type="derived")
```

### 进化触发器

进化可以由以下事件自动触发：

1. **执行后分析** - 每次技能执行后自动评估
2. **工具降级检测** - 工具成功率下降时触发
3. **指标监控** - 定期检查技能健康指标

---

## 🤝 多智能体协调

### 智能体角色

| 角色 | 职责 | 关键能力 |
|------|------|----------|
| **Executor** | 执行具体任务 | 技能执行、任务处理、错误恢复 |
| **Supervisor** | 监督和质量控制 | 输出验证、质量评估、反馈生成 |
| **Scheduler** | 任务调度和资源分配 | 优先级管理、负载均衡、死线处理 |
| **Coordinator** | 多智能体协调 | 通信管理、冲突解决、协同优化 |

### 部署集群

```python
import asyncio
from bagualu import BaGuaLuCore

async def main():
    core = BaGuaLuCore()
    await core.initialize()
    
    # 定义集群配置
    cluster_config = {
        "name": "my-cluster",
        "agents": [
            {"name": "executor1", "role": "executor", "skills": ["code-analysis"]},
            {"name": "executor2", "role": "executor", "skills": ["testing"]},
            {"name": "supervisor1", "role": "supervisor"},
            {"name": "scheduler1", "role": "scheduler"},
        ],
        "connections": [
            {"from": "executor1", "to": "supervisor1"},
            {"from": "executor2", "to": "supervisor1"},
        ]
    }
    
    # 部署集群
    agent_ids = await core.deploy_cluster(cluster_config)
    print(f"已部署 {len(agent_ids)} 个智能体")

asyncio.run(main())
```

---

## 🌐 Web 界面

### 启动 Web 服务器

```bash
# 启动 API 服务器
bagualu server --host 0.0.0.0 --port 8000
```

### REST API 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/agents` | POST | 部署智能体 |
| `/agents` | GET | 列出所有智能体 |
| `/workflows` | POST | 创建工作流 |
| `/workflows/{id}/execute` | POST | 执行工作流 |
| `/skills` | GET | 列出所有技能 |
| `/skills/{name}/evolve` | POST | 触发技能进化 |

### 使用示例

```bash
# 部署智能体
curl -X POST http://localhost:8000/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-agent",
    "role": "executor",
    "provider": "ollama",
    "model": "llama2"
  }'

# 执行工作流
curl -X POST http://localhost:8000/workflows/my-workflow/execute \
  -H "Content-Type: application/json" \
  -d '{"target": "analyze"}'
```

---

## 📚 技能系统

### 加载技能

```python
from pathlib import Path
from bagualu import BaGuaLuCore

async def load_skills():
    core = BaGuaLuCore()
    await core.initialize()
    
    # 从 OpenCode/Claude Code 技能目录加载
    await core.skills.import_skill_from_opencode(
        Path("~/.config/opencode/skills/my-skill")
    )
    
    # 列出所有技能
    skills = await core.skills.get_all_skills()
    for skill in skills:
        print(f"技能: {skill['name']}")
```

### 创建自定义技能

在 `~/.bagualu/skills/` 目录下创建 Markdown 文件：

```markdown
# ~/.bagualu/skills/my-skill.md

# 我的自定义技能

## 何时使用
当用户询问关于 [特定领域] 的问题时使用此技能。

## 工作流程
1. 第一步：分析需求
2. 第二步：收集信息
3. 第三步：生成输出
4. 第四步：验证结果

## 触发器
- 关键词 1
- 关键词 2
- 特定命令

## 示例
用户：帮我分析这个代码
助手：使用 my-skill 技能进行分析...
```

### 技能格式

技能文件支持以下部分：

- **标题** - 技能名称
- **描述** - 技能说明
- **何时使用** - 使用场景
- **工作流程** - 执行步骤
- **触发器** - 关键词列表
- **参数** - 输入参数定义
- **示例** - 使用示例

---

## 🔌 与其他项目集成

BaGuaLu 兼容以下项目的技能和插件：

- ✅ **OpenCode** 技能格式
- ✅ **Claude Code** 技能格式
- ✅ **OpenLaoKe** 配置系统
- ✅ **OpenSpace** 进化模式
- ✅ **OpenHarness** 工具系统

### 技能兼容性

```bash
# 复制 OpenCode 技能到 BaGuaLu
cp -r ~/.config/opencode/skills/* ~/.bagualu/skills/

# 复制 Claude Code 技能到 BaGuaLu
cp -r ~/.claude/skills/* ~/.bagualu/skills/
```

---

## 📊 示例代码

查看 [`examples/`](examples/) 目录获取完整示例：

### 示例列表

1. **simple_cluster.py** - 部署简单集群
2. **workflow_orchestration.py** - 工作流编排
3. **skill_evolution.py** - 技能进化演示

### 运行示例

```bash
# 运行集群示例
python examples/simple_cluster.py

# 运行工作流示例
python examples/workflow_orchestration.py

# 运行进化示例
python examples/skill_evolution.py
```

---

## 🛠️ 开发指南

### 安装开发依赖

```bash
pip install -e ".[dev]"
```

### 代码检查

```bash
# Ruff 检查
ruff check .

# Ruff 格式化
ruff format .

# 类型检查
mypy bagualu
```

### 运行测试

```bash
# 运行所有测试
pytest

# 带覆盖率
pytest --cov

# 详细输出
pytest -v
```

### 构建和发布

```bash
# 构建
python build.sh          # Linux/Mac
build.bat                # Windows
python publish.py build  # Python 脚本

# 发布到 PyPI
./upload_pypi.sh         # Linux/Mac
upload_pypi.bat          # Windows
python publish.py release # Python 脚本
```

---

## 🤝 贡献指南

我们欢迎各种形式的贡献！

### 贡献方式

- 📝 改进文档
- 🐛 报告 Bug
- ✨ 提出新功能
- 🔧 提交代码

### 开发流程

1. Fork 仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

详见 [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

---

## 🙏 致谢

BaGuaLu 的设计受到以下项目的启发：

- **OpenLaoKe** - 多提供商配置系统
- **OpenSpace** - 自我进化技能系统
- **OpenHarness** - 工具和插件架构

特别感谢所有贡献者和开源社区！

---

## 📞 联系方式

- **问题反馈**: [GitHub Issues](https://github.com/cycleuser/BaGuaLu/issues)
- **功能建议**: [GitHub Discussions](https://github.com/cycleuser/BaGuaLu/discussions)

---

<div align="center">

**八卦炉 - 锻造智能，炼化知识**

**用 ❤️ 打造 | 由 BaGuaLu 社区维护**

[![Star History Chart](https://api.star-history.com/svg?repos=cycleuser/BaGuaLu&type=Date)](https://star-history.com/#cycleuser/BaGuaLu&Date)

</div>