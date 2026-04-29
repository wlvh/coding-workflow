# Workflow Docs Sync - 操作手册

本文档说明如何用脚本 + agent 自动完成目标项目的 workflow 文档 full reconcile。
它是 agent 执行 sync 的长期操作入口；每次运行后的具体工单由
`.coding_workflow/diffs/agent_workorder.md` 生成。独立 reviewer 的启动入口见：

- `scripts/sync_pr_review_system.md`：独立 reviewer 的薄启动入口；具体审核规则来自 PR body auto 区中的 `Sync Review Contract`。

---

## 1. 模式定义

```text
当前项目事实 + 最新 coding-workflow upstream 规则
→ 脚本生成本轮 evidence epoch
→ agent 只补 Repo Facts Map、项目化文档和语义证据
→ 脚本生成 PR body auto 区的 Sync Review Contract
→ 脚本校验 PR body auto 区与本轮 sync_state 一致
→ 独立 reviewer 按 Sync Review Contract 守语义质量门
```

---

## 2. 单入口命令

普通 sync：

```bash
curl -fsSL https://raw.githubusercontent.com/wlvh/coding-workflow/main/scripts/sync.sh | bash
```

最终机械校验：

```bash
curl -fsSL https://raw.githubusercontent.com/wlvh/coding-workflow/main/scripts/sync.sh | bash -s -- --final
```

`sync.sh` 是唯一人机入口。Python 的 `--update-pr-body` 和 `--check-final` 是内部 CLI，agent 不需要直接记。

---

## 3. 前置条件

- 当前目录位于目标项目的 git worktree 内。
- 项目代码、配置、测试变更已经 commit / stash / discard。
- 允许 dirty 的文件只有 contract 列出的核心文档、`.gitignore`、`PR_BODY.md` 和 `.coding_workflow/diffs/`。

原因：full reconcile 的 PR body 要描述当前已提交项目事实。如果混入未提交代码，reviewer 无法判断这些事实是否会进入主干。

---

## 4. 脚本产物

每次 sync 会清空并重建 `.coding_workflow/diffs/`：

| 文件 / 目录 | 用途 |
|---|---|
| `agent_workorder.md` | agent 首读工单，把脚本信号翻译成动作。 |
| `pr_body_skeleton.md` | 带 sentinel 的 sync PR body 骨架。 |
| `sync_state.json` | 本轮 evidence epoch 的结构化状态，只供本轮 update / final check 使用。 |
| `upstream_full/` | contract 列出的 upstream 原文，给当前 agent 本地读取。 |
| `upstream_vs_local/` | contract 列出的 upstream vs local diff。 |
| `full_reconcile_report.md` | 本轮 commit、raw URL 和 review signals。 |
| `installation_status.md` | contract 列出的核心文档机械状态表。 |

注意：`upstream_full/` 只降低当前 agent 的读取成本；PR body 仍必须保留 commit-pinned raw URL，供独立 reviewer 复验。

---

## 5. Agent 工作流

1. 运行普通 sync。
2. 读取 `.coding_workflow/diffs/agent_workorder.md`。
3. 如果 `PR_BODY.md` 不存在，用 `.coding_workflow/diffs/pr_body_skeleton.md` 初始化。
4. 填写 `PR_BODY.md` 中 agent-owned sentinel 区：
   - `repo_facts_map`
   - `full_document_reconcile`
   - `remaining_human_decisions`
5. 根据工单项目化 contract 列出的核心文档。
6. 重跑普通 sync，让脚本刷新 script-owned auto 区。
   原因：agent 修改核心文档和 PR body 的 agent-owned 区后，第一次 sync 生成的 `sync_state.json`、文档状态、dirty core files 和 auto 区可能已经过期。重跑 sync 会用最终工作区重新生成本轮 evidence epoch，并保留 agent-owned 区，避免 reviewer 看到旧证据。
7. 提交前运行 `sync.sh --final`。final 会重新生成 evidence epoch，但不会刷新 `PR_BODY.md`；如果第 6 步漏跑、auto 区被手改或引用旧 upstream commit，final 必须 fail fast。
8. 将 PR URL 交给独立 sync PR reviewer；reviewer 按 PR body auto 区的 `Sync Review Contract` 审核。

脚本只表达机械信号。`specialized` 只表示脚本未发现模板复制、模板残留或 TODO anchor；如 Repo Facts Map 或 upstream 新规则要求，仍可修改。

---

## 6. PR Body Sentinel 合同

`PR_BODY.md` 分两类区：

- script-owned auto 区：由当前 `sync_state.json` 渲染，agent 不手改。
- agent-owned 区：由 agent 填写，重跑 sync 时保留。
- sentinel 外非空内容：不允许。重跑 sync 会 fail fast，agent 必须把人工内容搬进 `repo_facts_map`、`full_document_reconcile` 或 `remaining_human_decisions`。

关键 sentinel 由脚本渲染到 `Sync Review Contract`，不要在 reviewer prompt 或人工文档里维护第二份清单。

`sync.sh --final` 会字节级比较 auto 区和当前 `sync_state.json` 的渲染结果；如果 agent 忘了重跑 sync、手改 auto 区、或者 auto 区引用旧 upstream commit，都会 fail fast。

---

## 7. Final Gate 能证明什么

`sync.sh --final` 能证明：

- `PR_BODY.md` auto 区与当前 `sync_state.json` 一致，其中包括 script-owned `Sync Review Contract`。
- contract 列出的 core files、upstream raw URL 和 upstream instruction raw URL 结构齐全。
- Repo Facts Map 有 contract 列出的标题。
- Full Document Reconcile 覆盖 contract 列出的核心文档。
- PR body 和核心文档不含模板 marker / TODO anchor。
- PR body 不再包含脚本生成的 `待补充` / `待判断` 占位符。
- 没有 `installed_template`、`template_copy_requires_specialization`、`partially_specialized` 这类未处理机械状态。

`sync.sh --final` 不能证明：

- Repo Facts Map 的证据是否真实。
- 项目化文案是否准确。
- upstream 新规则是否被正确投影到所有本地文档。

这些质量门由 PR body auto 区的 `Sync Review Contract` 定义，并由 `scripts/sync_pr_review_system.md` 启动的独立 reviewer 执行。

---

## 8. 提交规则

只提交长期文件和必要测试。不要提交：

- `.coding_workflow/diffs/`
- 临时 clone 目录

`PR_BODY.md` 按目标项目规则处理：如果目标项目把它作为本地临时草稿，就不要提交；如果目标项目历史上已经跟踪它，必须遵循该项目自己的 PR 规则。

---

## 9. sync PR review

把 PR URL 给独立 reviewer，并使用：

```text
你是 sync PR reviewer。请按 PR body auto 区的 `Sync Review Contract` 审核 PR <URL>，并使用 PR body 中 commit-pinned 的 reviewer prompt raw URL 对齐输出格式。

特别注意：你必须打开 contract 列出的全部 raw GitHub URL，并对照 PR head 上 contract 列出的核心文档做 full reconcile cross-check。
```

通过条件：

- PASS：进入用户视角验收。
- WARN：在 PR body 说明为什么可接受，再进入用户视角验收。
- BLOCKER：修复后重跑 sync，刷新 PR body，再重新 review。
