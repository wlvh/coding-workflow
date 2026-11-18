# 编程回路提示与源索引

这里是 coding-loop v2 编程模型行为模板的中文源。人类流程入口是
[编程工作流](../docs/development_workflow/README.md)；执行系统从同一固定 Git 提交读取
[coding_workflow.json](coding_workflow.json)，按用途装入其中有序的 `promptPaths`。

## 默认提示组合

以下路径均相对当前目录，源索引使用相对 coding-workflow 仓库根的完整路径。
Issue 和 PR 的两方正式审查均由来自两家不同 LLM 公司的 LLM 承担。

| 用途键 | 按序装入 | 职责 |
|---|---|---|
| `issue_author` | [issue_agent.md](issue_agent.md) | 依据原始目标形成并统一维护同一 Issue |
| `issue_review_completion` | [issue_review_completion.md](issue_review_completion.md)、[review_exchange.md](review_exchange.md) | 一家公司完整审查 Issue，侧重完整性与可验收性，再交流证据 |
| `issue_review_minimality` | [issue_review_minimality.md](issue_review_minimality.md)、[review_exchange.md](review_exchange.md) | 另一家公司完整审查 Issue，侧重最小充分性，再交流证据 |
| `engineering_owner` | [engineering_owner.md](engineering_owner.md) | 连续承担调查、实施、验证，并向核实修复责任交接实际候选 |
| `pr_review_correctness` | [pr_review_system.md](pr_review_system.md)、[pr_review_correctness.md](pr_review_correctness.md)、[review_exchange.md](review_exchange.md) | 一家公司完整独立审查 PR，侧重正确性，再交流证据 |
| `pr_review_impact` | [pr_review_system.md](pr_review_system.md)、[pr_review_impact.md](pr_review_impact.md)、[review_exchange.md](review_exchange.md) | 另一家公司完整独立审查 PR，侧重影响与必要性，再交流证据 |
| `finding_verification_fact` | [finding_verification.md](finding_verification.md)、[finding_verification_fact.md](finding_verification_fact.md) | Codex 独立核实事实，最多三轮交流后综合，在同一核实会话修复成立问题 |
| `finding_verification_impact` | [finding_verification.md](finding_verification.md)、[finding_verification_impact.md](finding_verification_impact.md) | 另一家 LLM 公司的 LLM 独立核实影响与最小修复范围，并回应交流 |
| `integration_acceptance` | [integration_acceptance.md](integration_acceptance.md) | 复用有效双审证据，核对集成与交付条件 |
| `user_acceptance` | [user_acceptance.md](user_acceptance.md) | 开发前制定验收计划，由 Issue 作者统一维护修订，执行候选场景及部署补验 |
| `delivery_explanation` | [delivery_explanation.md](delivery_explanation.md) | 可演示候选完成必要验证后解释功能、机制和取舍，供用户体验验收 |

## 装入与固定采用

按索引顺序保存并装入每个文件的完整 UTF-8 Markdown 原文，包括代码块；已经装入的文件无需重复读取。

宿主提供实际用户要求、Issue、仓库规范、候选、证据、工具能力、授权和结果格式。
编程回路的自然语言行为模板以本目录的上游源为准；项目约定按其适用范围使用。

下游明确支持 `coding-loop-v2`，验证实际控制流程后启用。
固定提交、来源快照、实际发送输入、新旧工作及历史记录的处理，见
[固定版本采用与用户发起更新](../docs/development_workflow/version_adoption.md)。

## 保留的按需／历史材料

以下文件供按需引用和历史读取，未列入默认源索引：

- [fsd_core_contract.md](fsd_core_contract.md)：确实需要共享行为规格时按需参考，适用约定收束到 Issue。
- [target_state_bridge.md](target_state_bridge.md)：按需参考影响分析或迁移思路；普通仓库调查由原工程负责人完成。
- [issue_closure_fsd_acceptance.md](issue_closure_fsd_acceptance.md)：历史 FSD 收口写法。
