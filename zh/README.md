# 编程工作流操作入口

中文 | [English](../en/README.md)

本目录提供真正跨语言、跨框架、跨项目的中文核心模板、开发工作流和 canonical
`workflow-docs-sync` Skill。

## Quick Start

用户只调用一次 Skill，只提供目标 Git 仓库、`zh` 或 `en`，以及成功后是否创建 draft PR：

```text
使用 $workflow-docs-sync 同步 /目标仓库绝对路径，语言 zh，结束后不要创建 draft PR。
```

Skill 固定目标 HEAD 与上游 SHA，从当前代码、配置、测试、committed artifacts、可重复运行
结果和必要 Git 历史全量重建事实，再只做事实要求的最小文档改写。现有文档与上游模板都是
hypotheses，不是证据。

Architecture、Capability / User Behavior、Testing、Governance 是覆盖维度，不是固定 Agent
拓扑。主 Agent 是目标工作区唯一写入者；测试环境由项目命令、副作用、CI 和项目政策决定。

复核优先使用 fresh-context、blind-first independent reviewer。平台不能提供认知隔离时，
最终结果诚实标记 self-review。确定性 checker 只验证最终仓库状态，不证明调查、测试或复核
历史。

## Skill 安装

Studio 可直接加载 canonical `zh/skills/workflow-docs-sync/`。个人或团队安装只复制这一个
Skill，不保存来源状态；安装器会在任何目标 mutation 前拒绝 symlink、无效 frontmatter 和
会被复制的 ignored source residue：

```bash
python3 zh/scripts/install_skills.py --upstream-dir <clean-canonical-checkout>
python3 zh/scripts/install_skills.py --scope repo \
  --target-repo <目标仓库> --upstream-dir <clean-canonical-checkout>
```

## Template Contract

Markdown project-fill slot 使用 `<!-- project-fill: ... -->`，JSON 使用
`__PROJECT_FILL__:` 字符串前缀。目标项目必须在最终 `check` 前替换或删除全部 active marker。
固定 source object 中的每份非 PR 模板必须至少保留一个 active marker，PR template 豁免；
模板不预设语言、框架、test runner、服务或默认分支。

## 维护者地图

- 下游模板：以 `zh/` 九份核心文件为中文语义源，同步派生 `en/` 同路径文件。
- canonical Skill：`zh/skills/workflow-docs-sync/`。
- 安装器：`zh/scripts/install_skills.py`。
- 入口 README：根 README 做摘要，`zh/README.md` 是中文维护入口，`en/README.md` 从中文派生。
- 开发工作流与决策：`zh/docs/development_workflow/README.md` 和 `decisions.md`；英文概览在
  `en/docs/development_workflow/README.md`。
- 场景测试：`tests/test_workflow_docs_sync.py`；具体测试约束以代码为准。
- GitHub 路径：根 `.github/` 只服务本仓库 CI/GitHub；`zh/.github/` 与 `en/.github/` 是下游
  模板源。

最短入口是 `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider`。以下是唯一完整
验证命令权威；它比较验证前后的普通与 ignored 状态，不使用 `git clean`：

```bash
set -euo pipefail
validation_tmp="$(mktemp -d /tmp/coding-workflow-validation.XXXXXX)"
trap 'rm -rf -- "$validation_tmp"' EXIT
before="$validation_tmp/status.before"
after="$validation_tmp/status.after"

git status --porcelain=v1 -z --untracked-files=all --ignored > "$before"
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider
PYTHONPYCACHEPREFIX="$validation_tmp/pycache" python3 -m py_compile \
  zh/skills/workflow-docs-sync/scripts/sync_docs.py zh/scripts/install_skills.py
PYTHONDONTWRITEBYTECODE=1 \
  python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" \
  zh/skills/workflow-docs-sync
git diff --check
PYTHONDONTWRITEBYTECODE=1 python3 zh/skills/workflow-docs-sync/scripts/sync_docs.py --help
git status --porcelain=v1 -z --untracked-files=all --ignored > "$after"

if ! cmp -s "$before" "$after"; then
  diff -u <(tr '\0' '\n' < "$before") <(tr '\0' '\n' < "$after") || true
  exit 1
fi
```

## 目录地图

- [AGENTS.md](AGENTS.md)：agent 权威入口、稳定模块地图与影响规则模板。
- [architecture.md](architecture.md)：系统目的、调用链、边界、状态与副作用模板。
- [capability_contract.json](capability_contract.json)：能力、边界、职责与行为锚点契约。
- [interact.md](interact.md)：用户可观察行为与验收模板。
- [docs/business_user_guide.md](docs/business_user_guide.md)：首次使用业务指南模板。
- [TESTING.md](TESTING.md)：测试入口、层级、隔离和证据模板。
- [PR_Checklist.md](PR_Checklist.md)：通用 PR todo 与目标项目发布政策边界。
- [SOP.md](SOP.md)：稳定标准流程入口模板。
- [.github/pull_request_template.md](.github/pull_request_template.md)：长期 PR body 结构。
- [docs/development_workflow/README.md](docs/development_workflow/README.md)：完整开发工作流。
- [docs/development_workflow/decisions.md](docs/development_workflow/decisions.md)：产品实现决策。
- [skills/workflow-docs-sync/](skills/workflow-docs-sync/)：canonical 单会话同步 Skill。
- [scripts/install_skills.py](scripts/install_skills.py)：单 Skill 双平台薄复制器。

## 路径与双语边界

安装模板时只剥离开头的 `zh/`；例如 `zh/docs/business_user_guide.md` 落到目标仓库的
`docs/business_user_guide.md`。根目录 `.github/` 是本仓库基础设施，不是下游模板源。

中文是语义锚点，英文是派生层。本 PR 新增或修改的双语模板、README 和 development
workflow 必须同一 PR 闭合；未触及历史决策的既有翻译状态不要求顺手改变。
