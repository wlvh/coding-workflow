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

任何需要 owner 判断的范围、风险、成本、权限或失败语义，都必须保持显式，不得在模型合意或工程摘要中静默消失。每项 Owner Decision 至少写清：

- Decision：具体要决定什么；
- Evidence needed：作出决定需要什么证据；
- Evidence path：该证据能否在当前约束下合法取得；
- Blocked work：阻塞哪些 SU / 工作包 / 阶段；
- Unblocked work：哪些部分可以继续；
- Safe default：未决定时采用什么 fail-closed 默认。

若决定所需证据在当前约束下无法合法取得，必须把这个限制和需要 owner 选择的下一步写进 Issue，不得静默继续实现。
```