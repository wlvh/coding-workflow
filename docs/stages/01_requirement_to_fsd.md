# 阶段 1：需求确认与 FSD 制定

## 目标

把自然语言需求转成可实现、可测试、可审查的 `FSD Core Contract`。

## 输入

- 用户需求
- 仓库权威文档，例如 `AGENTS.md`
- 其他上游约束文档

## 输出

- 一份 `FSD Core Contract`

## 执行顺序

1. 人类先确认需求范围、目标和边界。
2. 把需求和仓库权威文档交给网页端 Pro 模型。
3. 使用 [prompts/fsd_core_contract.md](../../prompts/fsd_core_contract.md) 中的 prompt 生成 FSD。
4. 产出的 FSD 只定义外部可观察行为，不替代技术设计。

## 阶段约束

- 当前假设：网页端 GPT 5.4 Pro 不能自由探索本地代码和 GitHub。
- 因此这一阶段的 FSD 是脱离实际仓库实现细节的契约草图。
- 所有会影响外部可观察行为的内容都必须在 FSD 里钉死。

## 下一步入口

完成后进入 [docs/stages/02_bridge_to_issue.md](02_bridge_to_issue.md)。
