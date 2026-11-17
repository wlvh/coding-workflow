# 编程工作流

本工作流从用户需求形成 Issue，经过实施、测试与独立审查，交付可实际使用的软件成果。
当前为 **coding-loop v2**；决策依据见 [DEC-009](decisions.md#dec-009issue-直接驱动的编程回路与固定版本采用)。
[角色提示与源索引](../../prompts/README.md)是模型行为指令的唯一维护入口；
[固定版本采用与更新](version_adoption.md)定义下游怎样采用本规范。

## 目标与默认安排

Issue 和 PR 均由**来自两家不同 LLM 公司的 LLM**分别独立审查，再实际交换报告和结论。
工程负责人连续调查、实施和测试；审查发现的阻断问题经核实后，在 Codex 事实核实会话中修复，
形成新版本后交独立复审。可演示成果完成必要验证后，提供 Tech Lead 解读和用户验收入口。

## 1. Issue 直接表达目标，并给出初版验收安排

由 [Issue 作者](../../prompts/issue_agent.md)根据用户原话、有效决定和必要仓库事实编写 Issue，
写清用户问题、目标行为、必要边界和完成标准。有真实依赖、兼容要求或未决产品取舍时一并说明。

需求、共享约定和验收计划保存在目标项目的 GitHub Issue 或仓库文档中。单项需求直接写在 Issue；
跨 Issue 的稳定约定、必要影响结论或迁移安排放入目标仓库已有的文档目录，由相关 Issue 引用具体版本。

**开发前制定用户视角验收计划**：谁从哪个真实入口开始，用什么输入、做哪些操作，应该看到什么结果，
以及关键失败后怎样识别和继续。按[用户验收提示](../../prompts/user_acceptance.md)，由 Issue 作者
写入验收章节，或引用目标仓库中的验收文档。一个成果可以跨多个 Issue/PR，共用一份计划。

开发中由工程负责人提出有依据的修订，Issue 作者统一更新正文，记录日期、原因、变更条目和对既有
结果的影响，保留原要求及修订记录。
涉及目标或关键判据的变化交回 Issue 决定和受影响的需求审查。每次验收注明采用的计划版本、代码候选
与环境。候选可运行时执行可提前验证的场景，部署后补目标环境特有部分。

## 2. 来自两家不同 LLM 公司的 LLM 独立审查 Issue

将同一 Issue 版本交给两家公司的独立审查者：

- [完整性与可验收性审查](../../prompts/issue_review_completion.md)：检查是否忠实于原目标、是否遗漏必要行为、成功与重要失败是否可判定。
  不因可以想象更多情况就扩大需求。
- [最小充分性审查](../../prompts/issue_review_minimality.md)：优先删除、复用、合并和缩小；检查是否为方案自己制造的问题建设新机制。
  不要求固定减少百分比，也不能删去真实必要功能。

双方在独立上下文中读取原始需求、同一 Issue、可追溯仓库事实和相关工作，必要时补查决定性事实。
初审完成后，按[证据交流规则](../../prompts/review_exchange.md)互换原报告、回应分歧。两方均无阻断
问题时，也简短确认同一版本和覆盖范围。

意见分为阻断问题、非阻断建议和新增想法。新增想法未经采用不进入任务；双方同意不扩大用户需求。
Issue 作者统一修改正文，两方复核变化和未解决阻断项，给出针对最终版本的结论，再交工程负责人实施。
复核可以引用未变且仍适用的材料。

## 3. 同一工程负责人调查并实施

由[工程负责人](../../prompts/engineering_owner.md)接收审定 Issue、必要共享约定和验收计划，固定需求
版本、代码起点 H0 与采用的流程版本。先只读调查，随后在已有委托内自主实施。普通实现选择自行处理；
目标、关键行为或实际权限需要改变时，提出具体问题供用户决定。

### 按需求逐项实施

可用下面的短提示启动：

```text
按照当前 Issue 完成本次开发。
1. 先读 AGENTS.md，按其文档关系读取适用的 SOP.md、TESTING.md、PR_Checklist.md、interact.md；项目存在 capability_contract.json、docs/business_user_guide.md 时，检查本次需求涉及的公开承诺和使用说明。
2. 从 Issue 提取可逐项验收的需求点（Spec Unit，简称 SU），复用已有编号，在任务 todo 中维护 SU -> 代码改动 -> 测试 -> 文档 的对应关系，随着调查更新。
3. 测试策略与测试证据记录方式以 TESTING.md 为准。
4. 在 todo 中说明哪些测试复用、哪些参数化扩展、哪些需要新增；涉及跨模块行为时，指出哪一条具体 scenario 证明组合路径。一条场景可以覆盖多个 SU，不机械地为每个 SU 或 finding 新增独立测试。
```

预计文件清单随调查更新。在获准范围内自行补读调用方，选择需要新增、修改、删除或重命名的文件。
测试使用实际代码版本、必要依赖和配置，覆盖真实运行路径。普通项目测试随实现更新并接受审核；
关键业务验收判据按第 1 节的需求修订处理。

需要换会话或中断接续时，保留采用版本、实际修改、验证结果、未决问题和下一步；按
[公共约定](../../prompts/coding_common.md)核清原执行与写责任后继续。

## 4. 测试、自审与 Draft PR

优先复用项目真实测试和场景，按缺口参数化扩展或补充断言。跨接口、持久化或用户路径的改动，
选择能证明组合行为的验证。临时探针只有覆盖真实且持续的风险时才进入长期测试。
测试记录关联准确代码版本（候选）、验证定义、相关环境和原始输出。可以复用同一有效验证，
但不能从历史里挑一次 PASS 忽略后续尚未核清的失败或未知结果；覆盖缺口、测试定义、环境或候选变化时
判断受影响部分并补验。稳定性复跑、基线试验和新组合试验有各自目的，不一律视为重复。
成功与失败恢复都引用实际执行记录，保留已发生的失败与未知结果。

实施者完成自审、必要文档和真实验证后，在有效委托内创建或更新 Draft PR。
遵循目标仓库提交政策与 PR 模板，仓库外的临时 PR body 不进入提交；正文写实际改动、验证和限制，
引用 Issue，并把准确候选与验证证据交给两方独立审查者。

## 5. 跨公司 PR 双审、三轮内核实与 Codex 修复

两方分别使用[正确性审查](../../prompts/pr_review_correctness.md)和
[影响与必要性审查](../../prompts/pr_review_impact.md)，共同采用[完整 PR 审核规范](../../prompts/pr_review_system.md)。
每方都在独立上下文中完整审查同一准确候选，随后按[交流规则](../../prompts/review_exchange.md)交换原报告。

- 问题必须有具体触发条件、因果路径、影响和依据；重要主张必要时读调用方、运行已授权验证或复现。
- 两方交换初审发现与结论。需处理的 P0/P1 及其他阻断问题按批进入下述核实流程；非阻断建议单列。
- 未变且仍有效的调查可以复用；新候选必须取得与其内容和范围匹配的两方结论，不机械全仓重读。
- 无问题时可简短交流，不制造争议。事实争议继续补证；产品取舍转有效决定者；关键证据不足保留缺口。
- 普通风格建议不用达成一致。交流有界，超出约定资源或无新证据时说明缺口和下一步，不无限重复。

### 问题核实与证据交流

将同一候选和本批问题交给两个新的独立核实上下文：Codex 使用[事实核实提示](../../prompts/finding_verification_fact.md)，
核实真实性、触发路径、复现和严重度；另一家 LLM 公司的 LLM 使用[影响核实提示](../../prompts/finding_verification_impact.md)，
核实上下游、同类入口、根因及最小充分修复。两方先独立给出核实结果，再交换证据，由 Codex 综合。

独立核实完成后，按[核实流程](../../prompts/finding_verification.md)**最多交流三轮**；每轮回应具体分歧并
保留双方报告。有充分结论可提前结束，三轮后仍缺关键证据则保持 `REWORK_REQUIRED`，列明补证动作。
事实已清楚而涉及产品取舍时交用户决定。
全批反证成立且代码未变时，由正式审查者核对反证并收口。

### 在 Codex 核实会话中修复，再独立复审

成立且需要修复的问题，在上述 Codex 事实核实会话中执行修复。原写者交接实际候选、已有修改与证据，
执行方核对写责任和授权后再开放写入。该会话更新代码、必要测试和文档、PR body 及 Review / Fix Record。
会话无法恢复时，接续的 Codex 先根据原记录核实相关事实，再在该会话修复，并记录接续关系。

修复后的准确候选由两家不同 LLM 公司的 LLM 独立复审；修复者不能自签正式通过。
复审检查真实差异、相关影响及未解决问题，复用仍有效的调查，形成适用于当前候选的两方完整结论。
新发现的阻断问题继续进入核实、交流和修复。核实结论不替代正式 PR 审核。

使用 `PASS`、`REWORK_REQUIRED`、`OWNER_DECISION_REQUIRED`；仅在所需审核完成、无未解决阻断项和
关键证据缺口时 PASS。干净 PR 仍须两方完整初审和实际交流。

## 6. 基线前进、集成接收与按委托交付

原目标和委托仍成立时，可以基于 H0 继续形成原工作的候选。交付时说明实际基线及是否落后，
长任务在合适时机提前整合。主干移动不自动重做全部调查，但可继续开发不等于可以合并或发布。

接收者使用[集成接收提示](../../prompts/integration_acceptance.md)，核对准确交付物、有效双公司结论、
组合验证、阻断项与交付条件，复用有效代码审查与验证证据。

组合已审且不可变的成员时，复用有效成员结论，补组合验证和独立接收判断；每个成员通过不证明组合通过。
集成修改代码、配置、依赖、启用方式或连接关系，导致受审内容或证据适用性实质变化时，对差异和影响补验、
补充跨公司审核。新的合并 PR 仍满足双审要求，可聚焦组合和新增影响；集成者不能自签独立通过。

按有效委托合并、启用或部署，核对实际交付候选并记录结果；已授权的动作自主完成。

## 7. 开发后的 Tech Lead 解读与用户成果验收

可演示候选完成必要验证后，工程负责人使用[开发后解读提示](../../prompts/delivery_explanation.md)，
汇总实际功能、运行机制、开发取舍和验收结果，帮助用户理解成果并体验验收：

```text
本次开发已完成。请站在 Tech Lead 视角，依据实际代码、开发记录和验收结果帮助我理解：
1. 原目标、核心价值，以及现在实际完成到什么程度。
2. 改动前后用户怎样使用；用具体 case 说明输入、操作、结果和关键失败情况。
3. 关键机制如何工作，相关模块如何配合，使我能手动推演正常、失败和恢复过程。
4. 开发中遇到了什么问题，考虑过哪些方案，最终为什么这样选择；哪些复杂度被删除或保留，代价和证据是什么。
5. 回看本次开发，如果减少约 50% 开发量，最小方案是什么；保留什么、放弃什么，哪些判断仍是假设。
6. 按哪一版用户视角验收计划验证，结果是什么，计划为何修改，以及剩余限制和必要后续。
```

每项成果都给出与其复杂度相称的解读；详细 HTML 或流程图用于重大变化、理解需要或用户明确要求。
说明当前候选已测、已审、已合并或已启用的情况，以及仍待用户体验和确认的部分。

按[用户验收提示](../../prompts/user_acceptance.md)执行计划中的真实场景；可运行候选尽早验证，目标环境
特有部分部署后补验，并更新交付说明。用户可从验收计划查看操作、预期结果和执行依据，再决定是否接受。
一个成果跨多个 Issue/PR 时，按完整用户路径验收。

原目标的实现缺口按第 5 节核实、修复与复审；目标、范围或关键语义变化回到 Issue 决定。验收结果引用
实际计划版本，计划修改保留记录。用户接受对应实际的用户决定或明确委托。

## 贯穿规则：需求修订与恢复

新要求记录为修订，由工程负责人判断它属于澄清、原范围补充还是范围变化。当前执行按原输入完成或
停止，在受支持的接续点记录新要求的采用版本及负责承接的工作。停止与撤销直接走停止控制。

旧候选和验证结果保留原适用范围；新要求下可复用的事实明确引用，需要修改或补验的部分继续处理。
新旧工作和流程升级按[版本采用规则](version_adoption.md)处理。

## 必要产物与按需材料

常用产物为采用的 Issue、必要共享约定、代码候选及实际验证、独立审查意见、交付与成果验收记录。
各项记录相互引用，沿用项目已有的保存位置。需要共享规格或迁移方案时，使用
[按需材料](../../prompts/README.md#保留的按需历史材料)并注明适用范围。

## 代码项目核心文档

本仓库中的这些文件是给目标项目继承和项目化的跨语言、跨框架 upstream 基础模板。固定
规范写成完整规则，项目事实 slot 使用 active project-fill marker；目标项目通过最终检查前
必须替换或删除 marker。仅对 sync 工具自身有意义的实现细节放在
`zh/skills/workflow-docs-sync/`，不写入下游模板。

当前模板职责与入口统一见[中文维护入口的目录地图](../../README.md#目录地图)，此处不另维护
一份容易漂移的职责清单。

## Workflow Docs Sync

用户只调用一次 `$workflow-docs-sync`，只提供目标仓库、必选的 `zh` / `en`，以及成功后是否
创建 draft PR。Skill 内部解析 canonical upstream checkout；无法定位时使用仓库外临时 shallow clone，
并在整轮固定目标 HEAD 与上游 SHA。

- 写文档前至少以 `git ls-files -z` 建立范围；事实与政策的核验方法遵循
  [canonical Skill](../../skills/workflow-docs-sync/SKILL.md)，不在本说明重复定义。
- Architecture、Capability / User Behavior、Testing、Governance 是覆盖维度，不是固定 Agent
  拓扑。主 Agent 可独立完成，也可按模块、调用链、风险或证据类型动态委派只读调查。
- 主 Agent 是目标工作区唯一写入者。全量质疑九份文档后只改错误、缺失或失真部分；正确
  内容保持零 diff，不输出 disposition ledger、run state 或 receipt。
- 测试环境由真实命令、副作用、CI 能力和项目政策决定；记录实际环境、隔离、残留和清理，
  不把一种环境实现固化成跨项目规则。
- 复核优先使用 fresh-context、blind-first independent reviewer；不可用时明确标记
  self-review，不能冒充独立复核。BLOCKER 与无需产品决策的 actionable WARN 修复后复核。
- `sync_docs.py prepare` 先验证固定 object 与 language 下九份 UTF-8 source template 及非 PR
  active-marker invariant，再补齐缺失模板；`check` 重读同一 pinned source，并只读验证最终
  HEAD、dirty 范围、editable path 无 index/worktree 分叉、九份普通 UTF-8 非空文件、JSON
  object、active marker，以及存在时为 UTF-8 的 `.gitignore`。最终 bytes 的 whitespace 使用
  临时非 Git 目录和固定 Git 规则，不继承目标仓库 attributes。Checker 不解析 Markdown，也不
  验证目标项目 capability、测试层级或文案质量。单一 final-bytes 路径依赖同步范围外 dirty
  path 始终被拒绝；若未来放宽 allowlist，必须重新评估 whitespace 覆盖。index/worktree 分叉
  拒绝按 path 聚合两侧 status，并覆盖 index 删除或 rename source 后同路径 untracked / ignored
  重建；它消除的是两个发布候选，不是第二套 whitespace 检查。
- 安装器在任何删除或复制前验证 source/目标祖先、source symlink、Claude frontmatter 的标准
  分隔和会被复制的 ignored source residue；只精确清理废弃 reviewer Skill，不保存安装状态或
  来源 receipt。
- PR body 临时 Markdown 始终位于仓库外。commit、push 和 draft PR 创建只在用户要求且检查
  成功后，由通用 GitHub 发布能力完成。
- 最终机械检查只证明最终仓库状态，不证明调查、测试或复核执行历史。

维护入口：

- `zh/skills/workflow-docs-sync/SKILL.md`
- `zh/skills/workflow-docs-sync/agents/openai.yaml`
- `zh/skills/workflow-docs-sync/evals/README.md`
- `zh/skills/workflow-docs-sync/scripts/sync_docs.py`
- `zh/scripts/install_skills.py`
- `tests/test_workflow_docs_sync.py`

这些规则属于上游 sync 工具，不写入下游项目继承的核心模板。

## 上游双语语义等价审核 SOP

本 SOP 只适用于维护 `wlvh/coding-workflow` 上游仓库，不写入下游项目继承的
`AGENTS.md`、`architecture.md`、`TESTING.md`、`PR_Checklist.md` 或 `SOP.md` 模板。
目标是定期确认中文锚点文档的语义变化已经被英文派生路径吸收，或已经显式记录
`en-pending` follow-up。

触发节奏：每月最后一个工作日执行一次；如果本月修改过任意中文锚点核心文档、
`zh/README.md` 或 `zh/skills/workflow-docs-sync/`，则必须在下一次主线 PR 合并前执行。

### Step 1：确认审核范围

- 做什么：列出本轮要审核的中英配对文件，只覆盖本仓库声明的双语入口、模板和 sync 工具文档。
- 去哪看：`zh/README.md` 的“目录地图”、`sync_docs.py` 的 `CORE_FILES` 和中英模板目录。
- 做完如何验收：每一项必须是 `zh/路径 -> en/同名路径`；Skill 实现只在 canonical
  `zh/skills/workflow-docs-sync/` 维护，不创建英文实现副本，也不得出现 `.en.md`、
  `.en.json`、`.en.sh` 文件路径。

### Step 2：收集中英文变更证据

- 做什么：对每个配对文件查看自上次审核点以来的中文 diff 和英文 diff；没有明确上次审核点时，使用用户指定 base，或使用当前 PR base。
- 去哪看：`git log <base>..HEAD -- <path>`、`git diff <base>..HEAD -- <path>`、PR body 的“文档影响 / Review / 修复记录”。
- 做完如何验收：每个配对文件都有状态：`stable`、`zh_only`、`en_only`、`both`；`zh_only` 和 `en_only` 必须进入人工判断。

### Step 3：逐项判断语义等价

- 做什么：以中文 diff 为锚，判断英文是否覆盖同一流程、能力边界、验收不变量、路径和拒绝 / 追问规则；`both` 状态重点判断英文是否是中文语义派生，而不是独立创作。
- 去哪看：中文文件当前内容、英文文件当前内容、`zh/README.md` 的中文锚点规则和
  `zh/skills/workflow-docs-sync/SKILL.md` 的领域语义。
- 做完如何验收：每个配对文件得到一个结论：`ok`、`missing translation`、`stale en`、`contradiction`、`intentionally pending`；除 `ok` 外都必须记录具体文件、段落和建议处理方式。

### Step 4：生成审核结论

- 做什么：把本轮审核结果写成可转交的 issue、PR comment 或本地审查记录。
- 去哪看：本节 SOP、Step 2 的 git 证据、Step 3 的逐项判断。
- 做完如何验收：结论至少包含审核 base / HEAD、审核日期 UTC、配对文件清单、每项状态、需要修复的英文段落、是否存在 `en-pending`、下一步 owner。

### Step 5：闭合处理

- 做什么：对 `missing translation`、`stale en`、`contradiction` 生成修复任务；对暂不修的项确认 PR body 或 issue 中有 `en-pending` 和 follow-up 边界。
- 去哪看：本轮审核结论、相关 PR body 或 issue。
- 做完如何验收：所有非 `ok` 项都有明确 follow-up；如果本轮完成修复，重新执行 Step 2 和 Step 3，直到结论为 `ok` 或 `intentionally pending`。

反向规则：任何对 `AGENTS.md`、`TESTING.md`、`PR_Checklist.md`、`SOP.md`、
`architecture.md`、`interact.md`、`capability_contract.json` 或
`docs/business_user_guide.md` 的修改，如果只对本仓库 sync 工具特殊场景有用、对下游
继承项目无意义，必须迁移到 `zh/README.md`、`zh/docs/development_workflow/` 或
`zh/skills/workflow-docs-sync/` 后再合入。

配套边界：`en-pending` 只属于维护 `wlvh/coding-workflow` 上游仓库时的双语治理语境，
不得作为通用目标仓库审计 BLOCKER，避免中文或英文单一路径项目被误拦截。
