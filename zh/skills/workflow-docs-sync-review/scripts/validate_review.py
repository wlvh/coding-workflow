#!/usr/bin/env python3
"""校验独立 review JSON，并绑定 clean pinned upstream 与真实 GitHub PR。"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = SKILL_ROOT / "references/review-schema.json"
SOURCE_PATH = SKILL_ROOT / ".source.json"
RESULTS_DIR = Path(".coding_workflow/skill_results")
RANKS = {"PASS": 0, "WARN": 1, "BLOCKER": 2}


class ReviewError(RuntimeError):
    """保存必须以单行 JSON 返回的 review 校验错误。"""

    def __init__(self, *, error: str, detail: str) -> None:
        """参数为摘要和证据；预期构造结构化异常。"""
        super().__init__(error)
        self.error = error
        self.detail = detail


class JsonArgumentParser(argparse.ArgumentParser):
    """把 argparse 错误转换为 ReviewError。"""

    def error(self, message: str) -> None:
        """参数为 argparse 消息；预期抛出单行 JSON 错误。"""
        raise ReviewError(error="参数无效", detail=message)


def emit_json(*, payload: dict[str, Any]) -> None:
    """参数为结果对象；预期 stdout 写一行 UTF-8 JSON。"""
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))


def run(*, args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    """参数为命令和 cwd；预期返回捕获 UTF-8 输出的进程结果。"""
    return subprocess.run(
        args=args,
        cwd=cwd,
        env=os.environ.copy(),
        check=False,
        capture_output=True, encoding="utf-8",
    )


def git(*, repo_root: Path, args: list[str]) -> Any:
    """参数为仓库和 Git 参数；预期返回捕获输出的进程结果。"""
    return run(args=["git", "-C", str(repo_root), *args], cwd=repo_root)


def require_sha(*, value: str, label: str) -> str:
    """参数为候选值和字段名；预期返回完整小写 Git SHA。"""
    if re.fullmatch(r"[0-9a-f]{40}", value) is None:
        raise ReviewError(
            error=f"{label}无效",
            detail="必须是 40 位小写十六进制 Git SHA",
        )
    return value


def require_repo(*, value: str, label: str) -> tuple[Path, str]:
    """参数为仓库路径和角色；预期返回规范根目录与 HEAD。"""
    repo_root = Path(value).expanduser().resolve(strict=True)
    result = git(
        repo_root=repo_root, args=["rev-parse", "--show-toplevel", "HEAD"]
    )
    lines = result.stdout.splitlines()
    if result.returncode != 0 or len(lines) != 2:
        raise ReviewError(
            error=f"{label}无效",
            detail=result.stderr.strip() or "无法解析仓库根目录和 HEAD",
        )
    actual_root = Path(lines[0]).resolve(strict=True)
    if actual_root != repo_root:
        raise ReviewError(
            error=f"{label}必须是仓库根目录",
            detail=f"传入 {repo_root}，实际 {actual_root}",
        )
    return repo_root, require_sha(value=lines[1], label=f"{label} HEAD")


def status_text(*, repo_root: Path, tracked_only: bool) -> str:
    """参数为仓库和 tracked 开关；预期返回 NUL Git status 原文。"""
    untracked_arg = f"--untracked-files={'no' if tracked_only else 'all'}"
    result = git(
        repo_root=repo_root,
        args=["status", "--porcelain=v1", "-z", untracked_arg],
    )
    if result.returncode != 0:
        raise ReviewError(error="无法读取 Git 状态", detail=result.stderr.strip())
    return result.stdout


def require_upstream(*, value: str, expected_sha: str) -> tuple[Path, str]:
    """参数为 upstream 路径/SHA；预期返回 clean pinned checkout。"""
    expected_sha = require_sha(value=expected_sha, label="上游 SHA")
    upstream, actual_sha = require_repo(value=value, label="上游目录")
    if actual_sha != expected_sha:
        raise ReviewError(
            error="上游 SHA 不匹配",
            detail=f"期望 {expected_sha}，实际 {actual_sha}",
        )
    if status_text(repo_root=upstream, tracked_only=False):
        raise ReviewError(
            error="上游目录工作区不干净",
            detail="存在 tracked 或 untracked 改动",
        )
    return upstream, actual_sha


def validate_install_source(*, upstream_sha: str) -> None:
    """参数为调用 SHA；预期安装副本的三字段来源记录与其一致。"""
    if not SOURCE_PATH.is_file():
        return
    source = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    if (
        not isinstance(source, dict)
        or set(source) != {
            "upstream_sha", "canonical_relative_path", "platform"
        }
        or source["canonical_relative_path"]
        != "zh/skills/workflow-docs-sync-review"
        or source["platform"] not in {"codex", "claude"}
    ):
        raise ReviewError(
            error="reviewer Skill 来源记录无效",
            detail=".source.json 必须是合法三字段安装记录",
        )
    if source["upstream_sha"] != upstream_sha:
        raise ReviewError(
            error="reviewer Skill 来源 SHA 不匹配",
            detail=f"安装 {source['upstream_sha']}，调用 {upstream_sha}",
        )


def review_path(*, repo_root: Path, value: str) -> Path:
    """参数为仓库和结果路径；预期返回 skill_results 内真实文件。"""
    candidate = Path(value).expanduser()
    candidate = candidate if candidate.is_absolute() else repo_root / candidate
    resolved = candidate.resolve(strict=True)
    try:
        resolved.relative_to((repo_root / RESULTS_DIR).resolve())
    except ValueError as exc:
        raise ReviewError(
            error="review 路径无效",
            detail=f"必须位于 {RESULTS_DIR}/",
        ) from exc
    return resolved


def query_pr(*, repo_root: Path, number: int) -> dict[str, Any]:
    """参数为仓库和 PR number；预期返回真实 open PR identity。"""
    result = run(
        args=[
            "gh", "pr", "view", str(number), "--json",
            "number,state,headRefOid,body",
        ],
        cwd=repo_root,
    )
    if result.returncode != 0:
        raise ReviewError(
            error="无法读取实际审查 PR",
            detail=result.stderr.strip() or result.stdout.strip(),
        )
    payload = json.loads(result.stdout)
    if (
        not isinstance(payload, dict)
        or set(payload) != {"number", "state", "headRefOid", "body"}
        or payload["number"] != number
        or payload["state"] != "OPEN" or not isinstance(payload["body"], str)
    ):
        raise ReviewError(
            error="实际审查 PR identity 不匹配",
            detail=repr(payload),
        )
    require_sha(value=payload["headRefOid"], label="实际 PR head")
    return payload


def validate_review(*, review: Any, schema: Any) -> list[str]:
    """参数为 review/schema；预期返回全部形状与 verdict 派生错误。"""
    if not isinstance(review, dict) or not isinstance(schema, dict):
        return ["review 与 schema 根节点必须是对象"]
    properties = schema["properties"]
    required = set(schema["required"])
    errors = [
        f"$ 缺少字段 {key}" for key in required if key not in review
    ] + [
        f"$ 包含未声明字段 {key}"
        for key in review
        if key not in properties
    ]
    if errors:
        return errors
    levels: list[str] = []
    findings = review["findings"]
    if not isinstance(findings, list):
        errors.append("$.findings 必须是数组")
    else:
        for index, finding in enumerate(findings):
            if (
                not isinstance(finding, dict)
                or set(finding) != {"level", "claim", "evidence"}
                or finding["level"] not in RANKS
                or not isinstance(finding["claim"], str)
                or not finding["claim"].strip()
                or not isinstance(finding["evidence"], str)
                or not finding["evidence"].strip()
            ):
                errors.append(f"$.findings[{index}] 字段无效")
            else:
                levels.append(finding["level"])
    sections = review["review_sections"]
    expected_sections = set(properties["review_sections"]["required"])
    if not isinstance(sections, dict) or set(sections) != expected_sections:
        errors.append("$.review_sections 字段无效")
    else:
        for name in sorted(expected_sections):
            section = sections[name]
            if (
                not isinstance(section, dict)
                or set(section) != {"verdict", "evidence"}
                or section["verdict"] not in RANKS
                or not isinstance(section["evidence"], str)
                or not section["evidence"].strip()
            ):
                errors.append(f"$.review_sections.{name} 字段无效")
            else:
                levels.append(section["verdict"])
    if (
        not isinstance(review["pr"], int)
        or isinstance(review["pr"], bool)
        or review["pr"] < 1
    ):
        errors.append("$.pr 必须是正整数")
    for key in ("head_sha", "upstream_sha"):
        if (
            not isinstance(review[key], str)
            or re.fullmatch(r"[0-9a-f]{40}", review[key]) is None
        ):
            errors.append(f"$.{key} 必须是完整 SHA")
    evidence = review["evidence_index"]
    if (
        not isinstance(evidence, list)
        or not evidence
        or not all(isinstance(item, str) and item.strip() for item in evidence)
    ):
        errors.append("$.evidence_index 必须是非空字符串数组")
    if review["verdict"] not in RANKS:
        errors.append("$.verdict 非法")
    elif levels and review["verdict"] != max(
        levels,
        key=lambda value: RANKS[value],
    ):
        errors.append("顶层 verdict 必须等于 sections/findings 最高等级")
    return errors


def parse_args() -> Any:
    """无参数；预期返回五个必填 CLI 值。"""
    parser = JsonArgumentParser(description="校验独立 review JSON。")
    for name in ("target-repo", "upstream-dir", "upstream-sha", "review-file"):
        parser.add_argument(f"--{name}", required=True)
    parser.add_argument("--pr-number", required=True, type=int)
    args = parser.parse_args()
    if args.pr_number < 1:
        raise ReviewError(error="参数无效", detail="pr-number 必须为正整数")
    return args


def execute() -> dict[str, Any]:
    """无参数；预期绑定 upstream、真实 PR、target HEAD 与 review JSON。"""
    args = parse_args()
    _, upstream_sha = require_upstream(
        value=args.upstream_dir, expected_sha=args.upstream_sha
    )
    validate_install_source(upstream_sha=upstream_sha)
    target, target_head = require_repo(value=args.target_repo, label="目标仓库")
    if status_text(repo_root=target, tracked_only=False):
        raise ReviewError(
            error="目标仓库工作区不干净", detail="不得有 tracked 或 untracked 改动",
        )
    pull_request = query_pr(repo_root=target, number=args.pr_number)
    auto = re.search(
        r"(?s)<!-- sync:auto:start -->(.*?)<!-- sync:auto:end -->",
        pull_request["body"],
    )
    declared = [] if auto is None else re.findall(
        r"(?m)^- upstream_resolved_commit: ([0-9a-f]{40})$",
        auto.group(1),
    )
    if declared != [upstream_sha]:
        raise ReviewError(
            error="PR body upstream SHA 不匹配",
            detail=f"期望唯一声明 {upstream_sha}，实际 {declared}",
        )
    path = review_path(repo_root=target, value=args.review_file)
    review = json.loads(path.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = validate_review(review=review, schema=schema)
    if isinstance(review, dict) and not errors:
        expected = {
            "pr": pull_request["number"],
            "head_sha": pull_request["headRefOid"],
            "upstream_sha": upstream_sha,
        }
        for key, value in expected.items():
            if review[key] != value:
                errors.append(f"review.{key} 与真实值不一致")
        if target_head != pull_request["headRefOid"]:
            errors.append("目标仓库 HEAD 与实际 PR head 不一致")
    if errors:
        raise ReviewError(
            error="审查结果校验失败",
            detail="；".join(errors),
        )
    return {
        "status": "passed", "review_file": str(path), "pr": review["pr"],
        "head_sha": review["head_sha"], "verdict": review["verdict"],
    }


def run_cli() -> int:
    """无参数；预期成功返回 0，已知本地错误返回 1。"""
    try:
        payload = execute()
    except ReviewError as exc:
        emit_json(payload={"error": exc.error, "detail": exc.detail})
        return 1
    except (KeyError, OSError, TypeError, UnicodeError, ValueError) as exc:
        emit_json(
            payload={
                "error": "review validator 执行失败",
                "detail": f"{type(exc).__name__}: {exc}",
            }
        )
        return 1
    emit_json(payload=payload)
    return 0


if __name__ == "__main__":
    sys.exit(run_cli())
