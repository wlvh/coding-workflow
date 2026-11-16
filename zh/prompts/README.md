# 编程提示与源索引

[编程工作流](../docs/development_workflow/README.md)说明各阶段怎样推进。
[coding_workflow.json](coding_workflow.json)列出 coding-loop v2 的提示组合及加载顺序。

## 提示组合

各用途先加载[公共约定](coding_common.md)，再按下表加载角色提示。
需求和 PR 审查分别由来自两家不同 LLM 公司的 LLM 执行；两方完成独立初审后，使用共享交流提示交换结论。

| 用途键 | 公共约定之后按序加载 | 职责 |
|---|---|---|
| `issue_author` | [issue_agent.md](issue_agent.md) | 编写与维护 Issue |
| `issue_review_completion` | [issue_review_completion.md](issue_review_completion.md)、[review_exchange.md](review_exchange.md) | 完整审查 Issue，侧重完整性与可验收性 |
| `issue_review_minimality` | [issue_review_minimality.md](issue_review_minimality.md)、[review_exchange.md](review_exchange.md) | 完整审查 Issue，侧重最小充分性 |
| `engineering_owner` | [engineering_owner.md](engineering_owner.md) | 调查、实现、测试与修复 |
| `pr_review_correctness` | [pr_review_system.md](pr_review_system.md)、[pr_review_correctness.md](pr_review_correctness.md)、[review_exchange.md](review_exchange.md) | 完整审查 PR，侧重正确性 |
| `pr_review_impact` | [pr_review_system.md](pr_review_system.md)、[pr_review_impact.md](pr_review_impact.md)、[review_exchange.md](review_exchange.md) | 完整审查 PR，侧重影响与必要性 |
| `integration_acceptance` | [integration_acceptance.md](integration_acceptance.md) | 核对集成结果与交付条件 |
| `user_acceptance` | [user_acceptance.md](user_acceptance.md) | 制定验收场景并实际验证 |
| `delivery_explanation` | [delivery_explanation.md](delivery_explanation.md) | 说明成果、用法与取舍 |

## 接入

从同一个 Git 提交读取索引及所列源文件，按 `promptPaths` 顺序加载完整 UTF-8 Markdown 原文，
包括代码块。索引中的路径相对仓库根目录。

编程行为提示在本目录统一维护。执行工具补充实际任务、仓库资料、代码版本、测试结果、
工具能力、权限和输出格式。固定版本及更新方式见[版本采用说明](../docs/development_workflow/version_adoption.md)。

## 参考材料

- [fsd_core_contract.md](fsd_core_contract.md)：共享行为规格的写法。
- [target_state_bridge.md](target_state_bridge.md)：影响分析与迁移安排。
- [issue_closure_fsd_acceptance.md](issue_closure_fsd_acceptance.md)：历史 FSD 验收写法。
