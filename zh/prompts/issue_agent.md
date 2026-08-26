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

## Owner Decisions

只有当事实已经查清，剩下的是 owner 必须在范围、风险、成本、权限或失败语义之间作取舍时，才使用 `OWNER_DECISION_REQUIRED`。普通实现缺陷、证据不足、调查未完成或 Agent 不知道如何修复，仍按 `REWORK_REQUIRED` 处理。

需要 owner 判断的事项必须留在 Issue 中，用自然语言讲清楚为什么需要决定、主要选择及影响、哪些工作需要暂缓、哪些可以继续，以及未决定时采用什么安全默认。不要为了统一格式强迫每项填写固定表格或字段；目标是让 owner 能读懂并作出决定。

开发或 review 中出现新的 owner 取舍时，由当前负责推进该工作的 Agent 把它补回同一 Issue。Owner 决定后，也在同一处补上结论和理由。PR body、review comment 和聊天只引用 Issue 中的决定，不另写一份可能漂移的版本。
```
