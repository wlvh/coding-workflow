# Workflow Docs Sync - 操作手册

本文档说明如何用全量模式同步目标项目的 workflow 文档体系。设计哲学和审核规则见：

- `scripts/sync_workflow_docs.md`：执行 full reconcile 的 agent 工作流。
- `scripts/sync_pr_review_system.md`：审核 full reconcile PR 的 reviewer 规则。

---

## 1. 模式定义

本工具只保留一种模式：

```text
full_reconcile
```

含义：

```text
当前项目事实 + 最新 coding-workflow upstream 规则
→ 重新形成 Repo Facts Map
→ 全量检查 9 个核心文档
→ 生成本次 PR review 证据
```

本工具不维护 `.coding_workflow/source.json`，也不记录“上次同步到哪个项目 commit”。目标项目的日常文档维护由项目自身的 `AGENTS.md` / `TESTING.md` / `PR_Checklist.md` / `architecture.md` 等长期文件承担；sync 只负责在需要时全量复核当前状态。

---

## 2. 适用场景

| 场景 | 何时用 | 结果 |
|---|---|---|
| 首次接入 | 目标项目第一次引入 workflow 文档体系 | 安装缺失核心文档并要求项目化 |
| 周期复核 | 怀疑项目文档已漂移 | 重新审当前项目事实和 9 个核心文档 |
| upstream 升级吸收 | coding-workflow 新增或修改规则 | 用最新 upstream 规则全量检查本地文档 |
| PR review 前证据刷新 | sync PR 打开前或修复后 | 生成最新 `.coding_workflow/diffs/` 证据 |

---

## 3. 前置条件

- 当前目录位于目标项目的 git worktree 内。
- 项目代码、配置、测试变更已经 commit / stash / discard。
- 允许 dirty 的文件只有 9 个核心文档、`.gitignore`、`PR_BODY.md` 和 `.coding_workflow/diffs/`。

原因：full reconcile 的 PR body 要描述当前已提交项目事实。如果混入未提交代码，reviewer 无法判断这些事实是否会进入主干。

---

## 4. 运行命令

```bash
curl -fsSL https://raw.githubusercontent.com/wlvh/coding-workflow/main/scripts/sync.sh | bash
```

## 5. 预期输出

```text
sync mode: full_reconcile
upstream:  <12 char sha>
project:   <12 char sha>

Read these in order:
  1. .coding_workflow/diffs/full_reconcile_report.md
  2. .coding_workflow/diffs/installation_status.md
  3. .coding_workflow/diffs/upstream_vs_local/

Then read these upstream instructions pinned to upstream_resolved_commit:
  - scripts/sync_workflow_docs.md: https://raw.githubusercontent.com/wlvh/coding-workflow/<full sha>/scripts/sync_workflow_docs.md
  - scripts/sync_pr_review_system.md: https://raw.githubusercontent.com/wlvh/coding-workflow/<full sha>/scripts/sync_pr_review_system.md
First action: produce a full Repo Facts Map in PR body.
The PR will be reviewed by an LLM using the pinned sync PR review system URL above.

Sync Summary fields for PR body (transcribe verbatim):
  - sync mode: full_reconcile
  - upstream_resolved_commit: <full sha>
  - project_head_commit: <full sha>
  - evidence_source: working_tree
  - core files checked: 9

Working Tree State at Sync Time:
  - project_head_commit is the base commit; evidence content is read from the working tree.
  - evidence_source: working_tree
  - dirty core files (working tree differs from HEAD):
    - none / <core file path>
```

---

## 6. 运行后读取顺序

1. `.coding_workflow/diffs/full_reconcile_report.md`
   - 本次 upstream commit、项目 HEAD、raw URL、review signals。
2. `.coding_workflow/diffs/installation_status.md`
   - 9 个核心文件的状态。
3. `.coding_workflow/diffs/upstream_vs_local/`
   - 最新 upstream 模板和本地文件的逐文件 diff。
4. `scripts/sync_workflow_docs.md`
   - 按 full reconcile 流程写 PR body 和修改文档。

---

## 7. PR Body 必填段

```markdown
## Repo Facts Map
(完整 10 项，每项必须有代码路径 / 文档路径 / 命令输出等证据)

## Sync Summary
- sync mode: full_reconcile
- upstream_resolved_commit:
- project_head_commit:
- evidence_source: working_tree
- core files checked: 9

## Working Tree State at Sync Time
(复制 full_reconcile_report.md 中的工作区状态；`project_head_commit` 是 sync 运行时 base commit，证据内容来自 working tree)

## Upstream Templates at Sync Time
(复制 sync 输出的 9 个 raw URL)

## Installation Status
(复制 installation_status.md 的 9 行表格)

## Full Document Reconcile
| 文件 | 当前判断 | 是否需要更新 | 证据 |
|---|---|---|---|

## Remaining Human Decisions
(没有也写 none)
```

---

## 8. 判定规则

- `installed_template`：sync 刚安装 upstream 模板，必须项目化后才能合并。
- `template_copy_requires_specialization`：文件与 upstream 完全一致，除 PR template 外必须解释或项目化。
- `partially_specialized`：仍有模板占位符，必须修。
- `inherited_upstream_allowed`：只允许 `.github/pull_request_template.md` 使用。
- `specialized`：看起来已项目化，但 reviewer 仍需对照 upstream raw URL 检查。

---

## 9. 提交规则

只提交长期文件和必要测试。不要提交：

- `.coding_workflow/diffs/`
- 临时 clone 目录

重跑 sync 会先清空旧的 `.coding_workflow/diffs/` 证据，再生成本次 full reconcile 的新证据。

`PR_BODY.md` 按当前仓库规则处理：如果目标项目把它作为本地临时草稿，就不要提交；如果目标项目历史上已经跟踪它，必须遵循该项目自己的 PR 规则。

---

## 10. sync PR review

把 PR URL 给独立 reviewer，并使用：

```text
你是 sync PR reviewer。请按 PR body 中 `scripts/sync_pr_review_system.md` 对应的 upstream_resolved_commit raw URL 规则审核 PR <URL>，输出格式严格按其 "## Sync PR Review" 模板。

特别注意：PR body 必须包含 9 个 upstream raw GitHub URL。你必须打开这些 URL，并对照 PR head 上的 9 个核心文档做 full reconcile cross-check。
```

通过条件：

- PASS：进入用户视角验收。
- WARN：在 PR body 说明为什么可接受，再进入用户视角验收。
- BLOCKER：修复后重跑 sync，刷新 PR body，再重新 review。
