#!/usr/bin/env python3
"""
Workflow Docs Full Reconcile.

Purpose:
    Generate one-run evidence for reconciling a target repository's workflow
    documents against the latest `wlvh/coding-workflow` upstream templates.

Call flow:
    main()
      -> assert_git_repo()
      -> assert_upstream_repo()
      -> assert_no_unmanaged_dirty()
      -> assert_no_legacy_source()
      -> ensure_gitignore()
      -> stage_full_reconcile_outputs()
      -> render_pr_body_skeleton()
      -> print_summary()

This script intentionally has no committed baseline manifest. Each run is a
full review of current project facts plus the latest upstream rules. Scratch
evidence is written under `.coding_workflow/diffs/` and is not committed.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from difflib import unified_diff
from pathlib import Path

CORE_FILES = (
    "AGENTS.md",
    "architecture.md",
    "capability_contract.json",
    "interact.md",
    "docs/business_user_guide.md",
    "TESTING.md",
    "PR_Checklist.md",
    "SOP.md",
    ".github/pull_request_template.md",
)

SYNC_PROMPT_FILES = (
    "scripts/sync_pr_review_system.md",
)

PERMITTED_INHERIT_FILES = frozenset({
    ".github/pull_request_template.md",
})

TEMPLATE_MARKERS = (
    "<项目名>",
    "<项目 / agent / app 名称>",
    "<对象>",
    "<指标 / 结果>",
    "Case 1：确认一个对象最近是否异常",
    "待项目负责人补充",
    "sample_supported_question",
    "sample_multi_object_comparison_not_supported",
    "sample_no_final_business_decision",
    "sample_requires_context_before_answer",
    "CAPABILITY.sample_",
    "BOUNDARY.sample_",
    "RESPONSIBILITY.sample_",
    "BEHAVIOR.sample_",
)

TODO_ANCHOR_COMMENTS = (
    "<!-- capability-anchor: TODO -->",
    "<!-- test-anchor: TODO -->",
)

SYNC_MANAGED_DIRTY_PATHS = frozenset(CORE_FILES) | frozenset({
    ".gitignore",
    "PR_BODY.md",
})

GITIGNORE_LINES = (
    "PR_BODY.md",
    ".coding_workflow/diffs/",
)

DIFFS_DIR = ".coding_workflow/diffs"
STATE_FILE = "sync_state.json"
WORKORDER_FILE = "agent_workorder.md"
PR_BODY_SKELETON_FILE = "pr_body_skeleton.md"
PR_BODY_PREVIOUS_FILE = "pr_body_previous.md"
UPSTREAM_FULL_DIR = "upstream_full"

SYNC_AUTO_START = "<!-- sync:auto:start -->"
SYNC_AUTO_END = "<!-- sync:auto:end -->"
SYNC_PR_BODY_MARKER = "<!-- sync:pr-body version=1 -->"
AGENT_SECTIONS = (
    "repo_facts_map",
    "full_document_reconcile",
    "remaining_human_decisions",
)
PR_BODY_REQUIRED_SECTIONS = (
    "Repo Facts Map",
    "Sync Summary",
    "Working Tree State at Sync Time",
    "Sync Review Contract",
    "Upstream Templates at Sync Time",
    "Upstream Instructions at Sync Time",
    "Installation Status",
    "Full Document Reconcile",
    "Remaining Human Decisions",
)
REPO_FACTS_HEADINGS = (
    "### 1. 项目类型",
    "### 2. 系统输入",
    "### 3. 系统输出",
    "### 4. 用户身份",
    "### 5. 核心模块清单",
    "### 6. 主要数据流",
    "### 7. 关键不变量",
    "### 8. 当前能力清单",
    "### 9. 测试现状",
    "### 10. 不确定项",
)
BLOCKING_FINAL_STATUSES = frozenset({
    "installed_template",
    "template_copy_requires_specialization",
    "partially_specialized",
})
UNFILLED_AGENT_PLACEHOLDERS = (
    "待补充",
    "待判断",
)

LEGACY_SOURCE_PATH = ".coding_workflow/source.json"
LEGACY_SOURCE_MIGRATION_NOTE = (
    ".coding_workflow/source.json belonged to the removed incremental baseline "
    "flow. Full reconcile does not use it; delete or archive it after "
    "confirming it is no longer needed."
)


def git(*args: str, cwd: Path) -> str:
    """Run git and return stdout.

    Parameters:
        *args: Git subcommand and flags, already split by argument.
        cwd: Repository or upstream clone path.

    Expected output:
        Captured stdout as a string. Non-zero git exits raise immediately.
    """
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        encoding="utf-8",
        text=True,
    ).stdout


def git_optional(*args: str, cwd: Path) -> str | None:
    """Run git and return stdout when the command succeeds.

    Parameters:
        *args: Git subcommand and flags, already split by argument.
        cwd: Repository or upstream clone path.

    Expected output:
        Captured stdout, or None when git exits non-zero. This is used only for
        existence checks where failing fast would hide a clearer message.
    """
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=False,
        capture_output=True,
        encoding="utf-8",
        text=True,
    )
    return result.stdout if result.returncode == 0 else None


def file_at_ref(upstream_dir: Path, ref: str, path: str) -> str | None:
    """Return one upstream template file at a git ref.

    Parameters:
        upstream_dir: Local clone of `wlvh/coding-workflow`.
        ref: Commit SHA or ref name.
        path: Repository-relative file path.

    Expected output:
        UTF-8 text at `ref:path`, or None if upstream lacks the file.
    """
    return git_optional("show", f"{ref}:{path}", cwd=upstream_dir)


def upstream_raw_url(upstream_sha: str, rel_path: str) -> str:
    """Return a commit-pinned raw GitHub URL for one upstream file.

    Parameters:
        upstream_sha: Resolved upstream commit SHA.
        rel_path: Repository-relative upstream file path.

    Expected output:
        Raw GitHub URL pinned to `upstream_sha`, safe to read after the
        temporary upstream clone has been removed.
    """
    return (
        "https://raw.githubusercontent.com/wlvh/coding-workflow/"
        f"{upstream_sha}/{rel_path}"
    )


def agent_section_start(section_name: str) -> str:
    """Return the start sentinel for an agent-preserved PR body section.

    Parameters:
        section_name: Stable section key from `AGENT_SECTIONS`.

    Expected output:
        HTML comment sentinel that survives normal Markdown rendering.
    """
    return f"<!-- sync:agent:start {section_name} -->"


def agent_section_end(section_name: str) -> str:
    """Return the end sentinel for an agent-preserved PR body section.

    Parameters:
        section_name: Stable section key from `AGENT_SECTIONS`.

    Expected output:
        HTML comment sentinel that lets the script preserve semantic work while
        refreshing deterministic sync evidence.
    """
    return f"<!-- sync:agent:end {section_name} -->"


def required_sync_sentinels() -> tuple[str, ...]:
    """Return all PR body sentinels required by the sync contract.

    Parameters:
        None.

    Expected output:
        Tuple of exact sentinel strings rendered into `PR_BODY.md`. Keeping the
        list derived from existing constants prevents the reviewer prompt from
        becoming a second source of truth.
    """
    sentinels = [
        SYNC_PR_BODY_MARKER,
        SYNC_AUTO_START,
        SYNC_AUTO_END,
    ]
    for section_name in AGENT_SECTIONS:
        sentinels.append(agent_section_start(section_name=section_name))
        sentinels.append(agent_section_end(section_name=section_name))
    return tuple(sentinels)


def diffs_root_for(repo_root: Path) -> Path:
    """Return the scratch evidence directory for one sync epoch.

    Parameters:
        repo_root: Target project path.

    Expected output:
        `.coding_workflow/diffs` path under the target repository.
    """
    return repo_root / DIFFS_DIR


def state_path_for(repo_root: Path) -> Path:
    """Return the current sync state path.

    Parameters:
        repo_root: Target project path.

    Expected output:
        Path to `.coding_workflow/diffs/sync_state.json`, which is rebuilt on
        every full reconcile run and never acts as a persistent baseline.
    """
    return diffs_root_for(repo_root=repo_root) / STATE_FILE


def assert_git_repo(repo_root: Path) -> None:
    """Fail fast when REPO_ROOT is not inside a git worktree.

    Parameters:
        repo_root: Target project path.

    Expected output:
        None. The process exits with a clear error when sync cannot inspect git
        state. This accepts normal clones and `git worktree` checkouts.
    """
    inside = git_optional("rev-parse", "--is-inside-work-tree", cwd=repo_root)
    if inside is None or inside.strip() != "true":
        sys.exit(f"FATAL: {repo_root} is not inside a git worktree.")


def assert_upstream_repo(upstream_dir: Path) -> None:
    """Fail fast when UPSTREAM_DIR is missing or not a git worktree.

    Parameters:
        upstream_dir: Local clone of `wlvh/coding-workflow`.

    Expected output:
        None. The process exits with a clear error when a direct script caller
        provides an invalid upstream path.
    """
    if not upstream_dir.is_dir():
        sys.exit(
            f"FATAL: UPSTREAM_DIR does not exist or is not a directory: "
            f"{upstream_dir}"
        )
    inside = git_optional(
        "rev-parse",
        "--is-inside-work-tree",
        cwd=upstream_dir,
    )
    if inside is None or inside.strip() != "true":
        sys.exit(f"FATAL: UPSTREAM_DIR is not a git worktree: {upstream_dir}")


def is_sync_managed_dirty_path(path: str) -> bool:
    """Return whether an uncommitted path may be dirty during full reconcile.

    Parameters:
        path: Repository-relative path parsed from `git status --porcelain`.

    Expected output:
        True for sync scratch diffs, core workflow docs, `.gitignore`, and
        local `PR_BODY.md`; False for project code/config/test changes.
    """
    return (
        path.startswith(".coding_workflow/diffs/")
        or path in SYNC_MANAGED_DIRTY_PATHS
    )


def parse_dirty_status_paths(status_output: str) -> list[str]:
    """Parse NUL-delimited git porcelain rows into repository paths.

    Parameters:
        status_output: Output from `git status --porcelain=v1 -z -uall`.

    Expected output:
        Repository-relative dirty paths, including rename/copy sources and
        destinations. NUL parsing avoids quoted path edge cases in
        sync-managed directories.
    """
    paths: list[str] = []
    fields = status_output.split("\0")
    index = 0
    while index < len(fields):
        row = fields[index]
        index += 1
        if not row:
            continue
        paths.append(row[3:])
        if "R" in row[:2] or "C" in row[:2]:
            if index >= len(fields) or not fields[index]:
                sys.exit("FATAL: malformed git status rename/copy row.")
            paths.append(fields[index])
            index += 1
    return paths


def assert_no_unmanaged_dirty(repo_root: Path) -> None:
    """Refuse to run with uncommitted project code changes.

    Parameters:
        repo_root: Target project path.

    Expected output:
        None. Dirty project files make the full review ambiguous because the
        resulting PR evidence would mix committed facts with local scratch.
    """
    paths = parse_dirty_status_paths(
        status_output=git(
            "status",
            "--porcelain=v1",
            "-z",
            "-uall",
            cwd=repo_root,
        )
    )
    unmanaged: list[str] = []
    for path in paths:
        if not is_sync_managed_dirty_path(path):
            unmanaged.append(path)
    if unmanaged:
        legacy_source_note = ""
        if LEGACY_SOURCE_PATH in unmanaged:
            legacy_source_note = f"\n\nMigration note: {LEGACY_SOURCE_MIGRATION_NOTE}"
        sys.exit(
            "FATAL: uncommitted changes outside sync-managed files.\n"
            "Commit, stash, or discard project code/config/test changes before "
            "running full workflow-docs reconcile.\n\n"
            "Unmanaged dirty:\n  " + "\n  ".join(unmanaged)
            + legacy_source_note
        )


def assert_no_legacy_source(repo_root: Path) -> None:
    """Refuse repositories that still contain the removed baseline manifest.

    Parameters:
        repo_root: Target project path.

    Expected output:
        None. A tracked or otherwise clean `.coding_workflow/source.json` exits
        before sync writes new evidence, because full reconcile has no baseline
        source of truth to maintain.
    """
    if (repo_root / LEGACY_SOURCE_PATH).exists():
        sys.exit(
            f"FATAL: legacy incremental baseline file exists: "
            f"{LEGACY_SOURCE_PATH}\n\n"
            f"Migration note: {LEGACY_SOURCE_MIGRATION_NOTE}"
        )


def collect_dirty_core_files(repo_root: Path) -> list[str]:
    """Return core documents whose working tree content differs from HEAD.

    Parameters:
        repo_root: Target project path.

    Expected output:
        Ordered repository-relative core document paths. This is report metadata
        only: full reconcile intentionally reads working tree content so agents
        can modify docs and rerun sync before committing.
    """
    dirty_paths = set(parse_dirty_status_paths(
        status_output=git(
            "status",
            "--porcelain=v1",
            "-z",
            "-uall",
            "--",
            *CORE_FILES,
            cwd=repo_root,
        )
    ))
    return [path for path in CORE_FILES if path in dirty_paths]


def ensure_gitignore(repo_root: Path) -> None:
    """Ensure sync scratch files are ignored by git.

    Parameters:
        repo_root: Target project path.

    Expected output:
        `.gitignore` contains `PR_BODY.md` and `.coding_workflow/diffs/`.
        The change is deliberately made after the dirty check so a refused run
        does not leave surprise edits behind.
    """
    gitignore_path = repo_root / ".gitignore"
    existing = gitignore_path.read_text(encoding="utf-8") if gitignore_path.exists() else ""
    existing_lines = set(existing.splitlines())
    missing = [line for line in GITIGNORE_LINES if line not in existing_lines]
    if not missing:
        return
    prefix = existing.rstrip("\n")
    addition = "\n".join((
        "# Workflow docs sync scratch and PR draft",
        *missing,
    ))
    content = f"{prefix}\n\n{addition}\n" if prefix else f"{addition}\n"
    gitignore_path.write_text(content, encoding="utf-8")


def normalize_text(text: str) -> str:
    """Normalize line endings without changing semantic document content.

    Parameters:
        text: UTF-8 text read from a local file or upstream git object.

    Expected output:
        Text with CRLF and CR line endings normalized to LF, so template-copy
        detection does not depend on platform checkout settings.
    """
    return text.replace("\r\n", "\n").replace("\r", "\n")


def render_diff(left: str, right: str, left_label: str, right_label: str) -> str:
    """Render a unified diff between two text blobs.

    Parameters:
        left: Baseline text.
        right: Compared text.
        left_label: Diff label for `left`.
        right_label: Diff label for `right`.

    Expected output:
        Unified diff text ending with a newline, or an empty string when equal.
    """
    lines = unified_diff(
        normalize_text(text=left).splitlines(),
        normalize_text(text=right).splitlines(),
        fromfile=left_label,
        tofile=right_label,
        lineterm="",
    )
    diff = "\n".join(lines)
    return f"{diff}\n" if diff else ""


def marker_hits(text: str) -> list[str]:
    """Return line-level template marker hits in one text blob.

    Parameters:
        text: UTF-8 Markdown, JSON, or template text from a core file.

    Expected output:
        Human-readable `line: marker` entries for the agent workorder. These
        hits are mechanical signals only; semantic alignment remains reviewer
        work.
    """
    hits: list[str] = []
    markers = (*TEMPLATE_MARKERS, *TODO_ANCHOR_COMMENTS)
    for line_number, line in enumerate(text.splitlines(), start=1):
        for marker in markers:
            if marker in line:
                hits.append(f"line {line_number}: {marker}")
    return hits


def mechanical_action_for_status(status: str) -> str:
    """Translate a script status into a bounded agent action.

    Parameters:
        status: One status returned by `classify_core_file`.

    Expected output:
        A workorder sentence. `specialized` is deliberately weak: it only means
        the script found no mechanical required edit, not that the file is
        semantically aligned.
    """
    if status == "installed_template":
        return "必须基于 Repo Facts Map 项目化；不能把 upstream 模板原样提交。"
    if status == "template_copy_requires_specialization":
        return "必须解释为什么可继承，或基于当前项目事实项目化。"
    if status == "partially_specialized":
        return "必须清理模板残留或 TODO anchor，再重跑 sync。"
    if status == "inherited_upstream_allowed":
        return "脚本允许继承 upstream；仍需在 PR body 写清证据。"
    if status == "specialized":
        return (
            "脚本未发现机械必改项；如 Repo Facts Map 或 upstream 新规则要求，"
            "仍可修改。"
        )
    sys.exit(f"FATAL: unknown sync status: {status}")


def classify_core_file(
    rel_path: str,
    exists: bool,
    local_text: str,
    upstream_text: str,
) -> tuple[str, str]:
    """Classify one core document for full reconcile review.

    Parameters:
        rel_path: Repository-relative core file path.
        exists: Whether the target project had the file before this run.
        local_text: Current target file text, or empty string when missing.
        upstream_text: Latest upstream template text.

    Expected output:
        `(status, note)` for the Installation Status table.
    """
    normalized_local_text = normalize_text(text=local_text)
    normalized_upstream_text = normalize_text(text=upstream_text)
    if not exists:
        if rel_path in PERMITTED_INHERIT_FILES:
            return (
                "inherited_upstream_allowed",
                "File was missing; sync installed upstream template. "
                "This file is permitted to inherit upstream content.",
            )
        return (
            "installed_template",
            "File was missing; sync installed upstream template. "
            "Agent must project-specialize before commit.",
        )
    if normalized_local_text == normalized_upstream_text:
        if rel_path in PERMITTED_INHERIT_FILES:
            return (
                "inherited_upstream_allowed",
                "File matches upstream verbatim; this file may inherit upstream.",
            )
        return (
            "template_copy_requires_specialization",
            "File matches upstream verbatim; project-specific review is required.",
        )
    if any(marker in normalized_local_text for marker in TEMPLATE_MARKERS):
        return (
            "partially_specialized",
            "File contains template placeholders; agent must finish specialization.",
        )
    if any(comment in normalized_local_text for comment in TODO_ANCHOR_COMMENTS):
        return (
            "partially_specialized",
            "File contains TODO anchor comments; agent must finish specialization.",
        )
    return (
        "specialized",
        "File appears project-specific; reviewer must still cross-check latest upstream rules.",
    )


def write_installation_status(
    diffs_root: Path,
    core_records: list[dict[str, object]],
) -> None:
    """Write per-core-file status evidence.

    Parameters:
        diffs_root: `.coding_workflow/diffs` path.
        core_records: Per-core-file state rows for this sync epoch.

    Expected output:
        `installation_status.md` summarizing every core document.
    """
    lines = [
        "# Installation Status",
        "",
        "Full reconcile checks every core document against latest upstream.",
        "",
        "| File | Action | Note |",
        "|---|---|---|",
    ]
    for record in core_records:
        path = str(record["path"])
        action = str(record["status"])
        note = str(record["note"])
        lines.append(f"| `{path}` | `{action}` | {note} |")
    (diffs_root / "installation_status.md").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def write_full_reconcile_report(
    diffs_root: Path,
    upstream_sha: str,
    project_sha: str,
    dirty_core_files: list[str],
    core_records: list[dict[str, object]],
) -> None:
    """Write the run-level full reconcile report.

    Parameters:
        diffs_root: `.coding_workflow/diffs` path.
        upstream_sha: Latest upstream commit used by this run.
        project_sha: Target project base commit at sync time.
        dirty_core_files: Core documents whose working tree content differs
            from HEAD at sync time.
        core_records: Per-core-file state rows for this sync epoch.

    Expected output:
        `full_reconcile_report.md` with PR-body fields and review signals.
    """
    signals = [
        f"- `{path}`: `{status}`"
        for path, status in (
            (str(record["path"]), str(record["status"]))
            for record in core_records
        )
        if status != "specialized"
    ]
    lines = [
        "# Full Reconcile Report",
        "",
        "## Sync Summary",
        "",
        "- sync mode: full_reconcile",
        f"- upstream_resolved_commit: {upstream_sha}",
        f"- project_head_commit: {project_sha}",
        "- evidence_source: working_tree",
        f"- core files checked: {len(CORE_FILES)}",
        "",
        "## Working Tree State at Sync Time",
        "",
        (
            f"- project_head_commit: {project_sha} "
            "(base commit; evidence content is read from the working tree)"
        ),
        "- evidence_source: working_tree",
        "- dirty core files (working tree differs from HEAD):",
        *(
            [f"  - `{path}`" for path in dirty_core_files]
            if dirty_core_files
            else ["  - none"]
        ),
        "",
        "## Review-required signals",
        "",
        *(signals if signals else ["- none"]),
        "",
        "## Upstream Templates at Sync Time",
        "",
    ]
    lines.extend(
        f"- `{rel}`: {upstream_raw_url(upstream_sha=upstream_sha, rel_path=rel)}"
        for rel in CORE_FILES
    )
    lines.extend((
        "",
        "## Required PR Body Sections",
        "",
    ))
    lines.extend(f"- {section}" for section in PR_BODY_REQUIRED_SECTIONS)
    (diffs_root / "full_reconcile_report.md").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def build_sync_state(
    upstream_sha: str,
    project_sha: str,
    dirty_core_files: list[str],
    core_records: list[dict[str, object]],
    sync_prompt_records: list[dict[str, object]],
) -> dict[str, object]:
    """Build the per-run state consumed by PR-body helpers.

    Parameters:
        upstream_sha: Latest upstream commit used by this run.
        project_sha: Target project base commit at sync time.
        dirty_core_files: Core documents whose working tree differs from HEAD.
        core_records: Per-core-file state rows for this sync epoch.
        sync_prompt_records: Prompt file rows verified at the same upstream ref.

    Expected output:
        JSON-serializable state. It is valid only inside the current
        `.coding_workflow/diffs/` evidence epoch.
    """
    return {
        "schema_version": "0.2.0",
        "sync_mode": "full_reconcile",
        "upstream_resolved_commit": upstream_sha,
        "project_head_commit": project_sha,
        "evidence_source": "working_tree",
        "core_files_checked": len(CORE_FILES),
        "dirty_core_files": dirty_core_files,
        "sync_prompt_files": sync_prompt_records,
        "core_files": core_records,
    }


def write_sync_state(repo_root: Path, state: dict[str, object]) -> None:
    """Write current sync state under the scratch evidence directory.

    Parameters:
        repo_root: Target project path.
        state: JSON-serializable state from `build_sync_state`.

    Expected output:
        `.coding_workflow/diffs/sync_state.json` is replaced for this run.
    """
    state_path_for(repo_root=repo_root).write_text(
        json.dumps(
            state,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ) + "\n",
        encoding="utf-8",
    )


def render_contract_list(title: str, values: tuple[str, ...] | list[str]) -> list[str]:
    """Render one titled list inside the script-owned review contract.

    Parameters:
        title: Markdown subsection title.
        values: Contract literals derived from sync constants or current state.

    Expected output:
        Markdown lines. Empty lists are rendered as `none` so reviewers do not
        infer missing data from a blank subsection.
    """
    lines = ["", f"### {title}", ""]
    if values:
        lines.extend(
            f"- `{contract_display_literal(value=str(value))}`"
            for value in values
        )
    if not values:
        lines.append("- none")
    return lines


def contract_display_literal(value: str) -> str:
    """Return a contract display literal that cannot act as Markdown syntax.

    Parameters:
        value: Script-owned literal to show to reviewers.

    Expected output:
        Markdown-safe text. Angle brackets are escaped so sentinels and HTML
        comments listed in the review contract do not become real delimiters.
    """
    return value.replace("<", "&lt;").replace(">", "&gt;")


def render_review_contract(state: dict[str, object]) -> str:
    """Render the script-owned contract used by independent sync reviewers.

    Parameters:
        state: Current sync state loaded from `.coding_workflow/diffs`.

    Expected output:
        Markdown contract generated from script constants and current sync
        state. The reviewer prompt must point to this section instead of
        copying file lists, markers, sentinels, or blocking statuses.
    """
    core_paths = [str(record["path"]) for record in state["core_files"]]
    prompt_paths = [
        str(record["path"]) for record in state["sync_prompt_files"]
    ]
    lines = [
        "## Sync Review Contract",
        "",
        (
            "This script-owned contract is the authoritative checklist for "
            "the independent sync reviewer. Final gate owns mechanical "
            "structure, status, and residue checks; reviewers focus on "
            "evidence, upstream cross-check, and operability."
        ),
    ]
    lines.extend(render_contract_list(
        title="Required PR body sections",
        values=list(PR_BODY_REQUIRED_SECTIONS),
    ))
    lines.extend(render_contract_list(
        title="Required sync sentinels",
        values=list(required_sync_sentinels()),
    ))
    lines.extend(render_contract_list(
        title="Repo Facts Map headings",
        values=list(REPO_FACTS_HEADINGS),
    ))
    lines.extend(render_contract_list(
        title="Core documents to reconcile",
        values=core_paths,
    ))
    lines.extend(render_contract_list(
        title="Upstream instruction files",
        values=prompt_paths,
    ))
    return "\n".join(lines)


def render_sync_auto_section(state: dict[str, object]) -> str:
    """Render deterministic PR body sections from current sync state.

    Parameters:
        state: Current sync state loaded from `.coding_workflow/diffs`.

    Expected output:
        Markdown containing only script-owned sections. `--check-final`
        compares this block byte-for-byte against `PR_BODY.md`.
    """
    dirty_core_files = state["dirty_core_files"]
    core_files = state["core_files"]
    lines = [
        SYNC_AUTO_START,
        "## Sync Summary",
        "",
        "- sync mode: full_reconcile",
        f"- upstream_resolved_commit: {state['upstream_resolved_commit']}",
        f"- project_head_commit: {state['project_head_commit']}",
        "- evidence_source: working_tree",
        f"- core files checked: {state['core_files_checked']}",
        "",
        "## Working Tree State at Sync Time",
        "",
        (
            f"- project_head_commit: {state['project_head_commit']} "
            "(base commit; evidence content is read from the working tree)"
        ),
        "- evidence_source: working_tree",
        "- dirty core files (working tree differs from HEAD):",
    ]
    if dirty_core_files:
        for path in dirty_core_files:
            lines.append(f"  - `{path}`")
    if not dirty_core_files:
        lines.append("  - none")
    lines.extend(("", render_review_contract(state=state), ""))
    lines.extend((
        "## Upstream Templates at Sync Time",
        "",
    ))
    for record in core_files:
        lines.append(
            f"- `{record['path']}`: {record['upstream_raw_url']}"
        )
    lines.extend((
        "",
        "## Upstream Instructions at Sync Time",
        "",
    ))
    for record in state["sync_prompt_files"]:
        lines.append(
            f"- `{record['path']}`: {record['upstream_raw_url']}"
        )
    lines.extend((
        "",
        "## Installation Status",
        "",
        "| File | Action | Note |",
        "|---|---|---|",
    ))
    for record in core_files:
        lines.append(
            f"| `{record['path']}` | `{record['status']}` | "
            f"{record['note']} |"
        )
    lines.append(SYNC_AUTO_END)
    return "\n".join(lines)


def render_repo_facts_template() -> str:
    """Render the agent-owned Repo Facts Map template.

    Parameters:
        None.

    Expected output:
        Markdown with 10 required headings. The script validates structure, but
        independent review remains responsible for evidence quality.
    """
    lines = [
        "## Repo Facts Map",
        "",
        "每项必须有代码路径 / 文档路径 / 命令输出等证据；不能编。",
        "",
    ]
    for heading in REPO_FACTS_HEADINGS:
        lines.extend((heading, "证据: 待补充", ""))
    return "\n".join(lines).rstrip()


def render_full_document_reconcile_template(
    state: dict[str, object],
) -> str:
    """Render the agent-owned full reconcile evidence template.

    Parameters:
        state: Current sync state loaded from `.coding_workflow/diffs`.

    Expected output:
        Markdown table containing all 9 core documents. The script gives
        mechanical signals; the agent fills semantic judgment and evidence.
    """
    lines = [
        "## Full Document Reconcile",
        "",
        "| 文件 | 当前脚本信号 | 是否需要更新 | 证据 |",
        "|---|---|---|---|",
    ]
    for record in state["core_files"]:
        lines.append(
            f"| `{record['path']}` | `{record['status']}` | "
            "待判断 | 待补充 |"
        )
    return "\n".join(lines)


def render_remaining_human_decisions_template() -> str:
    """Render the agent-owned human decision placeholder.

    Parameters:
        None.

    Expected output:
        A minimal Markdown section. Agents keep `none` only when no unresolved
        project decision remains after reconcile.
    """
    return "\n".join((
        "## Remaining Human Decisions",
        "",
        "- none",
    ))


def wrap_agent_section(section_name: str, content: str) -> str:
    """Wrap one agent-owned section with stable sentinels.

    Parameters:
        section_name: Stable section key from `AGENT_SECTIONS`.
        content: Markdown content to preserve across script refreshes.

    Expected output:
        Sentinel-wrapped Markdown section.
    """
    return "\n".join((
        agent_section_start(section_name=section_name),
        content.rstrip(),
        agent_section_end(section_name=section_name),
    ))


def render_pr_body_skeleton(state: dict[str, object]) -> str:
    """Render a complete sentinel-based PR body skeleton.

    Parameters:
        state: Current sync state loaded from `.coding_workflow/diffs`.

    Expected output:
        Markdown body whose auto block can be replaced deterministically while
        preserving agent-owned semantic sections.
    """
    sections = [
        SYNC_PR_BODY_MARKER,
        wrap_agent_section(
            section_name="repo_facts_map",
            content=render_repo_facts_template(),
        ),
        render_sync_auto_section(state=state),
        wrap_agent_section(
            section_name="full_document_reconcile",
            content=render_full_document_reconcile_template(state=state),
        ),
        wrap_agent_section(
            section_name="remaining_human_decisions",
            content=render_remaining_human_decisions_template(),
        ),
    ]
    return "\n\n".join(sections) + "\n"


def write_pr_body_skeleton(
    diffs_root: Path,
    state: dict[str, object],
) -> None:
    """Write the current PR body skeleton into sync evidence.

    Parameters:
        diffs_root: `.coding_workflow/diffs` path.
        state: Current sync state.

    Expected output:
        `.coding_workflow/diffs/pr_body_skeleton.md` is ready for agents to
        copy or for `--update-pr-body` to apply.
    """
    (diffs_root / PR_BODY_SKELETON_FILE).write_text(
        render_pr_body_skeleton(state=state),
        encoding="utf-8",
    )


def write_agent_workorder(
    diffs_root: Path,
    state: dict[str, object],
) -> None:
    """Write a bounded action list for the next agent.

    Parameters:
        diffs_root: `.coding_workflow/diffs` path.
        state: Current sync state.

    Expected output:
        `.coding_workflow/diffs/agent_workorder.md` translates script signals
        into actions without claiming semantic alignment.
    """
    lines = [
        "# Agent Workorder",
        "",
        (
            "本工单只表达脚本发现的机械信号；"
            "语义是否对齐仍由 agent 和 reviewer 判断。"
        ),
        "",
        "## 入口",
        "",
        "1. 先补 `PR_BODY.md` 的 `Repo Facts Map`。",
        f"2. 按下表处理 {len(state['core_files'])} 个核心文档。",
        "3. 重跑 sync；最终提交前运行 `sync.sh --final`。",
        "",
        "## 文件处理清单",
        "",
        "| 文件 | 脚本信号 | 机械动作 | marker / TODO 命中 |",
        "|---|---|---|---|",
    ]
    for record in state["core_files"]:
        hits = record["marker_hits"]
        hit_text = "<br>".join(str(hit) for hit in hits) if hits else "none"
        lines.append(
            f"| `{record['path']}` | `{record['status']}` | "
            f"{record['mechanical_action']} | {hit_text} |"
        )
    lines.extend((
        "",
        "## 本地读取优先级",
        "",
        "- 上游原文：`.coding_workflow/diffs/upstream_full/`。",
        "- 本地 diff：`.coding_workflow/diffs/upstream_vs_local/`。",
        "- PR body 骨架：`.coding_workflow/diffs/pr_body_skeleton.md`。",
        "- 独立 reviewer 仍使用 PR body 中的 commit-pinned raw URL 复验。",
    ))
    (diffs_root / WORKORDER_FILE).write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def collect_sync_prompt_records(
    upstream_dir: Path,
    upstream_sha: str,
    upstream_full_root: Path,
) -> list[dict[str, object]]:
    """Verify and stage upstream instruction prompts for PR review.

    Parameters:
        upstream_dir: Local upstream clone.
        upstream_sha: Latest upstream commit.
        upstream_full_root: Root of the staged upstream text mirror.

    Expected output:
        Prompt records with live commit-pinned raw URLs and local mirror paths.
        A missing prompt fails fast before PR body automation can publish a
        dead review-instruction link.
    """
    prompt_records: list[dict[str, object]] = []
    for rel_path in SYNC_PROMPT_FILES:
        upstream_text = file_at_ref(
            upstream_dir=upstream_dir,
            ref=upstream_sha,
            path=rel_path,
        )
        if upstream_text is None:
            sys.exit(
                f"FATAL: upstream is missing required sync prompt file at "
                f"{upstream_sha[:12]}: {rel_path}"
            )

        upstream_full_path = upstream_full_root / rel_path
        upstream_full_path.parent.mkdir(parents=True, exist_ok=True)
        upstream_full_path.write_text(upstream_text, encoding="utf-8")
        prompt_records.append({
            "path": rel_path,
            "upstream_raw_url": upstream_raw_url(
                upstream_sha=upstream_sha,
                rel_path=rel_path,
            ),
            "upstream_full_path": (
                f"{DIFFS_DIR}/{UPSTREAM_FULL_DIR}/{rel_path}"
            ),
        })
    return prompt_records


def stage_full_reconcile_outputs(
    repo_root: Path,
    upstream_dir: Path,
    upstream_sha: str,
    project_sha: str,
) -> tuple[dict[str, object], list[str]]:
    """Generate scratch evidence and install missing core templates.

    Parameters:
        repo_root: Target project path.
        upstream_dir: Local upstream clone.
        upstream_sha: Latest upstream commit.
        project_sha: Target project base commit at sync time.

    Expected output:
        Sync state and dirty core document paths. Scratch
        evidence is regenerated under `.coding_workflow/diffs/` on every run.
    """
    diffs_root = diffs_root_for(repo_root=repo_root)
    if diffs_root.exists():
        shutil.rmtree(diffs_root)
    comparison_root = diffs_root / "upstream_vs_local"
    upstream_full_root = diffs_root / UPSTREAM_FULL_DIR
    comparison_root.mkdir(parents=True, exist_ok=True)
    upstream_full_root.mkdir(parents=True, exist_ok=True)

    core_records: list[dict[str, object]] = []
    for rel_path in CORE_FILES:
        upstream_text = file_at_ref(
            upstream_dir=upstream_dir,
            ref=upstream_sha,
            path=rel_path,
        )
        if upstream_text is None:
            sys.exit(
                f"FATAL: upstream is missing required core file at "
                f"{upstream_sha[:12]}: {rel_path}"
            )

        local_path = repo_root / rel_path
        exists = local_path.exists()
        local_text = local_path.read_text(encoding="utf-8") if exists else ""
        status, note = classify_core_file(
            rel_path=rel_path,
            exists=exists,
            local_text=local_text,
            upstream_text=upstream_text,
        )

        safe_name = rel_path.replace("/", "__") + ".diff"
        diff_rel_path = f"{DIFFS_DIR}/upstream_vs_local/{safe_name}"
        diff_text = render_diff(
            left=upstream_text,
            right=local_text,
            left_label=f"upstream/{rel_path}",
            right_label=f"local/{rel_path}",
        )
        (comparison_root / safe_name).write_text(diff_text, encoding="utf-8")

        upstream_full_path = upstream_full_root / rel_path
        upstream_full_path.parent.mkdir(parents=True, exist_ok=True)
        upstream_full_path.write_text(upstream_text, encoding="utf-8")

        upstream_full_rel_path = f"{DIFFS_DIR}/{UPSTREAM_FULL_DIR}/{rel_path}"
        marker_source_text = upstream_text if not exists else local_text
        core_records.append({
            "path": rel_path,
            "status": status,
            "note": note,
            "mechanical_action": mechanical_action_for_status(status=status),
            "marker_hits": marker_hits(text=marker_source_text),
            "upstream_raw_url": upstream_raw_url(
                upstream_sha=upstream_sha,
                rel_path=rel_path,
            ),
            "upstream_full_path": upstream_full_rel_path,
            "diff_path": diff_rel_path,
        })

        if not exists:
            local_path.parent.mkdir(parents=True, exist_ok=True)
            local_path.write_text(upstream_text, encoding="utf-8")

    sync_prompt_records = collect_sync_prompt_records(
        upstream_dir=upstream_dir,
        upstream_sha=upstream_sha,
        upstream_full_root=upstream_full_root,
    )
    write_installation_status(diffs_root=diffs_root, core_records=core_records)
    dirty_core_files = collect_dirty_core_files(repo_root=repo_root)
    state = build_sync_state(
        upstream_sha=upstream_sha,
        project_sha=project_sha,
        dirty_core_files=dirty_core_files,
        core_records=core_records,
        sync_prompt_records=sync_prompt_records,
    )
    write_full_reconcile_report(
        diffs_root=diffs_root,
        upstream_sha=upstream_sha,
        project_sha=project_sha,
        dirty_core_files=dirty_core_files,
        core_records=core_records,
    )
    write_sync_state(repo_root=repo_root, state=state)
    write_pr_body_skeleton(diffs_root=diffs_root, state=state)
    write_agent_workorder(diffs_root=diffs_root, state=state)
    return state, dirty_core_files


def print_summary(
    upstream_sha: str,
    project_sha: str,
    state: dict[str, object],
    dirty_core_files: list[str],
) -> None:
    """Print user-facing sync output.

    Parameters:
        upstream_sha: Latest upstream commit.
        project_sha: Target project base commit at sync time.
        state: Current sync state.
        dirty_core_files: Core documents whose working tree content differs
            from HEAD at sync time.

    Expected output:
        Stdout fields that can be copied into PR_BODY.md.
    """
    print("=" * 70)
    print("sync mode: full_reconcile")
    print(f"upstream:  {upstream_sha[:12]}")
    print(f"project:   {project_sha[:12]}")
    print()
    print("Read these in order:")
    print("  1. .coding_workflow/diffs/agent_workorder.md")
    print("  2. .coding_workflow/diffs/pr_body_skeleton.md")
    print("  3. .coding_workflow/diffs/full_reconcile_report.md")
    print("  4. .coding_workflow/diffs/installation_status.md")
    print("  5. .coding_workflow/diffs/upstream_vs_local/")
    print("  6. .coding_workflow/diffs/upstream_full/")
    print()
    print("Reviewer prompt pinned to upstream_resolved_commit:")
    for rel_path in SYNC_PROMPT_FILES:
        url = upstream_raw_url(upstream_sha=upstream_sha, rel_path=rel_path)
        print(f"  - {rel_path}: {url}")
    print("First action: produce a full Repo Facts Map in PR body.")
    print(
        "The PR will be reviewed by an LLM using the thin reviewer prompt URL "
        "above and the script-owned Sync Review Contract in PR_BODY.md."
    )
    print()
    print("Sync Summary fields for PR body (transcribe verbatim):")
    print("  - sync mode: full_reconcile")
    print(f"  - upstream_resolved_commit: {upstream_sha}")
    print(f"  - project_head_commit: {project_sha}")
    print("  - evidence_source: working_tree")
    print(f"  - core files checked: {len(CORE_FILES)}")
    print()
    print("Working Tree State at Sync Time:")
    print(
        "  - project_head_commit is the base commit; evidence content "
        "is read from the working tree."
    )
    print("  - evidence_source: working_tree")
    print("  - dirty core files (working tree differs from HEAD):")
    if dirty_core_files:
        for path in dirty_core_files:
            print(f"    - {path}")
    else:
        print("    - none")
    print()
    print("Upstream templates at upstream_resolved_commit (for PR review reference):")
    for rel_path in CORE_FILES:
        url = upstream_raw_url(upstream_sha=upstream_sha, rel_path=rel_path)
        print(f"  - {rel_path}: {url}")
    print()

    signals = [
        f"  - {record['path']}: {record['status']}"
        for record in state["core_files"]
        if record["status"] != "specialized"
    ]
    if signals:
        print("Review-required signals (the PR review agent must address each):")
        for signal in signals:
            print(signal)
    print()
    print("Generated agent helpers:")
    print("  - .coding_workflow/diffs/agent_workorder.md")
    print("  - .coding_workflow/diffs/pr_body_skeleton.md")
    print("  - .coding_workflow/diffs/sync_state.json")
    print("=" * 70)


def load_sync_state(repo_root: Path) -> dict[str, object]:
    """Load the current sync state from the scratch evidence directory.

    Parameters:
        repo_root: Target project path.

    Expected output:
        Parsed JSON object for the current evidence epoch. Missing or stale
        state fails fast because PR body automation must not infer values.
    """
    state_path = state_path_for(repo_root=repo_root)
    if not state_path.exists():
        sys.exit(
            f"FATAL: missing {DIFFS_DIR}/{STATE_FILE}; run sync before "
            "updating or checking PR_BODY.md."
        )
    state = json.loads(state_path.read_text(encoding="utf-8"))
    required_keys = (
        "schema_version",
        "sync_mode",
        "upstream_resolved_commit",
        "project_head_commit",
        "evidence_source",
        "core_files_checked",
        "dirty_core_files",
        "sync_prompt_files",
        "core_files",
    )
    for key in required_keys:
        if key not in state:
            sys.exit(f"FATAL: sync state missing required key: {key}")
    return state


def extract_block(text: str, start: str, end: str) -> str:
    """Extract one sentinel-delimited block.

    Parameters:
        text: Full Markdown document.
        start: Exact start sentinel.
        end: Exact end sentinel.

    Expected output:
        Raw content between sentinels. Duplicate or malformed sentinels fail
        fast so script-owned and agent-owned regions cannot drift silently.
    """
    if text.count(start) != 1:
        sys.exit(f"FATAL: expected exactly one sentinel: {start}")
    if text.count(end) != 1:
        sys.exit(f"FATAL: expected exactly one sentinel: {end}")
    start_index = text.index(start) + len(start)
    end_index = text.index(end)
    if end_index < start_index:
        sys.exit(f"FATAL: malformed sentinel order: {start} before {end}")
    return text[start_index:end_index].strip("\n")


def sentinel_span(text: str, start: str, end: str) -> tuple[int, int]:
    """Return one sentinel-delimited span including both sentinels.

    Parameters:
        text: Full Markdown document.
        start: Exact start sentinel.
        end: Exact end sentinel.

    Expected output:
        `(start_index, end_index)` slice bounds for the full block. Duplicate
        or malformed sentinels fail fast before a refresh can lose content.
    """
    if text.count(start) != 1:
        sys.exit(f"FATAL: expected exactly one sentinel: {start}")
    if text.count(end) != 1:
        sys.exit(f"FATAL: expected exactly one sentinel: {end}")
    start_index = text.index(start)
    end_index = text.index(end) + len(end)
    if end_index < start_index:
        sys.exit(f"FATAL: malformed sentinel order: {start} before {end}")
    return start_index, end_index


def assert_no_content_outside_sync_sections(text: str) -> None:
    """Fail when a sentinel PR body contains refresh-unsafe outer content.

    Parameters:
        text: Existing PR body text with sync sentinels.

    Expected output:
        None. Human-authored content must live inside one of the three
        agent-owned sections so script refreshes cannot silently drop work.
    """
    if text.count(SYNC_PR_BODY_MARKER) != 1:
        sys.exit(f"FATAL: expected exactly one marker: {SYNC_PR_BODY_MARKER}")
    marker_start = text.index(SYNC_PR_BODY_MARKER)
    marker_end = marker_start + len(SYNC_PR_BODY_MARKER)
    spans = [(marker_start, marker_end)]
    spans.append(sentinel_span(
        text=text,
        start=SYNC_AUTO_START,
        end=SYNC_AUTO_END,
    ))
    for section_name in AGENT_SECTIONS:
        spans.append(sentinel_span(
            text=text,
            start=agent_section_start(section_name=section_name),
            end=agent_section_end(section_name=section_name),
        ))
    spans.sort()

    outside_parts: list[str] = []
    cursor = 0
    for start_index, end_index in spans:
        if start_index < cursor:
            sys.exit("FATAL: malformed overlapping sync sentinel sections.")
        outside_parts.append(text[cursor:start_index])
        cursor = end_index
    outside_parts.append(text[cursor:])

    if "".join(outside_parts).strip():
        sys.exit(
            "FATAL: PR_BODY.md contains content outside sync sentinel "
            "sections. Move human-authored text into repo_facts_map, "
            "full_document_reconcile, or remaining_human_decisions before "
            "rerunning sync."
        )


def pr_body_has_any_sync_sentinel(text: str) -> bool:
    """Return whether a PR body already uses sync sentinels.

    Parameters:
        text: Existing PR body text.

    Expected output:
        True when any known sync sentinel appears. This distinguishes a prior
        sync PR body from an unrelated local PR draft.
    """
    if SYNC_AUTO_START in text or SYNC_AUTO_END in text:
        return True
    for section_name in AGENT_SECTIONS:
        if agent_section_start(section_name=section_name) in text:
            return True
        if agent_section_end(section_name=section_name) in text:
            return True
    return False


def preserved_agent_sections(text: str) -> dict[str, str]:
    """Return agent-owned sections from an existing sentinel PR body.

    Parameters:
        text: Existing PR body text with sync sentinels.

    Expected output:
        Mapping from section name to existing content. The script preserves
        these regions across deterministic auto-section refreshes.
    """
    sections: dict[str, str] = {}
    for section_name in AGENT_SECTIONS:
        sections[section_name] = extract_block(
            text=text,
            start=agent_section_start(section_name=section_name),
            end=agent_section_end(section_name=section_name),
        )
    return sections


def render_pr_body_with_preserved_sections(
    state: dict[str, object],
    sections: dict[str, str],
) -> str:
    """Render a PR body using fresh auto state and preserved agent text.

    Parameters:
        state: Current sync state.
        sections: Existing agent-owned Markdown sections.

    Expected output:
        Complete sentinel PR body. Script-owned sections come from current
        state; semantic sections come from `sections`.
    """
    body_sections = [
        SYNC_PR_BODY_MARKER,
        wrap_agent_section(
            section_name="repo_facts_map",
            content=sections["repo_facts_map"],
        ),
        render_sync_auto_section(state=state),
        wrap_agent_section(
            section_name="full_document_reconcile",
            content=sections["full_document_reconcile"],
        ),
        wrap_agent_section(
            section_name="remaining_human_decisions",
            content=sections["remaining_human_decisions"],
        ),
    ]
    return "\n\n".join(body_sections) + "\n"


def update_pr_body(repo_root: Path, pr_body_path: Path) -> None:
    """Create or refresh a sentinel-based sync PR body.

    Parameters:
        repo_root: Target project path.
        pr_body_path: PR body file to create or update.

    Expected output:
        `PR_BODY.md` contains current deterministic sync sections. If an older
        non-sync draft exists, it is copied into scratch evidence before the
        file is replaced with the sync skeleton.
    """
    state = load_sync_state(repo_root=repo_root)
    skeleton = render_pr_body_skeleton(state=state)
    if not pr_body_path.exists():
        pr_body_path.write_text(skeleton, encoding="utf-8")
        print(f"Created {pr_body_path} from current sync skeleton.")
        return

    existing = pr_body_path.read_text(encoding="utf-8")
    if not pr_body_has_any_sync_sentinel(text=existing):
        previous_path = diffs_root_for(repo_root=repo_root) / PR_BODY_PREVIOUS_FILE
        previous_path.write_text(existing, encoding="utf-8")
        pr_body_path.write_text(skeleton, encoding="utf-8")
        print(
            f"Replaced non-sync {pr_body_path}; previous content saved to "
            f"{DIFFS_DIR}/{PR_BODY_PREVIOUS_FILE}."
        )
        return

    assert_no_content_outside_sync_sections(text=existing)
    sections = preserved_agent_sections(text=existing)
    refreshed = render_pr_body_with_preserved_sections(
        state=state,
        sections=sections,
    )
    pr_body_path.write_text(refreshed, encoding="utf-8")
    print(f"Updated script-owned sync sections in {pr_body_path}.")


def check_no_template_residue(path: Path, text: str) -> list[str]:
    """Return template residue failures for one text file.

    Parameters:
        path: File path used in diagnostics.
        text: UTF-8 text to scan.

    Expected output:
        Failure messages. The caller decides whether to exit so multiple
        issues can be reported together.
    """
    failures: list[str] = []
    markers = (*TEMPLATE_MARKERS, *TODO_ANCHOR_COMMENTS)
    for line_number, line in enumerate(text.splitlines(), start=1):
        for marker in markers:
            if marker in line:
                failures.append(f"{path}:{line_number}: template residue {marker}")
    return failures


def check_no_unfilled_agent_placeholders(text: str) -> list[str]:
    """Return failures for script-generated agent placeholders.

    Parameters:
        text: Existing PR body text.

    Expected output:
        Failure messages for placeholders that mean the agent never completed a
        semantic section. Agents may still write `待人工确认` when evidence is
        genuinely unavailable and list it under Remaining Human Decisions.
    """
    failures: list[str] = []
    for placeholder in UNFILLED_AGENT_PLACEHOLDERS:
        if placeholder in text:
            failures.append(
                f"PR_BODY.md still contains placeholder: {placeholder}. "
                "Use `待人工确认` under Remaining Human Decisions for real "
                "unresolved items."
            )
    return failures


def remove_review_contract_section(text: str) -> str:
    """Remove the script-owned review contract before residue scanning.

    Parameters:
        text: Full PR body text.

    Expected output:
        PR body text without the generated contract section. The contract must
        list marker literals for reviewer use, so residue checks should inspect
        human-authored sections and other auto evidence, not this checklist.
    """
    start = "\n## Sync Review Contract\n"
    end = "\n## Upstream Templates at Sync Time\n"
    if start not in text or end not in text:
        return text
    start_index = text.index(start)
    end_index = text.index(end)
    if end_index <= start_index:
        return text
    return text[:start_index] + text[end_index:]


def check_repo_facts_section(text: str) -> list[str]:
    """Return structural failures for the Repo Facts Map section.

    Parameters:
        text: Existing PR body text.

    Expected output:
        Missing-heading failures only. Evidence quality is intentionally left to
        the independent sync PR reviewer.
    """
    section = extract_block(
        text=text,
        start=agent_section_start(section_name="repo_facts_map"),
        end=agent_section_end(section_name="repo_facts_map"),
    )
    failures: list[str] = []
    for heading in REPO_FACTS_HEADINGS:
        if heading not in section:
            failures.append(f"Repo Facts Map missing heading: {heading}")
    return failures


def check_full_document_reconcile_section(text: str) -> list[str]:
    """Return structural failures for Full Document Reconcile.

    Parameters:
        text: Existing PR body text.

    Expected output:
        Missing-core-file failures. This verifies coverage, not the truth of the
        agent's semantic evidence.
    """
    section = extract_block(
        text=text,
        start=agent_section_start(section_name="full_document_reconcile"),
        end=agent_section_end(section_name="full_document_reconcile"),
    )
    failures: list[str] = []
    for rel_path in CORE_FILES:
        if rel_path not in section:
            failures.append(f"Full Document Reconcile missing file: {rel_path}")
    return failures


def check_blocking_statuses(state: dict[str, object]) -> list[str]:
    """Return failures for mechanical statuses that cannot pass final check.

    Parameters:
        state: Current sync state.

    Expected output:
        Failure messages for unresolved template installation/copy/residue
        states. Explicit human exceptions belong in reviewer judgment, not in
        this final mechanical gate.
    """
    failures: list[str] = []
    for record in state["core_files"]:
        status = str(record["status"])
        path = str(record["path"])
        if status in BLOCKING_FINAL_STATUSES:
            failures.append(f"{path} still has blocking sync status: {status}")
    return failures


def check_sync_state_shape(state: dict[str, object]) -> list[str]:
    """Return failures when current state lacks required file coverage.

    Parameters:
        state: Current sync state.

    Expected output:
        Failure messages for missing core files or prompt files. This keeps the
        PR body review inputs complete without making semantic claims.
    """
    failures: list[str] = []
    core_paths = [str(record["path"]) for record in state["core_files"]]
    prompt_paths = [str(record["path"]) for record in state["sync_prompt_files"]]
    for rel_path in CORE_FILES:
        if rel_path not in core_paths:
            failures.append(f"sync_state missing core file: {rel_path}")
    for rel_path in SYNC_PROMPT_FILES:
        if rel_path not in prompt_paths:
            failures.append(f"sync_state missing prompt file: {rel_path}")
    return failures


def check_pr_body_auto_section(
    state: dict[str, object],
    text: str,
) -> list[str]:
    """Return failures when PR body auto section is stale or edited.

    Parameters:
        state: Current sync state.
        text: Existing PR body text.

    Expected output:
        Failure messages. A mismatch means the PR body no longer describes the
        current `.coding_workflow/diffs/sync_state.json` evidence epoch.
    """
    actual = "\n".join((
        SYNC_AUTO_START,
        extract_block(text=text, start=SYNC_AUTO_START, end=SYNC_AUTO_END),
        SYNC_AUTO_END,
    ))
    expected = render_sync_auto_section(state=state)
    if actual != expected:
        return [
            "PR_BODY.md sync auto section differs from current sync_state.json; "
            "rerun sync or refresh PR_BODY.md."
        ]
    return []


def check_final_pr_body(repo_root: Path, pr_body_path: Path) -> None:
    """Run the final mechanical sync PR body gate.

    Parameters:
        repo_root: Target project path.
        pr_body_path: PR body file to validate.

    Expected output:
        Exit 0 when structure, sentinels, auto state, raw URLs, and mechanical
        residue checks pass. This does not certify Repo Facts Map quality.
    """
    if not pr_body_path.exists():
        sys.exit(f"FATAL: missing PR body file: {pr_body_path}")
    state = load_sync_state(repo_root=repo_root)
    text = pr_body_path.read_text(encoding="utf-8")
    failures: list[str] = []
    if SYNC_PR_BODY_MARKER not in text:
        failures.append("PR_BODY.md missing sync PR body marker.")
    assert_no_content_outside_sync_sections(text=text)
    failures.extend(check_sync_state_shape(state=state))
    failures.extend(check_pr_body_auto_section(state=state, text=text))
    failures.extend(check_repo_facts_section(text=text))
    failures.extend(check_full_document_reconcile_section(text=text))
    failures.extend(check_blocking_statuses(state=state))
    failures.extend(check_no_template_residue(
        path=pr_body_path,
        text=remove_review_contract_section(text=text),
    ))
    failures.extend(check_no_unfilled_agent_placeholders(text=text))
    for rel_path in CORE_FILES:
        core_path = repo_root / rel_path
        if core_path.exists():
            failures.extend(check_no_template_residue(
                path=core_path,
                text=core_path.read_text(encoding="utf-8"),
            ))
    if failures:
        sys.exit("FATAL: final sync check failed:\n  " + "\n  ".join(failures))
    print(
        "Final sync check passed: PR_BODY.md matches current sync_state.json "
        "and contains required structural coverage."
    )


def resolve_repo_root() -> Path:
    """Resolve the target repository root for every script mode.

    Parameters:
        None. The optional `REPO_ROOT` environment variable is honored when set
        by `sync.sh`; otherwise the current directory is used.

    Expected output:
        Absolute target repository path.
    """
    repo_root = (
        Path(os.environ["REPO_ROOT"]).resolve()
        if "REPO_ROOT" in os.environ
        else Path(".").resolve()
    )
    assert_git_repo(repo_root=repo_root)
    return repo_root


def run_full_reconcile() -> int:
    """Run full workflow-docs reconcile.

    Parameters:
        None. Inputs are environment variables set by `sync.sh`:
        `REPO_ROOT` and `UPSTREAM_DIR`.

    Expected output:
        Exit 0 after writing scratch evidence and printing PR-body fields.
    """
    upstream_dir_value = (
        os.environ["UPSTREAM_DIR"]
        if "UPSTREAM_DIR" in os.environ
        else ""
    )
    if not upstream_dir_value:
        sys.exit(
            "FATAL: UPSTREAM_DIR is not set; invoke sync through scripts/sync.sh."
        )

    repo_root = resolve_repo_root()
    upstream_dir = Path(upstream_dir_value).resolve()

    assert_upstream_repo(upstream_dir=upstream_dir)
    assert_no_unmanaged_dirty(repo_root=repo_root)
    assert_no_legacy_source(repo_root=repo_root)
    ensure_gitignore(repo_root=repo_root)

    upstream_sha = git("rev-parse", "HEAD", cwd=upstream_dir).strip()
    project_sha = git_optional("rev-parse", "HEAD", cwd=repo_root)
    if project_sha is None:
        sys.exit(
            "FATAL: target repository has no commits; make an initial commit "
            "before running full workflow-docs reconcile."
        )
    project_sha = project_sha.strip()
    state, dirty_core_files = stage_full_reconcile_outputs(
        repo_root=repo_root,
        upstream_dir=upstream_dir,
        upstream_sha=upstream_sha,
        project_sha=project_sha,
    )
    print_summary(
        upstream_sha=upstream_sha,
        project_sha=project_sha,
        state=state,
        dirty_core_files=dirty_core_files,
    )
    return 0


def main() -> int:
    """Dispatch full reconcile and internal PR body helper modes.

    Parameters:
        None. CLI arguments are intentionally minimal: normal sync, internal
        `--update-pr-body <path>`, or internal `--check-final <path>`.

    Expected output:
        Exit code for the selected mode.
    """
    args = sys.argv[1:]
    if not args:
        return run_full_reconcile()
    if len(args) == 2 and args[0] == "--update-pr-body":
        repo_root = resolve_repo_root()
        update_pr_body(
            repo_root=repo_root,
            pr_body_path=repo_root / args[1],
        )
        return 0
    if len(args) == 2 and args[0] == "--check-final":
        repo_root = resolve_repo_root()
        check_final_pr_body(
            repo_root=repo_root,
            pr_body_path=repo_root / args[1],
        )
        return 0
    sys.exit(
        "FATAL: usage: sync_coding_workflow.py "
        "[--update-pr-body PR_BODY.md | --check-final PR_BODY.md]"
    )


if __name__ == "__main__":
    sys.exit(main())
