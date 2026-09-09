# User-visible Behavior and Acceptance

## 0. Authority and Scope

已有正式用户文档、接口规范和已接受政策继续在各自覆盖范围内有效。`capability_contract.json`
登记选定的公开承诺与边界，本文档展开交互语义与验收，`docs/business_user_guide.md` 负责
使用说明；生成文档不因文件名自动覆盖既有权威。描述性事实核对当前实现证据，规范性政策
核对有效授权与政策依据，混合语句拆开处理。本文档只写可由 UI、API 响应或其他公开入口
直接观察的行为，不把日志、监控或内部状态当成用户结果。

<!-- project-fill: 说明本项目的公开入口、本文覆盖范围与排除项，并引用各自范围内有效的正式文档、接口规范与政策依据；完成后删除此 marker -->

## 1. Audience and Granularity

面向用户、外部调用 Agent、产品和验收人员。按能独立产生用户价值的 journey 编写；等价
选项只保留代表，描述可组合的原子行为，不枚举无价值的排列组合。future / proposed 行为
必须显式标注状态。

<!-- project-fill: 写明本项目的目标用户和验收粒度；完成后删除此 marker -->

## 2. Current behavior

每个 scenario 的当前行为必须有实现或测试证据，并使用以下字段。观察到的行为不自动成为
长期支持承诺；支持或拒绝政策须另有依据。尚未核实场景时，写明已检查入口与证据缺口；
只有确认适用的入口尚未配置时才写 `Not configured`，确实不适用时才写 `Not applicable`。

### Scenario

<!-- project-fill: 用一个已验证的真实场景替换本段；包含 User goal、Required context、User action or request、Directly observable result、Failure / degradation / escalation、Acceptance assertion 和适用的真实 contract/reference 或测试证据；完成后删除此 marker -->

## 3. Cross-cutting User-visible Invariants

不变量必须可由目标读者直接判断：项目采用 capability contract anchor 协议时，使用其
canonical anchor；项目已有自己的 contract/reference 机制时，使用该真实机制或可核对的测试
证据。不得为满足本模板发明 anchor registry，并避免依赖会随数据变化的示例数值。

<!-- project-fill: 列出跨 journey 的真实可见不变量与验收证据；没有时写 Not applicable — 已验证原因；完成后删除此 marker -->

## 4. Known Limits and Human Escalation

限制必须区分有依据的支持政策、当前实现限制、暂时降级和 future / proposed。当前如此运行
不等于项目承诺长期如此。人工升级只写已确认、用户能识别的触发条件、可见解释和责任角色，
不暴露内部监控细节，也不编造责任人或流程。

<!-- project-fill: 写入已验证限制、降级、拒绝和人工升级路径，并引用适用的真实 contract/reference 或测试证据；没有配置升级路径时准确说明；完成后删除此 marker -->

## 5. Combination Behavior

多项能力共同影响一个用户可观察结果时，先检查既有规则能否确定组合结果。共享对象、状态、
资源或优先级是调查提示，不是自动升级条件。只有事实已查清，仍有实质性语义分歧且超出
当前授权时，才登记 Open question；规则已能确定结果时，直接写明 Current behavior 并验证。

<!-- project-fill: 记录本项目实际存在且影响同一可观察结果的重要组合、适用的既有规则与行为证据；不枚举无价值的排列组合；没有适用组合时说明已检查范围与原因；完成后删除此 marker -->

## 6. Open questions

不要求每个项目都有未决问题。“未找到决定”不等于“维护者从未决定”；先调查既有规则和
当前授权，再判断是否需要决定。

<!-- project-fill: 仅为符合上述条件的真实问题保留下列四部分并填写内容；没有此类问题时删除问题骨架，说明已检查范围；完成后删除此 marker -->

### 问题标题

Current evidence:
已检查的证据；哪些是实现观察，哪些有政策依据。

Current behavior / safe boundary:
调用方当前实际能观察到什么，哪些行为尚不能确认可依赖。

Decision:
已有 Issue 或决定入口；没有则如实说明，不编造责任人或流程。

Close when:
决定落地后改写为 Current behavior，并补充对应行为测试。

## 7. Interface Entrypoints

用户与外部调用 Agent 应从真实公开接口及其正式参考进入。内部函数、偶然行为和规划不能
因写入本文就成为正式能力；本页补充交互语义，不取代接口规范。

<!-- project-fill: 指向本项目真实 API、CLI 或协议及正式接口参考，标明适用范围；没有此类接口、参考尚未配置与入口尚未确认应分别说明依据；完成后删除此 marker -->
