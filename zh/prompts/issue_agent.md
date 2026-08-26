# Issue Agent Prompt

## 用途

用于把 `FSD`、`Repo Impact Forecast` 和 `Target State Bridge` 固化成可执行 issue。

## Prompt

```text
基于 `FSD`、`Repo Impact Forecast` 和 `Target State Bridge` 给我一份 issue。你应该根据目前最新的主干代码进行；我已经把 GitHub app 给你打开，给你权限的目的不是让你直接在 GitHub 写 issue，而是调查代码全貌，没有调查就没有发言权。

## Issue 必须包含
1. 背景与目标（Why）
2. Scope / Non-goals
3. 契约摘要
4. 开发任务拆解（按 SU）
5. Target State Bridge 摘要
6. 预测的代码触点（非承诺）
7. 文档更新预测
8. 测试更新预测
9. Acceptance Checklist
10. 风险、开放问题与 Owner Decisions

## Owner Decisions：唯一规范

本节是本工作流对 `OWNER_DECISION_REQUIRED`、`OD-xxx` 记录格式和生命周期的唯一规范。README、Target State Bridge 和 PR review prompt 只能引用本节并说明各自的下一步动作，不得复制或改写一套平行定义。

只有当事实已经查清，且问题不能由当前 FSD、Issue、代码、测试或仓库权威机械判断，而是必须由 owner 在范围、风险、成本、权限或失败语义之间作选择时，才创建 Owner Decision。普通实现缺陷、证据不足、尚未完成的调查或 Agent 不知道如何修复，都不得包装成 Owner Decision，应继续按 `REWORK_REQUIRED` 处理。

Issue 的 `Owner Decisions` 节是唯一决策记录。每项使用稳定编号，并在同一记录中从 `OPEN` 更新为 `DECIDED`：

### OD-001 — <标题>
Status: OPEN / DECIDED
Question: <owner 要决定什么>
Options and trade-offs: <可选方案及代价>
Evidence: <已经查清、足以支撑取舍的事实和证据>
Blocks: <受阻 SU / 工作包 / 阶段>
Unblocked: <可以继续的工作>
Safe default: <未决定时的安全默认>
Decision and rationale: <决定后写入；未决定时写 Pending>

初始 Issue 中已经存在的 Owner Decision 由 Issue Agent 分配编号并写入。开发中发现新的 Owner Decision 时，由当前 Coding Agent 按本节格式写入同一 Issue；PR review 或 finding 验证中发现新的 Owner Decision 时，由负责综合分析和后续修复的 Codex 写入同一 Issue。提出 finding 的 reviewer 或 Claude Code 只提供事实、影响面和建议，不直接维护决策记录。依赖该决定的工作在记录写入前不得继续，未受阻工作继续推进。

Owner 作出决定后，由当前负责继续受阻工作的 Coding Agent 或 Codex 更新同一 `OD-xxx` 为 `DECIDED`，填写 `Decision and rationale`，再恢复受阻工作。PR body、review comment 和聊天只引用 `OD-xxx`，不得复制一份措辞不同的决策正文。
```
