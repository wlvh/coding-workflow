<!--
PR body 原则：

1. 只写本 PR 已经完成的事实，不写计划。
2. 文件清单必须来自：git diff --name-only <base>...HEAD。
3. 测试策略与测试证据记录方式以 TESTING.md 为准。
4. 用户可见变化对照 interact.md。
5. 架构变化对照 architecture.md。
6. 每轮 review / 修复都必须写入“Review / 修复记录”。
-->

## 1. 背景与目标

---

## 2. 实现方案

<!--
写核心思路和关键取舍。
不要复述所有代码。
-->

---

## 3. 文档影响

<!--
只写受影响的文档。
不受影响可以写：无。
-->

- `AGENTS.md`：
- `architecture.md`：
- `TESTING.md`：
- `interact.md`：
- `SOP.md`：
- `README.md`：
- `PR_Checklist.md`：

---

## 4. 用户与架构影响

用户可见变化：

- Yes / No
- 说明：

架构变化：

- Yes / No
- 说明：

---

## 5. Review / 修复记录

<!--
单 commit 策略下，这里就是修复历史。
每次 review、修复、merge-readiness 反馈后都必须更新。
-->

| 轮次 | 来源 | 问题摘要 | 判断 | 处理结果 | 证据 |
|---|---|---|---|---|---|
| R0 | 初始提交 | N/A | N/A | 初始实现 |  |
| R1 | Codex / Claude / 人工 |  | 真实存在 / 不成立 / 可暂缓 | Fixed / Won't fix / N/A |  |

---

## 6. 已知限制与回滚

已知限制：

- 

回滚方式：

- 

---

## 7. 最终自检

- [ ] 当前分支不是主干
- [ ] 已执行 `git diff --name-only <base>...HEAD`
- [ ] “变更范围”与实际 diff 一致
- [ ] PR body 不包含历史草稿、旧分支名、未落地计划
- [ ] 已按 `TESTING.md` 完成测试与测试记录
- [ ] 用户可见变化已对照 `interact.md`
- [ ] 架构变化已对照 `architecture.md`
- [ ] 每轮 review / 修复都已写入“Review / 修复记录”