#!/usr/bin/env python3
"""为单会话 Workflow Docs Sync 准备模板并检查最终仓库状态。

调用关系：CLI 解析参数后，``prepare`` 解析两个仓库的 HEAD、从固定上游提交读取
九份模板并只补齐缺失文件；``check`` 使用同一上游提交只读验证目标 HEAD、文件范围、
内容和 whitespace。脚本不运行项目测试，也不执行任何 Git 发布动作。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


CORE_FILES = (
    "architecture.md",
    "capability_contract.json",
    "interact.md",
    "docs/business_user_guide.md",
    "TESTING.md",
    "PR_Checklist.md",
    "SOP.md",
    "AGENTS.md",
    ".github/pull_request_template.md",
)
PR_TEMPLATE = ".github/pull_request_template.md"
EDITABLE_PATHS = frozenset((*CORE_FILES, ".gitignore"))
LANGUAGES = ("zh", "en")
SHA_PATTERN = re.compile(r"[0-9a-f]{40}")
ATX_HEADING = re.compile(r"^[ \t]{0,3}#{1,6}(?:[ \t]+(.*)|[ \t]*)$")
FENCE = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,})")
TEMPLATE_TOKENS = (
    "<项目名>",
    "<项目 / agent / app 名称>",
    "<对象>",
    "<指标 / 结果>",
    "<project name>",
    "<project / agent / app name>",
    "<object>",
    "<metric / result>",
    "Case 1：确认一个对象最近是否异常",
    "Case 1: Check whether one object is abnormal",
    "待项目负责人补充",
    "project owner must replace this",
    "sample_supported_question",
    "sample_multi_object_comparison_not_supported",
    "sample_no_final_business_decision",
    "sample_requires_context_before_answer",
    "CAPABILITY.sample_",
    "BOUNDARY.sample_",
    "RESPONSIBILITY.sample_",
    "BEHAVIOR.sample_",
    "<!-- capability-anchor: TODO -->",
    "<!-- test-anchor: TODO -->",
)


class SyncError(RuntimeError):
    """表示可预期且应以单行 JSON 返回的同步失败。"""

    def __init__(self, *, error: str, detail: str) -> None:
        """保存稳定错误摘要和具体证据。"""
        super().__init__(error)
        self.error = error
        self.detail = detail


class JsonArgumentParser(argparse.ArgumentParser):
    """把参数错误转换为稳定的同步错误。"""

    def error(self, message: str) -> None:
        """接收 argparse 消息并立即终止当前解析。"""
        raise SyncError(error="参数无效", detail=message)


@dataclass(frozen=True)
class Repository:
    """保存已经验证的 Git 根目录和当前提交。"""

    root: Path
    head: str


@dataclass(frozen=True)
class StatusEntry:
    """保存一条 porcelain 状态及其涉及的全部相对路径。"""

    code: str
    paths: tuple[str, ...]


def emit_json(*, payload: dict[str, Any]) -> None:
    """把结果写成一行 UTF-8 JSON，供当前会话直接消费。"""
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))


def run_git(*, repo_root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    """在指定仓库运行只含显式参数的 Git 命令并捕获 UTF-8 输出。"""
    environment = os.environ.copy()
    environment.update({"LC_ALL": "C", "GIT_OPTIONAL_LOCKS": "0"})
    return subprocess.run(
        args=["git", "-C", str(repo_root), *args],
        cwd=repo_root,
        env=environment,
        check=False,
        capture_output=True,
        encoding="utf-8",
        text=True,
    )


def git_output(*, repo_root: Path, args: list[str], purpose: str) -> str:
    """运行必须成功的 Git 命令并返回 stdout。"""
    result = run_git(repo_root=repo_root, args=args)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "Git 无输出"
        raise SyncError(error=purpose, detail=detail)
    return result.stdout


def require_sha(*, value: str, label: str) -> str:
    """验证并返回完整小写 Git SHA。"""
    if SHA_PATTERN.fullmatch(value) is None:
        raise SyncError(error=f"{label}无效", detail="必须是 40 位小写十六进制 Git SHA")
    return value


def require_repository(*, value: str, label: str) -> Repository:
    """验证路径恰好是 Git 工作树根目录并解析当前提交。"""
    try:
        candidate = Path(value).expanduser().resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise SyncError(error=f"{label}无效", detail=str(exc)) from exc
    root_text = git_output(
        repo_root=candidate,
        args=["rev-parse", "--show-toplevel"],
        purpose=f"无法解析{label}",
    ).strip()
    actual_root = Path(root_text).resolve(strict=True)
    if actual_root != candidate:
        raise SyncError(
            error=f"{label}必须是 Git 根目录",
            detail=f"传入 {candidate}，实际 {actual_root}",
        )
    head = git_output(
        repo_root=candidate,
        args=["rev-parse", "--verify", "HEAD^{commit}"],
        purpose=f"无法解析{label} HEAD",
    ).strip()
    return Repository(root=candidate, head=require_sha(value=head, label=f"{label} HEAD"))


def require_commit(*, repo_root: Path, value: str, label: str) -> str:
    """验证固定提交存在于指定上游对象库。"""
    commit = require_sha(value=value, label=label)
    resolved = git_output(
        repo_root=repo_root,
        args=["rev-parse", "--verify", f"{commit}^{{commit}}"],
        purpose=f"{label}不存在",
    ).strip()
    if resolved != commit:
        raise SyncError(error=f"{label}解析不一致", detail=f"期望 {commit}，实际 {resolved}")
    return commit


def parse_status(*, output: str) -> list[StatusEntry]:
    """解析 ``git status --porcelain=v1 -z``，包含 rename/copy 两端路径。"""
    fields = output.split("\0")
    entries: list[StatusEntry] = []
    index = 0
    while index < len(fields) and fields[index] != "":
        row = fields[index]
        if len(row) < 4 or row[2] != " ":
            raise SyncError(error="Git 状态格式无效", detail=repr(row))
        code = row[:2]
        paths = [row[3:]]
        index += 1
        if "R" in code or "C" in code:
            if index >= len(fields) or fields[index] == "":
                raise SyncError(error="Git 状态格式无效", detail="rename/copy 缺少来源路径")
            paths.append(fields[index])
            index += 1
        entries.append(StatusEntry(code=code, paths=tuple(paths)))
    return entries


def read_status(*, repo_root: Path) -> list[StatusEntry]:
    """读取目标仓库全部 tracked 和 untracked 状态。"""
    output = git_output(
        repo_root=repo_root,
        args=["status", "--porcelain=v1", "-z", "--untracked-files=all"],
        purpose="无法读取目标仓库状态",
    )
    return parse_status(output=output)


def require_editable_dirty(*, repo_root: Path) -> list[StatusEntry]:
    """在任何写入前拒绝九份文档和可选 gitignore 之外的 dirty 路径。"""
    entries = read_status(repo_root=repo_root)
    outside = sorted({
        path
        for entry in entries
        for path in entry.paths
        if path not in EDITABLE_PATHS
    })
    if outside:
        raise SyncError(error="存在同步范围外的 dirty path", detail=", ".join(outside))
    return entries


def read_template(
    *, upstream_root: Path, upstream_sha: str, language: str, relative_path: str
) -> str:
    """只通过固定提交的 Git 对象读取一个语言模板。"""
    source_path = f"{language}/{relative_path}"
    return git_output(
        repo_root=upstream_root,
        args=["show", f"{upstream_sha}:{source_path}"],
        purpose="无法读取固定上游模板",
    )


def read_templates(
    *, upstream_root: Path, upstream_sha: str, language: str
) -> dict[str, str]:
    """读取九份固定上游模板，缺少任意模板时不返回部分结果。"""
    return {
        path: read_template(
            upstream_root=upstream_root,
            upstream_sha=upstream_sha,
            language=language,
            relative_path=path,
        )
        for path in CORE_FILES
    }


def inspect_destinations(*, target_root: Path) -> tuple[list[str], list[str]]:
    """区分缺失和已有目标文件，并在写入前拒绝目录冲突。"""
    missing: list[str] = []
    existing: list[str] = []
    for relative_path in CORE_FILES:
        destination = target_root / relative_path
        current = target_root
        for part in Path(relative_path).parts:
            current /= part
            if current.is_symlink():
                raise SyncError(error="核心文档路径不能是符号链接", detail=relative_path)
            if current != destination and current.exists() and not current.is_dir():
                raise SyncError(error="核心文档父路径不是目录", detail=relative_path)
        if destination.is_file():
            existing.append(relative_path)
        elif destination.exists():
            raise SyncError(error="核心文档路径不是普通文件", detail=relative_path)
        else:
            missing.append(relative_path)
    return missing, existing


def install_missing(
    *, target_root: Path, templates: dict[str, str], missing: list[str]
) -> None:
    """只创建缺失模板及必要父目录，绝不重写已有文档。"""
    for relative_path in missing:
        destination = target_root / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open(mode="x", encoding="utf-8", newline="") as stream:
            stream.write(templates[relative_path])


def prepare(*, target_repo: str, upstream_dir: str, language: str) -> dict[str, Any]:
    """执行写入前检查，只补齐缺失模板并返回当前会话所需事实。"""
    target = require_repository(value=target_repo, label="目标仓库")
    upstream = require_repository(value=upstream_dir, label="上游目录")
    templates = read_templates(
        upstream_root=upstream.root,
        upstream_sha=upstream.head,
        language=language,
    )
    require_editable_dirty(repo_root=target.root)
    missing, existing = inspect_destinations(target_root=target.root)
    install_missing(target_root=target.root, templates=templates, missing=missing)
    return {
        "status": "prepared",
        "target_repo": str(target.root),
        "target_head": target.head,
        "upstream_dir": str(upstream.root),
        "upstream_sha": upstream.head,
        "language": language,
        "installed": missing,
        "existing": existing,
        "required_files": list(CORE_FILES),
    }


def normalize_text(*, text: str) -> str:
    """只规范换行符，使跨平台模板原样复制判断稳定。"""
    return text.replace("\r\n", "\n").replace("\r", "\n")


def line_hits(*, relative_path: str, text: str) -> list[str]:
    """返回明确模板 token 和未填写中文占位的逐行错误。"""
    failures: list[str] = []
    tokens = (*TEMPLATE_TOKENS, "待补充")
    for line_number, line in enumerate(text.splitlines(), start=1):
        for token in tokens:
            if token in line:
                failures.append(
                    f"{relative_path}:{line_number}: 检测到未项目化内容 {token}"
                )
    return failures


def markdown_failures(*, relative_path: str, text: str) -> list[str]:
    """忽略 fenced code，要求至少一个非空 ATX 标题且不存在空标题。"""
    failures: list[str] = []
    valid_heading = False
    fence_character = ""
    fence_width = 0
    for line_number, line in enumerate(text.splitlines(), start=1):
        fence_match = FENCE.match(line)
        if fence_match is not None:
            marker = fence_match.group(1)
            if not fence_character:
                fence_character, fence_width = marker[0], len(marker)
            elif marker[0] == fence_character and len(marker) >= fence_width:
                fence_character, fence_width = "", 0
            continue
        if fence_character:
            continue
        heading = ATX_HEADING.match(line)
        if heading is None:
            continue
        title = (heading.group(1) or "").strip()
        title = re.sub(r"[ \t]+#+[ \t]*$", "", title).strip()
        if re.fullmatch(r"#+", title) is not None:
            title = ""
        if title:
            valid_heading = True
        else:
            failures.append(f"{relative_path}:{line_number}: Markdown 标题为空")
    if not valid_heading:
        failures.append(f"{relative_path}: 缺少非空 Markdown 标题")
    return failures


def capability_failures(*, text: str) -> list[str]:
    """验证 capability contract 是合法 JSON object，不机械裁定项目语义。"""
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        return [f"capability_contract.json:{exc.lineno}: JSON 无效: {exc.msg}"]
    if not isinstance(payload, dict):
        return ["capability_contract.json: 顶层必须是 JSON object"]
    return []


def content_failures(*, target_root: Path, templates: dict[str, str]) -> tuple[
    list[str], dict[str, str]
]:
    """验证九份文件的存在性、编码、内容、标题、JSON 和模板差异。"""
    failures: list[str] = []
    texts: dict[str, str] = {}
    for relative_path in CORE_FILES:
        path = target_root / relative_path
        if path.is_symlink():
            failures.append(f"核心文档不能是符号链接: {relative_path}")
            continue
        if not path.is_file():
            failures.append(f"缺少必需文件: {relative_path}")
            continue
        try:
            text = path.read_bytes().decode("utf-8")
        except UnicodeDecodeError as exc:
            failures.append(f"{relative_path}: 不是有效 UTF-8: {exc}")
            continue
        texts[relative_path] = text
        if not text.strip():
            failures.append(f"{relative_path}: 文件为空")
            continue
        if relative_path.endswith(".md"):
            failures.extend(markdown_failures(relative_path=relative_path, text=text))
        failures.extend(line_hits(relative_path=relative_path, text=text))
        if (
            relative_path != PR_TEMPLATE
            and normalize_text(text=text)
            == normalize_text(text=templates[relative_path])
        ):
            failures.append(f"{relative_path}: 不允许与固定上游模板完全相同")
    if "capability_contract.json" in texts:
        failures.extend(capability_failures(text=texts["capability_contract.json"]))
    return failures, texts


def tracked_whitespace_failures(*, target_root: Path) -> list[str]:
    """对 working tree 和 index 的 tracked diff 运行 Git whitespace 检查。"""
    failures: list[str] = []
    for args, label in (
        (["diff", "--check"], "working tree"),
        (["diff", "--cached", "--check"], "index"),
    ):
        result = run_git(repo_root=target_root, args=args)
        if result.returncode != 0:
            detail = result.stdout.strip() or result.stderr.strip() or "无诊断输出"
            failures.append(f"{label} whitespace 检查失败: {detail}")
    return failures


def file_whitespace_failures(*, target_root: Path) -> list[str]:
    """用 Git 的同一规则检查九份最终文档和存在的辅助 gitignore。"""
    failures: list[str] = []
    paths = [path for path in CORE_FILES if (target_root / path).is_file()]
    gitignore = target_root / ".gitignore"
    if gitignore.is_symlink():
        failures.append(".gitignore: 不能是符号链接")
    elif gitignore.exists() and not gitignore.is_file():
        failures.append(".gitignore: 不是普通文件")
    elif gitignore.is_file():
        try:
            gitignore.read_bytes().decode("utf-8")
        except UnicodeDecodeError as exc:
            failures.append(f".gitignore: 不是有效 UTF-8: {exc}")
    if not gitignore.is_symlink() and gitignore.is_file():
        paths.append(".gitignore")
    for relative_path in paths:
        result = run_git(
            repo_root=target_root,
            args=[
                "diff",
                "--no-index",
                "--check",
                "--",
                os.devnull,
                str(target_root / relative_path),
            ],
        )
        if result.returncode not in (0, 1):
            detail = result.stdout.strip() or result.stderr.strip() or "无诊断输出"
            failures.append(f"最终文件 whitespace 检查失败: {detail}")
    return failures


def check(
    *,
    target_repo: str,
    upstream_dir: str,
    upstream_sha: str,
    expected_target_head: str,
    language: str,
) -> dict[str, Any]:
    """只读验证固定上游提交对应的最终目标仓库状态。"""
    target = require_repository(value=target_repo, label="目标仓库")
    expected_head = require_sha(value=expected_target_head, label="预期目标 HEAD")
    if target.head != expected_head:
        raise SyncError(
            error="目标 HEAD 已变化",
            detail=f"期望 {expected_head}，实际 {target.head}",
        )
    upstream = require_repository(value=upstream_dir, label="上游目录")
    pinned_sha = require_commit(
        repo_root=upstream.root,
        value=upstream_sha,
        label="上游 SHA",
    )
    entries = require_editable_dirty(repo_root=target.root)
    templates = read_templates(
        upstream_root=upstream.root,
        upstream_sha=pinned_sha,
        language=language,
    )
    failures, _ = content_failures(target_root=target.root, templates=templates)
    failures.extend(tracked_whitespace_failures(target_root=target.root))
    failures.extend(file_whitespace_failures(target_root=target.root))
    if failures:
        raise SyncError(error="最终仓库检查失败", detail=" | ".join(failures))
    return {
        "status": "passed",
        "target_repo": str(target.root),
        "target_head": target.head,
        "upstream_sha": pinned_sha,
        "language": language,
        "files_checked": len(CORE_FILES),
        "dirty_paths": sorted({path for entry in entries for path in entry.paths}),
    }


def build_parser() -> JsonArgumentParser:
    """构建只暴露 prepare 和 check 的内部 CLI。"""
    parser = JsonArgumentParser(description="准备并检查 Workflow Docs Sync。")
    commands = parser.add_subparsers(dest="command", required=True)
    prepare_parser = commands.add_parser("prepare")
    prepare_parser.add_argument("--target-repo", required=True)
    prepare_parser.add_argument("--upstream-dir", required=True)
    prepare_parser.add_argument("--language", choices=LANGUAGES, required=True)
    check_parser = commands.add_parser("check")
    check_parser.add_argument("--target-repo", required=True)
    check_parser.add_argument("--upstream-dir", required=True)
    check_parser.add_argument("--upstream-sha", required=True)
    check_parser.add_argument("--expected-target-head", required=True)
    check_parser.add_argument("--language", choices=LANGUAGES, required=True)
    return parser


def execute(*, args: argparse.Namespace) -> dict[str, Any]:
    """按已解析子命令调用对应实现并返回可序列化结果。"""
    if args.command == "prepare":
        return prepare(
            target_repo=args.target_repo,
            upstream_dir=args.upstream_dir,
            language=args.language,
        )
    if args.command == "check":
        return check(
            target_repo=args.target_repo,
            upstream_dir=args.upstream_dir,
            upstream_sha=args.upstream_sha,
            expected_target_head=args.expected_target_head,
            language=args.language,
        )
    raise SyncError(error="参数无效", detail=f"未知子命令: {args.command}")


def run_cli() -> int:
    """运行 CLI；成功或已知失败均只输出一行 JSON。"""
    try:
        payload = execute(args=build_parser().parse_args())
    except SyncError as exc:
        emit_json(payload={"status": "failed", "error": exc.error, "detail": exc.detail})
        return 1
    except (OSError, RuntimeError, TypeError, UnicodeError, ValueError) as exc:
        detail = f"{type(exc).__name__}: {exc}"
        emit_json(payload={"status": "failed", "error": "同步器执行失败", "detail": detail})
        return 1
    emit_json(payload=payload)
    return 0


if __name__ == "__main__":
    sys.exit(run_cli())
