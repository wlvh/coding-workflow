"""通过公共 CLI 和完整分发路径验证 Workflow Docs Sync 的核心风险边界。"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "zh/skills/workflow-docs-sync"
SYNC_SCRIPT = SKILL_ROOT / "scripts/sync_docs.py"
INSTALLER = REPO_ROOT / "zh/scripts/install_skills.py"
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
ACTIVE_MARKERS = ("<!-- project-fill:", "__PROJECT_FILL__:")
PLATFORM_ROOTS = (
    ("codex", Path(".agents/skills")),
    ("claude", Path(".claude/skills")),
)
OBSOLETE_SKILL = "workflow-docs-sync-review"


def run_command(
    *,
    args: list[str],
    cwd: Path,
    environment: dict[str, str] | None,
) -> subprocess.CompletedProcess[str]:
    """运行隔离子进程并返回稳定 UTF-8 输出，不隐式抛出命令错误。"""
    merged_environment = os.environ.copy()
    merged_environment.update(
        {"LC_ALL": "C", "PYTHONDONTWRITEBYTECODE": "1"}
    )
    if environment is not None:
        merged_environment.update(environment)
    return subprocess.run(
        args=args,
        cwd=cwd,
        env=merged_environment,
        check=False,
        capture_output=True,
        encoding="utf-8",
        text=True,
    )


def git(*, repo: Path, args: list[str], check: bool) -> str:
    """运行 Git 并在要求成功时用完整诊断立即终止场景。"""
    result = run_command(
        args=["git", "-C", str(repo), *args],
        cwd=repo,
        environment=None,
    )
    if check and result.returncode != 0:
        pytest.fail(
            f"git {' '.join(args)} failed ({result.returncode}):\n"
            f"stdout={result.stdout}\nstderr={result.stderr}"
        )
    return result.stdout


def init_repo(*, path: Path) -> Path:
    """创建带固定测试身份和初始提交的真实临时 Git 仓库。"""
    path.mkdir(parents=True)
    git(repo=path, args=["init", "-q"], check=True)
    git(
        repo=path,
        args=["config", "user.email", "tests@example.com"],
        check=True,
    )
    git(
        repo=path,
        args=["config", "user.name", "Workflow Scenario Tests"],
        check=True,
    )
    (path / "README.md").write_text(
        data="# Temporary repository\n",
        encoding="utf-8",
    )
    git(repo=path, args=["add", "README.md"], check=True)
    git(repo=path, args=["commit", "-q", "-m", "initial"], check=True)
    return path


def commit_all(*, repo: Path, message: str) -> str:
    """提交临时仓库全部状态并返回固定 HEAD。"""
    git(repo=repo, args=["add", "-A"], check=True)
    git(repo=repo, args=["commit", "-q", "-m", message], check=True)
    return git(repo=repo, args=["rev-parse", "HEAD"], check=True).strip()


def template_text(*, language: str, relative_path: str, version: str) -> str:
    """生成只含 active marker 的双语分发 fixture。"""
    if relative_path == "capability_contract.json":
        payload = {
            "schema_version": version,
            "status": f"__PROJECT_FILL__: {language} {version} project status",
        }
        return json.dumps(
            obj=payload,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ) + "\n"
    title = relative_path.replace("/", " ")
    if relative_path == ".github/pull_request_template.md":
        return f"# {language.upper()} {title} {version}\n"
    return (
        f"# {language.upper()} {title} {version}\n\n"
        "<!-- project-fill: replace with verified project facts -->\n"
    )


def write_templates(*, upstream: Path, version: str) -> None:
    """写入两种语言的九份 fixture，以便真实 Git object 固定其 bytes。"""
    for language in ("zh", "en"):
        for relative_path in CORE_FILES:
            path = upstream / language / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                data=template_text(
                    language=language,
                    relative_path=relative_path,
                    version=version,
                ),
                encoding="utf-8",
            )


def create_upstream(*, root: Path, version: str) -> tuple[Path, str]:
    """创建含双语模板的 clean 上游仓库和固定提交。"""
    upstream = init_repo(path=root)
    write_templates(upstream=upstream, version=version)
    sha = commit_all(repo=upstream, message=f"templates {version}")
    return upstream, sha


def parse_single_json(
    *, result: subprocess.CompletedProcess[str]
) -> dict[str, Any]:
    """断言 CLI stdout 只有一个 JSON object，并返回该数据。"""
    lines = result.stdout.splitlines()
    assert len(lines) == 1, result.stdout
    payload = json.loads(s=lines[0])
    assert isinstance(payload, dict)
    return payload


def run_prepare(
    *, target: Path, upstream: Path, language: str
) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    """通过公开 prepare CLI 返回进程结果和 JSON 数据。"""
    result = run_command(
        args=[
            sys.executable,
            str(SYNC_SCRIPT),
            "prepare",
            "--target-repo",
            str(target),
            "--upstream-dir",
            str(upstream),
            "--language",
            language,
        ],
        cwd=target,
        environment=None,
    )
    return result, parse_single_json(result=result)


def prepare_success(*, target: Path, upstream: Path, language: str) -> dict[str, Any]:
    """执行必须成功的 prepare，并立即返回会话固定数据。"""
    result, payload = run_prepare(
        target=target,
        upstream=upstream,
        language=language,
    )
    assert result.returncode == 0, payload
    assert payload["status"] == "prepared"
    return payload


def run_check(
    *,
    target: Path,
    upstream: Path,
    language: str,
    upstream_sha: str,
    expected_target_head: str,
    environment: dict[str, str] | None,
) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    """通过公开 check CLI 验证调用方固定的两端 SHA。"""
    result = run_command(
        args=[
            sys.executable,
            str(SYNC_SCRIPT),
            "check",
            "--target-repo",
            str(target),
            "--upstream-dir",
            str(upstream),
            "--upstream-sha",
            upstream_sha,
            "--expected-target-head",
            expected_target_head,
            "--language",
            language,
        ],
        cwd=target,
        environment=environment,
    )
    return result, parse_single_json(result=result)


def projectize(*, target: Path, label: str) -> None:
    """清除 fixture 的 active marker，并写入足够的目标项目事实。"""
    for relative_path in NON_PR_FILES:
        path = target / relative_path
        if relative_path == "capability_contract.json":
            path.write_text(
                data=json.dumps(
                    obj={"project": label},
                    ensure_ascii=False,
                    indent=2,
                ) + "\n",
                encoding="utf-8",
            )
            continue
        text = path.read_text(encoding="utf-8")
        text = text.replace(
            "<!-- project-fill: replace with verified project facts -->",
            f"Verified project facts for {label}.",
        )
        path.write_text(data=text, encoding="utf-8")


def file_tree(*, root: Path) -> dict[str, bytes]:
    """记录根目录下除 Git 元数据外的文件、目录和 symlink bytes。"""
    entries: dict[str, bytes] = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if relative.parts and relative.parts[0] == ".git":
            continue
        label = relative.as_posix()
        if path.is_symlink():
            entries[label] = f"SYMLINK:{os.readlink(path=path)}".encode("utf-8")
        elif path.is_file():
            entries[label] = path.read_bytes()
        elif path.is_dir():
            entries[f"{label}/"] = b"DIRECTORY"
    return entries


def repository_status(*, root: Path) -> str:
    """返回 porcelain 状态；非 Git 根以稳定 sentinel 表达。"""
    probe = run_command(
        args=["git", "-C", str(root), "rev-parse", "--show-toplevel"],
        cwd=root,
        environment=None,
    )
    if probe.returncode != 0:
        return "NOT_A_GIT_ROOT"
    return git(
        repo=root,
        args=["status", "--porcelain=v1", "--untracked-files=all"],
        check=True,
    )


def repository_snapshot(*, root: Path) -> tuple[dict[str, bytes], str]:
    """组合工作树 bytes 与 Git 状态，证明受测前置失败和 check 无副作用。"""
    return file_tree(root=root), repository_status(root=root)


def existing_core_paths(*, target: Path) -> set[str]:
    """返回存在或为 symlink 的核心路径，避免 broken symlink 被漏计。"""
    return {
        relative_path
        for relative_path in CORE_FILES
        if (target / relative_path).exists()
        or (target / relative_path).is_symlink()
    }


def assert_prepare_failure(
    *,
    target: Path,
    upstream: Path,
    expected_error: str,
    expected_core_paths: set[str],
) -> dict[str, Any]:
    """证明 prepare 失败摘要稳定，且调用前后 bytes 与 Git 状态完全一致。"""
    before = repository_snapshot(root=target)
    result, payload = run_prepare(
        target=target,
        upstream=upstream,
        language="zh",
    )
    assert result.returncode != 0
    assert payload["status"] == "failed"
    assert payload["error"] == expected_error
    assert repository_snapshot(root=target) == before
    assert existing_core_paths(target=target) == expected_core_paths
    return payload


def create_ready_case(
    *, root: Path, language: str
) -> tuple[Path, Path, dict[str, Any]]:
    """创建已 prepare 并完成 marker 清理的公共 check 场景。"""
    upstream, _ = create_upstream(root=root / "upstream", version="v1")
    target = init_repo(path=root / "target")
    prepared = prepare_success(
        target=target,
        upstream=upstream,
        language=language,
    )
    projectize(target=target, label=root.name)
    return upstream, target, prepared


def assert_check_failure(
    *,
    target: Path,
    upstream: Path,
    prepared: dict[str, Any],
    expected_error: str,
    expected_detail: str,
) -> dict[str, Any]:
    """断言公开 check 以稳定摘要拒绝指定无效终态。"""
    result, payload = run_check(
        target=target,
        upstream=upstream,
        language=prepared["language"],
        upstream_sha=prepared["upstream_sha"],
        expected_target_head=prepared["target_head"],
        environment=None,
    )
    assert result.returncode != 0
    assert payload["status"] == "failed"
    assert payload["error"] == expected_error
    assert expected_detail in payload["detail"]
    return payload


def append_bad_whitespace(*, path: Path) -> None:
    """向最终文件加入 Git 可识别的 trailing whitespace。"""
    with path.open(mode="a", encoding="utf-8", newline="") as stream:
        stream.write("bad trailing whitespace \n")


def create_installer_upstream(*, root: Path) -> Path:
    """把当前 canonical Skill 复制到 clean Git object，供安装器端到端读取。"""
    upstream = init_repo(path=root)
    destination = upstream / "zh/skills/workflow-docs-sync"
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        src=SKILL_ROOT,
        dst=destination,
        ignore=shutil.ignore_patterns("__pycache__", "*.py[cod]", ".DS_Store"),
    )
    commit_all(repo=upstream, message="canonical skill")
    return upstream


def seed_legacy_install(
    *, install_root: Path, obsolete_kinds: tuple[str, str]
) -> list[Path]:
    """建立多形态废弃 reviewer、外部目标和必须保留的无关 Skill。"""
    protected_targets: list[Path] = []
    for index, (platform, platform_root) in enumerate(PLATFORM_ROOTS):
        obsolete = install_root / platform_root / OBSOLETE_SKILL
        obsolete.parent.mkdir(parents=True, exist_ok=True)
        kind = obsolete_kinds[index]
        if kind == "directory":
            obsolete.mkdir()
            (obsolete / "legacy.bin").write_bytes(data=b"legacy reviewer\x00")
        elif kind == "file":
            obsolete.write_bytes(data=b"legacy reviewer file\x00")
        elif kind == "symlink":
            protected = (
                install_root.parent
                / f"{install_root.name}-{platform}-protected.bin"
            )
            protected.write_bytes(data=b"protected target\x00")
            obsolete.symlink_to(target=protected)
            protected_targets.append(protected)
        else:
            raise ValueError(f"未知废弃路径形态: {kind}")
        unrelated = install_root / platform_root / "unrelated-skill"
        unrelated.mkdir(parents=True, exist_ok=True)
        (unrelated / "keep.bin").write_bytes(data=b"keep unrelated\x00")
    return protected_targets


def run_user_install(
    *, upstream: Path, home: Path
) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    """在临时 HOME 执行公开 user-scope 安装流程。"""
    result = run_command(
        args=[
            sys.executable,
            str(INSTALLER),
            "--scope",
            "user",
            "--upstream-dir",
            str(upstream),
        ],
        cwd=REPO_ROOT,
        environment={"HOME": str(home)},
    )
    return result, parse_single_json(result=result)


def run_repo_install(
    *, upstream: Path, target: Path
) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    """在 clean 目标仓库执行公开 repo-scope 安装流程。"""
    result = run_command(
        args=[
            sys.executable,
            str(INSTALLER),
            "--scope",
            "repo",
            "--target-repo",
            str(target),
            "--upstream-dir",
            str(upstream),
        ],
        cwd=REPO_ROOT,
        environment=None,
    )
    return result, parse_single_json(result=result)


def assert_installed(*, install_root: Path) -> None:
    """验证双平台安装、Claude 显式调用边界与精确清理结果。"""
    for platform, platform_root in PLATFORM_ROOTS:
        installed = install_root / platform_root / "workflow-docs-sync"
        skill_text = (installed / "SKILL.md").read_text(encoding="utf-8")
        if platform == "claude":
            assert skill_text.count("disable-model-invocation: true") == 1
        else:
            assert "disable-model-invocation: true" not in skill_text
        obsolete = install_root / platform_root / OBSOLETE_SKILL
        assert not obsolete.exists() and not obsolete.is_symlink()
        assert (
            install_root / platform_root / "unrelated-skill/keep.bin"
        ).read_bytes() == b"keep unrelated\x00"
    assert not list(install_root.rglob(".source.json"))


def replace_active_markers(*, value: Any) -> Any:
    """模拟目标项目替换全部 active marker，保留 JSON 其余分发结构。"""
    if isinstance(value, dict):
        return {
            key: replace_active_markers(value=item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [replace_active_markers(value=item) for item in value]
    if isinstance(value, str) and any(
        marker in value for marker in ACTIVE_MARKERS
    ):
        return "verified project fact"
    return value


def production_text_files(*, root: Path) -> list[Path]:
    """列出全仓当前生产文本，排除测试自身、历史决策和生成缓存。"""
    excluded = {
        root / "tests/test_workflow_docs_sync.py",
        root / "zh/docs/development_workflow/decisions.md",
    }
    files: list[Path] = []
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if not path.is_file():
            continue
        if any(
            part in {".git", ".pytest_cache", "__pycache__"}
            for part in relative.parts
        ):
            continue
        if path in excluded:
            continue
        try:
            path.read_bytes().decode("utf-8")
        except UnicodeDecodeError:
            # 机器标识符约束的是当前生产文本；二进制资产不是散文或控制面。
            continue
        files.append(path)
    return sorted(files)


def is_installable_skill_entry(*, path: Path) -> bool:
    """返回安装器会复制的 Skill 条目，排除其明确忽略的生成缓存。"""
    return (
        "__pycache__" not in path.parts
        and path.name != ".DS_Store"
        and path.suffix not in {".pyc", ".pyd", ".pyo"}
    )


def test_scenario_1_success_path(tmp_path: Path) -> None:
    """场景 1：双语 prepare、项目化、固定 object 和连续只读 check。"""
    for language in ("zh", "en"):
        case_root = tmp_path / language
        upstream, upstream_sha = create_upstream(
            root=case_root / "upstream",
            version="v1",
        )
        target = init_repo(path=case_root / "target")
        prepared = prepare_success(
            target=target,
            upstream=upstream,
            language=language,
        )
        assert prepared["installed"] == list(CORE_FILES)
        assert prepared["existing"] == []
        assert prepared["upstream_sha"] == upstream_sha

        # 已有文档必须保持用户 bytes，prepare 不得用模板覆盖已核实项目内容。
        custom = "# Project facts\n\nVerified existing architecture.\n"
        (target / "architecture.md").write_text(
            data=custom,
            encoding="utf-8",
        )
        repeated_prepare = prepare_success(
            target=target,
            upstream=upstream,
            language=language,
        )
        assert repeated_prepare["installed"] == []
        assert repeated_prepare["existing"] == list(CORE_FILES)
        assert (target / "architecture.md").read_text(encoding="utf-8") == custom

        # 新目标在上游 dirty 时仍必须收到 HEAD object，而不是 working-tree bytes。
        committed_architecture = git(
            repo=upstream,
            args=["show", f"{upstream_sha}:{language}/architecture.md"],
            check=True,
        )
        (upstream / language / "architecture.md").write_text(
            data="# Dirty upstream bytes\n",
            encoding="utf-8",
        )
        dirty_target = init_repo(path=case_root / "dirty-target")
        dirty_prepared = prepare_success(
            target=dirty_target,
            upstream=upstream,
            language=language,
        )
        assert dirty_prepared["upstream_sha"] == upstream_sha
        assert (
            dirty_target / "architecture.md"
        ).read_text(encoding="utf-8") == committed_architecture

        # 项目化后连续 check 必须同值且不产生仓库副作用。
        projectize(target=target, label=f"scenario-1-{language}")
        before = repository_snapshot(root=target)
        first_result, first_payload = run_check(
            target=target,
            upstream=upstream,
            language=language,
            upstream_sha=prepared["upstream_sha"],
            expected_target_head=prepared["target_head"],
            environment=None,
        )
        middle = repository_snapshot(root=target)
        second_result, second_payload = run_check(
            target=target,
            upstream=upstream,
            language=language,
            upstream_sha=prepared["upstream_sha"],
            expected_target_head=prepared["target_head"],
            environment=None,
        )
        assert first_result.returncode == second_result.returncode == 0
        assert first_payload == second_payload
        assert before == middle == repository_snapshot(root=target)

        # 新 object 删除承重 marker 后，旧 object 仍通过而新 object 必须失败。
        (upstream / language / "architecture.md").write_text(
            data=f"# {language.upper()} marker-less v2\n",
            encoding="utf-8",
        )
        new_sha = commit_all(repo=upstream, message="marker-less templates v2")
        assert new_sha != upstream_sha
        pinned_result, pinned_payload = run_check(
            target=target,
            upstream=upstream,
            language=language,
            upstream_sha=prepared["upstream_sha"],
            expected_target_head=prepared["target_head"],
            environment=None,
        )
        assert pinned_result.returncode == 0, pinned_payload
        assert pinned_payload["upstream_sha"] == upstream_sha
        new_result, new_payload = run_check(
            target=target,
            upstream=upstream,
            language=language,
            upstream_sha=new_sha,
            expected_target_head=prepared["target_head"],
            environment=None,
        )
        assert new_result.returncode != 0
        assert new_payload["error"] == (
            "固定上游模板违反 source marker invariant"
        )
        assert new_sha in new_payload["detail"]
        assert f"{language}/architecture.md" in new_payload["detail"]

    # language 必须真实选择 source tree；不能把 prepare 的 zh 身份机械回显成 en PASS。
    language_root = tmp_path / "wrong-language"
    language_upstream = init_repo(path=language_root / "upstream")
    write_templates(upstream=language_upstream, version="v1")
    (language_upstream / "en/architecture.md").write_text(
        data="# EN marker-less source\n",
        encoding="utf-8",
    )
    language_sha = commit_all(repo=language_upstream, message="language fixture")
    language_target = init_repo(path=language_root / "target")
    language_prepared = prepare_success(
        target=language_target,
        upstream=language_upstream,
        language="zh",
    )
    assert language_prepared["upstream_sha"] == language_sha
    projectize(target=language_target, label="wrong-language")
    wrong_result, wrong_payload = run_check(
        target=language_target,
        upstream=language_upstream,
        language="en",
        upstream_sha=language_sha,
        expected_target_head=language_prepared["target_head"],
        environment=None,
    )
    assert wrong_result.returncode != 0
    assert wrong_payload["error"] == (
        "固定上游模板违反 source marker invariant"
    )
    assert "en/architecture.md" in wrong_payload["detail"]

    # unrelated object store 中即使 SHA 存在，也不能在没有九份 source path 时通过。
    unrelated = init_repo(path=language_root / "unrelated")
    unrelated_sha = git(
        repo=unrelated,
        args=["rev-parse", "HEAD"],
        check=True,
    ).strip()
    unrelated_result, unrelated_payload = run_check(
        target=language_target,
        upstream=unrelated,
        language="zh",
        upstream_sha=unrelated_sha,
        expected_target_head=language_prepared["target_head"],
        environment=None,
    )
    assert unrelated_result.returncode != 0
    assert unrelated_payload["error"] == "无法读取固定上游模板"
    assert "zh/architecture.md" in unrelated_payload["detail"]


def test_scenario_2_prepare_safe_failures(tmp_path: Path) -> None:
    """场景 2：prepare 的各类前置失败都不改变目标 bytes 或状态。"""
    upstream, _ = create_upstream(
        root=tmp_path / "upstream",
        version="v1",
    )

    # 真实仓库的子目录不能冒充根目录，且其 bytes 与父仓库状态必须保持不变。
    non_root_repo = init_repo(path=tmp_path / "non-root-repo")
    non_git = non_root_repo / "nested"
    non_git.mkdir()
    (non_git / "note.txt").write_text(data="nested directory\n", encoding="utf-8")
    assert_prepare_failure(
        target=non_git,
        upstream=upstream,
        expected_error="目标仓库必须是 Git 根目录",
        expected_core_paths=set(),
    )

    # allowlist 外 dirty path 必须在任何核心模板落盘前终止。
    outside_dirty = init_repo(path=tmp_path / "outside-dirty")
    (outside_dirty / "rogue.txt").write_text(data="rogue\n", encoding="utf-8")
    dirty_payload = assert_prepare_failure(
        target=outside_dirty,
        upstream=upstream,
        expected_error="存在同步范围外的 dirty path",
        expected_core_paths=set(),
    )
    assert "rogue.txt" in dirty_payload["detail"]

    # symlink 预检必须保留链接目标，并阻止其余八份模板形成部分安装。
    symlink_target = init_repo(path=tmp_path / "symlink-target")
    outside = tmp_path / "outside.md"
    outside.write_text(data="outside bytes\n", encoding="utf-8")
    (symlink_target / "SOP.md").symlink_to(target=outside)
    assert_prepare_failure(
        target=symlink_target,
        upstream=upstream,
        expected_error="核心文档路径不能是符号链接",
        expected_core_paths={"SOP.md"},
    )
    assert outside.read_bytes() == b"outside bytes\n"

    # 当前 HEAD 的 legacy source 缺少 active marker 时必须在目标写入前失败。
    legacy_upstream = init_repo(path=tmp_path / "legacy-upstream")
    write_templates(upstream=legacy_upstream, version="legacy")
    (legacy_upstream / "zh/architecture.md").write_text(
        data="# Legacy marker-less architecture\n",
        encoding="utf-8",
    )
    commit_all(repo=legacy_upstream, message="legacy marker-less source")
    legacy_target = init_repo(path=tmp_path / "legacy-target")
    legacy_payload = assert_prepare_failure(
        target=legacy_target,
        upstream=legacy_upstream,
        expected_error="固定上游模板违反 source marker invariant",
        expected_core_paths=set(),
    )
    assert "zh/architecture.md" in legacy_payload["detail"]

    # Git object 的原始 bytes 不是 UTF-8 时也必须在目标写入前失败。
    binary_upstream = init_repo(path=tmp_path / "binary-upstream")
    write_templates(upstream=binary_upstream, version="binary")
    (binary_upstream / "zh/architecture.md").write_bytes(
        data=b"# invalid source\n\xff\n"
    )
    commit_all(repo=binary_upstream, message="invalid UTF-8 source")
    binary_target = init_repo(path=tmp_path / "binary-target")
    binary_payload = assert_prepare_failure(
        target=binary_target,
        upstream=binary_upstream,
        expected_error="固定上游模板不是有效 UTF-8",
        expected_core_paths=set(),
    )
    assert "zh/architecture.md" in binary_payload["detail"]


def test_scenario_3_check_rejects_invalid_final_states(tmp_path: Path) -> None:
    """场景 3：公开 check 拒绝身份、范围、内容、marker、JSON 和 whitespace 失败。"""
    root = tmp_path / "missing"
    upstream, target, prepared = create_ready_case(root=root, language="zh")
    (target / "architecture.md").unlink()
    assert_check_failure(
        target=target,
        upstream=upstream,
        prepared=prepared,
        expected_error="最终仓库检查失败",
        expected_detail="缺少必需文件: architecture.md",
    )

    for marker_index, marker in enumerate(ACTIVE_MARKERS):
        root = tmp_path / f"active-{marker_index}"
        upstream, target, prepared = create_ready_case(root=root, language="zh")
        (target / "architecture.md").write_text(
            data=f"project text\n{marker}\n",
            encoding="utf-8",
        )
        assert_check_failure(
            target=target,
            upstream=upstream,
            prepared=prepared,
            expected_error="最终仓库检查失败",
            expected_detail=marker,
        )

    for case_name, content, detail in (
        ("invalid-json", "{\n", "JSON 无效"),
        ("non-object-json", "[]\n", "顶层必须是 JSON object"),
    ):
        root = tmp_path / case_name
        upstream, target, prepared = create_ready_case(root=root, language="zh")
        (target / "capability_contract.json").write_text(
            data=content,
            encoding="utf-8",
        )
        assert_check_failure(
            target=target,
            upstream=upstream,
            prepared=prepared,
            expected_error="最终仓库检查失败",
            expected_detail=detail,
        )

    root = tmp_path / "empty"
    upstream, target, prepared = create_ready_case(root=root, language="zh")
    (target / "architecture.md").write_text(data="", encoding="utf-8")
    assert_check_failure(
        target=target,
        upstream=upstream,
        prepared=prepared,
        expected_error="最终仓库检查失败",
        expected_detail="文件为空",
    )

    root = tmp_path / "invalid-utf8"
    upstream, target, prepared = create_ready_case(root=root, language="zh")
    (target / "architecture.md").write_bytes(data=b"project\n\xff")
    assert_check_failure(
        target=target,
        upstream=upstream,
        prepared=prepared,
        expected_error="最终仓库检查失败",
        expected_detail="不是有效 UTF-8",
    )

    root = tmp_path / "check-symlink"
    upstream, target, prepared = create_ready_case(root=root, language="zh")
    outside = tmp_path / "check-outside.md"
    outside.write_text(data="external\n", encoding="utf-8")
    (target / "architecture.md").unlink()
    (target / "architecture.md").symlink_to(target=outside)
    assert_check_failure(
        target=target,
        upstream=upstream,
        prepared=prepared,
        expected_error="最终仓库检查失败",
        expected_detail="核心文档不能是符号链接",
    )

    # 同一 final-bytes 路径覆盖 untracked、staged、tracked 和 committed 四种 Git 状态。
    for state in ("untracked", "staged", "tracked", "committed"):
        root = tmp_path / f"whitespace-{state}"
        upstream, target, prepared = create_ready_case(root=root, language="zh")
        if state == "tracked":
            commit_all(repo=target, message="project docs")
            prepared = prepare_success(
                target=target,
                upstream=upstream,
                language="zh",
            )
        append_bad_whitespace(path=target / "architecture.md")
        if state == "staged":
            git(repo=target, args=["add", "architecture.md"], check=True)
        elif state == "committed":
            commit_all(repo=target, message="bad whitespace")
            prepared = prepare_success(
                target=target,
                upstream=upstream,
                language="zh",
            )
        assert_check_failure(
            target=target,
            upstream=upstream,
            prepared=prepared,
            expected_error="最终仓库检查失败",
            expected_detail="trailing whitespace",
        )

    # ignored core path 仍属于 final bytes；Git-equivalent 检查也必须拒绝 conflict marker。
    root = tmp_path / "ignored-conflict-marker"
    upstream, target, prepared = create_ready_case(root=root, language="zh")
    (target / ".gitignore").write_text(
        data="architecture.md\n",
        encoding="utf-8",
    )
    (target / "architecture.md").write_text(
        data="<<<<<<< ours\nproject fact\n=======\nother fact\n>>>>>>> theirs\n",
        encoding="utf-8",
    )
    ignored_status = git(
        repo=target,
        args=["status", "--porcelain=v1", "--ignored"],
        check=True,
    )
    assert "!! architecture.md" in ignored_status
    assert_check_failure(
        target=target,
        upstream=upstream,
        prepared=prepared,
        expected_error="最终仓库检查失败",
        expected_detail="leftover conflict marker",
    )

    root = tmp_path / "gitignore-whitespace"
    upstream, target, prepared = create_ready_case(root=root, language="zh")
    (target / ".gitignore").write_text(data="*.local \n", encoding="utf-8")
    assert_check_failure(
        target=target,
        upstream=upstream,
        prepared=prepared,
        expected_error="最终仓库检查失败",
        expected_detail="trailing whitespace",
    )

    root = tmp_path / "gitignore-invalid-utf8"
    upstream, target, prepared = create_ready_case(root=root, language="zh")
    (target / ".gitignore").write_bytes(data=b"*.local\n\xff\n")
    assert_check_failure(
        target=target,
        upstream=upstream,
        prepared=prepared,
        expected_error="最终仓库检查失败",
        expected_detail=".gitignore: 不是有效 UTF-8",
    )

    # index 中为 bad whitespace、worktree 为 clean 时存在两个发布候选，必须先统一。
    root = tmp_path / "index-worktree-split"
    upstream, target, _ = create_ready_case(root=root, language="zh")
    commit_all(repo=target, message="project docs")
    prepared = prepare_success(
        target=target,
        upstream=upstream,
        language="zh",
    )
    architecture = target / "architecture.md"
    clean_bytes = architecture.read_bytes()
    append_bad_whitespace(path=architecture)
    git(repo=target, args=["add", "architecture.md"], check=True)
    architecture.write_bytes(data=clean_bytes)
    assert "MM architecture.md" in repository_status(root=target)
    assert_check_failure(
        target=target,
        upstream=upstream,
        prepared=prepared,
        expected_error="editable path 存在 index/worktree 分叉",
        expected_detail="MM architecture.md",
    )

    # 目标仓库 attributes 不得关闭 checker 对 final Markdown 的 whitespace 规则。
    root = tmp_path / "attributes-cannot-disable-whitespace"
    upstream, target, _ = create_ready_case(root=root, language="zh")
    (target / ".gitattributes").write_text(
        data="*.md -whitespace\n",
        encoding="utf-8",
    )
    commit_all(repo=target, message="disable repository whitespace attributes")
    prepared = prepare_success(
        target=target,
        upstream=upstream,
        language="zh",
    )
    append_bad_whitespace(path=target / "architecture.md")
    assert_check_failure(
        target=target,
        upstream=upstream,
        prepared=prepared,
        expected_error="最终仓库检查失败",
        expected_detail="trailing whitespace",
    )

    # 合法的用户级 attributes 也不得把同一份 bad final bytes 改判为通过。
    root = tmp_path / "global-attributes-cannot-disable-whitespace"
    upstream, target, prepared = create_ready_case(root=root, language="zh")
    home = root / "home"
    home.mkdir()
    global_attributes = root / "global_attributes"
    global_attributes.write_text(data="*.md -whitespace\n", encoding="utf-8")
    global_config = home / ".gitconfig"
    isolated_environment = {
        "GIT_CONFIG_GLOBAL": str(global_config),
        "HOME": str(home),
        "XDG_CONFIG_HOME": str(home / "xdg"),
    }
    config_result = run_command(
        args=[
            "git",
            "config",
            "--global",
            "core.attributesFile",
            str(global_attributes),
        ],
        cwd=root,
        environment=isolated_environment,
    )
    assert config_result.returncode == 0, config_result.stderr
    append_bad_whitespace(path=target / "architecture.md")
    check_result, check_payload = run_check(
        target=target,
        upstream=upstream,
        language=prepared["language"],
        upstream_sha=prepared["upstream_sha"],
        expected_target_head=prepared["target_head"],
        environment=isolated_environment,
    )
    assert check_result.returncode != 0
    assert check_payload["error"] == "最终仓库检查失败"
    assert "trailing whitespace" in check_payload["detail"]

    root = tmp_path / "head-change"
    upstream, target, prepared = create_ready_case(root=root, language="zh")
    commit_all(repo=target, message="unexpected head")
    assert_check_failure(
        target=target,
        upstream=upstream,
        prepared=prepared,
        expected_error="目标 HEAD 已变化",
        expected_detail="期望",
    )

    root = tmp_path / "outside-dirty"
    upstream, target, prepared = create_ready_case(root=root, language="zh")
    (target / "rogue.txt").write_text(data="rogue\n", encoding="utf-8")
    assert_check_failure(
        target=target,
        upstream=upstream,
        prepared=prepared,
        expected_error="存在同步范围外的 dirty path",
        expected_detail="rogue.txt",
    )


def test_scenario_4_installer_end_to_end(tmp_path: Path) -> None:
    """场景 4：user/repo、Codex/Claude、精确清理和重复安装形成完整闭环。"""
    upstream = create_installer_upstream(root=tmp_path / "upstream")

    # User scope 不依赖目标 Git；第二次运行必须产生相同安装 bytes。
    home = tmp_path / "home"
    home.mkdir()
    protected_targets = seed_legacy_install(
        install_root=home,
        obsolete_kinds=("symlink", "file"),
    )
    user_result, user_payload = run_user_install(upstream=upstream, home=home)
    assert user_result.returncode == 0, user_payload
    assert user_payload["scope"] == "user"
    assert user_payload["removed_obsolete"] == [
        str(home / platform_root / OBSOLETE_SKILL)
        for _, platform_root in PLATFORM_ROOTS
    ]
    assert_installed(install_root=home)
    for protected in protected_targets:
        assert protected.read_bytes() == b"protected target\x00"
    user_snapshot = file_tree(root=home)
    repeated_result, repeated_payload = run_user_install(
        upstream=upstream,
        home=home,
    )
    assert repeated_result.returncode == 0, repeated_payload
    assert repeated_payload["removed_obsolete"] == []
    assert file_tree(root=home) == user_snapshot

    # Repo scope 先提交安装结果，再证明重复安装不制造任何 Git diff。
    target = init_repo(path=tmp_path / "target")
    seed_legacy_install(
        install_root=target,
        obsolete_kinds=("directory", "directory"),
    )
    commit_all(repo=target, message="legacy skills")
    repo_result, repo_payload = run_repo_install(
        upstream=upstream,
        target=target,
    )
    assert repo_result.returncode == 0, repo_payload
    assert repo_payload["scope"] == "repo"
    assert_installed(install_root=target)
    commit_all(repo=target, message="installed canonical skill")
    repo_snapshot = repository_snapshot(root=target)
    repeated_result, repeated_payload = run_repo_install(
        upstream=upstream,
        target=target,
    )
    assert repeated_result.returncode == 0, repeated_payload
    assert repeated_payload["removed_obsolete"] == []
    assert repository_snapshot(root=target) == repo_snapshot


def test_scenario_5_repository_distribution_contract() -> None:
    """场景 5：真实仓库 bytes、Skill 结构、语境边界与旧控制面保持可分发。"""
    root_agents = REPO_ROOT / "AGENTS.md"
    assert root_agents.is_file() and not root_agents.is_symlink()

    skill_symlinks = sorted(
        path.relative_to(SKILL_ROOT).as_posix()
        for path in SKILL_ROOT.rglob("*")
        if is_installable_skill_entry(path=path) and path.is_symlink()
    )
    assert skill_symlinks == []
    actual_skill_directories = sorted(
        path.relative_to(SKILL_ROOT).as_posix()
        for path in SKILL_ROOT.rglob("*")
        if is_installable_skill_entry(path=path) and path.is_dir()
    )
    assert actual_skill_directories == ["agents", "evals", "scripts"]
    actual_skill_files = sorted(
        path.relative_to(SKILL_ROOT).as_posix()
        for path in SKILL_ROOT.rglob("*")
        if is_installable_skill_entry(path=path) and path.is_file()
    )
    assert actual_skill_files == [
        "SKILL.md",
        "agents/openai.yaml",
        "evals/README.md",
        "scripts/sync_docs.py",
    ]

    # 真实模板只通过直接 bytes 与 Git CLI 校验，避免重新耦合生产 helper。
    for language in ("zh", "en"):
        actual_templates = {
            relative_path
            for relative_path in CORE_FILES
            if (REPO_ROOT / language / relative_path).is_file()
        }
        assert actual_templates == set(CORE_FILES)
        for relative_path in CORE_FILES:
            path = REPO_ROOT / language / relative_path
            assert path.is_file() and not path.is_symlink()
            content = path.read_bytes()
            text = content.decode("utf-8")
            assert content
            assert b"\r" not in content
            whitespace = run_command(
                args=[
                    "git",
                    "diff",
                    "--no-index",
                    "--check",
                    "--",
                    os.devnull,
                    str(path),
                ],
                cwd=REPO_ROOT,
                environment=None,
            )
            assert whitespace.returncode in (0, 1), (
                whitespace.stdout + whitespace.stderr
            )
            assert whitespace.stdout == ""
            assert whitespace.stderr == ""
            if relative_path in NON_PR_FILES:
                assert any(marker in text for marker in ACTIVE_MARKERS), (
                    "equality removal depends on an active marker in "
                    f"{language}/{relative_path}"
                )

    # 固定文档锚点不得在 marker 清零后偷偷保留泛化测试结论。
    instructional_metadata = (
        "目标项目存在本地 alignment test 时，必须登记其真实测试锚点。",
        "The target project must register its own local alignment test when one exists.",
    )
    for language in ("zh", "en"):
        contract_path = REPO_ROOT / language / "capability_contract.json"
        contract = json.loads(s=contract_path.read_text(encoding="utf-8"))
        projectized = replace_active_markers(value=contract)
        serialized = json.dumps(obj=projectized, ensure_ascii=False)
        assert not any(marker in serialized for marker in ACTIVE_MARKERS)
        assert not any(text in serialized for text in instructional_metadata)
        documents = projectized["contracts"]["documents"]
        by_anchor = {entry["anchor_id"]: entry for entry in documents}
        for anchor in ("DOC.interact", "DOC.business_user_guide"):
            assert anchor in by_anchor
            assert not {
                "test_anchor",
                "test_status",
                "untested_reason",
            } & set(by_anchor[anchor])

    # 机械兜底只覆盖本次真实误植过的八份下游模板与五个精确 token。
    internal_context_tokens = (
        "disposable clone",
        "同步工作树",
        "synchronized worktree",
        "共享工作树",
        "shared worktree",
        "fresh-context",
        "blind-first",
        "通用 GitHub 发布能力",
        "general GitHub publishing capability",
    )
    guarded_templates = (
        "AGENTS.md",
        "TESTING.md",
        "PR_Checklist.md",
        ".github/pull_request_template.md",
    )
    context_hits: list[str] = []
    for language in ("zh", "en"):
        for relative_path in guarded_templates:
            path = REPO_ROOT / language / relative_path
            text = path.read_text(encoding="utf-8")
            for token in internal_context_tokens:
                if token in text:
                    context_hits.append(f"{language}/{relative_path}: {token}")
    assert context_hits == []

    # 窄修只撤回 WDS 实现，主执行者、证据与只读审查等通用协作原则必须保留。
    collaboration_contract = {
        "zh": (
            "主执行者对最终判断、最终产物和最终写入结果负责",
            "受委派结果必须经过审阅与合成",
            "不强制 Agent 数量或固定调度顺序",
            "协作者结论、投票或共识不等于证据",
            "调查与审查任务默认只读",
        ),
        "en": (
            "The primary executor owns final judgments, deliverables, and writes",
            "delegated results must be reviewed",
            "do not require a fixed agent count",
            "Agreement, voting, or consensus is not evidence",
            "Investigation and review tasks are read-only by default",
        ),
    }
    for language, statements in collaboration_contract.items():
        text = (REPO_ROOT / language / "AGENTS.md").read_text(encoding="utf-8")
        assert all(statement in text for statement in statements)

    deleted_paths = (
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
        "zh/skills/workflow-docs-sync/references",
        "zh/skills/workflow-docs-sync-review",
        "tests/test_workflow_sync_skill.py",
        "tests/test_sync_coding_workflow.py",
    )
    assert [
        path
        for path in deleted_paths
        if (REPO_ROOT / path).exists() or (REPO_ROOT / path).is_symlink()
    ] == []

    machine_identifiers = (
        "active_mode",
        "completed_modes",
        "run.json",
        "skill_runtime",
        "skill_results",
        "SYNC_PR_BODY_MARKER",
        "sync:agent:start",
        "headRefOid",
    )
    identifier_hits: list[str] = []
    for path in production_text_files(root=REPO_ROOT):
        text = path.read_text(encoding="utf-8")
        for identifier in machine_identifiers:
            if identifier in text:
                identifier_hits.append(
                    f"{path.relative_to(REPO_ROOT)}: {identifier}"
                )
    assert identifier_hits == []

    help_result = run_command(
        args=[sys.executable, str(SYNC_SCRIPT), "--help"],
        cwd=REPO_ROOT,
        environment=None,
    )
    assert help_result.returncode == 0
    assert "{prepare,check}" in help_result.stdout
    for removed_command in (
        "start-pass",
        "finish-pass",
        "prepare-submit",
        "seal-submit",
        "finish-submit",
    ):
        assert removed_command not in help_result.stdout
