---
name: github-knowledge-base
description: 通过 gh CLI 搜索 GitHub 仓库、Issues、PRs，并管理本地知识库。用于查找 GitHub 资源、克隆仓库到知识库、维护项目目录。当用户搜索 GitHub、查找仓库、克隆项目、或维护本地代码知识库时使用。
---

# GitHub Knowledge Base

通过 gh CLI 搜索 GitHub 资源，并管理本地知识库目录。

---

## GitHub Search via gh CLI

搜索命令格式: `gh search {repos|issues|prs} "<query>" --limit <n>`

**常用搜索示例：**

```bash
gh search repos "language:python stars:>1000 topic:mcp" --limit 20
gh search issues "repo:facebook/react state:open label:bug" --limit 30
gh search prs "repo:vercel/next.js is:merged" --limit 15
```

**搜索 qualifier 速查：**

| Qualifier | 适用于 | 说明 |
|-----------|--------|------|
| `language:<lang>` | repos/issues/prs | 编程语言 |
| `stars:><n>` | repos | 星标数 |
| `topic:<name>` | repos | 主题标签 |
| `user:<owner>` / `org:<org>` | repos | 所有者/组织 |
| `repo:<owner/repo>` | issues/prs | 指定仓库 |
| `state:open\|closed\|merged` | issues/prs | 状态 |
| `author:<username>` | issues/prs | 作者 |
| `label:<name>` | issues/prs | 标签 |
| `is:merged\|unmerged` | prs | 合并状态 |

**查看详情：**

```bash
gh issue view <number> --repo <owner/repo> --comments
gh pr view <number> --repo <owner/repo> --comments
```

---

## Local Knowledge Base Workflow

### Cloning a New Repository

1. **Parse the repo**: Extract `owner/name` from user request

2. **Clone to KB directory**:
   ```bash
   git clone https://github.com/<owner>/<name>.git E:/code/github/<name>
   ```

3. **Verify clone succeeded**:
   - 检查目录是否存在且包含文件
   - 如果克隆失败（仓库不存在、网络问题等），告知用户具体错误并停止后续步骤
   ```bash
   ls E:/code/github/<name>
   ```

4. **Generate project description**: Read README or key files to understand the project

5. **Update CLAUDE.md**: Add entry for the new repo following the existing format:
   ```markdown
   ### [<name>](/<name>)
   Brief one-line description of what the project does.

   Additional context if useful (key features, tech stack, etc.).
   ```

6. **Verify CLAUDE.md update**: 确认新条目已正确写入，格式与已有条目一致

7. **Confirm completion**: Tell user the repo was cloned and where to find it

### Default Clone Location

If user says "clone X" without specifying a directory, default to `E:/code/github/`.

---

## CLAUDE.md Format

知识库目录文件结构：

```markdown
# Claude Code 知识库

本目录包含X个GitHub项目，涵盖...领域概述。

---

## Category Name

### [project-name](/project-name)
Brief description of the project.

### [another-project](/another-project)
Brief description of another project.

---

## Another Category

### [more-projects](/more-projects)
Description here.
```

更新时保持分类和一致的格式。
