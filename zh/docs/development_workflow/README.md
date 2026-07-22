# 编程工作流

## 主流程

1. **确定需求**

2. **网页端 Pro 模型制定 `FSD Core Contract`**
   使用长 prompt：[prompts/fsd_core_contract.md](../../prompts/fsd_core_contract.md)
   备注：当前默认前提是 GPT Pro 不能自由探索本地代码和 GitHub，所以 FSD 先做黑盒契约。本阶段可以给AGENTS.md及其内链的文档，但不能直连代码仓库。
   权威文档列表（以后需要想个办法防止漂移）：
   * .github/pull_request_template.md
   * docs/business_user_guide.md
   * AGENTS.md
   * architecture.md
   * capability_contract.json
   * interact.md
   * PR_Checklist.md
   * SOP.md
   * TESTING.md

4. **Target State Bridge Agent（codex） 根据 `FSD + 当前仓库代码 + 仓库权威文档` 产出 `Repo Impact Forecast` 和 `Target State Bridge`**
  * 如果GPT 5.4 Pro模型可以在不接触本地代码和GitHub的情况下产出也能由它代为产出
  * 使用长 prompt：[prompts/target_state_bridge.md](../../prompts/target_state_bridge.md)

5. **Issue Agent （codex）写 issue**
   使用长 prompt：[prompts/issue_agent.md](../../prompts/issue_agent.md)
   目标：把 `FSD`、`Repo Impact Forecast` 和 `Target State Bridge` 固化成开发契约。
   完成后让codex和claude code互相讨论到达成合意。
7. **Coding Agent（codex） 按 issue 开发**
   短 prompt：

   ```text
   按照当前 issue 完成本次开发。
   1. 读取 AGENTS.md / SOP.md / TESTING.md / PR_Checklist.md / interact.md；如果项目存在 capability_contract.json / docs/business_user_guide.md，也必须按 AGENTS.md 的文档关系检查。
   2. 从 issue 中提取 Spec Unit，生成 SU -> 代码改动 -> 测试 -> 文档 的 todo list。
   3. 测试策略与测试证据记录方式以 `TESTING.md` 为准。
   ```

   备注：我在这里没有提FSD/Repo Impact Forecast/Target State Bridge，宪法文件已经转为issue。而且也没有提供编程开发的具体模板，因为我相信llm擅长做这个，issue也能做好制约。

8. ** codex 负责代码审核**
   预审核短 prompt：

   正式审核系统 prompt：[prompts/pr_review_system.md](../../prompts/pr_review_system.md)
   正式审核任务短 prompt：

   ```text
   对 XX 项目的 PR XX（最新head XX）进行严格详细全面的代码审查。PR_BODY.md 是你重要的参考材料。重要问题需要实际运行代码来验证你的猜想，没有调查就没有发言权。并额外检查是否遵守 TESTING.md / AGENTS.md / PR_Checklist.md / SOP.md / interact.md。
   对应issue：《》
   PR审核指南：《》
   ```
   审核完成的后的追问：按照PR审核指南，面向不熟悉本项目底层代码的程序员详细介绍你的发现。
   

   PR 提交短 prompt：

   ```text
   重新以 PR 审核的态度审核你的新增代码，如有问题先验证是否真实存在，再决定是否修复。
   先判断本地是主干还是分支，如果是主干则先创建分支并。然后在既有分支的既有 PR 上提交本地全部代码，
   要求：
   1. 遵守 PR_Checklist.md。
   2. PR 对外保持 1 个 commit。
   3. 每轮 review / 修复都必须更新 PR_BODY.md 的“Review / 修复记录”。
   4. PR_BODY.md 必须根据 `.github/pull_request_template.md` 填写，并覆盖已有 PR （如果本次对话才创建分支可以跳过）和本地全部修改内容。
   5. 测试策略与测试证据记录方式以 TESTING.md 为准。

   备注：
   - PR_BODY.md 是本地临时产物，不提交仓库。
   - PR_BODY.md 是重要的代码审核材料之一。
   - PR 审核指南：《》
   ```

9. **如果 review 有问题，先验证问题是否真实存在，再决定是否修**
   给 Codex 和 claude code 的短 prompt：

   ```text
   先不动代码，先检查实习生给出的问题是否真实存在。重要问题需要通过代码阅读、最小复现、定向测试或接近真实使用路径的验证来确认；没有调查就没有发言权。

   如果问题存在，请先输出分析，不要直接修复。分析必须包含：

   1. 检测：去对应PR描述检查是否之前修复过类似问题，如果有，如何制定一个端到端的验收计划来杜绝重复返工。
   2. 影响面：这个问题的上游输入、当前模块、下游调用方是否受影响；是否存在同类入口或相邻场景也需要一起检查。
   5. 同步项：判断是否需要同步测试说明、用户文档、架构/流程文档、PR 描述或 Review / 修复记录；如果不需要，也要说明原因。

   实习生的发现：《》
   ```

   * 执行顺序：先让codex 负责PR的代码审核，如果review 出问题。把问题发给 Codex 和 Opus 分别判断，再把 Opus 的意见发给 Codex 要求出综合分析版本。
   * 处理分歧：如果双方分歧仍然很大，再把 GPT 5.4 对 Opus 的反驳发给 Opus，让 Opus 重新分析后按自己的方案执行。
   * 在验证阶段codex和cc经常会有不同意见，在这里交互意见最多三次，然后以codex的意见为准，在codex验证的对话里直接输入‘按照你的观点进行修复‘
   * 修复后：继续复用“PR 提交短 prompt”。然后新开codex对话进行pr审核，一直到没有P0和P1问题为止。P2问题可以接受。
   * 备注：同一个 PR 的 patch 不需要每次重新完整粘贴给 GPT，可以在原对话里覆盖最新 patch，避免上下文过时。
   * 完整顺序：在具体操作中，先让codex 负责PR的代码审核，如果review 有问题，用第8节的prompt分别交给codex（新对话）和claude code验证，这里实习生的发现就是codex审核pr给出的发现。在验证阶段codex和cc经常会有不同意见，在这里交互意见最多三次，然后以codex的意见为准，在codex验证的对话里直接输入‘按照你的观点进行修复‘，然后在这个对话继续‘重新以 PR 审核的态度审核你的新增代码，如有问题先验证是否真实存在，再决定是否修复’这个pr提交环节。然后新开codex对话进行pr审核，一直到没有P0和P1问题为止。P2问题可以接受。
   * Finding 并集销号：跨 reviewer 或跨会话接力前，必须把历史 Finding Ledger、全部 GitHub review thread 和本轮新增 finding 做并集。每个来源 ID 都必须保留，并明确标记为 `confirmed`、`rejected`、`merged_as_duplicate:<ID>`、`downgraded:<新严重度>` 或 `needs_human`；已修复项另记关闭证据。任何 finding 从后续清单静默消失都视为流程错误，在并集未逐项销号前不得声明“无剩余问题”。

11. **如果 review 没有问题（定义为没有P0/P1级别发现），在 PR 评论区输入 `/claude-merge-check`**（这个环节暂时放弃，反复的PR审查已经足够）
   自动化文件：[.github/workflows/claude-merge-readiness.yml](../../../.github/workflows/claude-merge-readiness.yml)
   作用：做 merge-readiness 检查，而不是重复做 code review。
   通过规则：无问题则在 PR 评论区输入 `/claude-merge-check`，通过后再合入主干。

12. **PR 合并后，用网页端 GPT 的 apps 功能做 tech lead 总结**
   总结短 prompt：

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

   追问短 prompt：

   ```text
   这个PR合并入主干后用户有什么可感知的变化吗，用户如何利用这次PR的开发成果，以AGENTS.md为首的文档提供了很好的指引吗？AGENTS.md 及其内联的文档有没有需要更新的地方？综合评估当前代码分支这个 PR 以什么方式完成了什么任务，给这个项目带来了什么改变和影响，下一步的未来展望是什么？
   ```
   存档在PR评论区 
   
13. **Issue 关闭前，再从主干代码检查 FSD 是否真正开发完成**（这个环节暂时放弃，因为通过率100%，而且 12.如何以用户的角度来验收这次的 PR能发现更精准的问题）
    使用长 prompt：[prompts/issue_closure_fsd_acceptance.md](../../prompts/issue_closure_fsd_acceptance.md)
    目的：从主干代码倒查 issue 中的每个 `Spec Unit` 是否已实现，并强制输出 `Updates to FSD`（如有偏差）。

14. **再问 GPT 网页版：如何从用户视角验收这次 PR**
    
    验收计划需要GPT网页版和claude code达成合意。
    
    短 prompt：

   ```text
   针对这个issue和pr，制定一个验收计划，如何以用户体验的角度来验收这次的PR
   ```
 
 存档在PR评论区
 
 下一步：把这份用户视角验收建议交给 Codex，必要时结合 Playwright 等交互工具，真的走一遍验收。
 备注：这一步经常有可能直接产生新的开发计划。

## 核心产物

- `FSD Core Contract`：把需求翻译成可实现、可测试、可审核的契约。
- `Repo Impact Forecast`：预测 FSD 与当前仓库的真实触点、风险、文档和测试影响。
- `Target State Bridge`：定义开发完成后用户 / 调用方应该看到什么状态，以及如何验证。
- `Issue`：把契约、范围、任务拆解、文档更新预测、测试更新预测、验收条件固化。
- `PR_BODY.md`：本地临时 PR body 草稿，由 `.github/pull_request_template.md` 生成，不提交仓库；是 review 的重要输入材料。
- `Merge Readiness Report`：判断当前 PR 是否具备合并条件。
- `FSD 完备性验收报告`：Issue 关闭前的最后一道契约核查。
- `Workflow Docs Sync`：用户一次调用完成代码地图、四领域只读分析、主 Agent 统一改写、
  内部只读审计、测试和最终仓库检查。

## 代码项目核心文档

本仓库中的这些文件是给目标项目继承和项目化的 upstream 模板 / 样本文档。开发 sync
工具时，不因为工具实现细节去改写 `AGENTS.md`、`TESTING.md`、`PR_Checklist.md`、
`architecture.md` 这类模板；sync 工具自身说明和实现放在
`zh/skills/workflow-docs-sync/`。例外是 `.github/pull_request_template.md`：它是长期
PR body 模板，可以直接继承 upstream。

- `AGENTS.md`：agent 工作入口、文件简介、代码规范与文档关系。
- `architecture.md`：系统架构、模块边界、数据流、架构不变量与扩展点。
- `capability_contract.json`：能力边界、职责边界、agent 行为承诺的机器可读真相源。
- `interact.md`：用户可观察行为与验收不变量。
- `docs/business_user_guide.md`：面向首次接触业务人员的教学派生文档。
- `TESTING.md`：测试策略、测试分层、测试证据与 contract alignment 测试原则。
- `PR_Checklist.md`：PR 提交、commit / push、PR body 使用规则。
- `SOP.md`：标准流程骨架，只做入口，不重复规范。
- `.github/pull_request_template.md`：PR body 的长期模板。

## Workflow Docs Sync

用户只调用一次 `$workflow-docs-sync`，只提供目标仓库、可选 `zh` / `en` 和可选 draft
PR 意图。Skill 内部解析 canonical upstream checkout；无法定位时使用仓库外临时 shallow
clone，并在整轮固定同一上游提交。

- 主 Agent 是目标工作区唯一写入者，先建立真实代码地图。
- Architecture、Capability / User Behavior、Testing、Governance 四领域分析只读并只在
  当前会话返回发现；无 subagent 平台由主 Agent 按四个隔离章节顺序执行。
- 主 Agent 统一修改九份核心文档，再由内部只读对抗性审计检查事实、跨文档闭合和验证
  层级；BLOCKER 与可行动 WARN 修复后进行轻量复审。
- 主 Agent 实际运行目标项目必要测试并记录命令与结果。
- `sync_docs.py prepare` 只补齐缺失模板；`check` 只读验证最终 HEAD、dirty 范围、九份
  文件、编码、JSON、标题、模板残留、固定上游差异和 whitespace。
- 同步过程不读取、创建、改写或删除仓库内 `PR_BODY.md`，也不创建工单、模板镜像或运行状态。
  commit、push 和 draft PR 创建由通用 GitHub 发布能力在检查成功后完成。
- 最终机械检查只证明最终仓库状态，不证明四领域分析、审计或测试曾运行。

维护入口：

- `zh/skills/workflow-docs-sync/SKILL.md`
- `zh/skills/workflow-docs-sync/references/sections.md`
- `zh/skills/workflow-docs-sync/references/audit.md`
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
  `zh/skills/workflow-docs-sync/references/` 的领域语义。
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
