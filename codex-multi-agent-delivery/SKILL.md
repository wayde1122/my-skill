---
name: codex-multi-agent-delivery
description: 编排 Codex 的多 agent 自动化编码与交付流程，结合 AGENTS.md、.codex/config.toml、hooks、skills、MCP、CI 和 subagents，把复杂任务拆成 orchestrator、planner、explorer、docs_researcher、implementer、reviewer、release_guard 等角色协作。当用户需要设计或执行多 agent coding workflow、复杂功能开发、跨文件改动、PR 审查、发布前把关、把单 agent 任务升级为可控多 agent 流水线，或初始化当前仓库以接入这套工作流时使用。
---

# Codex Multi-Agent Delivery

把复杂编码任务组织成可控的多 agent 交付流程。先统一规则和验证，再决定哪些工作适合并行分派。

## 快速判断

优先判断是否真的需要多 agent：

- 小任务：单文件、小 bug、小范围补测试，直接走 `implementer -> reviewer`
- 中任务：多文件改动、需要先摸清调用链，加入 `planner` 和 `explorer`
- 大任务：跨模块改造、PR 审查、发布前检查，再加入 `docs_researcher` 和 `release_guard`

如果当前环境不支持 subagents，就压缩成：

`planner -> implementer -> reviewer`

如果目标仓库还没有这套工作流的基础文件，先运行初始化脚本：

```bash
python scripts/add_current_repo.py
```

## 先加载底座

开始前先确认这几个约束是否存在：

- `AGENTS.md` 或等效项目规则
- `.codex/config.toml`
- 统一的 `lint / test / build` 命令
- `hooks`、`CI`、`MCP` 中与任务直接相关的部分

如果这些基础约束缺失，不要直接进入“多 agent 并发改代码”。先指出缺口，并给出最小可执行方案。

优先使用仓库内的初始化脚本一次性补齐 Codex 侧骨架：

```bash
python scripts/add_current_repo.py --target <repo-path>
```

这个脚本默认生成：

- `AGENTS.md`
- `.codex/config.toml`
- `.codex/agents/*.toml`

它默认不覆盖现有文件；需要覆盖时显式传 `--force`。

详细约束见：

- [references/permissions.md](references/permissions.md)
- [references/mcp-and-ci.md](references/mcp-and-ci.md)

## 标准角色

默认使用这些角色：

- `orchestrator`：主控，负责分派、汇总、重排任务
- `planner`：拆任务、定范围、排顺序
- `explorer`：只读扫描代码路径和影响面
- `docs_researcher`：查文档和外部系统
- `implementer`：改代码、跑命令、补测试
- `reviewer`：检查回归、安全、缺失测试
- `release_guard`：检查 PR、CI、发布条件

完整职责矩阵见 [references/role-map.md](references/role-map.md)。

## 执行顺序

按这个顺序组织工作：

1. 让 `planner` 先输出不超过 5 步的计划，并明确哪些文件可能被修改。
2. 让 `explorer` 和 `docs_researcher` 并行补上下文，但保持只读。
3. 让 `orchestrator` 汇总结果，确认任务范围没有跑偏。
4. 只把实现工作交给 `implementer`。
5. 让 `implementer` 在改动后运行最小必要验证。
6. 让 `reviewer` 检查真实风险，而不是做风格挑刺。
7. 让 `release_guard` 判断是否满足 PR / CI / 发布条件。

完整流程和任务分层见 [references/workflow.md](references/workflow.md)。

## 回流规则

严格使用下面这组回流规则：

- `implementer` 验证失败：留在实现回路内自修复
- `reviewer` 发现实现问题：直接回到 `implementer`
- `release_guard` 发现流程或风险问题：回到 `orchestrator`
- `CI` 失败：回到 `orchestrator`，再分派给 `implementer`

不要把所有失败都打回主控。只有范围变化、风险升级、需要重新决策时，才回到 `orchestrator`。

完整失败回路见 [references/failure-loops.md](references/failure-loops.md)。

## 权限规则

默认只让 `implementer` 拥有写权限，其他角色保持只读。

- `explorer`、`docs_researcher`、`reviewer`、`release_guard`：`read-only`
- `implementer`：`workspace-write`

如果高风险命令需要额外审批，保留给 `approval_policy`、`auto_review`、`hooks` 和人工确认处理。

## 输出要求

最终交付至少包含：

- 变更摘要
- 验证结果
- 剩余风险
- 如果被 reviewer 或 release_guard 拦回，说明拦回原因

## 附带脚本

这份 skill 附带一个确定性脚本，用于把当前仓库接入这套 Codex 工作流：

- `scripts/add_current_repo.py`

适用场景：

- 当前仓库还没有 `AGENTS.md`
- 当前仓库还没有 `.codex/config.toml`
- 想快速生成一套标准 `agents/*.toml`
- 想先把仓库变成“可供多 agent 编排”的状态，再开始交付

## 参考资料

按需读取，不要一次性全量加载：

- [references/role-map.md](references/role-map.md)：角色职责和权限矩阵
- [references/workflow.md](references/workflow.md)：小、中、大任务工作流
- [references/failure-loops.md](references/failure-loops.md)：失败回流规则
- [references/permissions.md](references/permissions.md)：sandbox、审批、写权限建议
- [references/mcp-and-ci.md](references/mcp-and-ci.md)：MCP、hooks、CI 的结合方式
