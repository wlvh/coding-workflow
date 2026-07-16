"""验证轻量 Workflow Docs Sync harness、reviewer 和 installer。

调用关系：
    pytest / unittest -> WorkflowSyncSkillTests
    测试方法 -> 临时 clean upstream / target Git 仓库
    临时仓库 -> harness / pinned sync / fake gh / review validator
"""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
EXEC_SKILL = REPO_ROOT / "zh/skills/workflow-docs-sync"
REVIEW_SKILL = REPO_ROOT / "zh/skills/workflow-docs-sync-review"
HARNESS = EXEC_SKILL / "scripts/harness.py"
VALIDATE_REVIEW = REVIEW_SKILL / "scripts/validate_review.py"
INSTALL_SKILLS = REPO_ROOT / "zh/scripts/install_skills.py"
OPERATIONS = REPO_ROOT / "zh/scripts/OPERATIONS.md"
REVIEW_SYSTEM = REPO_ROOT / "zh/scripts/sync_pr_review_system.md"
OWNERSHIP = EXEC_SKILL / "references/pass_ownership.json"
MODES = ("PREPARE", "PASS_1", "PASS_2", "PASS_3", "PASS_4", "SUBMIT")
PASS_MODES = ("PASS_1", "PASS_2", "PASS_3", "PASS_4")
SKILL_NAMES = ("workflow-docs-sync", "workflow-docs-sync-review")
CORE_SOURCES = (
    "zh/architecture.md",
    "zh/capability_contract.json",
    "zh/interact.md",
    "zh/docs/business_user_guide.md",
    "zh/TESTING.md",
    "zh/PR_Checklist.md",
    "zh/SOP.md",
    "zh/AGENTS.md",
    "zh/.github/pull_request_template.md",
)
UPSTREAM_SOURCES = (
    "scripts/sync_coding_workflow.py",
    "zh/scripts/sync.sh",
    "zh/scripts/OPERATIONS.md",
    "zh/scripts/sync_pr_review_system.md",
    "zh/scripts/install_skills.py",
)
AGENT_SECTIONS = (
    "repo_facts_map",
    "full_document_reconcile",
    "pr_test_evidence",
    "upstream_drift_log",
    "agent_execution_evidence",
    "remaining_human_decisions",
)


def load_sync_module() -> Any:
    """加载 sync 实现，返回机械 PASS ownership 真相源。"""
    module_path = REPO_ROOT / "scripts/sync_coding_workflow.py"
    spec = importlib.util.spec_from_file_location(
        "sync_coding_workflow_skill_test",
        module_path,
    )
    if spec is None or spec.loader is None:
        raise AssertionError("无法加载 sync_coding_workflow.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SYNC_MODULE = load_sync_module()


def run_command(
    *,
    args: list[str],
    cwd: Path,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """运行测试命令，返回捕获 UTF-8 输出的 CompletedProcess。"""
    return subprocess.run(
        args=args,
        cwd=cwd,
        env=os.environ.copy() if env is None else env,
        check=False,
        capture_output=True,
        encoding="utf-8",
        text=True,
    )


def git(
    *,
    repo_root: Path,
    args: list[str],
) -> subprocess.CompletedProcess[str]:
    """在临时仓库用固定测试身份运行 Git；调用方判断返回码。"""
    return run_command(
        args=[
            "git",
            "-c", "user.email=skill-test@example.com",
            "-c", "user.name=skill-test",
            *args,
        ],
        cwd=repo_root,
    )


def git_head(*, repo_root: Path) -> str:
    """返回临时仓库完整 HEAD SHA。"""
    result = git(repo_root=repo_root, args=["rev-parse", "HEAD"])
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    return result.stdout.strip()


def commit_paths(
    *,
    repo_root: Path,
    paths: list[str],
    message: str,
) -> None:
    """提交显式路径，预期 HEAD 前进。"""
    add = git(repo_root=repo_root, args=["add", "--", *paths])
    commit = git(
        repo_root=repo_root,
        args=["commit", "-q", "-m", message],
    )
    if add.returncode != 0 or commit.returncode != 0:
        raise AssertionError(add.stderr + commit.stderr)


def commit_all(*, repo_root: Path, message: str) -> None:
    """提交临时仓库全部非 ignored 文件。"""
    add = git(repo_root=repo_root, args=["add", "."])
    commit = git(
        repo_root=repo_root,
        args=["commit", "-q", "-m", message],
    )
    if add.returncode != 0 or commit.returncode != 0:
        raise AssertionError(add.stderr + commit.stderr)


def initialize_repo(*, repo_root: Path) -> None:
    """创建带固定身份和一个基线提交的临时仓库。"""
    repo_root.mkdir(parents=True, exist_ok=True)
    result = git(repo_root=repo_root, args=["init", "-q"])
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    (repo_root / "seed.txt").write_text("基线\n", encoding="utf-8")
    commit_all(repo_root=repo_root, message="初始化")


def copy_upstream_sources(*, upstream: Path) -> None:
    """复制真实 sync、模板、prompt、installer 和两个 canonical Skill。"""
    for relative_path in (*UPSTREAM_SOURCES, *CORE_SOURCES):
        source = REPO_ROOT / relative_path
        destination = upstream / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    shutil.copytree(
        src=REPO_ROOT / "zh/skills",
        dst=upstream / "zh/skills",
    )


def create_upstream(
    *,
    repo_root: Path,
    fake_sync: bool,
    final_passes: bool = True,
) -> str:
    """创建 clean upstream；可用快速 fake sync 替代真实实现。"""
    copy_upstream_sources(upstream=repo_root)
    if fake_sync:
        final_lines = (
            "  echo 'final complete'\n"
            if final_passes
            else (
                "  echo 'FATAL: final sync check failed:'\n"
                "  echo '  template residue'\n"
                "  exit 1\n"
            )
        )
        script = repo_root / "zh/scripts/sync.sh"
        script.write_text(
            "#!/usr/bin/env bash\n"
            "set -euo pipefail\n"
            "mkdir -p .coding_workflow/diffs\n"
            "printf 'workorder\\n' > "
            ".coding_workflow/diffs/agent_workorder.md\n"
            "printf '{}\\n' > .coding_workflow/diffs/sync_state.json\n"
            "if [ \"$#\" -eq 1 ] && [ \"$1\" = \"--final\" ]; then\n"
            f"{final_lines}"
            "fi\n"
            "echo 'sync complete'\n",
            encoding="utf-8",
        )
    initialize_repo(repo_root=repo_root)
    return git_head(repo_root=repo_root)


def pr_body_text() -> str:
    """返回包含全部 stable sentinel 的最小测试 PR body。"""
    sections: list[str] = ["<!-- sync:pr-body version=1 -->"]
    for section_name in AGENT_SECTIONS:
        sections.extend(
            (
                f"<!-- sync:agent:start {section_name} -->",
                f"## {section_name}",
                "",
                f"{section_name} baseline",
                f"<!-- sync:agent:end {section_name} -->",
            )
        )
    return "\n".join(sections) + "\n"


def initialize_core_target(
    *,
    target: Path,
    upstream: Path,
    include_pr_body: bool = True,
) -> None:
    """创建已提交核心模板、runtime ignore 和可选 ignored PR body 的目标仓库。"""
    initialize_repo(repo_root=target)
    for source_path in CORE_SOURCES:
        destination = target / source_path.removeprefix("zh/")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(upstream / source_path, destination)
    (target / ".gitignore").write_text(
        "PR_BODY.md\n"
        ".coding_workflow/diffs/\n"
        ".coding_workflow/skill_results/\n"
        ".coding_workflow/skill_runtime/\n",
        encoding="utf-8",
    )
    commit_all(repo_root=target, message="准备核心文档")
    switch = git(
        repo_root=target,
        args=["switch", "-q", "-c", "workflow-docs"],
    )
    if switch.returncode != 0:
        raise AssertionError(switch.stderr)
    if include_pr_body:
        (target / "PR_BODY.md").write_text(
            pr_body_text(),
            encoding="utf-8",
        )


def initialize_specialized_target(*, target: Path) -> None:
    """创建所有核心文档已项目化、但尚未运行真实 sync 的目标仓库。"""
    initialize_repo(repo_root=target)
    for source_path in CORE_SOURCES:
        relative_path = source_path.removeprefix("zh/")
        destination = target / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        content = (
            '{"fixture": "specialized"}\n'
            if relative_path.endswith(".json")
            else f"# {relative_path}\n\nproject-specific fixture\n"
        )
        destination.write_text(content, encoding="utf-8")
    commit_all(repo_root=target, message="准备项目化核心文档")
    switch = git(
        repo_root=target,
        args=["switch", "-q", "-c", "workflow-docs"],
    )
    if switch.returncode != 0:
        raise AssertionError(switch.stderr)


def parse_json(*, result: subprocess.CompletedProcess[str]) -> Any:
    """解析脚本唯一一行 stdout JSON。"""
    lines = [line for line in result.stdout.splitlines() if line]
    if len(lines) != 1:
        raise AssertionError(
            f"stdout={result.stdout!r}, stderr={result.stderr!r}"
        )
    return json.loads(lines[0])


def fake_gh_env(
    *,
    bin_dir: Path,
    payload: dict[str, Any],
    no_real_gh: bool = False,
) -> dict[str, str]:
    """创建读取环境 JSON 的 fake gh，并返回密闭 PATH。"""
    bin_dir.mkdir(parents=True, exist_ok=True)
    fake_gh = bin_dir / "gh"
    fake_gh.write_text(
        f"#!{sys.executable}\n"
        "import os\n"
        "print(os.environ['FAKE_GH_PAYLOAD'])\n",
        encoding="utf-8",
    )
    fake_gh.chmod(0o755)
    env = os.environ.copy()
    suffix = "/usr/bin:/bin:/usr/sbin:/sbin" if no_real_gh else env["PATH"]
    env["PATH"] = f"{bin_dir}{os.pathsep}{suffix}"
    env["FAKE_GH_PAYLOAD"] = json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return env


def run_harness(
    *,
    command: str,
    target: Path,
    upstream: Path | None = None,
    upstream_sha: str | None = None,
    mode: str | None = None,
    pr_number: int | None = None,
    base: str | None = None,
    head: str | None = None,
    env: dict[str, str] | None = None,
    harness_path: Path = HARNESS,
) -> subprocess.CompletedProcess[str]:
    """运行 harness subcommand，并显式拼入适用参数。"""
    args = [
        sys.executable,
        str(harness_path),
        command,
        "--target-repo",
        str(target),
    ]
    if command != "status":
        if upstream is None or upstream_sha is None:
            raise AssertionError("修改命令必须提供 upstream 和 SHA")
        args.extend(
            [
                "--upstream-dir",
                str(upstream),
                "--upstream-sha",
                upstream_sha,
            ]
        )
    if mode is not None:
        args.extend(["--mode", mode])
    if pr_number is not None:
        args.extend(["--pr-number", str(pr_number)])
    if base is not None:
        args.extend(["--base", base])
    if head is not None:
        args.extend(["--head", head])
    return run_command(
        args=args,
        cwd=target,
        env=env,
    )


def append_text(*, path: Path, text: str) -> None:
    """向 UTF-8 文件末尾追加测试内容。"""
    path.write_text(
        path.read_text(encoding="utf-8") + text,
        encoding="utf-8",
    )


def replace_section(
    *,
    path: Path,
    section_name: str,
    text: str,
) -> None:
    """只替换 PR body 指定 sentinel section 的内容。"""
    content = path.read_text(encoding="utf-8")
    start = f"<!-- sync:agent:start {section_name} -->"
    end = f"<!-- sync:agent:end {section_name} -->"
    start_index = content.index(start) + len(start)
    end_index = content.index(end, start_index)
    path.write_text(
        content[:start_index]
        + "\n"
        + text
        + "\n"
        + content[end_index:],
        encoding="utf-8",
    )


def complete_prepare(
    *,
    target: Path,
    upstream: Path,
    upstream_sha: str,
) -> None:
    """执行 PREPARE，失败时立即抛出测试错误。"""
    result = run_harness(
        command="prepare",
        target=target,
        upstream=upstream,
        upstream_sha=upstream_sha,
    )
    if result.returncode != 0:
        raise AssertionError(result.stdout + result.stderr)


def complete_pass(
    *,
    target: Path,
    upstream: Path,
    upstream_sha: str,
    mode: str,
    relative_path: str,
) -> None:
    """按 start/semantic edit/finish 顺序完成一个 PASS。"""
    start = run_harness(
        command="start-pass",
        target=target,
        upstream=upstream,
        upstream_sha=upstream_sha,
        mode=mode,
    )
    if start.returncode != 0:
        raise AssertionError(start.stdout + start.stderr)
    append_text(
        path=target / relative_path,
        text=f"\n{mode} semantic edit\n",
    )
    finish = run_harness(
        command="finish-pass",
        target=target,
        upstream=upstream,
        upstream_sha=upstream_sha,
        mode=mode,
    )
    if finish.returncode != 0:
        raise AssertionError(finish.stdout + finish.stderr)


def complete_prepare_and_passes(
    *,
    target: Path,
    upstream: Path,
    upstream_sha: str,
) -> None:
    """完成 PREPARE 与 PASS_1–PASS_4，保留累计 dirty 文档。"""
    complete_prepare(
        target=target,
        upstream=upstream,
        upstream_sha=upstream_sha,
    )
    edits = {
        "PASS_1": "architecture.md",
        "PASS_2": "interact.md",
        "PASS_3": "TESTING.md",
        "PASS_4": "AGENTS.md",
    }
    for mode, relative_path in edits.items():
        complete_pass(
            target=target,
            upstream=upstream,
            upstream_sha=upstream_sha,
            mode=mode,
            relative_path=relative_path,
        )


def complete_real_prepare_and_passes(
    *,
    target: Path,
    upstream: Path,
    upstream_sha: str,
) -> None:
    """用真实 skeleton/sync 完成 PREPARE 和四个 ownership PASS。"""
    complete_prepare(
        target=target,
        upstream=upstream,
        upstream_sha=upstream_sha,
    )
    start = run_harness(
        command="start-pass",
        target=target,
        upstream=upstream,
        upstream_sha=upstream_sha,
        mode="PASS_1",
    )
    if start.returncode != 0:
        raise AssertionError(start.stdout + start.stderr)
    shutil.copy2(
        target / ".coding_workflow/diffs/pr_body_skeleton.md",
        target / "PR_BODY.md",
    )
    for section_name in (
        "repo_facts_map",
        "full_document_reconcile",
        "agent_execution_evidence",
    ):
        replace_section(
            path=target / "PR_BODY.md",
            section_name=section_name,
            text=f"## {section_name}\n\nreal PASS evidence",
        )
    append_text(path=target / "architecture.md", text="\nPASS_1 edit\n")
    finish = run_harness(
        command="finish-pass",
        target=target,
        upstream=upstream,
        upstream_sha=upstream_sha,
        mode="PASS_1",
    )
    if finish.returncode != 0:
        raise AssertionError(finish.stdout + finish.stderr)
    for mode, relative_path in {
        "PASS_2": "interact.md",
        "PASS_3": "TESTING.md",
        "PASS_4": "AGENTS.md",
    }.items():
        complete_pass(
            target=target,
            upstream=upstream,
            upstream_sha=upstream_sha,
            mode=mode,
            relative_path=relative_path,
        )


def prepare_and_seal_real_submit(
    *,
    target: Path,
    upstream: Path,
    upstream_sha: str,
) -> list[str]:
    """建立真实 SUBMIT baseline，填 evidence 后 seal 并返回精确提交集合。"""
    prepared = run_harness(
        command="prepare-submit",
        target=target,
        upstream=upstream,
        upstream_sha=upstream_sha,
    )
    if prepared.returncode != 0:
        raise AssertionError(prepared.stdout + prepared.stderr)
    replace_section(
        path=target / "PR_BODY.md",
        section_name="pr_test_evidence",
        text=(
            "## PR Test Evidence\n\n"
            "- commands: python -m pytest -q\n"
            "- result: passed\n"
            "- not run / N/A: none"
        ),
    )
    sealed = run_harness(
        command="seal-submit",
        target=target,
        upstream=upstream,
        upstream_sha=upstream_sha,
    )
    if sealed.returncode != 0:
        raise AssertionError(sealed.stdout + sealed.stderr)
    return parse_json(result=sealed)["allowed_commit_paths"]


def pull_request_payload(
    *,
    head_sha: str,
    body: str,
    pr_number: int = 12,
    base: str = "main",
    head: str = "workflow-docs",
) -> dict[str, Any]:
    """返回 finish-submit fake gh 所需完整 PR JSON。"""
    return {
        "number": pr_number,
        "state": "OPEN",
        "headRefOid": head_sha,
        "headRefName": head,
        "baseRefName": base,
        "body": body,
        "url": f"https://example.test/pull/{pr_number}",
    }


def valid_review(
    *,
    verdict: str,
    head_sha: str,
    upstream_sha: str,
    pr_number: int = 12,
    blocker_section: bool = False,
) -> dict[str, Any]:
    """构造完整 review fixture，可选制造 section BLOCKER。"""
    return {
        "verdict": verdict,
        "findings": [],
        "pr": pr_number,
        "head_sha": head_sha,
        "upstream_sha": upstream_sha,
        "review_sections": {
            section: {
                "verdict": (
                    "BLOCKER"
                    if blocker_section and section == "contract_compliance"
                    else "PASS"
                ),
                "evidence": f"{section} evidence",
            }
            for section in (
                "contract_compliance",
                "evidence_quality",
                "full_reconcile_closure",
                "per_pass_evidence_and_propagation",
                "test_drift_and_execution_evidence",
                "upstream_cross_check",
                "operability",
            )
        },
        "evidence_index": ["PR body", "architecture.md", "pytest"],
    }


def review_pr_payload(*, head_sha: str, upstream_sha: str) -> dict[str, Any]:
    """返回 reviewer validator 所需真实 identity 与 auto SHA。"""
    return {
        "number": 12,
        "state": "OPEN",
        "headRefOid": head_sha,
        "body": (
            "<!-- sync:auto:start -->\n"
            f"- upstream_resolved_commit: {upstream_sha}\n"
            "<!-- sync:auto:end -->\n"
        ),
    }


class WorkflowSyncSkillTests(unittest.TestCase):
    """覆盖 prompt、mode handoff、提交、review、安装和模板合同。"""

    def test_titles_ownership_and_transport_alignment(self) -> None:
        """PASS 标题/ownership 双向对账，人工与 Skill transport 不冲突。"""
        ownership = json.loads(OWNERSHIP.read_text(encoding="utf-8"))
        expected = {
            f"PASS_{index}": {
                "title": f"2.{index} {sync_pass['title']}",
                "owned": list(sync_pass["files"]),
            }
            for index, sync_pass in enumerate(
                SYNC_MODULE.SYNC_PASSES,
                start=1,
            )
        }
        self.assertEqual(set(ownership), set(expected))
        operations = OPERATIONS.read_text(encoding="utf-8")
        for mode in PASS_MODES:
            self.assertEqual(ownership[mode]["title"], expected[mode]["title"])
            self.assertEqual(ownership[mode]["owned"], expected[mode]["owned"])
            heading = f"### {ownership[mode]['title']}"
            start = operations.index(heading)
            candidates = [
                position
                for marker in ("\n### ", "\n## ")
                if (position := operations.find(marker, start + 1)) >= 0
            ]
            section = operations[start:min(candidates)]
            opening = section.index("```")
            body_start = section.index("\n", opening)
            body_end = section.index("```", body_start + 1)
            block = section[body_start + 1:body_end]
            self.assertIn("人工 code-block 模式", block)
            self.assertIn("Skill 模式", block)
            self.assertIn("不要执行本 block 末尾的 curl", block)

    def test_skills_do_not_copy_semantic_prompts(self) -> None:
        """两个 SKILL.md 不得复制 PASS/reviewer 任意连续 40 字符。"""
        source_texts = [
            OPERATIONS.read_text(encoding="utf-8"),
            REVIEW_SYSTEM.read_text(encoding="utf-8"),
        ]
        skill_texts = [
            (EXEC_SKILL / "SKILL.md").read_text(encoding="utf-8"),
            (REVIEW_SKILL / "SKILL.md").read_text(encoding="utf-8"),
        ]
        for source_text in source_texts:
            for index in range(len(source_text) - 39):
                fragment = source_text[index:index + 40]
                if fragment.isspace():
                    continue
                for skill_text in skill_texts:
                    self.assertNotIn(fragment, skill_text)

    def test_template_headings_and_pollution_regression(self) -> None:
        """上游空标题必须保留，且不能登记上游专属实现路径。"""
        agents = (REPO_ROOT / "zh/AGENTS.md").read_text(encoding="utf-8")
        testing = (REPO_ROOT / "zh/TESTING.md").read_text(encoding="utf-8")
        self.assertIn("### 核心模块", agents)
        self.assertIn("## 测试文件简介", testing)
        agents_inventory = agents.split("### 业务逻辑", 1)[0]
        for path in (
            "skills/workflow-docs-sync/",
            "skills/workflow-docs-sync-review/",
            "scripts/install_skills.py",
        ):
            self.assertNotIn(path, agents_inventory)
        self.assertNotIn("tests/test_workflow_sync_skill.py", testing)

    def test_prepare_requires_clean_pinned_upstream(self) -> None:
        """PREPARE 拒绝业务 dirty、错误 SHA 和 dirty upstream。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            upstream = root / "upstream"
            target = root / "target"
            sha = create_upstream(
                repo_root=upstream,
                fake_sync=True,
            )
            initialize_core_target(target=target, upstream=upstream)
            append_text(path=target / "seed.txt", text="dirty\n")
            dirty = run_harness(
                command="prepare",
                target=target,
                upstream=upstream,
                upstream_sha=sha,
            )
            self.assertNotEqual(dirty.returncode, 0)
            git(repo_root=target, args=["restore", "seed.txt"])
            wrong = run_harness(
                command="prepare",
                target=target,
                upstream=upstream,
                upstream_sha="0" * 40,
            )
            self.assertNotEqual(wrong.returncode, 0)
            append_text(
                path=upstream / "zh/scripts/OPERATIONS.md",
                text="\ndirty\n",
            )
            dirty_upstream = run_harness(
                command="prepare",
                target=target,
                upstream=upstream,
                upstream_sha=sha,
            )
            self.assertNotEqual(dirty_upstream.returncode, 0)

    def test_prepare_installs_missing_templates(self) -> None:
        """真实 sync 安装模板，PASS 可从 skeleton 初始化 PR body。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            upstream = root / "upstream"
            target = root / "target"
            sha = create_upstream(
                repo_root=upstream,
                fake_sync=False,
            )
            initialize_repo(repo_root=target)
            result = run_harness(
                command="prepare",
                target=target,
                upstream=upstream,
                upstream_sha=sha,
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout)
            payload = parse_json(result=result)
            self.assertIn("architecture.md", payload["changed_paths"])
            self.assertTrue(
                (
                    target
                    / ".coding_workflow/skill_results/PREPARE.json"
                ).is_file()
            )
            start = run_harness(
                command="start-pass",
                target=target,
                upstream=upstream,
                upstream_sha=sha,
                mode="PASS_1",
            )
            self.assertEqual(start.returncode, 0, msg=start.stdout)
            shutil.copy2(
                target / ".coding_workflow/diffs/pr_body_skeleton.md",
                target / "PR_BODY.md",
            )
            replace_section(
                path=target / "PR_BODY.md",
                section_name="repo_facts_map",
                text="PASS_1 smoke",
            )
            append_text(
                path=target / "architecture.md",
                text="\nPASS_1 semantic edit\n",
            )
            finish = run_harness(
                command="finish-pass",
                target=target,
                upstream=upstream,
                upstream_sha=sha,
                mode="PASS_1",
            )
            self.assertEqual(finish.returncode, 0, msg=finish.stdout)

    def test_complete_mode_sequence_handoff(self) -> None:
        """PREPARE 至 SUBMIT 起点必须允许合法累计 dirty handoff。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            upstream = root / "upstream"
            target = root / "target"
            sha = create_upstream(repo_root=upstream, fake_sync=True)
            initialize_core_target(target=target, upstream=upstream)
            complete_prepare_and_passes(
                target=target,
                upstream=upstream,
                upstream_sha=sha,
            )
            submit = run_harness(
                command="prepare-submit",
                target=target,
                upstream=upstream,
                upstream_sha=sha,
            )
            self.assertEqual(submit.returncode, 0, msg=submit.stdout)
            payload = parse_json(result=submit)
            self.assertEqual(
                payload["allowed_commit_paths"],
                ["AGENTS.md", "TESTING.md", "architecture.md", "interact.md"],
            )

    def test_start_pass_rejects_inter_mode_edit(self) -> None:
        """后续 PASS 文件在 PASS_1 开始前被修改时必须失败。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            upstream = root / "upstream"
            target = root / "target"
            sha = create_upstream(repo_root=upstream, fake_sync=True)
            initialize_core_target(target=target, upstream=upstream)
            complete_prepare(
                target=target,
                upstream=upstream,
                upstream_sha=sha,
            )
            append_text(path=target / "TESTING.md", text="\ninter-mode edit\n")
            result = run_harness(
                command="start-pass",
                target=target,
                upstream=upstream,
                upstream_sha=sha,
                mode="PASS_1",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(
                parse_json(result=result)["error"],
                "mode 间发现未归属改动",
            )

    def test_finish_pass_enforces_path_and_pr_body_sections(self) -> None:
        """当前 PASS 只能修改 owned 文档和允许的 PR body section。"""
        for scenario in ("path", "rename", "section"):
            with self.subTest(scenario=scenario):
                with tempfile.TemporaryDirectory() as temp_dir:
                    root = Path(temp_dir)
                    upstream = root / "upstream"
                    target = root / "target"
                    sha = create_upstream(repo_root=upstream, fake_sync=True)
                    initialize_core_target(target=target, upstream=upstream)
                    if scenario == "rename":
                        source = target / "?? architecture.md"
                        source.touch()
                        (target / "architecture.md").unlink()
                        commit_paths(
                            repo_root=target,
                            paths=["architecture.md", "?? architecture.md"],
                            message="prepare rename source",
                        )
                    complete_prepare(
                        target=target,
                        upstream=upstream,
                        upstream_sha=sha,
                    )
                    start = run_harness(
                        command="start-pass",
                        target=target,
                        upstream=upstream,
                        upstream_sha=sha,
                        mode="PASS_1",
                    )
                    self.assertEqual(start.returncode, 0)
                    if scenario == "rename":
                        source.replace(target / "architecture.md")
                        git(
                            repo_root=target,
                            args=["add", "-N", "architecture.md"],
                        ).check_returncode()
                    else:
                        append_text(
                            path=target / "architecture.md",
                            text="\nPASS_1 edit\n",
                        )
                    if scenario == "path":
                        append_text(
                            path=target / "TESTING.md",
                            text="\nunauthorized\n",
                        )
                    elif scenario == "section":
                        replace_section(
                            path=target / "PR_BODY.md",
                            section_name="pr_test_evidence",
                            text="unauthorized section",
                        )
                    finish = run_harness(
                        command="finish-pass",
                        target=target,
                        upstream=upstream,
                        upstream_sha=sha,
                        mode="PASS_1",
                    )
                    self.assertNotEqual(finish.returncode, 0)
                    if scenario == "rename":
                        self.assertEqual(
                            parse_json(result=finish)["error"],
                            "PASS 产生越权路径",
                        )

    def test_full_sequence_completes_submit_with_body_binding(self) -> None:
        """真实 sync 完成 seal 失败、修复、提交和无真实 gh 的全序列。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            upstream = root / "upstream"
            target = root / "target"
            fake_bin = root / "bin"
            sha = create_upstream(repo_root=upstream, fake_sync=False)
            initialize_specialized_target(target=target)
            complete_real_prepare_and_passes(
                target=target,
                upstream=upstream,
                upstream_sha=sha,
            )
            prepared = run_harness(
                command="prepare-submit",
                target=target,
                upstream=upstream,
                upstream_sha=sha,
            )
            self.assertEqual(prepared.returncode, 0, msg=prepared.stdout)
            run_path = target / ".coding_workflow/skill_runtime/run.json"
            before = json.loads(run_path.read_text(encoding="utf-8"))
            self.assertEqual(before["active_mode"], "SUBMIT")
            self.assertFalse(before["submit_ready"])
            failed = run_harness(
                command="seal-submit",
                target=target,
                upstream=upstream,
                upstream_sha=sha,
            )
            self.assertNotEqual(failed.returncode, 0)
            self.assertEqual(
                parse_json(result=failed)["error"],
                "pinned final gate 失败",
            )
            after = json.loads(run_path.read_text(encoding="utf-8"))
            self.assertEqual(after["run_id"], before["run_id"])
            self.assertEqual(after["active_mode"], "SUBMIT")
            self.assertFalse(after["submit_ready"])
            self.assertTrue(
                (
                    target
                    / ".coding_workflow/skill_runtime/baselines/SUBMIT.json"
                ).is_file()
            )
            replace_section(
                path=target / "PR_BODY.md",
                section_name="pr_test_evidence",
                text=(
                    "## PR Test Evidence\n\n"
                    "- commands: python -m pytest -q\n"
                    "- result: passed\n"
                    "- not run / N/A: none"
                ),
            )
            sealed = run_harness(
                command="seal-submit",
                target=target,
                upstream=upstream,
                upstream_sha=sha,
            )
            self.assertEqual(sealed.returncode, 0, msg=sealed.stdout)
            allowed = parse_json(result=sealed)["allowed_commit_paths"]
            commit_paths(
                repo_root=target,
                paths=allowed,
                message="workflow docs",
            )
            head_sha = git_head(repo_root=target)
            body = (target / "PR_BODY.md").read_text(encoding="utf-8")
            env = fake_gh_env(
                bin_dir=fake_bin,
                payload=pull_request_payload(
                    head_sha=head_sha,
                    body=body.rstrip("\n") + "\r\n",
                ),
                no_real_gh=True,
            )
            finish = run_harness(
                command="finish-submit",
                target=target,
                upstream=upstream,
                upstream_sha=sha,
                pr_number=12,
                base="main",
                head="workflow-docs",
                env=env,
            )
            self.assertEqual(finish.returncode, 0, msg=finish.stdout)
            state = json.loads(
                (
                    target / ".coding_workflow/skill_runtime/run.json"
                ).read_text(encoding="utf-8")
            )
            self.assertEqual(state["completed_modes"], list(MODES))
            repeated = run_harness(
                command="start-pass",
                target=target,
                upstream=upstream,
                upstream_sha=sha,
                mode="PASS_1",
            )
            self.assertNotEqual(repeated.returncode, 0)
            self.assertEqual(
                parse_json(result=repeated)["error"],
                "workflow 已完成",
            )

    def test_failed_gate_restart_uses_local_start_head(self) -> None:
        """未发布分支也能保留旧 runtime 并从 start_head 整轮重启。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            upstream = root / "upstream"
            target = root / "target"
            restart = root / "restart"
            publish = root / "publish.git"
            fake_bin = root / "bin"
            sha = create_upstream(repo_root=upstream, fake_sync=False)
            initialize_specialized_target(target=target)
            bare = run_command(
                args=["git", "init", "-q", "--bare", str(publish)],
                cwd=root,
            )
            self.assertEqual(bare.returncode, 0, msg=bare.stderr)
            add_origin = git(
                repo_root=target,
                args=["remote", "add", "origin", str(publish)],
            )
            self.assertEqual(add_origin.returncode, 0, msg=add_origin.stderr)
            remote_head = git(
                repo_root=target,
                args=["ls-remote", "--heads", "origin", "workflow-docs"],
            )
            self.assertEqual(remote_head.stdout, "")
            complete_real_prepare_and_passes(
                target=target,
                upstream=upstream,
                upstream_sha=sha,
            )
            prepared = run_harness(
                command="prepare-submit",
                target=target,
                upstream=upstream,
                upstream_sha=sha,
            )
            self.assertEqual(prepared.returncode, 0, msg=prepared.stdout)
            failed = run_harness(
                command="seal-submit",
                target=target,
                upstream=upstream,
                upstream_sha=sha,
            )
            self.assertNotEqual(failed.returncode, 0)
            old_run_path = (
                target / ".coding_workflow/skill_runtime/run.json"
            )
            old_state = json.loads(old_run_path.read_text(encoding="utf-8"))
            clone = run_command(
                args=[
                    "git", "clone", "--no-local", "--no-checkout",
                    "--origin", "failed-source",
                    str(target), str(restart),
                ],
                cwd=root,
            )
            self.assertEqual(clone.returncode, 0, msg=clone.stderr)
            checkout = git(
                repo_root=restart,
                args=[
                    "switch", "-C", "workflow-docs",
                    old_state["project_head"],
                ],
            )
            self.assertEqual(checkout.returncode, 0, msg=checkout.stderr)
            restore_origin = git(
                repo_root=restart,
                args=["remote", "add", "origin", str(publish)],
            )
            self.assertEqual(
                restore_origin.returncode,
                0,
                msg=restore_origin.stderr,
            )
            self.assertEqual(
                git_head(repo_root=restart),
                old_state["project_head"],
            )
            complete_real_prepare_and_passes(
                target=restart,
                upstream=upstream,
                upstream_sha=sha,
            )
            allowed = prepare_and_seal_real_submit(
                target=restart,
                upstream=upstream,
                upstream_sha=sha,
            )
            commit_paths(
                repo_root=restart,
                paths=allowed,
                message="restarted workflow docs",
            )
            push = git(
                repo_root=restart,
                args=[
                    "push", "-q", "origin",
                    "HEAD:refs/heads/workflow-docs",
                ],
            )
            self.assertEqual(push.returncode, 0, msg=push.stderr)
            restarted_head = git_head(repo_root=restart)
            env = fake_gh_env(
                bin_dir=fake_bin,
                payload=pull_request_payload(
                    head_sha=restarted_head,
                    body=(restart / "PR_BODY.md").read_text(
                        encoding="utf-8"
                    ),
                ),
                no_real_gh=True,
            )
            finish = run_harness(
                command="finish-submit",
                target=restart,
                upstream=upstream,
                upstream_sha=sha,
                pr_number=12,
                base="main",
                head="workflow-docs",
                env=env,
            )
            self.assertEqual(finish.returncode, 0, msg=finish.stdout)
            preserved = json.loads(old_run_path.read_text(encoding="utf-8"))
            self.assertEqual(preserved["run_id"], old_state["run_id"])
            self.assertEqual(preserved["active_mode"], "SUBMIT")
            self.assertFalse(preserved["submit_ready"])

    def test_submit_rejects_extra_or_missing_committed_paths(self) -> None:
        """真实 final 后 committed set 必须精确等于 sealed allowed set。"""
        for scenario in ("extra", "missing"):
            with self.subTest(scenario=scenario):
                with tempfile.TemporaryDirectory() as temp_dir:
                    root = Path(temp_dir)
                    upstream = root / "upstream"
                    target = root / "target"
                    fake_bin = root / "bin"
                    sha = create_upstream(repo_root=upstream, fake_sync=False)
                    initialize_specialized_target(target=target)
                    complete_real_prepare_and_passes(
                        target=target,
                        upstream=upstream,
                        upstream_sha=sha,
                    )
                    allowed = prepare_and_seal_real_submit(
                        target=target,
                        upstream=upstream,
                        upstream_sha=sha,
                    )
                    if scenario == "extra":
                        append_text(
                            path=target / "seed.txt",
                            text="business\n",
                        )
                        commit_paths(
                            repo_root=target,
                            paths=[*allowed, "seed.txt"],
                            message="extra path",
                        )
                    else:
                        commit_paths(
                            repo_root=target,
                            paths=[allowed[0]],
                            message="partial docs",
                        )
                    head_sha = git_head(repo_root=target)
                    env = fake_gh_env(
                        bin_dir=fake_bin,
                        payload=pull_request_payload(
                            head_sha=head_sha,
                            body=(
                                target / "PR_BODY.md"
                            ).read_text(encoding="utf-8"),
                        ),
                    )
                    finish = run_harness(
                        command="finish-submit",
                        target=target,
                        upstream=upstream,
                        upstream_sha=sha,
                        pr_number=12,
                        base="main",
                        head="workflow-docs",
                        env=env,
                    )
                    self.assertNotEqual(finish.returncode, 0)
                    self.assertEqual(
                        parse_json(result=finish)["error"],
                        "SUBMIT committed scope 不匹配",
                    )

    def test_submit_rejects_multiple_commits(self) -> None:
        """sealed 路径即使精确，SUBMIT 也只能新增一个 commit。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            upstream = root / "upstream"
            target = root / "target"
            fake_bin = root / "bin"
            sha = create_upstream(repo_root=upstream, fake_sync=False)
            initialize_specialized_target(target=target)
            complete_real_prepare_and_passes(
                target=target,
                upstream=upstream,
                upstream_sha=sha,
            )
            allowed = prepare_and_seal_real_submit(
                target=target,
                upstream=upstream,
                upstream_sha=sha,
            )
            commit_paths(
                repo_root=target,
                paths=allowed[:-1],
                message="first docs commit",
            )
            commit_paths(
                repo_root=target,
                paths=allowed[-1:],
                message="second docs commit",
            )
            env = fake_gh_env(
                bin_dir=fake_bin,
                payload=pull_request_payload(
                    head_sha=git_head(repo_root=target),
                    body=(target / "PR_BODY.md").read_text(encoding="utf-8"),
                ),
            )
            finish = run_harness(
                command="finish-submit",
                target=target,
                upstream=upstream,
                upstream_sha=sha,
                pr_number=12,
                base="main",
                head="workflow-docs",
                env=env,
            )
            self.assertNotEqual(finish.returncode, 0)
            self.assertEqual(
                parse_json(result=finish)["error"],
                "SUBMIT commit 数不匹配",
            )

    def test_submit_rejects_stale_remote_body(self) -> None:
        """真实 seal 后远端 body 与 sealed body 不同必须失败。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            upstream = root / "upstream"
            target = root / "target"
            fake_bin = root / "bin"
            sha = create_upstream(repo_root=upstream, fake_sync=False)
            initialize_specialized_target(target=target)
            complete_real_prepare_and_passes(
                target=target,
                upstream=upstream,
                upstream_sha=sha,
            )
            allowed = prepare_and_seal_real_submit(
                target=target,
                upstream=upstream,
                upstream_sha=sha,
            )
            commit_paths(
                repo_root=target,
                paths=allowed,
                message="workflow docs",
            )
            env = fake_gh_env(
                bin_dir=fake_bin,
                payload=pull_request_payload(
                    head_sha=git_head(repo_root=target),
                    body="stale body",
                ),
            )
            finish = run_harness(
                command="finish-submit",
                target=target,
                upstream=upstream,
                upstream_sha=sha,
                pr_number=12,
                base="main",
                head="workflow-docs",
                env=env,
            )
            self.assertNotEqual(finish.returncode, 0)
            self.assertEqual(
                parse_json(result=finish)["error"],
                "远端 PR 与本地提交不匹配",
            )

    def test_finish_submit_rejects_post_seal_workflow_change(self) -> None:
        """seal 后即使提交路径集合正确，workflow 内容篡改仍失败。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            upstream = root / "upstream"
            target = root / "target"
            fake_bin = root / "bin"
            sha = create_upstream(repo_root=upstream, fake_sync=False)
            initialize_specialized_target(target=target)
            complete_real_prepare_and_passes(
                target=target,
                upstream=upstream,
                upstream_sha=sha,
            )
            allowed = prepare_and_seal_real_submit(
                target=target,
                upstream=upstream,
                upstream_sha=sha,
            )
            append_text(path=target / "AGENTS.md", text="\npost-seal tamper\n")
            commit_paths(
                repo_root=target,
                paths=allowed,
                message="tampered docs",
            )
            head_sha = git_head(repo_root=target)
            env = fake_gh_env(
                bin_dir=fake_bin,
                payload=pull_request_payload(
                    head_sha=head_sha,
                    body=(target / "PR_BODY.md").read_text(encoding="utf-8"),
                ),
            )
            finish = run_harness(
                command="finish-submit",
                target=target,
                upstream=upstream,
                upstream_sha=sha,
                pr_number=12,
                base="main",
                head="workflow-docs",
                env=env,
            )
            self.assertNotEqual(finish.returncode, 0)
            self.assertEqual(
                parse_json(result=finish)["error"],
                "sealed workflow 内容已变化",
            )

    def test_finish_submit_rejects_post_seal_file_mode_change(self) -> None:
        """seal 后 workflow executable bit 变化也必须失败。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            upstream = root / "upstream"
            target = root / "target"
            fake_bin = root / "bin"
            sha = create_upstream(repo_root=upstream, fake_sync=False)
            initialize_specialized_target(target=target)
            complete_real_prepare_and_passes(
                target=target,
                upstream=upstream,
                upstream_sha=sha,
            )
            allowed = prepare_and_seal_real_submit(
                target=target,
                upstream=upstream,
                upstream_sha=sha,
            )
            (target / "AGENTS.md").chmod(0o755)
            commit_paths(
                repo_root=target,
                paths=allowed,
                message="changed file mode",
            )
            env = fake_gh_env(
                bin_dir=fake_bin,
                payload=pull_request_payload(
                    head_sha=git_head(repo_root=target),
                    body=(target / "PR_BODY.md").read_text(encoding="utf-8"),
                ),
            )
            finish = run_harness(
                command="finish-submit",
                target=target,
                upstream=upstream,
                upstream_sha=sha,
                pr_number=12,
                base="main",
                head="workflow-docs",
                env=env,
            )
            self.assertNotEqual(finish.returncode, 0)
            self.assertEqual(
                parse_json(result=finish)["error"],
                "sealed workflow 内容已变化",
            )

    def test_status_and_result_schema_survive_restart(self) -> None:
        """新进程可读取 run.json，PREPARE result 字段保持精确。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            upstream = root / "upstream"
            target = root / "target"
            sha = create_upstream(repo_root=upstream, fake_sync=True)
            initialize_core_target(target=target, upstream=upstream)
            complete_prepare(
                target=target,
                upstream=upstream,
                upstream_sha=sha,
            )
            status = run_harness(command="status", target=target)
            self.assertEqual(status.returncode, 0)
            self.assertEqual(
                parse_json(result=status)["completed_modes"],
                ["PREPARE"],
            )
            result = json.loads(
                (
                    target / ".coding_workflow/skill_results/PREPARE.json"
                ).read_text(encoding="utf-8")
            )
            self.assertEqual(
                set(result),
                {
                    "schema_version",
                    "run_id",
                    "mode",
                    "status",
                    "upstream_sha",
                    "project_head",
                    "created_at_utc",
                    "changed_paths",
                    "details",
                    "error",
                },
            )

    def test_review_validator_derives_verdict_and_binds_real_pr(self) -> None:
        """review section 最高等级、PR number/head 和 target HEAD 必须一致。"""
        self.assertFalse((REVIEW_SKILL / ".source.json").exists())
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            upstream = root / "upstream"
            target = root / "target"
            fake_bin = root / "bin"
            sha = create_upstream(repo_root=upstream, fake_sync=True)
            initialize_repo(repo_root=target)
            (target / ".gitignore").write_text(
                ".coding_workflow/skill_results/\n",
                encoding="utf-8",
            )
            commit_all(repo_root=target, message="ignore review results")
            head_sha = git_head(repo_root=target)
            review_file = (
                target / ".coding_workflow/skill_results/review.json"
            )
            review_file.parent.mkdir(parents=True, exist_ok=True)
            review_file.write_text(
                json.dumps(
                    valid_review(
                        verdict="PASS",
                        head_sha=head_sha,
                        upstream_sha=sha,
                        blocker_section=True,
                    ),
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            env = fake_gh_env(
                bin_dir=fake_bin,
                payload=review_pr_payload(
                    head_sha=head_sha,
                    upstream_sha=sha,
                ),
                no_real_gh=True,
            )
            args = [
                sys.executable,
                str(VALIDATE_REVIEW),
                "--target-repo",
                str(target),
                "--upstream-dir",
                str(upstream),
                "--upstream-sha",
                sha,
                "--review-file",
                str(review_file),
                "--pr-number",
                "12",
            ]
            conflict = run_command(args=args, cwd=target, env=env)
            self.assertNotEqual(conflict.returncode, 0)
            review_file.write_text(
                json.dumps(
                    valid_review(
                        verdict="BLOCKER",
                        head_sha=head_sha,
                        upstream_sha=sha,
                        blocker_section=True,
                    ),
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            valid = run_command(args=args, cwd=target, env=env)
            self.assertEqual(valid.returncode, 0, msg=valid.stdout)
            artifact = target / "untracked-review-artifact.txt"
            artifact.write_text("unexpected\n", encoding="utf-8")
            dirty = run_command(args=args, cwd=target, env=env)
            self.assertNotEqual(dirty.returncode, 0)
            self.assertEqual(
                parse_json(result=dirty)["error"],
                "目标仓库工作区不干净",
            )
            artifact.unlink()
            wrong_sha_env = fake_gh_env(
                bin_dir=fake_bin,
                payload=review_pr_payload(
                    head_sha=head_sha,
                    upstream_sha="0" * 40,
                ),
                no_real_gh=True,
            )
            wrong_sha = run_command(
                args=args,
                cwd=target,
                env=wrong_sha_env,
            )
            self.assertNotEqual(wrong_sha.returncode, 0)
            self.assertEqual(
                parse_json(result=wrong_sha)["error"],
                "PR body upstream SHA 不匹配",
            )
            for duplicate_sha in (sha, "0" * 40):
                payload = review_pr_payload(
                    head_sha=head_sha,
                    upstream_sha=sha,
                )
                payload["body"] = payload["body"].replace(
                    "<!-- sync:auto:end -->",
                    f"- upstream_resolved_commit: {duplicate_sha}\n"
                    "<!-- sync:auto:end -->",
                )
                duplicate_env = fake_gh_env(
                    bin_dir=fake_bin,
                    payload=payload,
                    no_real_gh=True,
                )
                duplicate = run_command(
                    args=args,
                    cwd=target,
                    env=duplicate_env,
                )
                self.assertNotEqual(duplicate.returncode, 0)
                self.assertEqual(
                    parse_json(result=duplicate)["error"],
                    "PR body upstream SHA 不匹配",
                )

    def test_installer_user_repo_and_source_metadata(self) -> None:
        """哑安装器覆盖复制双平台，Claude 禁止隐式调用。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            upstream = root / "upstream"
            home = root / "home"
            target = root / "target"
            home.mkdir()
            sha = create_upstream(repo_root=upstream, fake_sync=True)
            initialize_repo(repo_root=target)
            user_env = os.environ.copy()
            user_env["HOME"] = str(home)
            user = run_command(
                args=[
                    sys.executable,
                    str(INSTALL_SKILLS),
                    "--upstream-dir",
                    str(upstream),
                    "--upstream-sha",
                    sha,
                ],
                cwd=REPO_ROOT,
                env=user_env,
            )
            self.assertEqual(user.returncode, 0, msg=user.stdout)
            source = json.loads(
                (
                    home
                    / ".agents/skills/workflow-docs-sync/.source.json"
                ).read_text(encoding="utf-8")
            )
            self.assertEqual(
                source,
                {
                    "upstream_sha": sha,
                    "canonical_relative_path": "zh/skills/workflow-docs-sync",
                    "platform": "codex",
                },
            )
            review_source = json.loads(
                (
                    home
                    / ".agents/skills/workflow-docs-sync-review/.source.json"
                ).read_text(encoding="utf-8")
            )
            self.assertEqual(
                review_source["canonical_relative_path"],
                "zh/skills/workflow-docs-sync-review",
            )
            claude_skill = (
                home / ".claude/skills/workflow-docs-sync/SKILL.md"
            ).read_text(encoding="utf-8")
            self.assertIn("disable-model-invocation: true", claude_skill)
            repo = run_command(
                args=[
                    sys.executable,
                    str(INSTALL_SKILLS),
                    "--scope",
                    "repo",
                    "--target-repo",
                    str(target),
                    "--upstream-dir",
                    str(upstream),
                    "--upstream-sha",
                    sha,
                ],
                cwd=REPO_ROOT,
            )
            self.assertEqual(repo.returncode, 0, msg=repo.stdout)
            for skill_name in SKILL_NAMES:
                self.assertTrue(
                    (
                        target
                        / f".agents/skills/{skill_name}/SKILL.md"
                    ).is_file()
                )

    def test_installed_skill_requires_reinstall_for_new_sha(self) -> None:
        """SHA A 安装副本用 SHA B 调用时必须给出重装错误。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            upstream = root / "upstream"
            home = root / "home"
            target = root / "target"
            home.mkdir()
            sha_a = create_upstream(repo_root=upstream, fake_sync=True)
            env = os.environ.copy()
            env["HOME"] = str(home)
            install = run_command(
                args=[
                    sys.executable,
                    str(INSTALL_SKILLS),
                    "--upstream-dir",
                    str(upstream),
                    "--upstream-sha",
                    sha_a,
                ],
                cwd=REPO_ROOT,
                env=env,
            )
            self.assertEqual(install.returncode, 0)
            append_text(
                path=upstream / "zh/scripts/OPERATIONS.md",
                text="\nnew SHA\n",
            )
            commit_all(repo_root=upstream, message="new upstream")
            sha_b = git_head(repo_root=upstream)
            initialize_core_target(target=target, upstream=upstream)
            installed_harness = (
                home
                / ".agents/skills/workflow-docs-sync/scripts/harness.py"
            )
            result = run_harness(
                command="prepare",
                target=target,
                upstream=upstream,
                upstream_sha=sha_b,
                harness_path=installed_harness,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(
                parse_json(result=result)["error"],
                "Skill 来源 SHA 不匹配",
            )
            installed_reviewer = (
                home
                / ".agents/skills/workflow-docs-sync-review"
                / "scripts/validate_review.py"
            )
            review = run_command(
                args=[
                    sys.executable,
                    str(installed_reviewer),
                    "--target-repo",
                    str(target),
                    "--upstream-dir",
                    str(upstream),
                    "--upstream-sha",
                    sha_b,
                    "--review-file",
                    ".coding_workflow/skill_results/review.json",
                    "--pr-number",
                    "12",
                ],
                cwd=target,
            )
            self.assertNotEqual(review.returncode, 0)
            self.assertEqual(
                parse_json(result=review)["error"],
                "reviewer Skill 来源 SHA 不匹配",
            )

    def test_invocation_metadata_and_ci(self) -> None:
        """Codex/Claude 必须显式调用，最小 CI 必须运行 pytest。"""
        for skill_dir in (EXEC_SKILL, REVIEW_SKILL):
            frontmatter = (
                skill_dir / "SKILL.md"
            ).read_text(encoding="utf-8").split("---", 2)[1]
            keys = {
                line.split(":", 1)[0].strip()
                for line in frontmatter.splitlines()
                if line.strip()
            }
            self.assertEqual(keys, {"name", "description"})
            openai = (
                skill_dir / "agents/openai.yaml"
            ).read_text(encoding="utf-8")
            self.assertIn("allow_implicit_invocation: false", openai)
        modes = (
            EXEC_SKILL / "references/modes.md"
        ).read_text(encoding="utf-8")
        self.assertIn("$workflow-docs-sync", modes)
        self.assertIn("/workflow-docs-sync", modes)
        self.assertIn(
            "<workflow-docs-sync-root>/scripts/harness.py",
            modes,
        )
        self.assertNotIn("python3 scripts/harness.py", modes)
        review_skill = REVIEW_SKILL.joinpath("SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "<workflow-docs-sync-review-root>/scripts/validate_review.py",
            review_skill,
        )
        operations = (REPO_ROOT / "zh/scripts/OPERATIONS.md").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "`PR_BODY.md` 默认只用于更新 GitHub PR body，不提交仓库",
            operations,
        )
        workflow = (
            REPO_ROOT / ".github/workflows/test.yml"
        ).read_text(encoding="utf-8")
        self.assertIn("actions/setup-python", workflow)
        self.assertIn("python -m pytest -q", workflow)

    def test_reviewer_handoff_preserves_finding_union(self) -> None:
        """长期流程必须保留来源 ID 并禁止 finding 静默消失。"""
        workflow = (
            REPO_ROOT / "zh/docs/development_workflow/README.md"
        ).read_text(encoding="utf-8")
        for disposition in (
            "confirmed",
            "rejected",
            "merged_as_duplicate:<ID>",
            "downgraded:<新严重度>",
            "needs_human",
        ):
            self.assertIn(disposition, workflow)
        self.assertIn("静默消失", workflow)


if __name__ == "__main__":
    unittest.main()
