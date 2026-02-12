# My Skills

一组自定义的 [Cursor](https://www.cursor.com/) / [Claude Code](https://code.claude.com/) Agent Skills，用于扩展 AI 的专业能力。

## 包含的 Skills

| Skill | 说明 |
|-------|------|
| [github-knowledge-base](./github-knowledge-base/) | 通过 gh CLI 搜索 GitHub 仓库/Issues/PRs，并管理本地代码知识库 |
| [skill-validator](./skill-validator/) | 检查 Skill 是否符合 Anthropic 官方最佳实践，自动化结构检查 + AI 内容审查 |

## 安装

### Cursor

将 Skill 目录复制到个人 Skills 目录：

```bash
# 克隆仓库
git clone https://github.com/wayde1122/my-skill.git

# 复制到 Cursor Skills 目录
cp -r my-skill/github-knowledge-base ~/.cursor/skills/
cp -r my-skill/skill-validator ~/.cursor/skills/
```

### Claude Code

```bash
cp -r my-skill/github-knowledge-base ~/.claude/skills/
cp -r my-skill/skill-validator ~/.claude/skills/
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

检查任意 Skill 是否符合 [Anthropic 官方最佳实践](https://platform.claude.com/docs/agents-and-tools/agent-skills/best-practices)。

**触发方式**：当你要求"检查/验证/审查某个 Skill"时自动触发。

**验证流程**：

1. **脚本自动检查**（15 项结构性规则）

   ```bash
   python scripts/validate_skill.py <skill目录路径>

   # JSON 输出
   python scripts/validate_skill.py <skill目录路径> --format json
   ```

   检查项包括：SKILL.md 存在性、name/description 格式、正文行数、多余文件、Windows 路径、引用深度等。

2. **AI 内容审查**（6 项语义检查）

   description 质量、内容简洁性、术语一致性、时间敏感信息、示例质量、工作流反馈循环。

3. **输出分级报告**

   综合两部分结果，按三级分类输出：通过 / 建议改进 / 必须修复。

**前置要求**：Python 3.8+（无第三方依赖）。

---

## 什么是 Agent Skills

Agent Skills 是 Anthropic 定义的模块化能力扩展机制，通过 `SKILL.md` 文件为 AI Agent 提供专业领域知识、工作流和工具。详见 [官方文档](https://platform.claude.com/docs/agents-and-tools/agent-skills/overview)。

## License

MIT
