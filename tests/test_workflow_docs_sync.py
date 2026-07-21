"""验证单会话 Workflow Docs Sync 的 prepare、check、安装器和结构边界。"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "zh/skills/workflow-docs-sync"
SYNC_SCRIPT = SKILL_ROOT / "scripts/sync_docs.py"
INSTALLER = REPO_ROOT / "zh/scripts/install_skills.py"
PLATFORM_ROOTS = (Path(".agents/skills"), Path(".claude/skills"))
OBSOLETE_SKILL = "workflow-docs-sync-review"
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
NON_PR_FILES = tuple(
    path for path in CORE_FILES if path != ".github/pull_request_template.md"
)
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
    "待补充",
)
FORBIDDEN_CONTROL_WORDS = (
    "start-pass",
    "finish-pass",
    "prepare-submit",
    "seal-submit",
    "finish-submit",
    "active_mode",
    "completed_modes",
    "submit_ready",
    "run.json",
    "baseline",
    "skill_runtime",
    "skill_results",
    "SYNC_PR_BODY_MARKER",
    "sync:agent:start",
    "headRefOid",
)


def run(
    *,
    args: list[str],
    cwd: Path,
    check: bool = False,
    environment: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """运行测试子进程并稳定捕获 UTF-8 输出。"""
    merged_environment = os.environ.copy()
    merged_environment["LC_ALL"] = "C"
    merged_environment["PYTHONDONTWRITEBYTECODE"] = "1"
    if environment is not None:
        merged_environment.update(environment)
    return subprocess.run(
        args=args,
        cwd=cwd,
        env=merged_environment,
        check=check,
        capture_output=True,
        encoding="utf-8",
        text=True,
    )


def git(*, repo: Path, args: list[str], check: bool = True) -> str:
    """运行 Git 并返回去掉末尾换行的 stdout。"""
    result = run(args=["git", "-C", str(repo), *args], cwd=repo, check=False)
    if check and result.returncode != 0:
        pytest.fail(
            f"git {' '.join(args)} failed ({result.returncode}):\n"
            f"stdout={result.stdout}\nstderr={result.stderr}"
        )
    return result.stdout.strip()


def init_repo(*, path: Path) -> Path:
    """创建带固定身份和初始提交的临时 Git 仓库。"""
    path.mkdir(parents=True)
    git(repo=path, args=["init", "-q"])
    git(repo=path, args=["config", "user.email", "tests@example.com"])
    git(repo=path, args=["config", "user.name", "Workflow Tests"])
    (path / "README.md").write_text("# Temporary repository\n", encoding="utf-8")
    git(repo=path, args=["add", "README.md"])
    git(repo=path, args=["commit", "-q", "-m", "initial"])
    return path


def commit_all(*, repo: Path, message: str) -> str:
    """提交临时仓库全部文件并返回完整 HEAD。"""
    git(repo=repo, args=["add", "-A"])
    git(repo=repo, args=["commit", "-q", "-m", message])
    return git(repo=repo, args=["rev-parse", "HEAD"])


def template_text(*, language: str, relative_path: str, version: str) -> str:
    """生成无占位、可用于 pin 与 equality 测试的最小模板。"""
    if relative_path == "capability_contract.json":
        return json.dumps(
            {
                "schema_version": "1.0",
                "contracts": {
                    "documents": [
                        {
                            "anchor_id": f"DOC.{language}_{version}",
                            "statement": f"{language} {version} contract",
                        }
                    ]
                },
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ) + "\n"
    title = relative_path.replace("/", " ")
    return f"# {language.upper()} {title} {version}\n\nUpstream {version} text.\n"


def write_templates(*, upstream: Path, version: str) -> None:
    """向临时上游写入两种语言的九份模板。"""
    for language in ("zh", "en"):
        for relative_path in CORE_FILES:
            path = upstream / language / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                template_text(
                    language=language,
                    relative_path=relative_path,
                    version=version,
                ),
                encoding="utf-8",
            )


def create_upstream(*, root: Path, version: str = "v1") -> tuple[Path, str]:
    """创建并提交双语模板上游。"""
    upstream = init_repo(path=root)
    write_templates(upstream=upstream, version=version)
    return upstream, commit_all(repo=upstream, message=f"templates {version}")


def create_target(*, root: Path) -> Path:
    """创建没有核心文档的 clean 目标仓库。"""
    return init_repo(path=root)


def parse_single_json(*, result: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    """断言脚本 stdout 恰好包含一行 JSON 并返回对象。"""
    lines = result.stdout.splitlines()
    assert len(lines) == 1, result.stdout
    payload = json.loads(lines[0])
    assert isinstance(payload, dict)
    return payload


def run_sync(
    *,
    command: str,
    target: Path,
    upstream: Path,
    language: str = "zh",
    upstream_sha: str | None = None,
    expected_target_head: str | None = None,
) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    """调用同步器内部 CLI 并解析单行结果。"""
    args = [
        sys.executable,
        str(SYNC_SCRIPT),
        command,
        "--target-repo",
        str(target),
        "--upstream-dir",
        str(upstream),
    ]
    if command == "check":
        assert upstream_sha is not None
        assert expected_target_head is not None
        args.extend(
            [
                "--upstream-sha",
                upstream_sha,
                "--expected-target-head",
                expected_target_head,
            ]
        )
    args.extend(["--language", language])
    result = run(args=args, cwd=target)
    return result, parse_single_json(result=result)


def prepare(
    *, target: Path, upstream: Path, language: str = "zh"
) -> dict[str, Any]:
    """运行成功的 prepare 并返回会话事实。"""
    result, payload = run_sync(
        command="prepare",
        target=target,
        upstream=upstream,
        language=language,
    )
    assert result.returncode == 0, payload
    assert payload["status"] == "prepared"
    return payload


def specialize(*, target: Path, label: str = "target") -> None:
    """把八份非 PR 模板改成项目内容，保留 PR template 直接继承。"""
    for relative_path in NON_PR_FILES:
        path = target / relative_path
        if relative_path == "capability_contract.json":
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["project"] = label
            path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        else:
            path.write_text(
                path.read_text(encoding="utf-8")
                + f"\nProject-specific evidence for {label}.\n",
                encoding="utf-8",
            )


def run_check(
    *,
    target: Path,
    upstream: Path,
    prepared: dict[str, Any],
    language: str = "zh",
    upstream_sha: str | None = None,
) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    """使用 prepare 返回的 SHA 和目标 HEAD 调用 check。"""
    return run_sync(
        command="check",
        target=target,
        upstream=upstream,
        language=language,
        upstream_sha=upstream_sha or prepared["upstream_sha"],
        expected_target_head=prepared["target_head"],
    )


def ready_case(
    *, tmp_path: Path, language: str = "zh"
) -> tuple[Path, Path, dict[str, Any]]:
    """创建已 prepare 且八份文档项目化的常用测试场景。"""
    upstream, _ = create_upstream(root=tmp_path / "upstream")
    target = create_target(root=tmp_path / "target")
    prepared = prepare(target=target, upstream=upstream, language=language)
    specialize(target=target)
    return upstream, target, prepared


def assert_check_failed(
    *,
    target: Path,
    upstream: Path,
    prepared: dict[str, Any],
    expected_text: str,
    language: str = "zh",
) -> dict[str, Any]:
    """断言最终检查失败且诊断包含指定文本。"""
    result, payload = run_check(
        target=target,
        upstream=upstream,
        prepared=prepared,
        language=language,
    )
    assert result.returncode == 1
    assert payload["status"] == "failed"
    assert expected_text in payload["detail"]
    return payload


def snapshot(*, repo: Path) -> tuple[dict[str, bytes], str]:
    """读取除 .git 外的文件 bytes 与 porcelain 状态。"""
    files = {
        path.relative_to(repo).as_posix(): path.read_bytes()
        for path in repo.rglob("*")
        if path.is_file() and ".git" not in path.relative_to(repo).parts
    }
    status = git(
        repo=repo,
        args=["status", "--porcelain=v1", "--untracked-files=all"],
    )
    return files, status


@pytest.mark.parametrize("language", ["zh", "en"])
def test_prepare_installs_selected_language_templates(
    tmp_path: Path, language: str
) -> None:
    """prepare 应从所选语言的固定 Git 对象安装九份模板。"""
    upstream, upstream_sha = create_upstream(root=tmp_path / "upstream")
    target = create_target(root=tmp_path / "target")
    payload = prepare(target=target, upstream=upstream, language=language)
    assert payload["upstream_sha"] == upstream_sha
    assert payload["installed"] == list(CORE_FILES)
    assert payload["existing"] == []
    for relative_path in CORE_FILES:
        assert (target / relative_path).read_text(encoding="utf-8") == (
            upstream / language / relative_path
        ).read_text(encoding="utf-8")


def test_prepare_is_idempotent(tmp_path: Path) -> None:
    """第二次 prepare 不得重写第一次安装的任何文件。"""
    upstream, _ = create_upstream(root=tmp_path / "upstream")
    target = create_target(root=tmp_path / "target")
    first = prepare(target=target, upstream=upstream)
    before = snapshot(repo=target)
    second = prepare(target=target, upstream=upstream)
    assert second["target_head"] == first["target_head"]
    assert second["installed"] == []
    assert second["existing"] == list(CORE_FILES)
    assert snapshot(repo=target) == before


def test_prepare_never_overwrites_existing_document(tmp_path: Path) -> None:
    """已有核心文档即使 dirty 也必须原样保留。"""
    upstream, _ = create_upstream(root=tmp_path / "upstream")
    target = create_target(root=tmp_path / "target")
    custom = "# Existing architecture\n\nProject truth.\n"
    (target / "architecture.md").write_text(custom, encoding="utf-8")
    payload = prepare(target=target, upstream=upstream)
    assert payload["installed"] == list(CORE_FILES[1:])
    assert payload["existing"] == ["architecture.md"]
    assert (target / "architecture.md").read_text(encoding="utf-8") == custom


def test_prepare_reads_committed_template_not_upstream_worktree(tmp_path: Path) -> None:
    """upstream dirty 内容不得影响 git-show 读取的 HEAD 模板。"""
    upstream, _ = create_upstream(root=tmp_path / "upstream")
    target = create_target(root=tmp_path / "target")
    committed = (upstream / "zh/architecture.md").read_text(encoding="utf-8")
    (upstream / "zh/architecture.md").write_text(
        "# Dirty upstream worktree\n",
        encoding="utf-8",
    )
    prepare(target=target, upstream=upstream)
    assert (target / "architecture.md").read_text(encoding="utf-8") == committed


def test_check_uses_prepare_sha_after_upstream_head_advances(tmp_path: Path) -> None:
    """check 必须复用 prepare SHA，而不能偷偷读取新的 upstream HEAD。"""
    upstream, old_sha = create_upstream(root=tmp_path / "upstream", version="v1")
    target = create_target(root=tmp_path / "target")
    prepared = prepare(target=target, upstream=upstream)
    specialize(target=target)
    write_templates(upstream=upstream, version="v2")
    new_sha = commit_all(repo=upstream, message="templates v2")
    (target / "architecture.md").write_text(
        (upstream / "zh/architecture.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    old_result, old_payload = run_check(
        target=target,
        upstream=upstream,
        prepared=prepared,
        upstream_sha=old_sha,
    )
    new_result, new_payload = run_check(
        target=target,
        upstream=upstream,
        prepared=prepared,
        upstream_sha=new_sha,
    )
    assert old_result.returncode == 0, old_payload
    assert old_payload["upstream_sha"] == old_sha
    assert new_result.returncode == 1
    assert "architecture.md" in new_payload["detail"]
    assert "完全相同" in new_payload["detail"]


@pytest.mark.parametrize("dirty_kind", ["untracked", "tracked"])
def test_prepare_rejects_outside_dirty_before_any_write(
    tmp_path: Path, dirty_kind: str
) -> None:
    """allowlist 外 dirty path 必须在九份模板落盘前失败。"""
    upstream, _ = create_upstream(root=tmp_path / "upstream")
    target = create_target(root=tmp_path / "target")
    if dirty_kind == "untracked":
        (target / "rogue.txt").write_text("rogue\n", encoding="utf-8")
    else:
        (target / "README.md").write_text("# Changed\n", encoding="utf-8")
    result, payload = run_sync(
        command="prepare",
        target=target,
        upstream=upstream,
    )
    assert result.returncode == 1
    assert "dirty path" in payload["error"]
    assert not any((target / path).exists() for path in CORE_FILES)


def test_prepare_rejects_rename_with_outside_endpoint(tmp_path: Path) -> None:
    """rename 的来源和目标都必须属于允许范围。"""
    upstream, _ = create_upstream(root=tmp_path / "upstream")
    target = create_target(root=tmp_path / "target")
    (target / "architecture.md").write_text("# Architecture\n", encoding="utf-8")
    commit_all(repo=target, message="add allowed doc")
    git(repo=target, args=["mv", "architecture.md", "rogue.md"])
    result, payload = run_sync(
        command="prepare",
        target=target,
        upstream=upstream,
    )
    assert result.returncode == 1
    assert "rogue.md" in payload["detail"]
    assert not (target / "capability_contract.json").exists()


def test_prepare_allows_core_and_gitignore_dirty(tmp_path: Path) -> None:
    """核心文档与辅助 .gitignore 是唯一允许的 dirty 范围。"""
    upstream, _ = create_upstream(root=tmp_path / "upstream")
    target = create_target(root=tmp_path / "target")
    (target / ".gitignore").write_text("*.local\n", encoding="utf-8")
    (target / "architecture.md").write_text(
        "# Project architecture\n",
        encoding="utf-8",
    )
    payload = prepare(target=target, upstream=upstream)
    assert "architecture.md" in payload["existing"]
    assert len(payload["installed"]) == 8


def test_prepare_preflights_parent_collision(tmp_path: Path) -> None:
    """父路径冲突必须在安装任意模板前失败。"""
    upstream, _ = create_upstream(root=tmp_path / "upstream")
    target = create_target(root=tmp_path / "target")
    (target / "docs").write_text("not a directory\n", encoding="utf-8")
    commit_all(repo=target, message="parent collision")
    result, payload = run_sync(
        command="prepare",
        target=target,
        upstream=upstream,
    )
    assert result.returncode == 1
    assert "父路径不是目录" in payload["error"]
    assert not (target / "architecture.md").exists()


def test_prepare_rejects_symlink_destination_before_write(tmp_path: Path) -> None:
    """核心文档 symlink 不得被当成已有普通文档。"""
    upstream, _ = create_upstream(root=tmp_path / "upstream")
    target = create_target(root=tmp_path / "target")
    outside = tmp_path / "outside.md"
    outside.write_text("# Outside\n", encoding="utf-8")
    (target / "architecture.md").symlink_to(outside)
    result, payload = run_sync(
        command="prepare",
        target=target,
        upstream=upstream,
    )
    assert result.returncode == 1
    assert "符号链接" in payload["error"]
    assert not (target / "capability_contract.json").exists()
    assert outside.read_text(encoding="utf-8") == "# Outside\n"


@pytest.mark.parametrize("missing_path", CORE_FILES)
def test_check_requires_all_nine_files(tmp_path: Path, missing_path: str) -> None:
    """缺少任意核心文件都必须失败。"""
    upstream, target, prepared = ready_case(tmp_path=tmp_path)
    (target / missing_path).unlink()
    assert_check_failed(
        target=target,
        upstream=upstream,
        prepared=prepared,
        expected_text=f"缺少必需文件: {missing_path}",
    )


def test_check_rejects_invalid_utf8(tmp_path: Path) -> None:
    """九份文件必须能严格解码为 UTF-8。"""
    upstream, target, prepared = ready_case(tmp_path=tmp_path)
    (target / "architecture.md").write_bytes(b"# valid\n\xff\n")
    assert_check_failed(
        target=target,
        upstream=upstream,
        prepared=prepared,
        expected_text="不是有效 UTF-8",
    )


@pytest.mark.parametrize(
    ("content", "expected"),
    [
        ("{\n", "JSON 无效"),
        ("[]\n", "顶层必须是 JSON object"),
    ],
)
def test_check_validates_capability_contract(
    tmp_path: Path, content: str, expected: str
) -> None:
    """capability contract 应验证合法 JSON object。"""
    upstream, target, prepared = ready_case(tmp_path=tmp_path)
    (target / "capability_contract.json").write_text(content, encoding="utf-8")
    assert_check_failed(
        target=target,
        upstream=upstream,
        prepared=prepared,
        expected_text=expected,
    )


def test_capability_contract_accepts_project_specific_object(tmp_path: Path) -> None:
    """机械层不强制项目合同 schema 或虚构语义锚点。"""
    upstream, target, prepared = ready_case(tmp_path=tmp_path)
    (target / "capability_contract.json").write_text(
        '{"project":"schema-owned-by-target"}\n',
        encoding="utf-8",
    )
    result, payload = run_check(
        target=target,
        upstream=upstream,
        prepared=prepared,
    )
    assert result.returncode == 0, payload


@pytest.mark.parametrize(
    ("content", "expected"),
    [
        ("", "文件为空"),
        ("plain text\n", "缺少非空 Markdown 标题"),
        ("#\nbody\n", "Markdown 标题为空"),
        ("# #\nbody\n", "Markdown 标题为空"),
        ("# ###\nbody\n", "Markdown 标题为空"),
        ("```text\n# code only\n```\n", "缺少非空 Markdown 标题"),
    ],
)
def test_check_rejects_empty_file_or_markdown_title(
    tmp_path: Path, content: str, expected: str
) -> None:
    """空内容、空标题和 code fence 内伪标题都不能通过。"""
    upstream, target, prepared = ready_case(tmp_path=tmp_path)
    (target / "architecture.md").write_text(content, encoding="utf-8")
    assert_check_failed(
        target=target,
        upstream=upstream,
        prepared=prepared,
        expected_text=expected,
    )


@pytest.mark.parametrize("token", TEMPLATE_TOKENS)
def test_check_rejects_explicit_template_tokens(tmp_path: Path, token: str) -> None:
    """明确列出的模板 token 和待填写值必须逐项失败。"""
    upstream, target, prepared = ready_case(tmp_path=tmp_path)
    (target / "architecture.md").write_text(
        f"# Project architecture\n\nResidue: {token}\n",
        encoding="utf-8",
    )
    assert_check_failed(
        target=target,
        upstream=upstream,
        prepared=prepared,
        expected_text="检测到未项目化内容",
    )


def test_check_does_not_generalize_angle_bracket_tokens(tmp_path: Path) -> None:
    """合法命令占位不得被泛化的尖括号规则误杀。"""
    upstream, target, prepared = ready_case(tmp_path=tmp_path)
    (target / "architecture.md").write_text(
        "# Project architecture\n\n"
        "Compare <base>...HEAD and publish <feature-branch> for <time range>.\n",
        encoding="utf-8",
    )
    result, payload = run_check(
        target=target,
        upstream=upstream,
        prepared=prepared,
    )
    assert result.returncode == 0, payload


@pytest.mark.parametrize("relative_path", NON_PR_FILES)
def test_check_rejects_non_pr_file_equal_to_template(
    tmp_path: Path, relative_path: str
) -> None:
    """除 PR template 外的八份文档都必须体现项目事实。"""
    upstream, target, prepared = ready_case(tmp_path=tmp_path)
    (target / relative_path).write_text(
        (upstream / "zh" / relative_path).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    assert_check_failed(
        target=target,
        upstream=upstream,
        prepared=prepared,
        expected_text=f"{relative_path}: 不允许与固定上游模板完全相同",
    )


def test_check_treats_crlf_template_copy_as_equal(tmp_path: Path) -> None:
    """模板 equality 只应忽略平台换行差异。"""
    upstream, target, prepared = ready_case(tmp_path=tmp_path)
    text = (upstream / "zh/architecture.md").read_text(encoding="utf-8")
    (target / "architecture.md").write_bytes(text.replace("\n", "\r\n").encode())
    assert_check_failed(
        target=target,
        upstream=upstream,
        prepared=prepared,
        expected_text="architecture.md: 不允许与固定上游模板完全相同",
    )


def test_pr_template_exact_inheritance_is_allowed(tmp_path: Path) -> None:
    """PR template 是唯一允许与固定上游完全相同的核心文件。"""
    upstream, target, prepared = ready_case(tmp_path=tmp_path)
    result, payload = run_check(
        target=target,
        upstream=upstream,
        prepared=prepared,
    )
    assert result.returncode == 0, payload
    assert payload["files_checked"] == 9


def tracked_ready_case(*, tmp_path: Path) -> tuple[Path, Path, dict[str, Any]]:
    """创建核心文档已提交、随后重新 prepare 的 whitespace 场景。"""
    upstream, target, _ = ready_case(tmp_path=tmp_path)
    commit_all(repo=target, message="project docs")
    prepared = prepare(target=target, upstream=upstream)
    return upstream, target, prepared


@pytest.mark.parametrize("state", ["unstaged", "staged", "committed"])
def test_check_rejects_tracked_whitespace(tmp_path: Path, state: str) -> None:
    """working tree、index 与已提交基线的 whitespace 都必须被发现。"""
    upstream, target, prepared = tracked_ready_case(tmp_path=tmp_path)
    with (target / "architecture.md").open("a", encoding="utf-8") as stream:
        stream.write("bad trailing whitespace \n")
    if state == "staged":
        git(repo=target, args=["add", "architecture.md"])
    elif state == "committed":
        commit_all(repo=target, message="bad baseline")
        prepared = prepare(target=target, upstream=upstream)
    assert_check_failed(
        target=target,
        upstream=upstream,
        prepared=prepared,
        expected_text="trailing whitespace",
    )


@pytest.mark.parametrize("bad_line,ignored", [
    ("bad trailing whitespace \n", False), ("<<<<<<< ours\n", False),
    ("bad trailing whitespace \n", True),
])
def test_untracked_whitespace(tmp_path: Path, bad_line: str, ignored: bool) -> None:
    """untracked 或 ignored 核心文档必须接受同等检查。"""
    upstream, target, prepared = ready_case(tmp_path=tmp_path)
    if ignored:
        (target / ".gitignore").write_text("architecture.md\n", encoding="utf-8")
    with (target / "architecture.md").open("a", encoding="utf-8") as stream:
        stream.write(bad_line)
    expected = "trailing whitespace" if bad_line.startswith("bad") else "conflict marker"
    assert_check_failed(
        target=target,
        upstream=upstream,
        prepared=prepared,
        expected_text=expected,
    )


@pytest.mark.parametrize(
    ("content", "expected"),
    [(b"*.local\n", None), (b"*.local \n", "trailing whitespace"),
     (b"*.local\n\xff", "不是有效 UTF-8")],
)
def test_check_validates_optional_gitignore(
    tmp_path: Path, content: bytes, expected: str | None) -> None:
    """可选 gitignore 必须是 UTF-8，且继续使用 Git whitespace 规则。"""
    upstream, target, prepared = ready_case(tmp_path=tmp_path)
    (target / ".gitignore").write_bytes(content)
    if expected is not None:
        assert_check_failed(
            target=target, upstream=upstream, prepared=prepared, expected_text=expected
        )
    else:
        result, payload = run_check(target=target, upstream=upstream, prepared=prepared)
        assert result.returncode == 0, payload


@pytest.mark.parametrize("kind", ["symlink", "directory"])
def test_check_rejects_non_regular_gitignore(tmp_path: Path, kind: str) -> None:
    """可选 gitignore 不得是 symlink 或其他非普通文件。"""
    upstream, target, prepared = ready_case(tmp_path=tmp_path)
    outside = tmp_path / "outside.gitignore"
    outside.write_text("external target\n", encoding="utf-8")
    if kind == "symlink":
        (target / ".gitignore").symlink_to(outside)
    else:
        (target / ".gitignore").mkdir()
    expected = "符号链接" if kind == "symlink" else "不是普通文件"
    assert_check_failed(
        target=target, upstream=upstream, prepared=prepared, expected_text=expected
    )
    assert outside.read_text(encoding="utf-8") == "external target\n"


def test_check_rejects_changed_target_head(tmp_path: Path) -> None:
    """prepare 后目标 HEAD 变化必须先于内容检查失败。"""
    upstream, target, prepared = ready_case(tmp_path=tmp_path)
    commit_all(repo=target, message="unexpected commit")
    result, payload = run_check(
        target=target,
        upstream=upstream,
        prepared=prepared,
    )
    assert result.returncode == 1
    assert payload["error"] == "目标 HEAD 已变化"


def test_check_is_idempotent_and_read_only(tmp_path: Path) -> None:
    """连续 check 应返回同一结果且不改变文件或 Git 状态。"""
    upstream, target, prepared = ready_case(tmp_path=tmp_path)
    before = snapshot(repo=target)
    first_result, first = run_check(
        target=target,
        upstream=upstream,
        prepared=prepared,
    )
    middle = snapshot(repo=target)
    second_result, second = run_check(
        target=target,
        upstream=upstream,
        prepared=prepared,
    )
    assert first_result.returncode == second_result.returncode == 0
    assert first == second
    assert before == middle == snapshot(repo=target)
    assert not (target / ".coding_workflow").exists()
    assert not (target / "PR_BODY.md").exists()


def test_existing_ignored_pr_body_is_not_sync_input(tmp_path: Path) -> None:
    """被目标仓库忽略的通用 PR 草稿不得被读取、重写或删除。"""
    upstream, _ = create_upstream(root=tmp_path / "upstream")
    target = create_target(root=tmp_path / "target")
    (target / ".gitignore").write_text("PR_BODY.md\n", encoding="utf-8")
    body = "# Unrelated PR draft\n"
    (target / "PR_BODY.md").write_text(body, encoding="utf-8")
    prepared = prepare(target=target, upstream=upstream)
    specialize(target=target)
    result, payload = run_check(
        target=target,
        upstream=upstream,
        prepared=prepared,
    )
    assert result.returncode == 0, payload
    assert (target / "PR_BODY.md").read_text(encoding="utf-8") == body
    assert not (target / ".coding_workflow").exists()


def create_installer_upstream(*, root: Path) -> Path:
    """创建同时含 canonical Skill 和应被忽略的第二 Skill 的 clean 上游。"""
    upstream = init_repo(path=root)
    canonical = upstream / "zh/skills/workflow-docs-sync"
    canonical.mkdir(parents=True)
    (canonical / "SKILL.md").write_text(
        "---\nname: workflow-docs-sync\n"
        "description: Test canonical skill.\n---\n\n# Skill\n",
        encoding="utf-8",
    )
    (canonical / "scripts").mkdir()
    (canonical / "scripts/helper.py").write_text("VALUE = 1\n", encoding="utf-8")
    obsolete = upstream / "zh/skills/workflow-docs-sync-review"
    obsolete.mkdir(parents=True)
    (obsolete / "SKILL.md").write_text(
        "---\nname: workflow-docs-sync-review\n"
        "description: Must not be copied.\n---\n",
        encoding="utf-8",
    )
    commit_all(repo=upstream, message="skills")
    return upstream


def run_installer(
    *, upstream: Path, target: Path | None = None, home: Path | None = None
) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    """以 repo 或临时 HOME user scope 运行安装器并解析 JSON。"""
    scope = "repo" if target is not None else "user"
    args = [sys.executable, str(INSTALLER), "--scope", scope, "--upstream-dir", str(upstream)]
    if target is not None:
        args.extend(["--target-repo", str(target)])
    result = run(
        args=args,
        cwd=REPO_ROOT,
        environment={"HOME": str(home)} if home is not None else None,
    )
    return result, parse_single_json(result=result)


def test_installer_repo_upgrade_removes_only_obsolete_directories(tmp_path: Path) -> None:
    """repo 升级应精确删除两份旧 reviewer，并保持其他 Skill 字节不变。"""
    upstream = create_installer_upstream(root=tmp_path / "upstream")
    target = create_target(root=tmp_path / "target")
    for platform_root in PLATFORM_ROOTS:
        obsolete = target / platform_root / OBSOLETE_SKILL
        obsolete.mkdir(parents=True)
        (obsolete / "legacy.bin").write_bytes(b"legacy reviewer\x00")
        unrelated = target / platform_root / "unrelated-skill"
        unrelated.mkdir()
        (unrelated / "keep.bin").write_bytes(b"keep unrelated\x00")
    commit_all(repo=target, message="legacy installed skills")
    result, payload = run_installer(upstream=upstream, target=target)
    assert result.returncode == 0, payload
    assert payload["skill"] == "workflow-docs-sync"
    expected = [str(target / root / OBSOLETE_SKILL) for root in PLATFORM_ROOTS]
    assert payload["removed_obsolete"] == expected
    for platform_root in PLATFORM_ROOTS:
        installed = target / platform_root / "workflow-docs-sync"
        assert (installed / "SKILL.md").is_file()
        assert (installed / "scripts/helper.py").is_file()
        assert not (target / platform_root / OBSOLETE_SKILL).exists()
        unrelated = target / platform_root / "unrelated-skill/keep.bin"
        assert unrelated.read_bytes() == b"keep unrelated\x00"
    assert not list(target.rglob(".source.json"))
    commit_all(repo=target, message="upgrade installed skills")
    repeated, repeated_payload = run_installer(upstream=upstream, target=target)
    assert repeated.returncode == 0, repeated_payload
    assert repeated_payload["removed_obsolete"] == []
    assert git(repo=target, args=["status", "--short"]) == ""


def test_installer_removes_obsolete_symlink_and_file(tmp_path: Path) -> None:
    """旧路径为 symlink 或普通文件时应 unlink，且不得跟随 symlink。"""
    upstream = create_installer_upstream(root=tmp_path / "upstream")
    target = create_target(root=tmp_path / "target")
    outside = tmp_path / "outside-skill"
    outside.mkdir()
    (outside / "keep.bin").write_bytes(b"external\x00")
    paths = [target / root / OBSOLETE_SKILL for root in PLATFORM_ROOTS]
    paths[0].parent.mkdir(parents=True)
    paths[0].symlink_to(outside, target_is_directory=True)
    paths[1].parent.mkdir(parents=True)
    paths[1].write_bytes(b"legacy file\x00")
    commit_all(repo=target, message="legacy path types")
    result, payload = run_installer(upstream=upstream, target=target)
    assert result.returncode == 0, payload
    assert payload["removed_obsolete"] == [str(path) for path in paths]
    assert all(not path.exists() and not path.is_symlink() for path in paths)
    assert (outside / "keep.bin").read_bytes() == b"external\x00"


def test_installer_user_upgrade_cleans_temporary_home(tmp_path: Path) -> None:
    """user scope 应在临时 HOME 执行同样的精确清理。"""
    upstream = create_installer_upstream(root=tmp_path / "upstream")
    home = tmp_path / "home"
    for platform_root in PLATFORM_ROOTS:
        obsolete = home / platform_root / OBSOLETE_SKILL
        obsolete.mkdir(parents=True)
        (obsolete / "legacy.bin").write_bytes(b"legacy\x00")
        unrelated = home / platform_root / "unrelated-skill"
        unrelated.mkdir()
        (unrelated / "keep.bin").write_bytes(b"keep\x00")
    result, payload = run_installer(upstream=upstream, home=home)
    assert result.returncode == 0, payload
    expected = [str(home / root / OBSOLETE_SKILL) for root in PLATFORM_ROOTS]
    assert payload["removed_obsolete"] == expected
    for platform_root in PLATFORM_ROOTS:
        assert not (home / platform_root / OBSOLETE_SKILL).exists()
        assert (home / platform_root / "workflow-docs-sync/SKILL.md").is_file()
        unrelated = home / platform_root / "unrelated-skill/keep.bin"
        assert unrelated.read_bytes() == b"keep\x00"
    assert not list(home.rglob(".source.json"))


def test_sync_cli_exposes_only_prepare_and_check() -> None:
    """内部 CLI 不得重新长出其他控制入口。"""
    result = run(
        args=[sys.executable, str(SYNC_SCRIPT), "--help"],
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0
    assert "{prepare,check}" in result.stdout
    assert "status" not in result.stdout


def test_deleted_control_plane_files_do_not_exist() -> None:
    """旧 launcher、review Skill、runbook 和测试不能作为兼容实现保留。"""
    deleted = (
        "PR_BODY.md",
        "scripts/sync_coding_workflow.py",
        "scripts/sync.sh",
        "zh/scripts/sync.sh",
        "en/scripts/sync.sh",
        "zh/scripts/OPERATIONS.md",
        "en/scripts/OPERATIONS.md",
        "zh/scripts/sync_pr_review_system.md",
        "en/scripts/sync_pr_review_system.md",
        "zh/skills/workflow-docs-sync/scripts/harness.py",
        "zh/skills/workflow-docs-sync/references/modes.md",
        "zh/skills/workflow-docs-sync/references/pass_ownership.json",
        "zh/skills/workflow-docs-sync-review",
        "tests/test_workflow_sync_skill.py",
        "tests/test_sync_coding_workflow.py",
    )
    assert [path for path in deleted if (REPO_ROOT / path).exists()] == []
    assert git(repo=REPO_ROOT, args=["ls-files", "--", "PR_BODY.md"]) == ""


def production_text_files() -> list[Path]:
    """列出结构性负向测试覆盖的生产与用户文档文件。"""
    suffixes = {".md", ".py", ".yaml", ".yml", ".json", ".sh"}
    excluded = {
        REPO_ROOT / "zh/docs/development_workflow/decisions.md",
        Path(__file__).resolve(),
    }
    return sorted(
        path
        for path in REPO_ROOT.rglob("*")
        if path.is_file()
        and ".git" not in path.relative_to(REPO_ROOT).parts
        and "__pycache__" not in path.parts
        and path.suffix in suffixes
        and path not in excluded
    )


def test_production_files_have_no_forbidden_control_plane_words() -> None:
    """除 DEC 历史外，生产面不得残留旧控制面状态或远端绑定词。"""
    hits: list[str] = []
    for path in production_text_files():
        text = path.read_text(encoding="utf-8")
        for word in FORBIDDEN_CONTROL_WORDS:
            if word in text:
                hits.append(f"{path.relative_to(REPO_ROOT)}: {word}")
    assert hits == []


def test_source_line_budgets() -> None:
    """保持测试可审查，并限制生产 Python 总体积。"""
    test_lines = Path(__file__).read_text(encoding="utf-8").count("\n") + 1
    production_lines = sum(
        path.read_text(encoding="utf-8").count("\n") + 1
        for path in (SYNC_SCRIPT, INSTALLER)
    )
    assert 600 <= test_lines <= 1000
    assert 500 <= production_lines <= 700


def test_skill_has_exact_minimal_structure() -> None:
    """canonical Skill 只保留合同指定的最小文件结构。"""
    actual = sorted(
        path.relative_to(SKILL_ROOT).as_posix()
        for path in SKILL_ROOT.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    )
    assert actual == [
        "SKILL.md",
        "agents/openai.yaml",
        "evals/README.md",
        "references/audit.md",
        "references/sections.md",
        "scripts/sync_docs.py",
    ]
