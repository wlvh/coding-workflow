# 编程工作流

## 主流程

1. **确定需求**

2. **网页端 Pro 模型制定 `FSD Core Contract`**
   使用长 prompt：[prompts/fsd_core_contract.md](prompts/fsd_core_contract.md)
   备注：当前默认前提是 GPT 5.4 Pro 不能自由探索本地代码和 GitHub，所以 FSD 先做黑盒契约。

3. **Target State Bridge Agent（codex） 根据 `FSD + 当前仓库代码 + 仓库权威文档` 产出 `Repo Impact Forecast` 和 `Target State Bridge`**
  * 如果GPT 5.4 Pro模型可以在不接触本地代码和GitHub的情况下产出也能由它代为产出
  * 使用长 prompt：[prompts/target_state_bridge.md](prompts/target_state_bridge.md)

5. **Issue Agent （codex）写 issue**
   使用长 prompt：[prompts/issue_agent.md](prompts/issue_agent.md)
   目标：把 `FSD`、`Repo Impact Forecast` 和 `Target State Bridge` 固化成开发契约。
   完成后让codex和claude code互相讨论到达成合意。
7. **Coding Agent（codex） 按 issue 开发**
   短 prompt：

   ```text
   按照当前 issue 完成本次开发。
   1. 读取 AGENTS.md / SOP.md / TESTING.md / PR_Checklist.md / interact.md；如果项目存在 capability_contract.json / docs/business_user_guide.md，也必须按 AGENTS.md 的文档关系检查。
   2. 从 issue 中提取 Spec Unit，生成 SU -> 代码改动 -> 测试 -> 文档 的 todo list。
   3. 提交前根据 `.github/pull_request_template.md` 生成并更新本地临时文件 `PR_BODY.md`。
   4. PR_BODY.md 必须覆盖：背景与目标、实现方案、变更范围、文档影响、用户与架构影响、Review / 修复记录、已知限制与回滚。
   测试策略与测试证据记录方式以 `TESTING.md` 为准。
   ```

   备注：我在这里没有提FSD/Repo Impact Forecast/Target State Bridge，宪法文件已经转为issue。而且也没有提供编程开发的具体模板，因为我相信llm擅长做这个，issue也能做好制约。

8. ** codex 负责代码审核**
   预审核短 prompt：

   正式审核系统 prompt：[prompts/pr_review_system.md](prompts/pr_review_system.md)
   正式审核任务短 prompt：

   ```text
   对 XX 项目的 PR XX（最新head XX）进行严格详细全面的代码审查。PR_BODY.md 是你重要的参考材料。重要问题需要实际运行代码来验证你的猜想，没有调查就没有发言权。并额外检查是否遵守 TESTING.md / AGENTS.md / PR_Checklist.md / SOP.md / interact.md。
   对应issue：《》
   PR审核指南：《》
   ```
   审核完成的后的追问：按照PR审核指南，面向不熟悉本项目底层代码的程序员详细介绍你的发现。
   

   既有 PR 提交短 prompt：

   ```text
   重新以 PR 审核的态度审核你的新增代码，如有问题先验证是否真实存在，再决定是否修复。

   然后在既有分支的既有 PR 上提交本地全部代码，要求：
   1. 遵守 PR_Checklist.md。
   2. PR 对外保持 1 个 commit。
   3. 每轮 review / 修复都必须更新 PR_BODY.md 的“Review / 修复记录”。
   4. PR_BODY.md 必须根据 `.github/pull_request_template.md` 填写，并覆盖已有 PR 和本地全部修改内容。
   5. 测试策略与测试证据记录方式以 TESTING.md 为准。

   备注：
   - PR_BODY.md 是本地临时产物，不提交仓库。
   - PR_BODY.md 是重要的代码审核材料之一。
   - PR 审核指南：《》
   ```

   新 PR 提交短 prompt：

   ```text
   重新以 PR 审核的态度审核你的新增代码，如有问题先验证是否真实存在，再决定是否修复。

   然后遵守 PR_Checklist.md 创建 PR，要求：
   1. 根据 `.github/pull_request_template.md` 生成并填写本地临时文件 PR_BODY.md。
   2. PR 对外保持 1 个 commit。
   3. PR_BODY.md 必须覆盖本地全部修改内容。
   4. 测试策略与测试证据记录方式以 TESTING.md 为准。

   备注：
   - PR_BODY.md 是本地临时产物，不提交仓库。
   - PR_BODY.md 是重要的代码审核材料之一。
   - PR 审核指南：《》
   ```

9. **如果 review 有问题，先验证问题是否真实存在，再决定是否修**
   给 Codex 和 claude code 的短 prompt：

   ```text
   先不动代码，先检查实习生给出的问题是否存在，如存在请列出证据并分析是否值得增加复杂度来修复。重要问题需要实际运行代码来验证你的猜想，没有调查就没有发言权。然后遵守AGENTS.md列出的准则给出你的方案。实习生的发现：《》
   ```

   执行顺序：先让 Codex 和 Opus 分别判断，再把 Opus 的意见发给 Codex 要求出综合分析版本。
   处理分歧：如果双方分歧仍然很大，再把 GPT 5.4 对 Opus 的反驳发给 Opus，让 Opus 重新分析后按自己的方案执行。
   修复后：继续复用“既有 PR 提交短 prompt”。
   备注：同一个 PR 的 patch 不需要每次重新完整粘贴给 GPT，可以在原对话里覆盖最新 patch，避免上下文过时。

10. **如果 review 没有问题（定义为没有P0/P1级别发现），在 PR 评论区输入 `/claude-merge-check`**（这个环节暂时放弃，反复的PR审查已经足够）
   自动化文件：[.github/workflows/claude-merge-readiness.yml](.github/workflows/claude-merge-readiness.yml)
   作用：做 merge-readiness 检查，而不是重复做 code review。
   通过规则：无问题则在 PR 评论区输入 `/claude-merge-check`，通过后再合入主干。

11. **PR 合并后，用网页端 GPT 的 apps 功能做 tech lead 总结**
   总结短 prompt：

   ```text
当前 PR XX 已经完成。请站在 tech lead 视角详细评估，但你的目标不是写一篇“好看的评审总结”，而是让我真正理解这个 PR 是怎么工作的。

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
   
12. **Issue 关闭前，再从主干代码检查 FSD 是否真正开发完成**（这个环节暂时放弃，因为通过率100%，而且 12.如何以用户的角度来验收这次的 PR能发现更精准的问题）
    使用长 prompt：[prompts/issue_closure_fsd_acceptance.md](prompts/issue_closure_fsd_acceptance.md)
    目的：从主干代码倒查 issue 中的每个 `Spec Unit` 是否已实现，并强制输出 `Updates to FSD`（如有偏差）。

13. **再问 GPT 网页版：如何从用户视角验收这次 PR**
    验收计划需要GPT网页版和claude code达成合意。
    短 prompt：

   ```text
   如何以用户的角度来验收这次的 PR？

   验收必须分两层：
   1. UX 层：用户为了……进入……执行……看到……（按 interact.md 的剧本格式写）
   2. 契约层：对照 issue 中的 Acceptance Checklist 逐条核查，每一条 SU/AC 给出
      "实现位置 + 实际行为 + FSD 期望 + 是否一致"四列。
      如果发现任何不一致（即使工程上合理），明确标注"需要 Updates to FSD"
      并附偏差说明。
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

## 代码项目核心文档
- `AGENTS.md`：agent 工作入口、文件简介、代码规范与文档关系。
- `architecture.md`：系统架构、模块边界、数据流、架构不变量与扩展点。
- `capability_contract.json`：能力边界、职责边界、agent 行为承诺的机器可读真相源。
- `interact.md`：用户可观察行为与验收不变量。
- `docs/business_user_guide.md`：面向首次接触业务人员的教学派生文档。
- `TESTING.md`：测试策略、测试分层、测试证据与 contract alignment 测试原则。
- `PR_Checklist.md`：PR 提交、commit / push、PR body 使用规则。
- `SOP.md`：标准流程骨架，只做入口，不重复规范。
- `.github/pull_request_template.md`：PR body 的长期模板。
