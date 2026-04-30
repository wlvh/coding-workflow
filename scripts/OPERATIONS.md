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

普通 sync 完成后，第一步打开 `.coding_workflow/diffs/agent_workorder.md`，
按其中 `## 入口` 执行；本文档每个 pass 内部仍是自包含 prompt，可直接复制到新对话。

---

## 2. Sync Agent Pass

### 2.0 共用执行契约

每个 pass prompt 都必须能单独复制到新对话执行。执行 agent 先读本轮机器信号，
再按对应 pass prompt 判断和写入。

| 项 | 契约 |
|---|---|
| 本轮工单 | `.coding_workflow/diffs/agent_workorder.md`，先读其中 `## 入口`、`## Sync Pass Plan`、`## 文件处理清单`。 |
| 上游副本 | `.coding_workflow/diffs/upstream_full/`，每个 pass 只读取自己 owned docs 的上游版本。 |
| PR body 初始化 | 如果 `PR_BODY.md` 不存在，先用 `.coding_workflow/diffs/pr_body_skeleton.md` 初始化；如果 skeleton 也不存在，停止并回报普通 sync 未正确生成。 |
| PR body marker | `PR_BODY.md` 必须包含 `<!-- sync:pr-body version=1 -->`。 |
| script-owned auto 区 | `<!-- sync:auto:start -->` 到 `<!-- sync:auto:end -->` 只能由脚本刷新，agent 不得手改。 |
| agent-owned sentinel 格式 | `<!-- sync:agent:start <name> -->` 到 `<!-- sync:agent:end <name> -->`；sentinel 外不得写内容。 |
| agent-owned section 名 | `repo_facts_map`、`pass_handoffs`、`full_document_reconcile`、`remaining_human_decisions`。 |

| section name | start sentinel | end sentinel |
|---|---|---|
| `repo_facts_map` | `<!-- sync:agent:start repo_facts_map -->` | `<!-- sync:agent:end repo_facts_map -->` |
| `pass_handoffs` | `<!-- sync:agent:start pass_handoffs -->` | `<!-- sync:agent:end pass_handoffs -->` |
| `full_document_reconcile` | `<!-- sync:agent:start full_document_reconcile -->` | `<!-- sync:agent:end full_document_reconcile -->` |
| `remaining_human_decisions` | `<!-- sync:agent:start remaining_human_decisions -->` | `<!-- sync:agent:end remaining_human_decisions -->` |

`Repo Facts Map` 固定包含 10 个子项，PASS 1 负责完整补事实，后续 pass 只能按证据补正：

```text
### 1. 项目类型
### 2. 系统输入
### 3. 系统输出
### 4. 用户身份
### 5. 核心模块清单
### 6. 主要数据流
### 7. 关键不变量
### 8. 当前能力清单
### 9. 测试现状
### 10. 不确定项
```

`Sync Pass Status` 位于 `pass_handoffs` agent section 内，表头固定为：

```text
| pass_id | pass | status | evidence |
```

| pass_id | pass | owned docs |
|---|---|---|
| `code_architecture` | PASS 1 - Code Facts / Architecture | `architecture.md` |
| `capability_behavior` | PASS 2 - Capability / User Behavior | `capability_contract.json`, `interact.md`, `docs/business_user_guide.md` |
| `testing_quality` | PASS 3 - TESTING Independent Review | `TESTING.md` |
| `governance_closure` | PASS 4 - Governance / Reverse Closure | `PR_Checklist.md`, `SOP.md`, `AGENTS.md`, `.github/pull_request_template.md` |

`status` 列必须字面等于 `ready_for_next_pass` 才算 ready；`evidence` 列不能保留
`待补充`。

`Full Document Reconcile` 位于 `full_document_reconcile` agent section 内，表头固定为：

```text
| pass | 文件 | 当前脚本信号 | upstream semantic delta | adopted where | not adopted because | evidence | downstream impact |
```

- `upstream semantic delta`：本轮上游模板相对本地需要吸收或拒绝的语义变化。
- `adopted where`：已落地的位置。
- `not adopted because`：拒绝或暂不采用的原因；没有拒绝项写 `none`。
- `evidence`：代码路径、文档路径或命令输出证据。
- `downstream impact`：后续 pass、治理文档或用户需要承接的事项；没有写 `none`。

每个 pass 完成后必须重跑普通 sync：

```bash
curl -fsSL https://raw.githubusercontent.com/wlvh/coding-workflow/main/scripts/sync.sh | bash
```

PR 提交 agent 才运行 final gate：

```bash
curl -fsSL https://raw.githubusercontent.com/wlvh/coding-workflow/main/scripts/sync.sh | bash -s -- --final
```

PASS 1/2/3 是证据驱动：证据不足时写不确定项或 downstream impact，不当场追问用户。
PASS 4 是治理闭合：治理决策无法从前三个 pass 证据推出时可以当场追问；仍拿不到答案才写入
`Remaining Human Decisions`。

### 2.1 PASS 1 - Code Facts / Architecture

```text
当前仓库已经运行过普通 sync。请只执行本文档的
PASS 1 - Code Facts / Architecture。

前置条件：
- 当前仓库必须已经运行过普通 sync。

必须读取：
1. `.coding_workflow/diffs/agent_workorder.md`
2. `.coding_workflow/diffs/upstream_full/architecture.md`
3. `PR_BODY.md`；如果不存在，先用 `.coding_workflow/diffs/pr_body_skeleton.md` 初始化
4. `PR_BODY.md` 的 agent-owned sections：`repo_facts_map`、`pass_handoffs`、
   `full_document_reconcile`、`remaining_human_decisions`
5. 当前仓库的代码入口、模块边界、数据流、状态模型、外部依赖和代码层不变量

只允许修改：
- `architecture.md`
- `PR_BODY.md` 的 `repo_facts_map`
- `PR_BODY.md` 的 `pass_handoffs` 中 `code_architecture` 行
- `PR_BODY.md` 的 `full_document_reconcile` 中 `architecture.md` 行

必须填写：
- `Repo Facts Map` 的 10 个固定子项；每项必须有代码路径、文档路径或命令输出证据。
- `architecture.md` 中证据足够的代码事实；无代码证据的段落不得凭空写满。
- `Sync Pass Status` 的 `code_architecture` 行，ready 时 status 必须写成
  `ready_for_next_pass`。
- `Full Document Reconcile` 的 `architecture.md` 行，包括 upstream semantic delta、
  adopted where、not adopted because、evidence 和 downstream impact。

停止条件：
- `.coding_workflow/diffs/agent_workorder.md` 或需要的 skeleton / upstream 文件缺失。
- 需要判断能力边界、用户行为、测试门禁或治理规则；不要越权修改，写入不确定项或
  downstream impact。
- 证据不足；不要编造架构结论，把缺口写进 `Repo Facts Map` 的不确定项或
  `Full Document Reconcile` 的 evidence / downstream impact。

完成后：
1. 运行普通 sync：`curl -fsSL https://raw.githubusercontent.com/wlvh/coding-workflow/main/scripts/sync.sh | bash`。
2. 确认普通 sync 成功。
3. 回报修改了哪些文件和 PR body sections。
4. 回报 `Sync Pass Status` 中 `code_architecture` 是否为 `ready_for_next_pass`。
5. 回报是否写入 downstream impact 或需要后续 pass 承接。
```

### 2.2 PASS 2 - Capability / User Behavior

```text
请只执行本文档的 PASS 2 - Capability / User Behavior。

前置条件：
- `PR_BODY.md` 的 `Sync Pass Status` 中 `code_architecture` 行 status 必须字面等于
  `ready_for_next_pass`；否则停止并回报需要先完成 PASS 1。

必须读取：
1. `.coding_workflow/diffs/agent_workorder.md`
2. `.coding_workflow/diffs/upstream_full/capability_contract.json`
3. `.coding_workflow/diffs/upstream_full/interact.md`
4. `.coding_workflow/diffs/upstream_full/docs/business_user_guide.md`
5. `PR_BODY.md`；如果不存在，先用 `.coding_workflow/diffs/pr_body_skeleton.md` 初始化
6. `PR_BODY.md` 的 agent-owned sections：`repo_facts_map`、`pass_handoffs`、
   `full_document_reconcile`、`remaining_human_decisions`
7. `architecture.md`、`capability_contract.json`、`interact.md`、
   `docs/business_user_guide.md`

只允许修改：
- `capability_contract.json`
- `interact.md`
- `docs/business_user_guide.md`
- `PR_BODY.md` 的 `repo_facts_map` 中能力相关事实
- `PR_BODY.md` 的 `pass_handoffs` 中 `capability_behavior` 行
- `PR_BODY.md` 的 `full_document_reconcile` 中本 pass 三个 owned docs 行

必须填写：
- `capability_contract.json`：能力边界、职责边界和 agent 行为承诺的机器可读契约。
- `interact.md`：用户可观察行为和验收不变量。
- `docs/business_user_guide.md`：业务人员教学文档，只解释已存在能力，不新增能力。
- `Sync Pass Status` 的 `capability_behavior` 行，ready 时 status 必须写成
  `ready_for_next_pass`。
- `Full Document Reconcile` 中 `capability_contract.json`、`interact.md`、
  `docs/business_user_guide.md` 三行。

停止条件：
- PASS 1 未 ready。
- 能力边界声明找不到 `capability_contract.json` 锚点，或用户可观察行为找不到
  `interact.md` 锚点。
- 需要改 `architecture.md` 才能闭合；不要顺手改，写 downstream impact 指回 PASS 1。
- `docs/business_user_guide.md` 与 contract 或 interact 冲突；修改 business guide，
  不要扩大能力边界。

完成后：
1. 运行普通 sync：`curl -fsSL https://raw.githubusercontent.com/wlvh/coding-workflow/main/scripts/sync.sh | bash`。
2. 确认普通 sync 成功。
3. 回报修改了哪些文件和 PR body sections。
4. 回报 `Sync Pass Status` 中 `capability_behavior` 是否为 `ready_for_next_pass`。
5. 回报是否写入 downstream impact 或需要后续 pass 承接。
```

### 2.3 PASS 3 - TESTING Independent Review

```text
请只执行本文档的 PASS 3 - TESTING Independent Review。

前置条件：
- `PR_BODY.md` 的 `Sync Pass Status` 中 `code_architecture` 和
  `capability_behavior` 行 status 都必须字面等于 `ready_for_next_pass`；
  否则停止并回报应该回到哪个 pass。

必须读取：
1. `.coding_workflow/diffs/agent_workorder.md`
2. `.coding_workflow/diffs/upstream_full/TESTING.md`
3. `PR_BODY.md`；如果不存在，先用 `.coding_workflow/diffs/pr_body_skeleton.md` 初始化
4. `PR_BODY.md` 的 agent-owned sections：`repo_facts_map`、`pass_handoffs`、
   `full_document_reconcile`、`remaining_human_decisions`
5. `architecture.md`、`capability_contract.json`、`interact.md`、
   `docs/business_user_guide.md`、`TESTING.md`、`tests/` 和目标项目测试入口

只允许修改：
- `TESTING.md`
- `PR_BODY.md` 的 `repo_facts_map` 中测试现状相关事实
- `PR_BODY.md` 的 `pass_handoffs` 中 `testing_quality` 行
- `PR_BODY.md` 的 `full_document_reconcile` 中 `TESTING.md` 行

必须填写：
- `TESTING.md` 中的 `## TESTING_REVIEW_PACKET` section；如果不存在就新增，包含 9 项：
  existing_test_inventory、redundant_tests、missing_high_value_tests、
  tests_not_worth_adding、unit_vs_contract_vs_scenario_vs_e2e_decision、
  real_failure_modes_covered、mock_only_risks、recommended_gate、
  downstream_requirements_for_PR_Checklist。
- `Sync Pass Status` 的 `testing_quality` 行，ready 时 status 必须写成
  `ready_for_next_pass`。
- `Full Document Reconcile` 的 `TESTING.md` 行。

停止条件：
- PASS 1 或 PASS 2 未 ready。
- 需要新增或修改测试代码才能证明测试策略；本 pass 不改 `tests/`，把建议写入
  `TESTING.md` 或 downstream impact。
- PASS 1/2 的事实或锚点不足以支撑测试策略；不要顺手改前置 pass 文件，在
  downstream impact 写清应该回到哪个 pass。

完成后：
1. 运行普通 sync：`curl -fsSL https://raw.githubusercontent.com/wlvh/coding-workflow/main/scripts/sync.sh | bash`。
2. 确认普通 sync 成功。
3. 回报修改了哪些文件和 PR body sections。
4. 回报 `Sync Pass Status` 中 `testing_quality` 是否为 `ready_for_next_pass`。
5. 回报是否写入 downstream impact 或需要 PASS 4 承接。
```

### 2.4 PASS 4 - Governance / Reverse Closure

```text
请只执行本文档的 PASS 4 - Governance / Reverse Closure。

前置条件：
- `PR_BODY.md` 的 `Sync Pass Status` 中 `code_architecture`、`capability_behavior`
  和 `testing_quality` 行 status 都必须字面等于 `ready_for_next_pass`；
  否则停止并回报应该回到哪个 pass。

必须读取：
1. `.coding_workflow/diffs/agent_workorder.md`
2. `.coding_workflow/diffs/upstream_full/PR_Checklist.md`
3. `.coding_workflow/diffs/upstream_full/SOP.md`
4. `.coding_workflow/diffs/upstream_full/AGENTS.md`
5. `.coding_workflow/diffs/upstream_full/.github/pull_request_template.md`
6. `PR_BODY.md`；如果不存在，先用 `.coding_workflow/diffs/pr_body_skeleton.md` 初始化
7. `PR_BODY.md` 的 agent-owned sections：`repo_facts_map`、`pass_handoffs`、
   `full_document_reconcile`、`remaining_human_decisions`
8. `architecture.md`、`capability_contract.json`、`interact.md`、
   `docs/business_user_guide.md`、`TESTING.md`、`PR_Checklist.md`、`SOP.md`、
   `AGENTS.md` 和 `.github/pull_request_template.md`

只允许修改：
- `PR_Checklist.md`
- `SOP.md`
- `AGENTS.md`
- `.github/pull_request_template.md`
- `PR_BODY.md` 的 `pass_handoffs` 中 `governance_closure` 行
- `PR_BODY.md` 的 `full_document_reconcile` 中本 pass 四个 owned docs 行
- `PR_BODY.md` 的 `remaining_human_decisions`

必须填写：
- 前三个 pass 的 downstream impact 是否已被治理文档消费。
- `PR_Checklist.md`、`SOP.md`、`AGENTS.md` 的同步治理规则。
- PR template override decision：判断目标项目是否继承上游 PR template、是否有本地覆盖，
  并把决定写入 `Full Document Reconcile` 的 adopted where 或 not adopted because。
- `Sync Pass Status` 的 `governance_closure` 行，ready 时 status 必须写成
  `ready_for_next_pass`。
- `Remaining Human Decisions`：没有待判断项保留 `none`；否则列出具体待决事项。

停止条件：
- PASS 1/2/3 任一未 ready。
- 必须回到前置 pass 才能闭合；不要替上游补语义结论，在 downstream impact 写清回到哪个 pass。
- 治理决策无法从前三个 pass 证据推出；先当场追问用户，仍拿不到答案才写入
  `Remaining Human Decisions`。
- `AGENTS.md ## 文件简介` 内部项目文件条目需要项目代码事实；本 pass 不重写这些条目，
  只确认 heading 和同步治理规则。

完成后：
1. 运行普通 sync：`curl -fsSL https://raw.githubusercontent.com/wlvh/coding-workflow/main/scripts/sync.sh | bash`。
2. 确认普通 sync 成功。
3. 回报修改了哪些文件和 PR body sections。
4. 回报 `Sync Pass Status` 中 `governance_closure` 是否为 `ready_for_next_pass`。
5. 回报是否全部 pass ready、是否可以进入 PR 提交流程。
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
