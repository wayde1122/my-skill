# My Skills

一组自定义的 [Cursor](https://www.cursor.com/) / [Claude Code](https://code.claude.com/) / Codex Agent Skills，用于扩展 AI 的专业能力。

## 包含的 Skills

| Skill | 说明 |
|-------|------|
| [github-knowledge-base](./github-knowledge-base/) | 通过 gh CLI 搜索 GitHub 仓库/Issues/PRs，并管理本地代码知识库 |
| [skill-validator](./skill-validator/) | 检查 Skill 是否符合 Anthropic 官方最佳实践，自动化结构检查 + AI 内容审查 |
| [formatting-nanobot-output](./formatting-nanobot-output/) | 美化 nanobot 回复输出格式，使用结构化排版和符号标记，适配 QQ/Telegram 等平台 |
| [codex-multi-agent-delivery](./codex-multi-agent-delivery/) | 编排 Codex 多 Agent 自动化编码、审查、PR 与交付工作流 |

## 安装

### Cursor

将 Skill 目录复制到个人 Skills 目录：

```bash
# 克隆仓库
git clone https://github.com/wayde1122/my-skill.git

# 复制到 Cursor Skills 目录
cp -r my-skill/github-knowledge-base ~/.cursor/skills/
cp -r my-skill/skill-validator ~/.cursor/skills/
cp -r my-skill/formatting-nanobot-output ~/.cursor/skills/
```

### Claude Code

```bash
cp -r my-skill/github-knowledge-base ~/.claude/skills/
cp -r my-skill/skill-validator ~/.claude/skills/
cp -r my-skill/formatting-nanobot-output ~/.claude/skills/
```

### Codex

```bash
cp -r my-skill/codex-multi-agent-delivery ~/.codex/skills/
```

安装后无需额外配置，Agent 会在对话中自动发现并使用。

---

## Skill 详情

### github-knowledge-base

通过 `gh` CLI 搜索 GitHub 资源，并管理本地代码知识库。

**触发方式**：当你要求搜索 GitHub 仓库、查找 Issues/PRs、克隆项目到知识库时自动触发。

**主要功能**：
- 搜索 GitHub 仓库、Issues、Pull Requests
- 克隆仓库到本地知识库目录
- 维护 CLAUDE.md 项目目录文件

**前置要求**：[GitHub CLI (gh)](https://cli.github.com/) 已安装并登录。

### skill-validator

检查任意 Skill 是否符合 [Anthropic 官方最佳实践](https://platform.claude.com/docs/zh-CN/agents-and-tools/agent-skills/best-practices)。

**触发方式**：当你要求"检查/验证/审查某个 Skill"时自动触发。

**验证流程**：

1. **脚本自动检查**（19 项规则）

   ```bash
   python scripts/validate_skill.py <skill目录路径>

   # JSON 输出
   python scripts/validate_skill.py <skill目录路径> --format json
   ```

   检查项包括：

   | 类别 | 检查项 |
   |------|--------|
   | 结构规范 | SKILL.md 存在性、name/description 格式、正文行数、多余文件、Windows 路径、引用深度等 (15 项) |
   | 信息安全 | 硬编码凭据、危险命令、HTTP 明文 URL、敏感路径引用 (4 项) |

2. **AI 内容审查**（8 项语义检查）

   | 检查项 | 说明 |
   |--------|------|
   | A. description 质量 | 第三人称、WHAT + WHEN、触发关键词 |
   | B. 内容简洁性 | 不含通用知识、优先示例 |
   | C. 术语一致性 | 不混用同义词 |
   | D. 时间敏感信息 | 无过期日期性表述 |
   | E. 示例质量 | 具体输入/输出对 |
   | F. 工作流与反馈循环 | 步骤分解、验证环节 |
   | G. 信息安全 | 凭据变形、输入注入、路径遍历 |
   | H. 权限最小化 | 最小权限原则 |

3. **输出分级报告**

   综合两部分结果，按三级分类输出：通过 / 建议改进 / 必须修复。

**前置要求**：Python 3.8+（无第三方依赖）。

### formatting-nanobot-output

美化 [nanobot](https://github.com/HKUDS/nanobot) 的回复输出格式，适配 QQ、Telegram、Discord 等聊天平台。

**触发方式**：当需要让 nanobot 回复更美观、更易读时自动触发。

**主要功能**：
- 使用全角符号（`【】`、`▎`、`◆`）替代 Markdown 标题，兼容不渲染 Markdown 的平台
- 提供 5 种回复模板：问答、步骤、对比、代码、摘要
- 按平台特性适配输出格式（QQ 纯文本符号 / Telegram 混合 / Discord 完整 Markdown）

**部署到 nanobot**：
```bash
cp SKILL.md ~/.nanobot/skills/pretty-output.md
pkill -f nanobot && nanobot gateway
```

**前置要求**：已安装并运行 [nanobot](https://github.com/HKUDS/nanobot)。

### codex-multi-agent-delivery

把 Codex 的多 Agent 协作和自动化底座结合起来，形成一套可控的编码交付工作流。

**触发方式**：当你要求设计或执行多 Agent coding workflow、复杂功能开发、跨文件改动、PR 审查、发布前把关、把单 Agent 任务升级为多 Agent 流水线、或初始化当前仓库以接入这套流程时自动触发。

**主要功能**：
- 统一 `orchestrator / planner / explorer / docs_researcher / implementer / reviewer / release_guard` 的角色分工
- 规定 `reviewer -> implementer`、`release_guard -> orchestrator` 等标准回流路径
- 把 `AGENTS.md`、`.codex/config.toml`、hooks、MCP、CI 纳入同一条交付链路
- 提供脚本为当前仓库生成最小可用的 Codex 多 Agent 骨架

**适用前提**：仓库最好已经具备统一的验证命令和基础项目规则。

**初始化当前仓库**：

如果你想把“当前仓库”快速接入这套工作流，可以运行：

```bash
# 在目标仓库目录中执行
python ~/.codex/skills/codex-multi-agent-delivery/scripts/add_current_repo.py
```

或者直接从本仓库源码运行：

```bash
python my-skill/codex-multi-agent-delivery/scripts/add_current_repo.py --target /path/to/repo
```

脚本默认会添加：

- `AGENTS.md`
- `.codex/config.toml`
- `.codex/agents/planner.toml`
- `.codex/agents/explorer.toml`
- `.codex/agents/docs-researcher.toml`
- `.codex/agents/implementer.toml`
- `.codex/agents/reviewer.toml`
- `.codex/agents/release-guard.toml`

默认不会覆盖已有文件。需要覆盖时显式传入：

```bash
python ~/.codex/skills/codex-multi-agent-delivery/scripts/add_current_repo.py --force
```

如果你还想同时放一个 hooks 占位模板：

```bash
python ~/.codex/skills/codex-multi-agent-delivery/scripts/add_current_repo.py --include-hooks-template
```

初始化完成后，记得把 `AGENTS.md` 里的验证命令占位符替换成你仓库自己的 `lint / test / build` 命令。

---

## 什么是 Agent Skills

Agent Skills 是 Anthropic 定义的模块化能力扩展机制，通过 `SKILL.md` 文件为 AI Agent 提供专业领域知识、工作流和工具。详见 [官方文档](https://platform.claude.com/docs/zh-CN/agents-and-tools/agent-skills/overview)。

## License

MIT
