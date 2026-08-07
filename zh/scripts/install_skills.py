#!/usr/bin/env python3
"""安装 canonical workflow-docs-sync，并清理精确废弃的 reviewer Skill。"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


SKILL_NAME = "workflow-docs-sync"
OBSOLETE_SKILL_NAME = "workflow-docs-sync-review"
PLATFORM_ROOTS = {"codex": Path(".agents/skills"), "claude": Path(".claude/skills")}
SOURCE_IGNORE_PATTERNS = ("__pycache__", "*.py[cod]", ".DS_Store")


class InstallError(RuntimeError):
    """表示应立即停止的本地安装错误。"""


def git(*, repo_root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    """在指定路径运行 Git 并捕获 UTF-8 输出。"""
    environment = {**os.environ, "LC_ALL": "C"}
    return subprocess.run(
        args=["git", "-C", str(repo_root), *args],
        cwd=repo_root,
        env=environment,
        check=False,
        capture_output=True,
        encoding="utf-8",
        text=True,
    )


def require_clean_repo(*, value: str, label: str) -> Path:
    """验证路径恰好是 clean Git 工作树根目录。"""
    root = Path(value).expanduser().resolve(strict=True)
    top = git(repo_root=root, args=["rev-parse", "--show-toplevel"])
    if top.returncode != 0:
        raise InstallError(top.stderr.strip() or f"{label}不是 Git 仓库")
    actual = Path(top.stdout.strip()).resolve(strict=True)
    if actual != root:
        raise InstallError(f"{label}必须是 Git 根目录：{actual}")
    status_args = ["status", "--porcelain=v1", "--untracked-files=all"]
    status = git(repo_root=root, args=status_args)
    if status.returncode != 0:
        raise InstallError(status.stderr.strip() or f"无法读取{label}状态")
    if status.stdout:
        raise InstallError(f"{label}工作区不干净：{status.stdout.strip()}")
    return root


def claude_text(*, text: str) -> str:
    """为 Claude 副本添加禁止隐式调用的 frontmatter 标记。"""
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\r\n") != "---":
        raise InstallError("SKILL.md 缺少标准 YAML frontmatter")
    closing_index = next(
        (
            index
            for index, line in enumerate(lines[1:], start=1)
            if line.rstrip("\r\n") == "---"
        ),
        None,
    )
    if closing_index is None:
        raise InstallError("SKILL.md 缺少标准 YAML frontmatter")
    frontmatter = "".join(lines[1:closing_index]).rstrip("\r\n")
    body = "".join(lines[closing_index + 1 :])
    return (
        f"---\n{frontmatter}\ndisable-model-invocation: true\n---\n{body}"
    )


def remove_path(*, path: Path) -> bool:
    """删除一个精确路径，并返回是否实际删除。"""
    # 先识别 symlink，避免把外部目标目录当作本地目录递归删除。
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path=path)
    else:
        return False
    return True


def is_source_copy_ignored(*, relative_path: Path) -> bool:
    """判断 source entry 是否属于安装器明确不会复制的缓存。"""
    return any(
        fnmatch.fnmatchcase(name, pattern)
        for name in relative_path.parts
        for pattern in SOURCE_IGNORE_PATTERNS
    )


def validate_source(*, upstream_root: Path, source: Path) -> None:
    """在任何安装写入前验证 canonical Skill 可安全复制。"""
    # 从 Git 根逐层检查，避免 zh/ 或 skills/ symlink 隐藏仓库外 source。
    current = upstream_root
    for part in source.relative_to(upstream_root).parts:
        current /= part
        if current.is_symlink():
            raise InstallError(
                "canonical Skill 路径不能包含符号链接："
                f"{current.relative_to(upstream_root).as_posix()}"
            )
        if not current.is_dir():
            raise InstallError(f"canonical Skill 不完整：{source}")
    if (source / "SKILL.md").is_symlink() or not (
        source / "SKILL.md"
    ).is_file():
        raise InstallError(f"canonical Skill 不完整：{source}")
    # 拒绝 tracked symlink，避免 copytree 跟随链接读取仓库外 bytes。
    symlinks = sorted(
        path.relative_to(source).as_posix()
        for path in source.rglob("*")
        if path.is_symlink()
    )
    if symlinks:
        raise InstallError(f"canonical Skill 不能包含符号链接：{symlinks}")
    # 普通 status 看不到 ignored residue；拒绝任何会进入安装结果的
    # 此类文件。
    source_relative = source.relative_to(upstream_root)
    ignored = git(
        repo_root=upstream_root,
        args=[
            "ls-files",
            "-z",
            "--others",
            "--ignored",
            "--exclude-standard",
            "--directory",
            "--",
            source_relative.as_posix(),
        ],
    )
    if ignored.returncode != 0:
        raise InstallError(
            ignored.stderr.strip() or "无法检查 canonical Skill ignored path"
        )
    unsafe_ignored = sorted(
        path.relative_to(source_relative).as_posix()
        for value in ignored.stdout.split("\0")
        if value
        for path in (Path(value),)
        if not is_source_copy_ignored(
            relative_path=path.relative_to(source_relative)
        )
    )
    if unsafe_ignored:
        raise InstallError(
            f"canonical Skill 包含会被安装的 ignored path：{unsafe_ignored}"
        )
    # Claude 转换可能失败；先验证标准分隔，防止另一平台已写入。
    claude_text(text=(source / "SKILL.md").read_text(encoding="utf-8"))


def validate_install_parents(*, install_root: Path) -> None:
    """在任何删除前拒绝越出安装根的父路径 symlink 或非目录。"""
    for platform_root in PLATFORM_ROOTS.values():
        current = install_root
        for part in platform_root.parts:
            current /= part
            relative_path = current.relative_to(install_root).as_posix()
            if current.is_symlink():
                raise InstallError(
                    f"安装路径父级不能是符号链接：{relative_path}"
                )
            if current.exists() and not current.is_dir():
                raise InstallError(f"安装路径父级不是目录：{relative_path}")


def copy_skill(*, source: Path, destination: Path, platform: str) -> None:
    """覆盖一个明确目录并复制 canonical 单 Skill。"""
    remove_path(path=destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        src=source,
        dst=destination,
        symlinks=False,
        ignore=shutil.ignore_patterns(*SOURCE_IGNORE_PATTERNS),
    )
    if platform == "claude":
        skill_path = destination / "SKILL.md"
        text = claude_text(text=skill_path.read_text(encoding="utf-8"))
        skill_path.write_text(text, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    """解析 upstream、user/repo scope 和目标仓库。"""
    parser = argparse.ArgumentParser(description="安装 workflow-docs-sync。")
    parser.add_argument("--scope", choices=("user", "repo"), default="user")
    parser.add_argument("--target-repo")
    parser.add_argument("--upstream-dir", required=True)
    args = parser.parse_args()
    if (args.scope == "repo") != (args.target_repo is not None):
        parser.error("只有 repo scope 必须且可以提供 --target-repo")
    return args


def execute() -> dict[str, object]:
    """从 clean checkout 安装一个 Skill 并移除精确废弃路径。"""
    args = parse_args()
    upstream = require_clean_repo(value=args.upstream_dir, label="上游目录")
    install_root = (
        require_clean_repo(value=args.target_repo, label="目标仓库")
        if args.scope == "repo"
        else Path.home().resolve()
    )
    source = upstream / "zh/skills" / SKILL_NAME
    # 两个平台和 Claude 转换全部预检后才 mutation，避免半安装状态。
    validate_source(upstream_root=upstream, source=source)
    validate_install_parents(install_root=install_root)
    actions, removed_obsolete = [], []
    for platform, platform_root in PLATFORM_ROOTS.items():
        obsolete = install_root / platform_root / OBSOLETE_SKILL_NAME
        if remove_path(path=obsolete):
            removed_obsolete.append(str(obsolete))
        destination = install_root / platform_root / SKILL_NAME
        copy_skill(source=source, destination=destination, platform=platform)
        actions.append({"platform": platform, "destination": str(destination)})
    return {
        "status": "passed",
        "scope": args.scope,
        "skill": SKILL_NAME,
        "install_root": str(install_root),
        "removed_obsolete": removed_obsolete,
        "actions": actions,
    }


def run_cli() -> int:
    """运行安装器并以一行 JSON 报告成功或失败。"""
    try:
        payload = execute()
    except (InstallError, OSError, RuntimeError, UnicodeError) as exc:
        payload = {"status": "failed", "error": str(exc)}
        print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
        return 1
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    sys.exit(run_cli())
