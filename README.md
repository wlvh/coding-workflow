# 编程工作流

这个仓库把原始长流程拆成三层：

1. `README.md` 只保留主流程导航。
2. `docs/stages/` 负责说明每个阶段的输入、输出和决策点。
3. `prompts/` 存放可直接复用的 prompt 模板。

如果只想快速进入流程，按下面顺序阅读即可。

## 主流程

1. 需求确认与 FSD 制定
   说明文件：[docs/stages/01_requirement_to_fsd.md](docs/stages/01_requirement_to_fsd.md)
   Prompt 文件：[prompts/fsd_core_contract.md](prompts/fsd_core_contract.md)

2. Target State Bridge 与 Issue 产出
   说明文件：[docs/stages/02_bridge_to_issue.md](docs/stages/02_bridge_to_issue.md)
   Prompt 文件：[prompts/target_state_bridge.md](prompts/target_state_bridge.md)、[prompts/issue_agent.md](prompts/issue_agent.md)

3. 编码、PR 准备与首轮审核
   说明文件：[docs/stages/03_coding_to_pr.md](docs/stages/03_coding_to_pr.md)
   Prompt 文件：[prompts/coding_agent.md](prompts/coding_agent.md)、[prompts/review_file_request.md](prompts/review_file_request.md)、[prompts/pr_review_system.md](prompts/pr_review_system.md)、[prompts/pr_review_task.md](prompts/pr_review_task.md)、[prompts/submit_existing_pr.md](prompts/submit_existing_pr.md)、[prompts/submit_new_pr.md](prompts/submit_new_pr.md)

4. Review 争议处理与补丁回合
   说明文件：[docs/stages/04_review_resolution_loop.md](docs/stages/04_review_resolution_loop.md)
   Prompt 文件：[prompts/review_recheck_local.md](prompts/review_recheck_local.md)、[prompts/submit_existing_pr.md](prompts/submit_existing_pr.md)

5. 合并前治理、合并后总结与验收
   说明文件：[docs/stages/05_merge_post_merge_acceptance.md](docs/stages/05_merge_post_merge_acceptance.md)
   Prompt 文件：[prompts/post_merge_summary.md](prompts/post_merge_summary.md)、[prompts/post_merge_agents_update_check.md](prompts/post_merge_agents_update_check.md)、[prompts/issue_closure_fsd_acceptance.md](prompts/issue_closure_fsd_acceptance.md)、[prompts/user_acceptance_check.md](prompts/user_acceptance_check.md)
   Workflow 文件：[.github/workflows/claude-merge-readiness.yml](.github/workflows/claude-merge-readiness.yml)

## 关键产物

产物说明见：[docs/reference/artifacts.md](docs/reference/artifacts.md)

## 目录约定

- `docs/stages/`：阶段流程说明。
- `docs/reference/`：术语和产物说明。
- `prompts/`：直接给模型使用的 prompt。
- `.github/workflows/`：合并前治理自动化。
