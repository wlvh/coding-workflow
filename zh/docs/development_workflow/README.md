# 编程工作流

完整决策见
[DEC-008](decisions.md#dec-008开发工作流采用复杂度守恒与可退役实验机制)。

## 主流程

1. **确定需求**

2. **网页端 Pro 模型制定 `FSD Core Contract`**
   使用长 prompt：[prompts/fsd_core_contract.md](../../prompts/fsd_core_contract.md)
   权威文档列表：
   * .github/pull_request_template.md
   * docs/business_user_guide.md
   * AGENTS.md
   * architecture.md
   * capability_contract.json
   * interact.md
   * PR_Checklist.md
   * SOP.md
   * TESTING.md

3. **Target State Bridge Agent 根据 `FSD + 当前仓库代码 + 仓库权威文档` 产出 `Repo Impact Forecast` 和 `Target State Bridge`**
   * Pro 模型产出。
   * 使用长 prompt：[prompts/target_state_bridge.md](../../prompts/target_state_bridge.md)

4. **Issue Agent 写 Issue**
   使用长 prompt：[prompts/issue_agent.md](../../prompts/issue_agent.md)
   目标：把 `FSD`、`Repo Impact Forecast` 和 `Target State Bridge` 固化成唯一实施入口。需要 owner 判断的范围、风险、成本、权限或失败语义必须保持显式，不得在模型合意中静默消失。

5. **Codex 与 Claude Code 从正交镜头审核 Issue，再形成一份合意 Issue**

   **需求完成 / 验收镜头：**

   ```text
   从需求完成和验收可判定的角度审核当前 Issue。

   重点判断：核心用户目标是否闭合；Scope / Non-goals 是否明确；成功、失败、拒绝、降级和人工升级是否可判定；Acceptance Checklist 是否能明确判断完成；是否有本应由 owner 决定的事项被工程方案静默拍板。

   ```

   **工程量 / 最小充分镜头：**

   ```text
   从工程量、长期复杂度和最小充分性的角度审核当前 Issue。

   重点判断：是否可以减少约一半开发量而仍保留核心价值；是否在为方案自己制造的问题继续写代码；测试能否复用，能够构建端到端的测试体系。有没有脱裤子放屁的开发。

   ```

   由第 4 步的 Issue Agent 执笔更新 Issue；两个镜头只提供意见，不直接编辑 Issue。

6. **高风险 Issue 在 Coding 前执行 Issue Readback**

   Readback 使用现有 Tech Lead 解释能力，不成为新权威：

   ```text
   当前 Issue 尚未开始编码。请站在 Tech Lead 视角详细解读，目标是让我真正理解它将如何工作，而不是复述原文。

   必须说明：
   1. 一句话目标、核心价值和明确非目标；
   2. 每个工作包为什么存在，删除后会失去什么；
   3. 预计运行时因果链；
   4. 最不直观的三个机制；
   5. 主要长期复杂度和维护代价；
   6. 如果减少约 50% 开发量，最小方案是什么；
   7. 哪些测试复用、哪些参数化，以及哪一条 scenario 覆盖端到端组合；
   8. 当前仍需要 owner 决定什么；
   9. 哪些是 Issue / 仓库事实，哪些只是工程推断，哪些尚未验证。

   本解读不是新的产品或工程权威。发现歧义时必须回写 Issue，不得只在解读中形成新要求。
   ```

   Readback 完成后，由 owner 明确批准当前 Issue；未批准，或 Issue 的 Scope / Non-goals、Acceptance Checklist、工作包边界、核心失败 / 恢复语义、Owner Decisions 发生实质变化时，不得进入第 7 步。

7. **Coding Agent 按批准的 Issue 开发**

   ```text
   按照当前已批准 Issue 完成本次开发。
   1. 读取 AGENTS.md / SOP.md / TESTING.md / PR_Checklist.md / interact.md；如果项目存在 capability_contract.json / docs/business_user_guide.md，也必须按 AGENTS.md 的文档关系检查。
   2. 从 Issue 提取 Spec Unit，生成 SU -> 代码改动 -> 测试 -> 文档 的 todo list。
   3. 测试策略与测试证据记录方式以 TESTING.md 为准。
   4. 在 todo list 中说明哪些测试复用、哪些参数化扩展，以及哪一条 scenario 证明跨模块组合路径；不得机械地为每个 SU 或 finding 新增独立测试。
   5. 若发现批准后的 Issue 已发生实质变化，停止并要求重新批准，不得自行解释为仍获授权。
   ```

8. **Coding Agent 自审并提交 Draft PR**

   正式代码审核系统 prompt：[prompts/pr_review_system.md](../../prompts/pr_review_system.md)

   PR 提交短 prompt：

   ```text
   重新以 PR 审核的态度审核你的新增代码；发现问题后先验证是否真实存在，再决定是否修复。
   先判断本地是主干还是分支；如在主干，则按仓库政策创建分支。然后在既有分支的既有 PR 上提交本地全部目标范围代码。

   要求：
   1. 遵守 PR_Checklist.md。
   2. 遵守仓库当前 commit 策略；单 commit 只是可替换的团队默认。
   3. 每轮 review / 修复都更新 PR body 的 Review / Fix Record；但发散闸门不依赖作者 body 才能工作。
   4. 根据 `.github/pull_request_template.md` 在仓库外创建临时 Markdown body，并覆盖已有 PR 和本地全部修改内容。
   5. 测试策略与测试证据记录方式以 TESTING.md 为准。

   临时 PR body 位于仓库外，不进入目标工作树或 commit。
   ```

9. **独立 PR Review：先审核当前 exact head，再判断历史模式**

   Reviewer 先 blind-first 读取当前 exact head、Issue、仓库权威、完整 diff、测试与 artifact，形成并冻结本轮初始 findings；之后才读取前两轮审核报告或 GitHub review comments，判断是否重复根因或发散。作者总结和 PR body 只是证据之一，不能替代当前事实，也不是发散闸门的唯一地基。

   Reviewer 必须在结论中区分实测复现、读码推断和未检查；环境或权限阻塞属于未检查的原因。未检查内容若可能改变 P0/P1、`SPEC_GAP` 或授权结论，不得 PASS，必须输出 `REQUEST_EVIDENCE`。

10. **Finding 由两个正交镜头验证；根据证据选择修复、退回规格或提交 owner**

   **模型 A：事实 / 复现镜头。** 它不读取历史审核或作者修复叙事，只读取当前 exact head、当前 finding、Issue 和仓库权威。

   ```text
   只判断当前 finding 是否真实成立。确认现实可达入口、前置条件、调用链、最小复现或定向测试、实际后果、现有测试为何未拦截和严重度。

   输出只能是：CONFIRMED / REFUTED / REQUEST_EVIDENCE。
   不要设计大范围修复。
   ```

   **模型 B：实例 / 系统性镜头。** 它先不读历史，固定当前责任边界、state owner、持久化协议和副作用链的初始分类；随后才读取前两轮审核报告判断是否成类或发散。

   ```text
   假设 finding 成立，判断它是孤立实例还是系统性失效。检查上游、当前模块与下游影响面；同类入口或相邻状态；当前建议是在修根因还是只修样例；最小闭合边界；能否扩展已有机制；测试应复用还是参数化；是否属于规格缺口或 owner decision。

   输出只能是：LOCAL_FIX / SYSTEMIC_FIX / SPEC_REVISION_REQUIRED / OWNER_DECISION_REQUIRED。
   ```

   两种走向与直觉相反，必须遵守：`SPEC_REVISION_REQUIRED` 时停止改代码、退回 Bridge；`OWNER_DECISION_REQUIRED` 时只停止受阻工作包，未受阻部分继续。其余组合按 token 字面执行。

   删除“若干轮后以 Codex 为准”。分歧由可复现行为、代码 / 配置 / 测试 / artifact、已冻结 Issue 和 owner 决策裁决；双方都无可复现证据时保留 `REQUEST_EVIDENCE`，不强行裁定。

   **发散闸门：**满足任一条件时停止逐 finding 补丁，并输出 `SPEC_REVISION_REQUIRED`：

   1. 上一轮修复直接制造本轮新的 P0/P1；
   2. 连续两轮新增 P0/P1 落在同一 runtime entrypoint、state owner、persistence protocol 或 external side-effect execution chain；
   3. 同一执行链完成一轮修复后，下一轮仍需新增 durable state、checkpoint、持久化 artifact、recovery branch 或 terminal semantics。

   触发后返回 Bridge 完整枚举受影响执行链。

   **Owner Decision 输出契约：**必须说清要决定什么、作出决定所需证据能否在当前权限 / 安全 / 成本约束下合法取得、阻塞哪些工作包与不阻塞哪些，以及 owner 未决前的安全默认。若证据无法合法取得，结论是 `SPEC_REVISION_REQUIRED`。

   最终出口只能是：

   - `PASS`；
   - `REWORK_REQUIRED`；
   - `SPEC_REVISION_REQUIRED`；
   - `OWNER_DECISION_REQUIRED`；
   - `REQUEST_EVIDENCE`。

11. **终验、合并、合并后解读与用户验收**

   `PASS` 后按目标项目的独立验收与合并政策执行。仓库中的 `/claude-merge-check` 和 Issue closure FSD acceptance 可以作为可选工具使用，但不再列为当前通用主流程或核心产物。

   **合并后 Tech Lead 机制解读**

   ```text
   当前 PR XX （对应issue XX） 已经完成。请站在 tech lead 视角详细评估，但你的目标不是写一篇“好看的评审总结”，而是让我真正理解这个 PR 是怎么工作的。

   A. 执行摘要
   - 这个 PR 的一句话定性
   - 它实际完成的 3~5 个关键动作

   B. 改动地图
   对每个关键动作都按下面格式展开：
   1. 代码位置（文件 + 函数）
   2. 改动前是什么
   3. 改动后是什么
   4. 运行时因果链（谁调用谁，数据怎么流动）
   5. 为什么这样改能达到目标
   6. 代价/复杂度上升在哪里

   C. 非直观点强制拆解
   对回答中最不直观的 3 个点，必须单独做“机制层解释”：
   - 禁止抽象词，必须讲到具体 Python 机制
   - 必须给 before/after 伪代码
   - 必须说清“它影响什么，不影响什么”

   D. 证据约束
   - 区分“代码事实”和“你的判断”
   - 没有从代码直接验证到的内容，明确标记为推断

   E. 输出风格约束
   - 不要只写评价，要写机制
   - 不要只写价值，要写代价
   - 不要只写结论，要写证据链
   ```

   **用户可感知变化与文档检查**

   ```text
   这个PR合并入主干后用户有什么可感知的变化吗，用户如何利用这次PR的开发成果，以AGENTS.md为首的文档提供了很好的指引吗？AGENTS.md 及其内联的文档有没有需要更新的地方？综合评估当前代码分支这个 PR 以什么方式完成了什么任务，给这个项目带来了什么改变和影响，下一步的未来展望是什么？
   ```

   上述两份解读存档在 PR 评论区。编码前 Issue Readback 解释的是计划，不替代这里基于最终代码和真实交付结果的解读。

   **用户视角验收计划**

   验收计划需要 GPT 网页版和 Claude Code 达成合意。

   ```text
   针对这个issue和pr，制定一个验收计划，如何以用户体验的角度来验收这次的PR
   ```

   将验收计划存档在 PR 评论区，并交给 Codex；必要时结合 Playwright 等交互工具实际执行。该验收可能直接产生新的开发计划。

## 实验机制重审

发散闸门、条件性 Issue Readback 和 Owner Decision 输出契约先作为实验机制。每项累计 3 个适用 PR 后，按 [DEC-008](decisions.md#实验机制重审与退役) 分别输出 `PROMOTE`、`MODIFY` 或 `RETIRE`；从未触发，或触发后没有改变任何参与者下一步动作的机制，默认退役，除非有新的具体风险证据。

## 核心产物

- `FSD Core Contract`：把需求翻译成可实现、可测试、可审核的契约。
- `Repo Impact Forecast`：预测 FSD 与当前仓库的真实触点、风险、文档和测试影响。
- `Target State Bridge`：定义开发完成后用户 / 调用方应该看到什么状态，以及如何验证。
- `Issue`：把契约、范围、任务拆解、文档更新预测、测试更新预测、验收条件和 Owner Decisions 固化。
- 条件性 Issue Readback：帮助 owner 在编码前理解并批准具体 Issue 修订；不是第二套权威。
- 仓库外 PR body Markdown：由 `.github/pull_request_template.md` 派生，不进入目标工作树或 commit；是 review 和通用 GitHub 发布能力的输入。
- `Workflow Docs Sync`：用户一次调用完成全量事实重建、最小必要改写、真实测试、
  fresh-context independent review 或诚实 self-review，以及最终仓库检查。

## 代码项目核心文档

本仓库中的这些文件是给目标项目继承和项目化的跨语言、跨框架 upstream 基础模板。固定
规范写成完整规则，项目事实 slot 使用 active project-fill marker；目标项目通过最终检查前
必须替换或删除 marker。仅对 sync 工具自身有意义的实现细节放在
`zh/skills/workflow-docs-sync/`，不写入下游模板。

- `AGENTS.md`：agent 权威入口、稳定模块地图、影响规则与项目约定。
- `architecture.md`：系统目的、运行时主流程、边界、状态、失败与副作用。
- `capability_contract.json`：能力边界、职责边界、agent 行为承诺的机器可读真相源。
- `interact.md`：用户可观察行为与验收不变量。
- `docs/business_user_guide.md`：面向首次接触业务人员的教学派生文档。
- `TESTING.md`：测试入口、测试分层、隔离、测试证据与 alignment 边界。
- `PR_Checklist.md`：PR todo、Git diff、测试、文档、review closure 与仓库外 body 边界。
- `SOP.md`：标准流程骨架，只做入口，不重复规范。
- `.github/pull_request_template.md`：PR body 的长期模板。

## Workflow Docs Sync

用户只调用一次 `$workflow-docs-sync`，只提供目标仓库、必选的 `zh` / `en`，以及成功后是否
创建 draft PR。Skill 内部解析 canonical upstream checkout；无法定位时使用仓库外临时 shallow clone，
并在整轮固定目标 HEAD 与上游 SHA。

- 写文档前至少以 `git ls-files -z` 建立范围，从代码、配置、测试、committed artifacts、
  可重复运行结果和必要 Git 历史全量重建事实；现有文档与上游模板只是 hypotheses。
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
