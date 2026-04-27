# Workflow

## 任务分层

### 小任务

适合：

- 小 bug
- 单文件或少量文件改动
- 小范围补测试

建议链路：

`orchestrator -> planner -> implementer -> reviewer`

### 中任务

适合：

- 多文件改动
- 需要先摸清调用链
- 需要核对文档或外部依赖

建议链路：

`orchestrator -> planner -> explorer + docs_researcher -> implementer -> reviewer`

### 大任务

适合：

- 跨模块改造
- 大功能交付
- PR 审查
- 发布前把关

建议链路：

`orchestrator -> planner -> explorer + docs_researcher -> implementer -> reviewer -> release_guard -> CI`

## 标准执行顺序

1. `orchestrator` 读取任务、仓库规则、现有技能和外部上下文。
2. `planner` 输出不超过 5 步计划，并标出可能的写入文件。
3. `explorer` 与 `docs_researcher` 并行补上下文。
4. `orchestrator` 汇总后确认范围、风险和下一步。
5. `implementer` 改代码并运行最小必要验证。
6. `reviewer` 检查实现质量。
7. `release_guard` 检查是否满足 PR / CI / 发布条件。
8. 推进到 PR、Cloud task 或 CI。

## 并行原则

- 让 `explorer` 和 `docs_researcher` 并行，而不是和 `implementer` 抢写入权
- 避免多个可写 agent 同时改同一片区域
- 如果确实要并行实现，必须保证写入集互不重叠
