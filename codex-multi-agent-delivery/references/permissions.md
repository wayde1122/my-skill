# Permissions

## 默认权限建议

| Agent | 建议权限 |
|------|---------|
| `orchestrator` | `read-only` 或继承主会话 |
| `planner` | `read-only` |
| `explorer` | `read-only` |
| `docs_researcher` | `read-only` |
| `implementer` | `workspace-write` |
| `reviewer` | `read-only` |
| `release_guard` | `read-only` |

## 权限原则

1. 默认只让一个 agent 写代码。
2. 大多数 agent 只负责读、查、审、判定。
3. 高风险动作继续交给 sandbox、approval、hooks 和人工确认。

## 推荐配置方向

- `approval_policy = "on-request"`
- `approvals_reviewer = "auto_review"`
- `sandbox_mode = "workspace-write"`

如果仓库可信且任务明确，再逐步放宽。

## 什么时候不要上多写入 agent

- 仓库没有稳定测试
- 任务边界还不清楚
- 改动集中在同一组文件
- 你无法清楚界定写入所有权
