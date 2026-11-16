# 编程回路提示与源索引

这里是 coding-loop v2 编程模型行为模板的中文源。人类流程入口是
[编程工作流](../docs/development_workflow/README.md)；执行系统从同一固定 Git 提交读取
[coding_workflow.json](coding_workflow.json)，按用途装入其中有序的 `promptPaths`。
本仓库发布规范与提示，不表示 Tongxu 已完成对应控制流程、权限和运行能力改造。

## 默认提示组合

每种用途先装入 [公共约定](coding_common.md)。同一工程负责人可以在不同阶段使用不同用途；
文件数、用途数不等于模型调用数或必须新增的 agent 数。以下路径均相对当前目录，实际源索引
使用相对 coding-workflow 仓库根的完整路径。
Issue 和 PR 的两方正式审查均由来自两家不同 LLM 公司的 LLM 承担。

| 用途键 | 公共约定之后按序装入 | 职责 |
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
| `user_acceptance` | [user_acceptance.md](user_acceptance.md) | 提前设计验收、运行候选用户场景、补验部署相关缺口 |
| `delivery_explanation` | [delivery_explanation.md](delivery_explanation.md) | 按实际用户成果解释实现、使用方式和取舍 |

两公司初审先独立完成，再执行交流片段。双方无阻断问题时也实际交换结论并简短确认。
需要处理的 PR 阻断问题成批进入事实／影响核实；双方独立核实后最多交流三轮，由 Codex
综合，并在同一事实核实会话修复成立问题。正式复审与修复会话隔离，仍由两家不同 LLM
公司的 LLM 对当前候选给出结论。每份正式 PR 审查提示包含完整的 `pr_review_system.md`；
核实用途单独加载核实流程与本方重点，不混用正式审查者的只读职责和修复阶段。

## 装入与固定采用

按索引顺序保存并装入每个文件的完整 UTF-8 Markdown 原文，包括其中的代码块。不得只抽取
某个 `Prompt` 小节、由模型总结后代替原文，或通过本地角色文件、代码字符串及任务输入中的
自由行为政策静默覆盖上游。已经装入的文件不必让模型为了形式再读一次。

宿主提供实际用户要求、Issue、仓库规范、候选、证据、工具能力、授权和结果格式；这些真实
输入与机械限制不由源索引代办。所有编程回路的自然语言行为模板以本目录的上游源为准；
非编程秘书、项目管理与账号设置不要求迁入。项目约定仍按其真实适用范围使用，不能用它们
编造工具能力或扩大委托。

索引只标明规范身份、入口和有序源文件，不描述任意节点、循环、执行路由或插件。
下游必须明确支持 `coding-loop-v2`，验证实际控制流程后才启用；导入新版文本不能代替实现。
固定提交、来源快照、实际发送输入、新旧工作及历史记录的处理，见
[固定版本采用与用户发起更新](../docs/development_workflow/version_adoption.md)。
读取最新 README 可以发起一次更新判断；运行中的工作不会自动跟随 `main`，旧准备也不会
因为新默认版本而得到新增写权。

## 保留的按需／历史材料

以下文件不在默认源索引中，不构成新的前置产物链：

- [fsd_core_contract.md](fsd_core_contract.md)：确实需要共享行为规格时按需参考，适用约定收束到 Issue。
- [target_state_bridge.md](target_state_bridge.md)：按需参考影响分析或迁移思路；普通仓库调查由原工程负责人完成。
- [issue_closure_fsd_acceptance.md](issue_closure_fsd_acceptance.md)：历史 FSD 收口写法；新工作使用提前规划和候选实测的用户路径验收。

保留旧文件便于理解和引用，不意味着它们重新进入默认执行。旧工作的实际规则从其当时
固定的源快照恢复，不能用本目录当前内容改写历史结论。
