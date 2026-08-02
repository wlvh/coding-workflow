<!--
只写本 PR 已完成的事实。变更范围来自真实 Git diff；测试证据遵循 TESTING.md；用户行为和
架构影响分别核对 interact.md 与 architecture.md。不要把计划、历史草稿或本地未提交内容
写入 PR body。
-->

## 1. Background and Goal

<!-- 说明问题、目标、关联需求，以及本 PR 明确不处理的范围。 -->

## 2. Implementation and Tradeoffs

<!-- 说明核心实现、关键取舍、被拒绝方案及原因，不逐文件复述 diff。 -->

## 3. Actual Change Scope

<!-- 根据 git diff --name-only <base>...HEAD 列出实际变更；不要保留空表或计划中的文件。 -->

## 4. Documentation Impact

<!-- 列出实际更新的文档和证据。未更新的受影响候选文档写真实 no-update reason；不要求全部文档都有 diff。 -->

## 5. User-visible and Architecture Impact

<!-- 分别说明用户可观察变化与架构变化；没有时写 None，并给出核对依据。 -->

## 6. Testing Evidence

- Exact command：记录原样命令；未运行时写 `Not run`。
- Scope：说明该命令实际证明的层级、入口和边界。
- Result：记录通过、失败、跳过及关键数量或错误。
- Not-run reason：已运行时写 `Not applicable`；未运行时写具体原因和风险。
- Environment：记录实际执行环境、隔离方式、副作用和清理结果。

## 7. Review / Fix Record

<!-- 按 finding ID 记录 severity、证据、判断、修复和复核结果；没有 finding 时列出已核对的高风险点。不要增加重复 reconciliation ledger。 -->

## 8. Known Limits, Open Decisions, and Rollback

<!-- 区分已知限制、需要产品判断的 open decision 和可执行回滚；没有时明确写 None。 -->

## 9. Final Self-check

- [ ] Actual Change Scope 与真实 diff 一致。
- [ ] 测试命令、范围、结果和未运行原因准确。
- [ ] 用户可见与架构影响已核对对应权威文档。
- [ ] BLOCKER 与 actionable WARN 已关闭；open decisions 未被伪装为完成。
- [ ] PR body 不含历史草稿、未落地计划、错误 base/head 或仓库内临时 body 路径。
