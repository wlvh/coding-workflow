# Target State Bridge Prompt

## 用途

用于根据 `FSD + 当前仓库代码 + 仓库权威文档` 产出 `Repo Impact Forecast` 和 `Target State Bridge`。

## Prompt

```text
仓库权威文档：AGENTS.md / architecture.md / SOP.md / PR_Checklist.md / interact.md / TESTING.md / docs/business_user_guide.md / README.md。
如果项目存在 capability_contract.json，也必须读取并作为能力边界真相源。
我敲定了一份 FSD（功能规范说明书），因为 FSD 是在没有实际接触代码的情况下完成的。所以你需要基于《FSD + 当前仓库代码 + 仓库权威文档》来完成 FSD 和实际代码之间 Target State Bridge 的分析。

## 多Agent 执行协议

本阶段采用“并行取证、主 Agent 单一收敛”结构。

1. 主 Agent 首先：
   - 从 FSD 提取全部 Spec Unit、验收条件、非目标和未确认假设；
   - 建立 SU -> 候选代码入口 -> 测试区域 -> 文档区域的浅层调查地图。

2. 只有存在至少两个边界清晰、能够独立完成的证据域时，
   才启动只读 subagents。不得为了使用多Agent强行拆分高度耦合任务。

3. 可委派的证据域包括：
   - Runtime Path：入口、调用链、数据流、状态变化、错误与恢复路径；
   - Test Evidence：测试、fixture、CI、Stage 和验证缺口；
   - Contract Alignment：FSD 与仓库权威文档、能力边界、用户行为的冲突；
   - Compatibility / Risk：兼容入口、迁移、相邻场景和下游调用方。

4. 每个 subagent：
   - 只负责一个证据域；
   - 默认只读，不修改代码、文档或 FSD；
   - 可以提出 candidate impact，但不能决定最终 Must / Likely / Maybe；
   - 只返回：
     Scope
     Facts + 文件/符号/运行证据
     Inferences + 依据 + 置信度
     Unknowns
     Candidate impacts

5. 主 Agent 必须等待本轮要求的全部 subagents 返回，然后：
   - 自行复核关键调用链；
   - 解决证据冲突；
   - 独立写出唯一的 Repo Impact Forecast 和 Target State Bridge；
   - 不得把“多个 subagent 一致”本身作为事实证据。

## A. Repo Impact Forecast
目标：
- FSD 的哪些假设仍未确认
- Current / Compatibility 是否与仓库现状冲突
- 最可能影响的模块 / 文件 / 函数 / 脚本
- 需要更新的文档
- 需要更新的测试
- 建议必跑 Stage

要求：
- 区分 Must / Likely / Maybe
- 绝不把预测写成承诺

## B. Target State Bridge
目标：
- 开发完成后，用户 / 调用方应该能看到什么状态
- interact.md 应该怎么更新
- 应该通过哪些测试目录和哪些 Stage 来证明这些状态成立
- 什么才算真的 Done

要求：
- 必须输出用户可见层 Delta：

1. capability_contract.json Delta：
   - No change / Check needed / Update needed
   - 只在本次 FSD 改变能力边界、职责边界或 agent 行为承诺时标记为 Update needed。

2. interact.md Delta：
   - No change / Check needed / Update needed
   - 只在本次 FSD 改变用户可观察行为或验收不变量时标记为 Update needed。

3. docs/business_user_guide.md Delta：
   - No change / Check needed / Update needed
   - 只在本次 FSD 改变业务人员能问什么、怎么问、结果怎么看、什么时候该找人时标记为 Update needed。

- 若任何用户可见层 Delta 为 Update needed，必须给出 draft 文案或明确需要人类补充的内容。
- 不要把所有工程治理文档都扩展成 Delta 矩阵。
- AGENTS.md / architecture.md / TESTING.md / SOP.md / PR_Checklist.md 的影响仍放在 Repo Impact Forecast 的“需要更新的文档”里判断，不进入用户可见层 Delta。
- 必须输出 Verification Matrix：
  TS / AC -> 测试目录 -> Stage
- 不得擅自拍板关键失败路径；需要人类决定的失败路径要显式标注

```
