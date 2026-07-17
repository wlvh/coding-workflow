#!/usr/bin/env python3
"""从 clean pinned upstream 覆盖安装两个 Workflow Docs Sync Skill。"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


SKILL_NAMES = ("workflow-docs-sync", "workflow-docs-sync-review")
PLATFORM_ROOTS = {
    "codex": Path(".agents/skills"),
    "claude": Path(".claude/skills"),
}


class InstallError(RuntimeError):
    """保存必须 fail-fast 的安装错误。"""

    def __init__(self, *, error: str, detail: str) -> None:
        """参数为摘要和证据；预期构造结构化异常。"""
        super().__init__(error)
        self.error = error
        self.detail = detail


class JsonArgumentParser(argparse.ArgumentParser):
    """把 argparse 错误转换为 InstallError。"""

    def error(self, message: str) -> None:
        """参数为 argparse 消息；预期抛出单行 JSON 错误。"""
        raise InstallError(error="参数无效", detail=message)


def emit_json(*, payload: dict[str, Any]) -> None:
    """参数为结果对象；预期 stdout 写一行 UTF-8 JSON。"""
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))


def git(*, repo_root: Path, args: list[str]) -> Any:
    """参数为仓库和 Git 参数；预期返回捕获 UTF-8 输出的进程结果。"""
    return subprocess.run(
        args=["git", "-C", str(repo_root), *args],
        cwd=repo_root,
        env=os.environ.copy(),
        check=False,
        capture_output=True,
        encoding="utf-8",
        text=True,
    )


def require_sha(*, value: str, label: str) -> str:
    """参数为候选值和字段名；预期返回完整小写 Git SHA。"""
    if re.fullmatch(r"[0-9a-f]{40}", value) is None:
        raise InstallError(
            error=f"{label}无效",
            detail="必须是 40 位小写十六进制 Git SHA",
        )
    return value


def require_repo(*, value: str, label: str) -> tuple[Path, str]:
    """参数为仓库路径和角色；预期返回规范根目录与 HEAD。"""
    repo_root = Path(value).expanduser().resolve(strict=True)
    result = git(
        repo_root=repo_root,
        args=["rev-parse", "--show-toplevel", "HEAD"],
    )
    lines = result.stdout.splitlines()
    if result.returncode != 0 or len(lines) != 2:
        raise InstallError(
            error=f"{label}无效",
            detail=result.stderr.strip() or "无法解析仓库根目录和 HEAD",
        )
    actual_root = Path(lines[0]).resolve(strict=True)
    if actual_root != repo_root:
        raise InstallError(
            error=f"{label}必须是仓库根目录",
            detail=f"传入 {repo_root}，实际 {actual_root}",
        )
    return repo_root, require_sha(value=lines[1], label=f"{label} HEAD")


def require_clean(*, repo_root: Path, label: str) -> None:
    """参数为仓库和角色；预期工作区/暂存区无任何改动。"""
    result = git(
        repo_root=repo_root,
        args=["status", "--porcelain=v1", "--untracked-files=all"],
    )
    if result.returncode != 0:
        raise InstallError(error="无法读取 Git 状态", detail=result.stderr.strip())
    if result.stdout:
        raise InstallError(
            error=f"{label}工作区不干净", detail=result.stdout.strip()
        )


def claude_text(*, text: str) -> str:
    """参数为 canonical SKILL.md；预期禁止模型隐式调用。"""
    parts = text.split("---", 2)
    if len(parts) != 3 or parts[0] != "":
        raise InstallError(
            error="SKILL.md frontmatter 无效",
            detail="缺少标准 YAML frontmatter",
        )
    lines = parts[1].strip("\n").splitlines()
    key = "disable-model-invocation"
    indexes = [
        index for index, line in enumerate(lines)
        if line.split(":", 1)[0].strip() == key
    ]
    if len(indexes) > 1:
        raise InstallError(error="SKILL.md frontmatter 无效", detail=f"{key} 重复")
    if indexes:
        lines[indexes[0]] = f"{key}: true"
    if not indexes:
        lines.append(f"{key}: true")
    return "---\n" + "\n".join(lines) + "\n---" + parts[2]


def install(
    *,
    source: Path,
    destination: Path,
    platform: str,
    upstream_sha: str,
) -> dict[str, str]:
    """参数为来源/目标/平台；预期覆盖复制并写三字段来源记录。"""
    skill_name = source.name
    if not source.is_dir() or not (source / "SKILL.md").is_file():
        raise InstallError(error="canonical Skill 不完整", detail=str(source))
    if destination.is_symlink() or destination.is_file():
        destination.unlink()
    if destination.is_dir():
        shutil.rmtree(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        src=source,
        dst=destination,
        symlinks=False,
        ignore=shutil.ignore_patterns(
            "__pycache__", "*.py[cod]", ".DS_Store", ".source.json"
        ),
    )
    skill_path = destination / "SKILL.md"
    if platform == "claude":
        skill_path.write_text(
            claude_text(text=skill_path.read_text(encoding="utf-8")),
            encoding="utf-8",
        )
    source_record = {
        "upstream_sha": upstream_sha,
        "canonical_relative_path": f"zh/skills/{skill_name}",
        "platform": platform,
    }
    (destination / ".source.json").write_text(
        json.dumps(source_record, ensure_ascii=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    return {
        "skill": skill_name,
        "platform": platform,
        "destination": str(destination),
        "action": "copied",
    }


def parse_args() -> Any:
    """无参数；预期返回 scope、目标仓库、upstream 路径和 SHA。"""
    parser = JsonArgumentParser(description="复制 Workflow Docs Sync Skill。")
    parser.add_argument("--scope", choices=("user", "repo"), default="user")
    parser.add_argument("--target-repo")
    parser.add_argument("--upstream-dir", required=True)
    parser.add_argument("--upstream-sha", required=True)
    args = parser.parse_args()
    if (args.scope == "repo") != (args.target_repo is not None):
        raise InstallError(
            error="参数无效",
            detail="只有 repo scope 必须且可以提供 --target-repo",
        )
    return args


def execute() -> dict[str, Any]:
    """无参数；预期从 clean pinned upstream 覆盖复制四个安装目录。"""
    args = parse_args()
    expected_sha = require_sha(value=args.upstream_sha, label="上游 SHA")
    upstream, actual_sha = require_repo(value=args.upstream_dir, label="上游目录")
    if actual_sha != expected_sha:
        raise InstallError(
            error="上游 SHA 不匹配",
            detail=f"期望 {expected_sha}，实际 {actual_sha}",
        )
    require_clean(repo_root=upstream, label="上游目录")
    if args.scope == "user":
        if "HOME" not in os.environ:
            raise InstallError(error="缺少用户目录", detail="user scope 需要 HOME")
        install_root = Path(os.environ["HOME"]).expanduser().resolve()
    if args.scope == "repo":
        install_root, _ = require_repo(value=args.target_repo, label="目标仓库")
    actions = [
        install(
            source=upstream / "zh/skills" / skill_name,
            destination=install_root / platform_root / skill_name,
            platform=platform,
            upstream_sha=actual_sha,
        )
        for skill_name in SKILL_NAMES
        for platform, platform_root in PLATFORM_ROOTS.items()
    ]
    return {
        "status": "passed", "scope": args.scope, "upstream_sha": actual_sha,
        "install_root": str(install_root), "actions": actions,
    }


def run_cli() -> int:
    """无参数；预期成功返回 0，已知本地错误返回 1。"""
    try:
        payload = execute()
    except InstallError as exc:
        emit_json(payload={"error": exc.error, "detail": exc.detail})
        return 1
    except (KeyError, OSError, TypeError, UnicodeError, ValueError) as exc:
        emit_json(
            payload={"error": "Skill 安装失败",
                     "detail": f"{type(exc).__name__}: {exc}"}
        )
        return 1
    emit_json(payload=payload)
    return 0


if __name__ == "__main__":
    sys.exit(run_cli())
