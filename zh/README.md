# 编程工作流操作入口

中文 | [English](../en/README.md)

本目录提供真正跨语言、跨框架、跨项目的中文核心模板、开发工作流和 canonical
`workflow-docs-sync` Skill。

## 一句话开始

在目标项目的 Codex 中复制这一句：

```text
用 $skill-installer 安装 https://github.com/wlvh/coding-workflow/tree/main/zh/skills/workflow-docs-sync，然后立即用 $workflow-docs-sync 同步当前项目文档并创建 draft PR；如果当前会话尚未注册新 Skill，直接读取安装器返回目录中的 SKILL.md 继续执行，不要停下来要求重启。
```

上述指令用于首次安装；已经安装后，在其他项目中直接要求 `$workflow-docs-sync` 同步当前项目文档并创建 draft PR。

用户不需要提供目标绝对路径、`zh` / `en`、分支名、上游 SHA 或安装路径，也不需要预先清理
目标工作树。系统 `$skill-installer` 成功时输出
`Installed workflow-docs-sync to <installed-skill-root>`；当前会话尚未注册 Skill 时，以该次成功
输出中的真实目录为准，完整读取其中的 `SKILL.md`，从同一目录解析脚本并在本轮继续。不要猜测
固定安装目录，也不要等待下一轮。

## 默认行为

- 目标仓库：显式本地路径优先，其次是显式 GitHub repository URL，否则使用 Codex 当前工作目录
  所属的 Git 根。安装 Skill 的来源 URL 不会被误当成目标。
- 语言：显式 `zh` / `en` 优先；否则中文请求使用 `zh`，其他语言请求使用 `en`。
- PR：明确说不创建 PR 时不创建；提到 PR、提 PR、创建/提交 PR 或 open/create pull request 时
  创建 draft PR；未提及则不创建。永不自动标记 Ready 或合并。
- 工作树：本地目标请求 PR 时，从调用时 committed HEAD 在仓库外创建 clean worktree 和唯一
  新分支。最终报告前逐 byte 比较调用前的 NUL status 与 staged entries，并只对调用前 status
  路径复核类型、mode、普通文件 SHA-256 或 symlink target，从而覆盖 dirty tracked 内容被同状态
  覆写的事故。Skill 不枚举、读取或哈希 ignored path；调用前已有 `.env`、venv、
  `node_modules`、cache 等 ignored 内容的并发变化属于明确剩余风险，由全部执行只发生在外部
  worktree 的路径隔离承担。GitHub URL 会物化真实 clone/fetch checkout，并报告原工作树保护
  `NOT_APPLICABLE`。

本地目标的最终报告会明确写：

```text
本次同步与 PR 基于调用时的 committed HEAD；原工作树中的未提交修改未进入调查或 PR。
```

仓库没有 commit 时会报告 `BLOCKER`。最终只用 Candidate、Tests、Review、Process deviations
和 Publication 五条独立事实；不会输出 Overall 或聚合 PASS/PARTIAL/FAIL。发布读回不可用或
确认不一致都会保留本地正确 candidate 并报告 `Publication: PR_BLOCKED`，但采用不同的恢复处置。

## 仓库自带安装器（可选）

以下是维护者或需要同时安装 Codex / Claude 副本时的可选路径，不是上述一句话入口。先克隆
canonical 仓库并确认这个上游 checkout clean；这里的 clean 要求不适用于待同步的目标项目：

```bash
git clone --depth 1 https://github.com/wlvh/coding-workflow.git
cd coding-workflow

git status --porcelain=v1 --untracked-files=all
python3 zh/scripts/install_skills.py --upstream-dir "$PWD"
```

`git status` 应无输出；如果有输出，停止安装并先检查 canonical checkout。成功 JSON 同时列出
`~/.agents/skills/workflow-docs-sync/` 与 `~/.claude/skills/workflow-docs-sync/` 两项 action。

需要把 Skill 作为目标项目的一部分审查和共享时，在 canonical checkout 根目录运行：

```bash
python3 zh/scripts/install_skills.py \
  --scope repo \
  --target-repo "/目标仓库绝对路径" \
  --upstream-dir "$PWD"
```

repo scope 的目标路径必须恰好是 clean Git 根目录；审查生成的 Git diff 后，再按目标项目政策
提交。两种 scope 都会覆盖已有同名 Skill，并精确移除废弃的 `workflow-docs-sync-review`，不会
保存来源状态或自动更新。Studio 也可直接加载 canonical `zh/skills/workflow-docs-sync/`。

## 同步边界

Skill 固定目标 HEAD 与上游 SHA，从当前代码、配置、测试、committed artifacts、可重复运行
结果和必要 Git 历史全量重建事实，再只做事实要求的最小文档改写。现有文档与上游模板都是
hypotheses，不是证据。

Architecture、Capability / User Behavior、Testing、Governance 是覆盖维度，不是固定 Agent
拓扑。主 Agent 是执行 worktree 的唯一写入者；测试环境由项目命令、副作用、CI 和项目政策
决定。

复核优先使用 fresh-context、blind-first independent reviewer。平台不能提供认知隔离时，
最终结果诚实标记 self-review。确定性 checker 只验证最终仓库状态，不证明调查、测试或复核
历史。

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

## 相关项目

本仓库负责**生产者侧**：Agent 如何从 committed code、config、tests 和 artifacts 重建仓库事实，
把改动限制在最小必要范围，并从隔离 clean worktree 交付可审核的 draft PR。

[acceptance-agent](https://github.com/wlvh/acceptance-agent) 负责**验收者侧**：一个独立验收方
如何仅凭规格、最终产物和测试证据做出 `accept` / `reject` / `request_evidence` 判断——它被有意
禁止读取 builder 的实现对话，因此无法继承 builder 的 framing。

作者：[github.com/wlvh](https://github.com/wlvh) · [huaweidata.com](https://huaweidata.com)
