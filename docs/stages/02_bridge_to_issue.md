# 阶段 2：Target State Bridge 与 Issue 产出

## 目标

把脱离仓库上下文的 FSD，桥接到真实代码库、真实测试和真实文档上，并进一步沉淀为 issue。

## 输入

- `FSD Core Contract`
- 当前仓库代码
- 仓库权威文档：`AGENTS.md`、`SOP.md`、`PR_Checklist.md`、`interact.md`、`TESTING.md`

## 输出

- `Repo Impact Forecast`
- `Target State Bridge`
- issue 草案或正式 issue

## 执行顺序

1. 用 [prompts/target_state_bridge.md](../../prompts/target_state_bridge.md) 生成 `Repo Impact Forecast` 和 `Target State Bridge`。
2. 如果预估修改量超过 3000 行，把工作拆成主 issue 和多个 sub issue。
3. sub issue 必须满足独立验收、独立回滚、独立 code review。
4. 用 [prompts/issue_agent.md](../../prompts/issue_agent.md) 把 FSD、Forecast 和 Bridge 固化为 issue。

## 关键检查点

- `Repo Impact Forecast` 必须区分 `Must / Likely / Maybe`。
- `Target State Bridge` 必须输出 `interact.md Delta`。
- `Verification Matrix` 必须显式把 `TS / AC -> 测试目录 -> Stage` 对齐。
- 对关键失败路径，不允许模型擅自拍板，必须标记为需要人类决策。

## 下一步入口

完成后进入 [docs/stages/03_coding_to_pr.md](03_coding_to_pr.md)。
