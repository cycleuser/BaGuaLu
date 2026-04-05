# BaGuaLu 节点系统

ComfyUI 和 n8n 风格的强大节点系统，支持完全自定义的工作流编排。

## 📦 节点分类

### 1️⃣ 输入节点 (Input)
| 节点 | 功能 | 配置项 |
|------|------|--------|
| 📝 Text Input | 文本输入 | 默认值、多行、占位符 |
| 📁 File Input | 文件读取 | 文件路径、编码 |
| 🔷 JSON Input | JSON 解析 | 默认 JSON、验证模式 |

### 2️⃣ 智能体节点 (Agent)
| 节点 | 功能 | 配置项 |
|------|------|--------|
| 🤖 Agent Executor | 执行任务 | provider、model、temperature、role、instruction |
| 👁️ Agent Supervisor | 质量审核 | quality_threshold、auto_approve、criteria |

### 3️⃣ 逻辑节点 (Logic)
| 节点 | 功能 | 配置项 |
|------|------|--------|
| 🔀 Condition | 条件分支 | operator、compare_value |
| 🔣 Switch | 多路分流 | cases、default_case |
| 🔗 Merge | 合并数据 | merge_mode (array/concatenate/combine) |

### 4️⃣ 数据节点 (Data)
| 节点 | 功能 | 配置项 |
|------|------|--------|
| ⚙️ Transform | 数据转换 | expression |
| 🔍 Filter | 过滤数组 | condition |
| 🗺️ Map | 映射转换 | transform |

### 5️⃣ 工具节点 (Utility)
| 节点 | 功能 | 配置项 |
|------|------|--------|
| ⏱️ Delay | 延迟执行 | delay_ms |
| 🔁 Loop | 循环迭代 | batch_size、parallel |
| ⚠️ Error Handler | 错误处理 | continue_on_error、error_message |

### 6️⃣ API 节点 (API)
| 节点 | 功能 | 配置项 |
|------|------|--------|
| 🌐 HTTP Request | HTTP 请求 | method、url、headers、timeout、body |

## 🎨 节点配置详解

### 条件节点 (Condition)

```json
{
  "type": "logic.condition",
  "properties": {
    "operator": "equals",  // 支持：equals, not_equals, greater, less, contains, starts_with, ends_with
    "compare_value": "expected_value"
  }
}
```

### Switch 节点 - 多路分流

```json
{
  "type": "logic.switch",
  "properties": {
    "cases": [
      {"value": "free", "label": "免费用户"},
      {"value": "premium", "label": "高级用户"}
    ],
    "default_case": "free"
  }
}
```

### Agent Executor - 智能体执行

```json
{
  "type": "agent.executor",
  "properties": {
    "provider": "ollama",
    "model": "llama2",
    "temperature": 0.7,
    "max_tokens": 2000,
    "role": "executor",
    "instruction": "分析代码并生成报告"
  }
}
```

## 📋 工作流样例

### 1. 智能代码审查
- 使用 File Input 读取代码
- 多个 Agent Executor 并行分析
- Agent Supervisor 质量审核
- Merge 合并结果

### 2. API 数据管道
- HTTP Request 获取数据
- Error Handler 处理异常
- Condition 状态检查
- Filter/Transform 数据处理
- Loop 批量处理
- Delay 速率限制

### 3. A/B 测试路由器
- Switch 多路分流
- 不同用户等级不同处理
- Condition 区域检查
- Transform 格式化
- Merge 统一输出

## 🔧 创建自定义节点

```python
from bagualu.workflow.nodes.base import BaseNode, NodeDefinition, NodeInput, NodeOutput

class MyCustomNode(BaseNode):
    definition = NodeDefinition(
        type="custom.my_node",
        category="Custom",
        title="My Node",
        description="Custom node description",
        inputs=[
            NodeInput(name="input1", type="string", required=True),
            NodeInput(name="input2", type="number", default=10),
        ],
        outputs=[
            NodeOutput(name="result", type="string"),
        ],
        properties={
            "custom_prop": {"type": "string", default: "value"}
        }
    )
    
    async def execute(self, context):
        input1 = self.get_input("input1")
        input2 = self.get_input("input2")
        custom = self.get_property("custom_prop")
        
        return {"result": f"Processed: {input1}"}

# 注册节点
from bagualu.workflow.nodes.base import get_node_registry
registry = get_node_registry()
registry.register_node(MyCustomNode)
```

## 🎯 最佳实践

1. **模块化设计**: 每个节点只做一件事
2. **明确输入输出**: 定义清晰的接口
3. **错误处理**: 使用 Error Handler 捕获异常
4. **可配置性**: 使用 properties 提供灵活性
5. **可测试性**: 节点应该易于单独测试

## 📖 进阶用法

### 表达式语法

Transform 节点支持 JavaScript 风格表达式：

```javascript
// 访问输入数据
input

// 对象操作
input.map(item => item.value)
input.filter(item => item.active)
input.reduce((acc, item) => acc + item.value, 0)

// 字符串操作
input.toUpperCase()
input.split(',').map(s => s.trim())

// 数学运算
Math.round(input * 100) / 100

// 条件表达式
input.value > 100 ? 'high' : 'low'
```

### 循环批处理

```json
{
  "type": "utility.loop",
  "properties": {
    "batch_size": 10,
    "parallel": true
  }
}
```

### 错误恢复策略

```json
{
  "type": "utility.error",
  "properties": {
    "continue_on_error": true,
    "error_message": "Custom error message",
    "retry_count": 3
  }
}
```

## 🔌 与外部系统集成

### 调用外部 API

```json
{
  "type": "api.http",
  "properties": {
    "method": "POST",
    "url": "https://api.example.com/webhook",
    "headers": {
      "Authorization": "Bearer ${API_KEY}",
      "Content-Type": "application/json"
    },
    "body": {
      "event": "workflow.completed",
      "data": "${input}"
    }
  }
}
```

### 数据库操作

使用 HTTP Request 节点连接数据库 API，或使用自定义节点。

## 📊 性能优化

1. **并行处理**: 使用 parallel 模式的 Loop 节点
2. **批处理**: 设置合适的 batch_size
3. **缓存**: 对重复计算使用缓存
4. **超时**: 设置合理的 timeout 值
5. **限流**: 使用 Delay 节点控制速率
