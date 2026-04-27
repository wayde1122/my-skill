# MCP and CI

## 先有底座，再上多 agent

这份 skill 不是用来替代工程底座的。开始多 agent 前，最好已经具备：

- `AGENTS.md`
- `.codex/config.toml`
- 统一的 `lint / test / build`
- `hooks`
- `CI`
- 至少一个必要的 `MCP`

## MCP 的作用

MCP 适合交给 `docs_researcher` 或 `release_guard` 使用：

- `GitHub`：查 PR、Issue、分支、状态
- `Linear`：读任务上下文
- `Docs`：核对 API 和框架行为
- `Sentry`：读线上错误
- `Playwright`：做浏览器验证

不要让 `implementer` 为了查外部上下文而承担额外噪音。

## CI 的作用

CI 是最终事实裁判。

原则：

- 本地怎么验证，CI 就怎么验证
- reviewer 通过不等于真实通过
- CI 失败要回流，而不是口头忽略

## hooks 的作用

hooks 适合做：

- 危险命令拦截
- 提醒补测试
- 限制敏感路径
- 在提交前检查关键条件

多 agent 提效靠分工，稳定性交给 hooks 和 CI 兜底。
