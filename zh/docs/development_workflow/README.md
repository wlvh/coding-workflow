# 编程工作流

完整决策见
[DEC-008](decisions.md#dec-008开发工作流采用复杂度守恒与可退役实验机制)。

## 主流程

1. **确定需求**

2. **网页端 Pro 模型制定 `FSD Core Contract`**
   使用长 prompt：[prompts/fsd_core_contract.md](../../prompts/fsd_core_contract.md)

   备注：FSD 只钉死用户可观察的需求契约，不根据当前代码预设实现；代码触点、兼容性和落地路径留给下一步 Target State Bridge，避免需求被现状绑死。

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

   备注：Bridge 负责把黑盒 FSD 与当前仓库事实对齐，补齐代码、兼容性、文档和测试上下文；它区分预测与承诺，不改写 FSD 的用户目标。

4. **Issue Agent 写 Issue**
   使用长 prompt：[prompts/issue_agent.md](../../prompts/issue_agent.md)
   目标：把 `FSD`、`Repo Impact Forecast` 和 `Target State Bridge` 固化成唯一实施入口。需要 owner 判断的范围、风险、成本、权限或失败语义必须保持显式，不得在模型合意中静默消失。

   备注：Issue 是后续开发的唯一实施入口，避免 Coding Agent 同时面对多份可能漂移或互相冲突的上游指令。需要 owner 取舍的事项也保留在 Issue 中，后续 PR body、review comment 和聊天只引用 Issue，不另写一套可能漂移的版本。

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

   备注：两个镜头分别防止“需求没做完”和“工程做过头”，不是让两个模型重复投票。

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

   备注：Readback 的作用是让 owner 在编码前真正理解复杂 Issue；它不建立新的批准状态，也不替代 Issue 本身。

7. **Coding Agent 按 Issue 开发**

   ```text
   按照当前 Issue 完成本次开发。
   1. 读取 AGENTS.md / SOP.md / TESTING.md / PR_Checklist.md / interact.md；如果项目存在 capability_contract.json / docs/business_user_guide.md，也必须按 AGENTS.md 的文档关系检查。
   2. 从 Issue 提取 Spec Unit，生成 SU -> 代码改动 -> 测试 -> 文档 的 todo list。
   3. 测试策略与测试证据记录方式以 TESTING.md 为准。
   4. 在 todo list 中说明哪些测试复用、哪些参数化扩展，以及哪一条 scenario 证明跨模块组合路径；不得机械地为每个 SU 或 finding 新增独立测试。
   ```

   备注：这里不再重复传入 FSD / Repo Impact Forecast / Target State Bridge，因为它们已经固化进 Issue；也不提供通用开发模板，具体实现由当前仓库事实和 Issue 约束。

8. **Coding Agent 自审并提交 Draft PR**

   正式代码审核系统 prompt：[prompts/pr_review_system.md](../../prompts/pr_review_system.md)

   PR 提交短 prompt：

   ```text
   重新以 PR 审核的态度审核你的新增代码；发现问题后先验证是否真实存在，再决定是否修复。
   先判断本地是主干还是分支；如在主干，则按仓库政策创建分支。然后在既有分支的既有 PR 上提交本地全部目标范围代码。

   要求：
   1. 遵守 PR_Checklist.md。
   2. 遵守仓库当前 commit 策略；单 commit 只是可替换的团队默认。
   3. 每轮 review / 修复都更新 PR body 的 Review / Fix Record。
   4. 根据 `.github/pull_request_template.md` 在仓库外创建临时 Markdown body，并覆盖已有 PR 和本地全部修改内容。
   5. 测试策略与测试证据记录方式以 TESTING.md 为准。
   ```

   备注：
   - 临时 PR body 位于仓库外，不进入目标工作树或 commit。
   - PR body 是正式代码审核的重要参考材料之一，由通用 GitHub 发布能力读取。

9. **Codex 负责代码审核**

   正式审核系统 prompt：[prompts/pr_review_system.md](../../prompts/pr_review_system.md)

   正式审核任务短 prompt：

   ```text
   对 XX 项目的 PR XX（最新 head XX）进行严格详细全面的代码审查。在评估代码时不但要评估开发是否符合 issue，还要评估有没有过度开发，是否可以在架构层级精简（功能可以提前开发，但是不允许有脱裤子放屁的冗余）。切记不要去优化或修复一个本不应该存在的问题！仓库外临时 PR body Markdown 是重要参考材料，你需要检查有没有重复开发和修补，如果有，分析其原因。重要问题需要实际运行代码来验证你的猜想，没有调查就没有发言权。

   并检查是否遵守:
   * .github/pull_request_template.md
   * docs/business_user_guide.md
   * AGENTS.md
   * architecture.md
   * capability_contract.json
   * interact.md
   * PR_Checklist.md
   * SOP.md
   * TESTING.md

   对应issue：《》
   PR审核指南：《》
   你的职责不单是分析目前的pr有没有符合issue，有没有bug，也要分析这些代码的复杂度是不是必要的。切记不要去优化或修复一个本不应该存在的问题！

   本轮最终结论只能是：
   - PASS：没有 P0/P1 问题。
   - REWORK_REQUIRED：存在需要修复或补证据的问题。
   - OWNER_DECISION_REQUIRED：对应 Issue 中存在尚未决定、且会阻塞当前交付的 owner 取舍。
   ```

   审核完成后的追问：按照 PR 审核指南，面向不熟悉本项目底层代码的程序员详细介绍你的发现。

   备注：第 9 步负责从完整 PR 中发现问题；第 10 步只验证已经提出的 finding，不能替代正式 PR 审核。

10. **如果 review 有问题，先验证问题是否真实存在，再决定是否修**

   给 Codex 和 Claude Code 的共同 prompt：

   ```text
   先不动代码，先检查实习生给出的问题是否真实存在。重要问题需要通过代码阅读、最小复现、定向测试或接近真实使用路径的验证来确认；没有调查就没有发言权。

   如果问题存在，请先输出分析，不要直接修复。分析必须包含：

   1. 检测：去对应 PR 描述检查是否之前修复过类似问题，如果有，如何制定一个端到端的验收计划来杜绝重复返工。
   2. 影响面：这个问题的上游输入、当前模块、下游调用方是否受影响；是否存在同类入口或相邻场景也需要一起检查。
   3. 同步项：判断是否需要同步测试说明、用户文档、架构/流程文档、PR 描述或 Review / 修复记录；如果不需要，也要说明原因。
   4. 在评估代码时不但要评估开发是否符合 issue，还要评估有没有过度开发，是否可以在架构层级精简（功能可以提前开发，但是不允许有脱裤子放屁的冗余）。
   5. 你的职责不单是分析目前的 PR 有没有符合 issue、有没有 bug，也要分析这些代码的复杂度是不是必要的。切记不要去优化或修复一个本不应该存在的问题！

   本轮最终结论只能是：
   - PASS：该 finding 经验证不成立，或确认不构成 P0/P1；无需修改。
   - REWORK_REQUIRED：该 finding 成立，或现有证据不足以排除 P0/P1；需要修复或补证据。
   - OWNER_DECISION_REQUIRED：对应 Issue 中存在尚未决定、且会影响是否修复或修复范围的 owner 取舍。

   实习生的发现：《》
   ```

   Codex 重点确认问题是否成立、触发路径、最小复现和严重度；Claude Code 重点检查影响面、同类入口、是否只是一个实例，以及最小充分的修复方式。两者意见交叉核对后由 Codex 输出综合分析；分歧由代码、测试、可复现证据和 owner 决策处理，不以模型身份裁决。

   **完整顺序：**

   1. Coding Agent 完成开发、自审、更新仓库外 PR body，并提交或更新 Draft PR。
   2. 新开 Codex 对话，使用第 9 步完整审核 prompt 审核最新 exact head；开发对话中的自审不能替代这次审核。
   3. 若结论为 `PASS`，进入合并以及第 11 至 13 步。
   4. 若结论为 `REWORK_REQUIRED`，把每个 P0/P1 finding 分别放入新的 Codex 验证对话和 Claude Code 验证对话，使用本节共同 prompt。Codex 核实真实性、触发路径、复现和严重度；Claude Code 核实影响面、同类入口、根因和最小充分修复。
   5. 将 Claude Code 的意见交给 Codex 输出综合分析。仍有分歧时，只交换代码、测试、复现证据和 Issue 契约，最多三轮；仍证据不足则保持 `REWORK_REQUIRED` 并列明补证据动作，不以模型身份裁决。
   6. 综合结论为 `REWORK_REQUIRED` 时，在 Codex 验证对话中输入“按照综合分析进行修复”；修复后复用第 8 步 PR 提交短 prompt，更新代码、测试、文档、Review / Fix Record 和 PR body，并推送新 head。
   7. 每次修复后都新开 Codex 对话，再按第 9 步审核最新 exact head；重复到 `PASS`。P2 可以接受，但必须记录。
   8. 任何阶段出现 `OWNER_DECISION_REQUIRED` 时，把需要 owner 选择的事项以自然语言补回 Issue，并说明它影响哪些工作；受影响工作暂停，其他工作继续。Owner 决定后把结论和理由补回 Issue，再恢复工作、更新 PR，并重新执行第 9 步审核。

   Finding 闭合：在既有 PR review / fix record 和 GitHub thread 中保留来源 ID、判断与关闭证据；不得让未解决 finding 静默消失，也不另建一套重复 reconciliation ledger。

   备注：同一个 PR 的 patch 不必在同一验证对话中反复完整粘贴；应覆盖到最新 head，避免模型继续依据过时 patch。

11. **PR 合并后，用网页端 GPT 的 apps 功能做 Tech Lead 总结**

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

   存档在 PR 评论区。

12. **Issue 关闭前，再从主干代码检查 FSD 是否真正开发完成**（这个环节暂时放弃，因为通过率 100%，而且第 13 步以用户角度验收能发现更精准的问题）

   使用长 prompt：[prompts/issue_closure_fsd_acceptance.md](../../prompts/issue_closure_fsd_acceptance.md)

   目的：从主干代码倒查 Issue 中的每个 `Spec Unit` 是否已实现，并强制输出 `Updates to FSD`（如有偏差）。

13. **从用户视角验收这次 PR**

   验收计划需要 GPT 网页版和 Claude Code 达成合意。

   ```text
   针对这个issue和pr，制定一个验收计划，如何以用户体验的角度来验收这次的PR
   ```

   存档在 PR 评论区。下一步把这份用户视角验收建议交给 Codex，必要时结合 Playwright 等交互工具，真的走一遍验收。该步骤经常可能直接产生新的开发计划。

## 实验机制重审
条件性 Issue Readback 和 Owner Decision 机制先作为实验机制。每项累计 3 个适用 PR 后，按 [DEC-008](decisions.md#实验机制重审与退役) 分别输出 `PROMOTE`、`MODIFY` 或 `RETIRE`；从未触发，或触发后没有改变任何参与者下一步动作的机制，默认退役，除非有新的具体风险证据。

## 核心产物

- `FSD Core Contract`：把需求翻译成可实现、可测试、可审核的契约。
- `Repo Impact Forecast`：预测 FSD 与当前仓库的真实触点、风险、文档和测试影响。
- `Target State Bridge`：定义开发完成后用户 / 调用方应该看到什么状态，以及如何验证。
- `Issue`：把契约、范围、任务拆解、文档更新预测、测试更新预测、验收条件和需要 owner 判断的事项固化。
- 条件性 Issue Readback：帮助 owner 在编码前理解高风险 Issue；不是第二套权威。
- 仓库外 PR body Markdown：由 `.github/pull_request_template.md` 派生，不进入目标工作树或 commit；是 review 和通用 GitHub 发布能力的输入。
- `FSD 完备性验收报告`：Issue 关闭前从主干代码倒查 Spec Unit 与 FSD 偏差的报告。
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
