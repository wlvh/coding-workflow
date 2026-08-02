# User-visible Behavior and Acceptance

## 0. Authority and Scope

`capability_contract.json` 是能力边界的机器可读真相源；本文档是用户可观察行为与验收不变量
的真相源；`docs/business_user_guide.md` 只能派生解释二者。本文档只写可由 UI、API 响应或
其他公开入口直接观察的行为，不把日志、监控或内部状态当成用户结果。

<!-- project-fill: 说明本项目的公开入口、覆盖范围与明确排除项；完成后删除此 marker -->

## 1. Audience and Granularity

面向用户、产品和验收人员。按能独立产生用户价值的 journey 编写；等价选项只保留代表，
描述可组合的原子行为，不枚举无价值的排列组合。future / proposed 行为必须显式标注状态。

<!-- project-fill: 写明本项目的目标用户和验收粒度；完成后删除此 marker -->

## 2. Supported User Journeys

每个 scenario 都必须来自当前实现或测试证据，并使用以下字段。没有已验证 journey 时，写
`Not configured —` 加已检查的入口和原因，而不是编造示例。

### Scenario

<!-- project-fill: 用一个已验证的真实场景替换本段；包含 User goal、Required context、User action or request、Directly observable result、Failure / degradation / escalation、Acceptance assertion 和 capability anchor；完成后删除此 marker -->

## 3. Cross-cutting User-visible Invariants

不变量必须可由目标读者直接判断，通过稳定 capability anchor 回到 contract，并避免依赖
会随数据变化的示例数值。

<!-- project-fill: 列出跨 journey 的真实可见不变量与验收证据；没有时写 Not applicable — 已验证原因；完成后删除此 marker -->

## 4. Known Limits and Human Escalation

限制必须区分当前不支持、暂时降级和 future / proposed。人工升级只写用户能识别的触发条件、
可见解释和责任角色，不暴露内部监控细节。

<!-- project-fill: 写入已验证限制、降级、拒绝和人工升级路径，并引用 capability anchor；没有配置升级路径时准确说明；完成后删除此 marker -->
