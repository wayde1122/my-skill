# Failure Loops

## 失败回流规则

### 规划阶段

- `planner` 发现需求不清晰：回 `orchestrator`
- `explorer` 发现影响面超出预期：回 `planner`
- `docs_researcher` 发现文档假设错误：回 `planner` 或 `implementer`

### 实现阶段

- `implementer` 跑 `lint / test / build` 失败：留在实现回路内自修复
- `implementer` 发现需要扩大改动范围：回 `orchestrator`

### 审查阶段

- `reviewer` 发现回归、实现缺陷、边界条件问题、缺失测试：直接回 `implementer`
- `reviewer` 发现问题已经超出原任务边界：回 `orchestrator`

### 发布和交付阶段

- `release_guard` 发现 PR 条件不满足：回 `orchestrator`
- `release_guard` 发现需要人工确认的高风险项：回 `orchestrator`
- `CI` 失败：回 `orchestrator`，再由其分派给 `implementer`

## 一个关键原则

不要把所有失败都打回主控。

更高效的做法是：

- 实现类问题：回 `implementer`
- 决策类问题：回 `orchestrator`
