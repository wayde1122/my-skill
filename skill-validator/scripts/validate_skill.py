#!/usr/bin/env python3
"""
Skill Validator - 自动化检查 Skill 是否符合 Anthropic 官方最佳实践
纯标准库实现，无第三方依赖
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


# ── 常量 ──────────────────────────────────────────────────────────────

RESERVED_WORDS = {"anthropic", "claude"}

FORBIDDEN_FILES = {
    "README.md", "CHANGELOG.md", "INSTALLATION_GUIDE.md",
    "QUICK_REFERENCE.md", "SETUP.md", "TESTING.md",
}

NAME_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
XML_TAG_PATTERN = re.compile(r"<[^>]+>")
WINDOWS_PATH_PATTERN = re.compile(r"(?<![<\\])\b\w+\\[a-zA-Z_]\w*(?:\.\w+)?")
MD_LINK_PATTERN = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")

# 动名词相关的常见前缀/后缀词
GERUND_INDICATORS = [
    "analyzing", "building", "checking", "creating", "debugging",
    "deploying", "editing", "extracting", "formatting", "generating",
    "handling", "importing", "logging", "managing", "monitoring",
    "optimizing", "parsing", "processing", "querying", "rendering",
    "reviewing", "searching", "styling", "testing", "tracking",
    "transforming", "updating", "validating", "visualizing", "writing",
]

TOC_PATTERNS = [
    re.compile(r"^##?\s*(目录|内容|contents|toc|table\s+of\s+contents)", re.IGNORECASE | re.MULTILINE),
    re.compile(r"^-\s+\[.+\]\(#.+\)", re.IGNORECASE | re.MULTILINE),  # markdown TOC 链接格式
]


# ── 检查结果 ─────────────────────────────────────────────────────────

class CheckResult:
    PASS = "pass"
    WARN = "warn"
    ERROR = "error"
    SKIP = "skip"

    def __init__(self, check_id: str, status: str, message: str):
        self.check_id = check_id
        self.status = status
        self.message = message

    def to_dict(self):
        return {
            "id": self.check_id,
            "status": self.status,
            "message": self.message,
        }


# ── frontmatter 解析 ─────────────────────────────────────────────────

def parse_frontmatter(content: str):
    """手动解析 YAML frontmatter，不依赖 pyyaml"""
    lines = content.split("\n")
    if not lines or lines[0].strip() != "---":
        return None, content

    end_idx = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break

    if end_idx == -1:
        return None, content

    frontmatter = {}
    current_key = None
    current_value_lines = []

    for line in lines[1:end_idx]:
        # 检测 key: value 格式
        match = re.match(r"^(\w[\w-]*):\s*(.*)", line)
        if match:
            # 保存上一个 key
            if current_key is not None:
                frontmatter[current_key] = "\n".join(current_value_lines).strip()
            current_key = match.group(1)
            current_value_lines = [match.group(2)]
        elif current_key is not None:
            # 多行值的续行
            current_value_lines.append(line)

    # 保存最后一个 key
    if current_key is not None:
        frontmatter[current_key] = "\n".join(current_value_lines).strip()

    body = "\n".join(lines[end_idx + 1:])
    return frontmatter, body


# ── 各项检查函数 ─────────────────────────────────────────────────────

def check_skill_md_exists(skill_dir: Path) -> CheckResult:
    """检查 SKILL.md 是否存在"""
    skill_md = skill_dir / "SKILL.md"
    if skill_md.is_file():
        return CheckResult("skill_md_exists", CheckResult.PASS, "SKILL.md 存在")
    return CheckResult("skill_md_exists", CheckResult.ERROR, "SKILL.md 不存在")


def check_name_exists(frontmatter: dict) -> CheckResult:
    """检查 name 字段是否存在且非空"""
    name = frontmatter.get("name", "").strip()
    if not name:
        return CheckResult("name_exists", CheckResult.ERROR, "缺少 name 字段或为空")
    return CheckResult("name_exists", CheckResult.PASS, f"name 字段存在: {name}")


def check_name_length(frontmatter: dict) -> CheckResult:
    """检查 name 长度 <= 64 字符"""
    name = frontmatter.get("name", "").strip()
    if not name:
        return CheckResult("name_length", CheckResult.SKIP, "name 字段缺失，跳过长度检查")
    if len(name) > 64:
        return CheckResult("name_length", CheckResult.ERROR,
                           f"name 长度 {len(name)} 字符，超过 64 字符限制")
    return CheckResult("name_length", CheckResult.PASS,
                       f"name 长度 {len(name)} 字符 (≤ 64)")


def check_name_format(frontmatter: dict) -> CheckResult:
    """检查 name 是否仅含小写字母、数字、连字符"""
    name = frontmatter.get("name", "").strip()
    if not name:
        return CheckResult("name_format", CheckResult.SKIP, "name 字段缺失，跳过格式检查")
    if not NAME_PATTERN.match(name):
        return CheckResult("name_format", CheckResult.ERROR,
                           f"name \"{name}\" 格式非法，仅允许小写字母、数字、连字符")
    return CheckResult("name_format", CheckResult.PASS, f"name 格式合法: {name}")


def check_name_reserved_words(frontmatter: dict) -> CheckResult:
    """检查 name 是否包含保留词 anthropic / claude"""
    name = frontmatter.get("name", "").strip().lower()
    if not name:
        return CheckResult("name_reserved", CheckResult.SKIP, "name 字段缺失，跳过保留词检查")
    for word in RESERVED_WORDS:
        if word in name:
            return CheckResult("name_reserved", CheckResult.ERROR,
                               f"name 包含保留词 \"{word}\"，不允许使用")
    return CheckResult("name_reserved", CheckResult.PASS, "name 不含保留词")


def check_name_convention(frontmatter: dict) -> CheckResult:
    """检查 name 是否符合动名词命名惯例（建议性）"""
    name = frontmatter.get("name", "").strip()
    if not name:
        return CheckResult("name_convention", CheckResult.SKIP, "name 字段缺失，跳过命名惯例检查")

    parts = name.split("-")
    has_gerund = any(
        part in GERUND_INDICATORS or part.endswith("ing")
        for part in parts
    )
    if has_gerund:
        return CheckResult("name_convention", CheckResult.PASS,
                           f"name 符合动名词命名惯例: {name}")
    return CheckResult("name_convention", CheckResult.WARN,
                       f"建议使用动名词形式命名 (如 processing-pdfs)，当前: {name}")


def check_desc_exists(frontmatter: dict) -> CheckResult:
    """检查 description 字段是否存在且非空"""
    desc = frontmatter.get("description", "").strip()
    if not desc:
        return CheckResult("desc_exists", CheckResult.ERROR, "缺少 description 字段或为空")
    return CheckResult("desc_exists", CheckResult.PASS,
                       f"description 存在 ({len(desc)} 字符)")


def check_desc_length(frontmatter: dict) -> CheckResult:
    """检查 description 长度 <= 1024 字符"""
    desc = frontmatter.get("description", "").strip()
    if not desc:
        return CheckResult("desc_length", CheckResult.SKIP, "description 缺失，跳过长度检查")
    if len(desc) > 1024:
        return CheckResult("desc_length", CheckResult.ERROR,
                           f"description 长度 {len(desc)} 字符，超过 1024 字符限制")
    return CheckResult("desc_length", CheckResult.PASS,
                       f"description 长度 {len(desc)} 字符 (≤ 1024)")


def check_desc_no_xml(frontmatter: dict) -> CheckResult:
    """检查 description 是否包含 XML 标签"""
    desc = frontmatter.get("description", "").strip()
    if not desc:
        return CheckResult("desc_no_xml", CheckResult.SKIP, "description 缺失，跳过 XML 检查")
    if XML_TAG_PATTERN.search(desc):
        return CheckResult("desc_no_xml", CheckResult.ERROR,
                           "description 包含 XML 标签，不允许")
    return CheckResult("desc_no_xml", CheckResult.PASS, "description 不含 XML 标签")


def check_body_line_count(body: str) -> CheckResult:
    """检查 SKILL.md 正文行数 < 500"""
    lines = body.strip().split("\n") if body.strip() else []
    count = len(lines)
    if count >= 500:
        return CheckResult("body_lines", CheckResult.ERROR,
                           f"正文 {count} 行，超过 500 行限制")
    if count >= 400:
        return CheckResult("body_lines", CheckResult.WARN,
                           f"正文 {count} 行，接近 500 行限制，建议拆分到参考文件")
    return CheckResult("body_lines", CheckResult.PASS, f"正文 {count} 行 (< 500)")


def check_forbidden_files(skill_dir: Path) -> CheckResult:
    """检查是否存在多余文件"""
    found = []
    for item in skill_dir.iterdir():
        if item.name in FORBIDDEN_FILES:
            found.append(item.name)
    if found:
        return CheckResult("forbidden_files", CheckResult.WARN,
                           f"发现多余文件 (建议删除): {', '.join(found)}")
    return CheckResult("forbidden_files", CheckResult.PASS, "无多余文件")


def check_windows_paths(skill_dir: Path) -> CheckResult:
    """检查所有 .md 文件中是否有 Windows 风格路径"""
    issues = []
    for md_file in skill_dir.rglob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        # 排除代码块内的内容
        in_code_block = False
        for line_num, line in enumerate(content.split("\n"), 1):
            stripped = line.strip()
            if stripped.startswith("```"):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                continue
            matches = WINDOWS_PATH_PATTERN.findall(line)
            for m in matches:
                # 过滤误判：排除 URL 中的转义和常见非路径模式
                if "\\\\" in m or "http" in line:
                    continue
                rel_path = md_file.relative_to(skill_dir)
                issues.append(f"{rel_path}:{line_num} -> {m}")

    if issues:
        detail = "; ".join(issues[:5])
        suffix = f" (共 {len(issues)} 处)" if len(issues) > 5 else ""
        return CheckResult("windows_paths", CheckResult.WARN,
                           f"发现 Windows 风格路径: {detail}{suffix}")
    return CheckResult("windows_paths", CheckResult.PASS, "未发现 Windows 风格路径")


def check_reference_depth(skill_dir: Path, body: str) -> CheckResult:
    """检查引用文件深度是否 <= 1 级"""
    # 从 SKILL.md 提取本地文件引用
    level1_refs = set()
    for _, href in MD_LINK_PATTERN.findall(body):
        if href.startswith("http") or href.startswith("#"):
            continue
        level1_refs.add(href)

    # 检查被引用文件中是否又引用了其他本地文件
    deep_refs = []
    for ref in level1_refs:
        ref_path = skill_dir / ref
        if not ref_path.is_file():
            continue
        try:
            ref_content = ref_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for _, nested_href in MD_LINK_PATTERN.findall(ref_content):
            if nested_href.startswith("http") or nested_href.startswith("#"):
                continue
            # 被引用文件又链接了本地文件 -> 深度 > 1
            nested_path = (ref_path.parent / nested_href)
            if nested_path.is_file():
                deep_refs.append(f"{ref} -> {nested_href}")

    if deep_refs:
        detail = "; ".join(deep_refs[:3])
        return CheckResult("ref_depth", CheckResult.WARN,
                           f"引用深度超过 1 级: {detail}")
    return CheckResult("ref_depth", CheckResult.PASS, "引用深度 ≤ 1 级")


def check_reference_toc(skill_dir: Path) -> CheckResult:
    """检查超过 100 行的参考文件是否有目录"""
    missing_toc = []
    skill_md = skill_dir / "SKILL.md"

    for md_file in skill_dir.rglob("*.md"):
        if md_file == skill_md:
            continue
        try:
            content = md_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        lines = content.split("\n")
        if len(lines) <= 100:
            continue

        # 检查前 30 行是否有目录标识
        head = "\n".join(lines[:30])
        has_toc = any(p.search(head) for p in TOC_PATTERNS)
        if not has_toc:
            rel_path = md_file.relative_to(skill_dir)
            missing_toc.append(f"{rel_path} ({len(lines)} 行)")

    if missing_toc:
        return CheckResult("ref_toc", CheckResult.WARN,
                           f"超过 100 行的参考文件缺少目录: {', '.join(missing_toc)}")
    return CheckResult("ref_toc", CheckResult.PASS, "参考文件目录检查通过")


def check_extra_frontmatter_fields(frontmatter: dict) -> CheckResult:
    """检查 frontmatter 是否仅包含 name 和 description"""
    allowed = {"name", "description", "license"}
    extra = set(frontmatter.keys()) - allowed
    if extra:
        return CheckResult("extra_fields", CheckResult.WARN,
                           f"frontmatter 包含额外字段: {', '.join(extra)}")
    return CheckResult("extra_fields", CheckResult.PASS, "frontmatter 字段符合规范")


# ── 主流程 ───────────────────────────────────────────────────────────

def validate_skill(skill_dir: Path) -> dict:
    """执行所有检查，返回结果字典"""
    results = []

    # 1. SKILL.md 存在性
    r = check_skill_md_exists(skill_dir)
    results.append(r)
    if r.status == CheckResult.ERROR:
        # SKILL.md 不存在，后续检查无法进行
        return _build_report(skill_dir, None, results)

    # 读取 SKILL.md
    skill_md_path = skill_dir / "SKILL.md"
    content = skill_md_path.read_text(encoding="utf-8")
    frontmatter, body = parse_frontmatter(content)

    if frontmatter is None:
        results.append(CheckResult("frontmatter_parse", CheckResult.ERROR,
                                   "无法解析 YAML frontmatter，请检查 --- 分隔符"))
        return _build_report(skill_dir, None, results)

    # 2-6. name 字段检查
    results.append(check_name_exists(frontmatter))
    results.append(check_name_length(frontmatter))
    results.append(check_name_format(frontmatter))
    results.append(check_name_reserved_words(frontmatter))
    results.append(check_name_convention(frontmatter))

    # 7-9. description 字段检查
    results.append(check_desc_exists(frontmatter))
    results.append(check_desc_length(frontmatter))
    results.append(check_desc_no_xml(frontmatter))

    # 10. 正文行数
    results.append(check_body_line_count(body))

    # 11. 多余文件
    results.append(check_forbidden_files(skill_dir))

    # 12. Windows 路径
    results.append(check_windows_paths(skill_dir))

    # 13. 引用深度
    results.append(check_reference_depth(skill_dir, body))

    # 14. 参考文件目录
    results.append(check_reference_toc(skill_dir))

    # 15. frontmatter 额外字段
    results.append(check_extra_frontmatter_fields(frontmatter))

    skill_name = frontmatter.get("name", "unknown")
    return _build_report(skill_dir, skill_name, results)


def _build_report(skill_dir: Path, skill_name, results: list) -> dict:
    """构建检查报告"""
    passed = sum(1 for r in results if r.status == CheckResult.PASS)
    warnings = sum(1 for r in results if r.status == CheckResult.WARN)
    errors = sum(1 for r in results if r.status == CheckResult.ERROR)
    skipped = sum(1 for r in results if r.status == CheckResult.SKIP)

    return {
        "skill_path": str(skill_dir).replace("\\", "/"),
        "skill_name": skill_name if skill_name is not None else "unknown",
        "total_checks": len(results),
        "passed": passed,
        "warnings": warnings,
        "errors": errors,
        "skipped": skipped,
        "results": [r.to_dict() for r in results],
    }


# ── 输出格式 ─────────────────────────────────────────────────────────

STATUS_ICONS_UNICODE = {
    "pass": "\u2705",
    "warn": "\u26a0\ufe0f",
    "error": "\u274c",
    "skip": "\u23ed\ufe0f",
}

STATUS_ICONS_ASCII = {
    "pass": "[OK]",
    "warn": "[!!]",
    "error": "[XX]",
    "skip": "[--]",
}


def _get_status_icons():
    """根据终端编码能力选择图标集"""
    try:
        "\u2705".encode(sys.stdout.encoding if sys.stdout.encoding else "utf-8")
        return STATUS_ICONS_UNICODE
    except (UnicodeEncodeError, LookupError):
        return STATUS_ICONS_ASCII

STATUS_COLORS = {
    "pass": "\033[32m",   # green
    "warn": "\033[33m",   # yellow
    "error": "\033[31m",  # red
    "skip": "\033[90m",   # gray
}
RESET = "\033[0m"


def format_text(report: dict) -> str:
    """格式化为人类可读的终端输出"""
    icons = _get_status_icons()
    lines = []
    lines.append("")
    lines.append(f"{'=' * 60}")
    lines.append(f"  Skill Validator Report")
    lines.append(f"  Path: {report['skill_path']}")
    lines.append(f"  Name: {report['skill_name']}")
    lines.append(f"{'=' * 60}")
    lines.append("")

    for item in report["results"]:
        status = item["status"]
        icon = icons.get(status, "?")
        color = STATUS_COLORS.get(status, "")
        lines.append(f"  {icon} {color}[{status.upper():5s}]{RESET} {item['message']}")

    lines.append("")
    lines.append(f"  {'-' * 56}")

    p = report["passed"]
    w = report["warnings"]
    e = report["errors"]
    s = report["skipped"]
    total = report["total_checks"]

    lines.append(f"  Total: {total}  |  Pass: {p}  |  Warn: {w}  |  Error: {e}  |  Skip: {s}")

    if e > 0:
        lines.append(f"\n  {STATUS_COLORS['error']}Result: FAILED - {e} error(s) must be fixed{RESET}")
    elif w > 0:
        lines.append(f"\n  {STATUS_COLORS['warn']}Result: PASSED with {w} warning(s){RESET}")
    else:
        lines.append(f"\n  {STATUS_COLORS['pass']}Result: ALL PASSED{RESET}")

    lines.append("")
    return "\n".join(lines)


def format_json(report: dict) -> str:
    """格式化为 JSON"""
    return json.dumps(report, ensure_ascii=False, indent=2)


# ── CLI 入口 ─────────────────────────────────────────────────────────

def main():
    # 尝试设置 stdout 编码为 UTF-8（Windows 兼容）
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):
            pass

    parser = argparse.ArgumentParser(
        description="检查 Skill 是否符合 Anthropic 官方最佳实践",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python validate_skill.py /path/to/my-skill
  python validate_skill.py /path/to/my-skill --format json
  python validate_skill.py /path/to/my-skill --format text
        """,
    )
    parser.add_argument("skill_dir", help="Skill 目录路径")
    parser.add_argument(
        "--format", "-f",
        choices=["text", "json"],
        default="text",
        help="输出格式 (默认: text)",
    )

    args = parser.parse_args()
    skill_dir = Path(args.skill_dir).resolve()

    if not skill_dir.is_dir():
        print(f"Error: \"{skill_dir}\" is not a valid directory", file=sys.stderr)
        sys.exit(2)

    report = validate_skill(skill_dir)

    if args.format == "json":
        print(format_json(report))
    else:
        print(format_text(report))

    # 有 error 则退出码为 1
    sys.exit(1 if report["errors"] > 0 else 0)


if __name__ == "__main__":
    main()
