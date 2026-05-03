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
- 如果已有 `PR_BODY.md` 不是 sync sentinel body，普通 sync 会 fail-fast；
  先移走、删除，或手动迁入 sync PR body 的 agent-owned 区后再运行。

普通 sync 输出：

- `.coding_workflow/diffs/agent_workorder.md`：本轮机器信号和本文档的 pinned URL。
- `.coding_workflow/diffs/pr_body_skeleton.md`：没有 `PR_BODY.md` 时的初始化骨架。
- `.coding_workflow/diffs/sync_state.json`：final gate 使用的机器状态。
- `.coding_workflow/diffs/upstream_full/`：本轮上游模板本地副本。

普通 sync 完成后，用户只需要从 PASS 1 开始复制对应 PASS 的 code block 到新对话。
`.coding_workflow/diffs/agent_workorder.md` 是给执行 agent 的本轮工单和机器信号；
用户不阅读也不影响启动下一步，执行 agent 会按 prompt 读取它。

---

## 2. Sync Agent Pass

每次新开对话，只复制并执行对应 PASS 的 code block；每个 PASS prompt 已内置必要共用规则。

### 2.1 PASS 1 - Code Facts / Architecture

```text
整体目标：完成本轮 workflow docs sync；用普通 sync 产物和代码证据更新本 pass
owned docs，并把结论写入 `PR_BODY.md` 的 agent-owned 区。
当前任务：只执行 PASS 1 - Code Facts / Architecture。不要执行其他 PASS。

前置条件：
- 当前仓库必须已经运行过普通 sync。

共用执行规则：
- 完整 PR body 结构、sync sentinel、Repo Facts heading 和表头，以
  `.coding_workflow/diffs/pr_body_skeleton.md` 或当前 `PR_BODY.md` 为准。
- 不得手改 `<!-- sync:auto:start -->` 到 `<!-- sync:auto:end -->` 区域、
  任何 sync sentinel、sentinel 外内容。
- 只修改本 pass 允许的文件和 agent-owned section 内容；本 pass 负责的
  agent-owned 内容不能保留 `待补充`。
- `Full Document Reconcile` 是 `PR_BODY.md` 的文档语义对账表；必须填写
  upstream semantic delta、adopted where、not adopted because、evidence、
  downstream impact；没有拒绝项或下游影响时写 `none`，无法判断时写
  `待判断` 留给 reviewer 和用户。
- `Full Document Reconcile` 的 evidence 列必须显式覆盖三类漂移；未发现写 `none`：
  `class-1 template/missing: ...<br>class-2 upstream: ...<br>class-3 code/test/behavior drift: ...`
- 本 pass owned docs 的漂移触发器：
  - `architecture.md`
    - class-1 template/missing：系统目的、模块表、数据流、状态 / 错误 / 外部依赖 / 不变量仍是模板或缺失。
    - class-2 upstream：upstream architecture 新增或调整架构章节 / 表达要求，本地未采纳也未说明原因。
    - class-3 code/test/behavior drift：代码新增入口、模块、数据流、状态模型、错误模型、外部依赖、扩展点或架构不变量，而 `architecture.md` 未跟上。
- 本 pass owned docs 的闭合规则：
  - class-1：用代码证据去模板化 `architecture.md`；证据不足写 evidence，不补虚假架构。
  - class-2：适用则 adopt 到 `architecture.md`；不适用写 not adopted because。
  - class-3：架构事实写回 `architecture.md`；能力、用户行为、测试或治理影响只写 downstream impact，不越权改后续 pass 文件。

必须读取：
1. `.coding_workflow/diffs/agent_workorder.md`
2. `.coding_workflow/diffs/upstream_full/architecture.md`
3. `PR_BODY.md`；如果不存在，先用 `.coding_workflow/diffs/pr_body_skeleton.md`
   初始化；如果 skeleton 缺失，停止并回报普通 sync 未正确生成
4. `PR_BODY.md` 的 `repo_facts_map` 和 `full_document_reconcile` 中 `architecture.md` 行
5. 当前仓库的代码入口、模块边界、数据流、状态模型、外部依赖和代码层不变量

只允许修改：
- `architecture.md`
- `PR_BODY.md` 的 `repo_facts_map`
- `PR_BODY.md` 的 `full_document_reconcile` 中 `architecture.md` 行

必须填写：
- `Repo Facts Map` 的 10 个固定子项；每项必须有代码路径、文档路径或命令输出证据。
- `architecture.md` 中证据足够的代码事实；无代码证据的段落不得凭空写满。
- `Full Document Reconcile` 的 `architecture.md` 行。

完成后：
1. 运行并确认普通 sync 成功：`curl -fsSL https://raw.githubusercontent.com/wlvh/coding-workflow/main/scripts/sync.sh | bash`。
2. 如果普通 sync 失败，停止并回报错误；不要手修 auto 区。
3. 回报普通 sync 已成功，以及本 pass 负责的 `Full Document Reconcile` 行是否留下
   `待判断`。
```

### 2.2 PASS 2 - Capability / User Behavior

```text
整体目标：完成本轮 workflow docs sync；用普通 sync 产物和代码证据更新本 pass
owned docs，并把结论写入 `PR_BODY.md` 的 agent-owned 区。
当前任务：只执行 PASS 2 - Capability / User Behavior。不要执行其他 PASS。

前置条件：
- `.coding_workflow/diffs/agent_workorder.md` 的 `## 文件处理清单` 中
  `architecture.md` 的 `marker / TODO 命中` 应为 `none`；否则停止并回报需要先完成
  PASS 1。

共用执行规则：
- 完整 PR body 结构、sync sentinel、Repo Facts heading 和表头，以
  `.coding_workflow/diffs/pr_body_skeleton.md` 或当前 `PR_BODY.md` 为准。
- 不得手改 `<!-- sync:auto:start -->` 到 `<!-- sync:auto:end -->` 区域、
  任何 sync sentinel、sentinel 外内容。
- 只修改本 pass 允许的文件和 agent-owned section 内容；本 pass 负责的
  agent-owned 内容不能保留 `待补充`。
- `Full Document Reconcile` 是 `PR_BODY.md` 的文档语义对账表；必须填写
  upstream semantic delta、adopted where、not adopted because、evidence、
  downstream impact；没有拒绝项或下游影响时写 `none`，无法判断时写
  `待判断` 留给 reviewer 和用户。
- `Full Document Reconcile` 的 evidence 列必须显式覆盖三类漂移；未发现写 `none`：
  `class-1 template/missing: ...<br>class-2 upstream: ...<br>class-3 code/test/behavior drift: ...`
- 本 pass owned docs 的漂移触发器：
  - `capability_contract.json`
    - class-1 template/missing：`sample_*` anchor、sample status、样本能力桶或占位能力仍未项目化。
    - class-2 upstream：upstream schema 新增能力桶、失败模式、行为承诺字段或锚点规则，本地未采纳也未说明原因。
    - class-3 code/test/behavior drift：代码或测试显示新增能力、拒绝、必须追问、降级或边界行为，但 contract 无对应 anchor。
  - `interact.md`
    - class-1 template/missing：用户可观察行为、不变量或验收口径仍是写作骨架或缺失。
    - class-2 upstream：upstream 用户行为写作规则、颗粒度原则或验收表达更新，本地未采纳也未说明原因。
    - class-3 code/test/behavior drift：代码新增可见入口、输出结构、错误提示、排序、默认行为或限制，但 `interact.md` 无对应不变量。
  - `docs/business_user_guide.md`
    - class-1 template/missing：尖括号占位、样例 case、泛用问法或模板说明仍未项目化。
    - class-2 upstream：upstream 教学结构、业务解释顺序或风险提示更新，本地未采纳也未说明原因。
    - class-3 code/test/behavior drift：contract / interact 已确认且业务人员会感知的能力，guide 未解释怎么问、怎么看、何时找人。
- 本 pass owned docs 的闭合规则：
  - `capability_contract.json`：class-1/2/3 修成真实能力边界和 stable anchor；证据不足写 downstream impact，不凭空声明能力。
  - `interact.md`：只闭合用户可观察行为和验收不变量；新增声明必须锚到 contract 或测试证据。
  - `docs/business_user_guide.md`：只解释 contract / interact 已确认且业务可感知的能力；能力未确认先回到 contract / interact。
  - class-2 不适用时，各 owned doc 对应写 not adopted because。

必须读取：
1. `.coding_workflow/diffs/agent_workorder.md`
2. `.coding_workflow/diffs/upstream_full/capability_contract.json`
3. `.coding_workflow/diffs/upstream_full/interact.md`
4. `.coding_workflow/diffs/upstream_full/docs/business_user_guide.md`
5. `PR_BODY.md`；如果不存在，先用 `.coding_workflow/diffs/pr_body_skeleton.md`
   初始化；如果 skeleton 缺失，停止并回报普通 sync 未正确生成
6. `PR_BODY.md` 的 `repo_facts_map` 中能力相关事实和 `full_document_reconcile`
   中本 pass 三个 owned docs 行
7. `architecture.md`、`capability_contract.json`、`interact.md`、
   `docs/business_user_guide.md`

只允许修改：
- `capability_contract.json`
- `interact.md`
- `docs/business_user_guide.md`
- `PR_BODY.md` 的 `repo_facts_map` 中能力相关事实
- `PR_BODY.md` 的 `full_document_reconcile` 中本 pass 三个 owned docs 行

必须填写：
- `capability_contract.json`：能力边界、职责边界和 agent 行为承诺的机器可读契约。
- `interact.md`：用户可观察行为和验收不变量。
- `docs/business_user_guide.md`：业务人员教学文档，只解释已存在能力，不新增能力。
- 锚点优先级：`capability_contract.json` → `interact.md` → 测试存在性；
  测试只用于证明能力实现存在，不替代 contract / interact，也不为测试设计背书。
- `Full Document Reconcile` 中 `capability_contract.json`、`interact.md`、
  `docs/business_user_guide.md` 三行。

完成后：
1. 运行并确认普通 sync 成功：`curl -fsSL https://raw.githubusercontent.com/wlvh/coding-workflow/main/scripts/sync.sh | bash`。
2. 如果普通 sync 失败，停止并回报错误；不要手修 auto 区。
3. 回报普通 sync 已成功，以及本 pass 负责的 `Full Document Reconcile` 行是否留下
   `待判断`。
```

### 2.3 PASS 3 - TESTING Independent Review

```text
整体目标：完成本轮 workflow docs sync；用普通 sync 产物和代码证据更新本 pass
owned docs，并把结论写入 `PR_BODY.md` 的 agent-owned 区。
当前任务：只执行 PASS 3 - TESTING Independent Review。不要执行其他 PASS。

前置条件：
- `.coding_workflow/diffs/agent_workorder.md` 的 `## 文件处理清单` 中
  `architecture.md`、`capability_contract.json`、`interact.md` 和
  `docs/business_user_guide.md` 的 `marker / TODO 命中` 应为 `none`；
  否则停止并回报应该回到 PASS 1 或 PASS 2。

共用执行规则：
- 完整 PR body 结构、sync sentinel、Repo Facts heading 和表头，以
  `.coding_workflow/diffs/pr_body_skeleton.md` 或当前 `PR_BODY.md` 为准。
- 不得手改 `<!-- sync:auto:start -->` 到 `<!-- sync:auto:end -->` 区域、
  任何 sync sentinel、sentinel 外内容。
- 只修改本 pass 允许的文件和 agent-owned section 内容；本 pass 负责的
  agent-owned 内容不能保留 `待补充`。
- `Full Document Reconcile` 是 `PR_BODY.md` 的文档语义对账表；必须填写
  upstream semantic delta、adopted where、not adopted because、evidence、
  downstream impact；没有拒绝项或下游影响时写 `none`，无法判断时写
  `待判断` 留给 reviewer 和用户。
- `Full Document Reconcile` 的 evidence 列必须显式覆盖三类漂移；未发现写 `none`：
  `class-1 template/missing: ...<br>class-2 upstream: ...<br>class-3 code/test/behavior drift: ...`
- 本 pass owned docs 的漂移触发器：
  - `TESTING.md`
    - class-1 template/missing：测试分层、测试证据、推荐 gate 或 `TESTING_REVIEW_PACKET` 仍是上游骨架或缺失。
    - class-2 upstream：upstream 新增测试原则、alignment 测试规则、证据记录方式或 gate 口径，本地未采纳也未说明原因。
    - class-3 code/test/behavior drift：`tests/` 冗长、重复、mock-only、只测实现细节，或没有覆盖新增能力；本 pass 只写 review packet，不改测试代码。
- 本 pass owned docs 的闭合规则：
  - `TESTING.md`：class-1/2 更新测试原则、证据记录和 gate；不适用的 upstream 规则写 not adopted because。
  - class-3 只写 `TESTING_REVIEW_PACKET`，把机械信号和定向证据落入 redundant_tests、missing_high_value_tests、tests_not_worth_adding、mock_only_risks、recommended_gate 和 downstream_requirements_for_PR_Checklist；本 pass 不改 `tests/`。

必须读取：
1. `.coding_workflow/diffs/agent_workorder.md`
2. `.coding_workflow/diffs/upstream_full/TESTING.md`
3. `PR_BODY.md`；如果不存在，先用 `.coding_workflow/diffs/pr_body_skeleton.md`
   初始化；如果 skeleton 缺失，停止并回报普通 sync 未正确生成
4. `PR_BODY.md` 的 `repo_facts_map` 中测试现状相关事实和 `full_document_reconcile`
   中 `TESTING.md` 行
5. `TESTING.md`、目标项目测试入口、`tests/` 清单和机械信号命令输出；只打开机械信号
   指向的具体测试片段
6. PASS 1/2 owned docs 的相关锚点或段落；只在测试策略需要时定向读取，不通读全文

只允许修改：
- `TESTING.md`
- `PR_BODY.md` 的 `repo_facts_map` 中测试现状相关事实
- `PR_BODY.md` 的 `full_document_reconcile` 中 `TESTING.md` 行

机械信号收集（示例命令，agent 必须按项目等价工具改写并在 evidence 写明实际命令）：
- `find tests -type f -name 'test_*.py' -exec wc -l {} + | sort -n`
- `grep -rh '^def test_\|^class Test' tests/`
- `git log --since='3 months ago' --name-only -- tests/`

必须填写：
- `TESTING.md` 顶部的 `## TESTING_REVIEW_PACKET` section；如果不存在就新增，包含 9 项：
  existing_test_inventory、redundant_tests、missing_high_value_tests、
  tests_not_worth_adding、unit_vs_contract_vs_scenario_vs_e2e_decision、
  real_failure_modes_covered、mock_only_risks、recommended_gate、
  downstream_requirements_for_PR_Checklist。
- `Full Document Reconcile` 的 `TESTING.md` 行。

完成后：
1. 运行并确认普通 sync 成功：`curl -fsSL https://raw.githubusercontent.com/wlvh/coding-workflow/main/scripts/sync.sh | bash`。
2. 如果普通 sync 失败，停止并回报错误；不要手修 auto 区。
3. 回报普通 sync 已成功，以及本 pass 负责的 `Full Document Reconcile` 行是否留下
   `待判断`。
```

### 2.4 PASS 4 - Governance / Reverse Closure

```text
整体目标：完成本轮 workflow docs sync；用普通 sync 产物和代码证据更新本 pass
owned docs，并把结论写入 `PR_BODY.md` 的 agent-owned 区。
当前任务：只执行 PASS 4 - Governance / Reverse Closure。不要执行其他 PASS。

前置条件：
- `.coding_workflow/diffs/agent_workorder.md` 的 `## 文件处理清单` 中 PASS 1/2/3
  owned docs 的 `marker / TODO 命中` 应为 `none`；否则停止并回报应该回到哪个 pass。

共用执行规则：
- 完整 PR body 结构、sync sentinel、Repo Facts heading 和表头，以
  `.coding_workflow/diffs/pr_body_skeleton.md` 或当前 `PR_BODY.md` 为准。
- 不得手改 `<!-- sync:auto:start -->` 到 `<!-- sync:auto:end -->` 区域、
  任何 sync sentinel、sentinel 外内容。
- 只修改本 pass 允许的文件和 agent-owned section 内容；本 pass 负责的
  agent-owned 内容不能保留 `待补充`。
- `Full Document Reconcile` 是 `PR_BODY.md` 的文档语义对账表；必须填写
  upstream semantic delta、adopted where、not adopted because、evidence、
  downstream impact；没有拒绝项或下游影响时写 `none`，无法判断时写
  `待判断` 留给 reviewer 和用户。
- `Full Document Reconcile` 的 evidence 列必须显式覆盖三类漂移；未发现写 `none`：
  `class-1 template/missing: ...<br>class-2 upstream: ...<br>class-3 code/test/behavior drift: ...`
- 本 pass owned docs 的漂移触发器：
  - `PR_Checklist.md`
    - class-1 template/missing：提交、PR body、测试证据或文档同步清单仍是骨架或缺失。
    - class-2 upstream：upstream 新增提交检查项、文档同步规则或 review 记录要求，本地未采纳也未说明原因。
    - class-3 code/test/behavior drift：PASS 1/2/3 的 downstream impact 需要提交流程约束，但 checklist 未收。
  - `SOP.md`
    - class-1 template/missing：只剩 SOP 原则、空段或样例流程，没有项目固定流程入口。
    - class-2 upstream：upstream SOP 原则或流程入口组织方式更新，本地未采纳也未说明原因。
    - class-3 code/test/behavior drift：代码或交付方式新增固定流程，如迁移、部署、E2E、live ops，但 SOP 无入口。
  - `AGENTS.md`
    - class-1 template/missing：`## 文件简介`、文档关系、测试 / PR 入口或业务知识仍是空段或模板。
    - class-2 upstream：upstream agent 工作规则、文档关系或文件简介要求更新，本地未采纳也未说明原因。
    - class-3 code/test/behavior drift：核心模块、业务逻辑、入口脚本或治理文件增删，但 `## 文件简介` 未跟上。
  - `.github/pull_request_template.md`
    - class-1 template/missing：文件缺失；这是唯一允许直接继承 upstream 的核心文件。
    - class-2 upstream：upstream PR template 更新时默认 adopt；本地覆盖才需要写清 not adopted because。
    - class-3 code/test/behavior drift：项目需要固定 PR 段落但 upstream 无法覆盖，才保留本地覆盖。
- 本 pass owned docs 的闭合规则：
  - `PR_Checklist.md`：把 PASS 1/2/3 downstream impact 中需要提交期强制执行的事项收进 checklist。
  - `SOP.md`：只为项目固定流程新增或更新流程入口；新增 / 修改 SOP 后同步 `AGENTS.md` 的 SOP 清单。
  - `AGENTS.md`：只按前三个 pass 的证据更新文件简介和治理入口；需要新的项目代码事实时写 downstream impact，不做大范围代码重读。
  - `.github/pull_request_template.md`：缺失或 upstream 更新默认 inherit / adopt；只有项目固定 PR 段落无法由 upstream 覆盖时，才保留最小本地覆盖并写 not adopted because。

必须读取：
1. `.coding_workflow/diffs/agent_workorder.md`
2. `.coding_workflow/diffs/upstream_full/PR_Checklist.md`
3. `.coding_workflow/diffs/upstream_full/SOP.md`
4. `.coding_workflow/diffs/upstream_full/AGENTS.md`
5. `.coding_workflow/diffs/upstream_full/.github/pull_request_template.md`
6. `PR_BODY.md`；如果不存在，先用 `.coding_workflow/diffs/pr_body_skeleton.md`
   初始化；如果 skeleton 缺失，停止并回报普通 sync 未正确生成
7. `PR_BODY.md` 的 `full_document_reconcile` 全表和 `remaining_human_decisions`
8. `PR_Checklist.md`、`SOP.md`、`AGENTS.md` 和 `.github/pull_request_template.md`
9. PASS 1/2/3 owned docs 仅在验证 downstream impact 闭合时定向读取相关段落；
   不默认通读前置 pass 全文

只允许修改：
- `PR_Checklist.md`
- `SOP.md`
- `AGENTS.md`
- `.github/pull_request_template.md`
- `PR_BODY.md` 的 `full_document_reconcile` 中本 pass 四个 owned docs 行
- `PR_BODY.md` 的 `remaining_human_decisions`

必须填写：
- 前三个 pass 的 downstream impact 是否已被治理文档消费。
- `Full Document Reconcile` 的 downstream impact 列必须逐 pass 显式列出：
  `PASS 1 找到 N 条 class-3 漂移，闭合于 architecture.md §X / 未闭合 K 条 deferred 到 ...`；
  `PASS 2 ... 闭合于 capability_contract.json / interact.md / docs/business_user_guide.md ...`；
  `PASS 3 ... 闭合于 TESTING_REVIEW_PACKET / 留作 PR_Checklist 待落实 ...`。
- `PR_Checklist.md`、`SOP.md`、`AGENTS.md` 的同步治理规则。
- PR template override decision：判断目标项目是否继承上游 PR template、是否有本地覆盖，
  并把决定写入 `Full Document Reconcile` 的 adopted where 或 not adopted because。
- `Remaining Human Decisions`：没有待判断项保留 `none`；否则列出具体待决事项。

完成后：
1. 运行并确认普通 sync 成功：`curl -fsSL https://raw.githubusercontent.com/wlvh/coding-workflow/main/scripts/sync.sh | bash`。
2. 如果普通 sync 失败，停止并回报错误；不要手修 auto 区。
3. 回报普通 sync 已成功，以及 `Full Document Reconcile` 或
   `Remaining Human Decisions` 是否留下 `待判断`。
```

---

## 3. PR 提交 Agent

PASS 4 完成后，启动 PR 提交 agent；提交判断以 `PR_BODY.md` 的
`Full Document Reconcile` / `Remaining Human Decisions` 和 final gate 为准，不以
PASS 4 的聊天摘要作为事实源。

```text
请按本项目 PR_Checklist.md 创建或更新 workflow docs sync PR。

前置条件：`Full Document Reconcile` 覆盖本轮核心文档，且
`Remaining Human Decisions` 已明确写成 `none` 或待判断项。

提交前检查工作区：如果混有非 sync 的代码、配置或测试改动，停止并要求用户处理。
如果 sync 内容又发生变化，停止并要求回到对应 sync pass 重跑普通 sync。
提交前检查 PR_BODY.md：如果 `Full Document Reconcile` 缺少本轮核心文档行或仍有
`待补充`，停止并要求回到对应 sync pass。`Remaining Human Decisions` 是语义风险表达，
不是 final gate 硬阻断；如有非 `none` 项，必须保留在 PR body 交给 reviewer 和用户判断。

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
