# Workflow Docs Sync - 操作手册

本文档说明如何用脚本 + agent 自动完成目标项目的 workflow 文档 full reconcile。
目标是把当前项目事实和最新 coding-workflow 规则对齐，最终由 PR reviewer 守语义质量门。
每次运行后的具体工单由 `.coding_workflow/diffs/agent_workorder.md` 生成。独立 reviewer 的启动入口见：

- `scripts/sync_pr_review_system.md`：独立 reviewer 的薄启动入口；具体审核规则来自 PR body auto 区中的 `Sync Review Contract`。

流程摘要：普通 sync 生成证据和工单；sync agent 补 PR body 和核心文档；
PR 提交 agent 运行 final gate 并创建或更新 PR；独立 reviewer 审查语义质量。

---

## 1. Quick Start：人在目标仓库里怎么完成 sync

运行位置：

- 在目标项目现有仓库目录里运行。

sync 运行前工作区契约：

- 首次运行普通 sync 前，不要混入代码、配置、测试等非 sync dirty 改动；脚本会拒绝这些 unmanaged dirty 文件并列出路径。
- 根据本轮工单重跑普通 sync 时，只允许 sync 管理的文件处于 dirty 状态：本轮 contract 列出的核心文档、`.gitignore`、`PR_BODY.md` 和 `.coding_workflow/diffs/`。

本轮权威入口：

- sync agent 的本轮动作、读取顺序和角色边界以 `.coding_workflow/diffs/agent_workorder.md` 为准。
- `PR_BODY.md` auto 区中的 `Sync Review Contract` 是独立 reviewer 的机械合同真相源。
- `scripts/sync_pr_review_system.md` 是 reviewer 系统 prompt；本手册中的 reviewer 短 prompt 只负责启动审查。
- PR 提交 agent 才在提交前运行 final gate；final gate 只证明机械一致性。

1. 在目标项目现有仓库目录里运行普通 sync。

   ```bash
   curl -fsSL https://raw.githubusercontent.com/wlvh/coding-workflow/main/scripts/sync.sh | bash
   ```

   这一步会生成本轮 sync 工单和证据目录。本轮具体读什么、改什么，以
   `.coding_workflow/diffs/agent_workorder.md` 为准；不要提交 `.coding_workflow/diffs/`。
   如果已有 `PR_BODY.md` 不是 sync sentinel 草稿，普通 sync 会把旧内容保存到
   `.coding_workflow/diffs/pr_body_previous.md`，再替换为本轮 sync PR body。
   `pr_body_previous.md` 属于 scratch 证据，下次普通 sync 会重建 `.coding_workflow/diffs/`；
   sync agent 如需保留旧草稿内容，必须先检查并迁入 PR body 的 agent-owned 区。

2. 把下面的短 prompt 发给目标项目里的 agent，让 agent 接手执行工单：

   ```text
   当前仓库已经运行过普通 sync。请以本轮 `.coding_workflow/diffs/agent_workorder.md`
   为 workflow docs sync 的权威工单，并读取 `.coding_workflow/diffs/agent_workorder.md`、
   `.coding_workflow/diffs/pr_body_skeleton.md`、`.coding_workflow/diffs/full_reconcile_report.md`、
   `.coding_workflow/diffs/installation_status.md`、`.coding_workflow/diffs/upstream_full/`
   和 `.coding_workflow/diffs/upstream_vs_local/`。

   如果 `PR_BODY.md` 不存在，用 `.coding_workflow/diffs/pr_body_skeleton.md` 初始化；
   然后只补齐 PR_BODY.md 的 agent-owned 区，不要手改 script-owned auto 区，也不要在
   sentinel 外写内容。按当前项目事实项目化 contract 列出的核心文档；无法从仓库证据
   判断的问题写进 `remaining_human_decisions`，不要编造。

   完成后必须重跑普通 sync，让脚本用最终工作区刷新 `sync_state.json` 和 PR body auto 区。
   最后按 `agent_workorder.md` 的角色边界回报是否存在 `remaining_human_decisions`；
   如无，说明已重跑普通 sync，可以进入 PR 提交流程。
   ```

3. 如果 agent 在 `remaining_human_decisions` 里留下问题，把回答连同下面的短 prompt
   发回给 sync agent：

   ```text
   以下是 `remaining_human_decisions` 的回答。请据此继续完成 workflow docs sync：

   <逐条回答>

   请把这些回答写入 PR_BODY.md 的 agent-owned 区，并按需要同步核心文档。
   完成后必须重跑普通 sync，让脚本用最终工作区刷新 `sync_state.json` 和 PR body auto 区。
   最后按 `agent_workorder.md` 的角色边界回报是否仍有无法判断的问题。
   如果仍有无法判断的问题，继续写入 `remaining_human_decisions`；
   否则说明已重跑普通 sync，可以进入 PR 提交流程。
   ```

4. sync agent 回报可以进入 PR 提交流程后，用“PR 提交 agent 流程”创建或更新 PR。

5. PR 提交 agent 给出 PR URL 后，用“sync PR review”启动独立 review，并按该节判定处理 PASS / WARN / BLOCKER。

---

## 2. PR 提交 agent 流程

当 sync agent 回报普通 sync 已重跑、没有待回答的 `remaining_human_decisions` 后，把下面的短 prompt 发给 PR 提交 agent：

```text
请按本项目 PR_Checklist.md 创建或更新 workflow docs sync PR。

前置条件：sync agent 已经重跑普通 sync，且没有待回答的 `remaining_human_decisions`。

提交前检查工作区：当前目录必须仍位于同一个目标项目仓库内。如果混有非 sync 的代码、配置或测试改动，先停止并要求用户处理。如果工作区又发生 sync 内容变化，先停止并要求回到 sync agent 重跑普通 sync。

提交范围契约：sync PR 只允许提交本轮 contract 列出的核心文档、`.gitignore`、必要测试，以及目标项目规则允许提交的 `PR_BODY.md`；不得提交 `.coding_workflow/diffs/` 或临时 clone 目录。

分支处理：PR 提交 agent 自己负责分支生命周期，不交给 sync agent。先确认当前分支和远端是否已有对应的 workflow docs sync PR；如果已有 PR 分支，就在该分支更新；如果没有，就在提交前基于当前 HEAD 创建 sync 专用分支，例如 `codex/workflow-docs-sync-YYYYMMDD`，再提交、推送并创建 PR。若当前 HEAD 不是预期 base，先停止并要求用户确认。

提交前必须运行 final gate：

curl -fsSL https://raw.githubusercontent.com/wlvh/coding-workflow/main/scripts/sync.sh | bash -s -- --final

如果 final gate 失败，不要手修 PR body auto 区；停止并要求回到 sync agent 重跑普通 sync 并修复。final gate 只证明机械一致性，不证明 Repo Facts Map 证据真实性、项目化文案准确性或 upstream 新规则语义投影正确性；这些交给独立 reviewer。

`PR_BODY.md` 按目标项目规则处理：先用 `git ls-files --error-unmatch PR_BODY.md` 判断是否已被仓库跟踪。已跟踪则遵循目标项目自己的 PR 规则；未跟踪则只用它更新 GitHub PR body，不提交。在 `wlvh/coding-workflow` 自身做 sync 时，遵循本仓库本地草稿和 sync sentinel 规则，不提交 `PR_BODY.md`。

创建或更新 PR 后，请回报：
1. PR URL。
2. commit hash。
3. 实际提交文件清单。
4. final gate 和测试证据。
5. `PR_BODY.md` 是已提交还是仅用于更新 GitHub PR body。
```

---

## 3. sync PR review

下面的短 prompt 用作触发；reviewer 的系统 prompt 在 `scripts/sync_pr_review_system.md`，contract 真相源在 PR body auto 区的 `Sync Review Contract`。

把 PR URL 给独立 reviewer，并使用：

```text
你是 sync PR reviewer。请按 PR body auto 区的 `Sync Review Contract` 审核 PR <URL>，并使用 PR body 中 commit-pinned 的 reviewer prompt raw URL 对齐输出格式。

特别注意：你必须打开 contract 列出的全部 raw GitHub URL，并对照 PR head 上 contract 列出的核心文档做 full reconcile cross-check。
```

通过条件：

- PASS：进入用户视角验收。
- WARN：在 PR body 说明为什么可接受，再进入用户视角验收。
- BLOCKER：先分类处理。机械 BLOCKER（final gate、auto 区、raw URL、contract 状态或 blocking status）交回 sync agent 重跑普通 sync；语义 BLOCKER（证据真实性、项目化文案准确性、upstream 规则投影）先补证据或让用户判断，再交 sync agent 写入文档和 PR body。sync agent 重跑普通 sync 后，重新走“PR 提交 agent 流程”，由 PR 提交 agent 再跑 final gate、更新 PR、重新 review。
