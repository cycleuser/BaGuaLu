# BaGuaLu 默认样例

本目录包含可直接加载的默认样例，包括工作流、智能体配置和技能。

## 📋 工作流样例 (`workflows/`)

包含 4 个预定义的工作流样例，可以直接在 Web UI 中加载使用：

### 1. 代码审查工作流 (`code-review.json`)
**用途**: 自动代码审查和分析  
**节点**: 4 个 (分析代码 → 审查质量 → 生成测试 → 创建报告)  
**适合场景**: 
- Pull Request 自动审查
- 代码质量检查
- 测试覆盖率提升

**工作流结构**:
```
analyze-code → review-quality → create-report
            ↘ generate-tests ↗
```

### 2. 数据分析工作流 (`data-pipeline.json`)
**用途**: 数据处理和分析管道  
**节点**: 5 个 (提取 → 清洗 → 分析 → 验证 → 报告)  
**适合场景**:
- ETL 数据处理
- 业务数据分析
- 自动化报告生成

**工作流结构**:
```
extract-data → clean-data → analyze-data → generate-report
                              ↓              ↑
                        validate-results → ↗
```

### 3. 测试生成工作流 (`test-generation.json`)
**用途**: 自动化测试生成和执行  
**节点**: 6 个 (扫描 → 分析 → 识别边界 → 生成 → 执行 → 修复)  
**适合场景**:
- 单元测试自动生成
- 测试覆盖率提升
- 持续集成测试

**工作流结构**:
```
scan-codebase → analyze-functions → generate-unit-tests → run-tests → fix-failing-tests
                     ↓                                        ↑
               identify-edge-cases ↘________________________↗
```

### 4. 多智能体协作工作流 (`multi-agent-collaboration.json`)
**用途**: 展示多智能体协同完成复杂任务  
**节点**: 6 个 (分解 → 研究/实现/测试 → 监督 → 整合)  
**适合场景**:
- 复杂项目开发
- 多角色协作任务
- 大型代码重构

**工作流结构**:
```
                  researcher ↘
task-decomposer → implementer → quality-supervisor → integrator
                  ↘ tester ↗
```

## 🎨 如何在 Web UI 中使用工作流样例

### 方法 1: 通过 Web UI 加载（推荐）

1. 启动服务器:
```bash
bagualu server
```

2. 打开浏览器访问: http://localhost:8000

3. 点击 **"Workflow Designer"** 标签

4. 在左侧面板找到 **"📋 Load Example"** 部分

5. 点击任意样例的 **"Load Example"** 按钮

6. 工作流将自动加载到画布中，可以：
   - **拖动节点** 调整位置
   - **双击节点** 编辑说明
   - **连接节点** 创建依赖关系
   - **点击保存** 存储工作流

### 方法 2: 通过 API 加载

```bash
# 列出所有可用样例
curl http://localhost:8000/workflows/examples

# 加载特定样例
curl -X POST http://localhost:8000/workflows/load-example/code-review
```

### 方法 3: 使用 CLI

```bash
# 查看样例
bagualu workflow list-examples

# 加载样例
bagualu workflow load code-review
```

## 🤖 智能体配置样例

创建智能体时可以使用以下配置：

### Executor Agent (执行智能体)
```json
{
  "name": "code-analyzer",
  "role": "executor",
  "provider": "ollama",
  "model": "llama2",
  "skills": ["code-analysis", "test-generator"]
}
```

### Supervisor Agent (监工智能体)
```json
{
  "name": "quality-supervisor",
  "role": "supervisor",
  "provider": "openai",
  "model": "gpt-4",
  "skills": ["code-review"]
}
```

### Scheduler Agent (调度智能体)
```json
{
  "name": "task-scheduler",
  "role": "scheduler",
  "provider": "ollama",
  "model": "llama2"
}
```

## 📚 技能样例 (`bagualu/skills/examples/`)

包含 3 个示例技能：

1. **data-analysis** - 数据分析技能
   - 支持 Excel、CSV、JSON 文件
   - DuckDB SQL 查询
   - 统计分析和导出

2. **code-review** - 代码审查技能
   - 代码质量检查
   - 最佳实践建议
   - 安全漏洞检测

3. **test-generator** - 测试生成技能
   - 单元测试生成
   - 边界案例识别
   - 测试执行和修复

## 🎯 快速开始

1. **启动服务器**:
```bash
bagualu server --host 0.0.0.0 --port 8000
```

2. **访问 Web UI**: http://localhost:8000

3. **加载样例工作流**:
   - 点击 "Workflow Designer"
   - 选择左侧的样例
   - 点击 "Load Example"

4. **编辑和运行**:
   - 拖动节点调整布局
   - 双击节点编辑指令
   - 点击 "Execute" 运行

5. **保存工作流**:
   - 点击 "Save Workflow"
   - 输入名称保存

## 📤 导出和导入工作流

### 导出工作流
在 Workflow Designer 中点击 **"Export"** 按钮，下载 JSON 文件。

### 导入工作流
在 Workflow Designer 中点击 **"Import"** 按钮，选择之前导出的 JSON 文件。

## 🔧 自定义工作流

可以基于样例创建自定义工作流：

1. 加载一个接近需求的样例
2. 修改节点配置
3. 添加/删除节点
4. 调整连接关系
5. 保存为新工作流

## 💡 最佳实践

1. **从简单开始**: 先使用单节点工作流测试
2. **渐进复杂**: 逐步添加节点和依赖
3. **明确指令**: 每个节点的 instruction 要清晰具体
4. **合理分工**: 不同类型任务用不同角色
5. **测试验证**: 执行前检查连接关系

## 🐛 故障排查

### 问题：样例加载失败
**解决**: 检查服务器日志，确保 `examples/workflows/` 目录存在

### 问题：节点无法拖动
**解决**: 确保浏览器支持 HTML5 Drag & Drop API

### 问题：工作流执行失败
**解决**: 检查节点依赖关系，确保没有循环依赖

## 📖 更多资源

- [完整文档](../README.md)
- [示例代码](../examples/)
- [API 文档](http://localhost:8000/docs)
