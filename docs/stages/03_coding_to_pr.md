# 阶段 3：编码、PR 准备与首轮审核

## 目标

基于 issue 完成开发，并产出可审查的 PR 叙事、测试证据和审核上下文。

## 输入

- 已经固化的 issue
- 仓库权威文档
- 本地代码库

## 输出

- 本地代码修改
- `PR_BODY.md`
- PR 审核输入材料

## 执行顺序

1. Coding Agent 按 [prompts/coding_agent.md](../../prompts/coding_agent.md) 开发。
2. 审核前，先用 [prompts/review_file_request.md](../../prompts/review_file_request.md) 让 GPT 5.4 Pro 判断还缺哪些文件。
3. 代码审核时使用：
   [prompts/pr_review_system.md](../../prompts/pr_review_system.md)
   [prompts/pr_review_task.md](../../prompts/pr_review_task.md)
4. 如果是既有 PR，按 [prompts/submit_existing_pr.md](../../prompts/submit_existing_pr.md) 提交。
5. 如果是新 PR，按 [prompts/submit_new_pr.md](../../prompts/submit_new_pr.md) 提交。

## 关键要求

- Coding Agent 只吃 issue，不再重复注入 FSD / Forecast / Bridge。
- `PR_BODY.md` 必须覆盖已有 PR 和本地全部修改内容。
- 既有 PR 要保持 commits 数量为 1 个。
- 审核时除了代码问题，还要额外检查：
  是否满足 `FSD Core Contract`
  是否达到 `Target State Bridge`
  是否遵守 `TESTING.md`、`AGENTS.md`、`PR_Checklist.md`

## 下一步入口

如果 review 无问题，进入 [docs/stages/05_merge_post_merge_acceptance.md](05_merge_post_merge_acceptance.md)；
如果 review 有问题，先进入 [docs/stages/04_review_resolution_loop.md](04_review_resolution_loop.md)。
