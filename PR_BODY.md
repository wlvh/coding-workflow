## 1. 背景与目标

PR #7 已合并后，用户指出 `scripts/OPERATIONS.md` 中的 PR 提交 agent 信息不够充分。

本 PR 的目标是只补强 PR 提交 agent 的可执行信息，让它能按同一个 prompt 完成读取、核对、final gate、单 commit 发布、PR body 更新和结果回报，不再依赖临场推导 `PR_Checklist.md` 的发布细节。

---

## 2. 实现方案

- 在 `scripts/OPERATIONS.md` 的 `## 3. PR 提交 Agent` 中新增明确任务边界：只执行 PR 提交，不补写 PASS 1/2/3/4 语义内容。
- 补充 PR 提交 agent 必须读取的文件：`PR_Checklist.md`、`TESTING.md`、`.github/pull_request_template.md`、`PR_BODY.md`、`.coding_workflow/diffs/sync_state.json`。
- 补充提交前核对：分支、工作区、`git diff --name-only <base>...HEAD`、`PR_BODY.md` 变更范围、`Full Document Reconcile` / `Remaining Human Decisions` 在 `PR_BODY.md` 中的具体读取位置、FDR 完整性、语义风险、测试记录和 final gate。
- 补充提交范围和单 commit 发布命令：区分更新既有 PR 与新建 PR，明确 `git commit --amend --no-edit`、`git push --force-with-lease`、`gh pr edit --body-file`、`gh pr create --draft --body-file`。
- 回归测试锁住 PR 提交 agent 的关键命令、禁止项和回报项，避免 prompt 再退回抽象描述。

---

## 3. 变更范围

来自 `git diff --name-only origin/main...HEAD`：

| 文件 / 目录 | 变更类型 | 说明 |
|---|---|---|
| `scripts/OPERATIONS.md` | 修改 | 补强 PR 提交 agent prompt，加入必须读取、提交前核对、提交范围、单 commit 发布和完成回报要求。 |
| `tests/test_sync_coding_workflow.py` | 修改 | 为 PR 提交 agent prompt 增加 literal 回归测试，锁住关键命令与禁止项。 |

---

## 4. 文档影响

受影响文档：

- `scripts/OPERATIONS.md`

说明：

- 本 PR 只调整 sync 工具操作手册中的 PR 提交流程 prompt。
- 不改变下游项目能力边界、用户可观察行为或 sync 脚本运行行为。
- 不需要更新 `capability_contract.json`、`interact.md` 或 `docs/business_user_guide.md`。

---

## 5. 用户与架构影响

用户可见变化：

- No
- 说明：不改变应用运行行为；只影响执行 workflow docs sync PR 提交的 agent prompt。

架构变化：

- No
- 说明：未修改 sync 脚本、状态模型、数据流或外部依赖。

---

## 6. Review / 修复记录

| 轮次 | 来源 | 问题摘要 | 判断 | 处理结果 | 证据 |
|---|---|---|---|---|---|
| R0 | 用户反馈 | PR 提交 agent 信息不够充分，缺少可直接执行的提交 / 更新 PR 细节。 | 真实存在 | 补充必须读取、提交前核对、提交范围、单 commit 发布命令和完成回报要求。 | `scripts/OPERATIONS.md`, `tests/test_sync_coding_workflow.py` |
| R1 | 自审 | PR #7 已经合并，无法继续提交到同一个 PR。 | 真实存在 | 从最新 `main` 新建后续分支，只提交 PR 提交 agent 的增量修改。 | `git status`, `gh pr view 7` |
| R2 | 用户反馈 | PR 提交 agent 读不懂 `Full Document Reconcile` / `Remaining Human Decisions`，因为 prompt 没告诉它去哪里读。 | 真实存在 | 在必须读取和提交前核对中明确指向 `PR_BODY.md` 的对应 heading，以及 agent-owned sentinel 区间。 | `scripts/OPERATIONS.md`, `tests/test_sync_coding_workflow.py` |

---

## 7. 已知限制与回滚

已知限制：

- PR 提交 agent prompt 比原来更长，但内容集中在发布阶段，不增加 PASS 1/2/3/4 的上下文负担。

回滚方式：

- 回滚本 PR 即可恢复到 PR #7 合并后的 PR 提交 agent prompt。

---

## 8. 最终自检

- [x] 当前分支不是主干：`codex/pr-submit-agent-prompt`
- [x] 已执行 `git diff --name-only origin/main...HEAD`
- [x] “变更范围”与实际 diff 一致
- [x] PR body 不包含历史草稿、旧分支名、未落地计划
- [x] 已按 `TESTING.md` 完成测试与测试记录
- [x] 用户可见变化已对照 `interact.md`
- [x] 架构变化已对照 `architecture.md`
- [x] 每轮 review / 修复都已写入“Review / 修复记录”
