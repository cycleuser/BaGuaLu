# AGENTS.md - BaGuaLu 开发指南

BaGuaLu（八卦炉）是一个智能体编排平台，用于部署、管理和进化智能体集群。

## 项目概述

### 目标
- 一键部署智能体集群（单个、矩阵、集群）
- 智能体和技能的自我进化能力
- 多提供商支持（Ollama、LMStudio、OpenAI、Claude、CodingPlan等）
- 工作流编排和Web界面设计
- 兼容OpenCode/Claude Code技能系统

### 参考项目
参考以下项目的设计：
- `/Users/fred/Documents/GitHub/cycleuser/OpenLaoKe` - 多提供商配置系统
- `/Users/fred/Documents/GitHub/Others/OpenSpace` - 自我进化技能系统
- `/Users/fred/Documents/GitHub/Others/OpenHarness` - 工具和插件架构

## 开发命令

### 安装
```bash
pip install -e ".[dev]"      # 安装开发依赖
pip install -e ".[dev,web]"  # 安装所有依赖（包括Web）
```

### 代码检查与格式化
```bash
ruff check .                 # 代码检查
ruff check . --fix           # 自动修复
ruff format .                # 格式化代码
```

### 类型检查
```bash
mypy                         # 运行mypy
mypy bagualu/core/           # 检查特定目录
```

### 测试
```bash
pytest                       # 完整测试套件
pytest --cov                 # 带覆盖率
pytest tests/test_core.py    # 单个文件
pytest -v                    # 详细输出
pytest -x                    # 首次失败时停止
```

### 构建
```bash
python build.sh              # Linux/Mac
build.bat                    # Windows
python publish.py build      # 使用Python脚本
```

### 发布到PyPI
```bash
./upload_pypi.sh             # Linux/Mac
upload_pypi.bat              # Windows
python publish.py release    # 使用Python脚本
```

## 代码风格

### 导入
- 每个模块顶部使用 `from __future__ import annotations`
- 导入顺序：标准库 → 第三方 → 本地（由 ruff `I` 规则强制）
- 使用 `TYPE_CHECKING` 守卫避免循环导入
- 使用 `bagualu.` 前缀的绝对导入

### 类型注解
- 所有函数签名必须有完整类型注解
- 使用 `|` 表示联合类型（如 `str | None`）
- 数据结构使用 `dataclass`
- 工具输入模式使用 `pydantic BaseModel`
- 枚举使用 `Enum`

### 命名约定
- 类名：`PascalCase`（如 `AgentCluster`, `SkillEngine`）
- 函数/方法：`snake_case`（如 `deploy_agent`, `evolve_skill`）
- 常量：`UPPER_SNAKE_CASE`（如 `MAX_AGENTS`, `DEFAULT_TIMEOUT`）
- 私有属性：前导下划线（如 `_agents`, `_config`）

### 格式化
- 行长度：100字符
- Ruff规则：E, F, I, N, W, UP, B, SIM
- mypy：非严格模式

### 错误处理
- 返回包含 `success` 字段的字典
- 记录错误，不要让程序崩溃
- 使用 `try/except` 捕获异常并记录

### 异步模式
- 所有IO操作使用 `async def`
- 测试使用 `pytest-asyncio`
- 使用 `asyncio` 进行异步操作

**重要：不要添加任何注释，除非用户明确要求。**

## 架构

```
bagualu/
├── core/                      # 核心编排系统
│   ├── bagualu_core.py        # 主核心类
│   ├── orchestrator.py        # 工作流编排器
│   └── resource_manager.py    # 资源管理
├── agents/                    # 智能体系统
│   ├── base.py                # 基础智能体抽象
│   ├── executor.py            # 执行智能体
│   ├── supervisor.py          # 监工智能体
│   ├── scheduler.py           # 调度智能体
│   └── cluster.py             # 集群管理
├── skills/                    # 技能系统
│   ├── skill_engine.py        # 技能引擎
│   ├── evolver.py             # 自我进化引擎
│   ├── registry.py            # 技能注册表
│   └── store.py               # 持久化存储
├── config/                    # 配置系统
│   ├── config_manager.py      # 配置管理
│   ├── providers.py           # 多提供商配置
│   └── wizard.py              # 配置向导
├── workflow/                  # 工作流系统
│   ├── workflow_engine.py     # 工作流引擎
│   └── workflow_dag.py        # DAG定义
├── tools/                     # 工具系统
│   └── base.py                # 工具基类
├── web/                       # Web界面
│   ├── api_server.py          # REST API
│   └── workflow_ui.py         # 工作流UI
└── entrypoints/               # 入口点
    └── cli.py                 # CLI入口
```

## 智能体角色

| 角色 | 职责 |
|------|------|
| **Executor** | 执行具体任务，使用技能 |
| **Supervisor** | 监督质量，处理异常 |
| **Scheduler** | 任务调度，资源分配 |
| **Coordinator** | 多智能体协调 |

## 技能进化

三种进化类型：
- **FIX**: 修复破损或过时的技能
- **DERIVED**: 从现有技能创建增强版本
- **CAPTURED**: 从成功执行中捕获新模式

## 配置

配置文件位于 `~/.bagualu/config.yaml`：
- 多提供商配置（Ollama, OpenAI, Claude等）
- API Key管理
- 集群设置

## 测试

所有测试位于 `tests/` 目录：
- `test_core.py` - 核心功能测试
- 使用 `pytest` 运行

## 示例

所有示例位于 `examples/` 目录：
- `simple_cluster.py` - 部署简单集群
- `workflow_orchestration.py` - 工作流编排
- `skill_evolution.py` - 技能进化

## 发布流程

1. 更新版本号（自动）
2. 运行测试：`pytest`
3. 代码检查：`ruff check .`
4. 构建：`python publish.py build`
5. 上传：`python publish.py release`

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License - 详见 LICENSE 文件