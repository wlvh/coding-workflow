# 阶段 5：合并前治理、合并后总结与验收

## 目标

在合并前确认 PR 已具备交付条件，在合并后补齐总结、FSD 完备性验收和用户视角验收。

## 输入

- 已通过 code review 的 PR
- `PR_BODY.md`
- 主干代码
- issue 中的 FSD

## 输出

- Merge Readiness Report
- PR 完成总结
- FSD 完备性验收报告
- 用户视角验收动作

## 执行顺序

1. 若当前 PR 没有 review 问题，在 PR 评论区输入 `/claude-merge-check`。
2. GitHub Action 见 [.github/workflows/claude-merge-readiness.yml](../../.github/workflows/claude-merge-readiness.yml)。
3. PR 合并后，用 [prompts/post_merge_summary.md](../../prompts/post_merge_summary.md) 让网页端 GPT 从 tech lead 视角总结本次 PR。
4. 收到总结后，再追问 [prompts/post_merge_agents_update_check.md](../../prompts/post_merge_agents_update_check.md)。
5. 关闭 issue 前，用 [prompts/issue_closure_fsd_acceptance.md](../../prompts/issue_closure_fsd_acceptance.md) 在主干代码上核对 FSD 是否已全部落地。
6. 再用 [prompts/user_acceptance_check.md](../../prompts/user_acceptance_check.md) 询问 GPT 5.4 thinking 如何从用户视角验收这次 PR。
7. 把上一步回答交给 Codex，必要时配合交互工具做一次真正的用户视角验收。

## Done 定义

- Merge Readiness 为 `PASS`，或者阻塞项已全部消除。
- PR 合并后的影响、变化和后续展望已总结。
- `AGENTS.md` 及其内联文档是否需要更新，已经被重新检查。
- issue 对应的 FSD 完备性验收已完成。
- 用户视角验收动作已执行，或已沉淀为下一步开发计划。
