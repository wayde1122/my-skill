# Role Map

## 标准角色矩阵

| Agent | 核心职责 | 是否写代码 | 默认权限 |
|------|----------|-----------|---------|
| `orchestrator` | 主控调度、汇总结果、决定返工或推进 | 否，尽量少写 | `read-only` 或继承主会话 |
| `planner` | 拆任务、定范围、排顺序 | 否 | `read-only` |
| `explorer` | 读代码、查调用链、找受影响文件 | 否 | `read-only` |
| `docs_researcher` | 查文档、MCP、外部系统行为 | 否 | `read-only` |
| `implementer` | 改代码、跑命令、补测试 | 是 | `workspace-write` |
| `reviewer` | 查回归、安全、缺失测试 | 否 | `read-only` |
| `release_guard` | 查 PR 条件、CI、发布风险 | 否 | `read-only` |

## 角色边界

### orchestrator

- 负责决定是否启用多 agent
- 负责决定是否重新规划
- 不要把它当成主要实现者

### planner

- 负责把任务压缩成可执行步骤
- 必须标出受影响模块和潜在风险
- 不负责落代码

### explorer

- 只读分析真实调用路径
- 适合先并行扫仓库
- 不负责提出大规模重构

### docs_researcher

- 通过官方文档或 MCP 核对行为
- 用于确认 API、框架版本、外部系统约束
- 不做代码改动

### implementer

- 是唯一默认拥有写权限的 agent
- 负责最小正确改动
- 负责在本地验证失败时继续修复

### reviewer

- 先看行为正确性，再看测试缺口，再看安全风险
- 不做风格主导型 review
- 发现实现缺陷时直接回 `implementer`

### release_guard

- 检查是否达到 PR / merge / release 条件
- 关注 CI、发布风险、兼容性和高风险模块
- 发现需要重新决策的问题时回 `orchestrator`
