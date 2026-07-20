"""Regression tests for workflow-docs sync behavior.

Call flow:
    python -m unittest discover -s tests
      -> SyncWorkflowTests creates a temporary target git repository
      -> scripts/sync.sh runs against this checkout as the upstream template
      -> assertions verify final-gate and PR body refresh contracts
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SYNC_SH = REPO_ROOT / "scripts" / "sync.sh"


def load_sync_module() -> object:
    """Load the sync script under test without executing its CLI.

    Parameters:
        None.

    Expected output:
        Imported module object exposing the same constants used by sync.
    """
    module_path = REPO_ROOT / "scripts" / "sync_coding_workflow.py"
    previous_language = (
        os.environ["CODING_WORKFLOW_LANGUAGE"]
        if "CODING_WORKFLOW_LANGUAGE" in os.environ
        else None
    )
    if "CODING_WORKFLOW_LANGUAGE" in os.environ:
        del os.environ["CODING_WORKFLOW_LANGUAGE"]
    spec = importlib.util.spec_from_file_location(
        "sync_coding_workflow_under_test",
        module_path,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import sync script: {module_path}")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    finally:
        if previous_language is not None:
            os.environ["CODING_WORKFLOW_LANGUAGE"] = previous_language
    return module


SYNC_MODULE = load_sync_module()
CORE_FILES = tuple(SYNC_MODULE.CORE_FILES)


def run_command(
    args: list[str],
    cwd: Path,
    env: dict[str, str],
    check: bool,
) -> subprocess.CompletedProcess[str]:
    """Run one command with UTF-8 capture for diagnosis.

    Parameters:
        args: Executable and split arguments.
        cwd: Working directory.
        env: Environment variables for the child process.
        check: Whether a non-zero return code should fail the test helper.

    Expected output:
        CompletedProcess with stdout, stderr, and return code. When `check` is
        true, failures raise AssertionError with captured output.
    """
    result = subprocess.run(
        args=args,
        cwd=cwd,
        env=env,
        check=False,
        capture_output=True,
        encoding="utf-8",
        text=True,
    )
    if check and result.returncode != 0:
        raise AssertionError(
            f"command failed: {args}\nSTDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}"
        )
    return result


def sync_env(upstream_dir: Path) -> dict[str, str]:
    """Return an environment that uses the checkout as upstream.

    Parameters:
        upstream_dir: Upstream coding-workflow checkout to exercise.

    Expected output:
        Environment dictionary. The override keeps tests offline and ensures
        they exercise the script version under review.
    """
    env = os.environ.copy()
    env["CODING_WORKFLOW_UPSTREAM_DIR"] = str(upstream_dir)
    return env


def write_core_files(repo_root: Path, omitted_paths: set[str]) -> None:
    """Write project-specific core files into a temporary target repo.

    Parameters:
        repo_root: Temporary target repository root.
        omitted_paths: Repository-relative core files to leave missing.

    Expected output:
        All non-omitted core files exist with marker-free project text.
    """
    for rel_path in CORE_FILES:
        if rel_path in omitted_paths:
            continue
        path = repo_root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"project specific content for {rel_path}\n",
            encoding="utf-8",
        )


def commit_initial_repo(repo_root: Path) -> None:
    """Create the first git commit for a temporary target repo.

    Parameters:
        repo_root: Temporary target repository root.

    Expected output:
        A clean git repository with one commit, so sync can resolve HEAD.
    """
    env = os.environ.copy()
    run_command(args=["git", "init", "-q"], cwd=repo_root, env=env, check=True)
    run_command(
        args=["git", "config", "user.email", "review@example.com"],
        cwd=repo_root,
        env=env,
        check=True,
    )
    run_command(
        args=["git", "config", "user.name", "review"],
        cwd=repo_root,
        env=env,
        check=True,
    )
    run_command(args=["git", "add", "."], cwd=repo_root, env=env, check=True)
    run_command(
        args=["git", "commit", "-q", "-m", "init"],
        cwd=repo_root,
        env=env,
        check=True,
    )


def create_target_repo(repo_root: Path, omitted_paths: set[str]) -> None:
    """Create a temporary target repo ready for sync.

    Parameters:
        repo_root: Temporary target repository root.
        omitted_paths: Core files intentionally absent before sync.

    Expected output:
        A committed repo whose files are safe for sync to inspect.
    """
    write_core_files(repo_root=repo_root, omitted_paths=omitted_paths)
    commit_initial_repo(repo_root=repo_root)


def run_sync(repo_root: Path, check: bool) -> subprocess.CompletedProcess[str]:
    """Run the public sync launcher against the checkout under test.

    Parameters:
        repo_root: Temporary target repository root.
        check: Whether a non-zero result should fail immediately.

    Expected output:
        Completed sync process using this repository as the upstream template.
    """
    return run_command(
        args=["bash", str(SYNC_SH)],
        cwd=repo_root,
        env=sync_env(upstream_dir=REPO_ROOT),
        check=check,
    )


def create_sync_pr_body(repo_root: Path) -> Path:
    """Run ordinary sync and create a sentinel PR body for final-gate tests.

    Parameters:
        repo_root: Temporary target repository root.

    Expected output:
        Path to `PR_BODY.md` created from the current sync skeleton.
    """
    run_sync(repo_root=repo_root, check=True)
    run_command(
        args=[
            "python3",
            str(REPO_ROOT / "scripts" / "sync_coding_workflow.py"),
            "--update-pr-body",
            "PR_BODY.md",
        ],
        cwd=repo_root,
        env=sync_env(upstream_dir=REPO_ROOT),
        check=True,
    )
    return repo_root / "PR_BODY.md"


def create_upstream_without_prompt(
    upstream_root: Path,
    missing_prompt_path: str,
) -> None:
    """Create an upstream checkout whose HEAD lacks one prompt file.

    Parameters:
        upstream_root: Destination directory for a committed upstream copy.
        missing_prompt_path: Repository-relative prompt file to delete.

    Expected output:
        A git worktree using the current source under review, with HEAD missing
        the selected prompt so sync must reject its raw URL.
    """
    shutil.copytree(
        src=REPO_ROOT,
        dst=upstream_root,
        ignore=shutil.ignore_patterns(
            ".git",
            ".coding_workflow",
            "__pycache__",
            "*.pyc",
        ),
    )
    commit_initial_repo(repo_root=upstream_root)
    (upstream_root / missing_prompt_path).unlink()
    env = os.environ.copy()
    run_command(
        args=["git", "add", "-A"],
        cwd=upstream_root,
        env=env,
        check=True,
    )
    run_command(
        args=["git", "commit", "-q", "-m", "remove prompt"],
        cwd=upstream_root,
        env=env,
        check=True,
    )


def create_committed_upstream_copy(upstream_root: Path) -> None:
    """Create an upstream copy whose HEAD includes uncommitted test fixtures.

    Parameters:
        upstream_root: Destination directory for a committed upstream copy.

    Expected output:
        A git worktree containing the current checkout files, including new
        English templates added by the patch under test.
    """
    shutil.copytree(
        src=REPO_ROOT,
        dst=upstream_root,
        ignore=shutil.ignore_patterns(
            ".git",
            ".coding_workflow",
            "__pycache__",
            "*.pyc",
        ),
    )
    commit_initial_repo(repo_root=upstream_root)


def fill_agent_placeholders(pr_body_path: Path) -> None:
    """Replace script placeholders with review-safe test content.

    Parameters:
        pr_body_path: PR body file generated by sync.

    Expected output:
        Agent-owned sections no longer contain final-gate placeholder words.
    """
    text = pr_body_path.read_text(encoding="utf-8")
    if "待补充" not in text:
        raise AssertionError("expected script placeholders before filling")
    for section_name in SYNC_MODULE.AGENT_SECTIONS:
        start = SYNC_MODULE.agent_section_start(section_name=section_name)
        end = SYNC_MODULE.agent_section_end(section_name=section_name)
        start_index, end_index = SYNC_MODULE.sentinel_span(
            text=text,
            start=start,
            end=end,
        )
        section = text[start_index:end_index]
        text = (
            text[:start_index]
            + section.replace("待补充", "已填写")
            + text[end_index:]
        )
    pr_body_path.write_text(text, encoding="utf-8")


def extract_review_contract(pr_body_text: str) -> str:
    """Extract the compact review contract from a generated PR body.

    Parameters:
        pr_body_text: Full PR body skeleton or draft.

    Expected output:
        Markdown for `Sync Review Contract`. Missing boundaries fail the test
        because reviewers must not infer contract values from any prompt.
    """
    start = "## Sync Review Contract"
    end = "## Upstream Templates at Sync Time"
    if start not in pr_body_text:
        raise AssertionError("missing Sync Review Contract section")
    if end not in pr_body_text:
        raise AssertionError("missing upstream template section after contract")
    start_index = pr_body_text.index(start)
    end_index = pr_body_text.index(end)
    if end_index <= start_index:
        raise AssertionError("Sync Review Contract appears out of order")
    return pr_body_text[start_index:end_index]


def sample_sync_state() -> dict[str, object]:
    """Build a minimal state for render-only PR body tests.

    Parameters:
        None.

    Expected output:
        State dictionary with all core and prompt records needed by
        `render_pr_body_skeleton`. URLs are inert because the test only verifies
        local rendering from constants.
    """
    core_records = []
    for rel_path in CORE_FILES:
        core_records.append({
            "path": rel_path,
            "sync_pass_id": SYNC_MODULE.sync_pass_id_for_file(
                rel_path=rel_path,
            ),
            "status": "specialized",
            "note": "ok",
            "upstream_raw_url": f"https://example.invalid/{rel_path}",
        })
    prompt_records = [
        {
            "path": rel_path,
            "upstream_raw_url": f"https://example.invalid/{rel_path}",
        }
        for rel_path in SYNC_MODULE.SYNC_PROMPT_FILES
    ]
    return SYNC_MODULE.build_sync_state(
        upstream_sha="a" * 40,
        project_sha="b" * 40,
        dirty_core_files=[],
        core_records=core_records,
        sync_prompt_records=prompt_records,
    )


class SyncWorkflowTests(unittest.TestCase):
    """Behavioral regressions for sync shell and PR body helpers."""

    def test_pr_body_skeleton_renders_sync_constants(self) -> None:
        """Generated skeleton should own PR body structure literals."""
        state = sample_sync_state()
        skeleton = SYNC_MODULE.render_pr_body_skeleton(
            state=state,
        )
        expected_literals = [
            SYNC_MODULE.SYNC_PR_BODY_MARKER,
            SYNC_MODULE.SYNC_AUTO_START,
            SYNC_MODULE.SYNC_AUTO_END,
            "| " + " | ".join(SYNC_MODULE.FULL_RECONCILE_COLUMNS) + " |",
            "## PR Test Evidence",
            "## Upstream Drift Log",
            "## Agent Execution Evidence",
        ]
        for section_name in SYNC_MODULE.AGENT_SECTIONS:
            expected_literals.extend((
                SYNC_MODULE.agent_section_start(section_name=section_name),
                SYNC_MODULE.agent_section_end(section_name=section_name),
            ))
        expected_literals.extend(SYNC_MODULE.REPO_FACTS_HEADINGS)
        for sync_pass in SYNC_MODULE.SYNC_PASSES:
            expected_literals.append(str(sync_pass["title"]))

        for literal in expected_literals:
            self.assertIn(
                literal,
                skeleton,
                msg=f"PR body skeleton missing sync literal: {literal}",
            )
        self.assertNotIn(
            "待补充 | 待补充 | none | 待补充 | 待判断",
            skeleton,
        )
        for record in state["core_files"]:
            pass_title = SYNC_MODULE.sync_pass_title_for_id(
                pass_id=str(record["sync_pass_id"]),
            )
            expected_row = (
                f"| {pass_title} | `{record['path']}` | "
                f"`{record['status']}` | "
                "待补充 | 待补充 | 待补充 | 待补充 | 待补充 |"
            )
            self.assertIn(expected_row, skeleton)

    def test_each_pass_prompt_contains_common_execution_rules(self) -> None:
        """Every copyable pass prompt should carry its own guardrails."""
        operations_text = (
            REPO_ROOT / "zh/scripts/OPERATIONS.md"
        ).read_text(encoding="utf-8")
        self.assertNotIn("### 2.0 共用执行契约", operations_text)
        self.assertNotIn("ready_for_next_pass", operations_text)
        self.assertNotIn("Sync Pass Status", operations_text)
        self.assertNotIn("pass_handoffs", operations_text)
        self.assertNotIn(
            "PASS 4 回报普通 sync 已重跑、全部 pass ready",
            operations_text,
        )
        self.assertNotIn("整体任务：更新本地代码", operations_text)
        self.assertIn(
            "每次新开对话，只复制并执行对应 PASS 的 code block",
            operations_text,
        )
        self.assertIn(
            "不以\nPASS 4 的聊天摘要作为事实源",
            operations_text,
        )
        self.assertNotIn("第一步打开", operations_text)
        self.assertIn(
            "用户只需要从 PASS 1 开始复制对应 PASS 的 code block 到新对话",
            operations_text,
        )
        self.assertIn(
            "给执行 agent 的本轮工单和机器信号",
            operations_text,
        )
        self.assertIn(
            "用户不阅读也不影响启动下一步",
            operations_text,
        )
        self.assertIn("执行 agent 会按 prompt 读取它", operations_text)
        reconcile_agent_columns = [
            column
            for column in SYNC_MODULE.FULL_RECONCILE_COLUMNS
            if column not in {"pass", "文件", "当前脚本信号"}
        ]
        common_literals = [
            "整体目标：完成本轮 workflow docs sync",
            "owned docs，并把结论写入 `PR_BODY.md` 的 agent-owned 区",
            "当前任务：只执行",
            "不要执行其他 PASS",
            "共用执行规则",
            ".coding_workflow/diffs/agent_workorder.md",
            ".coding_workflow/diffs/pr_body_skeleton.md",
            "PR_BODY.md",
            "应由 PREPARE 机械创建",
            "不得自行复制 skeleton",
            "表格 cell 中的字面 `|` 必须写为 `\\|`",
            SYNC_MODULE.SYNC_AUTO_START,
            SYNC_MODULE.SYNC_AUTO_END,
            "任何 sync sentinel、sentinel 外内容",
            "agent-owned 内容不能保留 `待补充`",
            "`pr_test_evidence` 区只由 PR 提交 Agent 填写",
            "`agent_execution_evidence` 是执行自报清单",
            "`待判断` 留给 reviewer 和用户",
            "文档语义对账表",
            "没有拒绝项或下游影响时写",
            "evidence 列必须显式覆盖三类漂移",
            "class-1 template/missing",
            "class-2 upstream",
            "class-3 code/test/behavior drift",
            "不得字面引用上游模板 marker",
            "本 pass owned docs 的漂移触发器",
            "本 pass owned docs 的闭合规则",
            (
                "curl -fsSL https://raw.githubusercontent.com/"
                "wlvh/coding-workflow/main/zh/scripts/sync.sh | bash"
            ),
            "不要手修 auto 区",
            "人工 code-block 模式",
            "Skill 模式",
            "不要执行本 block 末尾的 curl",
            "pinned `finish-pass`",
        ]
        common_literals.extend(str(column) for column in reconcile_agent_columns)
        sync_passes = list(SYNC_MODULE.SYNC_PASSES)
        for index, sync_pass in enumerate(sync_passes, start=1):
            title = str(sync_pass["title"])
            start = f"### 2.{index} {title}"
            if index < len(sync_passes):
                next_title = str(sync_passes[index]["title"])
                end = f"### 2.{index + 1} {next_title}"
            else:
                end = "---\n\n## 3. PR 提交 Agent"
            self.assertIn(start, operations_text)
            self.assertIn(end, operations_text)
            pass_text = operations_text.split(start, maxsplit=1)[1].split(
                end,
                maxsplit=1,
            )[0]
            self.assertNotIn("本文档", pass_text)
            self.assertEqual(
                pass_text.count("应由 PREPARE 机械创建"),
                1,
                msg=f"{title} prompt should bind PR_BODY to PREPARE once",
            )
            self.assertNotIn("如果不存在，先用", pass_text)
            self.assertNotIn("回报修改了哪些文件", pass_text)
            self.assertNotIn("回报是否写入 downstream impact", pass_text)
            self.assertNotIn("PR body sections", pass_text)
            self.assertNotIn("是否全部 pass ready", pass_text)
            self.assertNotIn("读取收口", pass_text)
            self.assertNotIn("停止条件", pass_text)
            pass_specific_literals = []
            if title != "PASS 4 - Governance / Reverse Closure":
                self.assertNotIn("remaining_human_decisions", pass_text)
            if title == "PASS 1 - Code Facts / Architecture":
                pass_specific_literals.extend((
                    "系统目的、模块表、数据流",
                    "upstream architecture 新增或调整架构章节",
                    "代码新增入口、模块、数据流、状态模型",
                    "架构事实写回 `architecture.md`",
                    "能力、用户行为、测试或治理影响只写 downstream impact",
                    "本 pass 负责的 `Full Document Reconcile` 行",
                ))
            if title == "PASS 2 - Capability / User Behavior":
                pass_specific_literals.extend((
                    "`sample_*` anchor",
                    "代码或测试显示新增能力、拒绝、必须追问",
                    "`capability_contract.json`：class-1/2/3 修成真实能力边界和 stable anchor",
                    "用户可观察行为、不变量或验收口径",
                    "新增声明必须锚到 contract 或测试证据",
                    "怎么问、怎么看、何时找人",
                    "只解释 contract / interact 已确认且业务可感知的能力",
                    "本 pass 三个 owned docs 行",
                ))
            if title == "PASS 3 - TESTING Independent Review":
                pass_specific_literals.extend((
                    "`TESTING.md`：class-1/2 更新测试原则、证据记录和 gate",
                    "class-3 只写 `TESTING_REVIEW_PACKET`",
                    "机械信号收集",
                    "find tests -type f -name 'test_*.py'",
                    "grep -rh",
                    "git log --since='3 months ago'",
                    "按项目等价工具改写并在 evidence 写明实际命令",
                    "本 pass 只写 review packet，不改测试代码",
                    "只打开机械信号",
                    "不通读全文",
                ))
            if title == "PASS 4 - Governance / Reverse Closure":
                pass_specific_literals.extend((
                    "downstream impact 列必须逐 pass 显式列出",
                    "PASS 1 找到 N 条 class-3 漂移",
                    "PASS 2 ... 闭合于 capability_contract.json",
                    "PASS 3 ... 闭合于 TESTING_REVIEW_PACKET",
                    "需要提交期强制执行的事项收进 checklist",
                    "只为项目固定流程新增或更新流程入口",
                    "需要新的项目代码事实时写 downstream impact",
                    "缺失或 upstream 更新默认 inherit / adopt",
                    "唯一允许直接继承 upstream",
                    "不默认通读前置 pass 全文",
                ))
            expected_literals = [*common_literals]
            expected_literals.extend(pass_specific_literals)
            expected_literals.extend(
                f"`{rel_path}`" for rel_path in sync_pass["files"]
            )
            for literal in expected_literals:
                self.assertIn(
                    literal,
                    pass_text,
                    msg=f"{title} prompt missing self-contained rule: {literal}",
                )
        submit_text = operations_text.split(
            "## 3. PR 提交 Agent",
            maxsplit=1,
        )[1].split("---\n\n## 4. Sync PR Review", maxsplit=1)[0]
        submit_literals = [
            "当前任务：只执行 PR 提交 Agent",
            "`PR_Checklist.md`",
            "`TESTING.md`",
            "`.github/pull_request_template.md`",
            "`.coding_workflow/diffs/sync_state.json`",
            "`PR_BODY.md` 的 `Full Document Reconcile` 表",
            "`<!-- sync:agent:start full_document_reconcile -->` 到",
            "`PR_BODY.md` 的 `PR Test Evidence` 段",
            "`PR_BODY.md` 的 `Upstream Drift Log` 段",
            "`PR_BODY.md` 的 `Agent Execution Evidence` 表",
            "`PR_BODY.md` 的 `Remaining Human Decisions` 段",
            "`<!-- sync:agent:start remaining_human_decisions -->` 到",
            "`git branch --show-current`",
            "`git status --short`",
            "`git diff --name-only <base>...HEAD`",
            "PR body 中列了但 diff",
            "`PR_BODY.md` 的 `Full Document Reconcile` 表覆盖本轮核心文档",
            "`Agent Execution Evidence` 四个 PASS 行都已填写",
            "`Upstream Drift Log`",
            "`PR Test Evidence` 区",
            "不得把本 PR 一次性测试证据写入 `Repo Facts Map`",
            "`PR_BODY.md` 默认只用于更新 GitHub PR body，不提交仓库",
            "不得提交 `.coding_workflow/diffs/`",
            "`gh pr list --state open --head <branch>`",
            "`git commit --amend --no-edit`",
            "`git push --force-with-lease origin HEAD:<branch>`",
            "`gh pr edit <number> --body-file PR_BODY.md`",
            "`gh pr create --draft --title <title> --body-file PR_BODY.md --base <base> --head <branch>`",
            "禁止使用裸 `git push --force`",
            "不要手修 PR body auto 区",
            "`PR Test Evidence` 是否已记录测试命令、结果和 N/A 原因",
            "`Upstream Drift Log` 是否为 `none`",
            "`PR_BODY.md` 是已提交，还是仅用于更新 GitHub PR body",
            "`Remaining Human Decisions` 是否为 `none`",
        ]
        for literal in submit_literals:
            self.assertIn(
                literal,
                submit_text,
                msg=f"PR submit prompt missing execution detail: {literal}",
            )

    def test_final_mode_rejects_stale_auto_without_refresh(self) -> None:
        """`--final` must not repair stale auto content before checking it."""
        with tempfile.TemporaryDirectory() as temp_dir:
            target_root = Path(temp_dir)
            create_target_repo(repo_root=target_root, omitted_paths=set())
            pr_body_path = create_sync_pr_body(repo_root=target_root)
            fill_agent_placeholders(pr_body_path=pr_body_path)
            pr_body_text = pr_body_path.read_text(encoding="utf-8")
            stale_pr_body = pr_body_text.replace(
                "Final gate owns sentinels",
                "Stale gate owns sentinels",
            )
            pr_body_path.write_text(
                stale_pr_body,
                encoding="utf-8",
            )

            result = run_command(
                args=["bash", str(SYNC_SH), "--final"],
                cwd=target_root,
                env=sync_env(upstream_dir=REPO_ROOT),
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "sync auto section differs",
                f"{result.stdout}\n{result.stderr}",
            )
            self.assertIn(
                "Stale gate",
                pr_body_path.read_text(encoding="utf-8"),
            )

    def test_installed_template_reports_upstream_marker_hits(self) -> None:
        """Installed templates should report markers agents must remove."""
        with tempfile.TemporaryDirectory() as temp_dir:
            target_root = Path(temp_dir)
            create_target_repo(
                repo_root=target_root,
                omitted_paths={"docs/business_user_guide.md"},
            )

            run_sync(repo_root=target_root, check=True)

            state_path = target_root / ".coding_workflow/diffs/sync_state.json"
            state = json.loads(state_path.read_text(encoding="utf-8"))
            records = [
                record
                for record in state["core_files"]
                if record["path"] == "docs/business_user_guide.md"
            ]

            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]["status"], "installed_template")
            self.assertTrue(records[0]["marker_hits"])
            self.assertIn("<项目名>", "\n".join(records[0]["marker_hits"]))

    def test_refresh_rejects_content_outside_sync_sentinels(self) -> None:
        """Refresh must fail before dropping content outside sentinel blocks."""
        with tempfile.TemporaryDirectory() as temp_dir:
            target_root = Path(temp_dir)
            create_target_repo(repo_root=target_root, omitted_paths=set())
            pr_body_path = create_sync_pr_body(repo_root=target_root)
            fill_agent_placeholders(pr_body_path=pr_body_path)
            with pr_body_path.open(mode="a", encoding="utf-8") as pr_body:
                pr_body.write("\n## 验证\noutside sentinel\n")

            result = run_command(
                args=["bash", str(SYNC_SH)],
                cwd=target_root,
                env=sync_env(upstream_dir=REPO_ROOT),
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "content outside sync sentinel sections",
                f"{result.stdout}\n{result.stderr}",
            )
            self.assertIn(
                "outside sentinel",
                pr_body_path.read_text(encoding="utf-8"),
            )

    def test_refresh_rejects_non_sync_pr_body(self) -> None:
        """Ordinary sync should fail fast instead of migrating old drafts."""
        with tempfile.TemporaryDirectory() as temp_dir:
            target_root = Path(temp_dir)
            create_target_repo(repo_root=target_root, omitted_paths=set())
            (target_root / "PR_BODY.md").write_text(
                "ordinary draft\n",
                encoding="utf-8",
            )

            result = run_command(
                args=["bash", str(SYNC_SH)],
                cwd=target_root,
                env=sync_env(upstream_dir=REPO_ROOT),
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "exists but is not a sync PR body",
                f"{result.stdout}\n{result.stderr}",
            )
            self.assertEqual(
                "ordinary draft\n",
                (target_root / "PR_BODY.md").read_text(encoding="utf-8"),
            )

    def test_final_mode_passes_with_current_complete_pr_body(self) -> None:
        """`--final` should pass when auto and agent sections are complete."""
        with tempfile.TemporaryDirectory() as temp_dir:
            target_root = Path(temp_dir)
            create_target_repo(repo_root=target_root, omitted_paths=set())
            pr_body_path = create_sync_pr_body(repo_root=target_root)
            fill_agent_placeholders(pr_body_path=pr_body_path)

            result = run_command(
                args=["bash", str(SYNC_SH), "--final"],
                cwd=target_root,
                env=sync_env(upstream_dir=REPO_ROOT),
                check=True,
            )

            self.assertIn("Final sync check passed", result.stdout)

    def test_final_mode_rejects_unfilled_placeholder(self) -> None:
        """Final gate should reject agent-owned script placeholders."""
        with tempfile.TemporaryDirectory() as temp_dir:
            target_root = Path(temp_dir)
            create_target_repo(repo_root=target_root, omitted_paths=set())
            pr_body_path = create_sync_pr_body(repo_root=target_root)
            fill_agent_placeholders(pr_body_path=pr_body_path)
            pr_body_path.write_text(
                pr_body_path.read_text(encoding="utf-8").replace(
                    "已填写",
                    "待补充",
                    1,
                ),
                encoding="utf-8",
            )

            result = run_command(
                args=["bash", str(SYNC_SH), "--final"],
                cwd=target_root,
                env=sync_env(upstream_dir=REPO_ROOT),
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "still contains placeholder: 待补充",
                f"{result.stdout}\n{result.stderr}",
            )

    def test_final_mode_allows_visible_semantic_pending_decisions(self) -> None:
        """Final gate should leave semantic uncertainty to independent review."""
        with tempfile.TemporaryDirectory() as temp_dir:
            target_root = Path(temp_dir)
            create_target_repo(repo_root=target_root, omitted_paths=set())
            pr_body_path = create_sync_pr_body(repo_root=target_root)
            fill_agent_placeholders(pr_body_path=pr_body_path)
            pr_body_path.write_text(
                pr_body_path.read_text(encoding="utf-8").replace(
                    "已填写",
                    "待判断",
                    1,
                ),
                encoding="utf-8",
            )

            result = run_command(
                args=["bash", str(SYNC_SH), "--final"],
                cwd=target_root,
                env=sync_env(upstream_dir=REPO_ROOT),
                check=True,
            )

            self.assertIn("Final sync check passed", result.stdout)
            self.assertIn("待判断", pr_body_path.read_text(encoding="utf-8"))

    def test_generated_workorder_stays_thin_and_points_to_runbook(self) -> None:
        """Sync workorder should list machine facts, not duplicate prompts."""
        with tempfile.TemporaryDirectory() as temp_dir:
            target_root = Path(temp_dir)
            create_target_repo(repo_root=target_root, omitted_paths=set())

            result = run_sync(repo_root=target_root, check=True)
            output = f"{result.stdout}\n{result.stderr}"
            self.assertIn("sync OK: full_reconcile", output)
            self.assertIn("runbook:", output)
            self.assertIn("raw.githubusercontent.com", output)
            self.assertIn("agent workorder:", output)
            self.assertNotIn("Read these in order", output)
            self.assertNotIn("First action", output)
            self.assertNotIn("installation_status.md", output)
            self.assertNotIn("full_reconcile_report.md", output)

            workorder_path = (
                target_root
                / ".coding_workflow/diffs/agent_workorder.md"
            )
            workorder = workorder_path.read_text(encoding="utf-8")
            self.assertIn("zh/scripts/OPERATIONS.md", workorder)
            self.assertIn("## 文件处理清单", workorder)
            self.assertNotIn("## 入口", workorder)
            self.assertNotIn("## 角色边界", workorder)
            self.assertNotIn("## Sync Pass Plan", workorder)
            self.assertNotIn("## 本地读取优先级", workorder)
            self.assertNotIn("Sync Pass Status", workorder)
            self.assertIn("PASS 3 - TESTING Independent Review", workorder)
            workorder_lines = workorder.splitlines()
            file_header_index = workorder_lines.index(
                "| Pass | 文件 | 脚本信号 | 机械动作 | marker / TODO 命中 |"
            )
            self.assertTrue(
                workorder_lines[file_header_index + 2].startswith(
                    "| PASS 1 - Code Facts / Architecture | `architecture.md` |"
                ),
            )
            self.assertNotIn("## Copyable Pass Prompts", workorder)
            self.assertEqual(0, workorder.count("```text"))
            self.assertNotIn("tests_not_worth_adding", workorder)
            self.assertNotIn("propagation_targets", workorder)
            self.assertNotIn("kick_back_to", workorder)
            self.assertNotIn("AGENTS.md ## 文件简介", workorder)
            self.assertNotIn("Repo Facts Map", workorder)
            self.assertNotIn("upstream_vs_local", workorder)
            self.assertFalse(
                (target_root / ".coding_workflow/diffs/upstream_vs_local").exists()
            )
            self.assertFalse(
                (target_root / ".coding_workflow/diffs/installation_status.md").exists()
            )
            self.assertFalse(
                (target_root / ".coding_workflow/diffs/full_reconcile_report.md").exists()
            )

    def test_english_sync_uses_english_template_paths(self) -> None:
        """English launcher should sync the English path family."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            upstream_root = root / "upstream"
            target_root = root / "target"
            target_root.mkdir()
            create_committed_upstream_copy(upstream_root=upstream_root)
            omitted_paths = {
                "AGENTS.md",
                "TESTING.md",
                ".github/pull_request_template.md",
            }
            create_target_repo(
                repo_root=target_root,
                omitted_paths=omitted_paths,
            )

            result = run_command(
                args=["bash", str(upstream_root / "en/scripts/sync.sh")],
                cwd=target_root,
                env=sync_env(upstream_dir=upstream_root),
                check=True,
            )

            self.assertIn("en/scripts/OPERATIONS.md", result.stdout)
            self.assertTrue((target_root / "AGENTS.md").exists())
            self.assertTrue((target_root / "TESTING.md").exists())
            self.assertTrue(
                (target_root / ".github/pull_request_template.md").exists()
            )
            self.assertEqual(
                (upstream_root / "en/AGENTS.md").read_text(encoding="utf-8"),
                (target_root / "AGENTS.md").read_text(encoding="utf-8"),
            )
            state_path = (
                target_root / ".coding_workflow/diffs/sync_state.json"
            )
            state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual("en", state["workflow_language"])
            core_paths = [record["path"] for record in state["core_files"]]
            prompt_paths = [
                record["path"] for record in state["sync_prompt_files"]
            ]
            self.assertIn("AGENTS.md", core_paths)
            self.assertIn("capability_contract.json", core_paths)
            self.assertIn("en/scripts/OPERATIONS.md", prompt_paths)
            self.assertIn("en/scripts/sync_pr_review_system.md", prompt_paths)
            self.assertNotIn("en/AGENTS.md", core_paths)

    def test_language_core_files_pair_one_to_one(self) -> None:
        """Language source files should install to the same target paths."""
        self.assertEqual(
            len(SYNC_MODULE.ZH_CORE_SOURCE_FILES),
            len(SYNC_MODULE.EN_CORE_SOURCE_FILES),
        )
        for zh_path, en_path, zh_target, en_target in zip(
            SYNC_MODULE.ZH_CORE_SOURCE_FILES,
            SYNC_MODULE.EN_CORE_SOURCE_FILES,
            SYNC_MODULE.ZH_CORE_FILES,
            SYNC_MODULE.EN_CORE_FILES,
        ):
            self.assertTrue(zh_path.startswith("zh/"))
            self.assertTrue(en_path.startswith("en/"))
            self.assertEqual(zh_target, en_target)
            self.assertEqual(
                zh_target,
                SYNC_MODULE.strip_language_prefix(path=zh_path),
            )
            self.assertEqual(
                en_target,
                SYNC_MODULE.strip_language_prefix(path=en_path),
            )

    def test_language_prefix_strip_preserves_inner_github_path(self) -> None:
        """Only the leading language prefix is stripped from install paths."""
        self.assertEqual(
            ".github/pull_request_template.md",
            SYNC_MODULE.strip_language_prefix(
                path="zh/.github/pull_request_template.md",
            ),
        )
        self.assertEqual(
            ".github/pull_request_template.md",
            SYNC_MODULE.strip_language_prefix(
                path="en/.github/pull_request_template.md",
            ),
        )

    def test_final_mode_delegates_semantic_table_to_review(self) -> None:
        """Final gate should not deep-parse reviewer-owned evidence table."""
        with tempfile.TemporaryDirectory() as temp_dir:
            target_root = Path(temp_dir)
            create_target_repo(repo_root=target_root, omitted_paths=set())
            pr_body_path = create_sync_pr_body(repo_root=target_root)
            fill_agent_placeholders(pr_body_path=pr_body_path)
            text = pr_body_path.read_text(encoding="utf-8")
            text = text.replace(
                (
                    "| pass | 文件 | 当前脚本信号 | upstream semantic delta | "
                    "adopted where | not adopted because | evidence | "
                    "downstream impact |"
                ),
                "| reviewer owned malformed full reconcile table |",
                1,
            )
            pr_body_path.write_text(text, encoding="utf-8")

            result = run_command(
                args=["bash", str(SYNC_SH), "--final"],
                cwd=target_root,
                env=sync_env(upstream_dir=REPO_ROOT),
                check=True,
            )

            self.assertIn("Final sync check passed", result.stdout)

    def test_pr_body_review_contract_stays_compact(self) -> None:
        """Generated review contract should not dump script constants."""
        with tempfile.TemporaryDirectory() as temp_dir:
            target_root = Path(temp_dir)
            create_target_repo(repo_root=target_root, omitted_paths=set())

            run_command(
                args=["bash", str(SYNC_SH)],
                cwd=target_root,
                env=sync_env(upstream_dir=REPO_ROOT),
                check=True,
            )

            skeleton_path = (
                target_root
                / ".coding_workflow/diffs/pr_body_skeleton.md"
            )
            contract = extract_review_contract(
                pr_body_text=skeleton_path.read_text(encoding="utf-8"),
            )
            self.assertIn("Final gate owns sentinels", contract)
            self.assertIn("Reviewer must cross-check", contract)
            self.assertIn("architecture.md", contract)
            self.assertIn("zh/scripts/OPERATIONS.md", contract)
            self.assertIn("zh/scripts/sync_pr_review_system.md", contract)
            self.assertNotIn("Required sync sentinels", contract)
            self.assertNotIn("pass_id | pass | status | evidence", contract)
            self.assertNotIn("Full Document Reconcile columns", contract)
            self.assertNotIn("<!-- sync:", contract)

    def test_reviewer_prompt_does_not_copy_contract_literals(self) -> None:
        """Thin reviewer prompt must not become a second mechanical contract."""
        prompt_path = REPO_ROOT / "zh/scripts/sync_pr_review_system.md"
        prompt_text = prompt_path.read_text(encoding="utf-8")
        sentinel_literals = [
            SYNC_MODULE.SYNC_PR_BODY_MARKER,
            SYNC_MODULE.SYNC_AUTO_START,
            SYNC_MODULE.SYNC_AUTO_END,
        ]
        for section_name in SYNC_MODULE.AGENT_SECTIONS:
            sentinel_literals.append(
                SYNC_MODULE.agent_section_start(section_name=section_name)
            )
            sentinel_literals.append(
                SYNC_MODULE.agent_section_end(section_name=section_name)
            )
        forbidden_literals = [
            *CORE_FILES,
            *SYNC_MODULE.SYNC_PROMPT_FILES,
            *sentinel_literals,
            *SYNC_MODULE.TEMPLATE_MARKERS,
            *SYNC_MODULE.TODO_ANCHOR_COMMENTS,
            *sorted(SYNC_MODULE.BLOCKING_FINAL_STATUSES),
        ]
        forbidden_phrases = (
            "9 个",
            "2 个",
            "10 项",
            "core files checked: 9",
        )
        for literal in forbidden_literals:
            self.assertNotIn(
                literal,
                prompt_text,
                msg=f"review prompt copied contract literal: {literal}",
            )
        for phrase in forbidden_phrases:
            self.assertNotIn(
                phrase,
                prompt_text,
                msg=f"review prompt copied fixed count: {phrase}",
            )

    def test_sync_rejects_missing_upstream_prompt_file(self) -> None:
        """Sync must not publish raw URLs for missing review prompts."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            upstream_root = root / "upstream"
            target_root = root / "target"
            target_root.mkdir()
            create_upstream_without_prompt(
                upstream_root=upstream_root,
                missing_prompt_path="zh/scripts/sync_pr_review_system.md",
            )
            create_target_repo(repo_root=target_root, omitted_paths=set())

            result = run_command(
                args=["bash", str(upstream_root / "scripts" / "sync.sh")],
                cwd=target_root,
                env=sync_env(upstream_dir=upstream_root),
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "missing required sync prompt file",
                f"{result.stdout}\n{result.stderr}",
            )

    def test_pr_body_marker_counts_as_sync_sentinel(self) -> None:
        """A marker-only damaged sync draft should not look like plain text."""
        self.assertTrue(
            SYNC_MODULE.pr_body_has_any_sync_sentinel(
                text=f"{SYNC_MODULE.SYNC_PR_BODY_MARKER}\n"
            )
        )

    def test_warns_when_pr_body_is_tracked(self) -> None:
        """Sync should warn instead of silently accepting tracked PR_BODY.md."""
        with tempfile.TemporaryDirectory() as temp_dir:
            target_root = Path(temp_dir)
            (target_root / "PR_BODY.md").write_text(
                "tracked draft\n",
                encoding="utf-8",
            )
            commit_initial_repo(repo_root=target_root)

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                SYNC_MODULE.warn_if_pr_body_tracked(repo_root=target_root)

            self.assertIn("WARN: PR_BODY.md is tracked", output.getvalue())
            self.assertIn("git rm --cached PR_BODY.md", output.getvalue())

    def test_refresh_appends_upstream_drift_log(self) -> None:
        """Refreshing across upstream commits should preserve a drift warning."""
        with tempfile.TemporaryDirectory() as temp_dir:
            target_root = Path(temp_dir)
            old_state = sample_sync_state()
            new_state = sample_sync_state()
            new_state["upstream_resolved_commit"] = "c" * 40
            state_path = SYNC_MODULE.state_path_for(repo_root=target_root)
            state_path.parent.mkdir(parents=True, exist_ok=True)
            state_path.write_text(
                json.dumps(new_state, ensure_ascii=False),
                encoding="utf-8",
            )
            pr_body_path = target_root / "PR_BODY.md"
            pr_body_path.write_text(
                SYNC_MODULE.render_pr_body_skeleton(state=old_state),
                encoding="utf-8",
            )

            SYNC_MODULE.update_pr_body(
                repo_root=target_root,
                pr_body_path=pr_body_path,
            )

            refreshed = pr_body_path.read_text(encoding="utf-8")
            self.assertIn("## Upstream Drift Log", refreshed)
            self.assertIn(f"{'a' * 40} -> {'c' * 40}", refreshed)
            self.assertIn(
                "- upstream_resolved_commit: " + "c" * 40,
                refreshed,
            )


if __name__ == "__main__":
    unittest.main()
