# Workflow Docs Sync - 操作手册

本文档只说明 workflow docs sync 的人工入口、4 个 sync pass prompt 和角色边界。
每次运行后的文件清单、脚本信号、上游模板路径和本轮状态，以
`.coding_workflow/diffs/agent_workorder.md`、`sync_state.json` 和 `PR_BODY.md` 为准。

流程摘要：普通 sync 生成本轮证据和薄工单；4 个 sync pass 在新对话中按
本文档的专用 prompt 接力补核心文档和 PR body agent-owned 区；PR 提交
agent 运行 final gate 并创建或更新 PR；独立 reviewer 做语义审查。

---

## 1. Quick Start

在目标项目现有仓库目录运行普通 sync：

```bash
curl -fsSL https://raw.githubusercontent.com/wlvh/coding-workflow/main/scripts/sync.sh | bash
```

运行前要求：

- 不要混入非 sync 的代码、配置或测试 dirty 改动；脚本会 fail-fast 并列出路径。
- 根据本轮工单重跑普通 sync 时，只允许本轮核心文档、`.gitignore`、
  `PR_BODY.md` 和 `.coding_workflow/diffs/` 处于 dirty 状态。

普通 sync 输出：

- `.coding_workflow/diffs/agent_workorder.md`：本轮机器信号和本文档的 pinned URL。
- `.coding_workflow/diffs/pr_body_skeleton.md`：没有 `PR_BODY.md` 时的初始化骨架。
- `.coding_workflow/diffs/sync_state.json`：final gate 使用的机器状态。
- `.coding_workflow/diffs/upstream_full/`：本轮上游模板本地副本。

---

## 2. Sync Agent Pass

PASS 1 - Code Facts / Architecture：

```text
当前仓库已经运行过普通 sync。请只执行本文档的
PASS 1 - Code Facts / Architecture。

先读取 `.coding_workflow/diffs/agent_workorder.md`、`PR_BODY.md`
或 `.coding_workflow/diffs/pr_body_skeleton.md`、`.coding_workflow/diffs/upstream_full/`
以及当前仓库的代码入口、模块边界、数据流、状态模型、外部依赖和关键不变量。

专属目标：重建代码事实图，用可定位代码 / 文档 / 命令证据补 Repo Facts Map；
没有证据的内容写不确定项。只同步 `architecture.md`、`Sync Pass Status`
的 PASS 1 行和 `Full Document Reconcile` 的 `architecture.md` 行；把影响能力、
测试或治理的结论写入 `Full Document Reconcile` 的 downstream impact。

如果 `PR_BODY.md` 不存在，先用 `.coding_workflow/diffs/pr_body_skeleton.md`
初始化。不要手改 script-owned auto 区，不要在 sentinel 外写内容。
完成后必须重跑普通 sync，并回报本 pass 的 `Sync Pass Status` 是否为
`ready_for_next_pass`。
```

PASS 2 - Capability / User Behavior：

```text
请只执行本文档的 PASS 2 - Capability / User Behavior。

前置条件：先确认 `Sync Pass Status` 中 PASS 1 为 `ready_for_next_pass`；
否则停止并回报需要先完成 PASS 1。

先读取 `.coding_workflow/diffs/agent_workorder.md`、PASS 1 状态和证据、
`PR_BODY.md`、
`.coding_workflow/diffs/upstream_full/`、`capability_contract.json`、`interact.md`
和 `docs/business_user_guide.md`。

专属目标：基于 PASS 1 code facts 复核能力边界和用户可观察行为是否一致。
所有“能做 / 不能做 / 必须追问 / 必须拒绝 / 不得猜测”等声明必须有
contract、interact 或测试锚点。business guide 只能解释已存在能力，不新增能力。
把测试和治理要承接的规则写入 `Full Document Reconcile` 的 downstream impact。

只修改本 pass 拥有的核心文档、`Sync Pass Status` 的 PASS 2 行和对应
`Full Document Reconcile` 行。
完成后重跑普通 sync，并回报 PASS 2 是否 ready。
```

PASS 3 - TESTING Independent Review：

```text
请只执行本文档的 PASS 3 - TESTING Independent Review。

前置条件：先确认 `Sync Pass Status` 中 PASS 1 和 PASS 2 都是 `ready_for_next_pass`；
否则停止并回报应该回到哪个 pass。

先读取 `.coding_workflow/diffs/agent_workorder.md`、PASS 1/2 状态和证据、`PR_BODY.md`、
`.coding_workflow/diffs/upstream_full/`、`TESTING.md`、`tests/` 和目标项目测试入口。

专属目标：把 `TESTING.md` 当作测试体系审查，不是文字同步。必须从冗余度、
必要性、真实性、mock-only 风险、真实失败模式覆盖、unit/contract/scenario/E2E
分层、以及哪些测试不值得新增等角度重构测试体系。

必须填写 TESTING_REVIEW_PACKET：existing_test_inventory、redundant_tests、
missing_high_value_tests、tests_not_worth_adding、unit_vs_contract_vs_e2e_decision、
real_failure_modes_covered、mock_only_risks、recommended_gate、
downstream_requirements_for_PR_Checklist。

只修改 `TESTING.md`、`Sync Pass Status` 的 PASS 3 行和 `Full Document Reconcile`
的 `TESTING.md` 行。把 PR_Checklist 或治理流程必须承接的测试门禁写入
downstream impact。
完成后重跑普通 sync，并回报 PASS 3 是否 ready。
```

PASS 4 - Governance / Reverse Closure：

```text
请只执行本文档的 PASS 4 - Governance / Reverse Closure。

前置条件：先确认 `Sync Pass Status` 中 PASS 1/2/3 都是 `ready_for_next_pass`；
否则停止并回报应该回到哪个 pass。

先读取 `.coding_workflow/diffs/agent_workorder.md`、前三个 pass 状态和证据、`PR_BODY.md`、
`.coding_workflow/diffs/upstream_full/`、`PR_Checklist.md`、`SOP.md`、`AGENTS.md`
和 `.github/pull_request_template.md`。

专属目标：消费前三个 pass 的 downstream impact，对必须落到治理文档的规则做反向闭合。
同步 PR_Checklist、SOP、AGENTS 结构性骨架和 PR template override decision。
`AGENTS.md ## 文件简介` 内部项目文件条目不由 sync 重写；只能确认 heading 和同步治理规则。

只修改本 pass 拥有的核心文档、`Sync Pass Status` 的 PASS 4 行和对应
`Full Document Reconcile` 行。闭合不了就写清应该回到哪个 pass；
需要用户判断时由 PASS 4 当场追问，仍拿不到答案才写 Remaining Human Decisions。
不能替上游补语义结论。完成后重跑普通 sync，并回报是否全部 pass ready、
是否可以进入 PR 提交流程。
```

---

## 3. PR 提交 Agent

PASS 4 回报普通 sync 已重跑、全部 pass ready，且 `Remaining Human Decisions`
已显式记录为 none 或待判断项后，启动：

```text
请按本项目 PR_Checklist.md 创建或更新 workflow docs sync PR。

前置条件：PASS 4 已经重跑普通 sync，`Sync Pass Status` 中全部 pass
都是 `ready_for_next_pass`，且 `Remaining Human Decisions` 已明确写成
none 或待判断项。

提交前检查工作区：如果混有非 sync 的代码、配置或测试改动，停止并要求用户处理。
如果 sync 内容又发生变化，停止并要求回到对应 sync pass 重跑普通 sync。
提交前检查 PR_BODY.md：如果 `Sync Pass Status` 任一 pass 不是
`ready_for_next_pass`，停止并要求回到对应 sync pass。`Remaining Human Decisions`
是语义风险表达，不是 final gate 硬阻断；如有非 none 项，必须保留在 PR body
交给 reviewer 和用户判断。

提交范围：只允许提交本轮核心文档、`.gitignore`、必要测试，以及目标项目规则
允许提交的 `PR_BODY.md`；不得提交 `.coding_workflow/diffs/` 或临时 clone 目录。

提交前必须运行：

curl -fsSL https://raw.githubusercontent.com/wlvh/coding-workflow/main/scripts/sync.sh | bash -s -- --final

如果 final gate 失败，不要手修 PR body auto 区；回到对应 sync pass。
创建或更新 PR 后，回报 PR URL、commit hash、实际提交文件、final gate / 测试证据，
以及 `PR_BODY.md` 是已提交还是仅用于更新 GitHub PR body。
```

---

## 4. Sync PR Review

PR 提交 agent 给出 PR URL 后，启动独立 reviewer：

```text
你是 sync PR reviewer。请按 PR body auto 区的 `Sync Review Contract`
和 commit-pinned reviewer prompt raw URL 审核 PR <URL>。

必须打开 PR body upstream 段落列出的 raw URL，并对照 PR head 上的核心文档做
full reconcile cross-check。
```

处理结果：

- PASS：进入用户视角验收。
- WARN：在 PR body 说明为什么可接受，再进入用户视角验收。
- BLOCKER：机械问题回到 sync pass 重跑普通 sync；语义问题先补证据或让用户判断，
  再回到 sync pass 写入文档和 PR body，之后重新走 PR 提交和 review。
