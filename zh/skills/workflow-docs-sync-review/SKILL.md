---
name: workflow-docs-sync-review
description: 当需要在独立会话中审查工作流文档同步（workflow docs sync）PASS 项目化 PR、且不得修改 tracked 项目文件时使用。
---

## 调用协议

- 只在与执行 skill 不同的独立新会话中调用；输入为 workflow-docs PR 编号。
- 当前目录必须是该 PR 所属目标仓库且 HEAD 等于实际 PR head；显式提供 clean pinned upstream 路径和完整 SHA。
- 本 skill 不创建隔离上下文，不修改 tracked 项目文件，不修复自己发现的问题；只允许写入已忽略的 `.coding_workflow/skill_results/`。

## 审查流程

1. 确认目标仓库在审查前工作区干净，并记录 `git status`；写入 ignored result 后再次核对，输出必须完全相同。
2. 从 pinned checkout 读取 `zh/scripts/sync_pr_review_system.md` 全文，把它作为唯一审查规则。
3. 使用 `gh` 读取指定 PR 的 body、changed files、完整 diff 与 head SHA；按审查规则定向读取证据。
4. 只输出可由 PR、PR head、pinned upstream 或可复现命令证明的 finding；不得替执行者补写文档或 PR body。
5. 将结果写入 `.coding_workflow/skill_results/review_<UTC时间戳>.json`。结果必须包含完整 `head_sha`、`upstream_sha`、七个 `{verdict, evidence}` `review_sections`、最高影响 findings 和非空 `evidence_index`；整体结论取分节判定和 finding 等级中最严重者，不允许人工覆盖。
6. 把 `<workflow-docs-sync-review-root>` 解析为当前 canonical / installed `SKILL.md`
   所在目录的绝对路径；在目标仓库 cwd 运行
   `python3 "<workflow-docs-sync-review-root>/scripts/validate_review.py" --target-repo <目标仓库> --upstream-dir <pinned checkout> --upstream-sha <完整SHA> --review-file <结果文件> --pr-number <PR编号>`；validator 会再次查询真实 PR，并绑定 PR body upstream SHA、PR number、GitHub head、目标仓库 HEAD 和结果 JSON。
7. 校验通过后，把结果文件中的同一 JSON 原样作为会话最后一条消息。

## 停止条件

- upstream checkout 缺失、不是 git 仓库，或 HEAD 与 PR body 声明的 pinned SHA 不一致。
- PR 不存在、无法读取 diff、无法确定 head SHA，或目标仓库 HEAD / 参数 / 结果 JSON 与 GitHub PR identity 不一致。
- 审查规则文件缺失或无法以 UTF-8 读取。
- 审查前后 `git status` 不同，或出现 ignored result 之外的写入意图。
- 输出校验失败。
