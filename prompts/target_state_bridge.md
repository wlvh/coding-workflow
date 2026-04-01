# Target State Bridge Prompt

## 用途

用于根据 `FSD + 当前仓库代码 + 仓库权威文档` 产出 `Repo Impact Forecast` 和 `Target State Bridge`。

## Prompt

```text
仓库权威文档：AGENTS.md/SOP.md/PR_Checklist.md/interact.md/TESTING.md。
我敲定了一份 FSD（功能规范说明书），因为 FSD 是在没有实际接触代码的情况下完成的。所以你需要基于《FSD + 当前仓库代码 + 仓库权威文档》来完成 FSD 和实际代码之间 Target State Bridge 的分析。

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
- 必须输出 interact.md Delta：No change / Append / Modify
- 若不是 No change，必须给出 draft 文案
- 必须输出 Verification Matrix：
  TS / AC -> 测试目录 -> Stage
- 不得擅自拍板关键失败路径；需要人类决定的失败路径要显式标注

## C. 预估修改的代码量
如果修改量超过 3000 行以上则分为主 issue 和 sub issue。每次我都会把主 issue 和 sub issue 输入给编程 agent，要求其开发 sub issue。sub issue 必须能独立验收、能独立回滚、能独立 code review。
```
