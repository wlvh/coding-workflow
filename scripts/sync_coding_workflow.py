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
      -> print_summary()

This script intentionally has no committed baseline manifest. Each run is a
full review of current project facts plus the latest upstream rules. Scratch
evidence is written under `.coding_workflow/diffs/` and is not committed.
"""

from __future__ import annotations

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
    "scripts/sync_workflow_docs.md",
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


def classify_core_file(rel_path: str, exists: bool, local_text: str, upstream_text: str) -> tuple[str, str]:
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


def write_installation_status(diffs_root: Path, items: list[tuple[str, str, str]]) -> None:
    """Write per-core-file status evidence.

    Parameters:
        diffs_root: `.coding_workflow/diffs` path.
        items: `(path, status, note)` rows.

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
    for path, action, note in items:
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
    items: list[tuple[str, str, str]],
) -> None:
    """Write the run-level full reconcile report.

    Parameters:
        diffs_root: `.coding_workflow/diffs` path.
        upstream_sha: Latest upstream commit used by this run.
        project_sha: Target project base commit at sync time.
        dirty_core_files: Core documents whose working tree content differs
            from HEAD at sync time.
        items: Installation status rows.

    Expected output:
        `full_reconcile_report.md` with PR-body fields and review signals.
    """
    signals = [
        f"- `{path}`: `{status}`"
        for path, status, _ in items
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
        "- Repo Facts Map with 10 evidence-backed entries.",
        "- Sync Summary copied from this report.",
        "- Working Tree State at Sync Time copied from this report.",
        "- Installation Status copied from installation_status.md.",
        "- Full Document Reconcile explaining how each core document was checked.",
        "- Remaining Human Decisions, even when empty.",
    ))
    (diffs_root / "full_reconcile_report.md").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def stage_full_reconcile_outputs(
    repo_root: Path,
    upstream_dir: Path,
    upstream_sha: str,
    project_sha: str,
) -> tuple[list[tuple[str, str, str]], list[str]]:
    """Generate scratch evidence and install missing core templates.

    Parameters:
        repo_root: Target project path.
        upstream_dir: Local upstream clone.
        upstream_sha: Latest upstream commit.
        project_sha: Target project base commit at sync time.

    Expected output:
        Installation status rows and dirty core document paths. Scratch
        evidence is regenerated under `.coding_workflow/diffs/` on every run.
    """
    diffs_root = repo_root / ".coding_workflow" / "diffs"
    if diffs_root.exists():
        shutil.rmtree(diffs_root)
    comparison_root = diffs_root / "upstream_vs_local"
    comparison_root.mkdir(parents=True, exist_ok=True)

    statuses: list[tuple[str, str, str]] = []
    for rel_path in CORE_FILES:
        upstream_text = file_at_ref(upstream_dir=upstream_dir, ref=upstream_sha, path=rel_path)
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
        statuses.append((rel_path, status, note))

        safe_name = rel_path.replace("/", "__") + ".diff"
        diff_text = render_diff(
            left=upstream_text,
            right=local_text,
            left_label=f"upstream/{rel_path}",
            right_label=f"local/{rel_path}",
        )
        (comparison_root / safe_name).write_text(diff_text, encoding="utf-8")

        if not exists:
            local_path.parent.mkdir(parents=True, exist_ok=True)
            local_path.write_text(upstream_text, encoding="utf-8")

    write_installation_status(diffs_root=diffs_root, items=statuses)
    dirty_core_files = collect_dirty_core_files(repo_root=repo_root)
    write_full_reconcile_report(
        diffs_root=diffs_root,
        upstream_sha=upstream_sha,
        project_sha=project_sha,
        dirty_core_files=dirty_core_files,
        items=statuses,
    )
    return statuses, dirty_core_files


def print_summary(
    upstream_sha: str,
    project_sha: str,
    statuses: list[tuple[str, str, str]],
    dirty_core_files: list[str],
) -> None:
    """Print user-facing sync output.

    Parameters:
        upstream_sha: Latest upstream commit.
        project_sha: Target project base commit at sync time.
        statuses: Installation status rows.
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
    print("  1. .coding_workflow/diffs/full_reconcile_report.md")
    print("  2. .coding_workflow/diffs/installation_status.md")
    print("  3. .coding_workflow/diffs/upstream_vs_local/")
    print()
    print("Then read these upstream instructions pinned to upstream_resolved_commit:")
    for rel_path in SYNC_PROMPT_FILES:
        url = upstream_raw_url(upstream_sha=upstream_sha, rel_path=rel_path)
        print(f"  - {rel_path}: {url}")
    print("First action: produce a full Repo Facts Map in PR body.")
    print(
        "The PR will be reviewed by an LLM using the pinned sync PR "
        "review system URL above."
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
        f"  - {path}: {status}"
        for path, status, _ in statuses
        if status != "specialized"
    ]
    if signals:
        print("Review-required signals (the PR review agent must address each):")
        for signal in signals:
            print(signal)
    print("=" * 70)


def main() -> int:
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

    repo_root = (
        Path(os.environ["REPO_ROOT"]).resolve()
        if "REPO_ROOT" in os.environ
        else Path(".").resolve()
    )
    upstream_dir = Path(upstream_dir_value).resolve()

    assert_git_repo(repo_root=repo_root)
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
    statuses, dirty_core_files = stage_full_reconcile_outputs(
        repo_root=repo_root,
        upstream_dir=upstream_dir,
        upstream_sha=upstream_sha,
        project_sha=project_sha,
    )
    print_summary(
        upstream_sha=upstream_sha,
        project_sha=project_sha,
        statuses=statuses,
        dirty_core_files=dirty_core_files,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
