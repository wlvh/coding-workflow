#!/usr/bin/env python3
"""在 mode 边界检查 Workflow Docs Sync。

调用关系：main -> run_cli -> dispatch -> prepare/start-pass/finish-pass/
prepare-submit/seal-submit/finish-submit/status。输出为 run、baseline 和 result JSON。
只防善意漏步骤、顺手越权和提交事实错误，不防同权限主动恶意执行者。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


MODES = ("PREPARE", "PASS_1", "PASS_2", "PASS_3", "PASS_4", "SUBMIT")
PASS_MODES = ("PASS_1", "PASS_2", "PASS_3", "PASS_4")
RUNTIME_DIR = Path(".coding_workflow/skill_runtime")
RESULTS_DIR = Path(".coding_workflow/skill_results")
RUN_PATH = RUNTIME_DIR / "run.json"
BASELINES_DIR = RUNTIME_DIR / "baselines"
OWNERSHIP_PATH = (
    Path(__file__).resolve().parents[1] / "references/pass_ownership.json"
)
SKILL_ROOT = Path(__file__).resolve().parents[1]
SOURCE_METADATA_PATH = SKILL_ROOT / ".source.json"
WORKFLOW_EXTRA_PATHS = {".gitignore", "PR_BODY.md"}
AGENT_SECTIONS = (
    "repo_facts_map",
    "full_document_reconcile",
    "pr_test_evidence",
    "upstream_drift_log",
    "agent_execution_evidence",
    "remaining_human_decisions",
)


class HarnessError(RuntimeError):
    """表示必须 fail-fast 的可预期 harness 错误。"""

    def __init__(
        self,
        *,
        error: str,
        detail: str,
        extra: dict[str, Any] | None = None,
    ) -> None:
        """参数为错误、证据和附加字段；预期构造可序列化异常。"""
        super().__init__(error)
        self.error = error
        self.detail = detail
        self.extra = {} if extra is None else extra


class JsonArgumentParser(argparse.ArgumentParser):
    """把非法参数转换为单行 JSON 错误。"""

    def error(self, message: str) -> None:
        """参数为 argparse 消息；预期抛出 HarnessError。"""
        raise HarnessError(error="参数无效", detail=message)


def emit_json(*, payload: dict[str, Any]) -> None:
    """参数为结果对象；预期 stdout 恰好写一行 UTF-8 JSON。"""
    print(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
        file=sys.stdout,
    )


def utc_now() -> str:
    """无参数；预期返回秒级 UTC ISO 8601 字符串。"""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_process(
    *,
    args: list[str],
    cwd: Path,
    env: dict[str, str],
) -> subprocess.CompletedProcess[str]:
    """参数为拆分命令、cwd 和环境；预期返回捕获 UTF-8 输出的进程结果。"""
    return subprocess.run(
        args=args,
        cwd=cwd,
        env=env,
        check=False,
        capture_output=True,
        encoding="utf-8",
        text=True,
    )


def run_git(
    *,
    repo_root: Path,
    args: list[str],
) -> subprocess.CompletedProcess[str]:
    """参数为仓库根目录和 Git 参数；预期返回捕获输出的进程结果。"""
    return run_process(
        args=["git", "-C", str(repo_root), *args],
        cwd=repo_root,
        env=os.environ.copy(),
    )


def require_full_sha(*, value: str, label: str) -> str:
    """参数为候选值和字段名；预期返回 40 位小写 Git SHA。"""
    if re.fullmatch(r"[0-9a-f]{40}", value) is None:
        raise HarnessError(
            error=f"{label}无效",
            detail="必须是 40 位小写十六进制 Git SHA",
        )
    return value


def require_repository(*, path: Path, label: str) -> tuple[Path, str]:
    """参数为仓库路径和角色名；预期返回规范根目录与完整 HEAD。"""
    resolved = path.expanduser().resolve(strict=True)
    if not resolved.is_dir():
        raise HarnessError(error=f"{label}无效", detail=f"不是目录：{resolved}")
    result = run_git(
        repo_root=resolved,
        args=["rev-parse", "--show-toplevel", "HEAD"],
    )
    lines = result.stdout.splitlines()
    if result.returncode != 0 or len(lines) != 2:
        raise HarnessError(
            error=f"{label}无效",
            detail=result.stderr.strip() or "无法解析仓库根目录和 HEAD",
        )
    repo_root = Path(lines[0]).resolve(strict=True)
    if repo_root != resolved:
        raise HarnessError(
            error=f"{label}必须是仓库根目录",
            detail=f"传入 {resolved}，实际根目录 {repo_root}",
        )
    return repo_root, require_full_sha(value=lines[1], label=f"{label} HEAD")


def git_status_paths(
    *,
    repo_root: Path,
    tracked_only: bool = False,
) -> list[str]:
    """参数为仓库和未跟踪开关；预期返回含 rename 两端的排序 dirty 路径。"""
    untracked = "no" if tracked_only else "all"
    result = run_git(
        repo_root=repo_root,
        args=[
            "status",
            "--porcelain=v1",
            "-z",
            f"--untracked-files={untracked}",
        ],
    )
    if result.returncode != 0:
        raise HarnessError(
            error="无法读取 Git 状态",
            detail=result.stderr.strip(),
        )
    fields = iter(result.stdout.split("\0"))
    paths: list[str] = []
    for row in fields:
        if not row:
            continue
        if len(row) < 4 or row[2] != " ":
            raise HarnessError(error="无法解析 Git 状态", detail=repr(row))
        paths.append(row[3:])
        if row[0] in {"R", "C"} or row[1] in {"R", "C"}:
            source = next(fields, "")
            if not source:
                raise HarnessError(
                    error="无法解析 Git 状态",
                    detail="rename/copy 缺少原路径",
                )
            paths.append(source)
    return sorted(set(paths))


def require_clean_repository(*, repo_root: Path, label: str) -> None:
    """参数为仓库和角色名；预期仓库干净，否则列出 dirty 路径。"""
    dirty_paths = git_status_paths(repo_root=repo_root)
    if dirty_paths:
        raise HarnessError(
            error=f"{label}工作区不干净",
            detail=", ".join(dirty_paths),
            extra={"dirty_paths": dirty_paths},
        )


def require_upstream(
    *,
    upstream_dir_value: str,
    upstream_sha_value: str,
) -> tuple[Path, str]:
    """参数为 upstream 路径和 SHA；预期返回 clean pinned 根目录与 SHA。"""
    expected_sha = require_full_sha(
        value=upstream_sha_value,
        label="上游 SHA",
    )
    upstream_dir, actual_sha = require_repository(
        path=Path(upstream_dir_value),
        label="上游目录",
    )
    if actual_sha != expected_sha:
        raise HarnessError(
            error="上游 SHA 不匹配",
            detail=f"期望 {expected_sha}，实际 {actual_sha}",
        )
    require_clean_repository(repo_root=upstream_dir, label="上游目录")
    return upstream_dir, actual_sha


def validate_source_metadata(*, upstream_sha: str) -> None:
    """参数为 pinned SHA；预期 canonical 通过、安装副本来源 SHA 一致。"""
    if not SOURCE_METADATA_PATH.is_file():
        return
    metadata = read_json(path=SOURCE_METADATA_PATH)
    required = {"upstream_sha", "canonical_relative_path", "platform"}
    if not isinstance(metadata, dict) or set(metadata) != required:
        raise HarnessError(
            error="Skill 来源记录无效",
            detail=f"字段必须精确为：{', '.join(sorted(required))}",
        )
    if (
        metadata["upstream_sha"] != upstream_sha
        or metadata["canonical_relative_path"]
        != "zh/skills/workflow-docs-sync"
        or metadata["platform"] not in {"codex", "claude"}
    ):
        raise HarnessError(
            error="Skill 来源 SHA 不匹配",
            detail="切换 upstream SHA 后必须重新安装 Skill",
        )


def read_json(*, path: Path) -> Any:
    """参数为 JSON 路径；预期返回 UTF-8 解析值。"""
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(*, path: Path, payload: dict[str, Any]) -> None:
    """参数为路径和对象；预期原子写入带尾换行的 UTF-8 JSON。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
    text = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
    temporary.write_text(text + "\n", encoding="utf-8")
    temporary.replace(path)


def read_pr_body(*, repo_root: Path) -> str | None:
    """参数为目标仓库；预期返回本地 PR body，缺失时返回 None。"""
    path = repo_root / "PR_BODY.md"
    return path.read_text(encoding="utf-8") if path.is_file() else None


def load_ownership() -> dict[str, Any]:
    """无参数；预期返回精确覆盖四个 PASS 的 ownership。"""
    ownership = read_json(path=OWNERSHIP_PATH)
    if not isinstance(ownership, dict) or set(ownership) != set(PASS_MODES):
        raise HarnessError(
            error="PASS ownership 无效",
            detail="必须精确覆盖 PASS_1 至 PASS_4",
        )
    for mode in PASS_MODES:
        entry = ownership[mode]
        required = {"title", "owned", "pr_body_sections"}
        if not isinstance(entry, dict) or set(entry) != required:
            raise HarnessError(
                error="PASS ownership 无效",
                detail=f"{mode} 字段必须精确为 title/owned/pr_body_sections",
            )
        if (
            not isinstance(entry["title"], str)
            or not entry["title"]
            or not isinstance(entry["owned"], list)
            or not entry["owned"]
            or not all(
                isinstance(path, str) and path
                for path in entry["owned"]
            )
            or not isinstance(entry["pr_body_sections"], list)
            or not all(
                isinstance(section, str) and section in AGENT_SECTIONS
                for section in entry["pr_body_sections"]
            )
        ):
            raise HarnessError(
                error="PASS ownership 无效",
                detail=f"{mode} 含非法 title、owned 或 pr_body_sections",
            )
    return ownership


def all_owned_paths(*, ownership: dict[str, Any]) -> set[str]:
    """参数为 ownership；预期返回全部 owned 仓库相对路径并集。"""
    paths: set[str] = set()
    for mode in PASS_MODES:
        paths.update(ownership[mode]["owned"])
    return paths


def is_runtime_path(*, path: str) -> bool:
    """参数为仓库路径；预期 runtime、result 或 sync scratch 返回 True。"""
    roots = (
        ".coding_workflow/diffs",
        str(RUNTIME_DIR),
        str(RESULTS_DIR),
    )
    return any(
        path == root or path.startswith(f"{root}/")
        for root in roots
    )


def ordinary_dirty_paths(*, repo_root: Path) -> list[str]:
    """参数为目标仓库；预期返回排除 runtime 的排序 dirty 路径。"""
    return [
        path
        for path in git_status_paths(repo_root=repo_root)
        if not is_runtime_path(path=path)
    ]


def assert_dirty_allowed(
    *,
    repo_root: Path,
    allowed_paths: set[str],
    error: str,
) -> list[str]:
    """参数为仓库、允许集合和错误名；预期返回 dirty 路径或越权失败。"""
    dirty_paths = ordinary_dirty_paths(repo_root=repo_root)
    unauthorized = [
        path for path in dirty_paths if path not in allowed_paths
    ]
    if unauthorized:
        raise HarnessError(
            error=error,
            detail=", ".join(unauthorized),
            extra={"unauthorized_paths": unauthorized},
        )
    return dirty_paths


def snapshot_path(*, repo_root: Path, relative_path: str) -> dict[str, Any]:
    """参数为仓库和相对路径；预期返回可比较的存在性与内容摘要。"""
    path = repo_root / relative_path
    if path.is_symlink():
        target = os.readlink(path)
        return {
            "kind": "symlink",
            "sha256": hashlib.sha256(
                target.encode("utf-8")
            ).hexdigest(),
        }
    if path.is_file():
        return {
            "kind": "file",
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "executable": bool(path.stat().st_mode & 0o111),
        }
    if path.exists():
        raise HarnessError(
            error="无法记录文件快照",
            detail=f"不支持目录路径：{relative_path}",
        )
    return {"kind": "missing", "sha256": None}


def snapshot_workflow(
    *,
    repo_root: Path,
    workflow_paths: set[str],
) -> dict[str, Any]:
    """参数为仓库和 workflow 路径；预期返回逐文件内容快照。"""
    return {
        path: snapshot_path(repo_root=repo_root, relative_path=path)
        for path in sorted(workflow_paths)
    }


def changed_snapshot_paths(
    *,
    baseline: dict[str, Any],
    current: dict[str, Any],
) -> list[str]:
    """参数为起止快照；预期返回内容或存在性变化的排序路径。"""
    if set(baseline) != set(current):
        raise HarnessError(
            error="workflow 快照无效",
            detail="baseline 与 current 路径集合不同",
        )
    return sorted(
        path
        for path in baseline
        if baseline[path] != current[path]
    )


def validate_run_state(*, state: Any) -> dict[str, Any]:
    """参数为 run JSON；预期返回字段、顺序和类型合法的状态。"""
    required = {
        "schema_version", "run_id", "upstream_dir", "upstream_sha",
        "project_head", "completed_modes", "active_mode",
        "boundary_snapshot", "boundary_dirty_paths", "submit_ready",
        "started_at_utc", "updated_at_utc",
    }
    if not isinstance(state, dict) or set(state) != required:
        raise HarnessError(
            error="workflow run 状态无效",
            detail=f"字段必须精确为：{', '.join(sorted(required))}",
        )
    completed = state["completed_modes"]
    if (
        state["schema_version"] != 1
        or not isinstance(state["run_id"], str)
        or not state["run_id"]
        or not isinstance(completed, list)
        or completed != list(MODES[:len(completed)])
        or state["active_mode"] not in (None, *MODES)
        or not isinstance(state["boundary_snapshot"], dict)
        or not isinstance(state["boundary_dirty_paths"], list)
        or not isinstance(state["submit_ready"], bool)
    ):
        raise HarnessError(
            error="workflow run 状态无效",
            detail="schema、顺序或字段类型非法",
        )
    require_full_sha(value=state["upstream_sha"], label="状态 upstream_sha")
    require_full_sha(value=state["project_head"], label="状态 project_head")
    return state


def load_run_state(*, repo_root: Path) -> dict[str, Any]:
    """参数为目标仓库；预期返回已校验的 run state。"""
    path = repo_root / RUN_PATH
    if not path.is_file():
        raise HarnessError(
            error="缺少 workflow run 状态",
            detail="必须先执行 prepare",
        )
    return validate_run_state(state=read_json(path=path))


def write_run_state(*, repo_root: Path, state: dict[str, Any]) -> None:
    """参数为仓库和状态；预期校验后原子替换 run.json。"""
    state["updated_at_utc"] = utc_now()
    write_json(
        path=repo_root / RUN_PATH,
        payload=validate_run_state(state=state),
    )


def validate_baseline(*, baseline: Any, mode: str) -> dict[str, Any]:
    """参数为 baseline 和 mode；预期返回字段精确且 mode 匹配的对象。"""
    required = {
        "schema_version", "run_id", "mode", "upstream_sha", "start_head",
        "snapshot", "dirty_paths", "allowed_commit_paths", "pr_body_text",
        "created_at_utc",
    }
    if (
        not isinstance(baseline, dict)
        or set(baseline) != required
        or baseline["schema_version"] != 1
        or baseline["mode"] != mode
        or not isinstance(baseline["snapshot"], dict)
        or not isinstance(baseline["dirty_paths"], list)
        or not isinstance(baseline["allowed_commit_paths"], list)
        or baseline["pr_body_text"] is not None
        and not isinstance(baseline["pr_body_text"], str)
    ):
        raise HarnessError(
            error="mode baseline 无效",
            detail=f"{mode} baseline 字段或类型非法",
        )
    require_full_sha(value=baseline["upstream_sha"], label="baseline SHA")
    require_full_sha(value=baseline["start_head"], label="baseline HEAD")
    return baseline


def load_baseline(*, repo_root: Path, mode: str) -> dict[str, Any]:
    """参数为仓库和 mode；预期返回已校验的 baseline。"""
    path = repo_root / BASELINES_DIR / f"{mode}.json"
    if not path.is_file():
        raise HarnessError(
            error="缺少 mode baseline",
            detail=f"必须先执行 {mode} 起始命令",
        )
    return validate_baseline(
        baseline=read_json(path=path),
        mode=mode,
    )


def write_baseline(
    *,
    repo_root: Path,
    run_id: str,
    mode: str,
    upstream_sha: str,
    start_head: str,
    snapshot: dict[str, Any],
    dirty_paths: list[str],
    allowed_commit_paths: list[str],
) -> dict[str, Any]:
    """参数为 mode 起始事实；预期写入并返回轻量 baseline。"""
    baseline = {
        "schema_version": 1,
        "run_id": run_id,
        "mode": mode,
        "upstream_sha": upstream_sha,
        "start_head": start_head,
        "snapshot": snapshot,
        "dirty_paths": dirty_paths,
        "allowed_commit_paths": allowed_commit_paths,
        "pr_body_text": read_pr_body(repo_root=repo_root),
        "created_at_utc": utc_now(),
    }
    write_json(
        path=repo_root / BASELINES_DIR / f"{mode}.json",
        payload=validate_baseline(baseline=baseline, mode=mode),
    )
    return baseline


def write_result(
    *,
    repo_root: Path,
    run_id: str,
    mode: str,
    upstream_sha: str,
    project_head: str,
    changed_paths: list[str],
    details: dict[str, Any],
) -> dict[str, Any]:
    """参数为真实 mode 事实；预期原子写入并返回 passed result。"""
    payload = {
        "schema_version": 1,
        "run_id": run_id,
        "mode": mode,
        "status": "passed",
        "upstream_sha": upstream_sha,
        "project_head": project_head,
        "created_at_utc": utc_now(),
        "changed_paths": changed_paths,
        "details": details,
        "error": None,
    }
    write_json(path=repo_root / RESULTS_DIR / f"{mode}.json", payload=payload)
    return payload


def run_pinned_sync(
    *,
    target_repo: Path,
    upstream_dir: Path,
    final: bool,
) -> dict[str, Any]:
    """参数为目标、upstream 和 final 开关；预期返回成功 pinned sync 事实。"""
    sync_script = upstream_dir / "zh/scripts/sync.sh"
    if not sync_script.is_file():
        raise HarnessError(
            error="pinned sync 入口缺失",
            detail=str(sync_script),
        )
    command = ["bash", str(sync_script)]
    if final:
        command.append("--final")
    env = os.environ.copy()
    env["CODING_WORKFLOW_UPSTREAM_DIR"] = str(upstream_dir)
    result = run_process(args=command, cwd=target_repo, env=env)
    if result.returncode != 0:
        raise HarnessError(
            error="pinned final gate 失败" if final else "pinned sync 失败",
            detail=(
                f"退出码 {result.returncode}\n"
                f"stdout:\n{result.stdout[-4000:] or '无'}\n"
                f"stderr:\n{result.stderr[-4000:] or '无'}"
            ),
            extra={"returncode": result.returncode},
        )
    if not final:
        required_outputs = (
            Path(".coding_workflow/diffs/agent_workorder.md"),
            Path(".coding_workflow/diffs/sync_state.json"),
        )
        missing = [
            str(path)
            for path in required_outputs
            if not (target_repo / path).is_file()
        ]
        if missing:
            raise HarnessError(
                error="pinned sync 产物缺失",
                detail=", ".join(missing),
            )
    return {
        "command": command,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def require_state_upstream(
    *,
    state: dict[str, Any],
    upstream_dir: Path,
    upstream_sha: str,
) -> None:
    """参数为状态和 upstream；预期路径与 SHA 同时一致。"""
    if (
        state["upstream_dir"] != str(upstream_dir)
        or state["upstream_sha"] != upstream_sha
    ):
        raise HarnessError(
            error="workflow run 上游不一致",
            detail=(
                f"状态 {state['upstream_dir']}@{state['upstream_sha']}，"
                f"当前 {upstream_dir}@{upstream_sha}"
            ),
        )


def require_boundary_unchanged(
    *,
    repo_root: Path,
    state: dict[str, Any],
    workflow_paths: set[str],
) -> None:
    """参数为仓库、状态和路径；预期 mode 间快照与 dirty 集合未变化。"""
    current_snapshot = snapshot_workflow(
        repo_root=repo_root,
        workflow_paths=workflow_paths,
    )
    changed = changed_snapshot_paths(
        baseline=state["boundary_snapshot"],
        current=current_snapshot,
    )
    current_dirty = ordinary_dirty_paths(repo_root=repo_root)
    if changed or current_dirty != state["boundary_dirty_paths"]:
        raise HarnessError(
            error="mode 间发现未归属改动",
            detail=(
                f"内容变化：{changed}；"
                f"上次 dirty：{state['boundary_dirty_paths']}；"
                f"当前 dirty：{current_dirty}"
            ),
            extra={
                "changed_paths": changed,
                "previous_dirty_paths": state["boundary_dirty_paths"],
                "current_dirty_paths": current_dirty,
            },
        )


def parse_agent_sections(*, text: str) -> tuple[str, dict[str, str]]:
    """参数为 PR body；预期返回占位骨架和 agent section 内容。"""
    cursor = 0
    skeleton_parts: list[str] = []
    sections: dict[str, str] = {}
    for section_name in AGENT_SECTIONS:
        start_marker = f"<!-- sync:agent:start {section_name} -->"
        end_marker = f"<!-- sync:agent:end {section_name} -->"
        start_index = text.find(start_marker, cursor)
        if start_index < 0:
            raise HarnessError(
                error="PR_BODY agent section 缺失",
                detail=section_name,
            )
        body_start = start_index + len(start_marker)
        end_index = text.find(end_marker, body_start)
        if end_index < 0:
            raise HarnessError(
                error="PR_BODY agent section 未闭合",
                detail=section_name,
            )
        skeleton_parts.append(text[cursor:body_start])
        skeleton_parts.append(f"<SECTION:{section_name}>")
        skeleton_parts.append(end_marker)
        sections[section_name] = text[body_start:end_index]
        cursor = end_index + len(end_marker)
    skeleton_parts.append(text[cursor:])
    return "".join(skeleton_parts), sections


def assert_pr_body_scope(
    *,
    baseline_text: str | None,
    current_text: str | None,
    allowed_sections: set[str],
) -> None:
    """参数为起止 body 和允许 section；预期其他区域完全不变。"""
    if baseline_text is None or current_text is None:
        raise HarnessError(
            error="PR_BODY scope 无法校验",
            detail="PASS 开始和结束都必须存在 PR_BODY.md",
        )
    baseline_skeleton, baseline_sections = parse_agent_sections(
        text=baseline_text,
    )
    current_skeleton, current_sections = parse_agent_sections(
        text=current_text,
    )
    if baseline_skeleton != current_skeleton:
        raise HarnessError(
            error="PR_BODY 非 agent-owned 区域被修改",
            detail="PASS 只能修改允许的 sentinel section",
        )
    unauthorized = [
        section_name
        for section_name in AGENT_SECTIONS
        if section_name not in allowed_sections
        and baseline_sections[section_name] != current_sections[section_name]
    ]
    if unauthorized:
        raise HarnessError(
            error="PR_BODY section 越权",
            detail=", ".join(unauthorized),
            extra={"unauthorized_sections": unauthorized},
        )


def git_paths_between(
    *,
    repo_root: Path,
    start_sha: str,
    end_sha: str,
) -> list[str]:
    """参数为仓库和起止 SHA；预期返回排序 committed path。"""
    result = run_git(
        repo_root=repo_root,
        args=["diff", "--name-only", "-z", f"{start_sha}..{end_sha}", "--"],
    )
    if result.returncode != 0:
        raise HarnessError(
            error="无法读取 SUBMIT committed scope",
            detail=result.stderr.strip(),
        )
    return sorted(
        path for path in set(result.stdout.split("\0")) if path
    )


def git_commit_count_between(
    *,
    repo_root: Path,
    start_sha: str,
    end_sha: str,
) -> int:
    """参数为仓库和起止 SHA；预期返回两者之间的 commit 数。"""
    result = run_git(
        repo_root=repo_root,
        args=["rev-list", "--count", f"{start_sha}..{end_sha}"],
    )
    count = result.stdout.strip()
    if result.returncode != 0 or not count.isdecimal():
        raise HarnessError(
            error="无法读取 SUBMIT commit 数",
            detail=result.stderr.strip() or repr(count),
        )
    return int(count)


def query_pull_request(
    *,
    repo_root: Path,
    pr_number: int,
) -> dict[str, Any]:
    """参数为仓库和 PR number；预期返回真实 state/head/base/body。"""
    result = run_process(
        args=[
            "gh", "pr", "view", str(pr_number), "--json",
            "number,state,headRefOid,headRefName,baseRefName,body,url",
        ],
        cwd=repo_root,
        env=os.environ.copy(),
    )
    if result.returncode != 0:
        raise HarnessError(
            error="无法读取 GitHub PR",
            detail=result.stderr.strip() or result.stdout.strip(),
        )
    payload = json.loads(result.stdout)
    required = {
        "number", "state", "headRefOid", "headRefName", "baseRefName",
        "body", "url",
    }
    if not isinstance(payload, dict) or set(payload) != required:
        raise HarnessError(
            error="GitHub PR 证据无效",
            detail="字段不完整或含未声明字段",
        )
    return payload


def common_context(
    *,
    args: Any,
) -> tuple[Path, str, Path, str, dict[str, Any], set[str]]:
    """参数为公共 CLI 值；预期返回仓库、upstream 和 ownership 事实。"""
    target_repo, project_head = require_repository(
        path=Path(args.target_repo), label="目标仓库"
    )
    upstream_dir, upstream_sha = require_upstream(
        upstream_dir_value=args.upstream_dir,
        upstream_sha_value=args.upstream_sha,
    )
    validate_source_metadata(upstream_sha=upstream_sha)
    ownership = load_ownership()
    workflow_paths = (
        all_owned_paths(ownership=ownership) | WORKFLOW_EXTRA_PATHS
    )
    return (
        target_repo, project_head, upstream_dir,
        upstream_sha, ownership, workflow_paths,
    )


def bound_context(
    *, args: Any
) -> tuple[Path, str, Path, str, dict[str, Any], set[str], dict[str, Any]]:
    """参数为公共 CLI 值；预期追加已绑定的 run state。"""
    context = common_context(args=args)
    state = load_run_state(repo_root=context[0])
    require_state_upstream(
        state=state, upstream_dir=context[2], upstream_sha=context[3]
    )
    return (*context, state)


def prepare(*, args: Any) -> dict[str, Any]:
    """参数为 PREPARE CLI；预期完成 pinned sync、run 和 result。"""
    (
        target_repo, project_head, upstream_dir,
        upstream_sha, ownership, workflow_paths,
    ) = common_context(args=args)
    existing_run = target_repo / RUN_PATH
    if existing_run.is_file():
        state = load_run_state(repo_root=target_repo)
        if state["completed_modes"] != list(MODES):
            raise HarnessError(
                error="已有未完成 workflow run",
                detail="先完成当前 run，或显式删除 ignored runtime 后重启",
            )

    # PREPARE 之前不接受混入的业务或核心文档改动。
    before_dirty = assert_dirty_allowed(
        repo_root=target_repo,
        allowed_paths={"PR_BODY.md"},
        error="PREPARE 前工作区含无关改动",
    )
    before_snapshot = snapshot_workflow(
        repo_root=target_repo,
        workflow_paths=workflow_paths,
    )
    sync = run_pinned_sync(
        target_repo=target_repo,
        upstream_dir=upstream_dir,
        final=False,
    )

    # pinned sync 只能产生 workflow 管理路径。
    after_dirty = assert_dirty_allowed(
        repo_root=target_repo,
        allowed_paths=workflow_paths,
        error="PREPARE sync 产生越权改动",
    )
    after_snapshot = snapshot_workflow(
        repo_root=target_repo,
        workflow_paths=workflow_paths,
    )
    now = utc_now()
    state = {
        "schema_version": 1,
        "run_id": uuid4().hex,
        "upstream_dir": str(upstream_dir),
        "upstream_sha": upstream_sha,
        "project_head": project_head,
        "completed_modes": ["PREPARE"],
        "active_mode": None,
        "boundary_snapshot": after_snapshot,
        "boundary_dirty_paths": after_dirty,
        "submit_ready": False,
        "started_at_utc": now,
        "updated_at_utc": now,
    }
    write_baseline(
        repo_root=target_repo,
        run_id=state["run_id"],
        mode="PREPARE",
        upstream_sha=upstream_sha,
        start_head=project_head,
        snapshot=before_snapshot,
        dirty_paths=before_dirty,
        allowed_commit_paths=[],
    )
    write_run_state(repo_root=target_repo, state=state)
    changed = changed_snapshot_paths(
        baseline=before_snapshot,
        current=after_snapshot,
    )
    result = write_result(
        repo_root=target_repo,
        run_id=state["run_id"],
        mode="PREPARE",
        upstream_sha=upstream_sha,
        project_head=project_head,
        changed_paths=changed,
        details={
            "sync_command": sync["command"],
            "dirty_paths": after_dirty,
        },
    )
    return {
        "status": "passed",
        "mode": "PREPARE",
        "run_id": state["run_id"],
        "result": str(target_repo / RESULTS_DIR / "PREPARE.json"),
        "changed_paths": result["changed_paths"],
    }


def start_pass(*, args: Any) -> dict[str, Any]:
    """参数为 PASS CLI；预期保存 baseline 并返回 ownership/prompt 位置。"""
    (
        target_repo, project_head, upstream_dir,
        upstream_sha, ownership, workflow_paths, state,
    ) = bound_context(args=args)
    if state["active_mode"] is not None:
        raise HarnessError(
            error="已有 active mode",
            detail=str(state["active_mode"]),
        )
    if state["completed_modes"] == list(MODES):
        raise HarnessError(
            error="workflow 已完成",
            detail="不能再次启动 PASS",
        )
    expected_mode = MODES[len(state["completed_modes"])]
    if args.mode != expected_mode or args.mode not in PASS_MODES:
        raise HarnessError(
            error="mode 顺序无效",
            detail=f"期望 {expected_mode}，实际 {args.mode}",
        )
    if project_head != state["project_head"]:
        raise HarnessError(
            error="PASS 前项目 HEAD 变化",
            detail=f"状态 {state['project_head']}，当前 {project_head}",
        )

    # boundary 快照在建本 mode baseline 前发现跨会话顺手越权。
    require_boundary_unchanged(
        repo_root=target_repo,
        state=state,
        workflow_paths=workflow_paths,
    )
    dirty_paths = assert_dirty_allowed(
        repo_root=target_repo,
        allowed_paths=workflow_paths,
        error="PASS 前工作区含越权路径",
    )
    snapshot = snapshot_workflow(
        repo_root=target_repo,
        workflow_paths=workflow_paths,
    )
    write_baseline(
        repo_root=target_repo,
        run_id=state["run_id"],
        mode=args.mode,
        upstream_sha=upstream_sha,
        start_head=project_head,
        snapshot=snapshot,
        dirty_paths=dirty_paths,
        allowed_commit_paths=[],
    )
    state["active_mode"] = args.mode
    state["submit_ready"] = False
    write_run_state(repo_root=target_repo, state=state)
    operations_path = upstream_dir / "zh/scripts/OPERATIONS.md"
    title = ownership[args.mode]["title"]
    heading = f"### {title}"
    matches = [
        index for index, line in enumerate(
            operations_path.read_text(encoding="utf-8").splitlines(), start=1
        ) if line == heading
    ]
    if len(matches) != 1:
        raise HarnessError(
            error="PASS prompt 标题无效",
            detail=f"{heading} 匹配次数：{len(matches)}",
        )
    return {
        "status": "passed",
        "mode": args.mode,
        "title": title,
        "owned_paths": ownership[args.mode]["owned"],
        "pr_body_sections": ownership[args.mode]["pr_body_sections"],
        "operations_path": str(operations_path),
        "operations_heading_line": matches[0],
        "instruction": (
            "只执行该 PASS code block 的 Skill 模式语义部分；"
            "不要执行人工模式 curl。"
        ),
    }


def finish_pass(*, args: Any) -> dict[str, Any]:
    """参数为 PASS CLI；预期检查 ownership、sync 并写结果。"""
    (
        target_repo, project_head, upstream_dir,
        upstream_sha, ownership, workflow_paths, state,
    ) = bound_context(args=args)
    if args.mode not in PASS_MODES or state["active_mode"] != args.mode:
        raise HarnessError(
            error="active PASS 不匹配",
            detail=f"状态 {state['active_mode']!r}，实际 {args.mode}",
        )
    baseline = load_baseline(repo_root=target_repo, mode=args.mode)
    if (
        baseline["run_id"] != state["run_id"]
        or baseline["start_head"] != project_head
    ):
        raise HarnessError(
            error="PASS baseline 不匹配",
            detail="run_id 或项目 HEAD 已变化",
        )
    assert_dirty_allowed(
        repo_root=target_repo,
        allowed_paths=workflow_paths,
        error="PASS 产生越权路径",
    )
    before_sync_snapshot = snapshot_workflow(
        repo_root=target_repo,
        workflow_paths=workflow_paths,
    )
    changed = changed_snapshot_paths(
        baseline=baseline["snapshot"],
        current=before_sync_snapshot,
    )
    allowed = set(ownership[args.mode]["owned"]) | {"PR_BODY.md"}
    unauthorized = [path for path in changed if path not in allowed]
    if unauthorized:
        raise HarnessError(
            error="PASS ownership 越权",
            detail=", ".join(unauthorized),
            extra={"unauthorized_paths": unauthorized},
        )
    if "PR_BODY.md" in changed:
        assert_pr_body_scope(
            baseline_text=(
                baseline["pr_body_text"]
                or (
                    target_repo / ".coding_workflow/diffs/pr_body_skeleton.md"
                ).read_text(encoding="utf-8")
            ),
            current_text=read_pr_body(repo_root=target_repo),
            allowed_sections=set(
                ownership[args.mode]["pr_body_sections"]
            ),
        )

    # ownership 通过后才运行 pinned sync，防止 sync 掩盖 Agent 越权。
    sync = run_pinned_sync(
        target_repo=target_repo,
        upstream_dir=upstream_dir,
        final=False,
    )
    after_dirty = assert_dirty_allowed(
        repo_root=target_repo,
        allowed_paths=workflow_paths,
        error="PASS sync 产生越权改动",
    )
    after_snapshot = snapshot_workflow(
        repo_root=target_repo,
        workflow_paths=workflow_paths,
    )
    state["completed_modes"].append(args.mode)
    state["active_mode"] = None
    state["boundary_snapshot"] = after_snapshot
    state["boundary_dirty_paths"] = after_dirty
    write_run_state(repo_root=target_repo, state=state)
    result = write_result(
        repo_root=target_repo,
        run_id=state["run_id"],
        mode=args.mode,
        upstream_sha=upstream_sha,
        project_head=project_head,
        changed_paths=changed,
        details={
            "owned_paths": ownership[args.mode]["owned"],
            "pr_body_sections": ownership[args.mode]["pr_body_sections"],
            "sync_command": sync["command"],
            "dirty_paths_after_sync": after_dirty,
        },
    )
    return {
        "status": "passed",
        "mode": args.mode,
        "result": str(target_repo / RESULTS_DIR / f"{args.mode}.json"),
        "changed_paths": result["changed_paths"],
    }


def prepare_submit(*, args: Any) -> dict[str, Any]:
    """参数为 SUBMIT CLI；预期建立 active、unsealed 提交基线。"""
    (
        target_repo, project_head, upstream_dir,
        upstream_sha, ownership, workflow_paths, state,
    ) = bound_context(args=args)
    if state["completed_modes"] != list(MODES[:-1]):
        raise HarnessError(
            error="SUBMIT 前 mode 未完成",
            detail=str(state["completed_modes"]),
        )
    if state["active_mode"] is not None:
        raise HarnessError(
            error="SUBMIT 前仍有 active mode",
            detail=str(state["active_mode"]),
        )
    if project_head != state["project_head"]:
        raise HarnessError(
            error="SUBMIT 前项目 HEAD 变化",
            detail=f"状态 {state['project_head']}，当前 {project_head}",
        )
    require_boundary_unchanged(
        repo_root=target_repo,
        state=state,
        workflow_paths=workflow_paths,
    )
    dirty_paths = assert_dirty_allowed(
        repo_root=target_repo,
        allowed_paths=workflow_paths,
        error="SUBMIT 前工作区含越权路径",
    )
    legal_commit_paths = all_owned_paths(ownership=ownership) | {
        ".gitignore"
    }
    allowed_commit_paths = [
        path for path in dirty_paths if path in legal_commit_paths
    ]
    write_baseline(
        repo_root=target_repo,
        run_id=state["run_id"],
        mode="SUBMIT",
        upstream_sha=upstream_sha,
        start_head=project_head,
        snapshot=snapshot_workflow(
            repo_root=target_repo,
            workflow_paths=workflow_paths,
        ),
        dirty_paths=dirty_paths,
        allowed_commit_paths=allowed_commit_paths,
    )
    state["active_mode"] = "SUBMIT"
    state["submit_ready"] = False
    write_run_state(repo_root=target_repo, state=state)
    return {
        "status": "passed",
        "mode": "SUBMIT",
        "submit_start_head": project_head,
        "allowed_commit_paths": allowed_commit_paths,
        "next_command": "seal-submit",
    }


def seal_submit(*, args: Any) -> dict[str, Any]:
    """参数为 SUBMIT CLI；预期运行 final gate 并封存待提交内容。"""
    (
        target_repo, project_head, upstream_dir,
        upstream_sha, ownership, workflow_paths, state,
    ) = bound_context(args=args)
    if state["active_mode"] != "SUBMIT" or state["submit_ready"]:
        raise HarnessError(
            error="SUBMIT 无法 seal",
            detail="必须处于 prepare-submit 后的 active、unsealed 状态",
        )
    baseline = load_baseline(repo_root=target_repo, mode="SUBMIT")
    if (
        baseline["run_id"] != state["run_id"]
        or baseline["start_head"] != project_head
    ):
        raise HarnessError(
            error="SUBMIT seal baseline 不匹配",
            detail="run_id 或项目 HEAD 已变化",
        )
    before_snapshot = snapshot_workflow(
        repo_root=target_repo,
        workflow_paths=workflow_paths,
    )
    changed = changed_snapshot_paths(
        baseline=baseline["snapshot"],
        current=before_snapshot,
    )
    if any(path != "PR_BODY.md" for path in changed):
        raise HarnessError(
            error="SUBMIT seal 前 workflow 内容变化",
            detail=", ".join(changed),
            extra={"changed_paths": changed},
        )
    local_body = read_pr_body(repo_root=target_repo)
    assert_pr_body_scope(
        baseline_text=baseline["pr_body_text"],
        current_text=local_body,
        allowed_sections={"pr_test_evidence"},
    )
    assert_dirty_allowed(
        repo_root=target_repo,
        allowed_paths=workflow_paths,
        error="SUBMIT seal 前工作区含越权路径",
    )

    # 失败只吸收本次真实 sync 生成的 PR auto 区域，保留可重试状态。
    try:
        final_gate = run_pinned_sync(
            target_repo=target_repo,
            upstream_dir=upstream_dir,
            final=True,
        )
    except HarnessError:
        failed_snapshot = snapshot_workflow(
            repo_root=target_repo,
            workflow_paths=workflow_paths,
        )
        gate_changes = changed_snapshot_paths(
            baseline=before_snapshot,
            current=failed_snapshot,
        )
        if gate_changes and set(gate_changes) == {"PR_BODY.md"}:
            baseline["snapshot"] = failed_snapshot
            baseline["dirty_paths"] = ordinary_dirty_paths(
                repo_root=target_repo,
            )
            baseline["pr_body_text"] = read_pr_body(repo_root=target_repo)
            write_json(
                path=target_repo / BASELINES_DIR / "SUBMIT.json",
                payload=validate_baseline(baseline=baseline, mode="SUBMIT"),
            )
        raise

    # final reconcile 不得替 PASS agent 静默改写其 owned 文档。
    sealed_snapshot = snapshot_workflow(
        repo_root=target_repo,
        workflow_paths=workflow_paths,
    )
    gate_changes = changed_snapshot_paths(
        baseline=before_snapshot,
        current=sealed_snapshot,
    )
    if any(path != "PR_BODY.md" for path in gate_changes):
        raise HarnessError(
            error="final reconcile 改写 PASS-owned 内容",
            detail="必须显式重启整轮 workflow：" + ", ".join(gate_changes),
            extra={"changed_paths": gate_changes},
        )
    sealed_dirty = assert_dirty_allowed(
        repo_root=target_repo,
        allowed_paths=workflow_paths,
        error="SUBMIT seal 后工作区含越权路径",
    )
    legal_commit_paths = all_owned_paths(ownership=ownership) | {".gitignore"}
    baseline["snapshot"] = sealed_snapshot
    baseline["dirty_paths"] = sealed_dirty
    baseline["allowed_commit_paths"] = [
        path for path in sealed_dirty if path in legal_commit_paths
    ]
    baseline["pr_body_text"] = read_pr_body(repo_root=target_repo)
    write_json(
        path=target_repo / BASELINES_DIR / "SUBMIT.json",
        payload=validate_baseline(baseline=baseline, mode="SUBMIT"),
    )
    state["submit_ready"] = True
    write_run_state(repo_root=target_repo, state=state)
    return {
        "status": "passed",
        "mode": "SUBMIT",
        "allowed_commit_paths": baseline["allowed_commit_paths"],
        "final_gate_command": final_gate["command"],
    }


def finish_submit(*, args: Any) -> dict[str, Any]:
    """参数为 PR 事实；预期把 sealed 内容绑定 commit 与远端 PR。"""
    (
        target_repo, project_head, upstream_dir,
        upstream_sha, _ownership, workflow_paths, state,
    ) = bound_context(args=args)
    if state["active_mode"] != "SUBMIT" or not state["submit_ready"]:
        raise HarnessError(
            error="SUBMIT 尚未 seal",
            detail="必须先成功执行 seal-submit",
        )
    baseline = load_baseline(repo_root=target_repo, mode="SUBMIT")
    if baseline["run_id"] != state["run_id"]:
        raise HarnessError(
            error="SUBMIT baseline 不匹配",
            detail="run_id 已变化",
        )
    commit_count = git_commit_count_between(
        repo_root=target_repo,
        start_sha=baseline["start_head"],
        end_sha=project_head,
    )
    if commit_count != 1:
        raise HarnessError(
            error="SUBMIT commit 数不匹配",
            detail=f"期望 1，实际 {commit_count}",
        )
    committed_paths = git_paths_between(
        repo_root=target_repo,
        start_sha=baseline["start_head"],
        end_sha=project_head,
    )
    expected_paths = sorted(set(baseline["allowed_commit_paths"]))
    if committed_paths != expected_paths:
        raise HarnessError(
            error="SUBMIT committed scope 不匹配",
            detail=f"期望 {expected_paths}，实际 {committed_paths}",
            extra={
                "expected_committed_paths": expected_paths,
                "actual_committed_paths": committed_paths,
            },
        )
    current_snapshot = snapshot_workflow(
        repo_root=target_repo,
        workflow_paths=workflow_paths,
    )
    changed = changed_snapshot_paths(
        baseline=baseline["snapshot"],
        current=current_snapshot,
    )
    if changed:
        raise HarnessError(
            error="sealed workflow 内容已变化",
            detail=", ".join(changed),
            extra={"changed_paths": changed},
        )
    remaining_dirty = ordinary_dirty_paths(repo_root=target_repo)
    unexpected_dirty = [
        path for path in remaining_dirty if path != "PR_BODY.md"
    ]
    if unexpected_dirty:
        raise HarnessError(
            error="SUBMIT 后工作区不干净",
            detail=", ".join(unexpected_dirty),
            extra={"remaining_dirty_paths": remaining_dirty},
        )
    branch_result = run_git(
        repo_root=target_repo,
        args=["branch", "--show-current"],
    )
    branch = branch_result.stdout.strip()
    if (
        branch_result.returncode != 0
        or branch != args.head
        or branch in {"main", "master", args.base}
    ):
        raise HarnessError(
            error="SUBMIT head branch 不匹配",
            detail=f"期望 {args.head}，实际 {branch}",
        )
    pull_request = query_pull_request(
        repo_root=target_repo,
        pr_number=args.pr_number,
    )
    local_body = read_pr_body(repo_root=target_repo)
    if local_body is None:
        raise HarnessError(
            error="缺少本地 PR_BODY.md",
            detail="无法绑定远端 PR body",
        )
    if local_body != baseline["pr_body_text"]:
        raise HarnessError(
            error="本地 PR_BODY 与 sealed body 不匹配",
            detail="seal 后不得修改本地 PR body",
        )
    remote_body = pull_request["body"]
    sealed_body = baseline["pr_body_text"]
    body_matches = isinstance(remote_body, str) and (
        remote_body.replace("\r\n", "\n").replace("\r", "\n").rstrip("\n")
        == sealed_body.replace("\r\n", "\n").replace("\r", "\n").rstrip("\n")
    )
    if (
        pull_request["number"] != args.pr_number
        or pull_request["state"] != "OPEN"
        or pull_request["headRefOid"] != project_head
        or pull_request["headRefName"] != args.head
        or pull_request["baseRefName"] != args.base
        or not body_matches
    ):
        raise HarnessError(
            error="远端 PR 与本地提交不匹配",
            detail=(
                f"PR={pull_request['number']} state={pull_request['state']} "
                f"head={pull_request['headRefName']}@"
                f"{pull_request['headRefOid']} base="
                f"{pull_request['baseRefName']} body_match="
                f"{body_matches}"
            ),
        )

    # GitHub 已确认远端 head/body 后才把 SUBMIT 标记为完成。
    state["completed_modes"].append("SUBMIT")
    state["active_mode"] = None
    state["submit_ready"] = False
    state["project_head"] = project_head
    state["boundary_snapshot"] = current_snapshot
    state["boundary_dirty_paths"] = remaining_dirty
    write_run_state(repo_root=target_repo, state=state)
    result = write_result(
        repo_root=target_repo,
        run_id=state["run_id"],
        mode="SUBMIT",
        upstream_sha=upstream_sha,
        project_head=project_head,
        changed_paths=committed_paths,
        details={
            "pr_number": args.pr_number,
            "pr_url": pull_request["url"],
            "base": args.base,
            "head": args.head,
            "remote_body_matches": True,
            "remaining_dirty_paths": remaining_dirty,
        },
    )
    return {
        "status": "passed",
        "mode": "SUBMIT",
        "result": str(target_repo / RESULTS_DIR / "SUBMIT.json"),
        "pr_url": pull_request["url"],
        "project_head": result["project_head"],
        "committed_paths": committed_paths,
    }


def status(*, args: Any) -> dict[str, Any]:
    """参数为目标仓库；预期返回 run、mode 和结果路径状态。"""
    target_repo, project_head = require_repository(
        path=Path(args.target_repo),
        label="目标仓库",
    )
    path = target_repo / RUN_PATH
    if not path.is_file():
        return {
            "status": "not_started",
            "target_repo": str(target_repo),
            "project_head": project_head,
        }
    state = load_run_state(repo_root=target_repo)
    result_files = {
        mode: str(target_repo / RESULTS_DIR / f"{mode}.json")
        for mode in state["completed_modes"]
    }
    return {
        "status": "started",
        "run_id": state["run_id"],
        "completed_modes": state["completed_modes"],
        "active_mode": state["active_mode"],
        "submit_ready": state["submit_ready"],
        "state_project_head": state["project_head"],
        "current_project_head": project_head,
        "results": result_files,
    }


def add_common_arguments(*, parser: argparse.ArgumentParser) -> None:
    """参数为 subparser；预期加入三个 required target/upstream 参数。"""
    parser.add_argument("--target-repo", required=True)
    parser.add_argument("--upstream-dir", required=True)
    parser.add_argument("--upstream-sha", required=True)


def parse_args() -> Any:
    """无参数；预期返回含 subcommand 和全部显式值的 Namespace。"""
    parser = JsonArgumentParser(
        description="Workflow Docs Sync 轻量 mode harness。",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    prepare_parser = subparsers.add_parser("prepare")
    add_common_arguments(parser=prepare_parser)
    for command in ("start-pass", "finish-pass"):
        pass_parser = subparsers.add_parser(command)
        add_common_arguments(parser=pass_parser)
        pass_parser.add_argument(
            "--mode",
            required=True,
            choices=PASS_MODES,
        )
    for command in ("prepare-submit", "seal-submit"):
        submit_parser = subparsers.add_parser(command)
        add_common_arguments(parser=submit_parser)
    finish_submit_parser = subparsers.add_parser("finish-submit")
    add_common_arguments(parser=finish_submit_parser)
    finish_submit_parser.add_argument(
        "--pr-number",
        required=True,
        type=int,
    )
    finish_submit_parser.add_argument("--base", required=True)
    finish_submit_parser.add_argument("--head", required=True)
    status_parser = subparsers.add_parser("status")
    status_parser.add_argument("--target-repo", required=True)
    return parser.parse_args()


def dispatch(*, args: Any) -> dict[str, Any]:
    """参数为解析结果；预期返回对应 subcommand 的结构化结果。"""
    operations = {
        "prepare": prepare,
        "start-pass": start_pass,
        "finish-pass": finish_pass,
        "prepare-submit": prepare_submit,
        "seal-submit": seal_submit,
        "finish-submit": finish_submit,
        "status": status,
    }
    return operations[args.command](args=args)


def run_cli() -> int:
    """无参数；预期成功返回 0，已知本地错误返回 1，并只输出一行 JSON。"""
    try:
        payload = dispatch(args=parse_args())
    except HarnessError as exc:
        error_payload = {"error": exc.error, "detail": exc.detail}
        for key, value in exc.extra.items():
            error_payload[key] = value
        emit_json(payload=error_payload)
        return 1
    except (KeyError, OSError, TypeError, UnicodeError, ValueError) as exc:
        emit_json(
            payload={
                "error": "harness 执行失败",
                "detail": f"{type(exc).__name__}: {exc}",
            }
        )
        return 1
    emit_json(payload=payload)
    return 0


if __name__ == "__main__":
    sys.exit(run_cli())
