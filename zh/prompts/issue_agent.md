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

## Owner Decisions 规则

只有当某个问题不能由当前 FSD、Issue、代码、测试或仓库权威机械判断，而是必须由 owner 在范围、风险、成本、权限或失败语义之间作选择时，才创建 Owner Decision。普通实现缺陷、证据不足或尚未完成的调查不得包装成 Owner Decision。

Issue 的 `Owner Decisions` 节是唯一决策记录。每项使用稳定编号，并在同一记录中从 `OPEN` 更新为 `DECIDED`：

### OD-001 — <标题>
Status: OPEN / DECIDED
Question: <owner 要决定什么>
Options and trade-offs: <可选方案及代价>
Blocks: <受阻 SU / 工作包 / 阶段>
Unblocked: <可以继续的工作>
Safe default: <未决定时的安全默认>
Decision and rationale: <决定后写入；未决定时写 Pending>

需要 owner 判断的事项不得在模型合意或工程摘要中静默消失。开发中新增的 Owner Decision 必须先回写同一 Issue，再让依赖该决定的工作继续；未受阻工作继续推进。PR body、review comment 和聊天只引用 `OD-xxx`，不得复制一份不同措辞的决策正文。
```