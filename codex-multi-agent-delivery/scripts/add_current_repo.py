#!/usr/bin/env python3
"""Bootstrap the current repository for the Codex multi-agent workflow.

This script creates a minimal Codex-side workflow scaffold in a target repo.
It is intentionally conservative:

- Defaults to the current working directory.
- Does not overwrite existing files unless --force is passed.
- Focuses on Codex workflow files, not stack-specific CI commands.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import textwrap


AGENTS_MD = """\
# AGENTS.md

## Repository expectations

- Read the relevant files before changing code.
- Keep plans short and explicit before implementation.
- Prefer small, task-scoped changes over broad refactors.
- Reuse existing patterns, components, and helper functions when possible.
- Run the repository's validation commands after making changes.
- Include a short summary, validation results, and residual risks in final output.

## Validation commands

- Replace these placeholders with your real commands:
- `lint`: TODO
- `test`: TODO
- `build`: TODO

## Guardrails

- Do not edit secrets, infrastructure, or database schema unless the task explicitly requires it.
- Treat CI as the final source of truth even if local validation passes.
"""


CONFIG_TOML = """\
#:schema https://developers.openai.com/codex/config-schema.json

model = "gpt-5.5"
approval_policy = "on-request"
approvals_reviewer = "auto_review"
sandbox_mode = "workspace-write"

[features]
codex_hooks = true
multi_agent = true

[sandbox_workspace_write]
network_access = false

[agents]
max_threads = 6
max_depth = 1
"""


PLANNER_TOML = '''\
name = "planner"
description = "Task planner that breaks work into bounded, executable steps."
model = "gpt-5.4"
model_reasoning_effort = "high"
sandbox_mode = "read-only"
developer_instructions = """
Stay in planning mode.
Define scope, order, risk, and dependencies.
Do not make code changes.
"""
'''


EXPLORER_TOML = '''\
name = "explorer"
description = "Read-only codebase explorer for tracing files, call chains, and impact areas."
model = "gpt-5.4-mini"
model_reasoning_effort = "medium"
sandbox_mode = "read-only"
developer_instructions = """
Stay in exploration mode.
Trace execution paths and identify impacted files.
Do not make code changes.
"""
'''


DOCS_RESEARCHER_TOML = '''\
name = "docs_researcher"
description = "Documentation specialist that verifies APIs and framework behavior."
model = "gpt-5.4-mini"
model_reasoning_effort = "medium"
sandbox_mode = "read-only"
developer_instructions = """
Use official documentation and MCP wherever possible.
Return concise findings with links or exact references when available.
Do not make code changes.
"""
'''


IMPLEMENTER_TOML = '''\
name = "implementer"
description = "Implementation agent that writes code, runs validation, and iterates on failures."
model = "gpt-5.5"
model_reasoning_effort = "high"
sandbox_mode = "workspace-write"
developer_instructions = """
Make the smallest correct change.
Prefer existing project patterns.
Run validation after changes.
If validation fails, fix it before reporting back.
"""
'''


REVIEWER_TOML = '''\
name = "reviewer"
description = "Read-only reviewer focused on correctness, regressions, security, and missing tests."
model = "gpt-5.4"
model_reasoning_effort = "high"
sandbox_mode = "read-only"
developer_instructions = """
Review like an owner.
Prioritize correctness, security, regressions, and missing tests.
Do not make code changes.
"""
'''


RELEASE_GUARD_TOML = '''\
name = "release_guard"
description = "Final gatekeeper for PR readiness, CI state, risk review, and release conditions."
model = "gpt-5.4-mini"
model_reasoning_effort = "medium"
sandbox_mode = "read-only"
developer_instructions = """
Check merge readiness, CI status, release risk, and unresolved blockers.
Escalate high-risk changes instead of silently approving them.
Do not make code changes.
"""
'''


HOOKS_JSON = """\
{
  "note": "Replace this placeholder with real Codex hooks when your repo needs command guards or policy checks."
}
"""


FILES = {
    "AGENTS.md": AGENTS_MD,
    ".codex/config.toml": CONFIG_TOML,
    ".codex/agents/planner.toml": PLANNER_TOML,
    ".codex/agents/explorer.toml": EXPLORER_TOML,
    ".codex/agents/docs-researcher.toml": DOCS_RESEARCHER_TOML,
    ".codex/agents/implementer.toml": IMPLEMENTER_TOML,
    ".codex/agents/reviewer.toml": REVIEWER_TOML,
    ".codex/agents/release-guard.toml": RELEASE_GUARD_TOML,
}


def normalize_newlines(content: str) -> str:
    return textwrap.dedent(content).rstrip() + "\n"


def write_file(path: Path, content: str, force: bool) -> str:
    if path.exists() and not force:
        return "skipped"

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(normalize_newlines(content), encoding="utf-8")
    return "updated" if path.exists() and force else "created"


def bootstrap_repo(target: Path, force: bool, include_hooks_template: bool) -> list[tuple[str, str]]:
    results: list[tuple[str, str]] = []

    for relative_path, content in FILES.items():
        destination = target / relative_path
        existed_before = destination.exists()
        status = write_file(destination, content, force)
        if status == "updated" and not existed_before:
            status = "created"
        results.append((relative_path, status))

    if include_hooks_template:
        destination = target / ".codex/hooks.json"
        existed_before = destination.exists()
        status = write_file(destination, HOOKS_JSON, force)
        if status == "updated" and not existed_before:
            status = "created"
        results.append((".codex/hooks.json", status))

    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Add the Codex multi-agent workflow scaffold to the current repository."
    )
    parser.add_argument(
        "--target",
        default=".",
        help="Target repository path. Defaults to the current working directory.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing generated files.",
    )
    parser.add_argument(
        "--include-hooks-template",
        action="store_true",
        help="Also create a placeholder .codex/hooks.json template.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    target = Path(args.target).resolve()

    if not target.exists():
        print(f"[ERROR] Target path does not exist: {target}")
        return 1
    if not target.is_dir():
        print(f"[ERROR] Target path is not a directory: {target}")
        return 1

    results = bootstrap_repo(target, args.force, args.include_hooks_template)

    print(f"[OK] Bootstrapped Codex multi-agent workflow in: {target}")
    print()
    for relative_path, status in results:
        print(f"- {status:7} {relative_path}")

    print()
    print("Next steps:")
    print("- Replace the placeholder validation commands in AGENTS.md.")
    print("- Adjust .codex/config.toml to match your repo's approval and sandbox needs.")
    print("- Add MCP servers, hooks, and CI only where they fit your actual workflow.")
    print("- Run Codex in this repo and invoke the multi-agent delivery skill when needed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
